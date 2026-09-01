from flask import Flask, request, jsonify
import json

app = Flask(__name__)

HTML_PAGE = """
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
        
        .form-group input, .form-group select {
            width: 100%;
            padding: 12px;
            border: 2px solid #ddd;
            border-radius: 8px;
            font-size: 14px;
            transition: border-color 0.3s;
        }
        
        .form-group input:focus, .form-group select:focus {
            border-color: #667eea;
            outline: none;
        }
        
        .additional-info {
            grid-column: 1 / -1;
            background: #fff8e1;
            padding: 20px;
            border-radius: 15px;
            border: 2px solid #ffd54f;
            margin-top: 10px;
        }
        
        .additional-info h4 {
            color: #f57c00;
            margin-bottom: 15px;
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
                <input type="url" id="matchUrl" placeholder="Вставьте ссылку на матч (Лига Ставок, Flashscore, и т.д.)">
                <button onclick="loadFromUrl()">📥 Загрузить</button>
            </div>
            <p style="margin-top: 10px; font-size: 0.9em; color: #666;">
                Поддерживаются ссылки с сайтов: Лига Ставок, Flashscore, Tennis Explorer
            </p>
        </div>
        
        <div class="players">
            <div class="player-card">
                <h3>👤 Игрок 1</h3>
                
                <div class="form-group">
                    <label>Имя игрока</label>
                    <input type="text" id="p1Name" placeholder="Например: Новак Джокович">
                </div>
                
                <div class="form-group">
                    <label>Рейтинг ATP</label>
                    <input type="number" id="p1Rating" placeholder="Например: 1" min="1" max="2000">
                </div>
                
                <div class="form-group">
                    <label>Процент побед (%)</label>
                    <input type="number" id="p1WinRate" placeholder="Например: 83" min="0" max="100">
                </div>
                
                <div class="form-group">
                    <label>Победы на покрытии (%)</label>
                    <input type="number" id="p1SurfaceRate" placeholder="Например: 80" min="0" max="100">
                </div>
                
                <div class="form-group">
                    <label>Текущая форма (0-100)</label>
                    <input type="number" id="p1Form" placeholder="Например: 85" min="0" max="100">
                </div>
                
                <div class="form-group">
                    <label>Победы в личных встречах</label>
                    <input type="number" id="p1H2H" placeholder="Например: 5" min="0">
                </div>
                
                <div class="form-group">
                    <label>Статус травмы</label>
                    <select id="p1Injury">
                        <option value="healthy">Здоров</option>
                        <option value="questionable">Под вопросом</option>
                        <option value="injured">Травмирован</option>
                    </select>
                </div>
                
                <div class="form-group">
                    <label>Уровень усталости (0-100)</label>
                    <input type="number" id="p1Fatigue" placeholder="Например: 20" min="0" max="100" value="20">
                </div>
            </div>
            
            <div class="player-card">
                <h3>👤 Игрок 2</h3>
                
                <div class="form-group">
                    <label>Имя игрока</label>
                    <input type="text" id="p2Name" placeholder="Например: Карлос Алькарас">
                </div>
                
                <div class="form-group">
                    <label>Рейтинг ATP</label>
                    <input type="number" id="p2Rating" placeholder="Например: 2" min="1" max="2000">
                </div>
                
                <div class="form-group">
                    <label>Процент побед (%)</label>
                    <input type="number" id="p2WinRate" placeholder="Например: 79" min="0" max="100">
                </div>
                
                <div class="form-group">
                    <label>Победы на покрытии (%)</label>
                    <input type="number" id="p2SurfaceRate" placeholder="Например: 75" min="0" max="100">
                </div>
                
                <div class="form-group">
                    <label>Текущая форма (0-100)</label>
                    <input type="number" id="p2Form" placeholder="Например: 82" min="0" max="100">
                </div>
                
                <div class="form-group">
                    <label>Победы в личных встречах</label>
                    <input type="number" id="p2H2H" placeholder="Например: 3" min="0">
                </div>
                
                <div class="form-group">
                    <label>Статус травмы</label>
                    <select id="p2Injury">
                        <option value="healthy">Здоров</option>
                        <option value="questionable">Под вопросом</option>
                        <option value="injured">Травмирован</option>
                    </select>
                </div>
                
                <div class="form-group">
                    <label>Уровень усталости (0-100)</label>
                    <input type="number" id="p2Fatigue" placeholder="Например: 25" min="0" max="100" value="25">
                </div>
            </div>
            
            <div class="additional-info">
                <h4>📊 Дополнительная информация</h4>
                <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 15px;">
                    <div class="form-group">
                        <label>Тип покрытия</label>
                        <select id="surface">
                            <option value="hard">Хард</option>
                            <option value="clay">Грунт</option>
                            <option value="grass">Трава</option>
                            <option value="indoor">Indoor</option>
                        </select>
                    </div>
                    
                    <div class="form-group">
                        <label>Турнир</label>
                        <select id="tournament">
                            <option value="grand_slam">Большой шлем</option>
                            <option value="masters">Мастерс</option>
                            <option value="atp500">ATP 500</option>
                            <option value="atp250">ATP 250</option>
                        </select>
                    </div>
                    
                    <div class="form-group">
                        <label>Раунд</label>
                        <select id="round">
                            <option value="final">Финал</option>
                            <option value="semifinal">Полуфинал</option>
                            <option value="quarterfinal">Четвертьфинал</option>
                            <option value="early">Ранний раунд</option>
                        </select>
                    </div>
                </div>
            </div>
            
            <div class="additional-info" style="grid-column: 1 / -1; background: #e8f5e9; border-color: #4caf50;">
                <h4 style="color: #2e7d32;">💰 Коэффициенты букмекеров</h4>
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
            ⏳ Анализируем матч...
        </div>
        
        <div class="results" id="results">
            <h3>📈 Результаты анализа</h3>
            <div id="resultsContent"></div>
        </div>
    </div>
    
    <script>
        function loadFromUrl() {
            const url = document.getElementById('matchUrl').value;
            
            if (!url) {
                alert('Пожалуйста, вставьте ссылку на матч');
                return;
            }
            
            document.getElementById('loading').classList.add('show');
            
            // Имитация загрузки данных
            setTimeout(() => {
                document.getElementById('loading').classList.remove('show');
                
                // Здесь будет парсинг данных из URL
                // Пока заполняем тестовыми данными
                document.getElementById('p1Name').value = 'Новак Джокович';
                document.getElementById('p1Rating').value = '1';
                document.getElementById('p1WinRate').value = '83';
                document.getElementById('p1SurfaceRate').value = '80';
                document.getElementById('p1Form').value = '85';
                document.getElementById('p1H2H').value = '5';
                
                document.getElementById('p2Name').value = 'Карлос Алькарас';
                document.getElementById('p2Rating').value = '2';
                document.getElementById('p2WinRate').value = '79';
                document.getElementById('p2SurfaceRate').value = '75';
                document.getElementById('p2Form').value = '82';
                document.getElementById('p2H2H').value = '3';
                
                document.getElementById('p1Odds').value = '2.10';
                document.getElementById('p2Odds').value = '1.85';
                
                alert('✅ Данные загружены! Проверьте и нажмите "Анализировать"');
            }, 1500);
        }
        
        function analyzeMatch() {
            const p1Name = document.getElementById('p1Name').value || 'Игрок 1';
            const p2Name = document.getElementById('p2Name').value || 'Игрок 2';
            
            // Сбор данных
            const p1WinRate = parseFloat(document.getElementById('p1WinRate').value) / 100 || 0.5;
            const p2WinRate = parseFloat(document.getElementById('p2WinRate').value) / 100 || 0.5;
            
            const p1Rating = parseInt(document.getElementById('p1Rating').value) || 100;
            const p2Rating = parseInt(document.getElementById('p2Rating').value) || 100;
            
            const p1SurfaceRate = parseFloat(document.getElementById('p1SurfaceRate').value) / 100 || 0.5;
            const p2SurfaceRate = parseFloat(document.getElementById('p2SurfaceRate').value) / 100 || 0.5;
            
            const p1Form = parseFloat(document.getElementById('p1Form').value) / 100 || 0.5;
            const p2Form = parseFloat(document.getElementById('p2Form').value) / 100 || 0.5;
            
            const p1H2H = parseInt(document.getElementById('p1H2H').value) || 0;
            const p2H2H = parseInt(document.getElementById('p2H2H').value) || 0;
            
            const p1Fatigue = parseFloat(document.getElementById('p1Fatigue').value) / 100 || 0;
            const p2Fatigue = parseFloat(document.getElementById('p2Fatigue').value) / 100 || 0;
            
            const p1Injury = document.getElementById('p1Injury').value;
            const p2Injury = document.getElementById('p2Injury').value;
            
            const p1Odds = parseFloat(document.getElementById('p1Odds').value) || 0;
            const p2Odds = parseFloat(document.getElementById('p2Odds').value) || 0;
            
            // Расчет силы игроков
            let p1Strength = p1WinRate * 0.3 + 
                            (1 - p1Rating / 100) * 0.2 + 
                            p1SurfaceRate * 0.2 + 
                            p1Form * 0.2 + 
                            (p1H2H / (p1H2H + p2H2H || 1)) * 0.1;
            
            let p2Strength = p2WinRate * 0.3 + 
                            (1 - p2Rating / 100) * 0.2 + 
                            p2SurfaceRate * 0.2 + 
                            p2Form * 0.2 + 
                            (p2H2H / (p1H2H + p2H2H || 1)) * 0.1;
            
            // Штрафы за травмы
            if (p1Injury === 'injured') p1Strength *= 0.7;
            else if (p1Injury === 'questionable') p1Strength *= 0.85;
            
            if (p2Injury === 'injured') p2Strength *= 0.7;
            else if (p2Injury === 'questionable') p2Strength *= 0.85;
            
            // Штрафы за усталость
            p1Strength *= (1 - p1Fatigue * 0.1);
            p2Strength *= (1 - p2Fatigue * 0.1);
            
            // Вероятности
            const p1Prob = (p1Strength / (p1Strength + p2Strength)) * 100;
            const p2Prob = 100 - p1Prob;
            
            // Справедливые коэффициенты
            const fairP1Odds = (100 / p1Prob).toFixed(2);
            const fairP2Odds = (100 / p2Prob).toFixed(2);
            
            // Поиск value bets
            let valueBet = '';
            if (p1Odds > fairP1Odds) {
                valueBet = `💰 Value bet: ${p1Name} (коэф. ${p1Odds} vs справедливый ${fairP1Odds})`;
            } else if (p2Odds > fairP2Odds) {
                valueBet = `💰 Value bet: ${p2Name} (коэф. ${p2Odds} vs справедливый ${fairP2Odds})`;
            } else {
                valueBet = 'Нет value bets';
            }
            
            // Рекомендация
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
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return HTML_PAGE

@app.route('/api/analyze', methods=['POST'])
def analyze():
    try:
        data = request.json
        return jsonify({'success': True, 'data': data})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

app = app