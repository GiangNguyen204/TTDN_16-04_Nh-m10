from odoo import fields, models
from odoo.exceptions import UserError


class BjOtRequest(models.Model):
    _name = "bj.ot.request"
    _description = "BJ OT Request"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "create_date desc"

    name = fields.Char(default="OT Request", required=True)
    employee_id = fields.Many2one("hr.employee", required=True, index=True)
    company_id = fields.Many2one(related="employee_id.company_id", store=True, readonly=True)

    date = fields.Date(required=True)
    hours = fields.Float(required=True, default=1.0)
    reason = fields.Text()
    approver_id = fields.Many2one("res.users", default=lambda self: self.env.user, tracking=True)

    state = fields.Selection(
        [("draft", "Draft"), ("submitted", "Submitted"), ("approved", "Approved"), ("rejected", "Rejected")],
        default="draft",
        tracking=True,
    )

    def action_submit(self):
        for r in self:
            if r.hours <= 0:
                raise UserError("OT hours must be positive.")
        self.write({"state": "submitted"})
        return True

    def action_approve(self):
        self._create_ot_approved()
        self.write({"state": "approved"})
        return True

    def action_reject(self):
        self.write({"state": "rejected"})
        return True

    def _create_ot_approved(self):
        Ot = self.env["bj.ot.approved"]
        for r in self:
            Ot.create(
                {
                    "employee_id": r.employee_id.id,
                    "date": r.date,
                    "hours": r.hours,
                    "reason": r.reason or "",
                    "source_ref": f"ot:{r.id}",
                }
            )
