# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.
from odoo import models, fields


class DeliveryCarrier(models.Model):
    """
    Inherited to add the woocommerce carriers.
    @author: Maulik Barad on Date 12-Nov-2019.
    Migrated by Maulik Barad on Date 07-Oct-2021.
    """
    _inherit = "delivery.carrier"

    woo_code = fields.Char(help="WooCommerce Delivery Code")
