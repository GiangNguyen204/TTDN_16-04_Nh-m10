from odoo import fields, models


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    bj_dependent_count = fields.Integer(string="Dependents", default=0)
    bj_insurance_base_salary = fields.Float(string="Insurance Base Salary (optional)")
    bj_apply_insurance = fields.Boolean(string="Apply Insurance", default=True)
