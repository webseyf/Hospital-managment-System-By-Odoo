from odoo import fields, models

class AccountMove(models.Model):
    _inherit = 'account.move'

    appointment_id = fields.Many2one('hospital.appointment', string='Medical Appointment', readonly=True)
