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
  // Interactive Regional Marketplace Preview Switcher (US, IN, UK, DE, CA)
  // -----------------------------------------------------------------
  const regionalProducts = {
    US: {
      title: "Sony WH-1000XM5 Wireless Noise Canceling Headphones",
      category: "AUDIO • ASIN: B09B8V1LZ3 • 🇺🇸 AMAZON US",
      price: "$328.00",
      original: "$399.99",
      discount: "-18% OFF",
      rating: "4.6",
      deal: "🔥 Deal Active!",
      status: "🔥 Deal Active! Price is $51.99 below target",
      delta: "-18.0% 30d",
      image: "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=600&auto=format&fit=crop&q=80"
    },
    IN: {
      title: "OnePlus Nord Buds 2 TWS in-Ear Earbuds with Active Noise Cancellation",
      category: "AUDIO • ASIN: B0BY8MCQ9S • 🇮🇳 AMAZON INDIA",
      price: "₹2,499.00",
      original: "₹3,299.00",
      discount: "-24% OFF",
      rating: "4.5",
      deal: "🔥 Price Drop!",
      status: "🔥 Deal Active! Price is ₹500 below target",
      delta: "-24.2% 30d",
      image: "https://images.unsplash.com/photo-1590658268037-6bf12165a8df?w=600&auto=format&fit=crop&q=80"
    },
    UK: {
      title: "Apple AirPods Pro 2 Wireless Earbuds with USB-C MagSafe Case",
      category: "AUDIO • ASIN: B0CHWRXH8B • 🇬🇧 AMAZON UK",
      price: "£179.00",
      original: "£229.00",
      discount: "-22% OFF",
      rating: "4.8",
      deal: "🔥 Flash Deal!",
      status: "🔥 Deal Active! Price is £25.00 below target",
      delta: "-21.8% 30d",
      image: "https://images.unsplash.com/photo-1600294037681-c80b4cb5b434?w=600&auto=format&fit=crop&q=80"
    },
    DE: {
      title: "Sennheiser Momentum 4 Wireless ANC Headphones (60h Battery)",
      category: "AUDIO • ASIN: B0B647PVD3 • 🇩🇪 AMAZON GERMANY",
      price: "249,00 €",
      original: "349,00 €",
      discount: "-29% OFF",
      rating: "4.6",
      deal: "🔥 Deal Active!",
      status: "🔥 Deal Active! Price is 40,00 € below target",
      delta: "-28.7% 30d",
      image: "https://images.unsplash.com/photo-1546435770-a3e426bf472b?w=600&auto=format&fit=crop&q=80"
    },
    CA: {
      title: "Bose QuietComfort Ultra Wireless Noise Cancelling Headphones",
      category: "AUDIO • ASIN: B0CCZ26B5V • 🇨🇦 AMAZON CANADA",
      price: "CA$ 429.00",
      original: "CA$ 549.00",
      discount: "-22% OFF",
      rating: "4.7",
      deal: "🔥 Top Deal!",
      status: "🔥 Deal Active! Price is CA$ 50.00 below target",
      delta: "-21.9% 30d",
      image: "https://images.unsplash.com/photo-1484704849700-f032a568e944?w=600&auto=format&fit=crop&q=80"
    }
  };

  const regionPills = document.querySelectorAll('.preview-region-pill');
  const mockupImg = document.getElementById('mockupImg');
  const mockupTitle = document.getElementById('mockupTitle');
  const mockupCategory = document.getElementById('mockupCategory');
  const mockupPrice = document.getElementById('mockupPrice');
  const mockupOriginal = document.getElementById('mockupOriginal');
  const mockupDiscount = document.getElementById('mockupDiscount');
  const mockupRating = document.getElementById('mockupRating');
  const mockupDealBadge = document.getElementById('mockupDealBadge');
  const mockupStatus = document.getElementById('mockupStatus');
  const mockupDeltaPill = document.getElementById('mockupDeltaPill');

  regionPills.forEach(pill => {
    pill.addEventListener('click', () => {
      regionPills.forEach(p => p.classList.remove('active'));
      pill.classList.add('active');
      const region = pill.dataset.region;
      const prod = regionalProducts[region];
      if (!prod) return;

      if (mockupImg) {
        mockupImg.style.opacity = '0';
        setTimeout(() => {
          mockupImg.src = prod.image;
          mockupImg.alt = prod.title;
          mockupImg.style.opacity = '1';
        }, 150);
      }
      if (mockupTitle) mockupTitle.textContent = prod.title;
      if (mockupCategory) mockupCategory.textContent = prod.category;
      if (mockupPrice) mockupPrice.textContent = prod.price;
      if (mockupOriginal) mockupOriginal.textContent = prod.original;
      if (mockupDiscount) mockupDiscount.textContent = prod.discount;
      if (mockupRating) mockupRating.innerHTML = `<i class="fa-solid fa-star"></i> ${prod.rating}`;
      if (mockupDealBadge) mockupDealBadge.innerHTML = `<i class="fa-solid fa-fire"></i> ${prod.deal}`;
      if (mockupStatus) mockupStatus.textContent = prod.status;
      if (mockupDeltaPill) mockupDeltaPill.innerHTML = `<i class="fa-solid fa-arrow-trend-down"></i> ${prod.delta}`;
    });
  });

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

  // -----------------------------------------------------------------
  // Live Telemetry Marquee Synchronizer
  // -----------------------------------------------------------------
  async function fetchLiveTelemetry() {
    try {
      const res = await fetch('/api/products');
      if (!res.ok) return;
      const data = await res.json();
      if (data.status === 'success' && Array.isArray(data.products) && data.products.length > 0) {
        const count = data.products.length;
        const totalSavings = data.products.reduce((acc, p) => acc + (Number(p.potential_savings) || 0), 0);
        const signalsCount = count * 24 + 140;

        document.querySelectorAll('.dyn-marketplaces').forEach(el => {
          el.textContent = `${count} Live ASINs`;
        });
        document.querySelectorAll('.dyn-signals').forEach(el => {
          el.textContent = `${signalsCount.toLocaleString()}+ checks`;
        });
        document.querySelectorAll('.dyn-savings').forEach(el => {
          el.textContent = `$${Math.round(totalSavings).toLocaleString()} USD`;
        });
        document.querySelectorAll('.dyn-stores').forEach(el => {
          el.textContent = `18 Global Stores`;
        });
      }
    } catch (e) {
      // Graceful fallback to default ticker copy
    }
  }

  fetchLiveTelemetry();
});
