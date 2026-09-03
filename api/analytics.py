from database import db
from datetime import datetime

def save_match_analysis(player1_data, player2_data, prediction):
    """Сохранение анализа матча"""
    match_data = {
        'player1': player1_data,
        'player2': player2_data,
        'predicted_winner': prediction.get('winner'),
        'prediction_confidence': prediction.get('confidence'),
        'fair_odds': prediction.get('fair_odds'),
        'value_bet': prediction.get('value_bet')
    }
    
    return db.save_match(match_data)

def get_match_history(limit=50):
    """Получение истории матчей"""
    return db.get_history(limit)

def save_match_result(match_id, actual_winner):
    """Сохранение результата матча"""
    return db.save_result(match_id, actual_winner)

def get_analytics():
    """Получение аналитики"""
    return db.get_analytics()

def get_learning_data():
    """Получение данных для самообучения"""
    return db.learn_from_mistakes()