import datetime
import requests
import sqlite3
import time


def get_current_time():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def get_ticker_price():
    r = requests.get("https://api.binance.com/api/v3/ticker/price")
    result = r.json()
    return result


def bulk_insert_ticker_price(ticker_price):
    current_timestamp = datetime.datetime.now()
    rows = [(el["symbol"], float(el["price"]), current_timestamp) for el in ticker_price]
    base_query = "INSERT INTO ticker_price(SYMBOL, PRICE, CREATED_AT) VALUES (?, ?, ?)"

    conn = sqlite3.connect('binance.db')
    cursor = conn.cursor()
    cursor.executemany(base_query, rows)
    conn.commit()
    conn.close()


if __name__ == "__main__":
    print(f"[{get_current_time()}] START getting ticker price from BINANCE...")
    while True:
        print(f"[{get_current_time()}] CALL BINANCE TICKER PRICE API.")

        ticker_price = []
        try:
            ticker_price = get_ticker_price()
        except Exception as e:
            print(f"[{get_current_time()}] CALL BINANCE TICKER PRICE API: FAILED")
            print(f"[{get_current_time()}] CALL BINANCE TICKER PRICE API ERROR: {e}")

        if len(ticker_price) == 0:
            print(f"[{get_current_time()}] INSERT BINANCE TICKER PRICE: SKIPPED")
        else:
            bulk_insert_ticker_price(ticker_price)
            print(f"[{get_current_time()}] INSERT BINANCE TICKER PRICE with: {len(ticker_price)} rows.")
        
        print(f"[{get_current_time()}] Data checking finished.")


        time.sleep(60 * 5)
