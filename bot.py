import time
import requests
from pycoingecko import CoinGeckoAPI
from datetime import datetime, timedelta

# PORTFOLIO COMPLET
portfolio = {
    "LINK": 20, "AVAX": 10, "FET": 150, "INJ": 10,
    "RENDER": 30, "ETHFI": 100, "ONDO": 150, "NEAR": 24,
    "PENDLE": 30, "AR": 20, "POL": 12,
}

# COINGECKO IDS
ids = {
    "LINK": "chainlink", "AVAX": "avalanche-2", "FET": "fetch-ai", "INJ": "injective-protocol",
    "RENDER": "render-token", "ETHFI": "ether-fi", "ONDO": "ondo-finance", "NEAR": "near",
    "PENDLE": "pendle", "AR": "arweave", "POL": "polygon-ecosystem-token",
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
            data = cg.get_price(ids=list(ids.values()), vs_currencies='eur')
            prices = {sym: data[cid]['eur'] for sym, cid in ids.items() if cid in data}
            missing = [cid for cid in ids.values() if cid not in data]
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
    for sym, cid in ids.items():
        try:
            hist = cg.get_coin_history_by_id(id=cid, date=dt.strftime("%d-%m-%Y"))
            prices_1m[sym] = hist['market_data']['current_price']['eur']
        except:
            prices_1m[sym] = None
    return prices_1m

def format_portfolio(prices, prices_1m):
    if not prices:
        return "❌ PRIX COINGECKO NON DISPONIBLES."

    msg = "*PORTFOLIO UPDATE*\n\n"

    # PREMIER TABLEAU
    msg += "*PRIX 30 JOURS VS ACTUEL*\n\n"
    msg += "COIN | 30J AGO | Δ€ (%) | CURRENT\n"
    msg += "-----------------------------------------------------------------------\n"
    for sym in sorted(portfolio.keys()):
        price_now = prices.get(sym, 0)
        price_past = prices_1m.get(sym, 0) if prices_1m.get(sym) is not None else 0
        diff = price_now - price_past
        diff_pct = (diff / price_past * 100) if price_past != 0 else 0
        msg += f"{sym} | €{price_past:.2f} | {diff:+.2f} ({diff_pct:+.2f}%) | €{price_now:.2f}\n"
        msg += "-----------------------------------------------------------------------\n"

    msg += "\n*VALEUR ACTUELLE DU PORTFOLIO*\n\n"
    msg += "COIN | PRICE | QTY | TOTAL\n"
    msg += "-----------------------------------------------------------------------\n"
    total_portfolio = 0
    for sym in sorted(portfolio.keys()):
        price_now = prices.get(sym, 0)
        qty = portfolio[sym]
        total = price_now * qty
        total_portfolio += total
        msg += f"{sym} | €{price_now:.2f} | {qty} | €{total:.2f}\n"
        msg += "-----------------------------------------------------------------------\n"
    msg += f"*TOTAL PORTFOLIO: €{total_portfolio:.2f}*"

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
