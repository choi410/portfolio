# LiDAR·Vision 센서 융합 자율주행 비글

비글 로봇에 360° LiDAR 기반 충돌 회피와 카메라 기반 신호등·QR 인식을 결합한 자율주행 코드입니다. (2025.11 ~ 12)

## 동작
- **LiDAR 주행** `drive_logic()`: 정면·좌·우·후방 구역별 최소/평균 거리 → 긴급 정지, 사방 막힘 탈출, 측면 충돌 회피, P 제어 중앙 주행
- **신호등**: HSV 빨간색 마스크 픽셀 수로 정지 판단, 신호 해제 후 속도를 점진 복귀
- **QR 도착**: `detectAndDecodeMulti()`로 QR 중심 정렬 → 크기로 도착 판정 후 정지
- 실시간 LiDAR 레이더 시각화(Matplotlib)

## 실행
```bash
pip install roboid numpy matplotlib opencv-python
set BEAGLE_CAMERA_URL=http://<로봇 IP>:9527/videostream.cgi?loginuse=<ID>&loginpas=<PW>
python autonomous_driving.py
```
