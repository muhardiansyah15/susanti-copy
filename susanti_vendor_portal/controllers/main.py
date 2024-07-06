import requests
import os, ssl
import uuid
from odoo import http, _
from odoo.http import request
from datetime import datetime



class VendorPortalController(http.Controller):

    @http.route(['/my/price-submission/items/create'], type='json', auth='public', methods=['POST'], website=True, csrf=False)
    def create_pricelist_item(self, pricelist_item_data, **kw):
        try:
            user = request.env['res.users'].browse(request.env.user.id)
            shipment_from =  pricelist_item_data.get('delivery_from', False)
            shipment_to =  pricelist_item_data.get('delivery_to', False)
            vals = {
                'product_name': pricelist_item_data.get('pricelistitem_name', "New Pricelist Item"),
                'product_code': pricelist_item_data.get('pricelistitem_code', False),
                'partner_id': user.partner_id.id,
                'shipment_from_id': shipment_from and int(shipment_from),
                'shipment_to_id': shipment_to and int(shipment_to),
                'date_start': pricelist_item_data.get('start_date', False),
                'date_end': pricelist_item_data.get('end_date', False),
                'price': float(pricelist_item_data.get('price', 0)),
                'product_tmpl_id': 8,
                'shipment_capacity_id': pricelist_item_data.get('shipment_capacity', False) and int(pricelist_item_data.get('shipment_capacity')),
                'fee_type': pricelist_item_data.get('fee_type', False),
                'note': pricelist_item_data.get('note', False),
            }
            pricelistitem_id = request.env['product.supplierinfo'].sudo().create(vals)
            if pricelistitem_id and shipment_from and shipment_to:
                delivery_product = request.env['product.template'].sudo().search([('shipment_from_id','=',int(shipment_from)),
                                                                                  ('shipment_to_id','=',int(shipment_to))], limit=1)
                if delivery_product:
                    pricelistitem_id.sudo().write({'product_tmpl_id': delivery_product.id})
            if pricelistitem_id:
                return {'success': True}
            return {'success': False, 'message': _("Something went wrong while creating the project, please try again")}
        except:
            return {'success': False, 'message': _("Something went wrong while creating the project, please try again")}
        
        
        
    @http.route('/my/price-submission/items/update', type='http', auth="user", website=True)
    def update_pricelist_item(self, pricelist_id, **kw):
        pricelist = request.env['product.supplierinfo'].browse(int(pricelist_id))
        if pricelist:
            pricelist.write({'state': 'submit'})
            delivery_product = request.env['product.template'].sudo().search([('shipment_from_id','=',pricelist.shipment_from_id.id),
                                                                                  ('shipment_to_id','=',pricelist.shipment_to_id.id)], limit=1)
            if delivery_product:
                pricelist.write({'product_tmpl_id': delivery_product.id})
            
        return request.redirect('/my/price-submission/items')