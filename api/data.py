# Данные игроков и статистика
# Добавляйте сюда новые данные

import re

# База данных игроков (пример)
PLAYERS_DATABASE = {
    'novak djokovic': {
        'rating': 1,
        'gamesWon': 500,
        'gamesLost': 200,
        'aces': 300,
        'doubleFaults': 50,
        'firstServePct': 75,
        'secondServePct': 55,
        'bpWon': 200,
        'bpTotal': 400,
        'breakPct': 50
    },
    'carlos alcaraz': {
        'rating': 2,
        'gamesWon': 400,
        'gamesLost': 180,
        'aces': 250,
        'doubleFaults': 60,
        'firstServePct': 72,
        'secondServePct': 52,
        'bpWon': 180,
        'bpTotal': 380,
        'breakPct': 47
    },
    'daniil medvedev': {
        'rating': 3,
        'gamesWon': 450,
        'gamesLost': 220,
        'aces': 280,
        'doubleFaults': 55,
        'firstServePct': 70,
        'secondServePct': 50,
        'bpWon': 170,
        'bpTotal': 350,
        'breakPct': 48
    }
}

def parse_url(url):
    """Парсинг URL для извлечения имён игроков"""
    try:
        match = re.search(r'/tennis/([^/]+?)(?:-id-|$)', url)
        
        if not match:
            match = re.search(r'/([a-z]+-[a-z]-[a-z]+-[a-z])', url)
        
        if match:
            players_str = match.group(1)
            parts = players_str.split('-')
            parts = [p for p in parts if p]
            
            player1_parts = []
            player2_parts = []
            
            if 'i' in parts or 'and' in parts:
                separator_index = -1
                for i, part in enumerate(parts):
                    if part in ['i', 'and']:
                        separator_index = i
                        break
                
                if separator_index > 0:
                    player1_parts = parts[:separator_index]
                    player2_parts = parts[separator_index+1:]
            else:
                middle = len(parts) // 2
                player1_parts = parts[:middle]
                player2_parts = parts[middle:]
            
            p1_name = ' '.join(player1_parts).title().strip()
            p2_name = ' '.join(player2_parts).title().strip()
            
            if p1_name and p2_name:
                return {
                    'player1': {'name': p1_name},
                    'player2': {'name': p2_name}
                }
        
        return None
    except Exception as e:
        print(f"Error parsing URL: {e}")
        return None

def get_player_stats(player_name):
    """Получение статистики игрока из базы данных"""
    if not player_name:
        return {}
    
    # Нормализация имени
    normalized_name = player_name.lower().strip()
    
    # Поиск в базе
    if normalized_name in PLAYERS_DATABASE:
        return PLAYERS_DATABASE[normalized_name]
    
    # Частичное совпадение
    for name, stats in PLAYERS_DATABASE.items():
        if normalized_name in name or name in normalized_name:
            return stats
    
    return {}