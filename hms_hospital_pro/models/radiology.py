from odoo import api, fields, models, _

class HospitalRadiologyRequest(models.Model):
    _name = 'hospital.radiology.request'
    _description = 'Radiology Request'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Request ID', readonly=True, copy=False, default='New')
    patient_id = fields.Many2one('hospital.patient', string='Patient', required=True, tracking=True, index=True, ondelete='restrict')
    doctor_id = fields.Many2one('hospital.doctor', string='Requesting Doctor', required=True, tracking=True, index=True, ondelete='restrict')
    appointment_id = fields.Many2one('hospital.appointment', string='Appointment', index=True)
    visit_id = fields.Many2one('hospital.visit', string='Visit', required=True, index=True)
    is_billed = fields.Boolean(string='Invoiced', default=False, copy=False)
    
    date_requested = fields.Datetime(string='Date Requested', default=fields.Datetime.now)
    priority = fields.Selection([('0', 'Low'), ('1', 'Normal'), ('2', 'High'), ('3', 'Urgent')], string='Priority', default='1')
    
    state = fields.Selection([
        ('draft', 'Draft'),
        ('requested', 'Requested'),
        ('imaging', 'Imaging in Progress'),
        ('reporting', 'Reporting'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled')
    ], string='Status', default='draft', tracking=True)
    
    test_id = fields.Many2one('hospital.radiology.test', string='Scan Type', required=True)
    price = fields.Float(related='test_id.price', readonly=True)
    clinical_history = fields.Text(string='Clinical History')
    radiology_report = fields.Html(string='Radiology Report')
    attachment_ids = fields.Many2many('ir.attachment', string='Scans/Images')

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'New') == 'New':
                vals['name'] = self.env['ir.sequence'].next_by_code('hospital.radiology.request') or 'New'
        return super().create(vals_list)

    def action_request(self): self.state = 'requested'
    def action_imaging(self): self.state = 'imaging'
    def action_report(self): self.state = 'reporting'
    def action_complete(self): self.state = 'completed'

class HospitalRadiologyTest(models.Model):
    _name = 'hospital.radiology.test'
    _description = 'Radiology Test Definition'

    name = fields.Char(string='Test Name', required=True)
    code = fields.Char(string='Test Code')
    price = fields.Float(string='Price')
