from odoo import api, fields, models
from odoo.exceptions import ValidationError


class WorkingShift(models.Model):
    _name = "bj.working.shift"
    _description = "Working Shift"
    _order = "name"

    name = fields.Char(string="Tên ca", required=True, index=True)

    # time float: 8.5 = 08:30
    start_time = fields.Float(string="Giờ bắt đầu", required=True, default=8.0)
    end_time = fields.Float(string="Giờ kết thúc", required=True, default=17.0)

    break_minutes = fields.Integer(string="Nghỉ giữa ca (phút)", default=0)
    night_allowance = fields.Float(string="Phụ cấp ca đêm", default=0.0)

    late_threshold = fields.Integer(string="Ngưỡng đi muộn (phút)", default=0)
    early_threshold = fields.Integer(string="Ngưỡng về sớm (phút)", default=0)

    active = fields.Boolean(default=True)

    shift_hours = fields.Float(
        string="Số giờ ca (sau nghỉ)",
        compute="_compute_shift_hours",
        store=True,
        help="Tính tự động: (end - start) - break_minutes/60. Hỗ trợ ca qua đêm.",
    )

    note = fields.Text(string="Ghi chú")

    @api.depends("start_time", "end_time", "break_minutes")
    def _compute_shift_hours(self):
        for r in self:
            start = r.start_time or 0.0
            end = r.end_time or 0.0

            # ca qua đêm: end < start => cộng 24h
            dur = end - start
            if dur < 0:
                dur += 24.0

            break_h = (r.break_minutes or 0) / 60.0
            r.shift_hours = max(0.0, dur - break_h)

    @api.constrains("start_time", "end_time")
    def _check_time_range(self):
        for r in self:
            if (r.start_time is None) or (r.end_time is None):
                continue
            if r.start_time < 0 or r.start_time >= 24:
                raise ValidationError("Giờ bắt đầu phải nằm trong khoảng 0..24")
            if r.end_time < 0 or r.end_time >= 24:
                raise ValidationError("Giờ kết thúc phải nằm trong khoảng 0..24")

    @api.constrains("break_minutes")
    def _check_break(self):
        for r in self:
            if r.break_minutes is not None and r.break_minutes < 0:
                raise ValidationError("Nghỉ giữa ca không được âm")
