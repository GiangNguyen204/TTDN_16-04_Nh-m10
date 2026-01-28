{
    "name": "BJ Attendance Core",
    "summary": "Extend hr.attendance with source (manual/camera/device) and evidence attachments",
    "version": "19.0.1.0.0",
    "category": "Human Resources",
    "author": "Giang Nguyen",
    "license": "LGPL-3",
    "depends": ["hr_attendance"],
    "data": [
        "security/ir.model.access.csv",
        "views/hr_attendance_views.xml",
    ],
    "application": True,
    "installable": True,
}
