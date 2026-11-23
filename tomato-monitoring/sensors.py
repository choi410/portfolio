"""
라즈베리파이 4B 센서 읽기 모듈

결선 (BCM 기준)
- AM2302(DHT22) DATA  -> GPIO4  (Pin 7),  DATA-3.3V 사이 4.7kΩ 풀업
- SDS011              -> USB-UART 변환기 (/dev/ttyUSB0), 5V
- HC-SR04 TRIG        -> GPIO23 (Pin 16)
- HC-SR04 ECHO        -> GPIO24 (Pin 18), 1kΩ+2kΩ 전압 분배로 5V -> 3.3V
- YL-40(PCF8591) SDA  -> GPIO2  (Pin 3),  SCL -> GPIO3 (Pin 5), I2C 주소 0x48
- AM312 OUT           -> GPIO17 (Pin 11)

TOMATO_MOCK=1 이면 하드웨어 없이 가상 값을 만든다 (PC에서 대시보드 테스트용).
"""
import math
import os
import random
import time

MOCK = os.environ.get("TOMATO_MOCK") == "1"

DHT_PIN = 4
US_TRIG_PIN = 23
US_ECHO_PIN = 24
PIR_PIN = 17
PCF8591_ADDR = 0x48
LIGHT_CHANNEL = int(os.environ.get("TOMATO_LIGHT_CH", "0"))  # YL-40 조도(LDR) 채널
SDS011_PORT = os.environ.get("TOMATO_SDS_PORT", "/dev/ttyUSB0")


class AM2302:
    """온습도 센서. 측정 간격은 2초 이상 유지해야 한다."""

    def __init__(self):
        import adafruit_dht
        import board
        self.dev = adafruit_dht.DHT22(getattr(board, f"D{DHT_PIN}"), use_pulseio=False)

    def read(self):
        try:
            return self.dev.temperature, self.dev.humidity
        except RuntimeError:
            # 단선 통신 특성상 읽기 실패가 종종 난다. 다음 주기에 다시 읽는다.
            return None, None


class SDS011:
    """미세먼지 센서. 10바이트 프레임: AA C0 PM25L PM25H PM10L PM10H ID1 ID2 CS AB"""

    WARMUP_SEC = 30

    def __init__(self, port=SDS011_PORT):
        import serial
        self.ser = serial.Serial(port, baudrate=9600, timeout=2)
        self.started = time.time()

    def warming_up(self):
        return time.time() - self.started < self.WARMUP_SEC

    def read(self):
        self.ser.reset_input_buffer()
        for _ in range(20):
            if self.ser.read(1) != b"\xaa":
                continue
            f = self.ser.read(9)
            if len(f) == 9 and f[0] == 0xC0 and f[8] == 0xAB and sum(f[1:7]) % 256 == f[7]:
                pm25 = (f[1] | f[2] << 8) / 10.0
                pm10 = (f[3] | f[4] << 8) / 10.0
                return pm25, pm10
        return None, None


class HCSR04:
    def __init__(self):
        from gpiozero import DistanceSensor
        self.dev = DistanceSensor(echo=US_ECHO_PIN, trigger=US_TRIG_PIN, max_distance=2.0)

    def read(self):
        return round(self.dev.distance * 100, 1)  # cm


class YL40Light:
    """PCF8591 8비트 ADC. 밝을수록 LDR 저항이 줄어 값이 작아지므로 반전해 0~100%로 표시."""

    def __init__(self):
        from smbus2 import SMBus
        self.bus = SMBus(1)

    def read(self):
        self.bus.write_byte(PCF8591_ADDR, 0x40 | LIGHT_CHANNEL)
        self.bus.read_byte(PCF8591_ADDR)  # 첫 바이트는 이전 변환값이라 버린다
        raw = self.bus.read_byte(PCF8591_ADDR)
        return raw, round((255 - raw) / 255 * 100)


class AM312:
    def __init__(self):
        from gpiozero import MotionSensor
        self.dev = MotionSensor(PIR_PIN)

    def read(self):
        return bool(self.dev.motion_detected)


class SensorHub:
    """모든 센서를 한 번에 읽는다. 센서 하나가 실패해도 나머지는 계속 동작."""

    def __init__(self):
        self.sensors = {}
        if MOCK:
            return
        for name, cls in [("dht", AM2302), ("sds", SDS011), ("us", HCSR04),
                          ("light", YL40Light), ("pir", AM312)]:
            try:
                self.sensors[name] = cls()
            except Exception as e:  # 미연결 센서는 건너뛰고 로그만 남긴다
                print(f"[sensor] {name} 초기화 실패: {e}")

    def _safe(self, name, default):
        dev = self.sensors.get(name)
        if dev is None:
            return default
        try:
            return dev.read()
        except Exception as e:
            print(f"[sensor] {name} 읽기 실패: {e}")
            return default

    def read_all(self):
        if MOCK:
            return mock_reading()
        temp, hum = self._safe("dht", (None, None))
        pm25, pm10 = self._safe("sds", (None, None))
        sds = self.sensors.get("sds")
        _, light_pct = self._safe("light", (None, None))
        return {
            "temperature": temp,
            "humidity": hum,
            "pm25": pm25,
            "pm10": pm10,
            "pm_warming_up": bool(sds and sds.warming_up()),
            "light": light_pct,
            "distance": self._safe("us", None),
            "motion": self._safe("pir", None),
        }


def mock_reading():
    t = time.time() / 60
    return {
        "temperature": round(24 + 4 * math.sin(t) + random.uniform(-0.3, 0.3), 1),
        "humidity": round(55 + 15 * math.sin(t / 2) + random.uniform(-1, 1), 1),
        "pm25": round(abs(8 + 6 * math.sin(t / 3) + random.uniform(-1, 1)), 1),
        "pm10": round(abs(14 + 8 * math.sin(t / 3) + random.uniform(-1, 1)), 1),
        "pm_warming_up": False,
        "light": int(60 + 30 * math.sin(t / 4)),
        "distance": round(80 + random.uniform(-3, 3), 1),
        "motion": random.random() < 0.15,
    }
