{
    "name": "BJ Attendance Monthly Summary",
    "summary": "Monthly attendance summary per employee (work hours, days, late/early demo)",
    "version": "19.0.1.0.0",
    "category": "Human Resources",
    "author": "Giang Nguyen",
    "license": "LGPL-3",
    "depends": ["bj_attendance_core"],
    "data": [
        # "security/ir.model.access.csv",   # <-- TẠM TẮT ĐỂ CÀI ĐƯỢC
        "views/attendance_monthly_views.xml",
    ],
    "application": True,
    "installable": True,
}
