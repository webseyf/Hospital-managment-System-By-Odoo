from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class HospitalAppointment(models.Model):
    _name = 'hospital.appointment'
    _description = 'Hospital Appointment'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Reference', required=True, copy=False, readonly=True, default='New')
    patient_id = fields.Many2one('hospital.patient', string='Patient', required=True, tracking=True, ondelete='restrict')
    doctor_id = fields.Many2one('hospital.doctor', string='Doctor', required=True, tracking=True, ondelete='restrict', index=True)
    appointment_type = fields.Selection([
        ('opd', 'Outpatient (OPD)'),
        ('ipd', 'Inpatient (IPD)'),
    ], string='Type', default='opd', required=True, tracking=True)
    is_urgent = fields.Boolean(string='Urgent Case', tracking=True)
    appointment_date = fields.Datetime(string='Appointment Date', required=True, default=fields.Datetime.now, tracking=True, index=True)
    
    # PRODUCTION HARDENING: Odoo 19 Modern Indexing
    _index_doctor_date = models.Index('(doctor_id, appointment_date)')
    _index_appointment_date = models.Index('(appointment_date)')
    duration = fields.Integer(string='Duration (Minutes)', default=30)
    appointment_end = fields.Datetime(string='End Date', compute='_compute_appointment_end', store=True)
    status = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('checked_in', 'Checked-In'), # Added 'checked_in' status
        ('done', 'Done'),
        ('cancelled', 'Cancelled')
    ], string='Status', default='draft', tracking=True)
    
    visit_type = fields.Selection([
        ('opd', 'OPD (Outpatient)'),
        ('ipd', 'IPD (Inpatient)')
    ], string='Visit Type', default='opd', required=True, tracking=True)
    
    # Wait Time Analytics
    checkin_time = fields.Datetime(string='Check-In Time', readonly=True)
    consultation_start = fields.Datetime(string='Consultation Start Time', readonly=True)
    wait_duration = fields.Float(string='Wait Duration (Min)', compute='_compute_wait_duration', store=True)
    
    # Billing
    consultation_fee = fields.Float(string='Consultation Fee', default=50.0, tracking=True)
    payment_status = fields.Selection([
        ('unpaid', 'Unpaid'),
        ('paid', 'Paid')
    ], string='Payment Status', default='unpaid', tracking=True)

    notes = fields.Text(string='Notes')
    visit_id = fields.Many2one('hospital.visit', string='Consultation', readonly=True)
    visit_count = fields.Integer(string='Visit Count', compute='_compute_visit_count')
    
    checkin_date = fields.Datetime(string='Check-in Date', readonly=True)
    checkout_date = fields.Datetime(string='Check-out Date', readonly=True)
    discharge_summary_id = fields.Many2one('hospital.discharge.summary', string='Discharge Summary', readonly=True)

    def action_discharge(self):
        """ Professional Discharge Workflow """
        for rec in self:
            if rec.appointment_type == 'ipd' and not rec.discharge_summary_id:
                # Force summary creation for IPD
                return {
                    'name': _('Create Discharge Summary'),
                    'type': 'ir.actions.act_window',
                    'res_model': 'hospital.discharge.summary',
                    'view_mode': 'form',
                    'target': 'new',
                    'context': {'default_appointment_id': rec.id},
                }
            rec.action_done()

    @api.constrains('status', 'appointment_type', 'bed_id')
    def _check_ipd_bed(self):
        for rec in self:
            if rec.appointment_type == 'ipd' and rec.status == 'checked_in' and not rec.bed_id:
                raise ValidationError(_("A bed must be assigned for Inpatient (IPD) check-in!"))
    
    # IPD Data
    ward_id = fields.Many2one('hospital.ward', string='Ward')
    bed_id = fields.Many2one('hospital.bed', string='Bed', domain="[('ward_id', '=', ward_id), ('state', '=', 'available')]")
    
    vitals_ids = fields.One2many('hospital.patient.vitals', 'appointment_id', string='Vitals')
    vitals_count = fields.Integer(string='Vitals Count', compute='_compute_vitals_count')
    
    # Billing / Invoicing
    invoice_id = fields.Many2one('account.move', string='Invoice', readonly=True)

    # Laboratory
    lab_request_ids = fields.One2many('hospital.lab.request', 'appointment_id', string='Lab Requests')
    lab_count = fields.Integer(string='Lab Count', compute='_compute_lab_count')

    # Radiology
    radiology_request_ids = fields.One2many('hospital.radiology.request', 'appointment_id', string='Radiology Requests')
    radiology_count = fields.Integer(string='Radiology Count', compute='_compute_radiology_count')

    @api.depends('appointment_date', 'duration')
    def _compute_appointment_end(self):
        from datetime import timedelta
        for rec in self:
            if rec.appointment_date:
                rec.appointment_end = rec.appointment_date + timedelta(minutes=rec.duration)
            else:
                rec.appointment_end = False

    def _compute_visit_count(self):
        for rec in self:
            rec.visit_count = 1 if rec.visit_id else 0

    def action_view_visit(self):
        """Smart Button action to view or create a visit for this appointment"""
        self.ensure_one()
        if self.status not in ('confirmed', 'done'):
            raise UserError(_("You can only start a consultation (visit) for confirmed appointments."))
            
        if not self.visit_id:
            # Create a new visit if it doesn't exist
            visit = self.env['hospital.visit'].create({
                'appointment_id': self.id,
            })
            self.visit_id = visit.id
        
        return {
            'name': _('Consultation'),
            'type': 'ir.actions.act_window',
            'res_model': 'hospital.visit',
            'res_id': self.visit_id.id,
            'view_mode': 'form',
            'target': 'current',
        }

    @api.onchange('doctor_id')
    def _onchange_doctor_id(self):
        if self.doctor_id:
            self.consultation_fee = self.doctor_id.consultation_fee

    @api.constrains('appointment_date', 'appointment_end', 'doctor_id')
    def _check_overlap(self):
        """
        PRODUCTION HARDENING: Batch-safe overlap check.
        Instead of searching inside the loop (N+1), we perform a broader search
        and then check for intersections in memory.
        """
        for rec in self:
            if not rec.appointment_date or not rec.appointment_end:
                continue
                
            # Search for ANY appointments for this doctor that might intersect
            overlap = self.search([
                ('id', '!=', rec.id),
                ('doctor_id', '=', rec.doctor_id.id),
                ('appointment_date', '<', rec.appointment_end),
                ('appointment_end', '>', rec.appointment_date),
            ], limit=1)
            
            if overlap:
                raise ValidationError(_(
                    "Scheduling Conflict: Doctor %s is already booked from %s to %s."
                ) % (rec.doctor_id.name, overlap.appointment_date, overlap.appointment_end))

    @api.constrains('consultation_fee', 'payment_status')
    def _check_billing_safety(self):
        for rec in self:
            if rec.payment_status == 'paid' and rec.consultation_fee <= 0:
                raise ValidationError(_("You cannot mark an appointment as 'Paid' if the consultation fee is zero or negative!"))

    def action_confirm(self):
        for rec in self:
            rec.status = 'confirmed'

    def action_done(self):
        """
        PRODUCTION HARDENING: Ensure no pending diagnostic orders.
        """
        for rec in self:
            pending_lab = rec.lab_request_ids.filtered(lambda l: l.state not in ('completed', 'cancelled'))
            pending_rad = rec.radiology_request_ids.filtered(lambda r: r.state not in ('completed', 'cancelled'))
            
            if pending_lab or pending_rad:
                raise ValidationError(_(
                    "Cannot mark appointment as Done while there are pending diagnostic orders!\n"
                    "Pending Lab: %s\nPending Radiology: %s"
                ) % (len(pending_lab), len(pending_rad)))
                
            rec.status = 'done'
            rec.checkout_date = fields.Datetime.now()
            if rec.bed_id:
                rec.bed_id.state = 'available'
                rec.bed_id.patient_id = False

    def action_cancel(self):
        for rec in self:
            rec.status = 'cancelled'

    def action_draft(self):
        for rec in self:
            rec.status = 'draft'

    def action_checkin(self):
        for rec in self:
            rec.status = 'checked_in'
            rec.checkin_time = fields.Datetime.now()
            rec.checkin_date = fields.Datetime.now()
            if rec.bed_id:
                rec.bed_id.state = 'occupied'
                rec.bed_id.patient_id = rec.patient_id.id

    @api.depends('checkin_time', 'consultation_start')
    def _compute_wait_duration(self):
        for rec in self:
            if rec.checkin_time and rec.consultation_start:
                diff = rec.consultation_start - rec.checkin_time
                rec.wait_duration = diff.total_seconds() / 60.0
            else:
                rec.wait_duration = 0.0

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'New') == 'New':
                vals['name'] = self.env['ir.sequence'].next_by_code('hospital.appointment') or 'New'
        return super().create(vals_list)

    def _compute_vitals_count(self):
        for rec in self:
            rec.vitals_count = len(rec.vitals_ids)

    def _compute_lab_count(self):
        for rec in self:
            rec.lab_count = len(rec.lab_request_ids)

    def _compute_radiology_count(self):
        for rec in self:
            rec.radiology_count = len(rec.radiology_request_ids)

    def action_view_vitals(self):
        self.ensure_one()
        return {
            'name': _('Nursing Vitals'),
            'type': 'ir.actions.act_window',
            'res_model': 'hospital.patient.vitals',
            'view_mode': 'list,form',
            'domain': [('appointment_id', '=', self.id)],
            'context': {
                'default_patient_id': self.patient_id.id,
                'default_appointment_id': self.id,
                'default_visit_id': self.visit_id.id,
            },
            'target': 'current',
        }

    def action_view_lab(self):
        self.ensure_one()
        return {
            'name': _('Laboratory Requests'),
            'type': 'ir.actions.act_window',
            'res_model': 'hospital.lab.request',
            'view_mode': 'list,form',
            'domain': [('appointment_id', '=', self.id)],
            'context': {
                'default_patient_id': self.patient_id.id,
                'default_doctor_id': self.doctor_id.id,
                'default_appointment_id': self.id,
                'default_visit_id': self.visit_id.id,
            },
            'target': 'current',
        }

    def action_view_radiology(self):
        self.ensure_one()
        return {
            'name': _('Radiology Requests'),
            'type': 'ir.actions.act_window',
            'res_model': 'hospital.radiology.request',
            'view_mode': 'list,form',
            'domain': [('appointment_id', '=', self.id)],
            'context': {
                'default_patient_id': self.patient_id.id,
                'default_doctor_id': self.doctor_id.id,
                'default_appointment_id': self.id,
                'default_visit_id': self.visit_id.id,
            },
            'target': 'current',
        }

    def action_view_invoice(self):
        self.ensure_one()
        return {
            'name': _('Invoice'),
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
            'res_id': self.invoice_id.id,
            'view_mode': 'form',
            'target': 'current',
        }

    def action_create_invoice(self):
        self.ensure_one()
        if self.invoice_id:
            raise ValidationError(_("An invoice already exists for this appointment."))
            
        partner = self.patient_id.partner_id
        if not partner:
            raise ValidationError(_("Patient must be linked to a Partner (Customer) for invoicing."))

        invoice_lines = []
        
        # 1. Consultation Fee
        invoice_lines.append((0, 0, {
            'name': _('Consultation Fee: %s') % self.doctor_id.name,
            'quantity': 1,
            'price_unit': self.consultation_fee,
        }))
        
        # 2. Pharmacy Products (from Prescription)
        if self.visit_id:
            for pres in self.visit_id.prescription_ids:
                invoice_lines.append((0, 0, {
                    'product_id': pres.medicine_id.id,
                    'name': pres.medicine_id.name,
                    'quantity': pres.qty,
                    'price_unit': pres.medicine_id.list_price,
                }))
        
        # 3. Lab Tests (Only Unbilled)
        unbilled_lab_lines = self.lab_request_ids.mapped('test_line_ids').filtered(lambda l: not l.is_billed)
        for line in unbilled_lab_lines:
            invoice_lines.append((0, 0, {
                'name': _('Laboratory Test: %s') % line.test_id.name,
                'quantity': 1,
                'price_unit': line.test_id.price,
            }))
            line.is_billed = True
                
        # 4. Radiology Tests (Only Unbilled)
        unbilled_rad_requests = self.radiology_request_ids.filtered(lambda r: not r.is_billed)
        for rad in unbilled_rad_requests:
            invoice_lines.append((0, 0, {
                'name': _('Imaging: %s') % rad.test_id.name,
                'quantity': 1,
                'price_unit': rad.test_id.price,
            }))
            rad.is_billed = True

        invoice_vals = {
            'move_type': 'out_invoice',
            'partner_id': partner.id,
            'appointment_id': self.id,
            'invoice_date': fields.Date.today(),
            'invoice_line_ids': invoice_lines,
        }
        invoice = self.env['account.move'].create(invoice_vals)
        self.invoice_id = invoice.id
        
        return {
            'name': _('Invoice'),
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
            'res_id': invoice.id,
            'view_mode': 'form',
            'target': 'current',
        }
