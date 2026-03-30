from odoo import fields, models

class HospitalStaff(models.Model):
    _name = 'hospital.staff'
    _description = 'Clinical and Administrative Staff'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Name', required=True, tracking=True)
    role = fields.Selection([
        ('nurse', 'Nurse'),
        ('pathologist', 'Pathologist'),
        ('radiologist', 'Radiologist'),
        ('pharmacist', 'Pharmacist'),
        ('receptionist', 'Receptionist'),
        ('admin', 'Administrator'),
    ], string='Role', required=True, tracking=True)
    
    user_id = fields.Many2one('res.users', string='Related User')
    department_id = fields.Many2one('hospital.department', string='Department')
    active = fields.Boolean(default=True)
    phone = fields.Char(string='Phone')
    email = fields.Char(string='Email')
    
    # Audit Trail
    _user_unique = models.Constraint(
        'UNIQUE(user_id)',
        'A user can only be linked to one staff member!'
    )
