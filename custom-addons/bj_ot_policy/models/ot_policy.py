from odoo import api, fields, models


class BjOtPolicy(models.Model):
    _name = "bj.ot.policy"
    _description = "BJ OT Policy"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Char(required=True, default="Default OT Policy")
    active = fields.Boolean(default=True)

    weekday_rate = fields.Float(default=1.5, tracking=True)
    weekend_rate = fields.Float(default=2.0, tracking=True)
    holiday_rate = fields.Float(default=3.0, tracking=True)

    night_shift_allowance = fields.Float(default=0.0, tracking=True)
    min_ot_minutes = fields.Integer(default=30, tracking=True)

    holiday_dates = fields.Char(
        string="Holiday Dates (YYYY-MM-DD, comma separated)",
        help="Simple demo list of holidays. Example: 2026-01-01,2026-04-30",
    )

    @api.model
    def get_default_policy(self):
        rec = self.search([("active", "=", True)], limit=1)
        if not rec:
            rec = self.create({"name": "Default OT Policy"})
        return rec
