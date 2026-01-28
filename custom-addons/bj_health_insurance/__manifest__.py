# -*- coding: utf-8 -*-
{
    "name": "BJ Health Insurance (BHYT)",
    "version": "19.0.1.0.0",
    "category": "Human Resources/Payroll",
    "summary": "Academic BHYT module: config rates and auto compute on payslip",
    "depends": [
        "hr",
        # đổi tên đúng module payroll của bạn:
        "bj_payroll_core",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/insurance_config_views.xml",
        "views/hr_employee_views.xml",
        "views/hr_payslip_views.xml",
    ],
    "installable": True,
    "application": False,
}
