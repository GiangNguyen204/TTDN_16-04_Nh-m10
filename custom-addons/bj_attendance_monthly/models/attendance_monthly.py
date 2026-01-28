from datetime import datetime, timedelta
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from odoo.tools.float_utils import float_round


class AttendanceMonthly(models.Model):
    _name = "bj.attendance.monthly"
    _description = "Monthly Attendance Summary"
    _rec_name = "display_name"
    _order = "year desc, month desc, employee_id"

    employee_id = fields.Many2one("hr.employee", required=True, index=True)
    year = fields.Integer(required=True, index=True)
    month = fields.Integer(required=True, index=True)

    # ===== LEVEL 1 =====
    total_work_hours = fields.Float(compute="_compute_totals", store=True)
    total_days = fields.Float(compute="_compute_totals", store=True)

    # ===== LEVEL 2: overtime + sources + late/early =====
    total_ot_hours = fields.Float(compute="_compute_totals", store=True)
    total_late = fields.Integer(compute="_compute_totals", store=True)
    total_early = fields.Integer(compute="_compute_totals", store=True)

    total_camera = fields.Integer(compute="_compute_totals", store=True)
    total_manual = fields.Integer(compute="_compute_totals", store=True)
    total_device = fields.Integer(compute="_compute_totals", store=True)

    display_name = fields.Char(compute="_compute_display_name", store=True)

    @api.depends("employee_id", "year", "month")
    def _compute_display_name(self):
        for r in self:
            if r.employee_id and r.year and r.month:
                r.display_name = f"{r.employee_id.name} - {r.month:02d}/{r.year}"
            else:
                r.display_name = False

    # ---------------------------------
    # Constraints (thay cho _sql_constraints)
    # ---------------------------------
    @api.constrains("employee_id", "year", "month")
    def _check_unique_emp_month(self):
        for r in self:
            if not (r.employee_id and r.year and r.month):
                continue

            if r.month < 1 or r.month > 12:
                raise ValidationError(_("Tháng phải nằm trong khoảng 1..12."))

            dup = self.search_count([
                ("id", "!=", r.id),
                ("employee_id", "=", r.employee_id.id),
                ("year", "=", r.year),
                ("month", "=", r.month),
            ])
            if dup:
                raise ValidationError(_("Đã tồn tại tổng hợp công tháng này cho nhân viên!"))

    # --------------------------
    # Helpers
    # --------------------------
    def _get_month_range(self, year: int, month: int):
        date_start = datetime(year, month, 1)
        if month == 12:
            date_end = datetime(year + 1, 1, 1)
        else:
            date_end = datetime(year, month + 1, 1)
        return date_start, date_end

    def _get_attendances_in_month(self, employee_id: int, date_start, date_end):
        """
        Chỉ lấy attendance có check_in nằm trong tháng.
        Lưu ý: demo đơn giản. Nếu bạn muốn chuẩn thực tế, lọc theo overlap check_in/out.
        """
        return self.env["hr.attendance"].search([
            ("employee_id", "=", employee_id),
            ("check_in", ">=", date_start),
            ("check_in", "<", date_end),
        ])

    def _get_shift_of_employee(self, employee):
        """
        Level 2 hook: nếu bạn làm bj_working_shift và gán employee.shift_id
        thì monthly sẽ tự dùng để tính đi muộn/về sớm/OT.
        """
        return getattr(employee, "shift_id", False)

    def _calc_late_early_ot(self, attendances, shift):
        """
        Demo Level 2:
        - Nếu chưa có shift => late/early = 0, OT = max(0, worked_hours - 8)
        - Nếu có shift (start_time/end_time float giờ):
            + late: check_in > shift_start + threshold
            + early: check_out < shift_end - threshold
            + OT: max(0, worked_hours - shift_hours)
        """
        total_late = 0
        total_early = 0
        total_ot = 0.0

        if not attendances:
            return total_late, total_early, total_ot

        # fallback nếu chưa có shift: lấy 8h/ngày làm chuẩn demo
        if not shift:
            for at in attendances:
                wh = at.worked_hours or 0.0
                total_ot += max(0.0, wh - 8.0)
            return total_late, total_early, float_round(total_ot, 2)

        # Có shift: dùng giờ chuẩn của ca
        shift_hours = max(0.0, (shift.end_time or 0.0) - (shift.start_time or 0.0))
        late_threshold = getattr(shift, "late_threshold", 0) or 0  # phút
        early_threshold = getattr(shift, "early_threshold", 0) or 0  # phút

        for at in attendances:
            if not at.check_in:
                continue

            # build shift start/end datetime theo ngày check_in
            day = at.check_in.date()
            shift_start = datetime(day.year, day.month, day.day) + timedelta(hours=float(shift.start_time or 0.0))
            shift_end = datetime(day.year, day.month, day.day) + timedelta(hours=float(shift.end_time or 0.0))

            # ca qua đêm (end < start) => cộng 1 ngày
            if (shift.end_time or 0.0) < (shift.start_time or 0.0):
                shift_end += timedelta(days=1)

            # late
            if at.check_in and at.check_in > (shift_start + timedelta(minutes=late_threshold)):
                total_late += 1

            # early chỉ tính khi có check_out
            if at.check_out and at.check_out < (shift_end - timedelta(minutes=early_threshold)):
                total_early += 1

            # OT
            wh = at.worked_hours or 0.0
            total_ot += max(0.0, wh - shift_hours)

        return total_late, total_early, float_round(total_ot, 2)

    # --------------------------
    # Main compute
    # --------------------------
    @api.depends("employee_id", "year", "month")
    def _compute_totals(self):
        for r in self:
            # default reset
            r.total_work_hours = 0.0
            r.total_days = 0.0
            r.total_ot_hours = 0.0
            r.total_late = 0
            r.total_early = 0
            r.total_camera = 0
            r.total_manual = 0
            r.total_device = 0

            if not (r.employee_id and r.year and r.month):
                continue

            date_start, date_end = r._get_month_range(r.year, r.month)
            atts = r._get_attendances_in_month(r.employee_id.id, date_start, date_end)

            # Tổng giờ làm
            work_hours = sum((at.worked_hours or 0.0) for at in atts)
            r.total_work_hours = float_round(work_hours, 2)

            # Demo quy đổi công: 8h = 1 công
            r.total_days = float_round(work_hours / 8.0, 2)

            # Đếm nguồn chấm công (Level 2 audit)
            # (field source bạn đã thêm ở bj_attendance_core)
            r.total_camera = len(atts.filtered(lambda a: a.source == "camera"))
            r.total_manual = len(atts.filtered(lambda a: a.source == "manual"))
            r.total_device = len(atts.filtered(lambda a: a.source == "device"))

            # Late/Early/OT theo ca (nếu có)
            shift = r._get_shift_of_employee(r.employee_id)
            late, early, ot_hours = r._calc_late_early_ot(atts, shift)
            r.total_late = late
            r.total_early = early
            r.total_ot_hours = ot_hours
