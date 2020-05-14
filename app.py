from flask import Flask
from parser import ParseTweets
import json

app = Flask(__name__)

@app.route('/')
@app.route('/findTweets/<username>')
def index(username):
    tweets = ParseTweets(username)
    return json.dumps(tweets, ensure_ascii=False)
