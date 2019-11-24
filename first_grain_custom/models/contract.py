from odoo import api,fields,models,_
from datetime import datetime, timedelta, time


class BillLeading(models.Model):
    _name = "contract.form"
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    _description = "Contract"

    name = fields.Char('')
    contract_date = fields.Datetime('Contract Date')
    source_document_rfq = fields.Many2one('purchase.order','Source Document')
    vendor = fields.Many2one('res.partner','Vendor')
    # Address Part
    street = fields.Char(related='vendor.street')
    street2 = fields.Char(related='vendor.street2')
    zip = fields.Char(related='vendor.zip')
    city = fields.Char(related='vendor.city')
    state_id = fields.Many2one("res.country.state", string='State', related='vendor.state_id')
    country_id = fields.Many2one('res.country', string='Country', related='vendor.country_id')

    customer = fields.Many2one('res.partner','Customer')
    # Address Part
    c_street = fields.Char(related='customer.street')
    c_street2 = fields.Char(related='customer.street2')
    c_zip = fields.Char(related='customer.zip')
    c_city = fields.Char(related='customer.city')
    c_state_id = fields.Many2one("res.country.state", string='State', related='customer.state_id')
    c_country_id = fields.Many2one('res.country', string='Country', related='customer.country_id')

    # fields
    origin = fields.Char('Origin')
    quantity = fields.Float('Quantity')
    quantity_note = fields.Char('Quantity Note')
    quality = fields.Char('Quality')
    delivery_term = fields.Char('Delivery Terms')
    shipment_period = fields.Char('Shipment Period')
    price = fields.Char('Price')
    prov_price = fields.Char('prov_price')

    payment_term = fields.Many2one('account.payment.term',related='source_document_rfq.payment_term_id')
    protection = fields.Char('Protection')
    fail_pay_dil = fields.Char('Failure to Pay or Delivery')
    load_doc_instruction = fields.Char('Loading and Documentary instructions')
    discharge = fields.Char('Discharge')
    licenses = fields.Char('Licenses')
    taxation = fields.Char('Taxation')
    title_risk = fields.Char('Title/Risk')
    low_jurisduction= fields.Char('Law and Jurisdction')
    compliance = fields.Char('Compliance')
    antiboycott = fields.Char('Antiboycott')
    confidentiality = fields.Char('Confidentiality')
    assignment_clause = fields.Char('Assignment Clause')
    limit_liability = fields.Char('Limitation of Liability')
    terms_conds_rule = fields.Char('Terms, Conditions and Rules')
    language = fields.Char('Language')

    state = fields.Selection([('new', 'New'), ('request_approval', 'Request Approval'),('Wait_ceo_confirm','Wait CEO Confirm'),('confirmed','Confirmed')], default='new', string="State", index=True)
    notification_status = fields.Char()

    def action_request_approval(self):
        self.state = 'request_approval'
    #     Send Notification For GM And Account Manager
        gm_id = self.env.ref('first_grain_custom.group_gm').id
        account_manager_id = self.env.ref('account.group_account_manager').id
        user_ids = self.env['res.users'].search([('groups_id', 'in', [gm_id,account_manager_id])])
        if user_ids:
            self.notification_status = 'Contract ' + str(self.name) + ' asked for Approval'
            for user_id in user_ids:
                activity_ins = self.env['mail.activity'].sudo().create(
                    {'res_id': self.id,
                         'res_model_id': self.env['ir.model'].search([('model', '=', 'contract.form')],limit=1).id,
                         'res_model': 'contract.form',
                         'activity_type_id': 4,
                         'summary': 'Request Approval',
                         'note': 'Contract ' + str(self.name) + ' asked for Approval',
                         'date_deadline': fields.Date.today(),
                         'activity_category': 'default',
                         'previous_activity_type_id': False,
                         'recommended_activity_type_id': False,
                         'user_id': user_id.id
                    })

    def action_approve(self):
        self.state = 'Wait_ceo_confirm'

        #     Send Notification For CEO
        ceo_id = self.env.ref('first_grain_custom.group_ceo').id
        user_ids = self.env['res.users'].search([('groups_id', 'in', [ceo_id])])
        if user_ids:
            self.notification_status = 'Contract ' + self.name + 'need Confirm'
            for user_id in user_ids:
                activity_ins = self.env['mail.activity'].sudo().create(
                    {'res_id': self.id,
                     'res_model_id': self.env['ir.model'].search([('model', '=', 'contract.form')], limit=1).id,
                     'res_model': 'contract.form',
                     'activity_type_id': 4,
                     'summary': 'Contract Confirm',
                     'note': 'Contract ' + self.name + 'need Confirm',
                     'date_deadline': fields.Date.today(),
                     'activity_category': 'default',
                     'previous_activity_type_id': False,
                     'recommended_activity_type_id': False,
                     'user_id': user_id.id
                     })

    def action_confirm(self):
        self.state = 'confirmed'
        # create Analytic Account
        self.env['account.analytic.account'].create({'name':self.name})
        # create Operation 
        self.env['operation.logistic'].create({
            'name':self.name,
            'contract_no':self.name,
            'purchase_id':self.source_document_rfq.id,
        })
        # send notification or operation create
        gm_id = self.env.ref('first_grain_custom.group_operation_l_manager').id
        account_manager_id = self.env.ref('account.group_account_manager').id
        user_ids = self.env['res.users'].search([('groups_id', 'in', [gm_id, account_manager_id])])
        if user_ids:
            self.notification_status = 'Operation ' + self.name + 'has been created'
            for user_id in user_ids:
                activity_ins = self.env['mail.activity'].sudo().create(
                    {'res_id': self.id,
                     'res_model_id': self.env['ir.model'].search([('model', '=', 'operation.logistic')], limit=1).id,
                     'res_model': 'operation.logistic',
                     'activity_type_id': 6,
                     'summary': 'Operation Created',
                     'note': 'Operation ' + self.name + 'has been created',
                     'date_deadline': fields.Date.today(),
                     'activity_category': 'default',
                     'previous_activity_type_id': False,
                     'recommended_activity_type_id': False,
                     'user_id': user_id.id
                     })

        # send notification to CEO to set Price

                #     Send Notification For CEO
                ceo_id = self.env.ref('first_grain_custom.group_ceo').id
                user_ids = self.env['res.users'].search([('groups_id', 'in', [ceo_id])])
                if user_ids:
                    for user_id in user_ids:
                        activity_ins = self.env['mail.activity'].sudo().create(
                            {'res_id': self.id,
                             'res_model_id': self.env['ir.model'].search([('model', '=', 'contract.form')], limit=1).id,
                             'res_model': 'contract.form',
                             'activity_type_id': 4,
                             'summary': 'Set Price',
                             'note': 'Set Price',
                             'date_deadline': fields.Date.today(),
                             'activity_category': 'default',
                             'previous_activity_type_id': False,
                             'recommended_activity_type_id': False,
                             'user_id': user_id.id
                             })

        # confirm purchase order
        self.source_document_rfq.button_confirm()

