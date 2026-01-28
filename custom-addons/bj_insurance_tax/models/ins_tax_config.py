from odoo import api, fields, models
from odoo.exceptions import ValidationError


class BjInsTaxConfig(models.Model):
    _name = "bj.ins.tax.config"
    _description = "BJ Insurance & Tax Config"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Char(default="Default Config", required=True)

    # employee portions (demo)
    bhxh_rate_employee = fields.Float(string="BHXH Employee Rate (%)", default=8.0, tracking=True)
    bhyt_rate_employee = fields.Float(string="BHYT Employee Rate (%)", default=1.5, tracking=True)
    bhtn_rate_employee = fields.Float(string="BHTN Employee Rate (%)", default=1.0, tracking=True)

    personal_deduction = fields.Float(string="Personal Deduction", default=11000000.0, tracking=True)
    dependent_deduction = fields.Float(string="Dependent Deduction", default=4400000.0, tracking=True)

    bracket_ids = fields.One2many("bj.tax.bracket", "config_id", string="Tax Brackets")

    @api.constrains("bhxh_rate_employee", "bhyt_rate_employee", "bhtn_rate_employee")
    def _check_rates(self):
        for r in self:
            for f in ("bhxh_rate_employee", "bhyt_rate_employee", "bhtn_rate_employee"):
                if r[f] < 0 or r[f] > 100:
                    raise ValidationError("Rates must be between 0 and 100.")

    @api.model
    def get_default_config(self):
        rec = self.search([], limit=1)
        if not rec:
            rec = self.create({"name": "Default Config"})
        return rec


class BjTaxBracket(models.Model):
    _name = "bj.tax.bracket"
    _description = "BJ Tax Bracket"
    _order = "from_amount asc"

    config_id = fields.Many2one("bj.ins.tax.config", required=True, ondelete="cascade")
    from_amount = fields.Float(required=True)
    to_amount = fields.Float(help="Leave 0 for no upper limit.")
    rate = fields.Float(string="Rate (%)", required=True)
    quick_deduction = fields.Float(string="Quick Deduction", default=0.0)

    @api.constrains("rate")
    def _check_rate(self):
        for b in self:
            if b.rate < 0 or b.rate > 100:
                raise ValidationError("Tax rate must be between 0 and 100.")
