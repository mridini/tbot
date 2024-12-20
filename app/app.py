from flask import Flask, request, jsonify
import psycopg2
from datetime import datetime
from ib_insync import IB, Stock, MarketOrder
import asyncio

app = Flask(__name__)

async def connect_ib():
    ib = IB()
    try:
        await ib.connectAsync('99.31.78.89', 7496, clientId=1)  # clientId should be unique per connection
        print("Connected successfully!")
        return ib
    except Exception as e:
        print(f"Error connecting to Interactive Brokers: {e}")
        return None

async def place_order(symbol, order_type, quantity):
    ib = await connect_ib()

    if not ib:
        return "Connection error"

    try:
        # get the stock
        stock = Stock(symbol, 'SMART', 'USD')
        await ib.qualifyContractsAsync(stock)

        # create order
        order = MarketOrder(order_type, quantity)
        trade = ib.placeOrder(stock, order)

        # wait for confirmation
        await asyncio.sleep(2)
        order_status = trade.orderStatus.status
        ib.disconnect()

        print(f"Order placed: {order_status}")
        return order_status
    except Exception as e:
        print(f"Error placing order: {e}")
        return "Order failed"



# establish database connection
def get_db_connection():
    conn = psycopg2.connect(
        host="tvibbot_postgres", # name of postgres container
        database="tvibbot_db", 
        user="tvibbot_user",
        password="tvibbot_password"
    )
    return conn


@app.route('/')
def home():
    time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    return {
        "message": "Hello from Flask! I am currently running on a Docker Container!",
        "time": time
    }


@app.route('/webhook', methods=['POST'])
async def webhook():
    try:
        # parse req
        alert = request.json
        symbol = alert.get('symbol')
        exchange = alert.get('exchange')
        price = alert.get('price')
        quantity = alert.get('quantity')
        time = alert.get('time')
        strategy = alert.get('strategy', 'default_strategy')  # Add default
        status = alert.get('status', 'new')                  # Add default

        order_status = await place_order(symbol, 'BUY', quantity)

        # Insert the alert into the database
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO alerts (symbol, exchange, price, quantity, time, strategy, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s);
            """,
            (symbol, exchange, price, quantity, time, strategy, status)
        )
        conn.commit()
        cursor.close()
        conn.close()

        print(f"Inserted alert and order status into database: {alert}")
        return jsonify({"message": "Alert received and stored and order placed"}), 200
    except Exception as e:
        print(f"Error processing alert: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=80)
