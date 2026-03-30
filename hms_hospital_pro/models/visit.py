from odoo import fields, models, api, _

class HospitalVisit(models.Model):
    _name = 'hospital.visit'
    _description = 'Patient Visit / Consultation'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Reference', readonly=True, copy=False, default=lambda self: _('New'))
    appointment_id = fields.Many2one('hospital.appointment', string='Appointment', required=True, tracking=True, ondelete='restrict')
    patient_id = fields.Many2one(related='appointment_id.patient_id', string='Patient', required=True, store=True)
    doctor_id = fields.Many2one(related='appointment_id.doctor_id', string='Doctor', required=True, store=True)
    visit_date = fields.Datetime(string='Visit Date', default=fields.Datetime.now, required=True, tracking=True)
    
    # Clinical Data
    symptoms = fields.Text(string='Symptoms', tracking=True)
    diagnosis = fields.Text(string='Diagnosis', required=True, tracking=True)
    notes = fields.Text(string='Notes')
    
    # Relational Data
    prescription_ids = fields.One2many('hospital.prescription', 'visit_id', string='Prescriptions')
    vitals_ids = fields.One2many('hospital.patient.vitals', 'visit_id', string='Vitals')
    lab_request_ids = fields.One2many('hospital.lab.request', 'visit_id', string='Lab Requests')
    radiology_request_ids = fields.One2many('hospital.radiology.request', 'visit_id', string='Radiology Requests')

    # PRODUCTION HARDENING: Odoo 19 Modern SQL Constraint
    _unique_appointment_visit = models.Constraint(
        'UNIQUE(appointment_id)',
        'A consultation already exists for this appointment!'
    )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('hospital.visit') or _('New')
        return super(HospitalVisit, self).create(vals_list)
