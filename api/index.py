from flask import Flask, request, jsonify
import json
import re

app = Flask(__name__)

# Импорт дополнительных модулей
try:
    from features import load_additional_features
    from data import get_player_stats, parse_url
except ImportError:
    # Если модули не найдены, используем базовые функции
    def load_additional_features():
        return {}
    
    def get_player_stats(player_name):
        return {}
    
    def parse_url(url):
        return None

# Базовый HTML (можно расширять через features)
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
        
        .container {
            max-width: 1000px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            padding: 30px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
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
        
        .url-input-group button:hover {
            background: #5a6fd8;
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
            transition: border-color 0.3s;
        }
        
        .form-group input:focus {
            border-color: #667eea;
            outline: none;
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
            transition: all 0.3s;
        }
        
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0,0,0,0.3);
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
        
        .loading {
            display: none;
            text-align: center;
            padding: 20px;
            color: #667eea;
            font-weight: bold;
        }
        
        .loading.show {
            display: block;
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
            animation: slideIn 0.3s;
        }
        
        @keyframes slideIn {
            from { transform: translateX(100%); }
            to { transform: translateX(0); }
        }
        
        .additional-features {
            margin-top: 20px;
            padding: 20px;
            background: #f5f5f5;
            border-radius: 10px;
            border: 2px dashed #ccc;
        }
        
        .additional-features h4 {
            color: #666;
            margin-bottom: 15px;
        }
        
        @media (max-width: 600px) {
            .players { grid-template-columns: 1fr; }
            .container { padding: 15px; }
            h1 { font-size: 1.5em; }
            .url-input-group { flex-direction: column; }
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🎾 Теннис Анализатор</h1>
        <p class="subtitle">Профессиональный анализ теннисных матчей</p>
        
        <div class="url-section">
            <h3>🔗 Загрузка матча по ссылке</h3>
            <div class="url-input-group">
                <input type="url" id="matchUrl" placeholder="Вставьте ссылку на матч с Лиги Ставок">
                <button onclick="loadFromUrl()">📥 Загрузить</button>
            </div>
            <p style="margin-top: 10px; font-size: 0.9em; color: #666;">
                Имена игроков будут загружены автоматически.
            </p>
        </div>
        
        <div class="players">
            <div class="player-card">
                <h3>👤 Игрок 1</h3>
                
                <div class="form-group">
                    <label>Имя игрока</label>
                    <input type="text" id="p1Name" placeholder="Имя игрока">
                </div>
                
                <div class="form-group">
                    <label>Рейтинг ATP</label>
                    <input type="number" id="p1Rating" placeholder="Например: 50" min="1" max="2000">
                </div>
                
                <div class="form-group">
                    <label>Выигранные геймы</label>
                    <input type="number" id="p1GamesWon" placeholder="Например: 120" min="0">
                </div>
                
                <div class="form-group">
                    <label>Проигранные геймы</label>
                    <input type="number" id="p1GamesLost" placeholder="Например: 80" min="0">
                </div>
                
                <div class="form-group">
                    <label>Эйсы</label>
                    <input type="number" id="p1Aces" placeholder="Например: 45" min="0">
                </div>
                
                <div class="form-group">
                    <label>Двойные ошибки</label>
                    <input type="number" id="p1DoubleFaults" placeholder="Например: 15" min="0">
                </div>
                
                <div class="form-group">
                    <label>% очков на 1-й подаче</label>
                    <input type="number" id="p1FirstServePct" placeholder="Например: 72" min="0" max="100">
                </div>
                
                <div class="form-group">
                    <label>% очков на 2-й подаче</label>
                    <input type="number" id="p1SecondServePct" placeholder="Например: 52" min="0" max="100">
                </div>
                
                <div class="form-group">
                    <label>Выигранные брейк-поинты</label>
                    <input type="number" id="p1BreakPointsWon" placeholder="Например: 30" min="0">
                </div>
                
                <div class="form-group">
                    <label>Общие брейк-поинты</label>
                    <input type="number" id="p1BreakPointsTotal" placeholder="Например: 60" min="0">
                </div>
                
                <div class="form-group">
                    <label>% реализации брейк-поинтов</label>
                    <input type="number" id="p1BreakPct" placeholder="Например: 50" min="0" max="100">
                </div>
            </div>
            
            <div class="player-card">
                <h3>👤 Игрок 2</h3>
                
                <div class="form-group">
                    <label>Имя игрока</label>
                    <input type="text" id="p2Name" placeholder="Имя игрока">
                </div>
                
                <div class="form-group">
                    <label>Рейтинг ATP</label>
                    <input type="number" id="p2Rating" placeholder="Например: 80" min="1" max="2000">
                </div>
                
                <div class="form-group">
                    <label>Выигранные геймы</label>
                    <input type="number" id="p2GamesWon" placeholder="Например: 100" min="0">
                </div>
                
                <div class="form-group">
                    <label>Проигранные геймы</label>
                    <input type="number" id="p2GamesLost" placeholder="Например: 90" min="0">
                </div>
                
                <div class="form-group">
                    <label>Эйсы</label>
                    <input type="number" id="p2Aces" placeholder="Например: 35" min="0">
                </div>
                
                <div class="form-group">
                    <label>Двойные ошибки</label>
                    <input type="number" id="p2DoubleFaults" placeholder="Например: 20" min="0">
                </div>
                
                <div class="form-group">
                    <label>% очков на 1-й подаче</label>
                    <input type="number" id="p2FirstServePct" placeholder="Например: 68" min="0" max="100">
                </div>
                
                <div class="form-group">
                    <label>% очков на 2-й подаче</label>
                    <input type="number" id="p2SecondServePct" placeholder="Например: 48" min="0" max="100">
                </div>
                
                <div class="form-group">
                    <label>Выигранные брейк-поинты</label>
                    <input type="number" id="p2BreakPointsWon" placeholder="Например: 25" min="0">
                </div>
                
                <div class="form-group">
                    <label>Общие брейк-поинты</label>
                    <input type="number" id="p2BreakPointsTotal" placeholder="Например: 55" min="0">
                </div>
                
                <div class="form-group">
                    <label>% реализации брейк-поинтов</label>
                    <input type="number" id="p2BreakPct" placeholder="Например: 45" min="0" max="100">
                </div>
            </div>
            
            <div style="grid-column: 1 / -1; background: #e8f5e9; padding: 20px; border-radius: 15px; border: 2px solid #4caf50;">
                <h4 style="color: #2e7d32; margin-bottom: 15px;">💰 Коэффициенты букмекеров</h4>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px;">
                    <div class="form-group">
                        <label>Коэффициент на победу Игрока 1</label>
                        <input type="number" id="p1Odds" placeholder="Например: 2.10" step="0.01" min="1.01">
                    </div>
                    
                    <div class="form-group">
                        <label>Коэффициент на победу Игрока 2</label>
                        <input type="number" id="p2Odds" placeholder="Например: 1.85" step="0.01" min="1.01">
                    </div>
                </div>
            </div>
        </div>
        
        <button class="btn" onclick="analyzeMatch()">📊 Анализировать матч</button>
        
        <div class="loading" id="loading">
            ⏳ Анализируем...
        </div>
        
        <div class="results" id="results">
            <h3>📈 Результаты анализа</h3>
            <div id="resultsContent"></div>
        </div>
        
        <div class="additional-features" id="additionalFeatures">
            <h4>🔧 Дополнительные функции</h4>
            <div id="additionalFeaturesContent">
                <!-- Здесь будут дополнительные функции -->
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
                showNotification('Пожалуйста, вставьте ссылку на матч');
                return;
            }
            
            document.getElementById('loading').classList.add('show');
            
            fetch('/api/parse_url', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({url: url})
            })
            .then(response => response.json())
            .then(data => {
                document.getElementById('loading').classList.remove('show');
                
                if (data.success && data.player1 && data.player2) {
                    if (data.player1.name) {
                        document.getElementById('p1Name').value = data.player1.name;
                    }
                    
                    if (data.player2.name) {
                        document.getElementById('p2Name').value = data.player2.name;
                    }
                    
                    // Загрузка дополнительной статистики
                    loadPlayerStats(data.player1.name, 1);
                    loadPlayerStats(data.player2.name, 2);
                    
                    showNotification('✅ Имена загружены!');
                } else {
                    showNotification('⚠️ ' + (data.error || 'Не удалось загрузить данные'));
                }
            })
            .catch(error => {
                document.getElementById('loading').classList.remove('show');
                showNotification('❌ Ошибка. Заполните данные вручную.');
            });
        }
        
        function loadPlayerStats(playerName, playerNumber) {
            fetch('/api/player_stats', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({name: playerName})
            })
            .then(response => response.json())
            .then(data => {
                if (data.success && data.stats) {
                    const prefix = 'p' + playerNumber;
                    
                    if (data.stats.rating) document.getElementById(prefix + 'Rating').value = data.stats.rating;
                    if (data.stats.gamesWon) document.getElementById(prefix + 'GamesWon').value = data.stats.gamesWon;
                    if (data.stats.gamesLost) document.getElementById(prefix + 'GamesLost').value = data.stats.gamesLost;
                    if (data.stats.aces) document.getElementById(prefix + 'Aces').value = data.stats.aces;
                    if (data.stats.doubleFaults) document.getElementById(prefix + 'DoubleFaults').value = data.stats.doubleFaults;
                    if (data.stats.firstServePct) document.getElementById(prefix + 'FirstServePct').value = data.stats.firstServePct;
                    if (data.stats.secondServePct) document.getElementById(prefix + 'SecondServePct').value = data.stats.secondServePct;
                    if (data.stats.bpWon) document.getElementById(prefix + 'BreakPointsWon').value = data.stats.bpWon;
                    if (data.stats.bpTotal) document.getElementById(prefix + 'BreakPointsTotal').value = data.stats.bpTotal;
                    if (data.stats.breakPct) document.getElementById(prefix + 'BreakPct').value = data.stats.breakPct;
                }
            });
        }
        
        function analyzeMatch() {
            const p1Name = document.getElementById('p1Name').value || 'Игрок 1';
            const p2Name = document.getElementById('p2Name').value || 'Игрок 2';
            
            const p1Rating = parseInt(document.getElementById('p1Rating').value) || 100;
            const p2Rating = parseInt(document.getElementById('p2Rating').value) || 100;
            
            const p1GamesWon = parseInt(document.getElementById('p1GamesWon').value) || 0;
            const p1GamesLost = parseInt(document.getElementById('p1GamesLost').value) || 0;
            const p2GamesWon = parseInt(document.getElementById('p2GamesWon').value) || 0;
            const p2GamesLost = parseInt(document.getElementById('p2GamesLost').value) || 0;
            
            const p1Aces = parseInt(document.getElementById('p1Aces').value) || 0;
            const p2Aces = parseInt(document.getElementById('p2Aces').value) || 0;
            
            const p1DoubleFaults = parseInt(document.getElementById('p1DoubleFaults').value) || 0;
            const p2DoubleFaults = parseInt(document.getElementById('p2DoubleFaults').value) || 0;
            
            const p1FirstServe = parseFloat(document.getElementById('p1FirstServePct').value) / 100 || 0.5;
            const p2FirstServe = parseFloat(document.getElementById('p2FirstServePct').value) / 100 || 0.5;
            
            const p1SecondServe = parseFloat(document.getElementById('p1SecondServePct').value) / 100 || 0.5;
            const p2SecondServe = parseFloat(document.getElementById('p2SecondServePct').value) / 100 || 0.5;
            
            const p1BPWon = parseInt(document.getElementById('p1BreakPointsWon').value) || 0;
            const p1BPTotal = parseInt(document.getElementById('p1BreakPointsTotal').value) || 0;
            const p2BPWon = parseInt(document.getElementById('p2BreakPointsWon').value) || 0;
            const p2BPTotal = parseInt(document.getElementById('p2BreakPointsTotal').value) || 0;
            
            const p1BreakPct = parseFloat(document.getElementById('p1BreakPct').value) / 100 || 0.5;
            const p2BreakPct = parseFloat(document.getElementById('p2BreakPct').value) / 100 || 0.5;
            
            const p1Odds = parseFloat(document.getElementById('p1Odds').value) || 0;
            const p2Odds = parseFloat(document.getElementById('p2Odds').value) || 0;
            
            let p1Strength = 0;
            let p2Strength = 0;
            
            p1Strength += (1 - p1Rating / 100) * 0.3;
            p2Strength += (1 - p2Rating / 100) * 0.3;
            
            const p1GameRatio = p1GamesWon / (p1GamesWon + p1GamesLost || 1);
            const p2GameRatio = p2GamesWon / (p2GamesWon + p2GamesLost || 1);
            p1Strength += p1GameRatio * 0.2;
            p2Strength += p2GameRatio * 0.2;
            
            const totalAces = p1Aces + p2Aces || 1;
            p1Strength += (p1Aces / totalAces) * 0.1;
            p2Strength += (p2Aces / totalAces) * 0.1;
            
            const totalDF = p1DoubleFaults + p2DoubleFaults || 1;
            p1Strength += (1 - p1DoubleFaults / totalDF) * 0.1;
            p2Strength += (1 - p2DoubleFaults / totalDF) * 0.1;
            
            const p1ServeAvg = (p1FirstServe + p1SecondServe) / 2;
            const p2ServeAvg = (p2FirstServe + p2SecondServe) / 2;
            p1Strength += p1ServeAvg * 0.2;
            p2Strength += p2ServeAvg * 0.2;
            
            p1Strength += p1BreakPct * 0.1;
            p2Strength += p2BreakPct * 0.1;
            
            const p1Prob = (p1Strength / (p1Strength + p2Strength)) * 100;
            const p2Prob = 100 - p1Prob;
            
            const fairP1Odds = (100 / p1Prob).toFixed(2);
            const fairP2Odds = (100 / p2Prob).toFixed(2);
            
            let valueBet = '';
            if (p1Odds > fairP1Odds) {
                valueBet = `💰 Value bet: ${p1Name} (коэф. ${p1Odds} vs справедливый ${fairP1Odds})`;
            } else if (p2Odds > fairP2Odds) {
                valueBet = `💰 Value bet: ${p2Name} (коэф. ${p2Odds} vs справедливый ${fairP2Odds})`;
            } else {
                valueBet = 'Нет value bets';
            }
            
            const recommendation = p1Prob > p2Prob ? p1Name : p2Name;
            const recommendationProb = Math.max(p1Prob, p2Prob);
            
            document.getElementById('resultsContent').innerHTML = `
                <div style="margin-bottom: 20px;">
                    <h4>🎯 Вероятность победы:</h4>
                    <div style="margin: 15px 0;">
                        <p><strong>${p1Name}</strong>: ${p1Prob.toFixed(1)}% (справедливый коэф. ${fairP1Odds})</p>
                        <div class="probability-bar">
                            <div class="probability-fill" style="width: ${p1Prob}%"></div>
                        </div>
                    </div>
                    <div style="margin: 15px 0;">
                        <p><strong>${p2Name}</strong>: ${p2Prob.toFixed(1)}% (справедливый коэф. ${fairP2Odds})</p>
                        <div class="probability-bar">
                            <div class="probability-fill" style="width: ${p2Prob}%"></div>
                        </div>
                    </div>
                </div>
                
                <div style="background: #e3f2fd; padding: 15px; border-radius: 10px; margin-bottom: 20px;">
                    <h4>📊 Сравнение статистики:</h4>
                    <table style="width: 100%; border-collapse: collapse;">
                        <tr>
                            <th style="text-align: left; padding: 8px;">Показатель</th>
                            <th style="text-align: center; padding: 8px;">${p1Name}</th>
                            <th style="text-align: center; padding: 8px;">${p2Name}</th>
                        </tr>
                        <tr><td style="padding: 8px;">Рейтинг ATP</td><td style="text-align: center;">${p1Rating}</td><td style="text-align: center;">${p2Rating}</td></tr>
                        <tr><td style="padding: 8px;">Геймы (В/П)</td><td style="text-align: center;">${p1GamesWon}/${p1GamesLost}</td><td style="text-align: center;">${p2GamesWon}/${p2GamesLost}</td></tr>
                        <tr><td style="padding: 8px;">Эйсы</td><td style="text-align: center;">${p1Aces}</td><td style="text-align: center;">${p2Aces}</td></tr>
                        <tr><td style="padding: 8px;">Двойные ошибки</td><td style="text-align: center;">${p1DoubleFaults}</td><td style="text-align: center;">${p2DoubleFaults}</td></tr>
                        <tr><td style="padding: 8px;">1-я подача (%)</td><td style="text-align: center;">${(p1FirstServe * 100).toFixed(0)}%</td><td style="text-align: center;">${(p2FirstServe * 100).toFixed(0)}%</td></tr>
                        <tr><td style="padding: 8px;">2-я подача (%)</td><td style="text-align: center;">${(p1SecondServe * 100).toFixed(0)}%</td><td style="text-align: center;">${(p2SecondServe * 100).toFixed(0)}%</td></tr>
                        <tr><td style="padding: 8px;">Брейк-поинты (В/О)</td><td style="text-align: center;">${p1BPWon}/${p1BPTotal}</td><td style="text-align: center;">${p2BPWon}/${p2BPTotal}</td></tr>
                    </table>
                </div>
                
                <div style="background: #fff3e0; padding: 15px; border-radius: 10px; margin-bottom: 20px;">
                    <h4>💰 Сравнение с букмекером:</h4>
                    <p>Букмекер: ${p1Name} - ${p1Odds || 'нет данных'}, ${p2Name} - ${p2Odds || 'нет данных'}</p>
                    <p>Наш анализ: ${p1Name} - ${fairP1Odds}, ${p2Name} - ${fairP2Odds}</p>
                    <p style="margin-top: 10px; font-weight: bold;">${valueBet}</p>
                </div>
                
                <div class="recommendation-box">
                    <h4>💡 Рекомендация:</h4>
                    <p style="font-size: 1.1em; margin-top: 10px;">
                        Ставка на победу: <strong>${recommendation}</strong><br>
                        Уверенность: <strong>${recommendationProb.toFixed(1)}%</strong>
                    </p>
                </div>
            `;
            
            document.getElementById('results').classList.add('show');
            document.getElementById('results').scrollIntoView({ behavior: 'smooth' });
        }
        
        // Загрузка дополнительных функций
        function loadAdditionalFeatures() {
            fetch('/api/features')
            .then(response => response.json())
            .then(data => {
                if (data.success && data.features) {
                    document.getElementById('additionalFeaturesContent').innerHTML = data.features.html;
                }
            });
        }
        
        // Загрузка при старте
        loadAdditionalFeatures();
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

@app.route('/api/player_stats', methods=['POST'])
def api_player_stats():
    try:
        data = request.json
        player_name = data.get('name', '')
        stats = get_player_stats(player_name)
        return jsonify({'success': True, 'stats': stats})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/features', methods=['GET'])
def api_features():
    try:
        features = load_additional_features()
        return jsonify({'success': True, 'features': features})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

app = app