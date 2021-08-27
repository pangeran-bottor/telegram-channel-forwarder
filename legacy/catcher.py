from telethon import TelegramClient
from telethon import sync, events
from threading import Thread
import asyncio
import re
import requests
import json
import sqlite3
import time
import datetime

class Settings:
    db = sqlite3.connect('work.db', check_same_thread=False)
    cur = db.cursor()
    with open('config.txt') as config:
        lines = config.readlines()
    for var in lines:
        if re.search('API_ID', var):
            api_id = var[len('API_ID')+1:var.index('\n')]
        if re.search('API_HASH', var):
            api_hash = var[len('API_HASH')+1:var.index('\n')]
        if re.search('SESSION', var):
            session = var[len('SESSION')+1:var.index('\n')]
        if re.search('IGNORE', var):
            ignore = var[len('IGNORE')+1:var.index('\n')].split(';')
            for ignr in ignore:
                switch = ignore.index(ignr)
                ignr = ignr.split('-')
                ignore[switch] = ignr
        if re.search('CHANNEL_ID', var):
            channels = var[len('CHANNEL_ID')+1:var.index('\n')].split(';')
        if re.search('EXCHANGE', var):
            exchange = var[len('EXCHANGE')+1:var.index('\n')].split(';')
        if re.search('BUY', var):
            buy = var[len('BUY')+1:var.index('\n')].split(';')
        if re.search('TARGET', var):
            target = var[len('TARGET')+1:var.index('\n')].split(';')
        if re.search('SEC_REFRESH', var):
            sec_refresh = var[len('SEC_REFRESH')+1:var.index('\n')]
        if re.search('STOP_PRC', var):
            stop_prc = var[len('STOP_PRC')+1:var.index('%')]
        if re.search('PROFIT_DROP_PRC', var):
            profit_drop_prc = var[len('PROFIT_DROP_PRC')+1:var.index('%')]
        if re.search('PROFIT_TOP_PRC', var):
            profit_top_prc = var[len('PROFIT_TOP_PRC')+1:var.index('%')]
    client = TelegramClient(session, api_id, api_hash)
    not_alphabet = r'[^a-zA-Z]'
    not_numbers = r'[^0-9]'

def ignore_list(msg):
    try:
        for ignr1 in Settings.ignore:
            for ignr2 in ignr1:
                if re.search(ignr2.lower(), msg.lower()):
                    return 0
    except:
        for ignr2 in ignore:
            if re.search(ignr2.lower(), msg.lower()):
                return 0
    return msg
