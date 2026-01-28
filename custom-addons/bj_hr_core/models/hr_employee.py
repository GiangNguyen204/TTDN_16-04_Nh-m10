from odoo import api, fields, models

class HrEmployee(models.Model):
    _inherit = "hr.employee"

    wage_type = fields.Selection(
        [("hour", "Theo giờ"), ("day", "Theo ngày"), ("month", "Theo tháng")],
        default="month",
        string="Hình thức lương",
        tracking=True,
    )
    base_wage = fields.Monetary(string="Lương cơ bản", currency_field="currency_id", tracking=True)
    currency_id = fields.Many2one("res.currency", default=lambda self: self.env.company.currency_id.id)

    # 3 ảnh mẫu khuôn mặt (demo lưu attachment/binary trong Odoo)
    face_image_1 = fields.Binary(string="Ảnh mẫu 1")
    face_image_2 = fields.Binary(string="Ảnh mẫu 2")
    face_image_3 = fields.Binary(string="Ảnh mẫu 3")

    # embedding (vector) lưu dạng text (JSON string) cho demo
    face_embedding_json = fields.Text(string="Face embedding (JSON)")
