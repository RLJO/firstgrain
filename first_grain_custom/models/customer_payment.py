from odoo import api,fields,models,_
from datetime import datetime, timedelta, time



class AccountPayment(models.Model):
    _inherit = 'account.payment'

    analytic_account_id = fields.Many2one('account.analytic.account','Analytic Account')

    state = fields.Selection(
        [('draft', 'Draft'), ('request_approval', 'Request Approval'), ('gm_ceo_approval', 'GM/CEO Approved'),
         ('posted', 'Validated'), ('sent', 'Sent'), ('reconciled', 'Reconciled'), ('cancelled', 'Cancelled')],
        readonly=True, default='draft', copy=False, string="Status")

    notifi_status = fields.Char()

    def action_request_approval(self):
        self.state = 'request_approval'
        #     Send Notification For GM And Account Manager
        gm_id = self.env.ref('first_grain_custom.group_gm').id
        ceo_id = self.env.ref('first_grain_custom.group_ceo').id
        user_ids = self.env['res.users'].search([('groups_id', 'in', [gm_id, ceo_id])])
        if user_ids:
            self.notifi_status = 'Vendor Payment ' + str(self.name) + ' asked for Approval'
            for user_id in user_ids:
                activity_ins = self.env['mail.activity'].sudo().create(
                    {'res_id': self.id,
                     'res_model_id': self.env['ir.model'].search([('model', '=', 'account.payment')], limit=1).id,
                     'res_model': 'account.payment',
                     'activity_type_id': 4,
                     'summary': 'Request Approval',
                     'note': 'Payment ' + str(self.name) + ' asked for Approval',
                     'date_deadline': fields.Date.today(),
                     'activity_category': 'default',
                     'previous_activity_type_id': False,
                     'recommended_activity_type_id': False,
                     'user_id': user_id.id
                     })

    def action_approve(self):
        self.state = 'gm_ceo_approval'
        #     Send Notification For GM And Account Manager
        ap_id = self.env.ref('first_grain_custom.group_ap').id
        user_ids = self.env['res.users'].search([('groups_id', 'in', [ap_id])])
        if user_ids:
            self.notifi_status = 'Vendor Payment ' + str(self.name) + ' has been approved'
            for user_id in user_ids:
                activity_ins = self.env['mail.activity'].sudo().create(
                    {'res_id': self.id,
                     'res_model_id': self.env['ir.model'].search([('model', '=', 'account.payment')], limit=1).id,
                     'res_model': 'account.payment',
                     'activity_type_id': 4,
                     'summary': 'Request Approval',
                     'note': 'Payment ' + str(self.name) + ' has been approved',
                     'date_deadline': fields.Date.today(),
                     'activity_category': 'default',
                     'previous_activity_type_id': False,
                     'recommended_activity_type_id': False,
                     'user_id': user_id.id
                     })

    def action_reject(self):
        self.state = 'draft'
        #     Send Notification For GM And Account Manager
        ap_id = self.env.ref('first_grain_custom.group_ap').id
        user_ids = self.env['res.users'].search([('groups_id', 'in', [ap_id])])
        if user_ids:
            self.notifi_status = 'Vendor Payment ' + str(self.name) + ' has been rejected'
            for user_id in user_ids:
                activity_ins = self.env['mail.activity'].sudo().create(
                    {'res_id': self.id,
                     'res_model_id': self.env['ir.model'].search([('model', '=', 'account.payment')], limit=1).id,
                     'res_model': 'account.payment',
                     'activity_type_id': 4,
                     'summary': 'Request Approval',
                     'note': 'Payment ' + str(self.name) + ' has been rejected',
                     'date_deadline': fields.Date.today(),
                     'activity_category': 'default',
                     'previous_activity_type_id': False,
                     'recommended_activity_type_id': False,
                     'user_id': user_id.id
                     })
    def post(self):
        res = super(AccountPayment,self).post()

        moves_lines = self.env['account.move.line'].search([('payment_id','in', self.ids)])

        for line in moves_lines:

                if line.credit :
                    line.write({
                        'analytic_account_id':self.analytic_account_id.id
                    })

        return res
