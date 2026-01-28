from datetime import date
from odoo import api, fields, models
from odoo.exceptions import UserError


class BjHrPayslip(models.Model):
    _name = "bj.hr.payslip"
    _description = "BJ Payslip"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "date_from desc, id desc"

    name = fields.Char(default="New", copy=False, readonly=True)
    employee_id = fields.Many2one("hr.employee", required=True, index=True)
    company_id = fields.Many2one("res.company", default=lambda self: self.env.company, required=True)
    currency_id = fields.Many2one(related="company_id.currency_id", store=True, readonly=True)

    date_from = fields.Date(required=True, default=lambda self: date.today().replace(day=1))
    date_to = fields.Date(required=True, default=lambda self: date.today())
    month = fields.Integer(compute="_compute_month_year", store=True)
    year = fields.Integer(compute="_compute_month_year", store=True)

    state = fields.Selection(
        [("draft", "Draft"), ("computed", "Computed"), ("confirmed", "Confirmed"), ("cancelled", "Cancelled")],
        default="draft",
        tracking=True,
    )

    # attendance inputs
    work_days = fields.Float(default=0.0, tracking=True)
    work_hours = fields.Float(default=0.0, tracking=True)
    ot_hours = fields.Float(default=0.0, tracking=True)
    late_minutes = fields.Integer(default=0, tracking=True)
    early_minutes = fields.Integer(default=0, tracking=True)
    night_shift_days = fields.Float(default=0.0, tracking=True)

    # money
    gross_salary = fields.Monetary(default=0.0, tracking=True)
    total_allowance = fields.Monetary(default=0.0, tracking=True)
    total_deduction = fields.Monetary(default=0.0, tracking=True)
    net_salary = fields.Monetary(default=0.0, tracking=True)

    # link to pay run
    payslip_run_id = fields.Many2one("bj.hr.payslip.run", ondelete="set null")

    line_ids = fields.One2many("bj.hr.payslip.line", "payslip_id", copy=True)

    def _get_attendance_monthly_model(self):
        """
        Try common model names. If your existing module uses a different model name,
        add it here.
        """
        for model in ("bj.attendance.monthly", "attendance.monthly", "hr.attendance.monthly"):
            if model in self.env:
                return model
        return None

    def _load_from_attendance_monthly(self):
        model_name = self._get_attendance_monthly_model()
        if not model_name:
            return  # silently skip

        Monthly = self.env[model_name]

        for slip in self:
            # Try to find a monthly record for the employee in the same month/year
            # This is a best-effort integration.
            domain = [
                ("employee_id", "=", slip.employee_id.id),
            ]
            # try fields month/year or date range
            if "month" in Monthly._fields and "year" in Monthly._fields:
                domain += [("month", "=", slip.month), ("year", "=", slip.year)]
            elif "date_from" in Monthly._fields and "date_to" in Monthly._fields:
                domain += [("date_from", "<=", slip.date_to), ("date_to", ">=", slip.date_from)]

            rec = Monthly.search(domain, limit=1, order="id desc")
            if not rec:
                continue

            # map common field names
            def _get_any(r, names, default=0.0):
                for n in names:
                    if n in r._fields:
                        return r[n] or default
                return default

            slip.work_days = float(_get_any(rec, ["work_days", "worked_days", "days_worked"], 0.0))
            slip.work_hours = float(_get_any(rec, ["work_hours", "worked_hours", "hours_worked"], 0.0))
            slip.ot_hours = float(_get_any(rec, ["ot_hours", "overtime_hours"], 0.0))
            slip.late_minutes = int(_get_any(rec, ["late_minutes", "late_min"], 0))
            slip.early_minutes = int(_get_any(rec, ["early_minutes", "early_min"], 0))
            slip.night_shift_days = float(_get_any(rec, ["night_shift_days", "night_days"], 0.0))

    @api.depends("date_from", "date_to")
    def _compute_month_year(self):
        for slip in self:
            d = slip.date_from or date.today()
            slip.month = d.month
            slip.year = d.year

    @api.model_create_multi
    def create(self, vals_list):
        seq = self.env["ir.sequence"]
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = seq.next_by_code("bj.hr.payslip") or "PSL"
        return super().create(vals_list)

    def action_load_attendance(self):
        self._load_from_attendance_monthly()

    def _compute_gross(self):
        for slip in self:
            emp = slip.employee_id
            if not emp:
                slip.gross_salary = 0.0
                continue

            base = emp.bj_base_salary or 0.0
            if emp.bj_salary_type == "month":
                denom = emp.bj_standard_work_days or 26.0
                slip.gross_salary = base * (slip.work_days / denom) if denom else 0.0
            elif emp.bj_salary_type == "day":
                slip.gross_salary = base * slip.work_days
            else:
                slip.gross_salary = base * slip.work_hours

    def _apply_rules(self):
        Rule = self.env["bj.payroll.rule"]
        rules = Rule.search([("active", "=", True)], order="sequence asc, id asc")

        for slip in self:
            slip.line_ids.unlink()
            allowance = 0.0
            deduction = 0.0

            for rule in rules:
                if rule.amount_type == "fixed":
                    amt = rule.amount
                else:
                    amt = slip.gross_salary * (rule.amount / 100.0)

                self.env["bj.hr.payslip.line"].create(
                    {
                        "payslip_id": slip.id,
                        "rule_id": rule.id,
                        "code": rule.code,
                        "name": rule.name,
                        "rule_type": rule.rule_type,
                        "amount": amt,
                    }
                )

                if rule.rule_type == "allowance":
                    allowance += amt
                else:
                    deduction += amt

            slip.total_allowance = allowance
            slip.total_deduction = deduction

    def _compute_net(self):
        for slip in self:
            slip.net_salary = slip.gross_salary + slip.total_allowance - slip.total_deduction

    def action_compute(self):
        for slip in self:
            if slip.state not in ("draft", "computed"):
                raise UserError("Only Draft/Computed payslips can be computed.")
        self.action_load_attendance()
        self._compute_gross()
        self._apply_rules()
        # Insurance/Tax module (if installed) can override/extend via inheritance
        self._compute_net()
        self.write({"state": "computed"})
        return True

    def action_confirm(self):
        self.write({"state": "confirmed"})
        return True

    def action_set_draft(self):
        self.write({"state": "draft"})
        return True

    def action_cancel(self):
        self.write({"state": "cancelled"})
        return True


class BjHrPayslipLine(models.Model):
    _name = "bj.hr.payslip.line"
    _description = "BJ Payslip Line"
    _order = "id asc"

    payslip_id = fields.Many2one("bj.hr.payslip", required=True, ondelete="cascade")
    rule_id = fields.Many2one("bj.payroll.rule", ondelete="set null")
    name = fields.Char(required=True)
    code = fields.Char()
    rule_type = fields.Selection([("allowance", "Allowance"), ("deduction", "Deduction")], required=True)
    amount = fields.Monetary(required=True, default=0.0)
    currency_id = fields.Many2one(related="payslip_id.currency_id", store=True, readonly=True)
