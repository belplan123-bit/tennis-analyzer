// Глобальные переменные
let charts = {};

// Функция для создания графика
function createChart(canvasId, chartType, labels, data, options = {}) {
    const ctx = document.getElementById(canvasId).getContext('2d');
    
    // Уничтожаем существующий график, если есть
    if (charts[canvasId]) {
        charts[canvasId].destroy();
    }
    
    const defaultOptions = {
        responsive: true,
        maintainAspectRatio: false,
        animation: {
            duration: 1000,
            easing: 'easeInOutQuart'
        }
    };
    
    const chartOptions = {...defaultOptions, ...options};
    
    charts[canvasId] = new Chart(ctx, {
        type: chartType,
        data: {
            labels: labels,
            datasets: [{
                data: data,
                backgroundColor: [
                    'rgba(102, 126, 234, 0.7)',
                    'rgba(118, 75, 162, 0.7)',
                    'rgba(255, 99, 132, 0.7)',
                    'rgba(75, 192, 192, 0.7)',
                    'rgba(255, 206, 86, 0.7)'
                ],
                borderColor: [
                    'rgba(102, 126, 234, 1)',
                    'rgba(118, 75, 162, 1)',
                    'rgba(255, 99, 132, 1)',
                    'rgba(75, 192, 192, 1)',
                    'rgba(255, 206, 86, 1)'
                ],
                borderWidth: 2
            }]
        },
        options: chartOptions
    });
    
    return charts[canvasId];
}

// Функция для форматирования чисел
function formatNumber(number, decimals = 2) {
    return Number(number).toFixed(decimals);
}

// Функция для отображения уведомлений
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} notification`;
    notification.innerHTML = message;
    notification.style.position = 'fixed';
    notification.style.top = '20px';
    notification.style.right = '20px';
    notification.style.zIndex = '9999';
    notification.style.minWidth = '300px';
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.remove();
    }, 3000);
}

// Функция для загрузки данных ATP игроков
async function loadATPPlayers() {
    try {
        const response = await fetch('/api/atp/players');
        const players = await response.json();
        return players;
    } catch (error) {
        console.error('Ошибка загрузки игроков:', error);
        return [];
    }
}

// Функция для автозаполнения полей игрока
function autofillPlayer(playerSelect, playerData) {
    const player = playerData.find(p => p.name === playerSelect.value);
    
    if (player) {
        document.getElementById(`${playerSelect.id.replace('Select', 'Name')}`).value = player.name;
        document.getElementById(`${playerSelect.id.replace('Select', 'Rating')}`).value = player.rating;
        document.getElementById(`${playerSelect.id.replace('Select', 'WinRate')}`).value = player.win_rate * 100;
        document.getElementById(`${playerSelect.id.replace('Select', 'SurfaceWinRate')}`).value = player.surface_win_rate * 100;
        document.getElementById(`${playerSelect.id.replace('Select', 'Form')}`).value = player.recent_form * 100;
    }
}

// Обработчик загрузки страницы
document.addEventListener('DOMContentLoaded', function() {
    // Инициализация tooltip'ов
    if (typeof bootstrap !== 'undefined') {
        const tooltips = document.querySelectorAll('[data-bs-toggle="tooltip"]');
        tooltips.forEach(tooltip => new bootstrap.Tooltip(tooltip));
    }
    
    // Добавление обработчиков для динамических элементов
    const urlInput = document.getElementById('matchUrl');
    if (urlInput) {
        urlInput.addEventListener('paste', function(e) {
            setTimeout(() => {
                const url = e.target.value;
                if (url) {
                    showNotification('Ссылка вставлена. Нажмите "Загрузить" для анализа', 'success');
                }
            }, 100);
        });
    }
});

// Функция для экспорта результатов
function exportResults(format = 'json') {
    const results = document.getElementById('resultsBody');
    if (!results) return;
    
    const data = results.innerHTML;
    
    if (format === 'json') {
        const blob = new Blob([JSON.stringify(data)], {type: 'application/json'});
        downloadBlob(blob, 'analysis_results.json');
    } else if (format === 'html') {
        const blob = new Blob([data], {type: 'text/html'});
        downloadBlob(blob, 'analysis_results.html');
    }
}

// Функция для скачивания файла
function downloadBlob(blob, filename) {
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}