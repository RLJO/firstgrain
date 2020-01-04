from odoo import api,fields,models,_
from datetime import datetime, timedelta, time



class BillLeading(models.Model):
    _name = 'bill.leading'

    def _default_sale_line_domain(self):
        return [('id','=',self.operation_id.contract_no.id)]

    name = fields.Char('Number Bill')
    operation_id = fields.Many2one('operation.logistic','Operation')
    contract_id = fields.Many2one('contract.form','Contract',domain=lambda self:self._default_sale_line_domain())
    quantity = fields.Float('Quantity')
    date = fields.Date()
    product_type = fields.Many2one('product.product','Product Type')
    product_description = fields.Char('Product Description')
    vessel = fields.Char('Vessel Type')
    port_leading = fields.Char('Port Of Leading')
    port_discharge = fields.Char('Port Of Discharge')
    original = fields.Char('ORIGINAL')

    sale_type_ids = fields.One2many('sale.order.type','bill_leading_id')
    delivery_order_ids = fields.One2many('delivery.order.type','bill_leading_id')


    @api.onchange('product_type')
    def product_type_change(self):
        if self.product_type :
            self.product_description = self.product_type.name

    # Domain in Contract
    @api.onchange('operation_id')
    def operation_change(self):
        if self.operation_id:
            domain = {'contract_id':[('id', '=', self.operation_id.contract_no.id)]}
            return {'domain':domain}

    @api.model
    def create(self, values):
        bill = super(BillLeading,self).create(values)
        if bill.operation_id:
            bill.operation_id.write({'bill_no':bill.id})
        if bill.delivery_order_ids :
            for delivery in bill.delivery_order_ids:
                delivery.delivery_order_id.write({'bill_leading_id':bill.id})
        return  bill

