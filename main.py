import os
import xmlrpc.client
from fastapi import FastAPI

app = FastAPI()

ODOO_URL = os.getenv("ODOO_URL")
ODOO_DB = os.getenv("ODOO_DB")
ODOO_USER = os.getenv("ODOO_USER")
ODOO_PASSWORD = os.getenv("ODOO_PASSWORD")

@app.get("/")
def home():
    return {"status": "ok", "service": "targo_odoo"}

@app.get("/test-odoo")
def test_odoo():
    common = xmlrpc.client.ServerProxy(f"{ODOO_URL}/xmlrpc/2/common")
    uid = common.authenticate(ODOO_DB, ODOO_USER, ODOO_PASSWORD, {})

    if not uid:
        return {"ok": False, "message": "No se pudo autenticar con Odoo"}

    return {"ok": True, "uid": uid, "message": "Conexión correcta con Odoo"}


@app.post("/create-order")
async def create_order(request: Request):
    data = await request.json()

    customer_name = data.get("customer_name")
    phone = data.get("phone")
    email = data.get("email")
    order_number = data.get("order_number")

    common = xmlrpc.client.ServerProxy(f"{ODOO_URL}/xmlrpc/2/common")
    uid = common.authenticate(ODOO_DB, ODOO_USER, ODOO_PASSWORD, {})
    models = xmlrpc.client.ServerProxy(f"{ODOO_URL}/xmlrpc/2/object")

    # 1. Buscar cliente
    partner_ids = models.execute_kw(
        ODOO_DB, uid, ODOO_PASSWORD,
        'res.partner', 'search',
        [[['email', '=', email]]]
    )

    if partner_ids:
        partner_id = partner_ids[0]
    else:
        # 2. Crear cliente
        partner_id = models.execute_kw(
            ODOO_DB, uid, ODOO_PASSWORD,
            'res.partner', 'create',
            [{
                'name': customer_name,
                'email': email,
                'phone': phone
            }]
        )

    # 3. Crear orden de venta
    order_id = models.execute_kw(
        ODOO_DB, uid, ODOO_PASSWORD,
        'sale.order', 'create',
        [{
            'partner_id': partner_id,
            'client_order_ref': order_number
        }]
    )

    return {
        "ok": True,
        "order_id": order_id,
        "message": "Orden creada en Odoo"
    }
