"""
Paiements CinetPay pour GUELANE (Wave, Orange Money, MTN, Moov, cartes).

Structure prête à l'emploi. Pour activer, définir dans .env :
  CINETPAY_API_KEY=...        (obtenu sur ton compte marchand CinetPay)
  CINETPAY_SITE_ID=...        (obtenu après abonnement à un service)
  PROPHET_PUBLIC_URL=https://ton-domaine.com   (URL publique du backend, pour les webhooks)

Tant que ces variables ne sont pas définies, l'API renvoie une erreur claire (503)
au lieu de planter. L'activation réelle nécessite un compte marchand + un déploiement en ligne.

Flux :
  1. Le client clique "Passer à Premium" → le frontend appelle /api/payment/init
  2. Le backend initialise le paiement chez CinetPay et renvoie une URL de guichet
  3. Le client paie (Wave/Orange/carte) sur le guichet CinetPay
  4. CinetPay notifie /api/payment/webhook → on vérifie et on passe le compte en Premium
"""
import os
import json
import time
import random
import urllib.request

CINETPAY_API_KEY = os.environ.get("CINETPAY_API_KEY", "")
CINETPAY_SITE_ID = os.environ.get("CINETPAY_SITE_ID", "")
PROPHET_PUBLIC_URL = os.environ.get("PROPHET_PUBLIC_URL", "")

CINETPAY_PAYMENT_URL = "https://api-checkout.cinetpay.com/v2/payment"
CINETPAY_CHECK_URL = "https://api-checkout.cinetpay.com/v2/payment/check"

# Prix de l'abonnement Premium (en FCFA / XOF — pas de centimes)
PREMIUM_PRICE_XOF = 5000  # à ajuster selon ta stratégie


def is_configured() -> bool:
    return bool(CINETPAY_API_KEY and CINETPAY_SITE_ID and PROPHET_PUBLIC_URL)


def generate_transaction_id() -> str:
    """Identifiant unique de transaction (sans caractères spéciaux)."""
    return f"GUELANE{int(time.time())}{random.randint(1000, 9999)}"


def init_payment(email: str, nom: str = "", phone: str = "") -> dict:
    """
    Initialise un paiement Premium chez CinetPay.
    Renvoie {'payment_url': ..., 'transaction_id': ...} en cas de succès.
    """
    transaction_id = generate_transaction_id()
    payload = {
        "apikey": CINETPAY_API_KEY,
        "site_id": CINETPAY_SITE_ID,
        "transaction_id": transaction_id,
        "amount": PREMIUM_PRICE_XOF,
        "currency": "XOF",
        "description": "Abonnement GUELANE Premium",
        "customer_id": email,
        "customer_email": email,
        "customer_name": nom or email.split("@")[0],
        "customer_surname": "",
        "customer_phone_number": phone,
        "channels": "ALL",  # Wave, Orange, MTN, Moov, cartes
        "lang": "FR",
        "metadata": email,  # pour retrouver l'utilisateur au moment du webhook
        "notify_url": f"{PROPHET_PUBLIC_URL}/api/payment/webhook",
        "return_url": f"{PROPHET_PUBLIC_URL}/api/payment/return",
    }
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        CINETPAY_PAYMENT_URL, data=data,
        headers={"Content-Type": "application/json"}, method="POST"
    )
    with urllib.request.urlopen(req, timeout=20) as resp:
        result = json.loads(resp.read().decode("utf-8"))

    # CinetPay renvoie code "201" et data.payment_url en cas de succès
    if str(result.get("code")) == "201" and result.get("data", {}).get("payment_url"):
        return {
            "payment_url": result["data"]["payment_url"],
            "transaction_id": transaction_id,
        }
    raise RuntimeError(f"CinetPay: {result.get('message', 'échec initialisation')}")


def verify_payment(transaction_id: str) -> dict:
    """
    Vérifie le statut réel d'une transaction auprès de CinetPay (source de vérité).
    Renvoie {'status': 'ACCEPTED'|..., 'metadata': email, ...}.
    """
    payload = {
        "apikey": CINETPAY_API_KEY,
        "site_id": CINETPAY_SITE_ID,
        "transaction_id": transaction_id,
    }
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        CINETPAY_CHECK_URL, data=data,
        headers={"Content-Type": "application/json"}, method="POST"
    )
    with urllib.request.urlopen(req, timeout=20) as resp:
        result = json.loads(resp.read().decode("utf-8"))
    d = result.get("data", {})
    return {
        "status": d.get("status", "UNKNOWN"),
        "metadata": d.get("metadata", ""),
        "amount": d.get("amount", 0),
        "raw": result,
    }
