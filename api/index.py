from flask import Flask, render_template, request, jsonify
import json
import os
from datetime import datetime

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analysis')
def analysis():
    return render_template('analysis.html')

@app.route('/api/analyze', methods=['POST'])
def analyze():
    data = request.json
    
    # Простой анализ
    p1_win_rate = float(data.get('player1', {}).get('win_rate', 0.5))
    p2_win_rate = float(data.get('player2', {}).get('win_rate', 0.5))
    
    p1_prob = p1_win_rate / (p1_win_rate + p2_win_rate)
    p2_prob = 1 - p1_prob
    
    return jsonify({
        'player1_probability': round(p1_prob * 100, 1),
        'player2_probability': round(p2_prob * 100, 1),
        'recommended_bet': 'Победа ' + ('Игрока 1' if p1_prob > p2_prob else 'Игрока 2')
    })

# Для Vercel
app = app