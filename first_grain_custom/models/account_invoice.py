from odoo import api,fields,models,_


class AccountInvoiceLine(models.Model):
    _inherit = "account.move.line"

    analytic_account_id = fields.Many2one('account.analytic.account', 'Analytic Account')

    @api.onchange('product_id')
    def get_analytic_account(self):
        if self.product_id:
            self.analytic_account_id = self.product_id.analytic_account_id

class AccountInvoice(models.Model):
    _inherit = "account.move"

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
