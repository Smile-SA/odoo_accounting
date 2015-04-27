# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 Smile (<http://www.smile.fr>). All Rights Reserved
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import openerp.tests.common as common
from openerp import workflow


class test_account(common.TransactionCase):

    def setUp(self):
        super(test_account, self).setUp()
        self.account_inv = self.env['account.invoice']
        self.account_inv_line = self.env['account.invoice.line']
        self.a_period = self.env['account.period']
        partner_id = self.env.ref('base.res_partner_2')
        journal_id = self.env.ref('account.sales_journal')
        company_id = self.env.ref('base.main_company')
        currency_id = self.env.ref('base.EUR')
        a_rec_id = self.env.ref('account.a_recv')
        a_sale_id = self.env.ref('account.a_sale')
        product_id = self.env.ref('product.product_product_5')

        # INVOICE1
        inv_vals1 = {'partner_id': partner_id.id,
                     'journal_id': journal_id.id,
                     'company_id': company_id.id,
                     'currency_id': currency_id.id,
                     'account_id': a_rec_id.id,
                     'date_invoice': '2015-01-07'}
        self.inv_id1 = self.account_inv.create(inv_vals1)

        inv_line_vals1 = {'product_id': product_id.id,
                          'account_id': a_sale_id.id,
                          'name': '[PC-DEM] PC on Demand',
                          'price_unit': 900.0,
                          'quantity': 10.0,
                          'invoice_id': self.inv_id1.id}
        self.inv_line_id1 = self.account_inv_line.create(inv_line_vals1)

        # INVOICE2
        inv_vals2 = {'partner_id': partner_id.id,
                     'journal_id': journal_id.id,
                     'company_id': company_id.id,
                     'currency_id': currency_id.id,
                     'account_id': a_rec_id.id,
                     'date_invoice': '2015-02-02'}
        self.inv_id2 = self.account_inv.create(inv_vals2)

        inv_line_vals2 = {'product_id': product_id.id,
                          'account_id': a_sale_id.id,
                          'name': '[PC-DEM] PC on Demand',
                          'price_unit': 800.0,
                          'quantity': 5.0,
                          'invoice_id': self.inv_id2.id}
        self.inv_line_id2 = self.account_inv_line.create(inv_line_vals2)
        # GET PERIODS
        self.period_id1 = self.a_period.find(self.inv_id1.date_invoice)
        self.period_id2 = self.a_period.find(self.inv_id2.date_invoice)

    def test_invoice_move_seq1(self):
        self.cr.execute('select COUNT(*) from account_invoice where period_id = %s', (self.period_id1.id,))
        pcount = int(self.cr.fetchall()[0][0]) + 1
        workflow.trg_validate(self.uid, 'account.invoice', self.inv_id1.id, 'invoice_open', self.cr)
        self.assertTrue(self.inv_id1.state == 'wait')
        self.assertTrue(self.inv_id1.move_id.name == '2015/01/%04d' % pcount)
        self.assertTrue(self.inv_id1.number == '2015/01/%04d' % pcount)

    def test_invoice_move_seq2(self):
        self.cr.execute('select COUNT(*) from account_invoice where period_id = %s', (self.period_id2.id,))
        pcount = int(self.cr.fetchall()[0][0]) + 1
        workflow.trg_validate(self.uid, 'account.invoice', self.inv_id2.id, 'invoice_open', self.cr)
        self.assertTrue(self.inv_id2.state == 'wait')
        self.assertTrue(self.inv_id2.move_id.name == '2015/02/%04d' % pcount)
        self.assertTrue(self.inv_id2.number == '2015/02/%04d' % pcount)
