from odoo import api,fields,models,_


class Accountbudget(models.Model):
    _inherit = "crossovered.budget"
    budget_new_line = fields.One2many('crossovered.budget.new.line', 'budget_id',string="Budget Lines")

class AccountbudgetNewLine(models.Model):
    _name = "crossovered.budget.new.line"

    payment_term_id = fields.Many2one('account.payment.term', string='Payment Terms')
    qty = fields.Integer('Quantity/Volume')
    net_loss = fields.Integer('net profit/loss per ton')
    total_loss = fields.Float(compute='_get_total_profit_loss')
    note = fields.Text('Note')

    budget_id = fields.Many2one('crossovered.budget')


    @api.depends('net_loss','qty')
    def _get_total_profit_loss(self):
        self.total_loss = self.qty * self.net_loss

class AccountbudgetLine(models.Model):
    _inherit = "crossovered.budget.lines"

    planned_qty = fields.Float('Planned Quantity')
    actual_qty = fields.Float('Actual Quantity' ,readonly=True)


