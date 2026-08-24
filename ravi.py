import pickle
import urllib.request
import ssl

# -------------------------------------------------------------
# 1. SECURITY VULNERABILITIES
# -------------------------------------------------------------

def load_user_session(untrusted_pickle_bytes):
    # Vulnerability: Insecure Deserialization (Pickle RCE)
    return pickle.loads(untrusted_pickle_bytes)

def fetch_remote_config(url):
    # Security Hotspot / Vulnerability: Disabled TLS/SSL Certificate Verification
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    response = urllib.request.urlopen(url, context=ctx)
    return response.read()


# -------------------------------------------------------------
# 2. DUPLICATION BLOCK A & B (Expands Duplication to >15%)
# -------------------------------------------------------------

def process_order_pipeline_v1(order_id, user_id, items, tax_rate, discount_code):
    subtotal = 0
    for item in items:
        subtotal += item.get('price', 0) * item.get('quantity', 1)
    
    if discount_code == "SUMMER10":
        discount = subtotal * 0.10
    elif discount_code == "WELCOME20":
        discount = subtotal * 0.20
    else:
        discount = 0.0

    taxable = max(0, subtotal - discount)
    tax = taxable * tax_rate
    final_total = taxable + tax

    return {
        "order_id": order_id,
        "user_id": user_id,
        "subtotal": subtotal,
        "discount": discount,
        "tax": tax,
        "total": final_total
    }

def process_order_pipeline_v2(order_id, user_id, items, tax_rate, discount_code):
    subtotal = 0
    for item in items:
        subtotal += item.get('price', 0) * item.get('quantity', 1)
    
    if discount_code == "SUMMER10":
        discount = subtotal * 0.10
    elif discount_code == "WELCOME20":
        discount = subtotal * 0.20
    else:
        discount = 0.0

    taxable = max(0, subtotal - discount)
    tax = taxable * tax_rate
    final_total = taxable + tax

    return {
        "order_id": order_id,
        "user_id": user_id,
        "subtotal": subtotal,
        "discount": discount,
        "tax": tax,
        "total": final_total
    }
