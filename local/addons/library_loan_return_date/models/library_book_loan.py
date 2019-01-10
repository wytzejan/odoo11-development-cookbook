# -*- coding: utf-8 -*-

from odoo import models, fields, api

class LibraryBookLoan(models.Model):
    _inherit = 'library.book.loan'
    expected_return_date = fields.Date ('Due for', required=True)