/* upload.js — drag & drop, preview, AJAX submit */
(function () {
  'use strict';

  const form = document.getElementById('classify-form');
  const dropZone = document.getElementById('drop-zone');
  const imageInput = document.getElementById('image-input');
  const previewWrap = document.getElementById('preview-wrap');
  const previewImg = document.getElementById('preview-img');
  const previewName = document.getElementById('preview-name');
  const dropDefault = document.getElementById('drop-default');
  const clearBtn = document.getElementById('clear-image');
  const analyzeBtn = document.getElementById('analyze-btn');
  const btnText = document.getElementById('btn-text');
  const btnIcon = document.getElementById('btn-icon');
  const loadingOverlay = document.getElementById('loading-overlay');
  const alertBox = document.getElementById('alert-box');

  // Particle canvas background
  initParticles();

  // ----- Drag & drop -----
  ['dragenter', 'dragover'].forEach(evt => {
    dropZone.addEventListener(evt, e => {
      e.preventDefault();
      dropZone.classList.add('drag-over');
    });
  });

  ['dragleave', 'drop'].forEach(evt => {
    dropZone.addEventListener(evt, e => {
      e.preventDefault();
      dropZone.classList.remove('drag-over');
    });
  });

  dropZone.addEventListener('drop', e => {
    const file = e.dataTransfer.files[0];
    if (file) setFile(file);
  });

  imageInput.addEventListener('change', () => {
    if (imageInput.files[0]) setFile(imageInput.files[0]);
  });

  clearBtn.addEventListener('click', e => {
    e.stopPropagation();
    clearFile();
  });

  function setFile(file) {
    const allowed = ['image/png', 'image/jpeg', 'image/webp', 'image/bmp'];
    if (!allowed.includes(file.type)) {
      showAlert('Invalid file type. Please upload PNG, JPG, JPEG, WEBP, or BMP.');
      return;
    }
    if (file.size > 16 * 1024 * 1024) {
      showAlert('File is too large (max 16 MB).');
      return;
    }

    const dt = new DataTransfer();
    dt.items.add(file);
    imageInput.files = dt.files;

    const reader = new FileReader();
    reader.onload = ev => {
      previewImg.src = ev.target.result;
      previewName.textContent = file.name + ' (' + (file.size / 1024).toFixed(1) + ' KB)';
      dropDefault.style.display = 'none';
      previewWrap.classList.add('active');
    };
    reader.readAsDataURL(file);
    hideAlert();
  }

  function clearFile() {
    imageInput.value = '';
    previewImg.src = '';
    previewWrap.classList.remove('active');
    dropDefault.style.display = '';
  }

  // ----- Form submit -----
  form.addEventListener('submit', async e => {
    e.preventDefault();
    hideAlert();

    const hasImage = imageInput.files && imageInput.files[0];
    const description = document.getElementById('description').value.trim();

    if (!hasImage && !description) {
      showAlert('Please upload an image or provide a text description.');
      return;
    }

    setLoading(true);

    const fd = new FormData();
    if (hasImage) fd.append('image', imageInput.files[0]);
    if (description) fd.append('description', description);

    try {
      const res = await fetch('/api/classify', { method: 'POST', body: fd });
      const data = await res.json();

      if (!res.ok) {
        throw new Error(data.error || 'Classification failed');
      }

      // Save to sessionStorage for result page
      sessionStorage.setItem('sandyResult', JSON.stringify(data));
      window.location.href = '/result';
    } catch (err) {
      showAlert('Error: ' + err.message);
      setLoading(false);
    }
  });

  function setLoading(on) {
    analyzeBtn.disabled = on;
    loadingOverlay.classList.toggle('active', on);
    btnText.textContent = on ? 'ANALYZING…' : 'ANALYZE SAMPLE';
    btnIcon.textContent = on ? '⏳' : '🔬';
  }

  function showAlert(msg) {
    alertBox.textContent = msg;
    alertBox.classList.remove('d-none');
    alertBox.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
  }

  function hideAlert() {
    alertBox.classList.add('d-none');
  }

  // ----- Particle background -----
  function initParticles() {
    const canvas = document.getElementById('particle-canvas');
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    let W, H, particles = [];

    function resize() {
      W = canvas.width = canvas.offsetWidth;
      H = canvas.height = canvas.offsetHeight;
    }

    function mkParticle() {
      return {
        x: Math.random() * W,
        y: Math.random() * H,
        r: Math.random() * 2 + 0.5,
        vx: (Math.random() - 0.5) * 0.4,
        vy: (Math.random() - 0.5) * 0.4,
        alpha: Math.random() * 0.5 + 0.1,
      };
    }

    resize();
    for (let i = 0; i < 80; i++) particles.push(mkParticle());
    window.addEventListener('resize', resize);

    function draw() {
      ctx.clearRect(0, 0, W, H);
      particles.forEach(p => {
        p.x += p.vx; p.y += p.vy;
        if (p.x < 0) p.x = W;
        if (p.x > W) p.x = 0;
        if (p.y < 0) p.y = H;
        if (p.y > H) p.y = 0;
        ctx.beginPath();
        ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
        ctx.fillStyle = `rgba(245,200,66,${p.alpha})`;
        ctx.fill();
      });
      requestAnimationFrame(draw);
    }
    draw();
  }
})();
