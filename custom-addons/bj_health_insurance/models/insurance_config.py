# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class BjInsuranceConfig(models.Model):
    _name = "bj.insurance.config"
    _description = "BJ Insurance Config"
    _order = "date_from desc, id desc"

    name = fields.Char(default="Insurance Config", required=True)
    active = fields.Boolean(default=True)

    date_from = fields.Date(required=True, default=fields.Date.today)
    date_to = fields.Date()

    # % NLĐ và % DN (đồ án có thể để nhập tay)
    bhyt_employee_rate = fields.Float(string="BHYT (Employee %) ", required=True, default=1.5)
    bhyt_company_rate = fields.Float(string="BHYT (Company %) ", required=True, default=3.0)

    base_type = fields.Selection(
        [
            ("basic", "Basic Salary"),
            ("gross", "Gross Salary"),
        ],
        string="Insurance Base",
        default="basic",
        required=True,
    )

    # Trần đóng BH (tuỳ chọn)
    cap_amount = fields.Monetary(string="Cap Amount", default=0.0, help="0 = no cap")
    currency_id = fields.Many2one("res.currency", default=lambda self: self.env.company.currency_id.id, required=True)

    @api.constrains("date_from", "date_to")
    def _check_dates(self):
        for r in self:
            if r.date_to and r.date_to < r.date_from:
                raise ValidationError(_("date_to must be >= date_from"))

    @api.model
    def get_current_config(self, date=None):
        """Get active config by date (payslip date)."""
        date = date or fields.Date.today()
        domain = [
            ("active", "=", True),
            ("date_from", "<=", date),
            "|",
            ("date_to", "=", False),
            ("date_to", ">=", date),
        ]
        return self.search(domain, limit=1)
