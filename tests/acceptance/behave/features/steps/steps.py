from behave import given, when, then
import requests
import time
import os

# Allow overriding the API base via env var so tests can run both locally
# and inside Docker. Default targets the running FastAPI server on localhost.
API_BASE = os.getenv("API_BASE", "http://localhost:8000/api")


@given('the API is available')
def step_api_available(context):
    # simple health check loop
    for _ in range(20):
        try:
            r = requests.get(f"{API_BASE}/invoices")
            if r.status_code in (200, 404, 405):
                return
        except Exception:
            time.sleep(0.5)
    assert False, 'API not available'


@when('I create an invoice with customer "{customer}" and amount {amount:f} and invoiceNumber "{invoiceNumber}"')
def step_create_invoice(context, customer, amount, invoiceNumber):
    payload = {"customer": customer, "amount": float(amount), "invoiceNumber": invoiceNumber}
    r = requests.post(f"{API_BASE}/invoices", json=payload)
    context.last_response = r
    if r.status_code == 200:
        context.invoice_id = r.json().get('id')


@when('I add an item to the invoice with productId "{productId}" and description "{description}" and quantity {quantity:d} and unitPrice {unitPrice:f}')
def step_add_item(context, productId, description, quantity, unitPrice):
    assert hasattr(context, 'invoice_id'), 'invoice_id missing'
    payload = {"productId": productId, "description": description, "quantity": int(quantity), "unitPrice": float(unitPrice)}
    r = requests.post(f"{API_BASE}/invoices/{context.invoice_id}/items", json=payload)
    context.last_response = r
    if r.status_code == 200:
        context.last_json = r.json()


@when('I update item {productId} on the invoice to quantity {quantity:d}')
def step_update_item(context, productId, quantity):
    assert hasattr(context, 'invoice_id')
    r = requests.patch(f"{API_BASE}/invoices/{context.invoice_id}/items/{productId}", json={"quantity": int(quantity)})
    context.last_response = r
    if r.status_code == 200:
        context.last_json = r.json()


@when('I delete item {productId} from the invoice')
def step_delete_item(context, productId):
    assert hasattr(context, 'invoice_id')
    r = requests.delete(f"{API_BASE}/invoices/{context.invoice_id}/items/{productId}")
    context.last_response = r
    if r.status_code == 200:
        context.last_json = r.json()


@when('I issue the invoice')
def step_issue(context):
    assert hasattr(context, 'invoice_id')
    r = requests.post(f"{API_BASE}/invoices/{context.invoice_id}:issue")
    context.last_response = r
    if r.status_code == 200:
        context.last_json = r.json()


@when('I pay the invoice')
def step_pay(context):
    assert hasattr(context, 'invoice_id')
    r = requests.post(f"{API_BASE}/invoices/{context.invoice_id}:pay")
    context.last_response = r
    if r.status_code == 200:
        context.last_json = r.json()


@when('I cancel the invoice')
def step_cancel(context):
    assert hasattr(context, 'invoice_id')
    r = requests.post(f"{API_BASE}/invoices/{context.invoice_id}:cancel")
    context.last_response = r
    if r.status_code == 200:
        context.last_json = r.json()


@then('the API responds with a created invoice id')
def step_assert_created_id(context):
    assert context.last_response.status_code == 200
    assert hasattr(context, 'invoice_id') and context.invoice_id is not None


@then('the API responds with items_count {count:d} and amount {amount:f}')
def step_assert_items_count_amount(context, count, amount):
    assert context.last_response.status_code == 200
    data = context.last_response.json()
    assert data.get('items_count') == count
    assert abs(float(data.get('amount')) - float(amount)) < 0.0001


@then('the API responds with status "{status}"')
def step_assert_status(context, status):
    assert context.last_response.status_code == 200
    data = context.last_response.json()
    assert data.get('status') == status


@then('the API response status code is {code:d}')
def step_assert_status_code(context, code):
    assert context.last_response.status_code == code
