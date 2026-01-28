from odoo import api, fields, models
from odoo.exceptions import UserError


class BjLeaveRequest(models.Model):
    _name = "bj.leave.request"
    _description = "BJ Leave Request"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "create_date desc"

    name = fields.Char(default="Leave Request", required=True)
    employee_id = fields.Many2one("hr.employee", required=True, index=True)
    company_id = fields.Many2one(related="employee_id.company_id", store=True, readonly=True)

    date_from = fields.Datetime(required=True)
    date_to = fields.Datetime(required=True)
    leave_type = fields.Selection(
        [("paid", "Paid"), ("unpaid", "Unpaid"), ("sick", "Sick")],
        default="paid",
        required=True,
        tracking=True,
    )
    reason = fields.Text()
    approver_id = fields.Many2one("res.users", default=lambda self: self.env.user, tracking=True)

    state = fields.Selection(
        [("draft", "Draft"), ("submitted", "Submitted"), ("approved", "Approved"), ("rejected", "Rejected")],
        default="draft",
        tracking=True,
    )

    def action_submit(self):
        for r in self:
            if r.date_to <= r.date_from:
                raise UserError("date_to must be after date_from.")
        self.write({"state": "submitted"})
        return True

    def action_approve(self):
        self._create_attendance_adjustment()
        self.write({"state": "approved"})
        return True

    def action_reject(self):
        self.write({"state": "rejected"})
        return True

    def _create_attendance_adjustment(self):
        Adj = self.env["bj.attendance.adjustment"]
        for r in self:
            Adj.create(
                {
                    "employee_id": r.employee_id.id,
                    "adjustment_type": "leave",
                    "date_from": r.date_from,
                    "date_to": r.date_to,
                    "hours": 0.0,
                    "reason": r.reason or "",
                    "source_ref": f"leave:{r.id}",
                }
            )
