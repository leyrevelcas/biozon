from odoo import http
from odoo.http import request, Response
import json

import base64

class ProductAPI(http.Controller):

    @http.route('/api/products', auth='public', type='http', methods=['GET'], csrf=False)
    def get_products(self):
        products = request.env['biozon.product'].search([])
        data = [{'name': p.name, 'price': p.price} for p in products]
        return Response(json.dumps(data), content_type='application/json')

    @http.route('/api/productsImg/<int:product_id>', auth='public', type='http', methods=['GET'], csrf=False)
    def get_products_img(self, product_id):
        products = request.env["biozon.product"].sudo().browse(product_id)
        if not products.exists():
            return request.not_found()
        # ahora ya si se descarga una imagen normal, esto antes no iba
        return Response(base64.b64decode(products.image), content_type='application/img')