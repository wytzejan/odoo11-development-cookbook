# -*- coding: utf-8 -*-

from odoo import models, fields, api

class LibraryMember(models.Model):
    _inherit = 'library.member'
    loan_duration = fields.Integer('Loan duration',
                                   default=15,
                                   required=True)

    @api.multi
    def return_all_books(self):
        self.ensure_one()
        wizard = self.env['library.returns.wizard']
        values = {
            'member_id': self.id,
            'book_ids': False
        }
        specs = wizard._onchange_spec()
        updates = wizard.onchange(values, ['member_id'], specs)
        value = updates.get('value', {})
        for name, val in value.items():
            if isinstance(val, tuple):
                value[name] = val[0]
        values.update(value)
        wiz = wizard.create(values)
        return wiz.record_returns()
