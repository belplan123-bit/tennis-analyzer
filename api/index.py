from flask import Flask, request, jsonify

app = Flask(__name__)

# HTML страница прямо в коде
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
            font-family: Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 800px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            padding: 30px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
        }
        
        h1 {
            text-align: center;
            color: #667eea;
            margin-bottom: 10px;
        }
        
        .subtitle {
            text-align: center;
            color: #666;
            margin-bottom: 30px;
        }
        
        .players {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .player-card {
            background: #f5f5f5;
            padding: 20px;
            border-radius: 10px;
        }
        
        .player-card h3 {
            color: #667eea;
            margin-bottom: 15px;
        }
        
        input {
            width: 100%;
            padding: 10px;
            margin-bottom: 10px;
            border: 2px solid #ddd;
            border-radius: 5px;
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
        }
        
        @media (max-width: 600px) {
            .players { grid-template-columns: 1fr; }
            .container { padding: 15px; }
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🎾 Теннис Анализатор</h1>
        <p class="subtitle">Профессиональный анализ теннисных матчей</p>
        
        <div class="players">
            <div class="player-card">
                <h3>Игрок 1</h3>
                <input type="text" id="p1Name" placeholder="Имя игрока" value="Новак Джокович">
                <input type="number" id="p1Rating" placeholder="Рейтинг ATP" value="1">
                <input type="number" id="p1WinRate" placeholder="Процент побед (%)" value="83">
                <input type="number" id="p1Form" placeholder="Текущая форма (0-100)" value="85">
            </div>
            
            <div class="player-card">
                <h3>Игрок 2</h3>
                <input type="text" id="p2Name" placeholder="Имя игрока" value="Карлос Алькарас">
                <input type="number" id="p2Rating" placeholder="Рейтинг ATP" value="2">
                <input type="number" id="p2WinRate" placeholder="Процент побед (%)" value="79">
                <input type="number" id="p2Form" placeholder="Текущая форма (0-100)" value="82">
            </div>
        </div>
        
        <button class="btn" onclick="analyzeMatch()">Анализировать матч</button>
        
        <div class="results" id="results">
            <h3>📊 Результаты анализа</h3>
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
            
            const p1Strength = p1WinRate * 0.5 + (1 - p1Rating / 100) * 0.3 + p1Form * 0.2;
            const p2Strength = p2WinRate * 0.5 + (1 - p2Rating / 100) * 0.3 + p2Form * 0.2;
            
            const p1Prob = (p1Strength / (p1Strength + p2Strength)) * 100;
            const p2Prob = 100 - p1Prob;
            
            const p1Odds = (100 / p1Prob).toFixed(2);
            const p2Odds = (100 / p2Prob).toFixed(2);
            
            const recommendation = p1Prob > p2Prob ? p1Name : p2Name;
            
            document.getElementById('resultsContent').innerHTML = `
                <h4>Вероятность победы:</h4>
                <p>${p1Name}: <strong>${p1Prob.toFixed(1)}%</strong> (коэф. ${p1Odds})</p>
                <div class="probability-bar">
                    <div class="probability-fill" style="width: ${p1Prob}%"></div>
                </div>
                <p>${p2Name}: <strong>${p2Prob.toFixed(1)}%</strong> (коэф. ${p2Odds})</p>
                <div class="probability-bar">
                    <div class="probability-fill" style="width: ${p2Prob}%"></div>
                </div>
                <div style="margin-top: 20px; padding: 15px; background: #e8f5e9; border-radius: 10px;">
                    <h4>💡 Рекомендация:</h4>
                    <p>Ставка на победу: <strong>${recommendation}</strong></p>
                </div>
            `;
            
            document.getElementById('results').classList.add('show');
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

# Для Vercel
app = app