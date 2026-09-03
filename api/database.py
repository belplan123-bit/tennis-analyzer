import json
import os
from datetime import datetime

class Database:
    def __init__(self):
        self.data_dir = 'data'
        self.history_file = os.path.join(self.data_dir, 'match_history.json')
        self.analytics_file = os.path.join(self.data_dir, 'analytics.json')
        self.ensure_directory()
    
    def ensure_directory(self):
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
        if not os.path.exists(self.history_file):
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump([], f)
        if not os.path.exists(self.analytics_file):
            with open(self.analytics_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'total_matches': 0,
                    'correct_predictions': 0,
                    'accuracy': 0,
                    'errors': [],
                    'learning_data': {}
                }, f)
    
    def save_match(self, match_data):
        """Сохранение матча в историю"""
        try:
            with open(self.history_file, 'r', encoding='utf-8') as f:
                history = json.load(f)
            
            match_data['timestamp'] = datetime.now().isoformat()
            match_data['id'] = len(history) + 1
            history.append(match_data)
            
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(history, f, ensure_ascii=False, indent=2)
            
            return True
        except Exception as e:
            print(f"Error saving match: {e}")
            return False
    
    def get_history(self, limit=50):
        """Получение истории матчей"""
        try:
            with open(self.history_file, 'r', encoding='utf-8') as f:
                history = json.load(f)
            return history[-limit:][::-1]  # Последние матчи первыми
        except:
            return []
    
    def save_result(self, match_id, actual_winner):
        """Сохранение результата матча"""
        try:
            with open(self.history_file, 'r', encoding='utf-8') as f:
                history = json.load(f)
            
            for match in history:
                if match.get('id') == match_id:
                    match['actual_winner'] = actual_winner
                    match['was_correct'] = (match.get('predicted_winner') == actual_winner)
                    break
            
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(history, f, ensure_ascii=False, indent=2)
            
            self.update_analytics()
            return True
        except Exception as e:
            print(f"Error saving result: {e}")
            return False
    
    def update_analytics(self):
        """Обновление аналитики на основе истории"""
        try:
            with open(self.history_file, 'r', encoding='utf-8') as f:
                history = json.load(f)
            
            completed_matches = [m for m in history if 'actual_winner' in m]
            correct = [m for m in completed_matches if m.get('was_correct', False)]
            
            analytics = {
                'total_matches': len(history),
                'completed_matches': len(completed_matches),
                'correct_predictions': len(correct),
                'accuracy': (len(correct) / len(completed_matches) * 100) if completed_matches else 0,
                'last_updated': datetime.now().isoformat()
            }
            
            with open(self.analytics_file, 'w', encoding='utf-8') as f:
                json.dump(analytics, f, ensure_ascii=False, indent=2)
            
            return analytics
        except Exception as e:
            print(f"Error updating analytics: {e}")
            return {}
    
    def get_analytics(self):
        """Получение аналитики"""
        try:
            with open(self.analytics_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}
    
    def learn_from_mistakes(self):
        """Самообучение на основе ошибок"""
        try:
            with open(self.history_file, 'r', encoding='utf-8') as f:
                history = json.load(f)
            
            # Анализ ошибок
            errors = []
            for match in history:
                if 'actual_winner' in match and not match.get('was_correct', False):
                    errors.append({
                        'match_id': match.get('id'),
                        'predicted': match.get('predicted_winner'),
                        'actual': match.get('actual_winner'),
                        'player1': match.get('player1', {}).get('name'),
                        'player2': match.get('player2', {}).get('name'),
                        'stats': match.get('stats', {})
                    })
            
            return errors
        except:
            return []

db = Database()