import sqlite3


conn = sqlite3.connect('binance.db')
cursor = conn.cursor()
query = """CREATE TABLE ticker_price(
            SYMBOL CHAR(20) NOT NULL,
            PRICE FLOAT NOT NULL, 
            CREATED_AT TIMESTAMP NOT NULL
        )
        """
cursor.execute(query)
conn.commit()
conn.close()