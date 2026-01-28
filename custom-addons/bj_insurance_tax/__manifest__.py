{
    "name": "BJ Insurance & Tax",
    "version": "19.0.1.0.0",
    "category": "Human Resources",
    "summary": "Insurance + Personal income tax computation for BJ custom payslips",
    "depends": ["base", "mail", "hr", "bj_payroll_core"],
    "data": [
        "security/ir.model.access.csv",
        "views/ins_tax_config_views.xml",
        "views/hr_employee_views.xml",
        "views/payslip_views.xml",
    ],
    "installable": True,
    "application": False,
    "license": "LGPL-3",
}
