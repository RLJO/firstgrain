from odoo import api,fields,models,_
from datetime import datetime, timedelta, time



class VehicleInfo(models.Model):
    _name = 'vehicle.info.line'

    driver_name = fields.Char('Driver Name')
    car_number = fields.Char('Car Number')
    car_type = fields.Char('Car Type')
    destination = fields.Char('Destination')
    qty = fields.Float('Quantity')
    delivery_order = fields.Many2one('stock.picking','Bill Leading')