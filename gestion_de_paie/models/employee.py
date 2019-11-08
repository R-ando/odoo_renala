# -*- coding: utf-8 -*-


from odoo import models, fields


class Employee(models.Model):
    _inherit = 'hr.employee'
    _name = 'hr.employee'

    first_name = fields.Char(string="Prenom", size=128)
    num_cnaps_emp = fields.Char(string="N° CNAPS", size=6)
    num_cin = fields.Char(string="N° CIN", size=10)
    date_cin = fields.Date(string='Date CIN')
    lieu_cin = fields.Char(string='Lieu de délivrance CIN')
    num_emp = fields.Char(string="N° Matricule", size=10)
    nombre_enfant_cnaps = fields.Integer(string=u"Nombre d'enfant allouée CNaPS")
