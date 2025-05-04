import hashlib
import base64
import uuid
from datetime import datetime

def generate_wayforpay_payment(user_id: int):
    merchant_account = "test_merch_n1"
    merchant_domain = "https://example.com"  # або твій домен, якщо є
    secret_key = "test"  # тестовий ключ WayForPay

    order_reference = str(uuid.uuid4())
    order_date = int(datetime.now().timestamp())
    amount = "1"
    currency = "UAH"
    product_name = ["PRO версія"]
    product_price = ["1"]
    product_count = ["1"]

    signature_data = [
        merchant_account,
        merchant_domain,
        order_reference,
        str(order_date),
        amount,
        currency,
        ";".join(product_name),
        ";".join(product_count),
        ";".join(product_price)
    ]
    signature_string = ";".join(signature_data)
    hash_string = base64.b64encode(hashlib.sha1(f"{signature_string}{secret_key}".encode()).digest()).decode()

    return {
        "merchantAccount": merchant_account,
        "merchantDomainName": merchant_domain,
        "orderReference": order_reference,
        "orderDate": order_date,
        "amount": amount,
        "currency": currency,
        "productName": product_name,
        "productCount": product_count,
        "productPrice": product_price,
        "merchantSignature": hash_string,
        "returnUrl": f"https://t.me/YourBotUsername",  # або твоя WebApp адреса
        "clientFirstName": "User",
        "clientLastName": "Telegram",
        "clientEmail": "user@example.com",
        "language": "UA"
    }
