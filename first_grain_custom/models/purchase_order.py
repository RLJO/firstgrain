from odoo import api,fields,models,_
from datetime import datetime, timedelta, time
class PurchaseOrderInherit(models.Model) :
    _inherit = 'purchase.order'

    limit_up_to = fields.Float('Limit Up To')
    premium_from = fields.Float('Premium Form')
    purchase_type = fields.Selection([('local','Local Purchase'),('semi_local','Semi Local Purchase'),('international','International Purchase'),('semi_international','Semi International Purchase'),('other','Other')] , string="Purchase Type")

    shipment_from = fields.Datetime('Shipment Period From')
    shipment_to = fields.Datetime('Shipment Period To')
    notification_status = fields.Char()
    is_account_advisor = fields.Boolean(compute='_is_account_advisor')
    monthly_plan = fields.Many2one('crossovered.budget','Monthly Plan')

    state = fields.Selection([
        ('draft', 'RFQ'),
        ('payment_term_request','Request Payment Term'),
        ('sent', 'RFQ Sent'),
        ('bid_received','BID Received'),
        ('cbot_approval','CBOT Approval'),
        ('gm_approval','General Manager Approval'),
        ('ceo_approval','CEO Approval'),
        ('issue_contract','Issue Contract'),
        ('to approve', 'To Approve'),
        ('purchase', 'Purchase Order'),
        ('done', 'Locked'),
        ('cancel', 'Cancelled')
    ], string='Status', readonly=True, index=True, copy=False, default='draft', tracking=True)

    price_method = fields.Selection([('flat','Flat Price'),('premium','Premium')],'Pricing Method')

    contract_count = fields.Integer(compute='_get_contract_count')

    def _is_account_advisor(self):
        self.is_account_advisor = self.env.user.has_group('account.group_account_manager')

    def button_confirm(self):
        res = super(PurchaseOrderInherit, self).button_confirm()

        if res and self.purchase_type =='other' :
            name = self.name + ' contract'
            contract_vals = {
            'name': name,
            'contract_date': fields.Datetime.now(),
            'source_document_rfq': self.id,
            'vendor':self.partner_id.id,
            }

            contract = self.env['contract.form'].create(contract_vals)
        return res

    def action_request_payment_term(self):
        self.state = 'payment_term_request'
        account_manager_id = self.env.ref('account.group_account_manager').id
        user_ids = self.env['res.users'].search([('groups_id', 'in', [account_manager_id])])
        if user_ids:
            self.notification_status = 'Payment Term Requested for ' + self.name
            for user_id in user_ids:
                activity_ins = self.env['mail.activity'].sudo().create(
                    {'res_id': self.id,
                     'res_model_id': self.env['ir.model'].search([('model', '=', 'purchase.order')], limit=1).id,
                     'res_model': 'purchase.order',
                     'activity_type_id': 6,
                     'summary': 'Payment Term request',
                     'note': 'Payment Term Requested for ' + self.name ,
                     'date_deadline': fields.Date.today(),
                     'activity_category': 'default',
                     'previous_activity_type_id': False,
                     'recommended_activity_type_id': False,
                     'user_id': user_id.id
                     })

    def action_payment_term_approve(self):
        self.state = 'sent'
        account_manager_id = self.env.ref('account.group_account_manager').id
        account_user_id = self.env.ref('purchase.group_purchase_user').id
        account_warning_user_id = self.env.ref('purchase.group_warning_purchase').id
        user_ids = self.env['res.users'].search([('groups_id', 'in', [account_user_id,account_warning_user_id,account_manager_id])])
        if user_ids:
            self.notification_status = 'Payment term Approved for ' + self.name
            for user_id in user_ids:
                activity_ins = self.env['mail.activity'].sudo().create(
                    {'res_id': self.id,
                     'res_model_id': self.env['ir.model'].search([('model', '=', 'purchase.order')], limit=1).id,
                     'res_model': 'purchase.order',
                     'activity_type_id': 6,
                     'summary': 'Payment Term request',
                     'note': 'Payment Term Approved for ' + self.name,
                     'date_deadline': fields.Date.today(),
                     'activity_category': 'default',
                     'previous_activity_type_id': False,
                     'recommended_activity_type_id': False,
                     'user_id': user_id.id
                     })

    def action_rfq_send(self):
        self.state = 'bid_received'

        # '''
        #         This function opens a window to compose an email, with the edi purchase template message loaded by default
        #         '''x
        self.ensure_one()
        ir_model_data = self.env['ir.model.data']
        try:
            if self.env.context.get('send_rfq', False):
                template_id = ir_model_data.get_object_reference('purchase', 'email_template_edi_purchase')[1]
            else:
                template_id = ir_model_data.get_object_reference('purchase', 'email_template_edi_purchase_done')[1]
        except ValueError:
            template_id = False
        try:
            compose_form_id = ir_model_data.get_object_reference('mail', 'email_compose_message_wizard_form')[1]
        except ValueError:
            compose_form_id = False
        ctx = dict(self.env.context or {})
        ctx.update({
            'default_model': 'purchase.order',
            'active_model': 'purchase.order',
            'active_id': self.ids[0],
            'default_res_id': self.ids[0],
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
            'custom_layout': "mail.mail_notification_paynow",
            'force_email': True,
            'mark_rfq_as_sent': True,
        })

        # In the case of a RFQ or a PO, we want the "View..." button in line with the state of the
        # object. Therefore, we pass the model description in the context, in the language in which
        # the template is rendered.
        lang = self.env.context.get('lang')
        if {'default_template_id', 'default_model', 'default_res_id'} <= ctx.keys():
            template = self.env['mail.template'].browse(ctx['default_template_id'])
            if template and template.lang:
                lang = template._render_template(template.lang, ctx['default_model'], ctx['default_res_id'])

        self = self.with_context(lang=lang)
        if self.state in ['draft', 'sent']:
            ctx['model_description'] = _('Request for Quotation')
        else:
            ctx['model_description'] = _('Purchase Order')

        return {
            'name': _('Compose Email'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form_id, 'form')],
            'view_id': compose_form_id,
            'target': 'new',
            'context': ctx,
        }

    def action_request_cbot_approve(self):
        self.state = 'cbot_approval'
        cbot_manager = self.env.ref('first_grain_custom.group_cbot_manager').id
        user_ids = self.env['res.users'].search(
            [('groups_id', 'in', [ cbot_manager])])
        if user_ids:
            self.notification_status = 'CBOT Approve Requested for ' + self.name
            for user_id in user_ids:
                activity_ins = self.env['mail.activity'].sudo().create(
                    {'res_id': self.id,
                     'res_model_id': self.env['ir.model'].search([('model', '=', 'purchase.order')], limit=1).id,
                     'res_model': 'purchase.order',
                     'activity_type_id': 6,
                     'summary': 'Payment Term request',
                     'note': 'CBOT Approve Requested for ' + self.name,
                     'date_deadline': fields.Date.today(),
                     'activity_category': 'default',
                     'previous_activity_type_id': False,
                     'recommended_activity_type_id': False,
                     'user_id': user_id.id
                     })

    def action_cbot_approve(self):
        self.state = 'gm_approval'
        gm_manager = self.env.ref('first_grain_custom.group_gm').id
        user_ids = self.env['res.users'].search(
            [('groups_id', 'in', [gm_manager])])
        if user_ids:
            self.notification_status = 'GM Approve Requested for ' + self.name
            for user_id in user_ids:
                activity_ins = self.env['mail.activity'].sudo().create(
                    {'res_id': self.id,
                     'res_model_id': self.env['ir.model'].search([('model', '=', 'purchase.order')], limit=1).id,
                     'res_model': 'purchase.order',
                     'activity_type_id': 6,
                     'summary': 'Payment Term request',
                     'note': 'GM Approve Requested for ' + self.name,
                     'date_deadline': fields.Date.today(),
                     'activity_category': 'default',
                     'previous_activity_type_id': False,
                     'recommended_activity_type_id': False,
                     'user_id': user_id.id
                     })

    def action_gm_approve(self):
        self.state = 'ceo_approval'
        ceo_manager = self.env.ref('first_grain_custom.group_ceo').id
        user_ids = self.env['res.users'].search(
            [('groups_id', 'in', [ceo_manager])])
        if user_ids:
            self.notification_status = 'CEO Approve Requested for ' + self.name
            for user_id in user_ids:
                activity_ins = self.env['mail.activity'].sudo().create(
                    {'res_id': self.id,
                     'res_model_id': self.env['ir.model'].search([('model', '=', 'purchase.order')], limit=1).id,
                     'res_model': 'purchase.order',
                     'activity_type_id': 6,
                     'summary': 'Payment Term request',
                     'note': 'CEO Approve Requested for ' + self.name,
                     'date_deadline': fields.Date.today(),
                     'activity_category': 'default',
                     'previous_activity_type_id': False,
                     'recommended_activity_type_id': False,
                     'user_id': user_id.id
                     })

    def action_gm_reject(self):
        self.state = 'cbot_approval'
        cbot_manager = self.env.ref('first_grain_custom.group_cbot_manager').id
        user_ids = self.env['res.users'].search(
            [('groups_id', 'in', [ cbot_manager])])
        if user_ids:
            self.notification_status = 'GM reject RFQ ,CBOT Approve Requested for ' + self.name
            for user_id in user_ids:
                activity_ins = self.env['mail.activity'].sudo().create(
                    {'res_id': self.id,
                     'res_model_id': self.env['ir.model'].search([('model', '=', 'purchase.order')], limit=1).id,
                     'res_model': 'purchase.order',
                     'activity_type_id': 6,
                     'summary': 'Payment Term request',
                     'note': 'GM reject RFQ ,CBOT Approve Requested for ' + self.name,
                     'date_deadline': fields.Date.today(),
                     'activity_category': 'default',
                     'previous_activity_type_id': False,
                     'recommended_activity_type_id': False,
                     'user_id': user_id.id
                     })

    def action_ceo_approve(self):
        self.state = 'issue_contract'
        gm_manager = self.env.ref('first_grain_custom.group_gm').id
        purchase_manager = self.env.ref('purchase.group_purchase_manager').id
        user_ids = self.env['res.users'].search(
            [('groups_id', 'in', [gm_manager , purchase_manager])])
        if user_ids:
            self.notification_status = 'CEO Approve RFQ ' + self.name
            for user_id in user_ids:
                activity_ins = self.env['mail.activity'].sudo().create(
                    {'res_id': self.id,
                     'res_model_id': self.env['ir.model'].search([('model', '=', 'purchase.order')], limit=1).id,
                     'res_model': 'purchase.order',
                     'activity_type_id': 6,
                     'summary': 'Payment Term request',
                     'note': 'CEO Approve RFQ ' + self.name,
                     'date_deadline': fields.Date.today(),
                     'activity_category': 'default',
                     'previous_activity_type_id': False,
                     'recommended_activity_type_id': False,
                     'user_id': user_id.id
                     })

    def action_ceo_reject(self):
        self.state = 'gm_approval'
        gm_manager = self.env.ref('first_grain_custom.group_gm').id
        user_ids = self.env['res.users'].search(
            [('groups_id', 'in', [gm_manager])])
        if user_ids:
            self.notification_status = 'CEO reject RFQ ,GM Approve Requested for ' + self.name
            for user_id in user_ids:
                activity_ins = self.env['mail.activity'].sudo().create(
                    {'res_id': self.id,
                     'res_model_id': self.env['ir.model'].search([('model', '=', 'purchase.order')], limit=1).id,
                     'res_model': 'purchase.order',
                     'activity_type_id': 6,
                     'summary': 'Payment Term request',
                     'note': 'CEO reject RFQ ,GM Approve Requested for ' + self.name,
                     'date_deadline': fields.Date.today(),
                     'activity_category': 'default',
                     'previous_activity_type_id': False,
                     'recommended_activity_type_id': False,
                     'user_id': user_id.id
                     })

    def action_create_contract(self):

        origin = ''
        qty = 0
        price = 0.0
        product = 0

        for line in self.order_line :
            qty = line.product_qty
            origin = line.origin
            price = line.price_unit
            product = line.product_id.id

        # vals = {
        #     'name': self.name +' - contract',
        #     'vendor': self.partner_id.id ,
        #     'source_document_rfq': self.id ,
        #     'payment_term' : self.payment_term_id.id ,
        #     'quantity': qty,
        #     'price': price,
        #     'origin':origin,
        # }
        # contract = self.env['contract.form'].create(vals)

        ctx = dict(self.env.context or {})
        ctx.update({
            'default_state':'new',
            'default_name': self.name + ' - contract',
            'default_vendor': self.partner_id.id,
            'default_source_document_rfq': self.id,
            'default_payment_term': self.payment_term_id.id,
            'default_quantity': qty,
            'default_price': price,
            'default_origin': origin,
            'default_commodity': product
        })

        compose_form_id = self.env['ir.model.data'].get_object_reference('first_grain_custom', 'contract_form_view_form')[1]
        return {
            'name': _('Contract Form'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'contract.form',
            'views': [(compose_form_id, 'form')],
            'view_id': compose_form_id,
            'target': 'new',
            'context': ctx,
        }

    def action_view_contract(self):
        compose_tree_id = self.env['ir.model.data'].get_object_reference('first_grain_custom', 'contract_form_view_tree')[1]
        compose_form_id = self.env['ir.model.data'].get_object_reference('first_grain_custom', 'contract_form_view_form')[1]
        contracts = self.env['contract.form'].search([('source_document_rfq', '=', self.id)])
        list = []
        for obj in contracts:
            list.append(obj.id)
        return {
            'name': _('Contracts'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form,tree',
            'res_model': 'contract.form',
            'views': [(compose_tree_id, 'tree')],
            'view_id': compose_tree_id,
            'target': 'current',
            'domain': [('id', 'in', list)],
        }

    def _get_contract_count(self):
        contracts = self.env['contract.form'].search([('source_document_rfq','=',self.id)])
        self.contract_count = len((contracts))

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order.line'

    origin = fields.Char('Origin')
    price_method = fields.Selection([('flat','Flat Price'),('premium','Premium')],'Pricing Method' ,compute='_get_price_method', related='order_id.price_method')

    premium_price = fields.Float('Premium Price')
    cbot_price = fields.Float('CBOT Price')
    limit_up = fields.Float('Limit Up')
    cbot_month = fields.Date('CBOT Month')
    pricing_phase = fields.Integer('Pricing Phase')

    def _get_price_method(self):
        self.price_method = self.order_id.price_method

