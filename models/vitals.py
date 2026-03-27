from odoo import api, fields, models, _

class HospitalPatientVitals(models.Model):
    _name = 'hospital.patient.vitals'
    _description = 'Patient Nursing Vitals'
    _order = 'vitals_date desc'

    patient_id = fields.Many2one('hospital.patient', string='Patient', required=True, index=True, ondelete='restrict')
    appointment_id = fields.Many2one('hospital.appointment', string='Appointment', required=True, index=True, ondelete='restrict')
    visit_id = fields.Many2one('hospital.visit', string='Visit', required=True, index=True, ondelete='cascade') # Vitals belong to clinical visit
    vitals_date = fields.Datetime(string='Date', default=fields.Datetime.now)
    
    # Vital Signs
    weight = fields.Float(string='Weight (kg)')
    height = fields.Float(string='Height (cm)')
    temperature = fields.Float(string='Temperature (°C)')
    pulse = fields.Integer(string='Pulse (BPM)')
    sys_bp = fields.Integer(string='Systolic BP (mmHg)')
    dia_bp = fields.Integer(string='Diastolic BP (mmHg)')
    spo2 = fields.Integer(string='SpO2 (%)')
    
    bmi = fields.Float(string='BMI', compute='_compute_bmi', store=True)

    @api.depends('weight', 'height')
    def _compute_bmi(self):
        for rec in self:
            if rec.weight and rec.height:
                height_m = rec.height / 100
                rec.bmi = rec.weight / (height_m * height_m)
            else:
                rec.bmi = 0
