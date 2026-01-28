{
    "name": "BJ Leave & OT Workflow",
    "version": "19.0.1.0.0",
    "category": "Human Resources",
    "summary": "Leave request + OT request workflow with approval and attendance adjustments",
    "depends": ["base", "mail", "hr", "bj_payroll_core"],
    "data": [
        "security/ir.model.access.csv",
        "views/leave_request_views.xml",
        "views/ot_request_views.xml",
    ],
    "installable": True,
    "application": False,
    "license": "LGPL-3",
}
