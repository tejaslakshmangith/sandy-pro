/* result.js — render classification result from sessionStorage */
(function () {
  'use strict';

  const GRADE_COLORS = {
    A1: '#00ff88', A2: '#44ff66', A3: '#88ff44',
    B1: '#ffcc00', B2: '#ff8800', B3: '#ff4400',
    C1: '#cc2200', C2: '#880000',
  };

  const GRADE_LABELS = {
    A1: 'Premium Export Quality', A2: 'High Commercial Grade',
    A3: 'Standard Industrial Grade', B1: 'Low Industrial Grade',
    B2: 'Processing Required', B3: 'Heavy Processing Needed',
    C1: 'Marginal Viability', C2: 'Waste/Gangue Material',
  };

  const CAT_CLASSES = {
    ore: 'badge-ore', mineral: 'badge-mineral',
    rock: 'badge-rock', stone: 'badge-stone',
  };

  function el(id) { return document.getElementById(id); }

  const raw = sessionStorage.getItem('sandyResult');
  if (!raw) {
    el('no-result').classList.remove('d-none');
    return;
  }

  let d;
  try { d = JSON.parse(raw); } catch { el('no-result').classList.remove('d-none'); return; }

  el('no-result').classList.add('d-none');
  el('result-content').classList.remove('d-none');

  // Category badge
  const cat = (d.category || 'unknown').toLowerCase();
  const badge = el('category-badge');
  badge.textContent = cat.toUpperCase();
  badge.className = 'category-banner ' + (CAT_CLASSES[cat] || 'badge-rock');

  // Name & formula
  el('result-name').textContent = d.specific_name || 'Unknown Sample';
  el('result-formula').textContent = d.chemical_formula ? '⚗ ' + d.chemical_formula : '';
  el('result-common').textContent = d.common_name ? '📌 ' + d.common_name : '';

  // Grade badge
  const grade = (d.quality_grade || 'C2').toUpperCase();
  const gradeColor = GRADE_COLORS[grade] || '#888888';
  const gradeBadge = el('grade-badge');
  gradeBadge.textContent = grade;
  gradeBadge.style.color = gradeColor;
  gradeBadge.style.borderColor = gradeColor;
  gradeBadge.style.textShadow = `0 0 20px ${gradeColor}`;
  el('grade-label').textContent = GRADE_LABELS[grade] || '';

  // Purity meter
  const purity = parseFloat(d.purity_percentage) || 0;
  const circum = 2 * Math.PI * 50; // r=50
  const offset = circum - (purity / 100) * circum;
  const fill = el('purity-fill');
  fill.style.strokeDasharray = circum;
  fill.style.strokeDashoffset = circum; // start hidden
  fill.setAttribute('stroke', gradeColor);
  el('purity-text').textContent = purity.toFixed(1) + '%';
  el('purity-text').setAttribute('fill', gradeColor);

  // Animate after paint
  requestAnimationFrame(() => {
    setTimeout(() => { fill.style.strokeDashoffset = offset; }, 100);
  });

  // Confidence
  const conf = parseFloat(d.confidence_score) || 0;
  el('confidence-val').textContent = conf.toFixed(0) + '%';
  setTimeout(() => { el('confidence-bar').style.width = conf + '%'; }, 200);

  // Hardness bar
  const hardness = parseFloat(d.hardness_mohs) || 0;
  const hBar = el('hardness-bar');
  for (let i = 1; i <= 10; i++) {
    const seg = document.createElement('div');
    seg.className = 'hardness-segment' + (i <= hardness ? ' active' : '');
    hBar.appendChild(seg);
  }
  const hNum = document.createElement('span');
  hNum.textContent = hardness;
  hNum.style.cssText = 'margin-left:6px;font-size:0.85rem;color:var(--accent-gold);font-weight:600;';
  hBar.appendChild(hNum);

  // Physical props
  el('val-texture').textContent = d.texture || '—';
  el('val-luster').textContent = d.luster || '—';
  el('val-color').textContent = d.color_description || '—';
  el('val-formation').textContent = d.formation_type || '—';
  el('val-age').textContent = d.geological_age || '—';

  // Commercial info
  const cv = (d.commercial_value || '').toLowerCase();
  const cvEl = el('val-commercial');
  cvEl.textContent = d.commercial_value || '—';
  cvEl.className = 'info-value cv-' + cv;

  const mv = d.market_value_usd_per_ton;
  el('val-market').textContent = mv != null ? '$' + Number(mv).toLocaleString() + ' /ton' : '—';

  el('val-mining').textContent = d.mining_suitability || '—';

  const extr = (d.extraction_difficulty || '').toLowerCase();
  const extrEl = el('val-extraction');
  extrEl.textContent = d.extraction_difficulty || '—';
  if (extr === 'easy') extrEl.style.color = 'var(--accent-green)';
  else if (extr === 'moderate') extrEl.style.color = 'var(--accent-gold)';
  else extrEl.style.color = '#ff4400';

  const envEl = el('val-env');
  envEl.textContent = d.environmental_impact || '—';
  envEl.className = 'info-value env-' + (d.environmental_impact || '').toLowerCase();

  el('val-source').textContent = d.source === 'ml_classifier' ? 'ML Classifier (fallback)' : 'Gemini 2.5 Pro';

  // Tags helper
  function renderTags(containerId, items, color) {
    const container = el(containerId);
    const arr = Array.isArray(items) ? items :
      (typeof items === 'string' ? items.split(',').map(s => s.trim()).filter(Boolean) : []);
    if (!arr.length) {
      container.innerHTML = '<span class="tag">—</span>';
      return;
    }
    container.innerHTML = arr.map(item =>
      `<span class="tag" style="${color ? 'border-color:' + color + ';color:' + color : ''}">${item}</span>`
    ).join('');
  }

  renderTags('elements-tags', d.primary_elements, 'var(--accent-blue)');
  renderTags('minerals-tags', d.associated_minerals);
  renderTags('uses-tags', d.industrial_uses, 'var(--accent-gold)');

  // Analysis notes
  el('analysis-notes').textContent = d.analysis_notes || 'No analysis notes provided.';

  // Processing steps
  const procContainer = el('processing-steps');
  const procRaw = d.recommended_processing || '';
  const steps = procRaw.split(/[,;|→>]+/).map(s => s.trim()).filter(Boolean);
  if (steps.length) {
    procContainer.innerHTML = steps.map((s, i) =>
      `<span class="processing-step">${s}</span>${i < steps.length - 1 ? '<span style="color:var(--text-muted);padding:0 4px;">→</span>' : ''}`
    ).join('');
  } else {
    procContainer.innerHTML = '<span class="tag">—</span>';
  }

  // Download report
  el('download-btn').addEventListener('click', () => {
    const lines = [
      'SANDY PRO — Classification Report',
      '====================================',
      `Name:               ${d.specific_name || ''}`,
      `Common Name:        ${d.common_name || ''}`,
      `Category:           ${d.category || ''}`,
      `Chemical Formula:   ${d.chemical_formula || ''}`,
      `Quality Grade:      ${d.quality_grade || ''} — ${GRADE_LABELS[grade] || ''}`,
      `Purity:             ${purity.toFixed(1)}%`,
      `Confidence:         ${conf.toFixed(0)}%`,
      `Commercial Value:   ${d.commercial_value || ''}`,
      `Market Value:       $${Number(d.market_value_usd_per_ton || 0).toLocaleString()} /ton`,
      `Mining Suitability: ${d.mining_suitability || ''}`,
      `Extraction:         ${d.extraction_difficulty || ''}`,
      `Environment:        ${d.environmental_impact || ''}`,
      `Formation:          ${d.formation_type || ''}`,
      `Hardness (Mohs):    ${d.hardness_mohs || ''}`,
      `Primary Elements:   ${(d.primary_elements || []).join(', ')}`,
      `Industrial Uses:    ${(d.industrial_uses || []).join(', ')}`,
      '',
      'Analysis Notes:',
      d.analysis_notes || '',
    ];
    const blob = new Blob([lines.join('\n')], { type: 'text/plain' });
    const a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = 'sandy-pro-report-' + (d.specific_name || 'sample').replace(/\s+/g, '-').toLowerCase() + '.txt';
    a.click();
  });
})();
