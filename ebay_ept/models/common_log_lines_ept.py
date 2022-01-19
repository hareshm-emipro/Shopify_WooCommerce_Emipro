#!/usr/bin/python3
# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.
"""
Describes new fields and methods for common log lines
"""
from odoo import models, fields


class CommonLogLineEpt(models.Model):
    """
    Describes common log book line
    """
    _inherit = "common.log.lines.ept"
    ebay_order_data_queue_line_id = fields.Many2one(
        "ebay.order.data.queue.line.ept", string="eBay Order Queue Line", help="eBay Order data queue line")
    import_product_queue_line_id = fields.Many2one(
        "ebay.import.product.queue.line", string="Product Queue Line", help="eBay product data queue line")

    def ebay_create_order_log_line(self, message, model_id, queue_line_id):
        """
        This method used to create a log line.
        :param message: Log line message
        :param model_id: model id to be store in log line
        :param queue_line_id: ebay order data queue line object
        :returns : common log line object
        """
        vals = {
            'message': message, 'model_id': model_id, 'res_id': queue_line_id and queue_line_id.id or False,
            'ebay_order_data_queue_line_id': queue_line_id and queue_line_id.id or False}
        return self.create(vals)
