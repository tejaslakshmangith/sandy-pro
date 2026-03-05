/* dashboard.js — Chart.js charts from /api/dashboard/stats */
(function () {
  'use strict';

  // Set Chart.js global defaults for dark theme
  Chart.defaults.color = '#8888aa';
  Chart.defaults.borderColor = '#2a2a3a';
  Chart.defaults.font.family = "'Segoe UI', system-ui, sans-serif";

  const GRADE_COLORS = {
    A1: '#00ff88', A2: '#44ff66', A3: '#88ff44',
    B1: '#ffcc00', B2: '#ff8800', B3: '#ff4400',
    C1: '#cc2200', C2: '#880000',
  };

  const CAT_COLORS = {
    ore: '#ff6b35', mineral: '#4fc3f7', rock: '#f5c842', stone: '#00ff88',
  };

  function el(id) { return document.getElementById(id); }

  async function loadStats() {
    try {
      const res = await fetch('/api/dashboard/stats');
      const data = await res.json();

      // Stat cards
      el('stat-total').textContent = data.total_records || '—';
      el('stat-purity').textContent = data.avg_purity != null ? data.avg_purity + '%' : '—';
      el('stat-a1').textContent = (data.grade_distribution || {})['A1'] || '0';

      // Category pie chart
      const catDist = data.category_distribution || {};
      new Chart(el('chart-category'), {
        type: 'doughnut',
        data: {
          labels: Object.keys(catDist).map(k => k.charAt(0).toUpperCase() + k.slice(1)),
          datasets: [{
            data: Object.values(catDist),
            backgroundColor: Object.keys(catDist).map(k => CAT_COLORS[k] || '#888'),
            borderColor: '#1a1a24',
            borderWidth: 3,
          }],
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: { position: 'right', labels: { padding: 16, font: { size: 12 } } },
          },
        },
      });

      // Grade bar chart
      const gradeDist = data.grade_distribution || {};
      const gradeOrder = ['A1','A2','A3','B1','B2','B3','C1','C2'];
      new Chart(el('chart-grade'), {
        type: 'bar',
        data: {
          labels: gradeOrder,
          datasets: [{
            label: 'Records',
            data: gradeOrder.map(g => gradeDist[g] || 0),
            backgroundColor: gradeOrder.map(g => GRADE_COLORS[g]),
            borderRadius: 6,
          }],
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: { legend: { display: false } },
          scales: {
            x: { grid: { color: '#2a2a3a' } },
            y: { grid: { color: '#2a2a3a' }, beginAtZero: true },
          },
        },
      });

      // Commercial value doughnut
      const cvDist = data.commercial_value_distribution || {};
      const cvColors = { premium: '#00ff88', high: '#f5c842', medium: '#ff8800', low: '#ff4400', marginal: '#880000' };
      new Chart(el('chart-commercial'), {
        type: 'doughnut',
        data: {
          labels: Object.keys(cvDist).map(k => k.charAt(0).toUpperCase() + k.slice(1)),
          datasets: [{
            data: Object.values(cvDist),
            backgroundColor: Object.keys(cvDist).map(k => cvColors[k] || '#888'),
            borderColor: '#1a1a24',
            borderWidth: 3,
          }],
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: { legend: { position: 'right', labels: { padding: 16, font: { size: 12 } } } },
        },
      });

      // Avg purity bar chart
      const purityByCat = data.avg_purity_by_category || {};
      new Chart(el('chart-purity'), {
        type: 'bar',
        data: {
          labels: Object.keys(purityByCat).map(k => k.charAt(0).toUpperCase() + k.slice(1)),
          datasets: [{
            label: 'Avg Purity %',
            data: Object.values(purityByCat),
            backgroundColor: Object.keys(purityByCat).map(k => CAT_COLORS[k] || '#888'),
            borderRadius: 6,
          }],
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: { legend: { display: false } },
          scales: {
            x: { grid: { color: '#2a2a3a' } },
            y: { grid: { color: '#2a2a3a' }, beginAtZero: true, max: 100 },
          },
        },
      });

      // Recent analyses table
      const recent = data.recent_analyses || [];
      if (recent.length) {
        const tbody = el('recent-table-body');
        tbody.innerHTML = recent.map((r, i) => `
          <tr>
            <td>${i + 1}</td>
            <td>${r.name || r.specific_name || '—'}</td>
            <td><span class="badge badge-${(r.category||'').toLowerCase()}">${r.category || '—'}</span></td>
            <td style="color:${GRADE_COLORS[(r.quality_grade||'').toUpperCase()]||'#888'};font-weight:700;">${r.quality_grade || '—'}</td>
            <td>${r.purity_percentage != null ? parseFloat(r.purity_percentage).toFixed(1) + '%' : '—'}</td>
            <td>${r.commercial_value || '—'}</td>
          </tr>
        `).join('');
      }

      // Ore class distribution chart
      const oreClassDist = data.ore_class_distribution || {};
      if (Object.keys(oreClassDist).length) {
        el('ore-class-empty').style.display = 'none';
        el('ore-class-chart-wrap').style.display = 'block';
        const oreColors = ['#ff6b35','#4fc3f7','#f5c842','#00ff88','#cc2200','#ff8800'];
        new Chart(el('chart-ore-class'), {
          type: 'doughnut',
          data: {
            labels: Object.keys(oreClassDist).map(k => k.charAt(0).toUpperCase() + k.slice(1)),
            datasets: [{
              data: Object.values(oreClassDist),
              backgroundColor: Object.keys(oreClassDist).map((_, i) => oreColors[i % oreColors.length]),
              borderColor: '#1a1a24',
              borderWidth: 3,
            }],
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { position: 'right', labels: { padding: 16, font: { size: 12 } } } },
          },
        });
      }

      // Classifier engine usage chart
      const engineDist = data.classifier_source_distribution || {};
      if (Object.keys(engineDist).length) {
        el('engine-empty').style.display = 'none';
        el('engine-chart-wrap').style.display = 'block';
        const engineLabels = { roboflow: '🤖 Roboflow', gemini: '✨ Gemini AI', ml_fallback: '🔬 ML Model', unknown: '❓ Unknown' };
        const engineColors = { roboflow: '#4fc3f7', gemini: '#f5c842', ml_fallback: '#ff6b35', unknown: '#888' };
        new Chart(el('chart-engine'), {
          type: 'doughnut',
          data: {
            labels: Object.keys(engineDist).map(k => engineLabels[k] || k),
            datasets: [{
              data: Object.values(engineDist),
              backgroundColor: Object.keys(engineDist).map(k => engineColors[k] || '#888'),
              borderColor: '#1a1a24',
              borderWidth: 3,
            }],
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { position: 'right', labels: { padding: 16, font: { size: 12 } } } },
          },
        });
      }

      // Integrated dataset sources
      const sources = data.dataset_sources || [];
      if (sources.length) {
        el('dataset-sources-grid').innerHTML = sources.map(s => `
          <div class="card" style="padding:1rem;">
            <div style="font-weight:700;color:var(--text-primary);margin-bottom:0.35rem;">${s.name}</div>
            <div style="font-size:0.82rem;color:var(--text-muted);margin-bottom:0.5rem;">${s.description || ''}</div>
            ${s.classes ? `<div style="display:flex;flex-wrap:wrap;gap:4px;margin-bottom:0.5rem;">${s.classes.map(c=>`<span class="tag">${c}</span>`).join('')}</div>` : ''}
            ${s.license ? `<div style="font-size:0.75rem;color:var(--text-muted);margin-bottom:0.35rem;">License: ${s.license}</div>` : ''}
            <a href="${s.url}" target="_blank" rel="noopener" style="font-size:0.8rem;color:var(--accent-blue);text-decoration:none;">🔗 View dataset →</a>
          </div>
        `).join('');
      }

    } catch (err) {
      console.error('Dashboard load error:', err);
    }
  }

  loadStats();
})();
