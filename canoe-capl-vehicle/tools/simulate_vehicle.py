"""
Driver.can / VehicleECU.can 로직을 Python으로 옮겨 시나리오를 돌려 보는 재현 시뮬레이션.
CANoe 실행 결과가 아니라, CAPL 코드의 계산식을 그대로 옮겨 동작을 시각화한 것입니다.

실행: python simulate_vehicle.py [출력 PNG 경로]
"""
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

TICK_MS = 100

# ---------------- VehicleECU.can 상수 ----------------
MAX_SPEED_FORWARD, MAX_SPEED_REVERSE = 250, 100
CREEP_LIMIT, CREEP_INC = 20, 2
BASE_DECEL, MAX_BRAKE_DECEL, NATURAL_DECEL = 2.0, 10.0, 0.5
ACC_BASE, ACC_MAX = 0.5, 10.0
ACC_SPORT, ACC_ECO = 3.0, -2.0
FUEL_STD, FUEL_ECO, FUEL_SPORT = 15.0, 9.0, -9.0
GEAR_NAME = {0: "P", 1: "D", 2: "R", 3: "N"}


class Driver:
    """Driver.can: 키 입력 -> 페달 램프(+5 / -10 per 100ms), 브레이크를 밟아야 변속 요청 송신"""

    def __init__(self):
        self.gear, self.brake, self.fwd, self.mode = 0, 0, 0, 0
        self.fwd_pressed = self.brake_pressed = False

    def key(self, k, ecu, log):
        if k in "prnd":
            target = {"p": 0, "d": 1, "r": 2, "n": 3}[k]
            if self.brake > 0:                      # 브레이크 페달 값이 있어야만 송신
                ecu.on_gear(target, log)
            else:
                log.append(("변속 요청 안 함 (브레이크 미입력)", k.upper()))
        elif k == "a":
            if not self.brake_pressed:
                self.fwd_pressed = not self.fwd_pressed
        elif k == "b":
            self.brake_pressed = not self.brake_pressed
        elif k == "m":
            self.mode = (self.mode + 1) % 3

    def tick(self):
        self.fwd = min(100, self.fwd + 5) if self.fwd_pressed else max(0, self.fwd - 10)
        self.brake = min(100, self.brake + 5) if self.brake_pressed else max(0, self.brake - 10)


class VehicleECU:
    """VehicleECU.can: 100ms마다 속도·연비 계산, 주행 중 변속 거부"""

    def __init__(self):
        self.speed, self.gear = 0.0, 0

    def on_gear(self, gear, log):
        if self.speed != 0.0 and gear != self.gear:
            log.append(("변속 거부 (주행 중)", GEAR_NAME[gear]))
            return
        self.gear = gear
        log.append(("변속 수락", GEAR_NAME[gear]))

    def tick(self, brake, fwd, mode):
        acc_base, acc_max, decel_base = ACC_BASE, ACC_MAX, BASE_DECEL
        if mode == 1:
            acc_base, acc_max = max(0.1, ACC_BASE + ACC_ECO), max(0.2, ACC_MAX + ACC_ECO)
        elif mode == 2:
            acc_base, acc_max, decel_base = ACC_BASE + ACC_SPORT, ACC_MAX + ACC_SPORT, BASE_DECEL + 2.0
        if brake > 0:                                # 브레이크 최우선
            self.speed = max(0.0, self.speed - (decel_base + brake / 100 * (MAX_BRAKE_DECEL - decel_base)))
        elif self.gear in (0, 3):
            self.speed = 0.0
        else:
            limit = MAX_SPEED_FORWARD if self.gear == 1 else MAX_SPEED_REVERSE
            if fwd > 0:
                self.speed += acc_base + fwd / 100 * (acc_max - acc_base)
            elif self.speed < CREEP_LIMIT:
                self.speed += CREEP_INC
            else:
                self.speed -= NATURAL_DECEL
            self.speed = min(max(self.speed, 0.0), limit)
        display = -self.speed if self.gear == 2 else self.speed
        return int(display)


