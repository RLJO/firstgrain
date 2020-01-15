from odoo import api,fields,models,_
from datetime import datetime, timedelta, time



class AcceptImport(models.Model):
    _name = 'accept.import'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    _description = "Accept Import"

    def _default_sale_line_domain(self):
        return [('id','=',self.operation_id.contract_no.id)]

    name = fields.Char('Accept Import No')
    operation_id = fields.Many2one('operation.logistic','Operation No',required=True)
    product_id = fields.Many2one('product.template', string='Product Name',related='operation_id.product_id')
    acceptation_agri = fields.Char('موافقه وزاره الزراعه')
    vessel_name = fields.Char('اسم الباخره')
    bill_leading = fields.Char('ارقام بوالص الشحن')
    port_dest = fields.Char('Port of Destination')
    organ = fields.Char('Organ')
    cortication_no = fields.Char(' Number of Cortication')
    cortication_date = fields.Date('Date of Cortication')
    invoice_no = fields.Many2one('account.move','Invoice No')
    invoice_date = fields.Date('Date of Invoice')

    state = fields.Selection([('draft', 'Draft'),('prepare','Prepare'),('done','Done')], default='draft', string="State", index=True)

    notifi_status = fields.Char()

    def action_prepare(self):
        self.state = 'prepare'

    def action_done(self):
        self.state = 'done'
        #     send notification that the accept import is done
        logistic_manger_id = self.env.ref('first_grain_custom.group_logistic_manager').id
        users_ids = self.env['res.users'].search(
            [('groups_id', 'in', [logistic_manger_id])])

        if users_ids:
                self.notifi_status = self.name + ' related by operation number ' +self.operation_id.name+' is done'
                for user_id in users_ids:
                    activity_ins = self.env['mail.activity'].sudo().create(
                        {'res_id': self.id,
                         'res_model_id': self.env['ir.model'].search([('model', '=', 'accept.import')], limit=1).id,
                         'res_model': 'accept.import',
                         'activity_type_id': 4,
                         'summary': 'Accept Import done',
                         'note':  'Accept Import ' + self.name + ' related by operation number ' +self.operation_id.name+'is done',
                         'date_deadline': fields.Date.today(),
                         'activity_category': 'default',
                         'previous_activity_type_id': False,
                         'recommended_activity_type_id': False,
                         'user_id': user_id.id
                         })
