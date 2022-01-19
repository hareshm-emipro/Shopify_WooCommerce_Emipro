#!/usr/bin/python3
# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.
from odoo import fields, models


class SaleReport(models.Model):
    _inherit = "sale.report"

    ebay_instance_id = fields.Many2one('ebay.instance.ept', 'eBay Sites', readonly=True)
    ebay_seller_id = fields.Many2one('ebay.seller.ept', 'eBay Seller', readonly=True)

    def _query(self, with_clause='', fields={}, groupby='', from_clause=''):
        fields['ebay_instance_id'] = ", s.ebay_instance_id as ebay_instance_id"
        fields['ebay_seller_id'] = ", s.ebay_seller_id as ebay_seller_id"
        groupby += ', s.ebay_instance_id, s.ebay_seller_id'
        return super()._query(with_clause, fields, groupby, from_clause)
