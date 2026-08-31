import requests
import json
import os
from datetime import datetime

class ATPDataLoader:
    def __init__(self):
        self.data_dir = 'data'
        self.players_file = os.path.join(self.data_dir, 'atp_players.json')
        self.ensure_data_directory()
    
    def ensure_data_directory(self):
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
    
    def get_players(self):
        """Загрузка списка игроков ATP"""
        if os.path.exists(self.players_file):
            with open(self.players_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        # Загрузка с API (пример)
        # В реальности нужно использовать официальные API
        players = self.fetch_players_from_api()
        self.save_players(players)
        return players
    
    def fetch_players_from_api(self):
        """Загрузка игроков из открытых источников"""
        # Пример: использование OpenTennis API
        # В реальном приложении замените на реальный API
        try:
            response = requests.get('https://api.opentennis.com/players')
            if response.status_code == 200:
                return response.json()
        except:
            pass
        
        # Запасной вариант - тестовые данные
        return self.get_test_players()
    
    def get_test_players(self):
        """Тестовые данные игроков"""
        return [
            {
                'id': 1,
                'name': 'Новак Джокович',
                'country': 'Сербия',
                'rating': 1,
                'points': 11245,
                'surface_preference': ['hard', 'clay', 'grass'],
                'win_rate': 0.83
            },
            {
                'id': 2,
                'name': 'Карлос Алькарас',
                'country': 'Испания',
                'rating': 2,
                'points': 8855,
                'surface_preference': ['clay', 'hard'],
                'win_rate': 0.79
            },
            # Добавьте больше игроков...
        ]
    
    def save_players(self, players):
        with open(self.players_file, 'w', encoding='utf-8') as f:
            json.dump(players, f, ensure_ascii=False, indent=2)
    
    def get_player_stats(self, player_id):
        """Получение статистики игрока"""
        players = self.get_players()
        for player in players:
            if player['id'] == player_id:
                return player
        return None