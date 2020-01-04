from odoo import api,fields,models,_
from datetime import datetime, timedelta, time



class Inventory(models.Model):
    _inherit = 'stock.picking'

    operation_id = fields.Many2one('operation.logistic','Operation')
    contract_no = fields.Many2one('contract.form','Contract')
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

    vessel_qty = fields.Float(related='policy_id.quantity', string='Vessel QTY')
    operation_bill_leading = fields.Integer(compute='_get_bills_leading', string='Bills')
    bill_product_qty = fields.Integer(compute='_get_bills_leading', string='Total QTY')
    sarf_kind = fields.Selection([('direct','صرف مباشر'),('stock','صرف مخزن')])
    bill_no = fields.Many2one('bill.leading' , related='policy_id')
    bill_qty = fields.Float(related='policy_id.quantity')

    stock_no = fields.Many2one('stock.location')
    stock_qty = fields.Float(compute='_get_stock_qty',default=-1)

    monsaref = fields.Float(compute='_get_monsaref')
    balance = fields.Float(compute='_get_balance')
    baky_mn_elfrag = fields.Float(compute='_get_baky_mn_elfrag')
    gararat_no = fields.Float(compute='_get_gararat_no')

    agree_no = fields.Char()

    tawsela_kind = fields.Selection([('wasaal','وصال') ,('tarheel','ارضه')])

    mkawel_elnakl = fields.Many2one('res.partner')
    state_id = fields.Many2one("res.country.state", string='State', ondelete='restrict',domain="[('country_id', '=', 65)]")

    agent = fields.Many2one('res.partner')

    # sale method
    def _get_sale_qty(self):
        qty = 0
        for line in self.sale_id.order_line:
            qty+= line.product_uom_qty
        self.sale_qty = qty

    def _get_sale_monsarf(self):
        picking_type = self.env['stock.picking.type'].search([('code','=','outgoing')])
        deliverys = self.env['stock.picking'].search([('state','=','done'),('sale_id','=',self.sale_id.id),
                                                      ('picking_type_id','=',picking_type.id)])
        qty = 0
        for picking in deliverys :
            for line in picking.move_ids_without_package:
                qty+= line.quantity_done

        self.sale_monsarf = qty

    @api.depends('sale_id')
    def _get_sale_balance(self):
        self.sale_balance = self.sale_qty - self.sale_monsarf

    @api.depends('sale_id')
    def _get_baky_mn_elakd(self):
        picking_type = self.env['stock.picking.type'].search([('code', '=', 'outgoing')])
        deliverys = self.env['stock.picking'].search(
            [('state', 'not in', ['done', 'cancel']), ('sale_id', '=', self.sale_id.id),
             ('picking_type_id', '=', picking_type.id)])
        qty = 0
        for picking in deliverys:
            for line in picking.move_ids_without_package:
                qty += line.quantity_done

        self.baky_mn_elakd = self.sale_balance - qty

    def _get_gararat_no(self):
        avarage = self.bill_no.product_type.grar_avarage
        if avarage > 0:
            self.sale_gararat_no = self.baky_mn_elakd / avarage
        else:
            self.sale_gararat_no = self.baky_mn_elakd


    def _sale_get_gararat_no(self):
        avarage = self.bill_no.product_type.grar_avarage
        if avarage > 0:
            self.sale_gararat_no = self.baky_mn_elakd / avarage
        else:
            self.sale_gararat_no = self.baky_mn_elakd
    # sale order
    sale_agent = fields.Many2one('res.partner',related='sale_id.partner_id')
    sale_qty = fields.Float(compute='_get_sale_qty')
    sale_monsarf = fields.Float(compute='_get_sale_monsarf')
    sale_balance = fields.Float(compute='_get_sale_balance')
    baky_mn_elakd = fields.Float(compute='_get_baky_mn_elakd')
    sale_gararat_no = fields.Float(compute='_sale_get_gararat_no')

    def _get_stock_qty(self):
        qty = 0
        if self.stock_no:
            quants = self.env['stock.quant'].search([('location-id','=',self.stock_no.id),('product_id','=',self.bill_no.product_type.id)])
            for quant in quants:
                qty+= quant.quantity
        self.stock_qty = qty

    def _get_bills_leading(self):
        self.bill_product_qty = 0
        self.operation_bill_leading = 0
        if self.operation_id:
            # عدد الافراجات المفتوحه
            bill_leadings = self.env['bill.leading'].search([('operation_id', '=', self.operation_id.id)])
            self.operation_bill_leading = len(bill_leadings)

            # اجمالي الكميات
            bill_leading_product = self.env['bill.leading'].search([('operation_id', '=', self.operation_id.id),
                                                                    ('product_type', '=', self.product_id.id)])
            total = 0
            for bill in bill_leading_product:
                total += bill_leading_product.quantity
            self.bill_product_qty = total

    def _get_monsaref(self):
        picking_type = self.env['stock.picking.type'].search([('code','=','outgoing')])
        deliverys = self.env['stock.picking'].search([('state','=','done'),('policy_id','=',self.policy_id.id),
                                                      ('picking_type_id','=',picking_type.id)])
        qty = 0
        for picking in deliverys :
            for line in picking.move_ids_without_package:
                qty+= line.quantity_done

        self.monsaref = qty

    @api.depends('stock_qty','stock_no','bill_qty','sarf_kind')
    def _get_balance(self):
        if self.sarf_kind =='direct' :
            self.balance = self.bill_qty - self.monsaref
        elif self.sarf_kind =='stock' :
            self.balance = self.stock_qty - self.monsaref
        else :
            self.balance = 0

    @api.depends('balance','sarf_kind')
    def _get_baky_mn_elfrag(self):
        picking_type = self.env['stock.picking.type'].search([('code', '=', 'outgoing')])
        deliverys = self.env['stock.picking'].search([('state', 'not in', ['done','cancel']), ('policy_id', '=', self.policy_id.id),
                                                      ('picking_type_id', '=', picking_type.id)])
        qty = 0
        for picking in deliverys:
            for line in picking.move_ids_without_package:
                qty += line.quantity_done

        self.baky_mn_elfrag = self.balance-qty

    @api.depends('sarf_kind')
    def _get_gararat_no(self):
        avarage =  self.bill_no.product_type.grar_avarage
        if avarage >0:
            self.gararat_no = self.baky_mn_elfrag / avarage
        else: self.gararat_no = self.baky_mn_elfrag

    mandob_code = fields.Many2one('res.partner')
    mandob_delivery = fields.Float(compute='_get_mandob_delivery')

    picking_code = fields.Selection(related='picking_type_id.code')
    def _get_mandob_delivery(self):
        picking_type = self.env['stock.picking.type'].search([('code','=','outgoing')])
        deliverys = self.env['stock.picking'].search([('policy_id', '=', self.policy_id.id),
                                                      ('picking_type_id', '=', picking_type.id)])
        self.mandob_delivery = len(deliverys)


    warehouse_code = fields.Many2one('stock.warehouse')
    lock_created = fields.Boolean(default=False)

    def action_generate_location(self):

        product = self.env['product.product']
        for line in self.move_ids_without_package:
            product = line.product_id
        name = ''
        if self.warehouse_code:
            name = self.warehouse_code.name + '-'
        if self.contract_no:
            name = name + self.contract_no.name + '-'
        if self.vessel :
            name = name + self.vessel + '-'
        if product :
            name = name + product

        vals={
            'name':name,
            'usage':'internal'
        }
        location = self.env['stock.location'].create(vals)
        self.lock_created = True

class StockMove(models.Model):
    _inherit = 'stock.move'

    operation_id = fields.Many2one('operation.logistic','Operation',related='picking_id.operation_id')
    policy_id = fields.Many2one('bill.leading' , 'Policy',related='picking_id.policy_id')
