from odoo import api, fields, models


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    bj_base_salary = fields.Float(string="Base Salary", tracking=True)
    bj_salary_type = fields.Selection(
        [("month", "Monthly"), ("day", "Daily"), ("hour", "Hourly")],
        string="Salary Type",
        default="month",
        tracking=True,
    )
    bj_standard_work_days = fields.Float(string="Standard Work Days/Month", default=26.0)
    bj_standard_work_hours = fields.Float(string="Standard Work Hours/Day", default=8.0)

    @api.depends("bj_base_salary", "bj_salary_type")
    def _compute_bj_hourly_rate(self):
        for emp in self:
            if emp.bj_salary_type == "hour":
                emp.bj_hourly_rate = emp.bj_base_salary
            elif emp.bj_salary_type == "day":
                # daily -> hourly based on standard hours/day
                emp.bj_hourly_rate = (emp.bj_base_salary / (emp.bj_standard_work_hours or 8.0)) if emp.bj_base_salary else 0.0
            else:
                # monthly -> hourly based on standard days/month & hours/day
                denom = (emp.bj_standard_work_days or 26.0) * (emp.bj_standard_work_hours or 8.0)
                emp.bj_hourly_rate = (emp.bj_base_salary / denom) if denom else 0.0

    bj_hourly_rate = fields.Float(string="Derived Hourly Rate", compute=_compute_bj_hourly_rate, store=True)
