from http import client
from flask import Flask, render_template, request, redirect
import requests, stripe, os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

app = Flask(__name__)
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
stripe.api_key = os.getenv("STRIPE_KEY")


openai_client = OpenAI(
    api_key=os.getenv("OPENAI_KEY")
)

@app.route('/')
def index():
    try:
        cars = requests.get(f"{BACKEND_URL}/cars/").json()
        return render_template('index.html', cars=cars)
    except Exception as e:
        return (f"Error fetching cars: {e}", 500 )
    
@app.route('/car/<int:car_id>')
def car_detail(car_id):
    try:
        car = requests.get(f"{BACKEND_URL}/cars/{car_id}").json()
        return render_template('car_detail.html', car=car)
    except Exception as e:
        return (f"Error fetching car details: {e}", 500 )
    
@app.route('/buy/<int:id>')
def buy_car(id):
    car = requests.get(f"{BACKEND_URL}/cars/{id}").json()

    prompt = (f"Write sales description for: {car['brand']} {car['model']},{car['colour']}, year {car['modelYear']}, {car['regNum']}")
    try:
        response = openai_client.chat.completions.create(
            model ="gpt-5.2",
            input = prompt
        )
        description = response.output_text
    except Exception:
        description = f"{car['brand']} {car['model']} - Excellent condition"
    session = stripe.checkout.Session.create(
        payment_method_types = ['card'],
        line_items =[{
            'price_data':{
                'currency': 'gbp',
                'product_data':{
                    'name': f"{car['brand']} {car['model']}",
                    'description': description,
                   
                },
                 'unit_amount': int(car['price'] * 100),
               
            },
             'quantity': 1,
        }],
        mode = 'payment',
        success_url = f"{request.url_root}success",
        cancel_url = f"{request.url_root}cancel",
    )
    return redirect(session.url, code=303)

@app.route('/success')
def success():
    return '<h1>Payment Successful!</h1><p>Thank you for your purchase.</p>'
@app.route('/cancel')
def cancel():
    return '<h1>Payment Cancelled</h1><p>Your payment was not completed.</p>'
