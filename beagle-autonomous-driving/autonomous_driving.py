import roboid as rb
import time as tm
import numpy as np
import math
import matplotlib.pyplot as plt
import cv2


# ==========================================
# 1. 설정 및 초기화
# ==========================================
beagle = rb.Beagle()
import os
# 카메라 스트림 주소는 환경변수로 지정 (계정 정보를 코드에 남기지 않기 위함)
# 예: set BEAGLE_CAMERA_URL=http://<로봇 IP>:9527/videostream.cgi?loginuse=<ID>&loginpas=<PW>
CAMERA_SOURCE = os.environ.get("BEAGLE_CAMERA_URL", "http://192.168.66.1:9527/videostream.cgi")
qr_detector = cv2.QRCodeDetector()


# ------------------------------------------
# [설정] 주행 파라미터
# ------------------------------------------
LIDAR_MIN = 30
LIDAR_MAX = 2000


STOP_DIST      = 60      # 🔴 정면 긴급 정지
NEAR_FRONT     = 120     # 🟡 정면 "가까움"
NEAR_BACK      = 120     # 🟡 후방 "가까움"
SIDE_EMERGENCY = 50      # 🔥 측면 절대 충돌 방지
FRONT_SAFE     = 600     # 직진 모드 활성 기준


MAX_SPEED   = 50
TURN_SPEED  = 20
MAX_STEER   = 40


# ------------------------------------------
# [수정됨] QR 파라미터 (인식률 개선)
# ------------------------------------------
# 350은 너무 커서 인식 실패 가능성 있음 -> 250으로 완화
TARGET_QR_SIZE = 200    
QR_ALIGN_SPEED = 10
QR_APPROACH_SPEED = 10
FRAME_WIDTH = 640
# 중앙 정렬 허용 범위를 넓혀서(40->60) 앞으로 더 잘 가게 함
CENTER_TOL = 60          


SHOW_PLOT = True


# ==========================================
# 2. 유틸 함수
# ==========================================
def get_clean_scan():
    scan = beagle.lidar()
    if not scan: return []
    return [d if (d and LIDAR_MIN < d < LIDAR_MAX) else 0 for d in scan]


def get_min_dist(scan, start, end):
    vals = []
    n = len(scan)
    for a in range(n):
        if start > end:
            if a >= start or a <= end:
                if scan[a] > 0: vals.append(scan[a])
        else:
            if start <= a <= end:
                if scan[a] > 0: vals.append(scan[a])
    return min(vals) if vals else 2000


def get_avg_dist(scan, start, end):
    vals = []
    n = len(scan)
    for a in range(n):
        if start > end:
            if a >= start or a <= end:
                if scan[a] > 0: vals.append(scan[a])
        else:
            if start <= a <= end:
                if scan[a] > 0: vals.append(scan[a])
    return (sum(vals) / len(vals)) if vals else 0


def find_farthest_direction(scan):
    max_d = 0
    max_i = 0
    for i, d in enumerate(scan):
        if d > max_d:
            max_d = d
            max_i = i
    return max_i, max_d


def soft_stop(total_time=0.5, steps=6):
    for i in range(steps, 0, -1):
        s = int(MAX_SPEED * (i / steps) * 0.4)
        beagle.wheels(s, s)
        tm.sleep(total_time / steps)
    beagle.wheels(0, 0)


# ==========================================
# 3. 주행 로직
# ==========================================
def drive_logic(scan):
    front_min = get_min_dist(scan, 330, 30)
    back_min  = get_min_dist(scan, 150, 210)
    left_min  = get_min_dist(scan, 60, 120)
    right_min = get_min_dist(scan, 240, 300)


    front_avg = get_avg_dist(scan, 330, 30)
    left_path = get_avg_dist(scan, 20, 80)
    right_path= get_avg_dist(scan, 280, 340)


    all_close = (front_min < NEAR_FRONT and back_min < NEAR_BACK and
                 left_min < NEAR_FRONT and right_min < NEAR_FRONT)
    if all_close:
        far_angle, _ = find_farthest_direction(scan)
        angle_rel = ((far_angle + 180) % 360) - 180
        if angle_rel > 0: return -TURN_SPEED, TURN_SPEED
        else: return TURN_SPEED, -TURN_SPEED


    if front_min < NEAR_FRONT:
        if front_min < STOP_DIST: return 0, 0
        if back_min > NEAR_BACK:
            if left_min < right_min: return -TURN_SPEED, -int(TURN_SPEED * 0.3)
            else: return -int(TURN_SPEED * 0.3), -TURN_SPEED
        return (-TURN_SPEED, TURN_SPEED) if left_min > right_min else (TURN_SPEED, -TURN_SPEED)


    if left_min < SIDE_EMERGENCY and right_min >= SIDE_EMERGENCY: return TURN_SPEED, -TURN_SPEED
    if right_min < SIDE_EMERGENCY and left_min >= SIDE_EMERGENCY: return -TURN_SPEED, TURN_SPEED
    if left_min < SIDE_EMERGENCY and right_min < SIDE_EMERGENCY: return TURN_SPEED, TURN_SPEED


    error = left_path - right_path
    if front_avg > FRONT_SAFE:
        kp = 0.01
        base_speed = MAX_SPEED
        if abs(error) < 150: error = 0
    else:
        kp = 0.05
        ratio = (front_avg - NEAR_FRONT) / (FRONT_SAFE - NEAR_FRONT)
        ratio = max(0.0, min(1.0, ratio))
        base_speed = TURN_SPEED + (MAX_SPEED - TURN_SPEED) * ratio
        base_speed = max(15, base_speed)


    steering = max(min(error * kp, MAX_STEER), -MAX_STEER)
    L = int(base_speed - steering)
    R = int(base_speed + steering)
    return max(min(L, 60), -60), max(min(R, 60), -60)


