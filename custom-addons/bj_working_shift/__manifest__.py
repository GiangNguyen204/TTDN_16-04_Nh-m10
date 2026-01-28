{
    "name": "BJ Working Shift",
    "version": "19.0.1.0.0",
    "category": "Human Resources",
    "summary": "Working shifts for employees (Level 2: late/early/OT base)",
    "author": "Giang Nguyen",
    "license": "LGPL-3",
    "depends": [
        "hr",
        "bj_attendance_core",      # để đồng bộ chuỗi module bạn đang xây
        "bj_attendance_monthly",   # monthly sẽ đọc shift_id để tính late/early/OT
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/working_shift_views.xml",
        "views/hr_employee_views.xml",
    ],
    "application": True,
    "installable": True,
}
