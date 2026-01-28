from datetime import date
from odoo import api, fields, models
from odoo.exceptions import UserError


class BjHrPayslipRun(models.Model):
    _name = "bj.hr.payslip.run"
    _description = "BJ Payslip Run"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "date_from desc, id desc"

    name = fields.Char(required=True, default="Payroll Batch")
    date_from = fields.Date(required=True, default=lambda self: date.today().replace(day=1))
    date_to = fields.Date(required=True, default=lambda self: date.today())
    company_id = fields.Many2one("res.company", default=lambda self: self.env.company, required=True)

    state = fields.Selection(
        [("draft", "Draft"), ("generated", "Generated"), ("computed", "Computed"), ("confirmed", "Confirmed")],
        default="draft",
        tracking=True,
    )

    slip_ids = fields.One2many("bj.hr.payslip", "payslip_run_id")
    slip_count = fields.Integer(compute="_compute_slip_count")

    @api.depends("slip_ids")
    def _compute_slip_count(self):
        for r in self:
            r.slip_count = len(r.slip_ids)

    def action_generate_payslips(self):
        for run in self:
            if run.state != "draft":
                raise UserError("You can only generate payslips in Draft state.")

            employees = self.env["hr.employee"].search([("company_id", "=", run.company_id.id)])
            if not employees:
                continue

            for emp in employees:
                self.env["bj.hr.payslip"].create(
                    {
                        "employee_id": emp.id,
                        "company_id": run.company_id.id,
                        "date_from": run.date_from,
                        "date_to": run.date_to,
                        "payslip_run_id": run.id,
                    }
                )

            run.state = "generated"
        return True

    def action_compute_all(self):
        for run in self:
            if run.state not in ("generated", "computed"):
                raise UserError("Compute is allowed only after payslips are generated.")
            run.slip_ids.action_compute()
            run.state = "computed"
        return True

    def action_confirm_all(self):
        for run in self:
            run.slip_ids.action_confirm()
            run.state = "confirmed"
        return True

    def action_set_draft(self):
        for run in self:
            run.slip_ids.action_set_draft()
            run.state = "draft"
        return True
