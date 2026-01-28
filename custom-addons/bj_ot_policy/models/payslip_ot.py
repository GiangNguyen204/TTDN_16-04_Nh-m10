from datetime import timedelta
from odoo import fields, models


class BjHrPayslip(models.Model):
    _inherit = "bj.hr.payslip"

    ot_amount = fields.Monetary(default=0.0, tracking=True)
    night_allowance_amount = fields.Monetary(default=0.0, tracking=True)

    def _is_holiday(self, policy, d):
        if not policy.holiday_dates:
            return False
        items = [x.strip() for x in policy.holiday_dates.split(",") if x.strip()]
        return d.isoformat() in items

    def _compute_ot_amount(self):
        policy = self.env["bj.ot.policy"].get_default_policy()

        for slip in self:
            emp = slip.employee_id
            hourly = emp.bj_hourly_rate or 0.0

            # Determine date type based on slip.date_to (demo). You can refine to per-day OT later.
            d = slip.date_to
            rate = policy.weekday_rate
            if d and d.weekday() >= 5:
                rate = policy.weekend_rate
            if d and self._is_holiday(policy, d):
                rate = policy.holiday_rate

            if (slip.ot_hours * 60) < (policy.min_ot_minutes or 0):
                slip.ot_amount = 0.0
            else:
                slip.ot_amount = hourly * slip.ot_hours * rate

            slip.night_allowance_amount = (policy.night_shift_allowance or 0.0) * (slip.night_shift_days or 0.0)

    def _compute_net(self):
        # let core compute net first
        super()._compute_net()
        # then add OT / night allowance (as allowances)
        self._compute_ot_amount()
        for slip in self:
            slip.net_salary += (slip.ot_amount + slip.night_allowance_amount)
            slip.total_allowance += (slip.ot_amount + slip.night_allowance_amount)
