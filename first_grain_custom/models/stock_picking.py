from odoo import api,fields,models,_
from datetime import datetime, timedelta, time



class Inventory(models.Model):
    _inherit = 'stock.picking'

    bill_leading_id = fields.Many2one('bill.leading','Bill No')