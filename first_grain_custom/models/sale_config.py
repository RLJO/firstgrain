from odoo import api, fields, models
from datetime import date


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    sales_person_discount = fields.Float(string='Salesperson Discount (%)', digits='Discount', default=0.0)
    gm_discount = fields.Float(string='GM Discount (%)', digits='Discount', default=0.0)
    ceo_discount = fields.Float(string='CEO Discount (%)', digits='Discount', default=0.0)

    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        res.update(
            sales_person_discount = float(self.env['ir.config_parameter'].get_param('sales_person_discount')),
            gm_discount = float(self.env['ir.config_parameter'].get_param('gm_discount')),
            ceo_discount = float(self.env['ir.config_parameter'].get_param('ceo_discount')),

        )
        return res

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        self.env['ir.config_parameter'].set_param('sales_person_discount', self.sales_person_discount)
        self.env['ir.config_parameter'].set_param('gm_discount', self.gm_discount)
        self.env['ir.config_parameter'].set_param('ceo_discount',self.ceo_discount)
