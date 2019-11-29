from odoo import api,fields,models,_
from datetime import datetime, timedelta, time



class AccountPayment(models.Model):
    _inherit = 'account.payment'

    analytic_account_id = fields.Many2one('account.analytic.account','Analytic Account')


    def post(self):
        res = super(AccountPayment,self).post()

        moves_lines = self.env['account.move.line'].search([('payment_id','in', self.ids)])

        for line in moves_lines:

                if line.credit :
                    line.write({
                        'analytic_account_id':self.analytic_account_id.id
                    })

        return res
