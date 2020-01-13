from odoo import api,fields,models,_
from datetime import datetime, timedelta, time



class Operation(models.Model):
    _name = "operation.logistic"
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    _description = "Operation And Logistic"

    name = fields.Char('')
    purchase_id = fields.Many2one('purchase.order','Purchase Order')
    contract_no = fields.Many2one('contract.form','Contract No.')
    arrived_date = fields.Date('Date Arrived')

    # First Tab
    # form4 = fields.Boolean('Form 4' )

    form4_attachment = fields.Binary(attachment=True)

    # Custom Tab
    custom_attachment = fields.Binary(attachment=True)
    release_attachment = fields.Binary(attachment=True)

    # Other Contract Tab
    # Marine
    marine_agent = fields.Boolean('Marine Agent')
    marine_agent_po = fields.Many2one('purchase.order','Marine Agent PO')
    marine_agent_contract = fields.Many2one('contract.form','Marine Agent Contract')

    # Inspection
    inspection_company = fields.Boolean('Inspection Company')
    inspection_company_po = fields.Many2one('purchase.order','Inspection Company PO')
    inspection_company_contract = fields.Many2one('contract.form','Inspection Company Contract')

    # Insurance
    insurance_company = fields.Boolean('Insurance Company')
    insurance_company_po = fields.Many2one('purchase.order','Insurance Company')
    insurance_company_contract = fields.Many2one('contract.form','Insurance Company Contract')
    service = fields.Selection([('classA','Class A'),('classB','Class B'),('classC','Class C')],string='Service')
    
    # Transportation
    transportation_contractor = fields.Boolean('Transportation Contractor')
    transportation_contractor_po = fields.Many2one('purchase.order','Transportation Contractor PO')
    transportation_contractor_contract = fields.Many2one('contract.form','Transportation Contractor Contract')

    #  Storing Commodities
    storing_commodities = fields.Boolean('Storing Commodities')
    storing_commodities_po = fields.Many2one('purchase.order','Storing Commodities PO')
    storing_commodities_contract = fields.Many2one('contract.form','Storing Commodities Contractor')

    #  Discharge Company
    discharge_company = fields.Boolean('Discharge Company')
    discharge_company_po = fields.Many2one('purchase.order','Discharge Company PO')
    discharge_company_contract = fields.Many2one('contract.form','Discharge Company Contractor')

    # phyto Tab
    phyto_attachment = fields.Binary('Phyto Attachment')
    phyto_docment = fields.Binary('Phyto Docment')

    notification_status = fields.Char()
    show_review = fields.Boolean(default=False)

    state = fields.Selection([('new', 'New'),('prepare','Prepare'), ('request_review', 'Wait PO Review'),('request_gm_ceo','Wait GM - CEO Approve'),('approved','Approved')], default='new', string="State", index=True)
    log_line_ids = fields.One2many('operation.log','operation_id')

    bill_no = fields.Many2one('bill.leading','Bill No ')
    @api.onchange('form4_attachment')
    def get_form4_attachment(self):
        if self.form4_attachment :
            self.form4 = True