# ==========================================
# 4. QR 및 신호등
# ==========================================
def process_qr_navigation(points):
    pts = points.reshape(4, 2).astype(int)
    # QR 크기 계산
    qr_width = int(np.linalg.norm(pts[0] - pts[1]))
   
    cx = int(np.mean(pts[:, 0]))
    offset = cx - (FRAME_WIDTH // 2)


    # [디버깅용 출력] 현재 크기와 목표 크기 비교
    print(f"👀 QR 감지됨! 현재크기: {qr_width} / 목표: {TARGET_QR_SIZE} (오차: {offset})")


    # 1) 중앙 정렬
    if abs(offset) > CENTER_TOL:
        return (QR_ALIGN_SPEED, -QR_ALIGN_SPEED, False) if offset > 0 else (-QR_ALIGN_SPEED, QR_ALIGN_SPEED, False)
   
    # 2) 전진 접근
    if qr_width < TARGET_QR_SIZE:
        return (QR_APPROACH_SPEED, QR_APPROACH_SPEED, False)
   
    # 3) 도착 (크기가 목표보다 커지면 True 반환)
    return (0, 0, True)


current_scale = 1.0
def detect_signal_and_update_scale(frame):
    global current_scale
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    red = cv2.inRange(hsv, (0,120,80), (10,255,255)) + cv2.inRange(hsv, (170,120,80), (180,255,255))
   
    if cv2.countNonZero(red) > 500:
        current_scale = 0.0
    else:
        if current_scale < 0.3: current_scale = 0.3
        current_scale = min(current_scale * 1.05, 1.0)
    return current_scale


def draw_polar(ax, scan, f, l, r, b):
    ax.clear()
    ax.set_theta_zero_location("N")
    ax.set_theta_direction(-1)
    ax.set_rmax(2000)
    angles = np.linspace(0, 2*np.pi, len(scan), endpoint=False)
    dists = np.array(scan)
    valid = dists > 0
    ax.plot(angles[valid], dists[valid], '.', color='gray', markersize=3)
    ax.plot([0], [f], 'o', color='orange', markersize=10)
    ax.plot([np.deg2rad(90)], [l], 'o', color='blue', markersize=10)
    ax.plot([np.deg2rad(270)], [r], 'o', color='green', markersize=10)
    ax.plot([np.deg2rad(180)], [b], 'o', color='purple', markersize=10)
    ax.set_title(f"Radar - F:{f} L:{l} R:{r}", fontsize=12)


# ==========================================
# 5. 메인 실행
# ==========================================
def main():
    global current_scale
    beagle.start_lidar()
    tm.sleep(1)
    cap = cv2.VideoCapture(CAMERA_SOURCE)


    if SHOW_PLOT:
        plt.ion()
        fig = plt.figure(figsize=(6, 6))
        ax = fig.add_subplot(111, projection='polar')


    print("🚀 시스템 시작: [고급주행 + QR정지] (디버깅 모드)")


    try:
        while True:
            ret, frame = cap.read()
            if not ret: break


            # 1. 신호등 (빨강 감지)
            scale = detect_signal_and_update_scale(frame)


            # 2. QR 코드 감지
            retval, decoded, points, _ = qr_detector.detectAndDecodeMulti(frame)
           
            if points is not None:
                # QR 발견! 정밀 제어 시작
                L, R, arrived = process_qr_navigation(points[0])
                beagle.wheels(L, R)
               
                # 시각화 (화면에 초록 박스 표시)
                pts = points[0].reshape(4, 2).astype(int)
                cv2.polylines(frame, [pts], True, (0, 255, 0), 3)
                cv2.imshow("Smart View", frame)
                cv2.waitKey(1)


                # 도착 확인 (True면 종료)
                if arrived:
                    print(f"\n🎉 [도착 완료] QR 크기 만족! ({decoded}) -> 시스템 종료")
                    beagle.wheels(0, 0) # 즉시 정지
                    break
               
                continue


            # 3. LiDAR 주행 (QR 없을 때)
            scan = get_clean_scan()
            if not scan: continue
           
            if SHOW_PLOT:
                f = get_min_dist(scan, 330, 30)
                l = get_min_dist(scan, 60, 120)
                r = get_min_dist(scan, 240, 300)
                b = get_min_dist(scan, 150, 210)
                draw_polar(ax, scan, f, l, r, b)
                plt.pause(0.001)


            if get_min_dist(scan, 330, 30) < STOP_DIST:
                beagle.wheels(0,0)
                continue


            L, R = drive_logic(scan)
            L, R = int(L * scale), int(R * scale)
            beagle.wheels(L, R)


            cv2.imshow("Smart View", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break


    finally:
        soft_stop()
        beagle.stop_lidar()
        cap.release()
        cv2.destroyAllWindows()
        if SHOW_PLOT: plt.close()
        print("🔴 시스템 전원 OFF")


if __name__ == "__main__":
    main()

