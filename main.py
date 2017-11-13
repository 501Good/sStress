# -*- coding: utf-8 -*-

DEFAULT_PORT = 5000
ADDITIVE_FOR_UID = 1000

try:
    from os import getuid

except ImportError:
    def getuid():
        return DEFAULT_PORT - ADDITIVE_FOR_UID

import requests
from flask import Flask, render_template, request, jsonify

import sys
import os
sys.path.append(os.path.abspath("./lstm"))
from text_accentAPI import AccentLSTM

app = Flask(__name__)
accent = AccentLSTM()
accent.initialize()

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/predict/', methods=['GET', 'POST'])
def predict():
    text = request.get_data().decode('utf-8')
    text = text.replace("'", "")
    print(text)
    accented_text = accent.put_stress(text)
    return accented_text


if __name__ == '__main__':
    app.run(port=getuid() + ADDITIVE_FOR_UID, debug=True)
