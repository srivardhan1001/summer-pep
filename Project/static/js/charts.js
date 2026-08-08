document.addEventListener('DOMContentLoaded', () => {

  if (!window.WEATHER_DAILY_DATA || !Array.isArray(window.WEATHER_DAILY_DATA) || window.WEATHER_DAILY_DATA.length === 0) {
    return;
  }

  const daily = window.WEATHER_DAILY_DATA;
  const labels = daily.map(d => `${d.day} (${d.date})`);

  let tempChart, humidityChart, windChart;

  function isDarkMode() {
    return document.documentElement.getAttribute('data-bs-theme') === 'dark';
  }

  function getColors() {
    const dark = isDarkMode();
    return {
      text: dark ? '#94a3b8' : '#475569',
      grid: dark ? 'rgba(255, 255, 255, 0.08)' : 'rgba(0, 0, 0, 0.06)',
      primary: '#60a5fa',
      info: '#22d3ee',
      warning: '#fbbf24',
      danger: '#f87171'
    };
  }

  function createGradient(ctx, colorStart, colorEnd) {
    const gradient = ctx.createLinearGradient(0, 0, 0, 300);
    gradient.addColorStop(0, colorStart);
    gradient.addColorStop(1, colorEnd);
    return gradient;
  }

  function renderCharts() {
    const colors = getColors();

    const chartOptions = {
      responsive: true,
      maintainAspectRatio: false,
      animation: {
        duration: 1200,
        easing: 'easeOutQuart'
      },
      plugins: {
        legend: {
          labels: { color: colors.text, font: { family: 'Poppins', size: 13, weight: '500' } }
        },
        tooltip: {
          backgroundColor: 'rgba(15, 23, 42, 0.85)',
          titleColor: '#f8fafc',
          bodyColor: '#cbd5e1',
          padding: 14,
          cornerRadius: 12,
          borderWidth: 1,
          borderColor: 'rgba(255,255,255,0.15)',
          titleFont: { family: 'Poppins', size: 14, weight: 'bold' },
          bodyFont: { family: 'Poppins', size: 13 }
        }
      },
      scales: {
        x: {
          grid: { color: colors.grid },
          ticks: { color: colors.text, font: { family: 'Poppins' } }
        },
        y: {
          grid: { color: colors.grid },
          ticks: { color: colors.text, font: { family: 'Poppins' } }
        }
      }
    };

    // 1. Temperature Chart
    const tempCanvas = document.getElementById('tempChart');
    if (tempCanvas) {
      const ctx = tempCanvas.getContext('2d');
      const maxGradient = createGradient(ctx, 'rgba(239, 68, 68, 0.35)', 'rgba(239, 68, 68, 0.0)');
      const minGradient = createGradient(ctx, 'rgba(59, 130, 246, 0.35)', 'rgba(59, 130, 246, 0.0)');

      if (tempChart) tempChart.destroy();
      tempChart = new Chart(ctx, {
        type: 'line',
        data: {
          labels: labels,
          datasets: [
            {
              label: 'Max Temp (°C)',
              data: daily.map(d => d.max_temp),
              borderColor: '#f87171',
              backgroundColor: maxGradient,
              tension: 0.45,
              fill: true,
              pointRadius: 6,
              pointHoverRadius: 9,
              pointBackgroundColor: '#f87171'
            },
            {
              label: 'Min Temp (°C)',
              data: daily.map(d => d.min_temp),
              borderColor: '#60a5fa',
              backgroundColor: minGradient,
              tension: 0.45,
              fill: true,
              pointRadius: 6,
              pointHoverRadius: 9,
              pointBackgroundColor: '#60a5fa'
            }
          ]
        },
        options: chartOptions
      });
    }

    // 2. Humidity Chart
    const humCanvas = document.getElementById('humidityChart');
    if (humCanvas) {
      const ctx = humCanvas.getContext('2d');
      const humGradient = createGradient(ctx, 'rgba(34, 211, 238, 0.4)', 'rgba(34, 211, 238, 0.05)');

      if (humidityChart) humidityChart.destroy();
      humidityChart = new Chart(ctx, {
        type: 'bar',
        data: {
          labels: labels,
          datasets: [{
            label: 'Humidity (%)',
            data: daily.map(d => d.humidity),
            backgroundColor: humGradient,
            borderColor: colors.info,
            borderWidth: 2,
            borderRadius: 12
          }]
        },
        options: chartOptions
      });
    }

    // 3. Wind Speed Chart
    const windCanvas = document.getElementById('windChart');
    if (windCanvas) {
      const ctx = windCanvas.getContext('2d');
      const windGradient = createGradient(ctx, 'rgba(251, 191, 36, 0.4)', 'rgba(251, 191, 36, 0.0)');

      if (windChart) windChart.destroy();
      windChart = new Chart(ctx, {
        type: 'line',
        data: {
          labels: labels,
          datasets: [{
            label: 'Wind Speed (km/h)',
            data: daily.map(d => d.wind_speed),
            borderColor: colors.warning,
            backgroundColor: windGradient,
            tension: 0.45,
            fill: true,
            pointRadius: 6,
            pointHoverRadius: 9,
            pointBackgroundColor: colors.warning
          }]
        },
        options: chartOptions
      });
    }
  }

  // Initial Chart Render
  renderCharts();

  window.updateChartColors = function() {
    renderCharts();
  };

  const chartTabs = document.querySelectorAll('#chartTabs button');
  chartTabs.forEach(tab => {
    tab.addEventListener('shown.bs.tab', () => {
      if (tempChart) tempChart.resize();
      if (humidityChart) humidityChart.resize();
      if (windChart) windChart.resize();
    });
  });

});
