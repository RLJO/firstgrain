from odoo import api,fields,models,_
from datetime import datetime, timedelta, time



class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    limit_up_to = fields.Float('Limit Up To')
    premium_from = fields.Float('Premium Form')