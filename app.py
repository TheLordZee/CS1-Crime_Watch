from flask import Flask, json, render_template, request, jsonify, redirect
import requests
from linkedin import linkedin

app = Flask(__name__)

APPLICATION_KEY = '77wclqoigysi1d'
APPLICATION_SECRET = 'L5CugPxm4eWoFspK'

RETURN_URL = 'http://127.0.0.1:5000'

URL = 'https://www.linkedin.com/oauth2/v2'

@app.route("/")
def homepage():
    """Show homepage."""
    data = {
        'response_type':'code',
        'client_id': '77wclqoigysi1d',
        'redirect_url':'https://127.0.0.1/auth/linkedin/callback',
        'state': 'ATotallyRandomString'
    }

    res = requests.get(URL + '/acessToken', params=data)

    # auth = linkedin.LinkedInAuthentication(
    # APPLICATION_KEY,
    # APPLICATION_SECRET,
    # RETURN_URL,
    # linkedin.PERMISSIONS.enums.values()
    # )

    # res = auth.authorization_url

    # print(res)
    # APPLICATION_KEY = '77wclqoigysi1d'
    # APPLICATION_SECRET = 'L5CugPxm4eWoFspK'

    return redirect('/code')