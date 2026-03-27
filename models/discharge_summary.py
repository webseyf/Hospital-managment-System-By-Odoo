from odoo import fields, models, api, _

class HospitalDischargeSummary(models.Model):
    _name = 'hospital.discharge.summary'
    _description = 'Patient Discharge Summary'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Reference', readonly=True, copy=False, default=lambda self: _('New'))
    appointment_id = fields.Many2one('hospital.appointment', string='Appointment', required=True, ondelete='cascade')
    patient_id = fields.Many2one(related='appointment_id.patient_id', string='Patient', store=True)
    doctor_id = fields.Many2one(related='appointment_id.doctor_id', string='Consultant Doctor', store=True)
    admission_date = fields.Datetime(related='appointment_id.checkin_date', string='Admission Date')
    discharge_date = fields.Datetime(string='Discharge Date', default=fields.Datetime.now)
    
    # Summary Data
    final_diagnosis = fields.Text(string='Final Diagnosis', required=True)
    clinical_summary = fields.Text(string='Clinical Summary', help='A brief summary of the patients history and clinical course.')
    treatment_given = fields.Text(string='Treatment Given')
    followup_instructions = fields.Text(string='Follow-up Instructions')
    is_discharged = fields.Boolean(default=True)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('hospital.discharge.summary') or _('New')
        return super(HospitalDischargeSummary, self).create(vals_list)
