from odoo import api,fields,models,_
from datetime import datetime, timedelta, time



class DeliveryOrderType(models.Model):
    _name = 'delivery.order.type'

    delivery_order_id = fields.Many2one('stock.picking','Delivery Order')
    customer_id = fields.Many2one('res.partner','Customer')
    qty = fields.Float('Quantity')
    product_id = fields.Many2one('product.template')

    bill_leading_id = fields.Many2one('bill_leading','Bill Leading')