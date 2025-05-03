import re
import os
from telethon import TelegramClient, events
from dotenv import load_dotenv

load_dotenv()

api_id = int(os.getenv("API_ID"))
api_hash = os.getenv("API_HASH")
source_channel = os.getenv("SOURCE_CHANNEL")
target_channel = os.getenv("TARGET_CHANNEL")

client = TelegramClient('user', api_id, api_hash)

def parse_message(text):
    if not ("Long" in text or "Short" in text):
        return None

    signal_type = "Long" if "Long" in text else "Short"
    name_match = re.search(r"Name:\s*([A-Z0-9/]+)", text)
    price_match = re.search(r"Entry price\(USDT\):\s*([\d.]+)", text)
    leverage_match = re.search(r"Margin mode:\s*Cross\s*\((\d+)X\)", text)
    targets = re.findall(r"\d+\)\s*([\d.]+)", text)

    if not name_match or not price_match or not leverage_match or not targets:
        return None

    name = name_match.group(1)
    entry_price = float(price_match.group(1))
    leverage = leverage_match.group(1)

    price_low = round(entry_price * 0.99, 5)
    price_high = round(entry_price * 1.01, 5)

    if signal_type == "Long":
        sl_price = round(entry_price * 0.95, 5)
        entry_line = f"{price_low} - {entry_price}"
        signal_text = "Regular (Long)"
    else:
        sl_price = round(entry_price * 1.05, 5)
        entry_line = f"{entry_price} - {price_high}"
        signal_text = "Regular (Short)"

    message = f"""🔥 Ege Trader
Signal Type: {signal_text}
Name: {name}
Leverage: Cross ({leverage})

↪️ Entry price(USDT): {entry_line}
SL: {sl_price}

Targets(USDT):"""
    for i, target in enumerate(targets, 1):
        message += f"\n{i}. {target}"
    message += "\n5. 🔝 unlimited\n\nExchanges: Binance Futures, Bitget Futures, ByBit USDT, KuCoin Futures, OKX Futures"

    return message

@client.on(events.NewMessage(chats=source_channel))
async def handler(event):
    text = event.raw_text
    parsed = parse_message(text)
    if parsed:
        await client.send_message(target_channel, parsed)

print("✅ Bot çalışıyor...")

client.start()
client.run_until_disconnected()
