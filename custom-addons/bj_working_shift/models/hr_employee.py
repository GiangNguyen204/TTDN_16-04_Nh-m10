from odoo import fields, models


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    shift_id = fields.Many2one(
        "bj.working.shift",
        string="Ca làm việc",
        help="Ca làm chính của nhân viên (Level 2: dùng để tính đi muộn/về sớm/OT).",
    )
