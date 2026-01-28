import base64
import os
import time
import json
import requests
import cv2
import face_recognition
import numpy as np
from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional

# =========================
# CONFIG
# =========================
ODOO_URL = "http://localhost:8069"
DB_NAME = "odoo19_fitdnu"          # <-- sửa theo DB của bạn
CAMERA_TOKEN = "abc123"            # <-- khớp token trong controller Odoo
API_PATH = "/bj/camera/checkin"    # <-- khớp route bạn đã tạo
DEVICE_ID = "LAPTOP_CAM_01"

# Face match
TOLERANCE = 0.45   # thấp = khó hơn, ít nhầm hơn
MODEL = "hog"      # demo nhanh; có thể đổi "cnn" nếu máy mạnh

# Runtime behavior
FRAME_RESIZE = 0.5         # giảm độ phân giải để nhanh hơn
MIN_SECONDS_BETWEEN_HITS = 10  # debounce per employee
REQUIRE_CONSISTENT_HITS = 3    # cần match liên tiếp N frame mới gửi
JPEG_QUALITY = 80              # ảnh minh chứng

# Enrollment folder structure:
# enroll/
#   1/
#     a.jpg
#     b.jpg
#     c.jpg
#   2/
#     ...
ENROLL_DIR = "enroll"


# =========================
# DATA STRUCTURES
# =========================
@dataclass
class EmployeeFaceDB:
    encodings: List[np.ndarray]
    employee_ids: List[int]


# =========================
# UTILS
# =========================
def bgr_to_b64jpg(image_bgr, quality=80) -> str:
    encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), int(quality)]
    ok, jpg = cv2.imencode(".jpg", image_bgr, encode_param)
    if not ok:
        raise RuntimeError("Failed to encode JPEG")
    return base64.b64encode(jpg.tobytes()).decode("utf-8")


def load_enrollment_db(enroll_dir: str) -> EmployeeFaceDB:
    encs: List[np.ndarray] = []
    ids: List[int] = []

    if not os.path.isdir(enroll_dir):
        raise RuntimeError(f"Enrollment dir not found: {enroll_dir}")

    for emp_folder in sorted(os.listdir(enroll_dir)):
        emp_path = os.path.join(enroll_dir, emp_folder)
        if not os.path.isdir(emp_path):
            continue
        try:
            emp_id = int(emp_folder)
        except:
            continue

        for fn in os.listdir(emp_path):
            if not fn.lower().endswith((".jpg", ".jpeg", ".png")):
                continue
            p = os.path.join(emp_path, fn)
            img = face_recognition.load_image_file(p)
            locs = face_recognition.face_locations(img, model=MODEL)
            if not locs:
                continue
            # lấy face đầu tiên (demo)
            enc = face_recognition.face_encodings(img, known_face_locations=locs)[0]
            encs.append(enc)
            ids.append(emp_id)

    if not encs:
        raise RuntimeError("No enrollment faces loaded. Put images in enroll/<employee_id>/")

    print(f"[ENROLL] Loaded {len(encs)} samples for {len(set(ids))} employees")
    return EmployeeFaceDB(encodings=encs, employee_ids=ids)


def match_face(face_encoding: np.ndarray, db: EmployeeFaceDB) -> Tuple[Optional[int], float]:
    """
    Returns (employee_id, confidence_like_score)
    confidence_like_score: chuyển từ distance sang điểm 0..1 (demo)
    """
    distances = face_recognition.face_distance(db.encodings, face_encoding)
    best_idx = int(np.argmin(distances))
    best_dist = float(distances[best_idx])
    if best_dist <= TOLERANCE:
        # score demo: dist càng nhỏ càng gần 1
        score = max(0.0, min(1.0, 1.0 - (best_dist / TOLERANCE)))
        return db.employee_ids[best_idx], score
    return None, 0.0


