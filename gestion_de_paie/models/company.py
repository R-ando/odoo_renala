# -*- coding: utf-8 -*-


from odoo import fields, models

class company(models.Model):
    _inherit = "res.company"

    company_matricule = fields.Char(string="Numéro Matricule", size=11)
    sme = fields.Integer(string="SME", size=8)