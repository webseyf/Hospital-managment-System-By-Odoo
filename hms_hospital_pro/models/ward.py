from odoo import api, fields, models, _

class HospitalWard(models.Model):
    _name = 'hospital.ward'
    _description = 'Hospital Ward'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Ward Name', required=True, tracking=True)
    building = fields.Char(string='Building')
    floor = fields.Integer(string='Floor')
    total_beds = fields.Integer(string='Total Beds', compute='_compute_total_beds')
    bed_ids = fields.One2many('hospital.bed', 'ward_id', string='Beds')

    @api.depends('bed_ids')
    def _compute_total_beds(self):
        for rec in self:
            rec.total_beds = len(rec.bed_ids)

class HospitalBed(models.Model):
    _name = 'hospital.bed'
    _description = 'Hospital Bed'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Bed Number', required=True, tracking=True)
    ward_id = fields.Many2one('hospital.ward', string='Ward', required=True, tracking=True)
    state = fields.Selection([
        ('available', 'Available'),
        ('occupied', 'Occupied'),
        ('reserved', 'Reserved'),
        ('under_maintenance', 'Maintenance')
    ], string='Status', default='available', tracking=True)
    patient_id = fields.Many2one('hospital.patient', string='Current Patient', readonly=True)
