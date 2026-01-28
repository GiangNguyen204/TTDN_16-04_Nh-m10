from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
import base64


class HrAttendance(models.Model):
    _inherit = "hr.attendance"

    # =========================
    # LEVEL 1: Source + Evidence
    # =========================
    source = fields.Selection(
        [
            ("manual", "Thủ công"),
            ("camera", "Camera"),
            ("device", "Thiết bị"),
        ],
        string="Nguồn chấm công",
        default="manual",
        index=True,
        required=True,  # Level 2: bật luôn để dữ liệu sạch
    )

    evidence_attachment_ids = fields.Many2many(
        "ir.attachment",
        "hr_attendance_ir_attachment_rel",
        "attendance_id",
        "attachment_id",
        string="Ảnh minh chứng",
        help="Ảnh chụp tại thời điểm chấm công (demo lưu trong Odoo attachment).",
    )

    # =========================
    # LEVEL 2: Camera metadata (ăn điểm)
    # =========================
    camera_device_id = fields.Char(
        string="Thiết bị camera",
        index=True,
        help="Mã thiết bị gửi dữ liệu (VD: LAPTOP_CAM_01).",
    )

    camera_confidence = fields.Float(
        string="Độ tin cậy nhận diện",
        digits=(3, 2),
        help="Điểm tin cậy match khuôn mặt (0..1) gửi từ client.",
    )

    camera_ts_local = fields.Char(
        string="Thời gian máy chấm (local)",
        help="Timestamp do máy chấm gửi lên (phục vụ đối soát/demo).",
    )

    # Optional: lưu raw payload (demo / audit)
    camera_payload_json = fields.Text(
        string="Camera payload (JSON)",
        help="Lưu payload thô để audit (demo).",
    )

    # =========================
    # VALIDATION
    # =========================
    @api.constrains("camera_confidence")
    def _check_camera_confidence(self):
        for rec in self:
            if rec.camera_confidence and (rec.camera_confidence < 0 or rec.camera_confidence > 1):
                raise ValidationError(_("camera_confidence phải nằm trong khoảng 0..1"))

    # =========================
    # HELPERS: dùng trong Controller
    # =========================
    def _create_evidence_attachments_from_b64(self, images_b64, employee_id=None):
        """
        Tạo ir.attachment từ list base64 JPEG/PNG.
        Trả về recordset attachments.
        """
        Attachment = self.env["ir.attachment"].sudo()
        created = self.env["ir.attachment"]

        if not images_b64:
            return created

        for i, b64 in enumerate(images_b64, start=1):
            # validate base64 (nhẹ)
            try:
                base64.b64decode(b64, validate=True)
            except Exception:
                continue

            name = f"attendance_evidence_emp{employee_id or 'x'}_{fields.Datetime.now()}_{i}.jpg"
            att = Attachment.create(
                {
                    "name": name,
                    "type": "binary",
                    "datas": b64,
                    "mimetype": "image/jpeg",
                    "res_model": "hr.attendance",
                    # res_id set sau khi attendance create (bên dưới)
                }
            )
            created |= att

        return created

    @api.model
    def camera_toggle_attendance(
        self,
        employee_id: int,
        images_b64=None,
        device_id=None,
        confidence=None,
        ts_local=None,
        payload_dict=None,
    ):
        """
        Level 2 entrypoint:
        - Nếu nhân viên đang có attendance mở (check_in chưa có check_out) => check_out
        - Nếu không => tạo check_in mới
        - Đính kèm ảnh minh chứng (nếu có)
        - Lưu metadata camera để audit + tổng hợp ca/OT
        """
        images_b64 = images_b64 or []
        payload_dict = payload_dict or {}

        Attendance = self.sudo()
        now_dt = fields.Datetime.now()

        # tìm attendance đang mở gần nhất
        open_att = Attendance.search(
            [("employee_id", "=", employee_id), ("check_out", "=", False)],
            order="check_in desc",
            limit=1,
        )

        if open_att:
            # CHECK OUT
            open_att.write(
                {
                    "check_out": now_dt,
                    "source": "camera",
                    "camera_device_id": device_id,
                    "camera_confidence": confidence,
                    "camera_ts_local": ts_local,
                    "camera_payload_json": payload_dict and str(payload_dict) or False,
                }
            )
            att_rec = open_att
            action = "check_out"
        else:
            # CHECK IN
            att_rec = Attendance.create(
                {
                    "employee_id": employee_id,
                    "check_in": now_dt,
                    "source": "camera",
                    "camera_device_id": device_id,
                    "camera_confidence": confidence,
                    "camera_ts_local": ts_local,
                    "camera_payload_json": payload_dict and str(payload_dict) or False,
                }
            )
            action = "check_in"

        # tạo attachments và link vào attendance
        atts = att_rec._create_evidence_attachments_from_b64(images_b64, employee_id=employee_id)
        if atts:
            # gắn res_id để attachment “thuộc” attendance
            atts.write({"res_model": "hr.attendance", "res_id": att_rec.id})
            att_rec.write({"evidence_attachment_ids": [(4, a.id) for a in atts]})

        return {
            "status": "success",
            "action": action,
            "attendance_id": att_rec.id,
            "employee_id": employee_id,
            "check_in": att_rec.check_in,
            "check_out": att_rec.check_out,
            "attachments": [a.id for a in atts],
        }
