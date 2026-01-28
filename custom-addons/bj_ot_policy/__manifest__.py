{
    "name": "BJ OT Policy",
    "version": "19.0.1.0.0",
    "category": "Human Resources",
    "summary": "Overtime policy (weekday/weekend/holiday) + night shift allowance",
    "depends": ["base", "mail", "bj_payroll_core"],
    "data": [
        "security/ir.model.access.csv",
        "views/ot_policy_views.xml",
    ],
    "installable": True,
    "application": False,
    "license": "LGPL-3",
}
