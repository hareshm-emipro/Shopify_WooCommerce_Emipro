# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.
from odoo import models, fields


class CommonLogLinesEpt(models.Model):
    _inherit = "common.log.lines.ept"
    _rec_name = "message"

    woo_customer_data_queue_line_id = fields.Many2one("woo.customer.data.queue.line.ept", "Woo Customer Queue Line")
    woo_order_data_queue_line_id = fields.Many2one("woo.order.data.queue.line.ept", "Woo Order Queue Line")
    woo_product_queue_line_id = fields.Many2one("woo.product.data.queue.line.ept", "Woo Product Queue Line")
    woo_coupon_data_queue_line_id = fields.Many2one("woo.coupon.data.queue.line.ept", "Woo Coupon Queue Line")

    def woo_create_product_log_line(self, message, model_id, queue_line_id, common_log_id):
        """
        This method is used to create a log line
        @param message: It contain the error message if error is generate while processing the product and its type
        is string
        @param model_id: It contain the id of the model and Its type is Integer
        @param queue_line_id: It contain the value of type integer of queue line id
        @param common_log_id:
        @return: return the new log line
        @author: Dipak Gogiya @Emipro Technologies Pvt.Ltd
        Migrated by Maulik Barad on Date 07-Oct-2021.
        """
        vals = {"message": message,
                "model_id": model_id,
                "log_book_id": common_log_id.id}
        if queue_line_id._name == "woo.order.data.queue.line.ept":
            vals.update({"woo_order_data_queue_line_id": queue_line_id.id})
        else:
            vals.update({"woo_product_queue_line_id": queue_line_id.id})
        return self.create(vals)

    def woo_product_export_log_line(self, message, model_id, common_log_id=False, product_template_id=False):
        """
        :param message: It contain the error message of product export or import processing
        :param common_log_id: It contain the io of the common log book and its type is Object
        :param model_id: It contain the id of the model and Its type is Integer
        :param product_template_id: It contain the browsable object of Product template
        @author: Dipak Gogiya @Emipro Technologies Pvt.Ltd
        Migrated by Maulik Barad on Date 07-Oct-2021.
        """
        vals = {"message": message,
                "model_id": model_id,
                "log_book_id": False if not common_log_id else common_log_id.id,
                "res_id": False if not product_template_id else product_template_id.id}
        return self.create(vals)
