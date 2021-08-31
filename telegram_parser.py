import json
import re


def get_entities():
    with open("entities.json") as f:
        entities = json.load(f)
    return entities


ENTITIES = get_entities()


def detect_symbol(line):
    detected = []
    clean_str = ''.join(word for word in line if word.isalnum())
    for symbol in ENTITIES["symbol"]:
        if symbol in clean_str:
            detected.append(symbol)
            return detected
    return detected


def detect_coin(line):
    detected = []
    clean_str = ''.join(word for word in line if word.isalnum())
    splitted_line = line.split()
    for symbol in ENTITIES["currency"]:
        # if symbol in clean_str:
        #     if symbol in splitted_line:
        #         detected.append(symbol)
        #         return detected
        if symbol in clean_str:
            for word in splitted_line:
                if symbol in word:
                    detected.append(symbol)
                    return detected
    return detected


def detect_buy(line):
    if "buy" not in line.lower():
        return []
    prices_str = re.findall(r'\d+(?:\.\d+)?', line)
    prices = []
    for price in prices_str:
        if "." not in price:
            prices.append(int(price))
        else:
            prices.append(float(price))
    return prices


def detect_tp(line):
    if ("sel" in line.lower() or "take profit" in line.lower()
       or "targets" in line.lower()):
        prices_str = re.findall(r'\d+(?:\.\d+)?', line)
        prices = []
        for price in prices_str:
            if "." not in price:
                prices.append(int(price))
            else:
                prices.append(float(price))
        return prices
    return []


def detect_stop(line):
    if "stop" in line.lower() or "loss" in line.lower():
        prices_str = re.findall(r'\d+(?:\.\d+)?', line)
        prices = []
        for price in prices_str:
            if "." not in price:
                prices.append(int(price))
            else:
                prices.append(float(price))
        return prices
    return []


def get_message_entities(message):
    entities = {
        "Pairs": [],
        "Coins": [],
        "Buy_Raw": [],
        "Buy": "undetected",
        "TP": "undetected",
        "SL": "undetected"
    }

    lines = message.split("\n")

    for line in lines:
        detected_symbol = detect_symbol(line)
        if detected_symbol:
            entities["Pairs"] += detected_symbol
        detected_coin = detect_coin(line)
        if detected_coin:
            entities["Coins"] += detected_coin

    for line in lines:
        detected_buy = detect_buy(line)
        if detected_buy:
            entities["Buy_Raw"] += detected_buy
            entities["Buy"] = max(detected_buy)
            break

    for line in lines:
        detected_tp = detect_tp(line)
        if detected_tp:
            entities["TP"] = ",".join(map(str, detected_tp))
            break

    for line in lines:
        detected_stop = detect_stop(line)
        if len(detected_stop) == 1:
            entities["SL"] = str(detected_stop[0])
            break
    return entities
