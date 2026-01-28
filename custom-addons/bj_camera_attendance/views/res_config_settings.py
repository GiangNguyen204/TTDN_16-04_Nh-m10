from odoo import fields, models

class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    camera_api_token = fields.Char(
        string="Camera API Token",
        config_parameter="bj_camera_attendance.api_token",
    )
