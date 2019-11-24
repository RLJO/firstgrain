from odoo import api,fields,models,_
from datetime import datetime, timedelta, time



class SaleOrderType(models.Model):
    _name = 'sale.order.type'

    sale_order_id = fields.Many2one('sale.order','Sale Order')
    customer_id = fields.Many2one('res.partner','Customer')
    qty = fields.Float('Quantity')

    bill_leading_id = fields.Many2one('bill_leading','Bill Leading')