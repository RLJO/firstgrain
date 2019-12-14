from odoo import api,fields,models,_
from datetime import datetime, timedelta, time



class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    limit_up_to = fields.Float('Limit Up To')
    premium_from = fields.Float('Premium Form')
    purchase_type = fields.Selection([('local','Local Purchase'),('semi_local','Semi Local Purchase'),('international','International Purchase'),('semi_international','Semi International Purchase')] , string="Purchase Type")

    def button_confirm(self):
        res = super(PurchaseOrder,self).button_confirm()
        if res :
            name = self.name + ' contract'
            contract_vals = {
            'name': name,
            'contract_date': fields.Datetime.now(),
            'source_document_rfq': self.id,
            'vendor':self.partner_id.id,
            }

            contract = self.env['contract.form'].create(contract_vals)
        return res