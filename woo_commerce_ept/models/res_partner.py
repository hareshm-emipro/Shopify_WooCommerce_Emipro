# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.
import logging
import requests

from odoo import models, fields, api, _
from odoo.exceptions import UserError

_logger = logging.getLogger("WooCommerce")


class ResPartner(models.Model):
    _inherit = "res.partner"

    is_woo_customer = fields.Boolean(string="Is Woo Customer?",
                                     help="Used for identified that the customer is imported from WooCommerce store.")

    def woo_check_proper_response(self, response, common_log_id):
        """
        This method checks for errors in received response from WooCommerce and creates log line for the issue.
        @param response: Response from the WooCommerce.
        @param common_log_id: Record of Logbook.
        @author: Maulik Barad on Date 31-Oct-2020.
        Migrated by Maulik Barad on Date 07-Oct-2021.
        """
        common_log_line_obj = self.env["common.log.lines.ept"]
        model_id = common_log_line_obj.get_model_id("woo.instance.ept")

        if not isinstance(response, requests.models.Response):
            message = "Import all customers \nResponse is not in proper format :: %s" % response
            common_log_line_obj.woo_product_export_log_line(message, model_id, common_log_id)
            return []
        if response.status_code not in [200, 201]:
            message = "Error in Import All Customers %s" % response.content
            common_log_line_obj.woo_product_export_log_line(message, model_id, common_log_id)
            return []
        try:
            data = response.json()
        except Exception as error:
            message = "Json Error : In import customers from WooCommerce. \n%s" % error
            common_log_line_obj.woo_product_export_log_line(message, model_id, common_log_id)
            return []
        return data

    def woo_import_all_customers(self, wc_api, common_log_id, page, woo_process_import_export_id):
        """
        This method used to request for the customer page.
        @param : self, wc_api, common_log_id, page, woo_process_import_export_id
        @author: Maulik Barad on Date 30-Oct-2020.
        Migrated by Maulik Barad on Date 07-Oct-2021.
        """
        queue_ids = []

        try:
            res = wc_api.get('customers', params={"per_page": 100, 'page': page})
        except Exception as error:
            raise UserError(_("Something went wrong while importing Customers.\n\nPlease Check your Connection and "
                              "Instance Configuration.\n\n" + str(error)))

        response = self.woo_check_proper_response(res, common_log_id)
        if response:
            queue_ids = self.create_woo_customer_queue(response, woo_process_import_export_id).ids
        return queue_ids

    @api.model
    def woo_get_customers(self, common_log_id, instance):
        """
        This method used to call the request of the customer and prepare a customer response.
        @param : self, common_log_id, instance
        @return: customers
        @author: Haresh Mori @Emipro Technologies Pvt. Ltd on date 28 August 2020.
        Migrated by Maulik Barad on Date 07-Oct-2021.
        """
        process_import_export = self.env["woo.process.import.export"]
        customer_queues = []

        woo_process_import_export_id = process_import_export.browse(self._context.get('import_export_record_id'))
        wc_api = instance.woo_connect()
        try:
            response = wc_api.get('customers', params={"per_page": 100})
        except Exception as error:
            raise UserError(_("Something went wrong while importing Customers.\n\nPlease Check your Connection and "
                              "Instance Configuration.\n\n" + str(error)))
        customers = self.woo_check_proper_response(response, common_log_id)
        if not customers:
            return customers
        total_pages = response.headers.get('X-WP-TotalPages')
        if int(total_pages) >= 2:
            queues = self.create_woo_customer_queue(customers, woo_process_import_export_id)
            customer_queues += queues.ids
            for page in range(2, int(total_pages) + 1):
                queue_ids = self.woo_import_all_customers(wc_api, common_log_id, page, woo_process_import_export_id)
                customer_queues += queue_ids
        else:
            queues = self.create_woo_customer_queue(customers, woo_process_import_export_id)
            customer_queues += queues.ids
        return customer_queues

    def create_woo_customer_queue(self, customer_data, woo_process_import_export_id):
        """
        This method creates queues for customer and notifies user about that.
        @param customer_data: Data of customer.
        @param woo_process_import_export_id: Record of process.import.export model.
        @return: Records of Customer queues.
        @author: Maulik Barad on Date 30-Oct-2020.
        Migrated by Maulik Barad on Date 07-Oct-2021.
        """
        bus_bus_obj = self.env['bus.bus']

        queues = woo_process_import_export_id.woo_create_customer_queue(customer_data)
        message = "Customer Queue created %s" % queues.mapped('name')
        bus_bus_obj._sendone(self.env.user.partner_id, 'simple_notification',
                             {'title': 'WooCommerce Connector', 'message': message, "sticky": False,
                              "warning": True})
        self._cr.commit()
        return queues

    def woo_create_contact_customer(self, vals, instance=False):
        """
        This method used to create a contact type customer.
        @param : self, vals, instance=False
        @return: partner
        @author: Haresh Mori @Emipro Technologies Pvt. Ltd on date 2 September 2020 .
        Migrated by Maulik Barad on Date 07-Oct-2021.
        """
        woo_partner_obj = self.env['woo.res.partner.ept']

        partner = woo_partner = woo_customer_id = False
        woo_id = vals.get('id') or False
        contact_first_name = vals.get('first_name', '')
        contact_last_name = vals.get('last_name', '')
        contact_email = vals.get('email', '')

        contact_name = "%s %s" % (contact_first_name, contact_last_name)
        if not contact_first_name and not contact_last_name:
            return False
        if woo_id:
            woo_customer_id = "%s" % woo_id
            woo_partner = woo_partner_obj.search([("woo_customer_id", "=", woo_customer_id),
                                                  ("woo_instance_id", "=", instance.id)], limit=1)
        if woo_partner:
            partner = woo_partner.partner_id
            return partner
        woo_partner_values = {'woo_customer_id': woo_customer_id, 'woo_instance_id': instance.id}
        if contact_email:
            partner = self.search_partner_by_email(contact_email)

        # If partner is not found, then need to create it.
        if not partner:
            contact_partner_vals = ({'customer_rank': 1, 'is_woo_customer': True, 'type': 'contact',
                                     'name': contact_name, 'email': contact_email or False})
            if vals.get('billing') and vals.get('billing').get('first_name') and vals.get('billing').get('last_name'):
                contact_partner_vals = self.woo_prepare_partner_vals(vals.get('billing'), instance)
                contact_partner_vals.update({'customer_rank': 1, 'is_woo_customer': True, 'type': 'invoice'})
            partner = self.create(contact_partner_vals)
        # If partner is found, then need to check if is_woo_customer is set or not in it.
        if not partner.is_woo_customer:
            partner.write({'is_woo_customer': True})

        partner.create_woo_res_partner_ept(woo_partner_values)
        return partner

    def create_woo_res_partner_ept(self, woo_partner_values):
        """
        This method use to create a Woocommerce layer customer.
        @param : self,woo_partner_values
        @author: Haresh Mori @Emipro Technologies Pvt. Ltd on date 31 August 2020 .
        Migrated by Maulik Barad on Date 07-Oct-2021.
        """
        woo_partner_obj = self.env['woo.res.partner.ept']
        woo_partner_values.update({'partner_id': self.id})
        return woo_partner_obj.create(woo_partner_values)

    def woo_search_address_partner(self, partner_vals, address_key_list, parent_id, partner_type):
        """
        This method searches for existing shipping/billing address.
        @param partner_vals: Dictionary of address data.
        @param address_key_list: Keys of address to check.
        @param parent_id: Id of existing partner, for searching in child of that partner.
        @param partner_type: Type of address to search for.
        @author: Maulik Barad on Date 31-Oct-2020.
        Migrated by Maulik Barad on Date 07-Oct-2021.
        """
        domain = [('type', '=', partner_type)]
        if parent_id:
            parent_domain = [('parent_id', '=', parent_id.id)]
            domain += parent_domain
        else:
            parent_domain = []
        address_partner = self._find_partner_ept(partner_vals, address_key_list, domain)
        if not address_partner:
            address_partner = self._find_partner_ept(partner_vals, address_key_list, parent_domain)
        if not address_partner:
            address_partner = self._find_partner_ept(partner_vals, address_key_list)
        return address_partner

    def woo_create_or_update_customer(self, customer_val, instance, parent_id, partner_type, customer_id=False):
        """
        This method used to create a billing and shipping address base on the customer val response.
        @param : self,customer_val,instance,parent_id,type
        @return: address_partner
        @author: Haresh Mori @Emipro Technologies Pvt. Ltd on date 2 September 2020 .
        Migrated by Maulik Barad on Date 07-Oct-2021.
        """
        address_key_list = ['name', 'street', 'street2', 'city', 'zip', 'phone', 'state_id', 'country_id']

        first_name = customer_val.get("first_name")
        last_name = customer_val.get("last_name")
        if not first_name and not last_name:
            return False
        company_name = customer_val.get("company")
        partner_vals = self.woo_prepare_partner_vals(customer_val, instance)
        woo_partner_values = {'woo_customer_id': customer_id, 'woo_instance_id': instance.id}

        if partner_type == 'delivery':
            address_key_list.remove("phone")
        if company_name:
            address_key_list.append('company_name')
            partner_vals.update({'company_name': company_name})

        address_partner = self.woo_search_address_partner(partner_vals, address_key_list, parent_id, partner_type)
        if address_partner:
            if not parent_id and customer_id and not address_partner.is_woo_customer:
                address_partner.create_woo_res_partner_ept(woo_partner_values)
                address_partner.write({'is_woo_customer': True})
            return address_partner

        if 'company_name' in partner_vals:
            partner_vals.pop('company_name')
        if parent_id:
            partner_vals.update({'parent_id': parent_id.id})
        partner_vals.update({'type': partner_type})
        address_partner = self.create(partner_vals)
        if not parent_id and customer_id:
            address_partner.create_woo_res_partner_ept(woo_partner_values)
            address_partner.write({'is_woo_customer': True})
        company_name and address_partner.write({'company_name': company_name})
        return address_partner

    def woo_prepare_partner_vals(self, vals, instance):
        """
        This method used to prepare a partner vals.
        @param : self,vals,instance
        @return: partner_vals
        @author: Haresh Mori @Emipro Technologies Pvt. Ltd on date 29 August 2020 .
        Migrated by Maulik Barad on Date 07-Oct-2021.
        """
        email = vals.get("email", False)
        first_name = vals.get("first_name")
        last_name = vals.get("last_name")
        name = "%s %s" % (first_name, last_name)
        phone = vals.get("phone")
        address1 = vals.get("address_1")
        address2 = vals.get("address_2")
        city = vals.get("city")
        zipcode = vals.get("postcode")
        state_code = vals.get("state")
        country_code = vals.get("country")

        country = self.get_country(country_code)
        state = self.create_or_update_state_ept(country_code, state_code, False, country)

        partner_vals = {
            'email': email or False, 'name': name, 'phone': phone,
            'street': address1, 'street2': address2, 'city': city, 'zip': zipcode,
            'state_id': state and state.id or False, 'country_id': country and country.id or False,
            'is_company': False, 'lang': instance.woo_lang_id.code,
        }
        update_partner_vals = self.remove_special_chars_from_partner_vals(partner_vals)
        return update_partner_vals
