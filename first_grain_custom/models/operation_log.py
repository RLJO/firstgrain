from odoo import api,fields,models,_
from datetime import datetime, timedelta, time



class Operation(models.Model):
    _name = "operation.log"
    _description = "Operation Log"

    date = fields.Date('Date')
    description = fields.Char('Description')
    user_id = fields.Many2one('res.users','User')
    operation_id = fields.Many2one('operation.logistic')