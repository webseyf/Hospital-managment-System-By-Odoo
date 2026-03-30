from odoo import api, fields, models, _

class HospitalLabRequest(models.Model):
    _name = 'hospital.lab.request'
    _description = 'Laboratory Request'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Request ID', readonly=True, copy=False, default='New')
    patient_id = fields.Many2one('hospital.patient', string='Patient', required=True, tracking=True, index=True, ondelete='restrict')
    doctor_id = fields.Many2one('hospital.doctor', string='Requesting Doctor', required=True, tracking=True, index=True, ondelete='restrict')
    appointment_id = fields.Many2one('hospital.appointment', string='Appointment', index=True)
    visit_id = fields.Many2one('hospital.visit', string='Visit', required=True, index=True)
    
    date_requested = fields.Datetime(string='Date Requested', default=fields.Datetime.now)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('requested', 'Requested'),
        ('collecting', 'Sample Collection'),
        ('testing', 'Testing'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled')
    ], string='Status', default='draft', tracking=True)
    
    test_line_ids = fields.One2many('hospital.lab.request.line', 'request_id', string='Tests')

    def action_request(self):
        for rec in self:
            rec.state = 'requested'

    def action_collect(self):
        for rec in self:
            rec.state = 'collecting'

    def action_test(self):
        for rec in self:
            rec.state = 'testing'

    def action_complete(self):
        for rec in self:
            rec.state = 'completed'

    def action_cancel(self):
        for rec in self:
            rec.state = 'cancelled'

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'New') == 'New':
                vals['name'] = self.env['ir.sequence'].next_by_code('hospital.lab.request') or 'New'
        return super().create(vals_list)

class HospitalLabRequestLine(models.Model):
    _name = 'hospital.lab.request.line'
    _description = 'Lab Request Line'

    request_id = fields.Many2one('hospital.lab.request', string='Request', ondelete='cascade')
    test_id = fields.Many2one('hospital.lab.test', string='Test', required=True)
    result_value = fields.Char(string='Result Value')
    normal_range = fields.Char(related='test_id.normal_range', string='Normal Range', readonly=True)
    unit = fields.Char(related='test_id.unit', string='Unit', readonly=True)
    is_billed = fields.Boolean(string='Invoiced', default=False, copy=False)

class HospitalLabTest(models.Model):
    _name = 'hospital.lab.test'
    _description = 'Lab Test Definition'

    name = fields.Char(string='Test Name', required=True)
    code = fields.Char(string='Test Code')
    normal_range = fields.Char(string='Normal Range')
    unit = fields.Char(string='Unit')
    price = fields.Float(string='Price')
