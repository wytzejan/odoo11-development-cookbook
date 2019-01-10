# -*- coding: utf-8 -*-

from odoo import models, fields, api

class LibraryMember(models.Model):
    _inherit = 'library.member'
    loan_duration = fields.Integer('Loan duration',
                                   default=15,
                                   required=True)
