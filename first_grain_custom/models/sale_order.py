from odoo import api,fields,models,_
from datetime import datetime, timedelta, time



class SaleOrder(models.Model):
    _inherit = 'sale.order'

    notifi_state = fields.Char()
    delivery_method = fields.Selection([('direct_bulk','Direct Bulk'),('direct_packed','Direct Packed'),('indirect_bulk','Indirect Bulk'),('indirect_packed','Indirect Packed')],'Delivery method')

    def action_confirm(self):
        res = super(SaleOrder, self).action_confirm()

        print("Send Notification")
        self.notifi_state = 'Has Been Confirmed'
        logistic_manger_id = self.env.ref('first_grain_custom.group_logistic_manager').id
        operation_manger_id = self.env.ref('first_grain_custom.group_operation_l_manager').id
        ex_manger_id = self.env.ref('first_grain_custom.group_ex_manager').id
        gm_id = self.env.ref('first_grain_custom.group_gm').id
        ceo_id = self.env.ref('first_grain_custom.group_ceo').id
        user_ids = self.env['res.users'].search(
            [('groups_id', 'in', [logistic_manger_id, operation_manger_id, ex_manger_id,gm_id,ceo_id])])
        if user_ids:
            self.notification_status = 'Sale Order ' + self.name + 'has been confirmed'
            for user_id in user_ids:
                activity_ins = self.env['mail.activity'].sudo().create(
                    {'res_id': self.id,
                     'res_model_id': self.env['ir.model'].search([('model', '=', 'sale.order')], limit=1).id,
                     'res_model': 'sale.order',
                     'activity_type_id': 4,
                     'summary': 'Form 4 Is Done',
                     'note':  'Sale Order ' + self.name + 'has been confirmed',
                     'date_deadline': fields.Date.today() + timedelta(days=1),
                     'activity_category': 'default',
                     'previous_activity_type_id': False,
                     'recommended_activity_type_id': False,
                     'user_id': user_id.id
                     })
