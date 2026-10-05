document.addEventListener('DOMContentLoaded', () => {
  // DOM Elements
  const landingTabLogin = document.getElementById('landingTabLogin');
  const landingTabRegister = document.getElementById('landingTabRegister');
  const landingLoginForm = document.getElementById('landingLoginForm');
  const landingRegisterForm = document.getElementById('landingRegisterForm');
  const landingLoginEmail = document.getElementById('landingLoginEmail');
  const landingLoginPassword = document.getElementById('landingLoginPassword');
  const landingRegName = document.getElementById('landingRegName');
  const landingRegEmail = document.getElementById('landingRegEmail');
  const landingRegPassword = document.getElementById('landingRegPassword');
  const landingThemeToggleBtn = document.getElementById('landingThemeToggleBtn');
  const heroQuickDemoBtn = document.getElementById('heroQuickDemoBtn');
  const quickDemoFillBtn = document.getElementById('quickDemoFillBtn');
  const landingPreviewCard = document.getElementById('landingPreviewCard');

  // -----------------------------------------------------------------
  // Theme Toggle System (Light Sand Luxe & Dark Ultra-Luxe)
  // -----------------------------------------------------------------
  function updateThemeIcon(theme) {
    if (!landingThemeToggleBtn) return;
    landingThemeToggleBtn.innerHTML = theme === 'dark' 
      ? '<i class="fa-solid fa-sun text-amber"></i>' 
      : '<i class="fa-solid fa-moon"></i>';
  }

  function applyLandingTheme() {
    const savedTheme = localStorage.getItem('landing_theme') || localStorage.getItem('app_theme') || 'light';
    document.documentElement.setAttribute('data-theme', savedTheme);
    updateThemeIcon(savedTheme);
  }

  applyLandingTheme();

  if (landingThemeToggleBtn) {
    landingThemeToggleBtn.addEventListener('click', () => {
      const current = document.documentElement.getAttribute('data-theme') || 'light';
      const nextTheme = current === 'dark' ? 'light' : 'dark';
      document.documentElement.setAttribute('data-theme', nextTheme);
      localStorage.setItem('landing_theme', nextTheme);
      localStorage.setItem('app_theme', nextTheme);
      updateThemeIcon(nextTheme);
      showToast(`Switched theme to ${nextTheme === 'light' ? 'Light Sand Luxe ☀️' : 'Dark Ultra-Luxe 🌙'}`, 'info');
    });
  }

  // -----------------------------------------------------------------
  // Interactive Card Pop-Up on Mockup Card (No Flip-Flop / Tilt)
  // -----------------------------------------------------------------
  if (landingPreviewCard) {
    landingPreviewCard.onmouseenter = () => {
      landingPreviewCard.style.transition = 'transform 0.28s cubic-bezier(0.34, 1.56, 0.64, 1), box-shadow 0.28s ease';
      landingPreviewCard.style.transform = 'translateY(-10px) scale(1.03)';
    };

    landingPreviewCard.onmousemove = (e) => {
      const rect = landingPreviewCard.getBoundingClientRect();
      const x = e.clientX - rect.left;
      const y = e.clientY - rect.top;
      landingPreviewCard.style.setProperty('--mouse-x', `${((x / rect.width) * 100).toFixed(1)}%`);
      landingPreviewCard.style.setProperty('--mouse-y', `${((y / rect.height) * 100).toFixed(1)}%`);
    };
    
    landingPreviewCard.onmouseleave = () => {
      landingPreviewCard.style.transition = 'transform 0.35s cubic-bezier(0.34, 1.56, 0.64, 1), box-shadow 0.35s ease';
      landingPreviewCard.style.transform = 'translateY(0px) scale(1)';
    };
  }

  // -----------------------------------------------------------------
  // 1-Click Fast Guest Demo Login
  // -----------------------------------------------------------------
  async function triggerFastDemoLogin() {
    showToast('⚡ Connecting as Jai S Ramani (Guest Demo)...', 'info');

    const demoEmail = 'jaisramani05@gmail.com';
    const demoPass = 'demo1234';

    try {
      let res = await fetch('/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: demoEmail, password: demoPass })
      });
      let data = await res.json();

      // If user not yet created in SQLite, auto-register first
      if (res.status === 401 || data.status === 'error') {
        res = await fetch('/api/auth/register', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ name: 'Jai S Ramani', email: demoEmail, password: demoPass })
        });
        data = await res.json();
      }

      if (data.status === 'success') {
        showToast('🎉 Welcome, Jai S Ramani! Launching Command Center...', 'success');
        setTimeout(() => {
          window.location.href = '/dashboard';
        }, 600);
      } else {
        // Fallback: direct redirect to dashboard
        window.location.href = '/dashboard';
      }
    } catch (err) {
      window.location.href = '/dashboard';
    }
  }

  if (heroQuickDemoBtn) {
    heroQuickDemoBtn.addEventListener('click', triggerFastDemoLogin);
  }

  if (quickDemoFillBtn) {
    quickDemoFillBtn.addEventListener('click', triggerFastDemoLogin);
  }

  // -----------------------------------------------------------------
  // GSAP Entrance Animations Suite
  // -----------------------------------------------------------------
  if (typeof gsap !== 'undefined') {
    // Hero Entrance
    gsap.from('.hero-badge, .hero-title, .hero-subtitle, .hero-ctas, .hero-stats', {
      duration: 0.8,
      y: 35,
      opacity: 0,
      stagger: 0.1,
      ease: 'power3.out'
    });

    gsap.from('.hero-auth-card', {
      duration: 0.9,
      x: 45,
      opacity: 0,
      ease: 'power3.out',
      delay: 0.2
    });

    // Step cards entrance
    gsap.from('.step-card', {
      duration: 0.6,
      scale: 0.85,
      y: 30,
      opacity: 0,
      stagger: 0.12,
      ease: 'back.out(1.8)',
      delay: 0.3
    });

    // Feature cards entrance
    gsap.from('.feature-card', {
      duration: 0.65,
      scale: 0.88,
      y: 25,
      opacity: 0,
      stagger: 0.08,
      ease: 'back.out(1.6)',
      delay: 0.4
    });
  }

  // -----------------------------------------------------------------
  // Tab Switchers
  // -----------------------------------------------------------------
  if (landingTabLogin && landingTabRegister) {
    landingTabLogin.addEventListener('click', () => {
      landingTabLogin.classList.add('active');
      landingTabRegister.classList.remove('active');
      landingLoginForm.classList.remove('hidden');
      landingRegisterForm.classList.add('hidden');
    });

    landingTabRegister.addEventListener('click', () => {
      landingTabRegister.classList.add('active');
      landingTabLogin.classList.remove('active');
      landingRegisterForm.classList.remove('hidden');
      landingLoginForm.classList.add('hidden');
    });
  }

  // -----------------------------------------------------------------
  // Email Login Handler
  // -----------------------------------------------------------------
  if (landingLoginForm) {
    landingLoginForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const email = landingLoginEmail.value;
      const password = landingLoginPassword.value;

      try {
        const res = await fetch('/api/auth/login', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ email, password })
        });
        const data = await res.json();
        if (data.status === 'success') {
          if (data.auto_alerts_triggered > 0) {
            showToast(`🔥 Logged In! ${data.auto_alerts_triggered} price drop alert email(s) automatically sent to your inbox!`, 'success');
          } else {
            showToast(`${data.message} Automated alerts active.`, 'success');
          }
          setTimeout(() => {
            window.location.href = '/dashboard';
          }, 800);
        } else {
          showToast(data.message || 'Invalid credentials', 'error');
        }
      } catch (err) {
        showToast('Login request failed', 'error');
      }
    });
  }

  // -----------------------------------------------------------------
  // Email Registration Handler
  // -----------------------------------------------------------------
  if (landingRegisterForm) {
    landingRegisterForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const name = landingRegName.value;
      const email = landingRegEmail.value;
      const password = landingRegPassword.value;

      try {
        const res = await fetch('/api/auth/register', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ email, password, name })
        });
        const data = await res.json();
        if (data.status === 'success') {
          if (data.auto_alerts_triggered > 0) {
            showToast(`🎉 Account Created! ${data.auto_alerts_triggered} price drop alert email(s) automatically sent!`, 'success');
          } else {
            showToast(`${data.message} Automated alerts armed.`, 'success');
          }
          setTimeout(() => {
            window.location.href = '/dashboard';
          }, 800);
        } else {
          showToast(data.message || 'Registration failed', 'error');
        }
      } catch (err) {
        showToast('Registration request failed', 'error');
      }
    });
  }

  // -----------------------------------------------------------------
  // Toast Notifications Helper
  // -----------------------------------------------------------------
  function showToast(msg, type = 'info') {
    const container = document.getElementById('toastContainer');
    if (!container) return;
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.innerHTML = `<i class="fa-solid fa-circle-info"></i> ${msg}`;
    container.appendChild(toast);

    if (typeof gsap !== 'undefined') {
      gsap.fromTo(toast, { x: 80, opacity: 0 }, { x: 0, opacity: 1, duration: 0.35, ease: 'power2.out' });
    }

    setTimeout(() => {
      if (typeof gsap !== 'undefined') {
        gsap.to(toast, { x: 80, opacity: 0, duration: 0.3, onComplete: () => toast.remove() });
      } else {
        toast.remove();
      }
    }, 4000);
  }
});
