from odoo import api,fields,models,_
from datetime import datetime, timedelta, time



class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    limit_up_to = fields.Float('Limit Up To')
    premium_from = fields.Float('Premium Form')
    purchase_type = fields.Selection([('local','Local Purchase'),('semi_local','Semi Local Purchase'),('international','International Purchase'),('semi_international','Semi International Purchase')] , string="Purchase Type")

    shipment_from = fields.Datetime('Shipment Period From')
    shipment_to = fields.Datetime('Shipment Period To')

    notification_status = fields.Char()

    is_account_advisor = fields.Boolean(compute='_is_account_advisor')

    def _is_account_advisor(self):
        self.is_account_advisor = self.env.user.has_group('account.group_account_manager')




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

    def action_request_payment_term(self):
        account_manager_id = self.env.ref('account.group_account_manager').id
        user_ids = self.env['res.users'].search([('groups_id', 'in', [account_manager_id])])
        if user_ids:
            self.notification_status = 'Payment Requested for ' + self.name
            for user_id in user_ids:
                activity_ins = self.env['mail.activity'].sudo().create(
                    {'res_id': self.id,
                     'res_model_id': self.env['ir.model'].search([('model', '=', 'purchase.order')], limit=1).id,
                     'res_model': 'purchase.order',
                     'activity_type_id': 6,
                     'summary': 'Payment Term request',
                     'note': 'Payment Requested for ' + self.name ,
                     'date_deadline': fields.Date.today(),
                     'activity_category': 'default',
                     'previous_activity_type_id': False,
                     'recommended_activity_type_id': False,
                     'user_id': user_id.id
                     })
