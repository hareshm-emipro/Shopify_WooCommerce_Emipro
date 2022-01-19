#!/usr/bin/python3
# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.
from . import models
from . import wizard
from . import report
from . import controllers
from odoo import api, SUPERUSER_ID
import string
import random


def generate_varification_token(crval, registry):
    """
    This method is generate random unique verification token with db_uuid for
    "eBay Marketplace Account Deletion/Closure Notifications Workflow"
    and set that generated token
    under the verification_token field under the seller.

    @author: Prashant Ramoliya @Emipro Technologies Pvt. Ltd on date 29/09/2021.
    Task Id : 178404
    :return:
    """
    env = api.Environment(crval, SUPERUSER_ID, {})
    config_para = env['ir.config_parameter']

    length = 10
    db_uuid = config_para.sudo().get_param('database.uuid')
    randomstr = ''.join(random.choices(string.ascii_letters + string.digits + '_', k=length))
    config_para.sudo().create({'key': "Marketplace Account Verification Token",
                        "value": db_uuid + randomstr})
    return True
