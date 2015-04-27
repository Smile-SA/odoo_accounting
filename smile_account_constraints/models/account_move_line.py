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

from openerp import models, fields, api, exceptions
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    debit = fields.Float('Debit', digits_compute=dp.get_precision('Account'), readonly=True, states={'draft': [('readonly', False)]})
    credit = fields.Float('Credit', digits_compute=dp.get_precision('Account'), readonly=True, states={'draft': [('readonly', False)]})
    move_id = fields.Many2one('account.move', 'Journal Entry', ondelete="cascade", help="The move of this entry line.",
                              select=2, required=True, readonly=True, states={'draft': [('readonly', False)]})

    @api.multi
    def unlink(self):
        for move_line in self:
            if move_line.move_id and move_line.move_id.state == 'posted':
                raise exceptions.Warning(_("Warning!"), _("You cannot delete journal item linked to posted entry!"))
        return super(AccountMoveLine, self).unlink()

    def write(self, cr, uid, ids, vals, context=None, check=True, update_check=True):
        for move_line in self.browse(cr, uid, ids, context):
            if 'move_id' in vals:
                acc_move = self.pool.get('account.move').browse(cr, uid, vals['move_id'], context=context)
                if acc_move.state == 'posted':
                    raise exceptions.Warning(_("Warning!"), _("You can not associate a new posted entry to journal item!"))
                elif acc_move.state == 'draft' and move_line.state == 'valid':
                    raise exceptions.Warning(_("Warning!"), _("You can not associate a new draft entry to valid journal item!"))
            if move_line.state == 'valid' and move_line.move_id.state == 'posted' and 'debit' in vals:
                raise exceptions.Warning(_("Warning!"), _("You can not update the debit of valid journal item associated to posted entry!"))
            if move_line.state == 'valid' and move_line.move_id.state == 'posted' and 'credit' in vals:
                raise exceptions.Warning(_("Warning!"),
                                         _("You can not update the credit of valid journal item associated to posted entry!"))
        return super(AccountMoveLine, self).write(cr, uid, ids, vals, context, check, update_check)