def main_catcher():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    @Settings.client.on(events.NewMessage())
    def new_message_handler(event):
        for ch in Settings.channels:
            if re.search(str(event.message.to_id.channel_id), ch):
                msg = ignore_list(event.message.message)
                ms = msg.lower()
                ms = str(ms).split('\n')
                msg = str(msg).split('\n')
        if msg[0] != 0:
            msg_date = event.message.date
            msg_date = str(msg_date).replace('-', '')
            msg_date = str(msg_date).replace(' ', '')
            msg_date = str(msg_date).replace(':', '')
            msg_date = str(msg_date).replace('+', '')
            msg_date = msg_date[:-4]

            for ex in Settings.exchange:
                for row in ms:
                    if re.search(ex, row):
                        exchange_var = ex

            for b in Settings.buy:
                for row in ms:
                    if re.search(b, row):
                        check = re.search(r'[0-9]', row)
                        if check:
                            ind = check.start()
                            buy_cost = row[ind:]
                            try:
                                num1 = buy_cost[buy_cost.index('-')+1:]
                                num2 = buy_cost[:buy_cost.index('-')]
                                if int(num1) > int(num2):
                                    buy_cost = num1
                                else:
                                    buy_cost = num2
                            except:
                                buy_cost = buy_cost[buy_cost.index(' '):]
                            break

            for row in msg:
                if re.search('#', row):
                    try:
                        pair = row[row.index('#')+1:row.index(' (')]
                        opt = ''
                        for c in pair:
                            if re.match(r'[A-Z]', c):
                                opt+=c
                        if len(opt) < 5:
                            opt += 'BTC'
                    except:
                        pass

            for tar in Settings.target:
                for row in ms:
                    if re.search(tar, row):
                        index = re.search(r'\d', row)
                        if index is not None:
                            index = index.start()
                        target_var = row[index:]
                        target_var = target_var[:target_var.index('-')]

            try:
                a=exchange_var
            except:
                exchange_var = 'NONE'
            try:
                a=buy_cost
            except:
                buy_cost = 'NONE'
            try:
                a=opt
            except:
                opt = 'NONE'
            try:
                a=target_var
            except:
                target_var = 'NONE'

            if not re.search(Settings.not_alphabet, exchange_var) or not re.search(Settings.not_alphabet, opt) or not re.search(Settings.not_numbers, buy_cost) or not re.search(Settings.not_numbers, target_var):
                if exchange_var != 'NONE' and opt != 'NONE' and buy_cost != 'NONE' and target_var != 'NONE':
                    json_cost = json.loads(requests.get(f'https://api.binance.com/api/v3/avgPrice?symbol={opt}').text)['price']
                    json_cost = json_cost.replace('.', '')
                    while json_cost[0] == '0':
                        json_cost = json_cost[1:]

                    if len(json_cost) > len(buy_cost) and len(json_cost) > len(target_var):
                        buy_cost = int(buy_cost)*(10**(len(json_cost)-len(buy_cost)))
                        target_var = int(target_var)*(10**(len(json_cost)-len(target_var)))

                    Settings.cur.execute('SELECT pair, target FROM Caught')
                    check = Settings.cur.fetchall()
                    ch = 0
                    for c in check:
                        if c[0] == opt and c[1] == target_var:
                            ch = 1
                        else:
                            pass
                    if ch == 0:
                        signal = f'Signal: {msg_date},{exchange_var},{opt},{buy_cost},{target_var}'

                        tc = str(time.time())
                        tc = tc[:tc.index('.')]

                        Settings.cur.execute('SELECT pair, closed FROM Caught')
                        pair_check = Settings.cur.fetchall()

                        if len(pair_check) != 0:
                            a=0
                            for p in pair_check:
                                if p[0] == opt and p[1] == '-':
                                    Settings.cur.execute(f'UPDATE Caught SET target="{target_var}" WHERE pair="{opt}" AND closed ="-"')
                                    Settings.cur.execute(f'UPDATE Caught SET time="{int(tc)}" WHERE pair="{opt}" AND closed ="-"')
                                    Settings.cur.execute(f'UPDATE Caught SET buy="{buy_cost}" WHERE pair="{opt}" AND closed ="-"')
                                    Settings.cur.execute(f'UPDATE Caught SET bought="-" WHERE pair="{opt}" AND closed ="-"')
                                    Settings.cur.execute(f'UPDATE Caught SET min="{json_cost}" WHERE pair="{opt}" AND closed ="-"')
                                    Settings.cur.execute(f'UPDATE Caught SET max="{json_cost}" WHERE pair="{opt}" AND closed ="-"')
                                    Settings.cur.execute(f'UPDATE Caught SET closed="-" WHERE pair="{opt}" AND closed ="-"')
                                    Settings.db.commit()
                                    a=1
                            if a == 0:
                                Settings.cur.execute(f'INSERT INTO Caught VALUES ("{opt}", "{buy_cost}", "{target_var}", "{int(tc)}", "-", "{json_cost}", "{json_cost}", "-", "{int(tc)}")')
                                Settings.db.commit()
                                print(signal)
                        else:
                            Settings.cur.execute(f'INSERT INTO Caught VALUES ("{opt}", "{buy_cost}", "{target_var}", "{int(tc)}", "-", "{json_cost}", "{json_cost}", "-", "{int(tc)}")')
                            Settings.db.commit()
                            print(signal)
                        if int(json_cost) <= int(buy_cost):
                            Settings.cur.execute(f'UPDATE Caught SET bought="{json_cost}" WHERE pair="{opt}" AND closed ="-"')
                            Settings.db.commit()
                            print(f'BUY: {opt}/{json_cost}')
                else:
                    print(f'Bad signal: {msg_date},{exchange_var},{opt},{buy_cost},{target_var}')
            else:
                print(f'Bad signal: {msg_date},{exchange_var},{opt},{buy_cost},{target_var}')

    Settings.client.start()
    Settings.client.run_until_disconnected()

