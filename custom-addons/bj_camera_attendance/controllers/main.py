import base64
import os
import time
import cv2
import requests
import face_recognition
import numpy as np
from typing import Dict, List, Tuple, Optional

# =========================
# CONFIG (PHẢI KHỚP ODOO)
# =========================
ODOO_URL = "http://localhost:8069"
API_PATH = "/api/camera/attendance"
CAMERA_TOKEN = "123456"            # KHỚP ir.config_parameter
DEVICE_ID = "LAPTOP_CAM_01"

# Face recognition
TOLERANCE = 0.45
MODEL = "hog"          # demo nhanh
FRAME_RESIZE = 0.5

# Anti spam
REQUIRE_CONSISTENT_HITS = 3
MIN_SECONDS_BETWEEN_HITS = 10

JPEG_QUALITY = 80

# Enrollment structure:
# enroll/
#   EMP001/
#     1.jpg
#     2.jpg
ENROLL_DIR = "enroll"


# =========================
# UTILS
# =========================
def bgr_to_b64jpg(image_bgr, quality=80) -> str:
    params = [int(cv2.IMWRITE_JPEG_QUALITY), quality]
    ok, jpg = cv2.imencode(".jpg", image_bgr, params)
    if not ok:
        raise RuntimeError("JPEG encode failed")
    return base64.b64encode(jpg.tobytes()).decode("utf-8")


def load_enrollment():
    encodings = []
    codes = []

    if not os.path.isdir(ENROLL_DIR):
        raise RuntimeError(f"Missing enroll dir: {ENROLL_DIR}")

    for code in sorted(os.listdir(ENROLL_DIR)):
        emp_dir = os.path.join(ENROLL_DIR, code)
        if not os.path.isdir(emp_dir):
            continue

        for fn in os.listdir(emp_dir):
            if not fn.lower().endswith((".jpg", ".png", ".jpeg")):
                continue

            img = face_recognition.load_image_file(os.path.join(emp_dir, fn))
            locs = face_recognition.face_locations(img, model=MODEL)
            if not locs:
                continue

            enc = face_recognition.face_encodings(img, locs)[0]
            encodings.append(enc)
            codes.append(code)

    if not encodings:
        raise RuntimeError("No face data loaded")

    print(f"[ENROLL] Loaded {len(encodings)} samples for {len(set(codes))} employees")
    return encodings, codes


def match_face(face_enc, db_encs, db_codes) -> Tuple[Optional[str], float]:
    dists = face_recognition.face_distance(db_encs, face_enc)
    idx = int(np.argmin(dists))
    dist = float(dists[idx])

    if dist <= TOLERANCE:
        score = max(0.0, 1.0 - dist / TOLERANCE)
        return db_codes[idx], score

    return None, 0.0


def post_to_odoo(employee_code: str, action: str, images: List[str]):
    url = f"{ODOO_URL}{API_PATH}"
    payload = {
        "employee_code": employee_code,
        "action": action,
        "images": images,
    }

    r = requests.post(
        url,
        json=payload,
        headers={
            "Content-Type": "application/json",
            "X-API-TOKEN": CAMERA_TOKEN,
        },
        timeout=10,
    )
    r.raise_for_status()
    return r.json()


# =========================
# MAIN
# =========================
def main():
    db_encs, db_codes = load_enrollment()

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        raise RuntimeError("Cannot open camera")

    last_sent: Dict[str, float] = {}
    hit_count: Dict[str, int] = {}

    print("[RUN] ESC to quit")

    while True:
        ok, frame = cap.read()
        if not ok:
            break

        small = cv2.resize(frame, (0, 0), fx=FRAME_RESIZE, fy=FRAME_RESIZE)
        rgb = cv2.cvtColor(small, cv2.COLOR_BGR2RGB)

        boxes = face_recognition.face_locations(rgb, model=MODEL)
        encs = face_recognition.face_encodings(rgb, boxes)

        seen = set()

        for (top, right, bottom, left), enc in zip(boxes, encs):
            code, score = match_face(enc, db_encs, db_codes)

            top *= int(1 / FRAME_RESIZE)
            right *= int(1 / FRAME_RESIZE)
            bottom *= int(1 / FRAME_RESIZE)
            left *= int(1 / FRAME_RESIZE)

            if not code:
                cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
                cv2.putText(frame, "Unknown", (left, top - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                continue

            seen.add(code)
            hit_count[code] = hit_count.get(code, 0) + 1

            cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
            cv2.putText(
                frame,
                f"{code} hit:{hit_count[code]}",
                (left, top - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 255, 0),
                2,
            )

            if hit_count[code] < REQUIRE_CONSISTENT_HITS:
                continue

            now = time.time()
            if now - last_sent.get(code, 0) < MIN_SECONDS_BETWEEN_HITS:
                continue

            try:
                img_b64 = bgr_to_b64jpg(frame, JPEG_QUALITY)
                resp = post_to_odoo(code, "toggle", [img_b64])
                print("[ODOO]", resp)
                last_sent[code] = now
                hit_count[code] = 0
            except Exception as e:
                print("[ERROR]", e)

        for c in list(hit_count.keys()):
            if c not in seen:
                hit_count[c] = 0

        cv2.imshow("Camera Attendance", frame)
        if cv2.waitKey(1) & 0xFF == 27:
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
