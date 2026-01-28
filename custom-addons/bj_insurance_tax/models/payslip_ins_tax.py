from odoo import api, fields, models


class BjHrPayslip(models.Model):
    _inherit = "bj.hr.payslip"

    insurance_total = fields.Monetary(default=0.0, tracking=True)
    taxable_income = fields.Monetary(default=0.0, tracking=True)
    pit_tax = fields.Monetary(string="PIT Tax", default=0.0, tracking=True)

    def _compute_insurance_and_tax(self):
        Config = self.env["bj.ins.tax.config"]
        cfg = Config.get_default_config()

        for slip in self:
            emp = slip.employee_id
            base = (emp.bj_insurance_base_salary or slip.gross_salary) if emp.bj_apply_insurance else 0.0

            bhxh = base * (cfg.bhxh_rate_employee / 100.0)
            bhyt = base * (cfg.bhyt_rate_employee / 100.0)
            bhtn = base * (cfg.bhtn_rate_employee / 100.0)
            slip.insurance_total = bhxh + bhyt + bhtn

            deduction = cfg.personal_deduction + (emp.bj_dependent_count * cfg.dependent_deduction)
            slip.taxable_income = max(0.0, slip.gross_salary - slip.insurance_total - deduction)

            # Simple bracket with optional quick deduction
            pit = 0.0
            brackets = cfg.bracket_ids.sorted("from_amount")
            if brackets:
                for b in brackets:
                    upper = b.to_amount or 0.0
                    if upper and slip.taxable_income > upper:
                        continue
                    if slip.taxable_income >= b.from_amount:
                        pit = (slip.taxable_income * (b.rate / 100.0)) - (b.quick_deduction or 0.0)
                        pit = max(0.0, pit)
                        break
                else:
                    # if taxable income exceeds all upper bounds, take last with no bound
                    last = brackets[-1]
                    if not last.to_amount:
                        pit = max(0.0, (slip.taxable_income * (last.rate / 100.0)) - (last.quick_deduction or 0.0))

            slip.pit_tax = pit

    def _compute_net(self):
        # override net computation: Gross + allowance - deduction - insurance - tax
        for slip in self:
            slip.net_salary = slip.gross_salary + slip.total_allowance - slip.total_deduction

        self._compute_insurance_and_tax()

        for slip in self:
            slip.net_salary = slip.net_salary - slip.insurance_total - slip.pit_tax