def time_count():
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        while True:
            Settings.cur.execute(f'SELECT pair FROM Caught')
            pair_check = Settings.cur.fetchall()
            if len(pair_check) != 0:
                for p in pair_check:
                    pair = p[0]
                    json_array = json.loads(requests.get(f'https://api.binance.com/api/v3/ticker/price').text)
                    for j in json_array:
                        if j['symbol'] == pair:
                            json_cost = j['price']
                            json_cost = json_cost.replace('.', '')
                            while json_cost[0] == '0':
                                json_cost = json_cost[1:]
                            Settings.cur.execute(f'SELECT buy, bought, min, max, closed, target FROM Caught WHERE pair="{pair}"')
                            answer = Settings.cur.fetchall()
                            for a in answer:
                                buy_var = a[0]#+
                                bought_var = a[1]#+
                                min_var = a[2]#+
                                max_var = a[3]#+
                                closed_var = a[4]#+
                                target_var = a[5]#+
                                tc = str(time.time())
                                tc = tc[:tc.index('.')]
                                if closed_var == '-':
                                    if bought_var == '-':
                                        if int(json_cost) <= int(buy_var):
                                            Settings.cur.execute(f'UPDATE Caught SET bought="{json_cost}" WHERE pair="{pair}"')
                                            Settings.db.commit()
                                            print(f'BUY: {pair}/{json_cost}')
                                        else:
                                            Settings.cur.execute(f'SELECT open_time FROM Caught WHERE pair="{pair}"')
                                            open_time = Settings.cur.fetchone()[-1]
                                            delta = int(tc)-int(open_time)
                                            days = (delta) // 86400
                                            hours = ((delta)-86400*days) // 3600
                                            minutes = ((delta)-86400*days-3600*hours) // 60
                                            seconds = ((delta)-86400*days-3600*hours-60*minutes)
                                            print(f'WAITING: {pair},{json_cost},{days} days {hours} hours {minutes} minutes {seconds} seconds ')

                                            if int(json_cost) > int(max_var):
                                                Settings.cur.execute(f'UPDATE Caught SET max="{json_cost}" WHERE pair="{pair}"')
                                                Settings.db.commit()
                                            if int(json_cost) < int(min_var):
                                                Settings.cur.execute(f'UPDATE Caught SET min="{json_cost}" WHERE pair="{pair}"')
                                                Settings.db.commit()
                                    else:
                                        Settings.cur.execute(f'SELECT open_time FROM Caught WHERE pair="{pair}"')
                                        open_time = Settings.cur.fetchone()[-1]
                                        delta = int(tc)-int(open_time)
                                        days = (delta) // 86400
                                        hours = ((delta)-86400*days) // 3600
                                        minutes = ((delta)-86400*days-3600*hours) // 60
                                        seconds = ((delta)-86400*days-3600*hours-60*minutes)
                                        if int(json_cost) > int(max_var):
                                            Settings.cur.execute(f'UPDATE Caught SET max="{json_cost}" WHERE pair="{pair}"')
                                            Settings.db.commit()
                                            max_var = json_cost
                                        if int(json_cost) < int(min_var):
                                            Settings.cur.execute(f'UPDATE Caught SET min="{json_cost}" WHERE pair="{pair}"')
                                            Settings.db.commit()
                                            min_var = json_cost
                                        if float(json_cost) <= float(bought_var)*(1-float(Settings.stop_prc)/100):
                                            Settings.cur.execute(f'UPDATE Caught SET closed="{json_cost}" WHERE pair="{pair}"')
                                            Settings.db.commit()
                                            res_prc = (1-(float(json_cost) / float(bought_var)))*100
                                            print(f'RESULT: {pair}/-{res_prc}%')
                                        if float(max_var) >= float(target_var)*(1+float(Settings.profit_top_prc)/100) and float(json_cost) <= float(max_var)*(1-float(Settings.profit_drop_prc)/100) and float(json_cost)-float(bought_var) >= 0:
                                            Settings.cur.execute(f'UPDATE Caught SET closed="{json_cost}" WHERE pair="{pair}"')
                                            Settings.db.commit()
                                            res_prc = (1-(float(bought_var) / float(json_cost)))*100
                                            print(f'RESULT: {pair}/+{res_prc}%')
                                        print(f'BOUGHT: {pair},{json_cost},[{min_var}|{max_var}]')
                time.sleep(int(Settings.sec_refresh))
    except:
        time.sleep(10)
th_1, th_2 = Thread(target=main_catcher), Thread(target=time_count)
th_1.start(), th_2.start()
th_1.join(), th_2.join()
