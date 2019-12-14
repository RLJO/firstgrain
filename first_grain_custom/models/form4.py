from odoo import api,fields,models,_
from datetime import datetime, timedelta, time


class BillLeading(models.Model):
    _name = "form.form"
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    _description = "Form 4"

    name = fields.Char('Number',required=True)
    operation_id = fields.Many2one('operation.logistic',string='Operation Number' ,required=True)
    issue_date  = fields.Date('Issue Date')
    bank_name = fields.Char('Bank Name')
    exporter_name = fields.Char('Exporter name')
    address = fields.Char('Address')
    id = fields.Integer('ID')
    product_id = fields.Many2one('product.template',string='Product Name')
    qty = fields.Integer('QTY')
    unit_price = fields.Float('Price Unit')
    contract_info = fields.Char('أساس التعاقد')

    organ = fields.Char('Organ')
    product_form = fields.Char('Product Form')
    source_doc = fields.Char('Source Document')
    bank_fees = fields.Float('Bank Fees')
    pay_bank_fees = fields.Float('Pay Bank Fees Issue')
    attachment_doc = fields.Binary()

    notification_status = fields.Char()
    state = fields.Selection([('draft', 'Draft'),('prepare','Prepare'), ('done', 'Done')], default='draft', string="State", index=True)


    def action_form_prepare(self):
        self.state = 'prepare'

    def action_form_done(self):
        self.state = 'done'