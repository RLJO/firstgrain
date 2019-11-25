from odoo import api, fields, models
from datetime import date


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    discount = fields.Float(string='SalespersonDiscount (%)', digits='Discount', default=0.0)
    discount = fields.Float(string='Discount (%)', digits='Discount', default=0.0)
    discount = fields.Float(string='Discount (%)', digits='Discount', default=0.0)
