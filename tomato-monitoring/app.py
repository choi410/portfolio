"""
토마토 생육 환경 모니터링 Flask 서버

- 백그라운드 스레드가 2초마다 센서를 읽어 최신값과 이력을 저장
- /          : 대시보드
- /api/data  : 최신값 + 생육 환경 점수 + 최근 이력(JSON)
"""
import os
import threading
import time
from collections import deque
from datetime import datetime

from flask import Flask, jsonify, render_template

from sensors import SensorHub

READ_INTERVAL_SEC = float(os.environ.get("TOMATO_INTERVAL", "2.0"))  # AM2302 최소 측정 간격 2초
HISTORY_LEN = 300        # 약 10분

# 토마토 적정 범위 (lo, hi, 범위를 벗어났을 때 0점이 되는 거리)
OPTIMAL = {
    "temperature": (18, 27, 8),
    "humidity": (60, 80, 30),
    "pm25": (0, 15, 35),
    "light": (40, 100, 40),
}
ADVICE = {
    "temperature": ("온도가 낮아요. 보온이 필요해요.", "온도가 높아요. 환기·차광이 필요해요."),
    "humidity": ("습도가 낮아요. 가습이나 관수가 필요해요.", "습도가 높아요. 병해 예방을 위해 환기하세요."),
    "pm25": (None, "미세먼지가 높아요. 외기 유입을 줄이세요."),
    "light": ("빛이 부족해요. 보광을 검토하세요.", None),
}

app = Flask(__name__)
hub = SensorHub()
lock = threading.Lock()
latest = {}
history = deque(maxlen=HISTORY_LEN)


def item_score(key, value):
    if value is None:
        return None
    lo, hi, margin = OPTIMAL[key]
    if lo <= value <= hi:
        return 100
    dist = lo - value if value < lo else value - hi
    return max(0, round(100 - dist / margin * 100))


def evaluate(data):
    scores, advice = {}, []
    for key, (lo, hi, _) in OPTIMAL.items():
        v = data.get(key)
        if key.startswith("pm") and data.get("pm_warming_up"):
            v = None  # SDS011 예열(30초) 중 값은 신뢰도가 낮아 제외
        s = item_score(key, v)
        scores[key] = s
        if s is not None and s < 100:
            msg = ADVICE[key][0] if v < lo else ADVICE[key][1]
            if msg:
                advice.append(msg)
    valid = [s for s in scores.values() if s is not None]
    total = round(sum(valid) / len(valid)) if valid else None
    if total is None:
        status = "측정 대기 중"
    elif total >= 80:
        status = "좋음 · 생육 환경이 양호해요"
    elif total >= 50:
        status = "보통 · 환경 개선이 필요해요"
    else:
        status = "나쁨 · 즉시 점검이 필요해요"
    return {"total": total, "status": status, "items": scores, "advice": advice}


def sensor_loop():
    while True:
        data = hub.read_all()
        data["time"] = datetime.now().strftime("%H:%M:%S")
        data["score"] = evaluate(data)
        with lock:
            latest.clear()
            latest.update(data)
            history.append({k: data[k] for k in ("time", "temperature", "humidity", "pm25", "light")})
        time.sleep(READ_INTERVAL_SEC)


@app.route("/")
def index():
    return render_template("index.html", optimal=OPTIMAL)


@app.route("/api/data")
def api_data():
    with lock:
        return jsonify({"latest": dict(latest), "history": list(history)[-60:]})


if __name__ == "__main__":
    threading.Thread(target=sensor_loop, daemon=True).start()
    port = int(os.environ.get("PORT", "5000"))
    app.run(host="0.0.0.0", port=port, debug=False)
