from odoo import models, fields, api, tools


class LibraryBookLoan(models.Model):
    _name = 'library.book.loan'
    book_id = fields.Many2one('library.book', 'Book',
                              required=True)
    member_id = fields.Many2one('library.member', 'Borrower',
                                required=True)
    state = fields.Selection([('ongoing', 'Ongoing'),
                              ('done', 'Done')],
                             'State',
                             default='ongoing', required=True)


class LibraryLoanWizard(models.TransientModel):
    _name = 'library.loan.wizard'
    member_id = fields.Many2one('library.member', string='Member')
    book_ids = fields.Many2many('library.book', string='Books')
    expected_return_date = fields.Date('Expected return date')

    @api.multi
    def record_loans(self):
        loan = self.env['library.book.loan']
        for wizard in self:
            member = wizard.member_id
            books = wizard.book_ids
            for book in books:
                # values = wizard._prepare_loan(book)
                loan.create({
                    'member_id': member.id,
                    'book_id': book.id
                })

    @api.multi
    def _prepare_loan(self, book):
        return {'member_id': self.member_id.id,
                'book_id': book.id}


class LibraryReturnsWizard(models.TransientModel):
    _name = 'library.returns.wizard'
    member_id = fields.Many2one('library.member', string='Member')
    book_ids = fields.Many2many('library.book', string='Books')

    @api.multi
    def record_returns(self):
        loan = self.env['library.book.loan']
        for rec in self:
            loans = loan.search(
                [('state', '=', 'ongoing'),
                 ('book_id', 'in', rec.book_ids.ids),
                 ('member_id', '=', rec.member_id.id)]
            )
            loans.write({'state': 'done'})
        return True

    @api.onchange('member_id')
    def onchange_member(self):
        loan = self.env['library.book.loan']
        loans = loan.search(
            [('state', '=', 'ongoing'),
             ('member_id', '=', self.member_id.id)]
        )
        self.book_ids = loans.mapped('book_id')
        # result = {
        #     'domain': {'book_ids': [
        #         ('id', 'in', self.book_ids.ids)
        #     ]}
        # }
        # late_domain = [
        #     ('id', 'in', loans.id),
        #     ('expected_return_date', '<', fields.Date.today())
        # ]
        # late_loans = loans.search(late_domain)
        # if late_loans:
        #     message = ('Warn the member that the following '
        #                'books are late:\n')
        #     titles = late_loans.mapped('book_id.name')
        #     result['warning'] = {
        #         'title': 'Late books',
        #         'message': message + '\n'.join(titles)
        #     }
        # return result


class LibraryBookLoanStatistics(models.Model):
    _name = 'library.book.loan.statistics'
    _auto = False

    book_id = fields.Many2one('library.book', 'Book', readonly=True)
    loan_id = fields.Many2one('library.book.loan', 'Loan', readonly=True)
    author_id = fields.Many2one('res.partner', 'Author', readonly=True)
    reader_id = fields.Many2one('library.member', 'Reader', readonly=True)
    reader_age = fields.Integer(
        'Reader age', readonly=True,
        group_operator='avg',
        help="the age of the reader when he borrowed the book"
    )

    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        query = """
        CREATE OR REPLACE VIEW library_book_loan_statistics AS (
        SELECT loan.id + author.res_partner_id * (SELECT MAX(id) FROM
                                                    library_book_loan)
                    AS id,
                loan.book_id AS book_id,
                loan.id AS loan_id,
                author.res_partner_id AS author_id,
                reader.id AS reader_id,
                EXTRACT(YEAR FROM age(loan.create_date,
                                            reader.date_of_birth))
                    AS reader_age
        FROM library_book_loan AS loan
        JOIN library_book AS book ON (loan.book_id = book.id)
        JOIN library_book_res_partner_rel AS author ON (book.id =
                                                author.library_book_id)
        JOIN library_member as reader ON (loan.member_id = reader.id)
        )
        """
        self.env.cr.execute(query)
