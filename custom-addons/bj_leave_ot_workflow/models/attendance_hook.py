from odoo import fields, models


class BjAttendanceAdjustment(models.Model):
    _name = "bj.attendance.adjustment"
    _description = "BJ Attendance Adjustment"
    _order = "date_from desc, id desc"

    employee_id = fields.Many2one("hr.employee", required=True, index=True)
    adjustment_type = fields.Selection([("leave", "Leave")], required=True, default="leave")
    date_from = fields.Datetime(required=True)
    date_to = fields.Datetime(required=True)
    hours = fields.Float(default=0.0)
    reason = fields.Text()
    source_ref = fields.Char(index=True)


class BjOtApproved(models.Model):
    _name = "bj.ot.approved"
    _description = "BJ Approved Overtime"
    _order = "date desc, id desc"

    employee_id = fields.Many2one("hr.employee", required=True, index=True)
    date = fields.Date(required=True)
    hours = fields.Float(required=True, default=1.0)
    reason = fields.Text()
    source_ref = fields.Char(index=True)