#     Def for request form 4
    def action_ask_for_form4(self):
        operation_manger_id = self.env.ref('first_grain_custom.group_operation_l_manager').id
        account_manager_id = self.env.ref('account.group_account_manager').id
        user_ids = self.env['res.users'].search([('groups_id', 'in', [operation_manger_id,account_manager_id])])

        if user_ids:
            self.notification_status = 'Operation ' + self.name + ' asked for form4'
            for user_id in user_ids:
                activity_ins = self.env['mail.activity'].sudo().create(
                    {'res_id': self.id,
                     'res_model_id': self.env['ir.model'].search([('model', '=', 'operation.logistic')], limit=1).id,
                     'res_model': 'operation.logistic',
                     'activity_type_id': 4,
                     'summary': 'Form 4 Request',
                     'note': 'Operation ' + self.name + ' asked for form4',
                     'date_deadline': fields.Date.today() ,
                     'activity_category': 'default',
                     'previous_activity_type_id': False,
                     'recommended_activity_type_id': False,
                     'user_id': user_id.id
                     })

    def action_done_form4(self):
        print("Noti")
        self.show_review = True
        operation_manger_id = self.env.ref('first_grain_custom.group_operation_l_manager').id
        ex_manger_id = self.env.ref('first_grain_custom.group_ex_manager').id
        user_ids = self.env['res.users'].search([('groups_id', 'in', [operation_manger_id,ex_manger_id])])
        if user_ids:
            self.notification_status = 'Operation ' + self.name + ' Form4 is done'
            for user_id in user_ids:
                activity_ins = self.env['mail.activity'].sudo().create(
                    {'res_id': self.id,
                     'res_model_id': self.env['ir.model'].search([('model', '=', 'operation.logistic')], limit=1).id,
                     'res_model': 'operation.logistic',
                     'activity_type_id': 4,
                     'summary': 'Form 4 Is Done',
                     'note': 'Operation ' + self.name + ' Form4 is done',
                     'date_deadline': fields.Date.today() ,
                     'activity_category': 'default',
                     'previous_activity_type_id': False,   
                     'recommended_activity_type_id': False,
                     'user_id': user_id.id
                     })
    def action_review_form4(self):
        print('Review Action')
        operation_manger_id = self.env.ref('first_grain_custom.group_operation_l_manager').id
        account_manager_id = self.env.ref('account.group_account_manager').id
        user_ids = self.env['res.users'].search([('groups_id', 'in', [operation_manger_id, account_manager_id])])
        if user_ids:
            self.notification_status = 'Operation ' + self.name + ' Form4 is Reviewed'
            for user_id in user_ids:
                activity_ins = self.env['mail.activity'].sudo().create(
                    {'res_id': self.id,
                     'res_model_id': self.env['ir.model'].search([('model', '=', 'operation.logistic')], limit=1).id,
                     'res_model': 'operation.logistic',
                     'activity_type_id': 4,
                     'summary': 'Form 4 Is Done',
                     'note': 'Operation ' + self.name + ' Form4 is reviewed',
                     'date_deadline': fields.Date.today() ,
                     'activity_category': 'default',
                     'previous_activity_type_id': False,
                     'recommended_activity_type_id': False,
                     'user_id': user_id.id
                     })

    def action_done_custom(self):
        print("send Notification for operation  ")
        logistic_manger_id = self.env.ref('first_grain_custom.group_logistic_manager').id
        user_ids = self.env['res.users'].search([('groups_id', 'in', [logistic_manger_id])])
        if user_ids:
            self.notification_status = 'Operation ' + self.name + ' Customs is done'
            for user_id in user_ids:
                activity_ins = self.env['mail.activity'].sudo().create(
                    {'res_id': self.id,
                     'res_model_id': self.env['ir.model'].search([('model', '=', 'operation.logistic')], limit=1).id,
                     'res_model': 'operation.logistic',
                     'activity_type_id': 4,
                     'summary': 'Form 4 Is Done',
                     'note': 'Operation ' + self.name + ' Customs is done',
                     'date_deadline': fields.Date.today(),
                     'activity_category': 'default',
                     'previous_activity_type_id': False,
                     'recommended_activity_type_id': False,
                     'user_id': user_id.id
                     })

    def action_done_phyto(self):
        print("Send Notification")
        logistic_manger_id = self.env.ref('first_grain_custom.group_logistic_manager').id
        operation_manger_id = self.env.ref('first_grain_custom.group_operation_l_manager').id
        ex_manger_id = self.env.ref('first_grain_custom.group_ex_manager').id
        gm_id = self.env.ref('first_grain_custom.group_gm').id
        ceo_id = self.env.ref('first_grain_custom.group_ceo').id
        user_ids = self.env['res.users'].search([('groups_id', 'in', [gm_id,ceo_id,logistic_manger_id,operation_manger_id,ex_manger_id])])
        if user_ids:
            self.notification_status = 'Operation ' + self.name + ' Phyto is done'
            for user_id in user_ids:
                activity_ins = self.env['mail.activity'].sudo().create(
                    {'res_id': self.id,
                     'res_model_id': self.env['ir.model'].search([('model', '=', 'operation.logistic')], limit=1).id,
                     'res_model': 'operation.logistic',
                     'activity_type_id': 4,
                     'summary': 'Form 4 Is Done',
                     'note': 'Operation ' + self.name + ' Phyto is done',
                     'date_deadline': fields.Date.today() ,
                     'activity_category': 'default',
                     'previous_activity_type_id': False,
                     'recommended_activity_type_id': False,
                     'user_id': user_id.id
                     })


