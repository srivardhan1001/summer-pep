document.addEventListener('DOMContentLoaded', () => {

  // Weather Background & Canvas Particle System
  const canvas = document.getElementById('weatherParticlesCanvas');
  let ctx = canvas ? canvas.getContext('2d') : null;
  let animationFrameId = null;
  let particles = [];
  let currentWeatherMode = 'default';

  function resizeCanvas() {
    if (!canvas) return;
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
  }

  if (canvas) {
    resizeCanvas();
    window.addEventListener('resize', resizeCanvas);
  }

  // Particle Generators
  function initParticles(mode) {
    currentWeatherMode = mode;
    particles = [];
    if (!canvas || !ctx) return;

    const count = mode === 'rain' ? 120 : (mode === 'snow' ? 80 : (mode === 'night' ? 70 : 40));

    for (let i = 0; i < count; i++) {
      particles.push({
        x: Math.random() * canvas.width,
        y: Math.random() * canvas.height,
        radius: Math.random() * (mode === 'snow' ? 3 : 2) + 1,
        length: Math.random() * 20 + 10,
        speedY: mode === 'rain' ? Math.random() * 10 + 12 : (mode === 'snow' ? Math.random() * 1.5 + 0.5 : Math.random() * 0.5 - 0.25),
        speedX: mode === 'snow' ? Math.random() * 1 - 0.5 : Math.random() * 0.4 - 0.2,
        alpha: Math.random() * 0.7 + 0.3,
        twinkleSpeed: Math.random() * 0.03 + 0.01
      });
    }
  }

  function renderParticles() {
    if (!canvas || !ctx) return;
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    const isNight = document.documentElement.getAttribute('data-bs-theme') === 'dark';

    if (currentWeatherMode === 'rain' || currentWeatherMode === 'thunderstorm') {
      ctx.strokeStyle = isNight ? 'rgba(186, 230, 253, 0.4)' : 'rgba(56, 189, 248, 0.5)';
      ctx.lineWidth = 1.5;
      particles.forEach(p => {
        ctx.beginPath();
        ctx.moveTo(p.x, p.y);
        ctx.lineTo(p.x + p.speedX * 2, p.y + p.length);
        ctx.stroke();

        p.y += p.speedY;
        p.x += p.speedX;
        if (p.y > canvas.height) {
          p.y = -20;
          p.x = Math.random() * canvas.width;
        }
      });

      // Occasional Thunderstorm Flash
      if (currentWeatherMode === 'thunderstorm' && Math.random() < 0.008) {
        ctx.fillStyle = 'rgba(255, 255, 255, 0.18)';
        ctx.fillRect(0, 0, canvas.width, canvas.height);
      }

    } else if (currentWeatherMode === 'snow') {
      ctx.fillStyle = '#ffffff';
      particles.forEach(p => {
        ctx.beginPath();
        ctx.arc(p.x, p.y, p.radius, 0, Math.PI * 2);
        ctx.fill();

        p.y += p.speedY;
        p.x += Math.sin(p.y * 0.02) * 0.5;
        if (p.y > canvas.height) {
          p.y = -10;
          p.x = Math.random() * canvas.width;
        }
      });

    } else if (isNight) {
      // Twinkling Starfield & Shooting Stars
      particles.forEach(p => {
        p.alpha += p.twinkleSpeed;
        if (p.alpha > 1 || p.alpha < 0.2) p.twinkleSpeed = -p.twinkleSpeed;

        ctx.fillStyle = `rgba(255, 255, 255, ${Math.abs(p.alpha)})`;
        ctx.beginPath();
        ctx.arc(p.x, p.y, p.radius, 0, Math.PI * 2);
        ctx.fill();
      });

      // Shooting star occasionally
      if (Math.random() < 0.005) {
        const startX = Math.random() * canvas.width * 0.8;
        const startY = Math.random() * canvas.height * 0.3;
        ctx.strokeStyle = 'rgba(255, 255, 255, 0.7)';
        ctx.lineWidth = 2;
        ctx.beginPath();
        ctx.moveTo(startX, startY);
        ctx.lineTo(startX + 80, startY + 40);
        ctx.stroke();
      }

    } else {
      // Warm Sunny Light Particles
      ctx.fillStyle = 'rgba(251, 191, 36, 0.25)';
      particles.forEach(p => {
        ctx.beginPath();
        ctx.arc(p.x, p.y, p.radius * 2, 0, Math.PI * 2);
        ctx.fill();

        p.y += p.speedY;
        p.x += p.speedX;

        if (p.y < 0 || p.y > canvas.height) p.speedY = -p.speedY;
        if (p.x < 0 || p.x > canvas.width) p.speedX = -p.speedX;
      });
    }

    animationFrameId = requestAnimationFrame(renderParticles);
  }

  // Update Body Background and Canvas Mode
  window.updateWeatherBackground = function(condition) {
    const body = document.getElementById('appBody');
    if (!body) return;

    body.classList.remove('weather-bg-default', 'weather-bg-sunny', 'weather-bg-rain', 'weather-bg-clouds', 'weather-bg-snow', 'weather-bg-thunderstorm');

    let mode = 'default';
    if (condition) {
      const c = condition.toLowerCase();
      if (c.includes('clear') || c.includes('sun')) {
        body.classList.add('weather-bg-sunny');
        mode = 'sunny';
      } else if (c.includes('rain') || c.includes('drizzle')) {
        body.classList.add('weather-bg-rain');
        mode = 'rain';
      } else if (c.includes('cloud')) {
        body.classList.add('weather-bg-clouds');
        mode = 'clouds';
      } else if (c.includes('snow')) {
        body.classList.add('weather-bg-snow');
        mode = 'snow';
      } else if (c.includes('thunder') || c.includes('lightning')) {
        body.classList.add('weather-bg-thunderstorm');
        mode = 'thunderstorm';
      } else {
        body.classList.add('weather-bg-default');
      }
    } else {
      body.classList.add('weather-bg-default');
    }

    if (canvas) {
      if (animationFrameId) cancelAnimationFrame(animationFrameId);
      initParticles(mode);
      renderParticles();
    }
  };

  // Trigger initial background mode
  const currentCondition = window.CURRENT_WEATHER_CONDITION || (document.getElementById('dashboardCityTitle') ? 'clear' : null);
  window.updateWeatherBackground(currentCondition);

});
