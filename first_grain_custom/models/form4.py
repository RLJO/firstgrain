from odoo import api,fields,models,_
from datetime import datetime, timedelta, time


class BillLeading(models.Model):
    _name = "form.form"
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    _description = "Form 4"

    name = fields.Char('Number',required=True)
    operation_id = fields.Many2one('operation.logistic',string='Operation Number' ,required=True)
    contract_no = fields.Many2one('contract.form','Contract No')
    purchase_id = fields.Many2one('purchase.order','Purchase No')
    issue_date  = fields.Date('Date')
    bank_name = fields.Selection([('ahly','البنك الاهلي'),('arabi','البنك العربي'),('qnb','QNB بنك')],'Bank Name')

    # QNB Part
    exporter_name = fields.Char('Exporter name')
    address = fields.Char('Address')
    export_number = fields.Integer('رقم البطاقه الاستراديه')
    tax_number = fields.Integer('رقم البطاقه الضريبيه')
    mobile = fields.Integer()
    fax = fields.Integer()

    product_id = fields.Many2one('product.template',string='Product Name')
    qty = fields.Integer('QTY')
    currency_id = fields.Many2one('res.currency','Currency')
    contract_info = fields.Char('أساس التعاقد')
    country_id = fields.Many2one('res.country', string='البلد المستورد منه البضاعه')

    unit = fields.Char('الوحده')
    unit_price = fields.Float('Price Unit')
    total_price = fields.Float('اجمالي القيمه بالعمله الاجنبيه')
    country_id_2 = fields.Many2one('res.country', string='البلد المنشأ')
    policy_no = fields.Char('رقم البولصه')

    currency = fields.Many2one('res.currency','Currency')
    subtotal_in_number = fields.Float('Total in Number')
    subtotal_in_word = fields.Char('Total in Words', compute='currency_text')
    doc_amount = fields.Float('مبلغ المستندات')

    doc_price = fields.Float('مبلغ المستندات')

    exp_name = fields.Char('اسم المستفيد(المصدر)')
    exp_addredd = fields.Char('العنوان')
    phone_number = fields.Char('التليفون')
    account_no = fields.Char('رقم حساب المستفيد المحول اليه')
    branch = fields.Char('اسم الفرع')
    branch_add = fields.Char('عنوان الفرع')
    state_id = fields.Many2one("res.country.state", string='المدينه')
    country_id = fields.Many2one('res.country', string='البلد')
    swift_code = fields.Char('SWIFT code')
    other = fields.Char('تعليمات اخري')
    masarif_bank = fields.Boolean('مصاريف بنك المستفيد (المصدر)      علي المستورد')
    signature = fields.Char('أمضاء')

    @api.depends('currency','subtotal_in_number','currency_money','total_money')
    def currency_text(self):
        if self.currency:
            self.subtotal_in_word =  self.currency.amount_to_text(self.subtotal_in_number)
        else:
            self.subtotal_in_word = ''
        if self.total_money :
            self.total_money_in_words =self.currency_money.amount_to_text(self.total_money)
        else:
            self.total_money_in_words = ''

    # El Arabi

    total_money = fields.Float('مبلغ')
    currency_money = fields.Many2one('res.currency','العمله')
    total_money_in_words = fields.Char(compute='currency_text')
    sign = fields.Char('التوقيع')

    araby_bank_account = fields.Char('رقم الحساب')

    bank_name_arabi = fields.Char('اسم البنك')
    example_name = fields.Char('رقم و تاريخ اصدار النموذج')
    export_name = fields.Char('اسم المستورد')
    main_address = fields.Char('عنوان النشاط الرئيسي')
    export_card = fields.Char('رقم البطاقه الاستيراديه/الاحتياجات')

    product_id_arabi = fields.Many2one('product.template','السلعه')
    qty_arabi = fields.Float('الكميه')
    total_qty = fields.Float('اجمالي القيمه بالعمله الاجنبيه')
    contract_base = fields.Char('اساس التعاقد')
    country_id_araby = fields.Many2one('res.country','بلد المنشأ')
    export_country = fields.Many2one('res.country','البلد المستورد منها البضاعه')
    exporter_sign = fields.Char('توقيع')

    s7b = fields.Float('سحب')
    invoice_no = fields.Char('رقم الفاتوره')
    with_date = fields.Date('بتاريخ')
    with_money = fields.Float('المبلغ')
    polisy = fields.Char('بولصيصه شحن رقم')
    with_date_2 = fields.Date('بتاريخ')
    format_peper = fields.Char('شهاده المنشأ')
    wiegth_peper = fields.Char('شهاده الوزن')
    full_peper = fields.Char('شهاده التعبئه')
    health_peper = fields.Char('شهاده صحيه')

    full_2_peper = fields.Char('شهاده تعبئه')
    analyse_peper = fields.Char('شهاده تحليل')
    others = fields.Char('شهادات اخري ')
    sign_watch = fields.Char('دقق التوقيع')
    signning = fields.Char('التوقيع')


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