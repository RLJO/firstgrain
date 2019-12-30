from odoo import api,fields,models,_
from datetime import datetime, timedelta, time



class Inventory(models.Model):
    _inherit = 'stock.picking'

    operation_id = fields.Many2one('operation.logistic','Operation')
    contract_no = fields.Many2one('contract.form','Contract',related='operation_id.contract_no')
    policy_id = fields.Many2one('bill.leading' , 'Policy')
    vessel = fields.Char('Vessel',related='policy_id.vessel')

    vehicle_line = fields.One2many('vehicle.info.line','delivery_order')

    notifi_state = fields.Char()

    def button_validate(self):
        res = super(Inventory,self).button_validate()

        # Send Notification
        self.notifi_state = 'Delivery Order ' + self.name + ' has been Validated '

        sale_manager_id = self.env.ref('sales_team.group_sale_manager').id
        ar_id = self.env.ref('first_grain_custom.group_ar').id
        ap_id = self.env.ref('first_grain_custom.group_ap').id
        account_manager_id = self.env.ref('account.group_account_manager').id
        user_ids = self.env['res.users'].search([('groups_id', 'in', [sale_manager_id , ap_id ,ar_id , account_manager_id])])
        if user_ids:
            for user_id in user_ids:
                activity_ins = self.env['mail.activity'].sudo().create(
                    {'res_id': self.id,
                     'res_model_id': self.env['ir.model'].search([('model', '=', 'stock.picking')],
                                                                 limit=1).id,
                     'res_model': 'stock.picking',
                     'activity_type_id': 4,
                     'summary': '',
                     'note':  'Delivery Order ' + self.name + ' has been Validated ',
                     'date_deadline': fields.Date.today(),
                     'activity_category': 'default',
                     'previous_activity_type_id': False,
                     'recommended_activity_type_id': False,
                     'user_id': user_id.id
                     })

        # Update line in bill of leading
        if self.policy_id:
            for line in self.move_ids_without_package:
                qty = line.quantity_done
                product = line.product_id
            delivery_order_line = {
                'delivery_order_id': self.id,
                'customer_id': self.partner_id.id,
                'qty': qty,
                'product_id': product.id,
                'bill_leading_id': self.policy_id.id,

            }
            self.env['delivery.order.type'].create(delivery_order_line)

        return res


class StockMove(models.Model):
    _inherit = 'stock.move'

    policy_id = fields.Many2one('bill.leading' , 'Policy',related='picking_id.policy_id')
    vessel_qty = fields.Float(related='policy_id.quantity')
