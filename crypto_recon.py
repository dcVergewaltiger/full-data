import requests

def detect_crypto_type(address: str) -> str:
    address = address.strip()
    if address.startswith("1") or address.startswith("3") or address.startswith("bc1"):
        return "bitcoin"
    elif address.startswith("0x") and len(address) == 42:
        return "ethereum"
    elif address.startswith("T") and len(address) == 34:
        return "tron"
    elif address.startswith("L") or address.startswith("M"):
        return "litecoin"
    elif len(address) == 34 and address.startswith("D"):
        return "dogecoin"
    return "unknown"

def lookup_bitcoin(address: str) -> dict:
    result = {"Adresse": address, "Typ": "Bitcoin (BTC)"}
    try:
        r = requests.get(f"https://blockchain.info/rawaddr/{address}", timeout=8).json()
        balance_btc = r.get("final_balance", 0) / 1e8
        total_recv  = r.get("total_received", 0) / 1e8
        total_sent  = r.get("total_sent", 0) / 1e8
        n_tx        = r.get("n_tx", 0)
        result["Guthaben (BTC)"]       = f"{balance_btc:.8f} BTC"
        result["Gesamt empfangen"]     = f"{total_recv:.8f} BTC"
        result["Gesamt gesendet"]      = f"{total_sent:.8f} BTC"
        result["Anzahl Transaktionen"] = str(n_tx)
        if r.get("txs"):
            last_tx = r["txs"][0]
            result["Letzte Transaktion"] = str(last_tx.get("hash", "?"))[:40] + "..."
    except Exception as e:
        result["Fehler"] = f"API-Fehler: {e}"
    result["Blockchain Explorer"] = f"https://www.blockchain.com/btc/address/{address}"
    result["Blockchair"]          = f"https://blockchair.com/bitcoin/address/{address}"
    result["Bitref"]              = f"https://bitref.com/{address}"
    return result

def lookup_ethereum(address: str) -> dict:
    result = {"Adresse": address, "Typ": "Ethereum (ETH)"}
    try:
        r = requests.get(
            f"https://api.etherscan.io/api?module=account&action=balance&address={address}&tag=latest&apikey=YourApiKeyToken",
            timeout=8
        ).json()
        if r.get("status") == "1":
            balance_eth = int(r["result"]) / 1e18
            result["Guthaben (ETH)"] = f"{balance_eth:.6f} ETH"
        else:
            result["Guthaben"] = "Nicht abrufbar (kein API-Key)"
    except Exception as e:
        result["Fehler"] = f"API-Fehler: {e}"
    result["Etherscan"]   = f"https://etherscan.io/address/{address}"
    result["Blockchair"]  = f"https://blockchair.com/ethereum/address/{address}"
    result["Ethplorer"]   = f"https://ethplorer.io/address/{address}"
    return result

def lookup_wallet(address: str) -> dict:
    address = address.strip()
    crypto_type = detect_crypto_type(address)
    if crypto_type == "bitcoin":
        return lookup_bitcoin(address)
    elif crypto_type == "ethereum":
        return lookup_ethereum(address)
    else:
        return {
            "Adresse":          address,
            "Erkannter Typ":    crypto_type if crypto_type != "unknown" else "Unbekannt",
            "Hinweis":          "Automatische Analyse nur für BTC und ETH. Manuelle Links unten.",
            "Blockchair":       f"https://blockchair.com/search?q={address}",
            "Blockchain.com":   f"https://www.blockchain.com/explorer/search?search={address}",
            "Etherscan":        f"https://etherscan.io/search?q={address}",
        }
