# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import base64
from collections import OrderedDict
from datetime import datetime

from odoo import http
from odoo.http import content_disposition, Controller, request, route
from odoo.exceptions import AccessError, MissingError
from odoo.http import request, Response
from odoo.tools import image_process
from odoo.tools.translate import _
from odoo.addons.portal.controllers import portal
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager

class CustomerPortal(CustomerPortal):
    
    OPTIONAL_BILLING_FIELDS = ["zipcode", "state_id", "vat", "company_name", "file"]
    MANDATORY_BILLING_FIELDS = ["name", "phone", "email", "street", "city", "country_id", "l10n_id_nik"]
    
    def _prepare_portal_layout_values(self):
        result = super()._prepare_portal_layout_values()
        partner_sudo = request.env.user.partner_id
        result['l10n_id_nik'] = partner_sudo.l10n_id_nik
        return result
    

    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        VendorPricelist = request.env['product.supplierinfo']
        Submission = request.env['vendor.pricelist.submission']
        if 'pricelist_count' in counters:
            values['pricelist_count'] = VendorPricelist.search_count([
            ]) if VendorPricelist.check_access_rights('read', raise_exception=False) else 0
        if 'submission_count' in counters:
            vendor_submission_count = Submission.search_count([
            ]) if Submission.check_access_rights('read', raise_exception=False) else 0
            values['submission_count'] = vendor_submission_count
        return values
    
    def _prepare_searchbar_sortings(self):
        return {
            'date': {'label': _('Newest'), 'order': 'create_date desc'},
            'name': {'label': _('Name'), 'order': 'product_name'},
        }
        
    @http.route(['/my/price-submissions', '/my/price-submissions/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_price_submission(self, page=1, date_begin=None, date_end=None, sortby=None, **kw):
        values = self._prepare_portal_layout_values()
        Submission = request.env['vendor.pricelist.submission']
        submissions = Submission.search([],)
        values.update({
            'submissions': submissions,
            'page_name': 'vendor_pricelist_submissions',
            'default_url': '/my/price-submissions',
        })
        return request.render("susanti_vendor_portal.portal_my_price_submissions", values)
    
    @http.route(['/my/price-submission/items', '/my/price-submission/items/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_price_submission_items(self, page=1, date_begin=None, date_end=None, sortby=None, **kw):
        values = self._prepare_portal_layout_values()
        Pricelist = request.env['product.supplierinfo']
        domain = []
        if date_begin and date_end:
            domain += [('create_date', '>', date_begin), ('create_date', '<=', date_end)]
            
        searchbar_sortings = self._prepare_searchbar_sortings()
        if not sortby or sortby not in searchbar_sortings:
            sortby = 'date'
        order = searchbar_sortings[sortby]['order']

        # Pricelist count
        pricelist_count = Pricelist.search_count(domain)
        # pager
        pager = portal_pager(
            url="/my/price-submission/items",
            url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby},
            total=pricelist_count,
            page=page,
            step=self._items_per_page
        )

        # content according to pager and archive selected
        pricelists = Pricelist.search([], order=order, limit=self._items_per_page, offset=pager['offset'])
        shipmentlocs = request.env['shipment.location'].search([])
        shipment_capacity_list = request.env['shipment.capacity'].sudo().search([])
        request.session['my_price_history'] = pricelists.ids[:100]
        values.update({
            'date': date_begin,
            'date_end': date_end,
            'pricelists': pricelists,
            'shipmentlocs': shipmentlocs,
            'shipment_capacity_list': shipment_capacity_list,
            'page_name': 'vendor_pricelist',
            'default_url': '/my/price-submission/items',
            'pager': pager,
            'searchbar_sortings': searchbar_sortings,
            'sortby': sortby
        })
        return request.render("susanti_vendor_portal.portal_my_price_submission_items", values)
    
    def details_form_validate(self, data, partner_creation=False):
        error, error_message = super().details_form_validate(data, partner_creation=partner_creation)
        partner_id = request.env.user.partner_id.id
        user_id = request.session.uid
        attachment_ids = request.env['ir.attachment'].sudo().search([
            ('res_model', '=', 'res.partner'), ('res_id', '=', partner_id),
            ('create_uid', '=', user_id)])
        if not attachment_ids:
            error['common'] = 'Missing required attachments'
            error_message.append("Upload your NPWP/Company Document/Company Profile")
        return error, error_message
    
    
class VendorPortalController(http.Controller):
    
    @http.route(['/attachment_proof/submit'], type='json', auth="public")
    def attachment_proof(self, **kw):
        if 'partner_id' in kw:
            partner_id = int(kw.get('partner_id'))
        else:
            partner_id = request.session.partner_id
        attached_files = kw['attachments']
        for attachment in attached_files:
            name = attachment['name']
            content = attachment['content']
            request.env['ir.attachment'].sudo().create({
                'name': name,
                'res_model': 'res.partner',
                'res_id': partner_id,
                'type': 'binary',
                'public': True,
                'datas': content,
            })
        return

    @http.route(['/attachment_proof/show_updated'], type='json', auth="public")
    def vendor_show_attachment(self, **kw):
        partner_id = request.env.user.partner_id.id
        user_id = request.session.uid
        attachment_ids_list = []
        attachment_ids = request.env['ir.attachment'].sudo().search([
            ('res_model', '=', 'res.partner'), ('res_id', '=', partner_id),
            ('create_uid', '=', user_id)])
        for attachment_id in attachment_ids:
            attachment_ids_list.append(({
                'id': attachment_id.id,
                'name': attachment_id.name
            }))
        return attachment_ids_list
    
    
    
    @http.route(['/payment_proof/submit'], type='json', auth="public")
    def payment_proof(self, **kw):
        if 'invoice_id' in kw:
            invoice_id = int(kw.get('invoice_id'))
        else:
            invoice_id = request.session.invoice
        attached_files = kw['attachments']
        for attachment in attached_files:
            name = attachment['name']
            content = attachment['content']
            request.env['ir.attachment'].sudo().create({
                'name': name,
                'res_model': 'account.move',
                'res_id': invoice_id,
                'type': 'binary',
                'public': True,
                'datas': content,
            })
        return

    @http.route(['/my_vendor_bill_screen/show_updated'], type='json', auth="public")
    def payment_show_receipt(self, **kw):
        if kw:
            invoice_id = kw['data']
        else:
            invoice_id = request.session.invoice
        user_id = request.session.uid
        attachment_ids_list = []
        attachment_ids = request.env['ir.attachment'].sudo().search([(
            'res_model', '=', 'account.move'), ('res_id', '=', invoice_id),
            ('create_uid', '=', user_id)])
        for attachment_id in attachment_ids:
            attachment_ids_list.append(({
                'id': attachment_id.id,
                'name': attachment_id.name
            }))
        return attachment_ids_list
