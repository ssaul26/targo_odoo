import os
import xmlrpc.client
from fastapi import FastAPI, Request, Body

app = FastAPI()

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
async def create_order(data: dict = Body(...)):
    
    billing = data.get("billing", {})

    customer_name = f"{billing.get('first_name', '')} {billing.get('last_name', '')}"
    phone = billing.get("phone", "")
    email = billing.get("email", "")
    order_number = str(data.get("id"))

    common = xmlrpc.client.ServerProxy(f"{ODOO_URL}/xmlrpc/2/common")
    uid = common.authenticate(ODOO_DB, ODOO_USER, ODOO_PASSWORD, {})
    models = xmlrpc.client.ServerProxy(f"{ODOO_URL}/xmlrpc/2/object")

    partner_ids = models.execute_kw(
        ODOO_DB, uid, ODOO_PASSWORD,
        'res.partner', 'search',
        [[['email', '=', email]]]
    )

    if partner_ids:
        partner_id = partner_ids[0]
    else:
        partner_id = models.execute_kw(
            ODOO_DB, uid, ODOO_PASSWORD,
            'res.partner', 'create',
            [{
                'name': customer_name,
                'email': email,
                'phone': phone
            }]
        )

    order_id = models.execute_kw(
        ODOO_DB, uid, ODOO_PASSWORD,
        'sale.order', 'create',
        [{
            'partner_id': partner_id,
            'client_order_ref': order_number
        }]
    )

    return {"ok": True, "order_id": order_id}
