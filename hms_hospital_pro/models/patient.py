from datetime import date
from odoo import api, fields, models, _

class HospitalPatient(models.Model):
    _name = 'hospital.patient'
    _description = 'Patient Master Data'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Name', required=True, tracking=True, index=True)
    uhid = fields.Char(string='UHID', required=True, copy=False, readonly=True, index=True, default=lambda self: _('New'))
    ref = fields.Char(string='Internal Reference', readonly=True, copy=False, default=lambda self: _('New'))
    partner_id = fields.Many2one('res.partner', string='Related Partner', ondelete='restrict', help="Linked Partner for Invoicing")
    
    # Core Patient Info
    date_of_birth = fields.Date(string='Date of Birth', tracking=True)
    age = fields.Integer(string='Age', compute='_compute_age', store=True, tracking=True, index=True)
    is_minor = fields.Boolean(string='Is Minor', compute='_compute_is_minor', store=True)
    gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
    ], string='Gender', default='male', tracking=True)
    blood_group = fields.Selection([
        ('A+', 'A+'), ('A-', 'A-'),
        ('B+', 'B+'), ('B-', 'B-'),
        ('AB+', 'AB+'), ('AB-', 'AB-'),
        ('O+', 'O+'), ('O-', 'O-'),
    ], string='Blood Group', tracking=True)
    marital_status = fields.Selection([
        ('single', 'Single'),
        ('married', 'Married'),
        ('widowed', 'Widowed'),
        ('divorced', 'Divorced'),
    ], string='Marital Status', tracking=True)
    medical_alert = fields.Text(string='Medical Alerts', help='Allergies, chronic conditions, etc.', tracking=True)
    
    # Emergency Contact
    emergency_contact_name = fields.Char(string='Emergency Contact Name', tracking=True)
    emergency_contact_phone = fields.Char(string='Emergency Contact Phone', tracking=True)
    active = fields.Boolean(string='Active', default=True)
    
    # EMR & Clinical Data
    allergies = fields.Text(string='Allergies', tracking=True)
    medical_history = fields.Text(string='Medical History', tracking=True)
    image_1920 = fields.Image(string='Profile Picture')
    
    # Contact Info
    phone = fields.Char(string='Phone', tracking=True)
    email = fields.Char(string='Email')
    address = fields.Text(string='Address')

    # Relational Data
    doctor_id = fields.Many2one('hospital.doctor', string='Assigned Doctor', tracking=True)
    appointment_ids = fields.One2many('hospital.appointment', 'patient_id', string='Appointments')
    tag_ids = fields.Many2many('hospital.tag', string='Tags')
    appointment_count = fields.Integer(string='Appointment Count', compute='_compute_appointment_count')
    next_appointment_id = fields.Many2one('hospital.appointment', compute='_compute_next_appointment', string='Next Appointment')
    medical_timeline = fields.Html(string='Medical Timeline', compute='_compute_medical_timeline', store=True)

    @api.depends('appointment_ids.appointment_date', 'appointment_ids.status')
    def _compute_next_appointment(self):
        """
        PERFORMANCE TIP: We use for rec in self to stay batch-safe.
        By using rec.appointment_ids (a prefetched set), we avoid 
        making a separate DATABASE SEARCH for every patient (N+1 Problem).
        """
        for rec in self:
            # We filter only confirmed appointments in the future
            future_apps = rec.appointment_ids.filtered(
                lambda a: a.status == 'confirmed' and a.appointment_date >= date.today()
            ).sorted(key='appointment_date')
            
            rec.next_appointment_id = future_apps[0] if future_apps else False

    @api.depends('ref', 'name')
    def _compute_display_name(self):
        for rec in self:
            res = []
            if rec.ref:
                res.append(f"[{rec.ref}]")
            if rec.name:
                res.append(rec.name)
            rec.display_name = " ".join(res) or _("New Patient")

    def _compute_appointment_count(self):
        for rec in self:
            rec.appointment_count = len(rec.appointment_ids)

    def action_view_appointments(self):
        return {
            'name': _('Appointments'),
            'res_model': 'hospital.appointment',
            'view_mode': 'list,form',
            'domain': [('patient_id', '=', self.id)],
            'target': 'current',
            'type': 'ir.actions.act_window',
        }

    @api.depends('date_of_birth')
    def _compute_age(self):
        for rec in self:
            today = date.today()
            if rec.date_of_birth:
                rec.age = today.year - rec.date_of_birth.year - (
                    (today.month, today.day) < (rec.date_of_birth.month, rec.date_of_birth.day)
                )
            else:
                rec.age = 0

    @api.depends('age')
    def _compute_is_minor(self):
        for rec in self:
            rec.is_minor = rec.age < 18

    @api.autovacuum
    def _archive_old_patients(self):
        # Implementation for archiving inactive patients (Real HMS requirement)
        pass

    @api.depends('appointment_ids.appointment_date', 'appointment_ids.status', 'appointment_ids.visit_id.diagnosis')
    def _compute_medical_timeline(self):
        """
        PRODUCTION HARDENING: Generates a professional EMR summary.
        """
        for rec in self:
            html = "<ul class='list-unstyled'>"
            # Sort appointments by date descending (latest first)
            apps = rec.appointment_ids.sorted(key='appointment_date', reverse=True)
            for app in apps:
                html += f"<li><b>{app.appointment_date.strftime('%Y-%m-%d')}</b> - {app.status.capitalize()} Consultation"
                if app.visit_id:
                    html += f"<br/><small>Diagnosis: {app.visit_id.diagnosis or 'N/A'}</small>"
                if app.lab_request_ids:
                    html += f"<br/><small>Labs: {', '.join(app.lab_request_ids.mapped('name'))}</small>"
                html += "</li><hr/>"
            html += "</ul>"
            rec.medical_timeline = html

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('ref', _('New')) == _('New'):
                vals['ref'] = self.env['ir.sequence'].next_by_code('hospital.patient') or _('New')
            if vals.get('uhid', _('New')) == _('New'):
                vals['uhid'] = self.env['ir.sequence'].next_by_code('hospital.patient.uhid') or _('New')
            
            # Create a related partner if not already provided
            if not vals.get('partner_id'):
                partner = self.env['res.partner'].create({
                    'name': vals.get('name'),
                    'email': vals.get('email'),
                    'phone': vals.get('phone'),
                    'is_company': False,
                    'type': 'contact',
                })
                vals['partner_id'] = partner.id

        return super(HospitalPatient, self).create(vals_list)
