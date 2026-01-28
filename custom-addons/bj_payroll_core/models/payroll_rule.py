from odoo import api, fields, models
from odoo.exceptions import ValidationError


class BjPayrollRule(models.Model):
    _name = "bj.payroll.rule"
    _description = "BJ Payroll Rule"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "sequence, id"

    name = fields.Char(required=True, tracking=True)
    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)

    code = fields.Char(required=True, tracking=True)
    rule_type = fields.Selection(
        [("allowance", "Allowance"), ("deduction", "Deduction")],
        required=True,
        default="allowance",
        tracking=True,
    )
    amount_type = fields.Selection(
        [("fixed", "Fixed"), ("percent", "Percent of Gross")],
        required=True,
        default="fixed",
        tracking=True,
    )
    amount = fields.Float(default=0.0, tracking=True)

    @api.constrains("code")
    def _check_code_unique(self):
        for r in self:
            if self.search_count([("code", "=", r.code), ("id", "!=", r.id)]) > 0:
                raise ValidationError("Payroll rule code must be unique.")
