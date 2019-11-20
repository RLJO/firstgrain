from odoo import api,fields,models,_
from datetime import datetime, timedelta, time



class BillLeading(models.Model):
    _name = "operation.logistic"
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    _description = "Operation And Logistic"

    name = fields.Char('')
    purchase_id = fields.Many2one('purchase.order','Purchase Order')
    contract_no = fields.Char('Contract No.')
    arrived_date = fields.Date('Date Arrived')

    # First Tab
    form4 = fields.Boolean('Form 4' )

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
            for user_id in user_ids:
                activity_ins = self.env['mail.activity'].sudo().create(
                    {'res_id': self.id,
                     'res_model_id': self.env['ir.model'].search([('model', '=', 'operation.logistic')], limit=1).id,
                     'res_model': 'operation.logistic',
                     'activity_type_id': 4,
                     'summary': 'Form 4 Request',
                     'note': 'Operation ' + self.name + ' asked for form4',
                     'date_deadline': fields.Date.today() + timedelta(days=1),
                     'activity_category': 'default',
                     'previous_activity_type_id': False,
                     'recommended_activity_type_id': False,
                     'user_id': user_id.id
                     })

    def action_done_form4(self):
        print("Noti")
        operation_manger_id = self.env.ref('first_grain_custom.group_operation_l_manager').id
        user_ids = self.env['res.users'].search([('groups_id', 'in', [operation_manger_id])])
        if user_ids:
            for user_id in user_ids:
                activity_ins = self.env['mail.activity'].sudo().create(
                    {'res_id': self.id,
                     'res_model_id': self.env['ir.model'].search([('model', '=', 'operation.logistic')], limit=1).id,
                     'res_model': 'operation.logistic',
                     'activity_type_id': 4,
                     'summary': 'Form 4 Is Done',
                     'note': 'Operation ' + self.name + ' Form4 is done',
                     'date_deadline': fields.Date.today() + timedelta(days=1),
                     'activity_category': 'default',
                     'previous_activity_type_id': False,   
                     'recommended_activity_type_id': False,
                     'user_id': user_id.id
                     })

    def action_done_custom(self):
        print("send Notification for operation  ")

    def action_done_phyto(self):
        print("Send Notification")

    def send_to_channel(self):
        operation_manger_id = self.env.ref('first_grain_custom.group_operation_l_manager').id
        if operation_manger_id:
            user_ids = self.env['res.users'].search([('groups_id', 'in', [operation_manger_id])])
        if user_ids:
            for user_id in user_ids:
                activity_ins = self.env['mail.activity'].sudo().create(
                    {'res_id': self.id,
                     'res_model_id': self.env['ir.model'].search([('model', '=', 'operation.logistic')], limit=1).id,
                     'res_model': 'operation.logistic',
                     'activity_type_id': 4,
                     'summary': 'Form 4 Request',
                     'note': 'Operation '+self.name+' asked for form4',
                     'date_deadline': fields.Date.today()+timedelta(days=1),
                     'activity_category': 'default',
                     'previous_activity_type_id': False,
                     'recommended_activity_type_id': False,
                     'user_id': user_id.id
                     })

