import time
import requests
from pycoingecko import CoinGeckoAPI
from datetime import datetime, timedelta

# PORTFOLIO COMPLET AVEC IDS
coins = {
    "ACA": {"id": "acala", "quantity": 1.0},
    "AR": {"id": "arweave", "quantity": 1.0},
    "AVAX": {"id": "avalanche-2", "quantity": 0.0},
    "BAND": {"id": "band-protocol", "quantity": 1.0},
    "CTK": {"id": "certik", "quantity": 1.0},
    "ETHFI": {"id": "ether-fi", "quantity": 0.0},
    "FET": {"id": "fetch-ai", "quantity": 1.0},
    "INJ": {"id": "injective-protocol", "quantity": 1.0},
    "NEAR": {"id": "near", "quantity": 0.0},
    "OCEAN": {"id": "ocean-protocol", "quantity": 0.0},
    "ONDO": {"id": "ondo-finance", "quantity": 1.0},
    "PENDLE": {"id": "pendle", "quantity": 1.0},
    "POL": {"id": "polygon-ecosystem-token", "quantity": 0.0},
    "RENDER": {"id": "render-token", "quantity": 1.0},
    "TIA": {"id": "celestia", "quantity": 1.0},
    "LINK": {"id": "chainlink", "quantity": 0.0},
    "XLM": {"id": "stellar", "quantity": 1.0},
    "SONIC": {"id": "sonic-3", "quantity": 1.0},
    "ONE": {"id": "harmony", "quantity": 0.0},
    "VET": {"id": "vechain", "quantity": 1.0},
}

# ⚠️ TOKEN ET CHAT_ID CODÉS EN DUR
TELEGRAM_TOKEN = "8403427353:AAFeW9hb3ixyLLYSm-a7aYhDOI8uyRfJCOE"
TELEGRAM_CHAT_ID = "7116219655"

print("⚙️ VARIABLES TELEGRAM CHARGÉES :")
print("TELEGRAM_TOKEN =", "✅" if TELEGRAM_TOKEN else "❌ MANQUANT")
print("CHAT_ID =", TELEGRAM_CHAT_ID if TELEGRAM_CHAT_ID else "❌ MANQUANT")

def send_telegram_message(message: str):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "Markdown"}
    try:
        r = requests.post(url, data=payload, timeout=10)
        print("🟢 TELEGRAM RESPONSE:", r.text)
        if r.status_code != 200:
            print("❌ TELEGRAM HTTP ERROR:", r.status_code)
    except Exception as e:
        print("❌ ERREUR TELEGRAM:", e)

def fetch_prices():
    cg = CoinGeckoAPI()
    for attempt in range(3):
        try:
            print("🟢 RÉCUPÉRATION DES PRIX COINGECKO...")
            data = cg.get_price(ids=[c['id'] for c in coins.values()], vs_currencies='eur')
            prices = {sym: data[c['id']]['eur'] for sym, c in coins.items() if c['id'] in data}
            missing = [c['id'] for c in coins.values() if c['id'] not in data]
            if missing:
                print("⚠️ COINS MANQUANTS:", missing)
            print("🟢 PRIX RÉCUPÉRÉS:", prices)
            return prices
        except Exception as e:
            print(f"⚠️ ERREUR COINGECKO (TENTATIVE {attempt+1}/3):", e)
            time.sleep(5)
    return {}

def fetch_prices_1m_ago():
    cg = CoinGeckoAPI()
    dt = datetime.utcnow() - timedelta(days=30)
    prices_1m = {}
    for sym, c in coins.items():
        try:
            hist = cg.get_coin_history_by_id(id=c['id'], date=dt.strftime("%d-%m-%Y"))
            prices_1m[sym] = hist['market_data']['current_price']['eur']
        except:
            prices_1m[sym] = None
    return prices_1m

def format_portfolio(prices, prices_1m):
    if not prices:
        return "❌ PRIX COINGECKO NON DISPONIBLES."

    msg = "*PORTFOLIO UPDATE*\n\n"
    msg += "*PRIX 30 JOURS VS ACTUEL*\n\n"
    msg += "COIN | 30J AGO | CURRENT | Δ (%)\n"
    msg += "-----------------------------------------------------------------------\n"

    total_past = 0
    total_now = 0

    for sym in sorted(coins.keys()):
        if coins[sym]["quantity"] == 0:  # ⬅️ NE PAS AFFICHER SI QUANTITÉ = 0
            continue
        price_now = prices.get(sym, 0)
        price_past = prices_1m.get(sym, 0) if prices_1m.get(sym) is not None else 0
        diff_pct = ( (price_now - price_past) / price_past * 100 ) if price_past != 0 else 0

        total_past += price_past
        total_now += price_now

        msg += f"{sym} | €{price_past:.2f} | €{price_now:.2f} | {diff_pct:+.2f}%\n"
        msg += "-----------------------------------------------------------------------\n"

    total_diff_pct = ( (total_now - total_past) / total_past * 100 ) if total_past != 0 else 0
    msg += f"TOTAL | €{total_past:.2f} | €{total_now:.2f} | {total_diff_pct:+.2f}%\n"
    msg += "-----------------------------------------------------------------------\n"

    return msg

def main():
    while True:
        try:
            prices = fetch_prices()
            prices_1m = fetch_prices_1m_ago()
            msg = format_portfolio(prices, prices_1m)
            print("🟢 MESSAGE FORMATÉ:", msg)
            send_telegram_message(msg)
            print("🟢 MESSAGE ENVOYÉ")
        except Exception as e:
            print("❌ ERREUR MAIN LOOP:", e)
        print("⏱ ATTENTE 10 MINUTES...")
        time.sleep(600)

if __name__ == "__main__":
    main()