# ---------------- 시나리오 ----------------
SCENARIO = [  # (시간 s, 키)
    (0.5, "b"), (1.5, "d"), (2.5, "b"),          # 브레이크 -> D 변속 -> 브레이크 해제(크립)
    (5.0, "a"), (5.8, "a"),                      # 가속 후 페달 해제(자연 감속)
    (9.0, "b"), (9.4, "r"),                      # 제동 중 R 변속 시도 -> 거부
    (11.0, "r"), (12.0, "b"),                    # 정지 후 R 변속 수락 -> 후진 크립
]
END_S = 16.0


def run():
    drv, ecu = Driver(), VehicleECU()
    t_axis, speed, fwd, brake, gear, events = [], [], [], [], [], []
    keys = sorted(SCENARIO)
    for i in range(int(END_S * 1000 / TICK_MS) + 1):
        t = i * TICK_MS / 1000
        while keys and keys[0][0] <= t + 1e-9:
            _, k = keys.pop(0)
            log = []
            drv.key(k, ecu, log)
            events += [(t, msg, g) for msg, g in log]
        drv.tick()
        disp = ecu.tick(drv.brake, drv.fwd, drv.mode)
        t_axis.append(t); speed.append(disp); fwd.append(drv.fwd); brake.append(drv.brake); gear.append(ecu.gear)
    return t_axis, speed, fwd, brake, gear, events


def plot(out):
    t, speed, fwd, brake, gear, events = run()
    from matplotlib import font_manager
    have = {f.name for f in font_manager.fontManager.ttflist}
    plt.rcParams["font.family"] = [f for f in ("Malgun Gothic", "AppleGothic", "NanumGothic") if f in have] + ["DejaVu Sans"]
    plt.rcParams["axes.unicode_minus"] = False
    fig, ax = plt.subplots(3, 1, figsize=(10, 6.4), sharex=True, height_ratios=[2.2, 1.3, 0.9])
    ax[0].plot(t, speed, color="#1c7ed6", lw=2)
    ax[0].axhline(0, color="#adb5bd", lw=0.8)
    ax[0].axhline(20, color="#868e96", lw=0.8, ls="--"); ax[0].text(13.0, 24, "크립 20km/h", fontsize=8, color="#868e96")
    ax[0].axhline(-20, color="#868e96", lw=0.8, ls="--")
    ax[0].set_ylabel("Display_Speed\n(km/h)")
    ax[1].plot(t, fwd, color="#2f9e44", lw=1.8, label="Forward_pedal")
    ax[1].plot(t, brake, color="#e03131", lw=1.8, label="Break_pedal")
    ax[1].set_ylabel("페달 (%)"); ax[1].legend(loc="upper right", fontsize=8, frameon=False)
    ax[2].step(t, gear, where="post", color="#495057", lw=1.8)
    ax[2].set_yticks([0, 1, 2, 3], ["P", "D", "R", "N"]); ax[2].set_ylabel("Gear")
    ax[2].set_xlabel("시간 (s)")
    for et, msg, g in events:
        rejected = "거부" in msg
        for a in ax:
            a.axvline(et, color="#e03131" if rejected else "#adb5bd", lw=1 if rejected else 0.7, ls=":")
        ax[0].annotate(f"{g} {msg}", (et, max(speed) * (0.9 if rejected else 0.55)),
                       fontsize=8, color="#e03131" if rejected else "#495057",
                       xytext=(4, 0), textcoords="offset points")
    for a in ax:
        a.grid(alpha=0.25); a.spines[["top", "right"]].set_visible(False)
    fig.suptitle("CAPL 로직 재현 시뮬레이션: 변속 인터록 · 크립 · 가속 · 제동", fontsize=12, x=0.01, ha="left")
    fig.tight_layout()
    fig.savefig(out, dpi=150)
    for e in events:
        print(f"{e[0]:5.1f}s  {e[2]}  {e[1]}")
    print("max speed", max(speed), "min", min(speed))


if __name__ == "__main__":
    plot(sys.argv[1] if len(sys.argv) > 1 else "vehicle_simulation.png")
