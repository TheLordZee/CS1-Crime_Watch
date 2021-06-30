from flask import Flask, json, render_template, request, jsonify, redirect
import requests

app = Flask(__name__)

APPLICATION_KEY = '77wclqoigysi1d'
APPLICATION_SECRET = 'L5CugPxm4eWoFspK'

URL = 'https://v2.jokeapi.dev/'

@app.route("/")
def homepage():
    """Show homepage."""
    return render_template('home.html')