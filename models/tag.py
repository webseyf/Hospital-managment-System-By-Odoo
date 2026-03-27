from odoo import fields, models

class HospitalTag(models.Model):
    _name = 'hospital.tag'
    _description = 'Patient Medical Tags'

    name = fields.Char(string='Name', required=True)
    color = fields.Integer(string='Color')
