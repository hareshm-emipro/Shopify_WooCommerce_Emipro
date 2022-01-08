# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.
import logging

from datetime import datetime, timedelta

from odoo import models, fields

_logger = logging.getLogger("WooCommerce")


class CommonLogBookEpt(models.Model):
    _inherit = "common.log.book.ept"
    _order = "id desc"

    woo_instance_id = fields.Many2one("woo.instance.ept", "Woo Instance")

    def woo_prepare_data_for_activity(self):
        """
        This method prepares necessary data from the log lines.
        @author: Maulik Barad on Date 10-Nov-2020.
        Migrated by Maulik Barad on Date 07-Oct-2021.
        """
        ir_model_obj = self.env["ir.model"]

        if self.log_lines.woo_order_data_queue_line_id:
            queue_lines = self.log_lines.woo_order_data_queue_line_id.filtered(lambda x: x.state == "failed")
            queue_id = queue_lines.order_data_queue_id
            model_name = "woo.order.data.queue.ept"
            woo_order_list = queue_lines.mapped("woo_order")
            note = "Your order has not been imported for Woo Order Reference : %s" % str(woo_order_list)[1:-1]
        else:
            queue_lines = self.log_lines.woo_product_queue_line_id.filtered(lambda x: x.state == "failed")
            queue_id = queue_lines.queue_id
            model_name = "woo.product.data.queue.ept"
            woo_order_list = queue_lines.mapped("woo_synced_data_id")
            note = "Your products has not been imported as Woo Products Reference : %s" % str(woo_order_list)[1:-1]
        model_id = ir_model_obj.search([("model", "=", model_name)])

        return queue_id, woo_order_list, note, model_id

    def create_woo_schedule_activity(self, queue_id=False, model_id=False, queue_crash_activity=False):
        """
        @author: Haresh Mori on date 03/12/2019
        Migrated by Maulik Barad on Date 07-Oct-2021.
        """
        woo_order_list = []
        mail_activity_obj = self.env["mail.activity"]

        if queue_crash_activity:
            woo_instance = queue_id.woo_instance_id
            note = "<p>Attention %s queue is processed 3 times you need to process it manually.</p>" % queue_id.name
        else:
            woo_instance = self.woo_instance_id
            queue_id, woo_order_list, note, model_id = self.woo_prepare_data_for_activity()

        activity_type_id = woo_instance.activity_type_id.id
        date_deadline = datetime.strftime(datetime.now() + timedelta(days=woo_instance.date_deadline), "%Y-%m-%d")

        if (note and woo_order_list) or queue_crash_activity:
            for user_id in woo_instance.user_ids:
                mail_activity = mail_activity_obj.search([("res_model_id", "=", model_id.id),
                                                          ("user_id", "=", user_id.id),
                                                          ("res_name", "=", queue_id.name),
                                                          ("activity_type_id", "=", activity_type_id)])
                if not mail_activity:
                    vals = {"activity_type_id": activity_type_id, "note": note, "res_id": queue_id.id,
                            "user_id": user_id.id, "res_model_id": model_id.id, "date_deadline": date_deadline}
                    try:
                        mail_activity_obj.create(vals)
                    except Exception:
                        _logger.info("Unable to create schedule activity, Please give proper "
                                     "access right of this user :%s  ", user_id.name)
        return True

    def woo_create_log_book(self, operation_type, instance, log_lines=False):
        """
        This method is used to create a log book.
        @param operation_type: Which type of operation is perform(import,export).
        @param instance: Browsable record of instance.
        @param log_lines: Ids of log lines.
        @author: Haresh Mori @Emipro Technologies Pvt. Ltd on date 6 November 2020 .
        Task_id: 168147 - Code refactoring : 5th - 6th November
        Migrated by Maulik Barad on Date 07-Oct-2021.
        """
        vals = {
            'type': operation_type,
            'module': 'woocommerce_ept',
            'woo_instance_id': instance.id if instance else False,
            'active': True,
            'log_lines': [(6, 0, log_lines if log_lines else [])],
        }
        log_book_id = self.create(vals)
        return log_book_id
