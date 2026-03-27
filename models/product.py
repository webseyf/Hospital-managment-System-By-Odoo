from odoo import fields, models

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    hospital_ok = fields.Boolean(string='Is a Medicine', default=False, help="Check this if the product is a medicine or medical supply.")
