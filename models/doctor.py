from odoo import fields, models

class HospitalDoctor(models.Model):
    _name = 'hospital.doctor'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Hospital Doctor'

    name = fields.Char(string='Name', required=True, tracking=True)
    specialization = fields.Char(string='Specialization', required=True, tracking=True)
    user_id = fields.Many2one('res.users', string='Related User')
    department_id = fields.Many2one('hospital.department', string='Department', tracking=True)
    consultation_duration = fields.Float(string='Consultation Duration (Mins)', default=15.0)
    available_days = fields.Many2many('hospital.week.day', string='Available Days')
    consultation_fee = fields.Float(string='Consultation Fee', default=500.0, tracking=True)
    active = fields.Boolean(string='Active', default=True)
    phone = fields.Char(string='Phone')
    email = fields.Char(string='Email')
    patient_ids = fields.One2many('hospital.patient', 'doctor_id', string='Patients')
