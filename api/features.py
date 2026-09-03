# Дополнительные функции для сайта
# Добавляйте новые функции сюда, не трогая index.py

def load_additional_features():
    """Загрузка дополнительных функций"""
    return {
        'html': """
        <div style="margin-top: 15px;">
            <h5>📊 Дополнительные инструменты:</h5>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 10px; margin-top: 10px;">
                <button onclick="alert('Функция в разработке')" style="padding: 10px; background: #667eea; color: white; border: none; border-radius: 5px; cursor: pointer;">
                    📈 История ставок
                </button>
                <button onclick="alert('Функция в разработке')" style="padding: 10px; background: #667eea; color: white; border: none; border-radius: 5px; cursor: pointer;">
                    📊 Графики формы
                </button>
                <button onclick="alert('Функция в разработке')" style="padding: 10px; background: #667eea; color: white; border: none; border-radius: 5px; cursor: pointer;">
                    🏆 Турниры
                </button>
            </div>
        </div>
        """
    }