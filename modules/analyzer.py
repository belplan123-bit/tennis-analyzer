import numpy as np
import pandas as pd
from datetime import datetime
import json
import os
import requests
from bs4 import BeautifulSoup

class TennisAnalyzer:
    def __init__(self):
        self.history_file = 'data/betting_history.json'
        self.ensure_data_directory()
    
    def ensure_data_directory(self):
        if not os.path.exists('data'):
            os.makedirs('data')
        if not os.path.exists(self.history_file):
            with open(self.history_file, 'w') as f:
                json.dump([], f)
    
    def analyze_match(self, player1_data, player2_data):
        """
        Анализ матча на основе данных игроков
        
        Параметры:
        player1_data = {
            'name': str,
            'rating': int,
            'win_rate': float,
            'surface_win_rate': float,
            'head_to_head_wins': int,
            'recent_form': float,
            'injury_status': str,
            'fatigue_level': float
        }
        """
        
        # Расчет силы игроков
        p1_strength = self.calculate_player_strength(player1_data)
        p2_strength = self.calculate_player_strength(player2_data)
        
        # Расчет вероятностей
        p1_win_probability = p1_strength / (p1_strength + p2_strength)
        p2_win_probability = 1 - p1_win_probability
        
        # Расчет справедливых коэффициентов
        p1_fair_odds = 1 / p1_win_probability
        p2_fair_odds = 1 / p2_win_probability
        
        # Прогнозы на разные рынки
        predictions = {
            'match_winner': {
                'player1': p1_win_probability,
                'player2': p2_win_probability,
                'fair_odds': {
                    'player1': round(p1_fair_odds, 2),
                    'player2': round(p2_fair_odds, 2)
                }
            },
            'sets': self.predict_sets(player1_data, player2_data),
            'games': self.predict_games(player1_data, player2_data),
            'handicap': self.predict_handicap(player1_data, player2_data),
            'total_games': self.predict_total_games(player1_data, player2_data)
        }
        
        # Сохранение в историю
        self.save_analysis(player1_data, player2_data, predictions)
        
        return predictions
    
    def calculate_player_strength(self, player_data):
        """Расчет силы игрока"""
        strength = 0
        
        # Рейтинг (вес 30%)
        rating_score = (2000 - player_data.get('rating', 1000)) / 1000
        strength += rating_score * 0.3
        
        # Процент побед (вес 25%)
        strength += player_data.get('win_rate', 0.5) * 0.25
        
        # Победы на покрытии (вес 20%)
        strength += player_data.get('surface_win_rate', 0.5) * 0.20
        
        # Текущая форма (вес 15%)
        strength += player_data.get('recent_form', 0.5) * 0.15
        
        # Личные встречи (вес 10%)
        h2h_score = min(player_data.get('head_to_head_wins', 0) / 10, 1)
        strength += h2h_score * 0.10
        
        # Штрафы за травмы и усталость
        if player_data.get('injury_status') == 'injured':
            strength *= 0.7
        elif player_data.get('injury_status') == 'questionable':
            strength *= 0.85
        
        strength *= (1 - player_data.get('fatigue_level', 0) * 0.1)
        
        return max(strength, 0.01)
    
    def predict_sets(self, p1_data, p2_data):
        """Прогноз на счет по сетам"""
        p1_prob = self.calculate_player_strength(p1_data)
        p2_prob = self.calculate_player_strength(p2_data)
        
        # Вероятности различных счетов
        sets_predictions = {
            '3_0': p1_prob * 0.3,
            '3_1': p1_prob * 0.25,
            '3_2': p1_prob * 0.15,
            '0_3': p2_prob * 0.3,
            '1_3': p2_prob * 0.25,
            '2_3': p2_prob * 0.15
        }
        
        # Нормализация
        total = sum(sets_predictions.values())
        for key in sets_predictions:
            sets_predictions[key] = round(sets_predictions[key] / total, 3)
        
        return sets_predictions
    
    def predict_games(self, p1_data, p2_data):
        """Прогноз на количество геймов"""
        p1_prob = self.calculate_player_strength(p1_data)
        p2_prob = self.calculate_player_strength(p2_data)
        
        avg_games = 22  # Среднее количество геймов в матче
        p1_games = avg_games * (p1_prob / (p1_prob + p2_prob))
        p2_games = avg_games * (p2_prob / (p1_prob + p2_prob))
        
        return {
            'player1_games': round(p1_games, 1),
            'player2_games': round(p2_games, 1),
            'total_games': round(p1_games + p2_games, 1),
            'over_22.5_probability': self.calculate_over_probability(p1_games + p2_games, 22.5),
            'under_22.5_probability': self.calculate_under_probability(p1_games + p2_games, 22.5)
        }
    
    def predict_handicap(self, p1_data, p2_data):
        """Прогноз на фору"""
        p1_prob = self.calculate_player_strength(p1_data)
        p2_prob = self.calculate_player_strength(p2_data)
        
        handicap = (p1_prob - p2_prob) * 6  # Примерное значение форы
        
        return {
            'recommended_handicap': round(handicap, 1),
            'player1_handicap_probability': 1 / (1 + np.exp(-handicap)),
            'player2_handicap_probability': 1 / (1 + np.exp(handicap))
        }
    
    def predict_total_games(self, p1_data, p2_data):
        """Прогноз на тотал геймов"""
        games_prediction = self.predict_games(p1_data, p2_data)
        total = games_prediction['total_games']
        
        return {
            'expected_total': total,
            'over_probability': self.calculate_over_probability(total, 22.5),
            'under_probability': self.calculate_under_probability(total, 22.5),
            'recommended_total': 22.5 if abs(total - 22.5) < abs(total - 23.5) else 23.5
        }
    
    def calculate_over_probability(self, value, threshold):
        """Расчет вероятности тотала больше"""
        sigma = 3  # Стандартное отклонение
        return 1 / (1 + np.exp(-(value - threshold) / sigma))
    
    def calculate_under_probability(self, value, threshold):
        """Расчет вероятности тотала меньше"""
        return 1 - self.calculate_over_probability(value, threshold)
    
    def parse_match_from_url(self, url):
        """Парсинг данных матча из URL"""
        try:
            response = requests.get(url, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            })
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Здесь нужно добавить парсинг конкретного сайта
                # Это пример, который нужно адаптировать под конкретный источник
                
                match_data = {
                    'player1': self.extract_player_data(soup, 1),
                    'player2': self.extract_player_data(soup, 2),
                    'tournament': self.extract_tournament(soup),
                    'surface': self.extract_surface(soup)
                }
                
                return match_data
            else:
                return None
        except Exception as e:
            print(f"Error parsing URL: {e}")
            return None
    
    def extract_player_data(self, soup, player_number):
        """Извлечение данных игрока из HTML"""
        # Пример, который нужно адаптировать
        return {
            'name': 'Игрок',
            'rating': 100,
            'win_rate': 0.6,
            'surface_win_rate': 0.55,
            'head_to_head_wins': 2,
            'recent_form': 0.7,
            'injury_status': 'healthy',
            'fatigue_level': 0.2
        }
    
    def extract_tournament(self, soup):
        """Извлечение информации о турнире"""
        return 'Турнир'
    
    def extract_surface(self, soup):
        """Извлечение типа покрытия"""
        return 'hard'
    
    def save_analysis(self, p1_data, p2_data, predictions):
        """Сохранение анализа в историю"""
        try:
            with open(self.history_file, 'r', encoding='utf-8') as f:
                history = json.load(f)
            
            analysis_record = {
                'date': datetime.now().isoformat(),
                'player1': p1_data,
                'player2': p2_data,
                'predictions': predictions
            }
            
            history.append(analysis_record)
            
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(history, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            print(f"Error saving analysis: {e}")