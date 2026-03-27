from odoo import fields, models

class HospitalWeekDay(models.Model):
    _name = 'hospital.week.day'
    _description = 'Days of the Week'
    _order = 'sequence'

    name = fields.Char(required=True)
    sequence = fields.Integer(default=10)
    code = fields.Char(required=True)
