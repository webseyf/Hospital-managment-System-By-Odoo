from odoo import api, fields, models, _

class HospitalDepartment(models.Model):
    _name = 'hospital.department'
    _description = 'Hospital Department'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Name', required=True, tracking=True)
    active = fields.Boolean(string='Active', default=True)
    department_head_id = fields.Many2one('hospital.doctor', string='Head of Department (HOD)')
    doctor_ids = fields.One2many('hospital.doctor', 'department_id', string='Doctors')
    description = fields.Text(string='Description')
