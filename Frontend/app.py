from Flask import Flask, render_template, request, redirect
import requests, stripe, openai, os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
stripe.api_key = os.getenv("STRIPE_KEY")
openai.api_key = os.getenv("OPENAI_KEY")


@app.route('/')
def index():
    try:
        cars = requests.get(f"{BACKEND_URL}/cars").json()
        return render_template('index.html', cars=cars)
    except Exception as e:
        return (f"Error fetching cars: {e}", 500 )