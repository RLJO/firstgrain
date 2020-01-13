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
    quality_arabic = fields.Char('الجوده')
    delivery_term = fields.Char('Delivery Terms')
    delivery_term_arabic = fields.Char('شروط التوصيل')
    shipment_period = fields.Char('Shipment Period')
    shipment_period_arabic = fields.Char('Shipment Period')
    supervision = fields.Char('Supervision')
    supervision_arabic = fields.Char('اشراف')
    weight = fields.Float('Weight')
    weight_arabic = fields.Float('الوزن')
    condition = fields.Char('Condition')
    condition_arabic = fields.Char('الشروط')
    price = fields.Float('Price')
    price_arabic = fields.Float('المبلغ')
    prov_price = fields.Char('Provisional Price')
    prov_price_arabic = fields.Char('سعر مؤقت')

    payment_term = fields.Many2one('account.payment.term',related='source_document_rfq.payment_term_id',string='Payment Term')
    payment_term_arabic = fields.Many2one('account.payment.term',related='source_document_rfq.payment_term_id',string='شروط الدفع')
    protection = fields.Char('Protection')
    protection_arabic = fields.Char('الحمايه')
    fail_pay_dil = fields.Char('Failure to Pay or Delivery')
    fail_pay_dil_arabic = fields.Char('فشل في التسليم او الدفع')

    load_doc_instruction = fields.Char('Loading and Documentary instructions')
    load_doc_instruction_arabic = fields.Char('Loading and Documentary instructions')

    discharge = fields.Char('Discharge')
    discharge_arabic = fields.Char('الخصم')
    licenses = fields.Char('Licenses')
    licenses_arabic = fields.Char('تراخيص')
    taxation = fields.Char('Taxation')
    taxation_arabic = fields.Char('الضرائب')
    title_risk = fields.Char('Title/Risk')
    title_risk_arabic = fields.Char('Title/Risk')
    low_jurisduction= fields.Char('Law and Jurisdction')
    low_jurisduction_arabic= fields.Char('Law and Jurisdction')
    compliance = fields.Char('Compliance')
    compliance_arabic = fields.Char('Compliance')
    antiboycott = fields.Char('Antiboycott')
    antiboycott_arabic = fields.Char('Antiboycott')
    confidentiality = fields.Char('Confidentiality')
    confidentiality_arabic= fields.Char('Confidentiality')
    assignment_clause = fields.Char('Assignment Clause')
    assignment_clause_arabic = fields.Char('Assignment Clause')
    limit_liability = fields.Char('Limitation of Liability')
    limit_liability_arabic = fields.Char('Limitation of Liability')
    terms_conds_rule = fields.Char('Terms, Conditions and Rules')
    terms_conds_rule_arabic = fields.Char('Terms, Conditions and Rules')
    language = fields.Char('Language')
    language_arabic = fields.Char('اللغه')

    commodity = fields.Many2one('product.product')

    state = fields.Selection([('new', 'New'), ('request_approval', 'Request Approval'),('Wait_ceo_confirm','Wait CEO Confirm'),('confirmed','Confirmed')], default='new', string="State", index=True)
    notification_status = fields.Char()

    # rfq Data
    rfq_vendor = fields.Many2one('res.partner','Vendor',related='source_document_rfq.partner_id')
    limit_up_to = fields.Float('Limit Up To',related='source_document_rfq.limit_up_to')
    premium_from = fields.Float('Premium Form',related='source_document_rfq.premium_from')
    purchase_type = fields.Selection(related='source_document_rfq.purchase_type',string="Purchase Type")

    shipment_from = fields.Datetime('Shipment Period From',related='source_document_rfq.shipment_from')
    shipment_to = fields.Datetime('Shipment Period To',related='source_document_rfq.shipment_to')
    monthly_plan = fields.Many2one('crossovered.budget','Monthly Plan',related='source_document_rfq.monthly_plan')

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
        operation =self.env['operation.logistic'].create({
            'name':self.name +' Operation',
            'contract_no':self.id,
            'purchase_id':self.source_document_rfq.id,
        })
        # send notification or operation create
        gm_id = self.env.ref('first_grain_custom.group_operation_l_manager').id
        account_manager_id = self.env.ref('account.group_account_manager').id
        user_ids = self.env['res.users'].search([('groups_id', 'in', [gm_id, account_manager_id])])
        if user_ids:
            operation.notification_status = 'Operation ' + operation.name + 'has been created'
            for user_id in user_ids:
                activity_ins = self.env['mail.activity'].sudo().create(
                    {'res_id': operation.id,
                     'res_model_id': self.env['ir.model'].search([('model', '=', 'operation.logistic')], limit=1).id,
                     'res_model': 'operation.logistic',
                     'activity_type_id': 6,
                     'summary': 'Operation Created',
                     'note': 'Operation ' + operation.name + 'has been created',
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
        self.source_document_rfq.state = 'draft'
        self.source_document_rfq.button_confirm()

