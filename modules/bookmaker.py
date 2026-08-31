import requests
import json
from datetime import datetime

class BookmakerComparison:
    def __init__(self):
        self.bookmakers = [
            'Лига Ставок',
            'Фонбет',
            'Winline',
            '1xBet',
            'Пари'
        ]
    
    def compare_odds(self, match_id):
        """
        Сравнение коэффициентов с букмекерами
        """
        comparison_data = {
            'match_id': match_id,
            'bookmakers': {}
        }
        
        for bookmaker in self.bookmakers:
            odds = self.get_bookmaker_odds(bookmaker, match_id)
            comparison_data['bookmakers'][bookmaker] = odds
        
        # Находим лучшие коэффициенты
        best_odds = self.find_best_odds(comparison_data['bookmakers'])
        comparison_data['best_odds'] = best_odds
        
        # Расчет маржи
        comparison_data['margins'] = self.calculate_margins(comparison_data['bookmakers'])
        
        return comparison_data
    
    def get_bookmaker_odds(self, bookmaker, match_id):
        """
        Получение коэффициентов от букмекера
        В реальном приложении нужно использовать API букмекеров
        """
        # Пример структуры данных
        return {
            'player1_win': 1.85,
            'player2_win': 1.95,
            'total_over_22.5': 1.90,
            'total_under_22.5': 1.90,
            'handicap_p1_minus_3.5': 1.85,
            'handicap_p2_plus_3.5': 1.95
        }
    
    def find_best_odds(self, all_odds):
        """
        Поиск лучших коэффициентов среди букмекеров
        """
        best_odds = {}
        
        for market in all_odds[list(all_odds.keys())[0]].keys():
            best_value = 0
            best_bookmaker = ''
            
            for bookmaker, odds in all_odds.items():
                if odds.get(market, 0) > best_value:
                    best_value = odds[market]
                    best_bookmaker = bookmaker
            
            best_odds[market] = {
                'value': best_value,
                'bookmaker': best_bookmaker
            }
        
        return best_odds
    
    def calculate_margins(self, all_odds):
        """
        Расчет маржи букмекеров
        """
        margins = {}
        
        for bookmaker, odds in all_odds.items():
            if 'player1_win' in odds and 'player2_win' in odds:
                margin = (1/odds['player1_win'] + 1/odds['player2_win'] - 1) * 100
                margins[bookmaker] = round(margin, 2)
        
        return margins
    
    def find_value_bets(self, our_odds, bookmaker_odds):
        """
        Поиск value bets (ставок с перевесом)
        """
        value_bets = []
        
        for market, our_odd in our_odds.items():
            if market in bookmaker_odds:
                bookmaker_odd = bookmaker_odds[market]['value']
                
                # Если наш коэффициент выше, чем у букмекера
                if our_odd > bookmaker_odd:
                    value = ((our_odd - bookmaker_odd) / bookmaker_odd) * 100
                    if value > 5:  # Порог для value bet
                        value_bets.append({
                            'market': market,
                            'our_odd': our_odd,
                            'bookmaker_odd': bookmaker_odd,
                            'value_percentage': round(value, 2)
                        })
        
        return value_bets