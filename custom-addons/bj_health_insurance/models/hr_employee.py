# -*- coding: utf-8 -*-
from odoo import fields, models


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    insurance_basic_salary = fields.Monetary(
        string="Insurance Basic Salary",
        help="Salary base used for insurance (BHYT). If empty, module will try contract wage / payslip wage.",
        currency_field="currency_id",
    )
    currency_id = fields.Many2one("res.currency", related="company_id.currency_id", readonly=True)
