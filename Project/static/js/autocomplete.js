/**
 * WeatherSphere - Professional City Search Autocomplete Module
 */
document.addEventListener('DOMContentLoaded', () => {

  const suggestionCache = new Map();

  function initAutocomplete(inputEl) {
    if (!inputEl) return;

    // Find or create parent container wrapper
    let wrapper = inputEl.closest('.hero-search-form') || inputEl.closest('.search-input-group') || inputEl.parentElement;
    if (!wrapper) return;

    // Ensure wrapper has relative positioning
    if (getComputedStyle(wrapper).position === 'static') {
      wrapper.style.position = 'relative';
    }

    // Create Dropdown Container
    let dropdown = document.createElement('div');
    dropdown.className = 'autocomplete-dropdown glass-card shadow-2xl d-none';
    wrapper.appendChild(dropdown);

    let debounceTimer = null;
    let activeIndex = -1;
    let currentResults = [];

    // Highlight query matches
    function highlightText(text, query) {
      if (!query) return text;
      const escapedQuery = query.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
      const regex = new RegExp(`(${escapedQuery})`, 'gi');
      return text.replace(regex, '<span class="search-highlight">$1</span>');
    }

    // Render Dropdown Items
    function renderDropdown(results, query) {
      currentResults = results;
      activeIndex = -1;

      if (!results || results.length === 0) {
        dropdown.innerHTML = `
          <div class="autocomplete-state-box text-center p-3 text-muted small">
            <i class="fa-solid fa-location-dot-slash me-2 text-warning"></i> No cities found
          </div>
        `;
        dropdown.classList.remove('d-none');
        return;
      }

      let html = '<div class="autocomplete-list rounded-4 overflow-hidden">';
      results.forEach((item, index) => {
        const highlightedLabel = highlightText(item.display_name, query);
        html += `
          <div class="autocomplete-item p-3 border-bottom border-secondary-subtle d-flex align-items-center gap-3 cursor-pointer" data-index="${index}">
            <div class="autocomplete-icon-box bg-primary-subtle text-primary rounded-circle">
              <i class="fa-solid fa-location-dot"></i>
            </div>
            <div class="flex-grow-1 truncate">
              <div class="fw-bold text-body small truncate">${highlightedLabel}</div>
              <div class="extra-small text-muted truncate">${item.state ? item.state + ', ' : ''}${item.country}</div>
            </div>
            <i class="fa-solid fa-arrow-right-long text-muted extra-small opacity-50"></i>
          </div>
        `;
      });
      html += '</div>';

      dropdown.innerHTML = html;
      dropdown.classList.remove('d-none');

      // Bind click event to items
      dropdown.querySelectorAll('.autocomplete-item').forEach(itemEl => {
        itemEl.addEventListener('click', (e) => {
          e.stopPropagation();
          const idx = parseInt(itemEl.dataset.index, 10);
          selectItem(results[idx]);
        });
      });
    }

    // Show Loading State
    function showLoading() {
      dropdown.innerHTML = `
        <div class="autocomplete-state-box text-center p-3 text-muted small">
          <div class="spinner-border spinner-border-sm text-primary me-2" role="status"></div>
          Searching cities...
        </div>
      `;
      dropdown.classList.remove('d-none');
    }

    // Close Dropdown
    function closeDropdown() {
      dropdown.classList.add('d-none');
      dropdown.innerHTML = '';
      activeIndex = -1;
      currentResults = [];
    }

    // Select Item and Submit Form
    function selectItem(item) {
      if (!item) return;
      inputEl.value = item.display_name;
      closeDropdown();

      // Submit parent form if available, else navigate
      const form = inputEl.closest('form');
      if (form) {
        if (window.showSpinner) window.showSpinner();
        form.submit();
      } else {
        if (window.showSpinner) window.showSpinner();
        window.location.href = `/dashboard?city=${encodeURIComponent(item.display_name)}`;
      }
    }

    // Fetch Suggestions with Debounce & Cache
    function fetchSuggestions(query) {
      const q = query.trim();
      if (q.length < 2) {
        closeDropdown();
        return;
      }

      if (suggestionCache.has(q.toLowerCase())) {
        renderDropdown(suggestionCache.get(q.toLowerCase()), q);
        return;
      }

      showLoading();

      fetch(`/api/cities/search?q=${encodeURIComponent(q)}`)
        .then(res => res.json())
        .then(data => {
          if (data.success && data.results) {
            suggestionCache.set(q.toLowerCase(), data.results);
            renderDropdown(data.results, q);
          } else {
            renderDropdown([], q);
          }
        })
        .catch(err => {
          console.error('Autocomplete fetch error:', err);
          closeDropdown();
        });
    }

    // Input Event Listener with 300ms Debounce
    inputEl.addEventListener('input', (e) => {
      clearTimeout(debounceTimer);
      const val = e.target.value;
      if (val.trim().length < 2) {
        closeDropdown();
        return;
      }
      debounceTimer = setTimeout(() => {
        fetchSuggestions(val);
      }, 300);
    });

    // Keyboard Navigation (ArrowUp, ArrowDown, Enter, Escape)
    inputEl.addEventListener('keydown', (e) => {
      if (dropdown.classList.contains('d-none') || currentResults.length === 0) {
        return;
      }

      const items = dropdown.querySelectorAll('.autocomplete-item');

      if (e.key === 'ArrowDown') {
        e.preventDefault();
        activeIndex = (activeIndex + 1) % items.length;
        updateActiveItem(items);
      } else if (e.key === 'ArrowUp') {
        e.preventDefault();
        activeIndex = (activeIndex - 1 + items.length) % items.length;
        updateActiveItem(items);
      } else if (e.key === 'Enter') {
        if (activeIndex >= 0 && activeIndex < currentResults.length) {
          e.preventDefault();
          selectItem(currentResults[activeIndex]);
        }
      } else if (e.key === 'Escape') {
        closeDropdown();
      }
    });

    function updateActiveItem(items) {
      items.forEach((it, idx) => {
        if (idx === activeIndex) {
          it.classList.add('active');
          it.scrollIntoView({ block: 'nearest' });
        } else {
          it.classList.remove('active');
        }
      });
    }

    // Close Dropdown when clicking outside
    document.addEventListener('click', (e) => {
      if (!wrapper.contains(e.target)) {
        closeDropdown();
      }
    });

    // Re-open on focus if query present
    inputEl.addEventListener('focus', () => {
      const val = inputEl.value.trim();
      if (val.length >= 2) {
        fetchSuggestions(val);
      }
    });

  }

  // Initialize Autocomplete on Hero and Navbar inputs
  const heroInput = document.getElementById('heroSearchInput');
  if (heroInput) initAutocomplete(heroInput);

  document.querySelectorAll('.navbar-search-form input').forEach(input => {
    initAutocomplete(input);
  });

});
