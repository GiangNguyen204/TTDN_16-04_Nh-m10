{
    "name": "BJ Payroll Core",
    "version": "19.0.1.0.0",
    "category": "Human Resources",
    "summary": "Custom payroll core: payslip + pay run + payroll rules",
    "depends": ["base", "mail", "hr"],
    "data": [
        "security/ir.model.access.csv",
        "data/sequence.xml",
        "views/payroll_menus.xml",
        "views/hr_employee_views.xml",
        "views/payroll_rule_views.xml",
        "views/hr_payslip_views.xml",
        "views/hr_payslip_run_views.xml",
    ],
    "installable": True,
    "application": True,
    "license": "LGPL-3",
}
