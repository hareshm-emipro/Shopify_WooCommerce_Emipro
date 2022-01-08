# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.
import odoo
from odoo import fields, models


class SaleReport(models.Model):
    _inherit = "sale.report"

    woo_instance_id = fields.Many2one("woo.instance.ept", "Woo Instance", copy=False, readonly=True)

    def _query(self, with_clause='', fields={}, groupby='', from_clause=''):
        """
        Inherit the query here to add the woo instance field for group by.
        @author: Haresh Mori @Emipro Technologies Pvt. Ltd on date 29 September 2020.
        Migrated by Maulik Barad on Date 07-Oct-2021.
        """
        fields['woo_instance_id'] = ", s.woo_instance_id as woo_instance_id"
        groupby += ', s.woo_instance_id'
        return super(SaleReport, self)._query(with_clause, fields, groupby, from_clause)

    def woo_sale_report(self):
        """
        Base on the odoo version it return the action.
        @author: Haresh Mori @Emipro Technologies Pvt. Ltd on date 29 September 2020.
        Migrated by Maulik Barad on Date 07-Oct-2021.
        """
        version_info = odoo.service.common.exp_version()
        if version_info.get('server_version') == '15.0':
            action = self.env.ref('woo_commerce_ept.woo_action_order_report_all').read()[0]
        else:
            action = self.env.ref('woo_commerce_ept.woo_sale_report_action_dashboard').read()[0]

        return action
