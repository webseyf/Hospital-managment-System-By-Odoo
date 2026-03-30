from odoo import api, fields, models

class HospitalPrescription(models.Model):
    _name = 'hospital.prescription'
    _description = 'Patient Prescription'

    visit_id = fields.Many2one('hospital.visit', string='Visit', required=True, ondelete='cascade')
    medicine_id = fields.Many2one('product.product', string='Medicine', required=True, domain=[('hospital_ok', '=', True)])
    lot_id = fields.Many2one('stock.lot', string='Batch / Lot', domain="[('product_id', '=', medicine_id)]")
    qty = fields.Float(string='Quantity', default=1.0)
    expiry_date = fields.Datetime(related='lot_id.expiration_date', string='Expiry Date', readonly=True)
    is_expired = fields.Boolean(compute='_compute_is_expired')
    dosage = fields.Char(string='Dosage', help='e.g. 1-0-1 or 500mg')
    duration = fields.Char(string='Duration', help='e.g. 5 Days')
    instruction = fields.Text(string='Special Instructions')
    @api.depends('expiry_date')
    def _compute_is_expired(self):
        today = fields.Date.today()
        for rec in self:
            rec.is_expired = rec.expiry_date and rec.expiry_date < today or False
