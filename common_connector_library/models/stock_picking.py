# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.
from odoo import models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    def _action_done(self):
        """
        Create and paid invoice on the basis of auto invoice work flow
        when invoicing policy is 'delivery'.
        Migration done by Haresh Mori on September 2021
        """
        result = super(StockPicking, self)._action_done()
        for picking in self:
            if picking.sale_id.invoice_status == 'invoiced':
                continue

            order = picking.sale_id
            work_flow_process_record = order and order.auto_workflow_process_id
            delivery_lines = picking.move_line_ids.filtered(lambda l: l.product_id.invoice_policy == 'delivery')

            if work_flow_process_record and delivery_lines and work_flow_process_record.create_invoice and \
                picking.picking_type_id.code == 'outgoing':
                order.validate_and_paid_invoices_ept(work_flow_process_record)
        return result

