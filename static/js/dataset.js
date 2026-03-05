/* dataset.js — search, filter, sort, paginate dataset table */
(function () {
  'use strict';

  const GRADE_COLORS = {
    A1: '#00ff88', A2: '#44ff66', A3: '#88ff44',
    B1: '#ffcc00', B2: '#ff8800', B3: '#ff4400',
    C1: '#cc2200', C2: '#880000',
  };

  let currentPage = 1;
  let debounceTimer;

  const fields = {
    search: document.getElementById('search-input'),
    category: document.getElementById('filter-category'),
    grade: document.getElementById('filter-grade'),
    cv: document.getElementById('filter-cv'),
    sortBy: document.getElementById('sort-by'),
  };

  const tbody = document.getElementById('dataset-tbody');
  const paginationInfo = document.getElementById('pagination-info');
  const paginationBtns = document.getElementById('pagination-btns');
  const recordCount = document.getElementById('record-count');

  // Event listeners
  fields.search.addEventListener('input', () => {
    clearTimeout(debounceTimer);
    debounceTimer = setTimeout(() => { currentPage = 1; loadData(); }, 350);
  });

  [fields.category, fields.grade, fields.cv, fields.sortBy].forEach(el => {
    el.addEventListener('change', () => { currentPage = 1; loadData(); });
  });

  async function loadData() {
    const params = new URLSearchParams({
      search: fields.search.value,
      category: fields.category.value,
      grade: fields.grade.value,
      commercial_value: fields.cv.value,
      sort_by: fields.sortBy.value,
      sort_order: 'asc',
      page: currentPage,
      per_page: 20,
    });

    tbody.innerHTML = `<tr><td colspan="10" style="text-align:center;padding:2rem;color:var(--text-muted);">Loading…</td></tr>`;

    try {
      const res = await fetch('/api/dataset?' + params);
      const data = await res.json();

      renderTable(data.data || []);
      renderPagination(data);
      recordCount.textContent = `${data.total} record${data.total !== 1 ? 's' : ''}`;
    } catch (err) {
      tbody.innerHTML = `<tr><td colspan="10" style="text-align:center;padding:2rem;color:#ff6b6b;">Error loading data: ${err.message}</td></tr>`;
    }
  }

  function renderTable(rows) {
    if (!rows.length) {
      tbody.innerHTML = `<tr><td colspan="10" style="text-align:center;padding:2rem;color:var(--text-muted);">No records match your filters.</td></tr>`;
      return;
    }
    tbody.innerHTML = rows.map(r => {
      const grade = (r.quality_grade || '').toUpperCase();
      const gradeColor = GRADE_COLORS[grade] || '#888888';
      const cat = (r.category || '').toLowerCase();
      return `<tr style="cursor:pointer;" onclick="showModal(${JSON.stringify(r).replace(/"/g, '&quot;')})">
        <td style="color:var(--text-muted)">${r.id}</td>
        <td style="font-weight:600">${r.name || ''}</td>
        <td><span class="badge badge-${cat}">${r.category || ''}</span></td>
        <td style="font-family:monospace;font-size:0.8rem;color:var(--accent-blue)">${r.chemical_formula || ''}</td>
        <td>${r.hardness_mohs || ''}</td>
        <td>${r.purity_percentage != null ? parseFloat(r.purity_percentage).toFixed(1) + '%' : ''}</td>
        <td style="color:${gradeColor};font-weight:700">${grade}</td>
        <td>${r.commercial_value || ''}</td>
        <td style="font-size:0.82rem;color:var(--text-muted)">${r.formation_type || ''}</td>
        <td style="font-size:0.82rem">${r.market_value_usd_per_ton != null ? '$' + Number(r.market_value_usd_per_ton).toLocaleString() : ''}</td>
      </tr>`;
    }).join('');
  }

  function renderPagination(data) {
    paginationInfo.textContent = `Page ${data.page} of ${data.pages} (${data.total} records)`;

    paginationBtns.innerHTML = '';
    if (data.pages <= 1) return;

    const addBtn = (label, page, disabled) => {
      const btn = document.createElement('button');
      btn.className = 'btn btn-secondary';
      btn.style.cssText = 'font-size:0.8rem;padding:4px 12px;';
      btn.textContent = label;
      btn.disabled = disabled;
      btn.addEventListener('click', () => { currentPage = page; loadData(); });
      paginationBtns.appendChild(btn);
    };

    addBtn('‹ Prev', currentPage - 1, currentPage === 1);

    const start = Math.max(1, currentPage - 2);
    const end = Math.min(data.pages, currentPage + 2);
    for (let p = start; p <= end; p++) {
      const btn = document.createElement('button');
      btn.className = 'btn ' + (p === currentPage ? 'btn-primary' : 'btn-secondary');
      btn.style.cssText = 'font-size:0.8rem;padding:4px 12px;';
      btn.textContent = p;
      const pg = p;
      btn.addEventListener('click', () => { currentPage = pg; loadData(); });
      paginationBtns.appendChild(btn);
    }

    addBtn('Next ›', currentPage + 1, currentPage === data.pages);
  }

  // Modal
  const modal = document.getElementById('row-modal');
  const modalClose = document.getElementById('modal-close');
  const modalName = document.getElementById('modal-name');
  const modalBadge = document.getElementById('modal-badge');
  const modalBody = document.getElementById('modal-body');

  window.showModal = function (row) {
    modalName.textContent = row.name || '';
    const cat = (row.category || '').toLowerCase();
    modalBadge.textContent = row.category || '';
    modalBadge.className = 'badge badge-' + cat + ' mb-2';

    const grade = (row.quality_grade || '').toUpperCase();
    const gradeColor = GRADE_COLORS[grade] || '#888';

    const fields = [
      ['Chemical Formula', row.chemical_formula],
      ['Color', row.color],
      ['Hardness (Mohs)', row.hardness_mohs],
      ['Luster', row.luster],
      ['Streak', row.streak],
      ['Cleavage', row.cleavage],
      ['Fracture', row.fracture],
      ['Crystal System', row.crystal_system],
      ['Specific Gravity', row.specific_gravity],
      ['Formation Type', row.formation_type],
      ['Primary Elements', row.primary_elements],
      ['Purity', row.purity_percentage != null ? parseFloat(row.purity_percentage).toFixed(1) + '%' : ''],
      ['Quality Grade', `<span style="color:${gradeColor};font-weight:700">${grade}</span>`],
      ['Commercial Value', row.commercial_value],
      ['Market Value', row.market_value_usd_per_ton != null ? '$' + Number(row.market_value_usd_per_ton).toLocaleString() + ' /ton' : ''],
      ['Industrial Uses', row.industrial_uses],
      ['Mining Region', row.mining_region],
      ['Extraction Difficulty', row.extraction_difficulty],
      ['Environmental Impact', row.environmental_impact],
    ];

    modalBody.innerHTML = fields.filter(([, v]) => v != null && v !== '').map(([k, v]) =>
      `<div class="info-row"><span class="info-label">${k}</span><span class="info-value">${v}</span></div>`
    ).join('');

    modal.classList.add('active');
  };

  modalClose.addEventListener('click', () => modal.classList.remove('active'));
  modal.addEventListener('click', e => { if (e.target === modal) modal.classList.remove('active'); });
  document.addEventListener('keydown', e => { if (e.key === 'Escape') modal.classList.remove('active'); });

  // Initial load
  loadData();

  // ── Mineral Reference Library ──────────────────────────────────────────
  let allMinerals = [];

  async function loadMinerals() {
    try {
      const res = await fetch('/api/dataset/minerals-meta');
      const meta = await res.json();
      allMinerals = meta.minerals || [];
      const sources = meta.sources || [];

      // Source badges
      const sourcesEl = document.getElementById('mineral-source-badges');
      sourcesEl.innerHTML = sources.map(s =>
        `<a href="${s.url}" target="_blank" rel="noopener"
            style="display:inline-flex;align-items:center;gap:6px;padding:4px 12px;border-radius:20px;
                   font-size:0.75rem;font-weight:600;text-decoration:none;
                   background:rgba(79,195,247,0.1);color:var(--accent-blue);
                   border:1px solid rgba(79,195,247,0.3);">
           🔗 ${s.name} (${s.license})
         </a>`
      ).join('');

      // Populate category filter
      const catFilter = document.getElementById('mineral-category-filter');
      const categories = [...new Set(allMinerals.map(m => m.category))].sort();
      categories.forEach(c => {
        const opt = document.createElement('option');
        opt.value = c; opt.textContent = c;
        catFilter.appendChild(opt);
      });

      renderMinerals();
    } catch (e) {
      document.getElementById('mineral-cards-grid').innerHTML =
        `<div style="color:#ff6b6b;padding:2rem;text-align:center;">Failed to load mineral data: ${e.message}</div>`;
    }
  }

  function renderMinerals() {
    const query = (document.getElementById('mineral-search').value || '').toLowerCase();
    const catFilter = document.getElementById('mineral-category-filter').value;

    const filtered = allMinerals.filter(m => {
      const matchText = !query ||
        m.name.toLowerCase().includes(query) ||
        m.category.toLowerCase().includes(query) ||
        (m.formula || '').toLowerCase().includes(query);
      const matchCat = !catFilter || m.category === catFilter;
      return matchText && matchCat;
    });

    const grid = document.getElementById('mineral-cards-grid');
    const emptyEl = document.getElementById('mineral-empty');

    if (!filtered.length) {
      grid.innerHTML = '';
      emptyEl.style.display = 'block';
      return;
    }
    emptyEl.style.display = 'none';

    const cvColor = { High: 'var(--accent-gold)', Medium: 'var(--accent-orange)', Low: 'var(--text-muted)' };

    grid.innerHTML = filtered.map(m => {
      const valueColor = cvColor[m.commercial_value] || 'var(--text-primary)';
      return `
      <div class="card" style="display:flex;flex-direction:column;gap:0.5rem;">
        <div style="display:flex;justify-content:space-between;align-items:flex-start;gap:0.5rem;flex-wrap:wrap;">
          <div style="font-size:1.05rem;font-weight:700;color:var(--text-primary);">${m.name}</div>
          <span class="badge" style="font-size:0.7rem;background:rgba(79,195,247,0.1);color:var(--accent-blue);border:1px solid rgba(79,195,247,0.3);">Kaggle</span>
        </div>
        <div style="font-family:monospace;font-size:0.82rem;color:var(--accent-blue);">${m.formula || 'N/A'}</div>
        <div style="font-size:0.8rem;color:var(--text-muted);">${m.category}</div>
        <div style="display:flex;gap:1.5rem;font-size:0.8rem;color:var(--text-muted);flex-wrap:wrap;">
          <span>🪨 Hardness: <strong style="color:var(--text-primary);">${m.hardness}</strong></span>
          <span>🎨 ${m.color}</span>
        </div>
        <div style="font-size:0.8rem;">
          Commercial: <strong style="color:${valueColor};">${m.commercial_value}</strong>
        </div>
        <div style="display:flex;flex-wrap:wrap;gap:4px;margin-top:0.25rem;">
          ${(m.industrial_uses || []).map(u => `<span class="tag" style="font-size:0.72rem;">${u}</span>`).join('')}
        </div>
      </div>`;
    }).join('');
  }

  document.getElementById('mineral-search').addEventListener('input', renderMinerals);
  document.getElementById('mineral-category-filter').addEventListener('change', renderMinerals);

  loadMinerals();
})();
