from flask import Flask
from parser import ParseTweets
from flask_cors import CORS
import json

app = Flask(__name__)
CORS(app)

@app.route('/')
@app.route('/findTweets/<username>')
def index(username):
    tweets = ParseTweets(username)
    print(json.dumps(tweets, ensure_ascii=False))
    return json.dumps(tweets, ensure_ascii=False)
