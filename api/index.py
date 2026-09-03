from flask import Flask, request, jsonify
import json
import re
from datetime import datetime

app = Flask(__name__)

# Импорт модулей
try:
    from features import load_additional_features
    from data import get_player_stats, parse_url
    from analytics import save_match_analysis, get_match_history, save_match_result, get_analytics, get_learning_data
except ImportError as e:
    print(f"Import error: {e}")
    def load_additional_features():
        return {}
    def get_player_stats(player_name):
        return {}
    def parse_url(url):
        return None
    def save_match_analysis(p1, p2, pred):
        return True
    def get_match_history(limit=50):
        return []
    def save_match_result(match_id, winner):
        return True
    def get_analytics():
        return {}
    def get_learning_data():
        return []

BASE_HTML = """
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Теннис Анализатор</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        body {
            font-family: 'Segoe UI', Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        
        .main-container {
            display: flex;
            gap: 20px;
            max-width: 1400px;
            margin: 0 auto;
        }
        
        .container {
            flex: 1;
            background: white;
            border-radius: 20px;
            padding: 30px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
        }
        
        .sidebar {
            width: 300px;
            background: white;
            border-radius: 20px;
            padding: 20px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
            max-height: 90vh;
            overflow-y: auto;
        }
        
        .sidebar h3 {
            color: #667eea;
            margin-bottom: 15px;
            text-align: center;
        }
        
        .history-item {
            background: #f8f9fa;
            padding: 10px;
            margin-bottom: 10px;
            border-radius: 10px;
            border: 1px solid #e0e0e0;
        }
        
        .history-item p {
            margin: 5px 0;
            font-size: 0.9em;
        }
        
        h1 {
            text-align: center;
            color: #667eea;
            margin-bottom: 10px;
            font-size: 2em;
        }
        
        .subtitle {
            text-align: center;
            color: #666;
            margin-bottom: 30px;
            font-size: 1.1em;
        }
        
        .url-section {
            background: #f0f4ff;
            padding: 20px;
            border-radius: 15px;
            margin-bottom: 30px;
            border: 2px solid #667eea;
        }
        
        .url-section h3 {
            color: #667eea;
            margin-bottom: 15px;
        }
        
        .url-input-group {
            display: flex;
            gap: 10px;
        }
        
        .url-input-group input {
            flex: 1;
            padding: 12px;
            border: 2px solid #ddd;
            border-radius: 8px;
            font-size: 14px;
        }
        
        .url-input-group button {
            padding: 12px 25px;
            background: #667eea;
            color: white;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-weight: bold;
            white-space: nowrap;
        }
        
        .players {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .player-card {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 15px;
            border: 2px solid #e0e0e0;
        }
        
        .player-card h3 {
            color: #667eea;
            margin-bottom: 20px;
            text-align: center;
            font-size: 1.3em;
        }
        
        .form-group {
            margin-bottom: 15px;
        }
        
        .form-group label {
            display: block;
            margin-bottom: 5px;
            color: #555;
            font-weight: bold;
            font-size: 0.9em;
        }
        
        .form-group input {
            width: 100%;
            padding: 12px;
            border: 2px solid #ddd;
            border-radius: 8px;
            font-size: 14px;
        }
        
        .btn {
            width: 100%;
            padding: 15px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 10px;
            font-size: 18px;
            font-weight: bold;
            cursor: pointer;
        }
        
        .results {
            display: none;
            margin-top: 20px;
            padding: 20px;
            background: #f0f4ff;
            border-radius: 10px;
        }
        
        .results.show {
            display: block;
            animation: fadeIn 0.5s;
        }
        
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        .probability-bar {
            height: 30px;
            background: #e0e0e0;
            border-radius: 15px;
            overflow: hidden;
            margin: 10px 0;
        }
        
        .probability-fill {
            height: 100%;
            background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
            transition: width 1s ease;
        }
        
        .recommendation-box {
            margin-top: 20px;
            padding: 15px;
            background: #e8f5e9;
            border-radius: 10px;
            border-left: 5px solid #4caf50;
        }
        
        .notification {
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 15px 20px;
            background: #4caf50;
            color: white;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            z-index: 1000;
        }
        
        @media (max-width: 768px) {
            .main-container {
                flex-direction: column;
            }
            .sidebar {
                width: 100%;
            }
            .players {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>
    <div class="main-container">
        <div class="container">
            <h1>🎾 Теннис Анализатор</h1>
            <p class="subtitle">Профессиональный анализ теннисных матчей</p>
            
            <div class="url-section">
                <h3>🔗 Загрузка матча по ссылке</h3>
                <div class="url-input-group">
                    <input type="url" id="matchUrl" placeholder="Вставьте ссылку на матч с Лиги Ставок">
                    <button onclick="loadFromUrl()">📥 Загрузить</button>
                </div>
            </div>
            
            <div class="players">
                <div class="player-card">
                    <h3>👤 Игрок 1</h3>
                    <div class="form-group"><label>Имя игрока</label><input type="text" id="p1Name"></div>
                    <div class="form-group"><label>Рейтинг ATP</label><input type="number" id="p1Rating"></div>
                    <div class="form-group"><label>Выигранные геймы</label><input type="number" id="p1GamesWon"></div>
                    <div class="form-group"><label>Проигранные геймы</label><input type="number" id="p1GamesLost"></div>
                    <div class="form-group"><label>Эйсы</label><input type="number" id="p1Aces"></div>
                    <div class="form-group"><label>Двойные ошибки</label><input type="number" id="p1DoubleFaults"></div>
                    <div class="form-group"><label>% очков на 1-й подаче</label><input type="number" id="p1FirstServePct"></div>
                    <div class="form-group"><label>% очков на 2-й подаче</label><input type="number" id="p1SecondServePct"></div>
                    <div class="form-group"><label>Выигранные брейк-поинты</label><input type="number" id="p1BreakPointsWon"></div>
                    <div class="form-group"><label>Общие брейк-поинты</label><input type="number" id="p1BreakPointsTotal"></div>
                    <div class="form-group"><label>% реализации брейк-поинтов</label><input type="number" id="p1BreakPct"></div>
                </div>
                
                <div class="player-card">
                    <h3>👤 Игрок 2</h3>
                    <div class="form-group"><label>Имя игрока</label><input type="text" id="p2Name"></div>
                    <div class="form-group"><label>Рейтинг ATP</label><input type="number" id="p2Rating"></div>
                    <div class="form-group"><label>Выигранные геймы</label><input type="number" id="p2GamesWon"></div>
                    <div class="form-group"><label>Проигранные геймы</label><input type="number" id="p2GamesLost"></div>
                    <div class="form-group"><label>Эйсы</label><input type="number" id="p2Aces"></div>
                    <div class="form-group"><label>Двойные ошибки</label><input type="number" id="p2DoubleFaults"></div>
                    <div class="form-group"><label>% очков на 1-й подаче</label><input type="number" id="p2FirstServePct"></div>
                    <div class="form-group"><label>% очков на 2-й подаче</label><input type="number" id="p2SecondServePct"></div>
                    <div class="form-group"><label>Выигранные брейк-поинты</label><input type="number" id="p2BreakPointsWon"></div>
                    <div class="form-group"><label>Общие брейк-поинты</label><input type="number" id="p2BreakPointsTotal"></div>
                    <div class="form-group"><label>% реализации брейк-поинтов</label><input type="number" id="p2BreakPct"></div>
                </div>
            </div>
            
            <button class="btn" onclick="analyzeMatch()">📊 Анализировать матч</button>
            
            <div class="results" id="results">
                <h3>📈 Результаты анализа</h3>
                <div id="resultsContent"></div>
            </div>
        </div>
        
        <div class="sidebar">
            <h3>📜 История матчей</h3>
            <div id="historyContent">
                <p style="text-align: center; color: #999;">История пуста</p>
            </div>
        </div>
    </div>
    
    <script>
        function showNotification(message) {
            const notification = document.createElement('div');
            notification.className = 'notification';
            notification.textContent = message;
            document.body.appendChild(notification);
            setTimeout(() => notification.remove(), 3000);
        }
        
        function loadFromUrl() {
            const url = document.getElementById('matchUrl').value;
            if (!url) {
                showNotification('Пожалуйста, вставьте ссылку');
                return;
            }
            
            fetch('/api/parse_url', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({url: url})
            })
            .then(response => response.json())
            .then(data => {
                if (data.success && data.player1 && data.player2) {
                    document.getElementById('p1Name').value = data.player1.name || '';
                    document.getElementById('p2Name').value = data.player2.name || '';
                    showNotification('✅ Имена загружены!');
                }
            });
        }
        
        function analyzeMatch() {
            const p1Name = document.getElementById('p1Name').value || 'Игрок 1';
            const p2Name = document.getElementById('p2Name').value || 'Игрок 2';
            
            // Сбор данных
            const player1 = {
                name: p1Name,
                rating: parseInt(document.getElementById('p1Rating').value) || 100,
                gamesWon: parseInt(document.getElementById('p1GamesWon').value) || 0,
                gamesLost: parseInt(document.getElementById('p1GamesLost').value) || 0,
                aces: parseInt(document.getElementById('p1Aces').value) || 0,
                doubleFaults: parseInt(document.getElementById('p1DoubleFaults').value) || 0,
                firstServePct: parseFloat(document.getElementById('p1FirstServePct').value) || 50,
                secondServePct: parseFloat(document.getElementById('p1SecondServePct').value) || 50,
                bpWon: parseInt(document.getElementById('p1BreakPointsWon').value) || 0,
                bpTotal: parseInt(document.getElementById('p1BreakPointsTotal').value) || 0,
                breakPct: parseFloat(document.getElementById('p1BreakPct').value) || 50
            };
            
            const player2 = {
                name: p2Name,
                rating: parseInt(document.getElementById('p2Rating').value) || 100,
                gamesWon: parseInt(document.getElementById('p2GamesWon').value) || 0,
                gamesLost: parseInt(document.getElementById('p2GamesLost').value) || 0,
                aces: parseInt(document.getElementById('p2Aces').value) || 0,
                doubleFaults: parseInt(document.getElementById('p2DoubleFaults').value) || 0,
                firstServePct: parseFloat(document.getElementById('p2FirstServePct').value) || 50,
                secondServePct: parseFloat(document.getElementById('p2SecondServePct').value) || 50,
                bpWon: parseInt(document.getElementById('p2BreakPointsWon').value) || 0,
                bpTotal: parseInt(document.getElementById('p2BreakPointsTotal').value) || 0,
                breakPct: parseFloat(document.getElementById('p2BreakPct').value) || 50
            };
            
            // Расчет силы
            let p1Strength = (1 - player1.rating / 100) * 0.3;
            let p2Strength = (1 - player2.rating / 100) * 0.3;
            
            const p1GameRatio = player1.gamesWon / (player1.gamesWon + player1.gamesLost || 1);
            const p2GameRatio = player2.gamesWon / (player2.gamesWon + player2.gamesLost || 1);
            p1Strength += p1GameRatio * 0.2;
            p2Strength += p2GameRatio * 0.2;
            
            const totalAces = player1.aces + player2.aces || 1;
            p1Strength += (player1.aces / totalAces) * 0.1;
            p2Strength += (player2.aces / totalAces) * 0.1;
            
            const totalDF = player1.doubleFaults + player2.doubleFaults || 1;
            p1Strength += (1 - player1.doubleFaults / totalDF) * 0.1;
            p2Strength += (1 - player2.doubleFaults / totalDF) * 0.1;
            
            const p1ServeAvg = (player1.firstServePct + player1.secondServePct) / 200;
            const p2ServeAvg = (player2.firstServePct + player2.secondServePct) / 200;
            p1Strength += p1ServeAvg * 0.2;
            p2Strength += p2ServeAvg * 0.2;
            
            p1Strength += (player1.breakPct / 100) * 0.1;
            p2Strength += (player2.breakPct / 100) * 0.1;
            
            const p1Prob = (p1Strength / (p1Strength + p2Strength)) * 100;
            const p2Prob = 100 - p1Prob;
            
            const fairP1Odds = (100 / p1Prob).toFixed(2);
            const fairP2Odds = (100 / p2Prob).toFixed(2);
            
            const winner = p1Prob > p2Prob ? p1Name : p2Name;
            const confidence = Math.max(p1Prob, p2Prob);
            
            // Сохранение в базу
            fetch('/api/save_match', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    player1: player1,
                    player2: player2,
                    prediction: {
                        winner: winner,
                        confidence: confidence.toFixed(1),
                        fair_odds: {p1: fairP1Odds, p2: fairP2Odds}
                    }
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    showNotification('✅ Матч сохранен в историю!');
                    loadHistory();
                }
            });
            
            // Отображение результатов
            document.getElementById('resultsContent').innerHTML = `
                <h4>🎯 Вероятность победы:</h4>
                <p><strong>${p1Name}</strong>: ${p1Prob.toFixed(1)}% (коэф. ${fairP1Odds})</p>
                <div class="probability-bar"><div class="probability-fill" style="width: ${p1Prob}%"></div></div>
                <p><strong>${p2Name}</strong>: ${p2Prob.toFixed(1)}% (коэф. ${fairP2Odds})</p>
                <div class="probability-bar"><div class="probability-fill" style="width: ${p2Prob}%"></div></div>
                <div class="recommendation-box">
                    <h4>💡 Рекомендация:</h4>
                    <p>Ставка на: <strong>${winner}</strong> (${confidence.toFixed(1)}%)</p>
                </div>
            `;
            
            document.getElementById('results').classList.add('show');
        }
        
        function loadHistory() {
            fetch('/api/history')
            .then(response => response.json())
            .then(data => {
                if (data.success && data.history && data.history.length > 0) {
                    let html = '';
                    data.history.forEach(match => {
                        html += `
                            <div class="history-item">
                                <p><strong>${match.player1.name}</strong> vs <strong>${match.player2.name}</strong></p>
                                <p>Прогноз: ${match.predicted_winner} (${match.prediction_confidence}%)</p>
                            </div>
                        `;
                    });
                    document.getElementById('historyContent').innerHTML = html;
                }
            });
        }
        
        // Загрузка истории при старте
        loadHistory();
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return BASE_HTML

@app.route('/api/parse_url', methods=['POST'])
def api_parse_url():
    try:
        data = request.json
        url = data.get('url', '')
        result = parse_url(url)
        if result:
            return jsonify({'success': True, **result})
        else:
            return jsonify({'success': False, 'error': 'Не удалось распознать'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/save_match', methods=['POST'])
def api_save_match():
    try:
        data = request.json
        success = save_match_analysis(data.get('player1'), data.get('player2'), data.get('prediction'))
        return jsonify({'success': success})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/history', methods=['GET'])
def api_history():
    try:
        history = get_match_history(50)
        return jsonify({'success': True, 'history': history})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/analytics', methods=['GET'])
def api_analytics():
    try:
        analytics = get_analytics()
        return jsonify({'success': True, 'analytics': analytics})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/learning', methods=['GET'])
def api_learning():
    try:
        errors = get_learning_data()
        return jsonify({'success': True, 'errors': errors})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

app = app