document.addEventListener('DOMContentLoaded', () => {

  // ------------------------------------------------------------------ //
  //  CSRF token helper                                                  //
  //  Reads the token from the <meta name="csrf-token"> tag injected by  //
  //  base.html.  All non-GET fetch() calls include this as the          //
  //  X-CSRFToken header so Flask-WTF accepts them.                      //
  // ------------------------------------------------------------------ //
  function getCsrfToken() {
    const meta = document.querySelector('meta[name="csrf-token"]');
    return meta ? meta.getAttribute('content') : '';
  }

  // Page Entrance Loader Fade Out
  const loader = document.getElementById('pageLoaderScreen');
  if (loader) {
    setTimeout(() => {
      loader.classList.add('fade-out');
      // Set display:none immediately alongside the CSS fade so there is
      // zero window where the element is invisible yet still intercepting
      // pointer events at z-index 10000.
      setTimeout(() => {
        loader.style.display = 'none';
      }, 650); // slightly longer than the 0.6s CSS transition
    }, 900);
  }

  // Global Spinner Helper
  window.showSpinner = function() {
    const spinner = document.getElementById('globalSpinner');
    if (spinner) spinner.classList.remove('d-none');
  };

  window.hideSpinner = function() {
    const spinner = document.getElementById('globalSpinner');
    if (spinner) spinner.classList.add('d-none');
  };

  // Real-Time Live Clock Ticker
  const clockEl = document.getElementById('liveClock');
  if (clockEl) {
    function updateClock() {
      const now = new Date();
      clockEl.textContent = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: true });
    }
    updateClock();
    setInterval(updateClock, 1000);
  }

  // Number Count-Up Animation
  function animateCountUp(el) {
    const target = parseFloat(el.dataset.count);
    if (isNaN(target)) return;

    const duration = 1200; // ms
    const startTime = performance.now();
    const isFloat = el.dataset.float === 'true';

    function updateNumber(currentTime) {
      const elapsed = currentTime - startTime;
      const progress = Math.min(elapsed / duration, 1);
      const easeProgress = 1 - Math.pow(1 - progress, 3); // Ease Out Cubic
      const currentVal = target * easeProgress;

      el.textContent = isFloat ? currentVal.toFixed(1) : Math.round(currentVal);

      if (progress < 1) {
        requestAnimationFrame(updateNumber);
      } else {
        el.textContent = isFloat ? target.toFixed(1) : target;
      }
    }

    requestAnimationFrame(updateNumber);
  }

  document.querySelectorAll('.count-up').forEach(el => animateCountUp(el));

  // Staggered Scroll Reveal Observer
  const revealElements = document.querySelectorAll('.reveal-on-scroll');
  if ('IntersectionObserver' in window && revealElements.length > 0) {
    const observer = new IntersectionObserver((entries) => {
      entries.forEach((entry, idx) => {
        if (entry.isIntersecting) {
          setTimeout(() => {
            entry.target.classList.add('is-visible');
          }, idx * 100);
          observer.unobserve(entry.target);
        }
      });
    }, { threshold: 0.1 });

    revealElements.forEach(el => observer.observe(el));
  } else {
    revealElements.forEach(el => el.classList.add('is-visible'));
  }

  // Mouse Parallax 3D Tilt Effect on Glass Cards
  document.querySelectorAll('.glass-card').forEach(card => {
    card.addEventListener('mousemove', (e) => {
      const rect = card.getBoundingClientRect();
      const x = e.clientX - rect.left;
      const y = e.clientY - rect.top;
      const centerX = rect.width / 2;
      const centerY = rect.height / 2;
      const rotateX = ((y - centerY) / centerY) * -4;
      const rotateY = ((x - centerX) / centerX) * 4;

      card.style.transform = `perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) translateY(-4px)`;
    });

    card.addEventListener('mouseleave', () => {
      card.style.transform = 'perspective(1000px) rotateX(0deg) rotateY(0deg) translateY(0px)';
    });
  });

  // Rotate Refresh Button Icon
  const refreshBtn = document.getElementById('refreshBtn');
  if (refreshBtn) {
    refreshBtn.addEventListener('click', () => {
      const icon = refreshBtn.querySelector('i');
      if (icon) icon.classList.add('fa-spin');
    });
  }

  // Browser Geolocation Handler
  const locateBtns = [document.getElementById('locationBtn'), document.getElementById('heroLocateBtn')].filter(Boolean);
  locateBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      if (!navigator.geolocation) {
        alert('Geolocation is not supported by your browser.');
        return;
      }
      showSpinner();
      navigator.geolocation.getCurrentPosition(
        (position) => {
          const lat = position.coords.latitude;
          const lon = position.coords.longitude;
          window.location.href = `/dashboard?lat=${lat}&lon=${lon}`;
        },
        (error) => {
          hideSpinner();
          let msg = 'Unable to retrieve location.';
          if (error.code === error.PERMISSION_DENIED) {
            msg = 'Location permission denied. Please allow browser location access.';
          }
          alert(msg);
        },
        { timeout: 10000 }
      );
    });
  });

  // Favorite Star Toggle Handler on Dashboard
  const favToggleBtn = document.getElementById('favToggleBtn');
  if (favToggleBtn) {
    favToggleBtn.addEventListener('click', async () => {
      const city = favToggleBtn.dataset.city;
      const country = favToggleBtn.dataset.country;
      const favStarIcon = document.getElementById('favStarIcon');

      try {
        const response = await fetch('/api/favorites/toggle', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCsrfToken(),
          },
          body: JSON.stringify({ city, country })
        });
        const res = await response.json();

        if (res.success) {
          if (res.is_favorite) {
            favStarIcon.className = 'fa-solid fa-star text-warning';
          } else {
            favStarIcon.className = 'fa-solid fa-star text-muted opacity-50';
          }
        }
      } catch (err) {
        console.error('Error toggling favorite:', err);
      }
    });
  }

  // Remove Favorite Handler on Favorites Page
  document.querySelectorAll('.btn-remove-fav').forEach(btn => {
    btn.addEventListener('click', async () => {
      const favId = btn.dataset.id;
      if (!confirm('Remove this city from favorites?')) return;
      try {
        const response = await fetch(`/api/favorites/${favId}`, {
          method: 'DELETE',
          headers: { 'X-CSRFToken': getCsrfToken() },
        });
        const res = await response.json();
        if (res.success) {
          const col = document.getElementById(`fav-card-col-${favId}`);
          if (col) col.remove();
        }
      } catch (err) {
        console.error('Error removing favorite:', err);
      }
    });
  });

  // Delete Individual Search History Row
  document.querySelectorAll('.btn-delete-history').forEach(btn => {
    btn.addEventListener('click', async () => {
      const historyId = btn.dataset.id;
      try {
        const response = await fetch(`/api/history/${historyId}`, {
          method: 'DELETE',
          headers: { 'X-CSRFToken': getCsrfToken() },
        });
        const res = await response.json();
        if (res.success) {
          const row = document.getElementById(`history-row-${historyId}`);
          if (row) row.remove();
        }
      } catch (err) {
        console.error('Error deleting history item:', err);
      }
    });
  });

  // Clear All Search History
  const clearHistoryBtn = document.getElementById('clearHistoryBtn');
  if (clearHistoryBtn) {
    clearHistoryBtn.addEventListener('click', async () => {
      if (!confirm('Are you sure you want to clear all search history?')) return;
      try {
        const response = await fetch('/api/history/clear', {
          method: 'DELETE',
          headers: { 'X-CSRFToken': getCsrfToken() },
        });
        const res = await response.json();
        if (res.success) {
          window.location.reload();
        }
      } catch (err) {
        console.error('Error clearing history:', err);
      }
    });
  }

  // City Comparison Modal Handler
  const compareForm = document.getElementById('compareForm');
  if (compareForm) {

    // ---- helpers ----
    const validationMsg  = document.getElementById('compareValidationMsg');
    const validationText = document.getElementById('compareValidationText');
    const resultsContainer = document.getElementById('compareResults');

    function showValidationError(msg) {
      validationText.textContent = msg;
      validationMsg.classList.remove('d-none');
    }
    function clearValidationError() {
      validationMsg.classList.add('d-none');
      validationText.textContent = '';
    }

    function getInputCities() {
      const c1 = (document.getElementById('compareCity1')?.value || '').trim();
      const c2 = (document.getElementById('compareCity2')?.value || '').trim();
      const c3 = (document.getElementById('compareCity3')?.value || '').trim();
      return [c1, c2, c3].filter(Boolean);  // drop empty strings
    }

    // AQI label helper (mirrors the backend mapping)
    function aqiLabel(index) {
      const labels = ['', 'Good', 'Fair', 'Moderate', 'Poor', 'Very Poor'];
      return labels[index] || 'N/A';
    }
    function aqiBadgeClass(index) {
      if (index <= 1) return 'bg-success-subtle text-success';
      if (index === 2) return 'bg-warning-subtle text-warning';
      return 'bg-danger-subtle text-danger';
    }

    // Build one rich comparison card
    function buildCompareCard(w) {
      const aqiIdx   = w.aqi?.index ?? '—';
      const aqiLbl   = w.aqi?.label ?? aqiLabel(aqiIdx);
      const aqiClass = aqiBadgeClass(w.aqi?.index ?? 0);

      return `
        <div class="col-12 col-md-6 col-xl-4">
          <div class="card compare-result-card h-100 border-0 shadow-sm">
            <!-- Card header: city + icon -->
            <div class="compare-card-header p-3 pb-0 d-flex justify-content-between align-items-start">
              <div>
                <h5 class="fw-extrabold mb-0 text-body">${escHtml(w.city)}</h5>
                <span class="badge bg-primary-subtle text-primary border border-primary-subtle rounded-pill px-2 py-1 small mt-1">
                  ${escHtml(w.country || '—')}
                </span>
              </div>
              <img src="https://openweathermap.org/img/wn/${escHtml(w.icon)}@2x.png"
                   alt="${escHtml(w.description)}" width="64" height="64"
                   class="compare-weather-icon">
            </div>

            <div class="compare-card-body p-3">
              <!-- Temperature block -->
              <div class="text-center py-2 mb-3 compare-temp-block rounded-4">
                <div class="display-5 fw-extrabold text-body lh-1">${w.temp}°<span class="fs-4 text-muted">C</span></div>
                <div class="text-muted small mt-1">Feels like <strong class="text-body">${w.feels_like}°C</strong></div>
                <div class="text-muted extra-small mt-1">
                  <span class="text-info me-2"><i class="fa-solid fa-temperature-arrow-down me-1"></i>${w.temp_min}°C</span>
                  <span class="text-danger"><i class="fa-solid fa-temperature-arrow-up me-1"></i>${w.temp_max}°C</span>
                </div>
                <div class="mt-2">
                  <span class="badge rounded-pill px-3 py-1 small fw-semibold bg-secondary-subtle text-body text-capitalize">
                    ${escHtml(w.description)}
                  </span>
                </div>
              </div>

              <!-- Metrics grid -->
              <div class="row g-2 compare-metrics">

                <div class="col-6">
                  <div class="compare-metric-box rounded-3 p-2 text-center">
                    <i class="fa-solid fa-droplet text-info small"></i>
                    <div class="extra-small text-muted">Humidity</div>
                    <div class="fw-bold text-body small">${w.humidity}%</div>
                  </div>
                </div>

                <div class="col-6">
                  <div class="compare-metric-box rounded-3 p-2 text-center">
                    <i class="fa-solid fa-wind text-primary small"></i>
                    <div class="extra-small text-muted">Wind</div>
                    <div class="fw-bold text-body small">${w.wind_speed} km/h</div>
                  </div>
                </div>

                <div class="col-6">
                  <div class="compare-metric-box rounded-3 p-2 text-center">
                    <i class="fa-solid fa-gauge-high text-warning small"></i>
                    <div class="extra-small text-muted">Pressure</div>
                    <div class="fw-bold text-body small">${w.pressure} hPa</div>
                  </div>
                </div>

                <div class="col-6">
                  <div class="compare-metric-box rounded-3 p-2 text-center">
                    <i class="fa-solid fa-eye text-success small"></i>
                    <div class="extra-small text-muted">Visibility</div>
                    <div class="fw-bold text-body small">${w.visibility} km</div>
                  </div>
                </div>

                <div class="col-6">
                  <div class="compare-metric-box rounded-3 p-2 text-center">
                    <i class="fa-solid fa-cloud text-secondary small"></i>
                    <div class="extra-small text-muted">Cloudiness</div>
                    <div class="fw-bold text-body small">${w.cloudiness}%</div>
                  </div>
                </div>

                <div class="col-6">
                  <div class="compare-metric-box rounded-3 p-2 text-center">
                    <i class="fa-solid fa-sun text-warning small"></i>
                    <div class="extra-small text-muted">UV Index</div>
                    <div class="fw-bold text-body small">${w.uv_index ?? '—'}</div>
                  </div>
                </div>

                <div class="col-6">
                  <div class="compare-metric-box rounded-3 p-2 text-center">
                    <i class="fa-solid fa-sun-plant-wilt text-warning small"></i>
                    <div class="extra-small text-muted">Sunrise</div>
                    <div class="fw-bold text-body small">${escHtml(w.sunrise || '—')}</div>
                  </div>
                </div>

                <div class="col-6">
                  <div class="compare-metric-box rounded-3 p-2 text-center">
                    <i class="fa-solid fa-moon text-primary small"></i>
                    <div class="extra-small text-muted">Sunset</div>
                    <div class="fw-bold text-body small">${escHtml(w.sunset || '—')}</div>
                  </div>
                </div>

              </div><!-- /metrics grid -->

              <!-- AQI footer badge -->
              <div class="text-center mt-3">
                <span class="badge ${aqiClass} rounded-pill px-3 py-1 fw-semibold">
                  <i class="fa-solid fa-smog me-1"></i> AQI ${aqiIdx} — ${escHtml(aqiLbl)}
                </span>
              </div>

              <!-- Link to full dashboard -->
              <div class="text-center mt-2">
                <a href="/dashboard?city=${encodeURIComponent(w.city)}"
                   class="btn btn-sm btn-outline-primary rounded-pill px-3 fw-semibold"
                   target="_blank">
                  Full Dashboard <i class="fa-solid fa-arrow-up-right-from-square ms-1"></i>
                </a>
              </div>
            </div><!-- /compare-card-body -->
          </div>
        </div>
      `;
    }

    // Escape HTML to prevent XSS in injected content
    function escHtml(str) {
      if (str == null) return '';
      return String(str)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;');
    }

    compareForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      clearValidationError();

      const cities = getInputCities();

      // Validation
      if (cities.length === 0) {
        showValidationError('Please enter at least two city names to compare.');
        return;
      }
      if (cities.length === 1) {
        showValidationError('Please enter at least two city names to compare.');
        return;
      }

      // Loading state
      resultsContainer.innerHTML = `
        <div class="col-12 text-center py-5">
          <div class="spinner-border text-primary mb-3" role="status" style="width:2.5rem;height:2.5rem;">
            <span class="visually-hidden">Loading...</span>
          </div>
          <p class="text-muted small fw-semibold">Fetching weather data for ${escHtml(cities.join(', '))}…</p>
        </div>
      `;

      try {
        const citiesParam = encodeURIComponent(cities.join(','));
        const response = await fetch(`/api/compare?cities=${citiesParam}`);

        if (!response.ok) {
          throw new Error(`Server responded with status ${response.status}`);
        }

        const res = await response.json();

        if (!res.success) {
          throw new Error(res.error || 'Unknown server error');
        }

        const data = res.comparison || [];

        if (data.length === 0) {
          resultsContainer.innerHTML = `
            <div class="col-12 text-center py-4">
              <i class="fa-solid fa-circle-xmark text-warning display-5 mb-3"></i>
              <h5 class="text-muted fw-semibold">No results returned</h5>
              <p class="text-muted small">Check the city names and try again. City names must be in English.</p>
            </div>
          `;
          return;
        }

        // Find failed cities (cities we asked for but got no result)
        const foundCities = data.map(w => w.city.toLowerCase());
        const notFound = cities.filter(c => !foundCities.some(f => f.includes(c.toLowerCase()) || c.toLowerCase().includes(f)));

        let html = data.map(buildCompareCard).join('');

        // Append a warning row for any cities that returned no data
        if (notFound.length > 0) {
          html += `
            <div class="col-12">
              <div class="alert glass-alert border-0 rounded-4 alert-warning small py-2 px-3 mb-0">
                <i class="fa-solid fa-triangle-exclamation me-1"></i>
                Could not find weather data for: <strong>${escHtml(notFound.join(', '))}</strong>. Check the spelling.
              </div>
            </div>
          `;
        }

        resultsContainer.innerHTML = html;

      } catch (err) {
        console.error('Comparison error:', err);
        resultsContainer.innerHTML = `
          <div class="col-12 text-center py-4">
            <i class="fa-solid fa-circle-xmark text-danger display-5 mb-3"></i>
            <h5 class="text-danger fw-semibold">Failed to fetch comparison data</h5>
            <p class="text-muted small">${escHtml(err.message)}</p>
            <button class="btn btn-outline-primary btn-sm rounded-pill px-4 mt-1" onclick="document.getElementById('compareForm').dispatchEvent(new Event('submit'))">
              <i class="fa-solid fa-arrows-rotate me-1"></i> Retry
            </button>
          </div>
        `;
      }
    });

  } // end compareForm

});
