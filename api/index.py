from flask import Flask, request, jsonify

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
            max-width: 900px;
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
        
        input {
            width: 100%;
            padding: 12px;
            border: 2px solid #ddd;
            border-radius: 8px;
            font-size: 14px;
            transition: border-color 0.3s;
        }
        
        input:focus {
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
        
        @media (max-width: 600px) {
            .players { grid-template-columns: 1fr; }
            .container { padding: 15px; }
            h1 { font-size: 1.5em; }
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🎾 Теннис Анализатор</h1>
        <p class="subtitle">Профессиональный анализ теннисных матчей</p>
        
        <div class="players">
            <div class="player-card">
                <h3>👤 Игрок 1</h3>
                
                <div class="form-group">
                    <label>Имя игрока</label>
                    <input type="text" id="p1Name" placeholder="Например: Новак Джокович" value="Новак Джокович">
                </div>
                
                <div class="form-group">
                    <label>Рейтинг ATP (1-100)</label>
                    <input type="number" id="p1Rating" placeholder="Например: 1" value="1" min="1" max="100">
                </div>
                
                <div class="form-group">
                    <label>Процент побед (%)</label>
                    <input type="number" id="p1WinRate" placeholder="Например: 83" value="83" min="0" max="100">
                </div>
                
                <div class="form-group">
                    <label>Текущая форма (0-100)</label>
                    <input type="number" id="p1Form" placeholder="Например: 85" value="85" min="0" max="100">
                </div>
            </div>
            
            <div class="player-card">
                <h3>👤 Игрок 2</h3>
                
                <div class="form-group">
                    <label>Имя игрока</label>
                    <input type="text" id="p2Name" placeholder="Например: Карлос Алькарас" value="Карлос Алькарас">
                </div>
                
                <div class="form-group">
                    <label>Рейтинг ATP (1-100)</label>
                    <input type="number" id="p2Rating" placeholder="Например: 2" value="2" min="1" max="100">
                </div>
                
                <div class="form-group">
                    <label>Процент побед (%)</label>
                    <input type="number" id="p2WinRate" placeholder="Например: 79" value="79" min="0" max="100">
                </div>
                
                <div class="form-group">
                    <label>Текущая форма (0-100)</label>
                    <input type="number" id="p2Form" placeholder="Например: 82" value="82" min="0" max="100">
                </div>
            </div>
        </div>
        
        <button class="btn" onclick="analyzeMatch()">📊 Анализировать матч</button>
        
        <div class="results" id="results">
            <h3>📈 Результаты анализа</h3>
            <div id="resultsContent"></div>
        </div>
    </div>
    
    <script>
        function analyzeMatch() {
            const p1Name = document.getElementById('p1Name').value || 'Игрок 1';
            const p2Name = document.getElementById('p2Name').value || 'Игрок 2';
            
            const p1WinRate = parseFloat(document.getElementById('p1WinRate').value) / 100 || 0.5;
            const p2WinRate = parseFloat(document.getElementById('p2WinRate').value) / 100 || 0.5;
            
            const p1Rating = parseInt(document.getElementById('p1Rating').value) || 100;
            const p2Rating = parseInt(document.getElementById('p2Rating').value) || 100;
            
            const p1Form = parseFloat(document.getElementById('p1Form').value) / 100 || 0.5;
            const p2Form = parseFloat(document.getElementById('p2Form').value) / 100 || 0.5;
            
            // Расчет силы игроков
            const p1Strength = p1WinRate * 0.5 + (1 - p1Rating / 100) * 0.3 + p1Form * 0.2;
            const p2Strength = p2WinRate * 0.5 + (1 - p2Rating / 100) * 0.3 + p2Form * 0.2;
            
            // Вероятности
            const p1Prob = (p1Strength / (p1Strength + p2Strength)) * 100;
            const p2Prob = 100 - p1Prob;
            
            // Коэффициенты
            const p1Odds = (100 / p1Prob).toFixed(2);
            const p2Odds = (100 / p2Prob).toFixed(2);
            
            // Рекомендация
            const recommendation = p1Prob > p2Prob ? p1Name : p2Name;
            const recommendationProb = Math.max(p1Prob, p2Prob);
            
            document.getElementById('resultsContent').innerHTML = `
                <div style="margin-bottom: 20px;">
                    <h4>🎯 Вероятность победы:</h4>
                    <div style="margin: 15px 0;">
                        <p><strong>${p1Name}</strong>: ${p1Prob.toFixed(1)}% (коэф. ${p1Odds})</p>
                        <div class="probability-bar">
                            <div class="probability-fill" style="width: ${p1Prob}%"></div>
                        </div>
                    </div>
                    <div style="margin: 15px 0;">
                        <p><strong>${p2Name}</strong>: ${p2Prob.toFixed(1)}% (коэф. ${p2Odds})</p>
                        <div class="probability-bar">
                            <div class="probability-fill" style="width: ${p2Prob}%"></div>
                        </div>
                    </div>
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