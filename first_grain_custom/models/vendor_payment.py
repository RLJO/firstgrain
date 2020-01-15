from odoo import api,fields,models,_

from datetime import datetime, timedelta, time



class VendorPayment(models.Model):
    _inherit = "account.payment"

    purchase_order_id = fields.Many2one('purchase.order','Purchase Order')
    action_resort_inside = fields.Selection([('limit_up','Limit Up'),('roll_over','Roll Over'),('partially_priced_Roll_over','Partially Priced - Roll Over'),('other','Other')],'Action Resort Inside')