# Operation Action buttons

    def action_request_approval_pom(self):
        self.state = 'request_review'
        print("Send Notification")
        po_id = self.env.ref('purchase.group_purchase_manager').id
        user_ids = self.env['res.users'].search(
            [('groups_id', 'in', [po_id])])
        if user_ids:
            self.notification_status = 'Operation ' + self.name + 'needs Purchase Manager Review'
            for user_id in user_ids:
                activity_ins = self.env['mail.activity'].sudo().create(
                    {'res_id': self.id,
                     'res_model_id': self.env['ir.model'].search([('model', '=', 'operation.logistic')], limit=1).id,
                     'res_model': 'operation.logistic',
                     'activity_type_id': 4,
                     'summary': 'Form 4 Is Done',
                     'note': 'Operation ' + self.name + 'needs Purchase Manager Review',
                     'date_deadline': fields.Date.today() ,
                     'activity_category': 'default',
                     'previous_activity_type_id': False,
                     'recommended_activity_type_id': False,
                     'user_id': user_id.id
                     })
        
    def action_approve_pom(self):
        self.state = 'request_gm_ceo'
        print("Send Notification")
        gm_id = self.env.ref('first_grain_custom.group_gm').id
        ceo_id = self.env.ref('first_grain_custom.group_ceo').id
        user_ids = self.env['res.users'].search([('groups_id', 'in', [gm_id,ceo_id])])
        if user_ids:
            self.notification_status = 'Operation ' + self.name + ' (Purchase Manager reviewed) , needs GM / CEO Approve'
            for user_id in user_ids:
                activity_ins = self.env['mail.activity'].sudo().create(
                    {'res_id': self.id,
                     'res_model_id': self.env['ir.model'].search([('model', '=', 'operation.logistic')], limit=1).id,
                     'res_model': 'operation.logistic',
                     'activity_type_id': 4,
                     'summary': 'Form 4 Is Done',
                     'note': 'Operation ' + self.name +  ' (Purchase Manager reviewed) , needs GM / CEO Approve',
                     'date_deadline': fields.Date.today(),
                     'activity_category': 'default',
                     'previous_activity_type_id': False,
                     'recommended_activity_type_id': False,
                     'user_id': user_id.id
                     })

    def action_approve_gm_ceo(self):
        self.state = 'approved'
        print("Send Notification")
        logistic_manger_id = self.env.ref('first_grain_custom.group_logistic_manager').id
        operation_manger_id = self.env.ref('first_grain_custom.group_operation_l_manager').id
        ex_manger_id = self.env.ref('first_grain_custom.group_ex_manager').id
        user_ids = self.env['res.users'].search([('groups_id', 'in', [logistic_manger_id,operation_manger_id,ex_manger_id])])
        if user_ids:
            self.notification_status = 'Operation ' + self.name + ' GM / CEO Approved'
            for user_id in user_ids:
                activity_ins = self.env['mail.activity'].sudo().create(
                    {'res_id': self.id,
                     'res_model_id': self.env['ir.model'].search([('model', '=', 'operation.logistic')], limit=1).id,
                     'res_model': 'operation.logistic',
                     'activity_type_id': 4,
                     'summary': 'Form 4 Is Done',
                     'note': 'Operation ' + self.name + ' GM / CEO Approved',
                     'date_deadline': fields.Date.today(),
                     'activity_category': 'default',
                     'previous_activity_type_id': False,
                     'recommended_activity_type_id': False,
                     'user_id': user_id.id
                     })

    def action_prepare(self):
        self.state = 'prepare'
        # Create Form 4

        form_vals = {
            'name':self.name +' Form 4',
            'operation_id':self.id,
        }
        form4 = self.env['form.form'].create(form_vals)
        self.form4 = form4.id
        # Send notification

        account_manager_id = self.env.ref('account.group_account_manager').id
        user_ids = self.env['res.users'].search([('groups_id', 'in', [account_manager_id])])
        if user_ids:
            form4.notification_status = 'Form 4 ' + self.name + ' created and needs preparing'
            for user_id in user_ids:
                activity_ins = self.env['mail.activity'].sudo().create(
                    {'res_id': form4.id,
                     'res_model_id': self.env['ir.model'].search([('model', '=', 'form.form')], limit=1).id,
                     'res_model': 'form.form',
                     'activity_type_id': 6,
                     'summary': 'Form Prepare',
                     'note': 'Form 4 ' + self.name + '  created and needs preparing',
                     'date_deadline': fields.Date.today(),
                     'activity_category': 'default',
                     'previous_activity_type_id': False,
                     'recommended_activity_type_id': False,
                     'user_id': user_id.id
                     })


    def write(self,vals):
        operation = super(Operation, self).write(vals)
        if vals.get('log_line_ids'):
            # Send Notification
            print("Send Notification")
            operation_manger_id = self.env.ref('first_grain_custom.group_operation_l_manager').id
            user_ids = self.env['res.users'].search([('groups_id', 'in', [operation_manger_id])])
            if user_ids:
                self.notification_status = 'Operation ' + self.name + ' Log Updated'
                for user_id in user_ids:
                    # raise Warning(user_id)
                    activity_ins = self.env['mail.activity'].sudo().create(
                        {'res_id': self.id,
                         'res_model_id': self.env['ir.model'].search([('model', '=', 'operation.logistic')],limit=1).id,
                         'res_model': 'operation.logistic',
                         'activity_type_id': 4,
                         'summary': 'Form 4 Is Done',
                         'note': 'Operation ' + self.name + 'Log Updated',
                         'date_deadline': fields.Date.today(),
                         'activity_category': 'default',
                         'previous_activity_type_id': False,
                         'recommended_activity_type_id': False,
                         'user_id': user_id.id
                         })

        return operation

    #  Form 4 Data
    form4 = fields.Many2one('form.form','Form 4')
    issue_date = fields.Date('Issue Date' ,related='form4.issue_date')
    bank_name = fields.Selection('Bank Name',related='form4.bank_name')
    exporter_name = fields.Char('Exporter name',related='form4.exporter_name')
    address = fields.Char('Address',related='form4.address')
    id = fields.Integer('ID',related='form4.id')
    product_id = fields.Many2one('product.template', string='Product Name',related='form4.product_id')
    qty = fields.Integer('QTY',related='form4.qty')
    unit_price = fields.Float('Price Unit',related='form4.unit_price')
    contract_info = fields.Char('أساس التعاقد',related='form4.contract_info')

    organ = fields.Char('Organ')
  