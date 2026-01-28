# -*- coding: utf-8 -*-
from odoo import api, fields, models


class HrPayslip(models.Model):
    _inherit = "bj.hr.payslip"

    bhyt_base_amount = fields.Monetary(string="BHYT Base", currency_field="currency_id", readonly=True)
    bhyt_employee_amount = fields.Monetary(string="BHYT (Employee)", currency_field="currency_id", readonly=True)
    bhyt_company_amount = fields.Monetary(string="BHYT (Company)", currency_field="currency_id", readonly=True)

    def _bj_get_basic_salary(self):
        """Try to resolve basic salary from employee field -> contract -> 0."""
        self.ensure_one()
        emp = self.employee_id
        if emp.insurance_basic_salary:
            return emp.insurance_basic_salary

        # nếu bạn có contract:
        contract = getattr(self, "contract_id", False)
        if contract and getattr(contract, "wage", 0.0):
            return contract.wage

        return 0.0

    def _bj_get_gross_salary(self):
        """Academic: if you already compute gross somewhere, link it here.
        For now, fallback to basic salary.
        """
        self.ensure_one()
        # nếu module bạn đã có field gross thì dùng luôn, ví dụ: self.gross_salary
        return self._bj_get_basic_salary()

    def bj_compute_bhyt(self):
        """Compute BHYT amounts and store on payslip."""
        Config = self.env["bj.insurance.config"]
        for slip in self:
            cfg = Config.get_current_config(date=slip.date_to or slip.date_from)
            if not cfg:
                slip.bhyt_base_amount = 0.0
                slip.bhyt_employee_amount = 0.0
                slip.bhyt_company_amount = 0.0
                continue

            base = slip._bj_get_basic_salary() if cfg.base_type == "basic" else slip._bj_get_gross_salary()

            # cap
            if cfg.cap_amount and cfg.cap_amount > 0:
                base = min(base, cfg.cap_amount)

            slip.bhyt_base_amount = base
            slip.bhyt_employee_amount = base * (cfg.bhyt_employee_rate / 100.0)
            slip.bhyt_company_amount = base * (cfg.bhyt_company_rate / 100.0)

    # Hook vào compute_sheet (thường có trong hr_payroll hoặc module payslip custom)
    def compute_sheet(self):
        res = super().compute_sheet()
        self.bj_compute_bhyt()
        return res
