# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.
from odoo import models, fields


class WooResPartnerEpt(models.Model):
    _name = "woo.res.partner.ept"
    _description = "WooCommerce Res Partner"

    partner_id = fields.Many2one("res.partner", "Customer", ondelete='cascade')
    woo_customer_id = fields.Char(help="WooCommerce customer id.")
    woo_instance_id = fields.Many2one("woo.instance.ept", "WooCommerce Instances",
                                      help="Instance id managed for identified that customer associated with which "
                                           "instance.")
