from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import json
import os
from datetime import datetime
import requests
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
from modules.atp_data import ATPDataLoader
from modules.analyzer import TennisAnalyzer
from modules.bookmaker import BookmakerComparison

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tennis_betting.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Инициализация модулей
atp_loader = ATPDataLoader()
analyzer = TennisAnalyzer()
bookmaker_comparison = BookmakerComparison()

# Модели базы данных
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    betting_history = db.relationship('BetHistory', backref='user', lazy=True)

class BetHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    match_name = db.Column(db.String(200), nullable=False)
    bet_type = db.Column(db.String(50), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    odds = db.Column(db.Float, nullable=False)
    result = db.Column(db.String(20), nullable=True)
    profit_loss = db.Column(db.Float, nullable=True)
    date = db.Column(db.DateTime, default=datetime.utcnow)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Маршруты
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analysis', methods=['GET', 'POST'])
def analysis():
    if request.method == 'POST':
        data = request.json
        player1_data = data.get('player1')
        player2_data = data.get('player2')
        
        # Анализ матча
        analysis_result = analyzer.analyze_match(player1_data, player2_data)
        
        return jsonify(analysis_result)
    
    return render_template('analysis.html')

@app.route('/history')
@login_required
def history():
    user_history = BetHistory.query.filter_by(user_id=current_user.id).all()
    return render_template('history.html', history=user_history)

@app.route('/comparison')
def comparison():
    return render_template('comparison.html')

@app.route('/api/atp/players')
def get_atp_players():
    players = atp_loader.get_players()
    return jsonify(players)

@app.route('/api/bookmaker/compare', methods=['POST'])
def compare_with_bookmaker():
    data = request.json
    match_id = data.get('match_id')
    comparison_data = bookmaker_comparison.compare_odds(match_id)
    return jsonify(comparison_data)

@app.route('/api/analyze/url', methods=['POST'])
def analyze_from_url():
    data = request.json
    url = data.get('url')
    
    # Парсинг данных из URL
    match_data = analyzer.parse_match_from_url(url)
    
    if match_data:
        return jsonify({'success': True, 'data': match_data})
    else:
        return jsonify({'success': False, 'error': 'Не удалось получить данные'})

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    # Для локального запуска
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))