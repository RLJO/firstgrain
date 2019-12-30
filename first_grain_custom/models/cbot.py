from odoo import api,fields,models,_
from datetime import datetime, timedelta, time



class CBOT(models.Model):
    _name = 'cbot.form'

    name = fields.Char('Name')
    po_number = fields.Many2one('purchase.order','PO Number')
    commodity = fields.Many2one('product.product','Commodity')
    premium_date = fields.Datetime('Premium Date')
    premium_price = fields.Float('Premium Price')
    cbot = fields.Float('CBOT')
    protection = fields.Char('Protection')
    conversion_rate = fields.Float('Conversion Rate')
    final_price  = fields.Float('Final Price')

    def action_update_cbot(self):
        po_line = self.env['purchase.order.line'].search([('order_id','=',self.po_number.id)])
        for line in po_line:
            line.update({
                'product_id': self.commodity.id,
                'premium_price': self.premium_price,
                'cbot_price': self.cbot
            })
