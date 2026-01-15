from odoo import http
from odoo.http import request, Response
import json

class ProductAPI(http.Controller):

    @http.route('/api/products', auth='public', type='http', methods=['GET'], csrf=False)
    def get_products(self):
        products = request.env['biozon.product'].search([])
        data = [{'name': p.name, 'price': p.price} for p in products]
        return Response(json.dumps(data), content_type='application/json')

