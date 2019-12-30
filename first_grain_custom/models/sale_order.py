from odoo import api,fields,models,_
from datetime import datetime, timedelta, time



class SaleOrder(models.Model):
    _inherit = 'sale.order'

    notifi_state = fields.Char()
    delivery_method = fields.Selection([('direct_bulk','Direct Bulk'),('direct_packed','Direct Packed'),('indirect_bulk','Indirect Bulk'),('indirect_packed','Indirect Packed')],'Delivery method')
    operation_id = fields.Many2one('operation.logistic','Operation')
    policy_id = fields.Many2one('bill.leading' , 'Policy')

    last_state = fields.Char()
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
                     'note':  'Sale Order ' + self.name + ' has been confirmed',
                     'date_deadline': fields.Date.today() ,
                     'activity_category': 'default',
                     'previous_activity_type_id': False,
                     'recommended_activity_type_id': False,
                     'user_id': user_id.id
                     })

        # Delivery Order Data
        for move in self.picking_ids:
            move.update({'operation_id':self.operation_id.id,
                         'policy_id':self.policy_id.id})

        # Update line in bill of leading
        if self.policy_id:
            for line in self.order_line:
                qty = line.product_uom_qty
            sale_order_line ={
                'sale_order_id':self.id,
                'customer_id':self.partner_id.id,
                'qty':qty,
                'bill_leading_id': self.policy_id.id,

            }
            self.env['sale.order.type'].create(sale_order_line)


    def action_approve_gm_discount(self):
        for line in self.order_line:
            if line.discount > 0.0:
                gm_discount = float(self.env['ir.config_parameter'].get_param('gm_discount'))
                if line.discount > gm_discount:
                    self.state = 'ceo_discount'
                    self.notifi_state = 'Sale Order ' + self.name + ' needs CEO discount Approval'
                    ceo_id = self.env.ref('first_grain_custom.group_ceo').id
                    user_ids = self.env['res.users'].search([('groups_id', 'in', [ceo_id])])
                    if user_ids:
                        for user_id in user_ids:
                            activity_ins = self.env['mail.activity'].sudo().create(
                                {'res_id': self.id,
                                 'res_model_id': self.env['ir.model'].search([('model', '=', 'sale.order')],
                                                                             limit=1).id,
                                 'res_model': 'sale.order',
                                 'activity_type_id': 4,
                                 'summary': 'Form 4 Is Done',
                                 'note': 'Sale Order ' + self.name + ' needs CEO discount Approval',
                                 'date_deadline': fields.Date.today() ,
                                 'activity_category': 'default',
                                 'previous_activity_type_id': False,
                                 'recommended_activity_type_id': False,
                                 'user_id': user_id.id
                                 })
                else :
                    self.state = self.last_state
                    self.notifi_state = 'Sale Order ' + self.name + 'discount Approved'
                    user_ids = [self.user_id]
                    if user_ids:
                        for user_id in user_ids:
                            activity_ins = self.env['mail.activity'].sudo().create(
                                {'res_id': self.id,
                                 'res_model_id': self.env['ir.model'].search([('model', '=', 'sale.order')],
                                                                             limit=1).id,
                                 'res_model': 'sale.order',
                                 'activity_type_id': 4,
                                 'summary': 'Form 4 Is Done',
                                 'note': 'Sale Order ' + self.name + ' discount Approved',
                                 'date_deadline': fields.Date.today() ,
                                 'activity_category': 'default',
                                 'previous_activity_type_id': False,
                                 'recommended_activity_type_id': False,
                                 'user_id': user_id.id
                                 })

    def action_approve_ceo_discount(self):
        self.state = self.last_state
        self.notifi_state = 'Sale Order ' + self.name + ' discount Approved'
        user_ids = [self.user_id]
        if user_ids:
            for user_id in user_ids:
                activity_ins = self.env['mail.activity'].sudo().create(
                                {'res_id': self.id,
                                 'res_model_id': self.env['ir.model'].search([('model', '=', 'sale.order')],
                                                                             limit=1).id,
                                 'res_model': 'sale.order',
                                 'activity_type_id': 4,
                                 'summary': 'Form 4 Is Done',
                                 'note': 'Sale Order ' + self.name + ' discount Approved',
                                 'date_deadline': fields.Date.today() ,
                                 'activity_category': 'default',
                                 'previous_activity_type_id': False,
                                 'recommended_activity_type_id': False,
                                 'user_id': user_id.id
                                 })


    @api.model
    def create(self,vals):
        res = super(SaleOrder,self).create(vals)
        for line in res.order_line:
            if line.discount > 0.0:
                if self.env.user.has_group('sales_team.group_sale_salesman') or self.env.user.has_group('sales_team.group_sale_salesman_all_leads') or self.env.user.has_group('sales_team.group_sale_manager') :
                    sales_discount = float(self.env['ir.config_parameter'].get_param('sales_person_discount'))
                    if line.discount > sales_discount:
                        self.last_state = res.state
                        res.write({'last_state':res.state,'state':'gm_discount','notifi_state': 'Sale Order ' + res.name + 'needs GM discount Approval'})
                        gm_id = self.env.ref('first_grain_custom.group_gm').id
                        user_ids = self.env['res.users'].search([('groups_id', 'in', [gm_id])])
                        if user_ids:
                            for user_id in user_ids:
                                activity_ins = self.env['mail.activity'].sudo().create(
                                    {'res_id': res.id,
                                     'res_model_id': self.env['ir.model'].search([('model', '=', 'sale.order')],
                                                                                 limit=1).id,
                                     'res_model': 'sale.order',
                                     'activity_type_id': 4,
                                     'summary': 'Form 4 Is Done',
                                     'note': 'Sale Order ' + res.name + ' needs GM discount Approval',
                                     'date_deadline': fields.Date.today() ,
                                     'activity_category': 'default',
                                     'previous_activity_type_id': False,
                                     'recommended_activity_type_id': False,
                                     'user_id': user_id.id
                                     })

                    #send notification to General Manager
        return res




