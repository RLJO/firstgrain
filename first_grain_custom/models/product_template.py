from odoo import api,fields,models,_

#inherit ProductTemplate class
class ProductTemplate(models.Model):
    _inherit = "product.template"

    analytic_account_id = fields.Many2one('account.analytic.account','Analytic Account')