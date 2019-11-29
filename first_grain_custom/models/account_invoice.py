from odoo import api,fields,models,_

from datetime import datetime, timedelta, time



class AccountInvoiceLine(models.Model):
    _inherit = "account.move.line"

    analytic_account_id = fields.Many2one('account.analytic.account', 'Analytic Account')

    @api.onchange('product_id')
    def get_analytic_account(self):
        if self.product_id:
            self.analytic_account_id = self.product_id.analytic_account_id

class AccountInvoice(models.Model):
    _inherit = "account.move"

    notifi_state = fields.Char()

    def action_post(self):
        res = super(AccountInvoice,self).action_post()

        for line in self.invoice_line_ids:
            if line.analytic_account_id:
                budgets_lines = self.env['crossovered.budget.lines'].search([('analytic_account_id','=',line.analytic_account_id.id),
                                                                             ('date_from','<=',line.date),('date_to','>=',line.date)])
                for budget in budgets_lines:
                    budget.update({
                        'actual_qty':budget.actual_qty+line.quantity
                    })

        # Send Notification
        self.notifi_state = 'Invoice ' + self.name + ' has been Confirmed \n' + 'Date : '+str(self.invoice_date)


        sale_manager_id = self.env.ref('sales_team.group_sale_manager').id
        user_ids = self.env['res.users'].search([('groups_id', 'in', [ sale_manager_id])])
        if user_ids:
            for user_id in user_ids:
                activity_ins = self.env['mail.activity'].sudo().create(
                    {'res_id': self.id,
                     'res_model_id': self.env['ir.model'].search([('model', '=', 'account.move')],
                                                                 limit=1).id,
                     'res_model': 'account.move',
                     'activity_type_id': 4,
                     'summary': '',
                     'note':'Invoice ' + self.name + ' has been Confirmed \n' + 'Date : '+str(self.invoice_date),
                     'date_deadline': fields.Date.today() ,
                     'activity_category': 'default',
                     'previous_activity_type_id': False,
                     'recommended_activity_type_id': False,
                     'user_id': user_id.id
                     })

        return res