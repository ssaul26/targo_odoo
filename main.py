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
