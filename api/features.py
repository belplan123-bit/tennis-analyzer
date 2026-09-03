def load_additional_features():
    """Загрузка дополнительных функций"""
    return {
        'html': """
        <div style="margin-top: 15px;">
            <h5>📊 Дополнительные инструменты:</h5>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 10px; margin-top: 10px;">
                <button onclick="showHistory()" style="padding: 10px; background: #667eea; color: white; border: none; border-radius: 5px; cursor: pointer;">
                    📜 История матчей
                </button>
                <button onclick="showAnalytics()" style="padding: 10px; background: #667eea; color: white; border: none; border-radius: 5px; cursor: pointer;">
                    📈 Аналитика
                </button>
                <button onclick="showLearning()" style="padding: 10px; background: #667eea; color: white; border: none; border-radius: 5px; cursor: pointer;">
                    🧠 Самообучение
                </button>
            </div>
        </div>
        
        <script>
            function showHistory() {
                fetch('/api/history')
                .then(response => response.json())
                .then(data => {
                    if (data.success && data.history) {
                        let html = '<h5>📜 История матчей:</h5>';
                        data.history.forEach(match => {
                            html += `
                                <div style="background: white; padding: 10px; margin: 5px 0; border-radius: 5px;">
                                    <p><strong>${match.player1.name}</strong> vs <strong>${match.player2.name}</strong></p>
                                    <p>Прогноз: ${match.predicted_winner} (${match.prediction_confidence}%)</p>
                                    ${match.actual_winner ? `<p>Результат: ${match.actual_winner} ${match.was_correct ? '✅' : '❌'}</p>` : ''}
                                </div>
                            `;
                        });
                        alert(html);
                    }
                });
            }
            
            function showAnalytics() {
                fetch('/api/analytics')
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        alert(`📈 Аналитика:\\nВсего матчей: ${data.analytics.total_matches || 0}\\nЗавершено: ${data.analytics.completed_matches || 0}\\nТочность: ${data.analytics.accuracy || 0}%`);
                    }
                });
            }
            
            function showLearning() {
                fetch('/api/learning')
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        alert(`🧠 Самообучение:\\nОшибок проанализировано: ${data.errors ? data.errors.length : 0}`);
                    }
                });
            }
        </script>
        """
    }