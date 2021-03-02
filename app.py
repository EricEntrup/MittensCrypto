import os
import json
import time
import random
import numpy as np
import pandas as pd
from datetime import datetime
from flask import Flask, Markup, render_template, Response
import robin_stocks as rs
from dotenv import load_dotenv
load_dotenv()
logged_in = rs.login(
    os.getenv("ROBINHOOD_USER"), 
    os.getenv("ROBINHODD_PASS")
    )
app = Flask(__name__)

samples = pd.DataFrame()


def crypto_quote(ticker):
    quote = rs.crypto.get_crypto_quote(ticker)
    data = {
        'timestamp':  datetime.now(),
        'ask_price':  float(quote['ask_price']),
        'bid_price':  float(quote['bid_price']),
        'mark_price': float(quote['mark_price']),
        'high_price': float(quote['high_price']),
        'low_price':  float(quote['low_price']),
        'open_price': float(quote['open_price']),
        'volume':     float(quote['volume']),
        'spread':     float(quote['bid_price']) - float(quote['ask_price'])
    }

    return data



@app.route('/chart-data')
def chart_data():
    def get_quote():
        global samples
        while True:
            quote = crypto_quote("DOGE")
            samples = samples.append(quote, ignore_index=True)

            json_data = json.dumps({
                'ask_price': samples['ask_price'].iloc[-1],
                'average': np.mean(samples['ask_price'].iloc[-40:])
            })

            yield f"data:{json_data}\n\n"
            time.sleep(1)

    return Response(get_quote(), mimetype='text/event-stream')



@app.route('/chart-data2')
def chart_data2():
    def get_quote():
        global samples
        i=0
        while True:
            time.sleep(1)
            if i%5==0:
                if samples.empty:
                    continue
                idx = samples.index[-1]
                print(idx)

                json_data = json.dumps({
                    'ask_price': samples.loc[idx, 'ask_price'],
                    'average': np.mean(samples.loc[idx-60:idx, 'ask_price'])
                })

                yield f"data:{json_data}\n\n"
            i+=1

    return Response(get_quote(), mimetype='text/event-stream')


@app.route('/')
def index():
    return render_template('index.html')



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)