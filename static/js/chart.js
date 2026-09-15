const serverName = window.CHART_SERVER_NAME;

fetch('/api/server/' + serverName + '/storage_info')
    .then(function(response) { return response.json(); })
    .then(function(data) {
        if (data.error) {
            alert(data.error);
            return;
        }

        document.getElementById('title').innerText = 'PCSMT2 | ' + serverName + '的存储占用图表';

        const ctx = document.getElementById('storageChart').getContext('2d');
        new Chart(ctx, {
            type: 'line',
            data: {
                labels: data.labels,
                datasets: [{
                    label: '存储大小 (' + data.type + ')',
                    data: data.values,
                    borderColor: 'rgb(60, 143, 232)',
                    borderWidth: 2,
                    tension: 0
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    title: {
                        display: true,
                        text: data.title
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            callback: function(value) {
                                return value + ' ' + data.type;
                            }
                        }
                    }
                }
            }
        });
    })
    .catch(function(error) {
        console.error('Error fetching data:', error);
        alert('无法获取存储数据');
    });