def post_attendance_to_odoo(
    employee_id: int,
    action: str,
    images_b64: List[str],
    confidence: float,
    ts_local: str,
) -> Dict:
    """
    action: 'check_in' | 'check_out' | 'toggle'
    """
    url = f"{ODOO_URL}{API_PATH}?db={DB_NAME}"
    payload = {
        "employee_id": employee_id,
        "action": action,
        "device_id": DEVICE_ID,
        "confidence": confidence,
        "ts_local": ts_local,   # hook Level 2: ca/OT tổng hợp theo timestamp
        "images": images_b64,   # hook: Odoo lưu attachment minh chứng
    }

    r = requests.post(
        url,
        json=payload,
        headers={
            "Content-Type": "application/json",
            "X-Camera-Token": CAMERA_TOKEN,
        },
        timeout=10,
    )
    r.raise_for_status()
    return r.json()


# =========================
# MAIN LOOP (LEVEL 2 READY)
# =========================
def main():
    db = load_enrollment_db(ENROLL_DIR)

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        raise RuntimeError("Cannot open webcam")

    # per-employee cooldown
    last_sent_by_emp: Dict[int, float] = {}
    # per-employee hit counter (để yêu cầu match liên tiếp)
    hit_count_by_emp: Dict[int, int] = {}

    print("[RUN] ESC to quit")
    while True:
        ok, frame = cap.read()
        if not ok:
            break

        # tăng tốc: resize frame
        small = cv2.resize(frame, (0, 0), fx=FRAME_RESIZE, fy=FRAME_RESIZE)
        rgb = cv2.cvtColor(small, cv2.COLOR_BGR2RGB)

        boxes = face_recognition.face_locations(rgb, model=MODEL)

        # reset hit counts mỗi frame (giữ lại logic theo emp)
        seen_emps_this_frame = set()

        if boxes:
            encs = face_recognition.face_encodings(rgb, boxes)

            for (top, right, bottom, left), enc in zip(boxes, encs):
                emp_id, score = match_face(enc, db)

                # scale box về frame gốc để vẽ
                top2 = int(top / FRAME_RESIZE)
                right2 = int(right / FRAME_RESIZE)
                bottom2 = int(bottom / FRAME_RESIZE)
                left2 = int(left / FRAME_RESIZE)

                if emp_id is None:
                    cv2.rectangle(frame, (left2, top2), (right2, bottom2), (0, 0, 255), 2)
                    cv2.putText(
                        frame, "Unknown",
                        (left2, top2 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2
                    )
                    continue

                seen_emps_this_frame.add(emp_id)

                # tăng hit counter cho emp match
                hit_count_by_emp[emp_id] = hit_count_by_emp.get(emp_id, 0) + 1

                cv2.rectangle(frame, (left2, top2), (right2, bottom2), (0, 255, 0), 2)
                cv2.putText(
                    frame, f"ID:{emp_id} score:{score:.2f} hit:{hit_count_by_emp[emp_id]}",
                    (left2, top2 - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2
                )

                # chỉ gửi khi đủ hit liên tiếp
                if hit_count_by_emp[emp_id] < REQUIRE_CONSISTENT_HITS:
                    continue

                now = time.time()
                last = last_sent_by_emp.get(emp_id, 0.0)
                if now - last < MIN_SECONDS_BETWEEN_HITS:
                    continue

                # tạo 1–2 ảnh minh chứng (demo: 1 ảnh current frame)
                b64 = bgr_to_b64jpg(frame, quality=JPEG_QUALITY)
                ts_local = time.strftime("%Y-%m-%d %H:%M:%S")

                try:
                    # action = toggle để Odoo tự quyết định check_in/out theo trạng thái mở
                    resp = post_attendance_to_odoo(
                        employee_id=emp_id,
                        action="toggle",
                        images_b64=[b64],
                        confidence=score,
                        ts_local=ts_local
                    )
                    print("[ODOO]", resp)
                    last_sent_by_emp[emp_id] = now
                    hit_count_by_emp[emp_id] = 0  # reset sau khi gửi thành công
                except Exception as e:
                    print("[ERROR]", str(e))
                    # không reset hit để còn thử lại, nhưng bạn có thể reset tùy ý

        # reset hit counter cho emp không xuất hiện ở frame này
        for emp in list(hit_count_by_emp.keys()):
            if emp not in seen_emps_this_frame:
                hit_count_by_emp[emp] = 0

        cv2.imshow("Camera Attendance (Level 2 Ready)", frame)
        if cv2.waitKey(1) & 0xFF == 27:  # ESC
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
