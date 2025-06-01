# app.py
from flask import Flask, jsonify, render_template, request, redirect
import os
from datetime import datetime
from Utility.logging_config import loggers, logger, logger_file_map
import logging
import Member
import Provider


app = Flask(__name__)
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))

loggers() 

@app.route('/getmember', methods=['GET'])
def getMember():
    result = Member.getMember()
    return jsonify({"member": result})

@app.route('/getprovider', methods=['GET'])
def getProvider():
    result = Provider.getProvider()
    return jsonify({"provider": result})


@app.route('/')
def index():
    loggers = logger_file_map  # Always returns fresh, non-mutated map
    current_levels = {
        name: logging.getLevelName(logging.getLogger(name).getEffectiveLevel())
        for name in loggers if name != 'root' and name
    }
    return render_template('index.html', loggers=loggers, now=datetime.now(), current_levels=current_levels)

@app.route('/set_level', methods=['POST'])
def set_level():
    name = request.form['logger_name']
    level_str = request.form['level']
    level = getattr(logging, level_str.upper(), logging.INFO)

    log = logger(name if name != 'root' else None)
    log.setLevel(level)
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000)
