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

    @api.depends('currency','subtotal_in_number','currency_money','total_money','currency_ids')
    def currency_text(self):
        if self.currency:
            self.subtotal_in_word =  self.currency.amount_to_text(self.subtotal_in_number)
        else:
            self.subtotal_in_word = ''

        if self.total_money :
            self.total_money_in_words =self.currency_money.amount_to_text(self.total_money)
        else:
            self.total_money_in_words = ''

        if self.currency_ids :
            self.money_in_words = self.currency_ids.amount_to_text(self.money)
            self.with_value_of_in_word = self.currency_ids.amount_to_text(self.with_value_of)
            self.money2_in_words = self.currency_ids.amount_to_text(self.money2)
        else:
            self.money_in_words = ''
            self.with_value_of_in_word = ''
            self.money2_in_words = ''

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

    # AL-AHLY BANK

    company_name = fields.Char('الشركه')
    money = fields.Float('المبلغ')
    money_in_words = fields.Char(compute='currency_text')
    bank_ahly_account = fields.Char('رقم الحساب')
    ahly_asign = fields.Char('التوقيع')

    company_name_for = fields.Char(' لـ شركه')
    money_for = fields.Float('المبلغ')
    invoice_number = fields.Char('رقم الفاتوره')
    for_assign =  fields.Char('التوقيع')

    cairo_at = fields.Date('Cairo At')
    with_value_of =  fields.Float('With Value Of')
    with_value_of_in_word =  fields.Char('With Value Of')
    maturity_date = fields.Date('Maturity Date')
    supplier = fields.Char('Supplier')
    invoice = fields.Char('Invoice No')
    signature_form = fields.Char('Signature')
    
    date = fields.Date('التاريخ')
    bank_branch = fields.Char('فرع البنك')
    benefet_name = fields.Char('اسم المستفيد')
    total_money_doc = fields.Float('اجمالي مبلغ التحصيل المستندي')
    currency_ids = fields.Many2one('res.currency','العمله')
    payment_term = fields.Char('شروط السداد')
    anti_doc = fields.Char('ضد المستندات')
    payment_money = fields.Float('مبلغ الاستحقاق')
    payment_date = fields.Date('تاريخ الاستحقاق')
    name_sign = fields.Char('الاسم')
    name_signture = fields.Char('التوقيع')

    date2 = fields.Date('التاريخ')
    import_name = fields.Char('اسم المورد بالانجليزيه')
    money2 = fields.Float('المبلغ')
    money2_in_words = fields.Char(compute='currency_text')
    company_name_2 = fields.Char('نقر نحن شركه')
    company_address_2 = fields.Char( 'المركز الرئيسي')
    segel_togary = fields.Char('سجل تجاري رقم')
    name_signture_2 = fields.Char('التوقيع')
    his_title = fields.Char('صفته')
    compony_name = fields.Char('اسم الشركه')
    name_signture_right_2 = fields.Char('من له حق التوقيع')
    title = fields.Char('الصفه')
    name_signture_2 = fields.Char('التوقيع')

    importer_name = fields.Char('اسم المستورد')
    importer_address = fields.Char('عنوان النشاط الرئيسي')
    importer_card = fields.Char('رقم البطاقه الاستراديه/الاجتياجات')
    tax_card = fields.Char('رقم البطاقه الضريبيه')

    product_id_2 = fields.Many2one('product.template','السلعه')
    product_qty = fields.Float('الكميه')
    unit_o_m = fields.Many2one('uom.uom','وحده القياس')
    unit_money = fields.Float('اجمالي القيمه بالعمله الاجنبيه')
    contract_base2 = fields.Char('اساس التعاقد')
    contry = fields.Many2one('res.country','بلد المنشأ')
    contry_2 = fields.Many2one('res.country','بلد المستورده منها البضاعه')

    comp_name = fields.Char('اسم الشركه')
    signn = fields.Char('التوقيع')

    funding_resource = fields.Char('مصدر التمويل')
    funding_way = fields.Char('طريقه السداد')

    def action_form_prepare(self):
        self.state = 'prepare'

    def action_form_done(self):
        self.state = 'done'

