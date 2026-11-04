document.addEventListener('DOMContentLoaded', () => {
  // Register GSAP ScrollTrigger if available
  if (typeof gsap !== 'undefined' && typeof ScrollTrigger !== 'undefined') {
    gsap.registerPlugin(ScrollTrigger);
  }

  // DOM Elements
  const productsGrid = document.getElementById('productsGrid');
  const emptyState = document.getElementById('emptyState');
  const addProductForm = document.getElementById('addProductForm');
  const productUrlInput = document.getElementById('productUrlInput');
  const targetPriceInput = document.getElementById('targetPriceInput');
  const targetPriceSymbol = document.getElementById('targetPriceSymbol');
  const scrapeAllBtn = document.getElementById('scrapeAllBtn');
  const searchFilter = document.getElementById('searchFilter');
  const categoryFilter = document.getElementById('categoryFilter');
  const themeToggleBtn = document.getElementById('themeToggleBtn');
  const currencySelector = document.getElementById('currencySelector');

  // Stats Elements
  const statTotalProducts = document.getElementById('statTotalProducts');
  const statPriceDrops = document.getElementById('statPriceDrops');
  const statTotalValue = document.getElementById('statTotalValue');
  const statTotalSavings = document.getElementById('statTotalSavings');
  const statAvgDiscount = document.getElementById('statAvgDiscount');
  const statScraperStatus = document.getElementById('statScraperStatus');

  // Filter & Sort Elements
  const recommendationFilter = document.getElementById('recommendationFilter');
  const sortFilter = document.getElementById('sortFilter');

  // Background Scheduler Elements
  const schedulerStatusPill = document.getElementById('schedulerStatusPill');
  const schedulerPillText = document.getElementById('schedulerPillText');
  const schedulerMenuStatusText = document.getElementById('schedulerMenuStatusText');
  const toggleSchedulerBtn = document.getElementById('toggleSchedulerBtn');
  const triggerSchedulerBtn = document.getElementById('triggerSchedulerBtn');

  // Chart Modal Elements
  const chartModal = document.getElementById('chartModal');
  const closeChartModal = document.getElementById('closeChartModal');
  const modalProductTitle = document.getElementById('modalProductTitle');
  const modalCurrentPrice = document.getElementById('modalCurrentPrice');
  const modalTargetPrice = document.getElementById('modalTargetPrice');
  const modalLowestPrice = document.getElementById('modalLowestPrice');
  const modalHighestPrice = document.getElementById('modalHighestPrice');
  let priceChartInstance = null;

  // Competitor Comparison Modal Elements
  const competitorModal = document.getElementById('competitorModal');
  const closeCompetitorModal = document.getElementById('closeCompetitorModal');
  const compModalProductTitle = document.getElementById('compModalProductTitle');
  const compModalProductSubtitle = document.getElementById('compModalProductSubtitle');
  const compArbitrageBanner = document.getElementById('compArbitrageBanner');
  const compVerdictText = document.getElementById('compVerdictText');
  const compVerdictSub = document.getElementById('compVerdictSub');
  const compMaxSavings = document.getElementById('compMaxSavings');
  const compTabIndian = document.getElementById('compTabIndian');
  const compTabGlobal = document.getElementById('compTabGlobal');
  const compCurrentCurrencyCode = document.getElementById('compCurrentCurrencyCode');
  const compAvailabilityOnlyToggle = document.getElementById('compAvailabilityOnlyToggle');
  const compAvailabilityNotice = document.getElementById('compAvailabilityNotice');
  const compAvailabilityNoticeText = document.getElementById('compAvailabilityNoticeText');
  const compTabIndianBadge = document.getElementById('compTabIndianBadge');
  const compTabGlobalBadge = document.getElementById('compTabGlobalBadge');
  const competitorStoresGrid = document.getElementById('competitorStoresGrid');
  const compPriceSpreadVal = document.getElementById('compPriceSpreadVal');
  const competitorSpreadBars = document.getElementById('competitorSpreadBars');
  const compChannelPillsRow = document.getElementById('compChannelPillsRow');
  let currentComparisonData = null;
  let activeMarketTab = 'indian';
  let activeChannelFilter = 'all';

  // Alert Modal Elements
  const alertModal = document.getElementById('alertModal');
  const closeAlertModal = document.getElementById('closeAlertModal');
  const sendTestAlertForm = document.getElementById('sendTestAlertForm');
  const alertEmailInput = document.getElementById('alertEmailInput');
  const alertProductId = document.getElementById('alertProductId');
  const emailPreviewContainer = document.getElementById('emailPreviewContainer');
  const previewSubject = document.getElementById('previewSubject');
  const emailPreviewFrame = document.getElementById('emailPreviewFrame');

  // Alert Auth Gating Modal Elements
  const alertAuthModal = document.getElementById('alertAuthModal');
  const closeAlertAuthModal = document.getElementById('closeAlertAuthModal');
  const modalTabLogin = document.getElementById('modalTabLogin');
  const modalTabRegister = document.getElementById('modalTabRegister');
  const quickLoginForm = document.getElementById('quickLoginForm');
  const quickRegisterForm = document.getElementById('quickRegisterForm');
  const quickLoginEmail = document.getElementById('quickLoginEmail');
  const quickLoginPassword = document.getElementById('quickLoginPassword');
  const quickRegName = document.getElementById('quickRegName');
  const quickRegEmail = document.getElementById('quickRegEmail');
  const quickRegPassword = document.getElementById('quickRegPassword');
  let pendingAlertProductId = null;

  // Auto-Alerts & Activity Log Elements
  const autoAlertsStatusText = document.getElementById('autoAlertsStatusText');
  const toggleAutoAlertsBtn = document.getElementById('toggleAutoAlertsBtn');
  const viewAlertLogsBtn = document.getElementById('viewAlertLogsBtn');
  const alertCountBadge = document.getElementById('alertCountBadge');
  const alertActivityModal = document.getElementById('alertActivityModal');
  const closeAlertActivityModal = document.getElementById('closeAlertActivityModal');
  const alertLogsContainer = document.getElementById('alertLogsContainer');
  const activityBannerText = document.getElementById('activityBannerText');

  // 6-Feature Intelligence Suite Elements
  let currentModalProductId = null;
  let basketSelectedIds = new Set();
  const basketFloatingBar = document.getElementById('basketFloatingBar');
  const basketCountBadge = document.getElementById('basketCountBadge');
  const basketSummaryText = document.getElementById('basketSummaryText');
  const basketClearBtn = document.getElementById('basketClearBtn');
  const basketOptimizeBtn = document.getElementById('basketOptimizeBtn');
  const basketModal = document.getElementById('basketModal');
  const closeBasketModal = document.getElementById('closeBasketModal');



  // Amazon Partner Bank Cards Selection (persisted in localStorage)
  let appliedBankCards = {};
  try {
    const savedBankCards = JSON.parse(localStorage.getItem('pricepilot_selected_bank_cards') || '{}');
    if (typeof savedBankCards === 'object' && savedBankCards !== null) {
      appliedBankCards = savedBankCards;
    }
  } catch (e) {
    appliedBankCards = {};
  }

  // Amazon Bank Card Offers Modal Elements
  const bankOffersModal = document.getElementById('bankOffersModal');
  const closeBankOffersModal = document.getElementById('closeBankOffersModal');
  const bankOffersModalList = document.getElementById('bankOffersModalList');
  const bankOffersModalSubtitle = document.getElementById('bankOffersModalSubtitle');

  function openBankOffersModal(productId) {
    const prod = allProducts.find(p => p.id === parseInt(productId, 10));
    if (!prod || !bankOffersModal) return;
    
    const net = prod.net_pricing || {};
    const offers = net.bank_offers || [];
    const currentSelectedCardId = appliedBankCards[prod.id] || '';

    if (bankOffersModalList) {
      if (offers.length === 0) {
        bankOffersModalList.innerHTML = `<div class="text-subtle" style="padding: 20px; text-align: center;">No partner bank card discounts available for this item.</div>`;
      } else {
        bankOffersModalList.innerHTML = offers.map(b => {
          const isSelected = currentSelectedCardId === b.id;
          const offerTitle = b.offer_title || `Offer ${b.offer_num || 1}`;

          return `
            <div class="amazon-offer-entry" data-offer-id="${b.id}">
              <div class="amazon-offer-header-row">
                <span class="amazon-offer-num-title">${escapeHtml(offerTitle)}</span>
                <button type="button" class="btn-apply-bank-offer ${isSelected ? 'applied' : ''}" data-prod-id="${prod.id}" data-card-id="${b.id}">
                  ${isSelected ? '<i class="fa-solid fa-check"></i> Applied' : 'Apply'}
                </button>
              </div>
              <p class="amazon-offer-desc-text">${escapeHtml(b.offer_desc)}</p>
              <div>
                <a href="#" class="amazon-see-details-link" data-toggle="terms_${prod.id}_${b.id}">See details &gt;</a>
                <div class="amazon-offer-terms-inline hidden" id="terms_${prod.id}_${b.id}">
                  ${escapeHtml(b.terms || 'Standard bank terms and conditions apply.')}
                </div>
              </div>
            </div>
          `;
        }).join('');

        // Attach apply button listeners
        bankOffersModalList.querySelectorAll('.btn-apply-bank-offer').forEach(btn => {
          btn.addEventListener('click', (e) => {
            e.stopPropagation();
            const pid = parseInt(btn.dataset.prodId, 10);
            const cid = btn.dataset.cardId;
            if (appliedBankCards[pid] === cid) {
              clearBankCardOffer(pid);
            } else {
              applyBankCardOffer(pid, cid);
            }
            openBankOffersModal(pid);
          });
        });

        // Attach inline "See details >" toggle listeners
        bankOffersModalList.querySelectorAll('.amazon-see-details-link').forEach(link => {
          link.addEventListener('click', (e) => {
            e.preventDefault();
            e.stopPropagation();
            const targetId = link.getAttribute('data-toggle');
            const targetEl = document.getElementById(targetId);
            if (targetEl) {
              const isHidden = targetEl.classList.contains('hidden');
              targetEl.classList.toggle('hidden');
              link.textContent = isHidden ? 'Hide details ▴' : 'See details >';
            }
          });
        });
      }
    }

    bankOffersModal.classList.remove('hidden');
    if (typeof gsap !== 'undefined') {
      gsap.fromTo('#bankOffersModal .modal-content', { scale: 0.9, opacity: 0, y: 15 }, { scale: 1, opacity: 1, y: 0, duration: 0.25, ease: 'power2.out' });
    }
  }

  function hideBankOffersModal() {
    if (bankOffersModal) bankOffersModal.classList.add('hidden');
  }
  if (closeBankOffersModal) closeBankOffersModal.addEventListener('click', hideBankOffersModal);
  if (bankOffersModal) {
    bankOffersModal.addEventListener('click', (e) => {
      if (e.target === bankOffersModal) hideBankOffersModal();
    });
  }

  function applyBankCardOffer(productId, cardId) {
    const prod = allProducts.find(p => p.id === productId);
    if (!prod) return;
    const offers = prod.net_pricing?.bank_offers || [];
    const card = offers.find(o => o.id === cardId);
    if (!card) return;

    appliedBankCards[productId] = cardId;
    try {
      localStorage.setItem('pricepilot_selected_bank_cards', JSON.stringify(appliedBankCards));
    } catch (e) {}

    const discText = formatMoney(card.discount_val, card.discount_val_native, prod.currency);
    showToast(`💳 ${card.bank_name} applied! Saved ${discText} at checkout`, 'success');
    renderProducts();
  }

  function clearBankCardOffer(productId) {
    delete appliedBankCards[productId];
    try {
      localStorage.setItem('pricepilot_selected_bank_cards', JSON.stringify(appliedBankCards));
    } catch (e) {}

    showToast('💳 Bank card offer removed', 'info');
    renderProducts();
  }

  let allProducts = [];
  let currentUser = null;

  // -----------------------------------------------------------------
  // GSAP & ScrollTrigger Animations Suite
  // -----------------------------------------------------------------
  function initGSAPAnimations() {
    if (typeof gsap === 'undefined') return;

    // Top Header Brand Entrance (nav-actions controls remain static & 100% permanently visible)
    gsap.from('.brand-logo, .brand-text', {
      duration: 0.6,
      y: -15,
      opacity: 0,
      stagger: 0.08,
      ease: 'power2.out',
      clearProps: 'all'
    });

    // ScrollTrigger: Elevated Navbar on Scroll
    if (typeof ScrollTrigger !== 'undefined') {
      ScrollTrigger.create({
        start: 'top -40',
        end: 99999,
        toggleClass: { className: 'navbar-scrolled', targets: '.navbar' }
      });

      // ScrollTrigger: KPI Grid Section Reveal
      gsap.from('.kpi-card', {
        scrollTrigger: {
          trigger: '.kpi-grid',
          start: 'top 90%',
          toggleActions: 'play none none none'
        },
        duration: 0.75,
        scale: 0.88,
        y: 25,
        opacity: 0,
        stagger: 0.1,
        ease: 'back.out(1.4)',
        clearProps: 'transform,opacity'
      });

      // ScrollTrigger: Add Section Reveal
      gsap.from('.add-section', {
        scrollTrigger: {
          trigger: '.add-section',
          start: 'top 88%',
          toggleActions: 'play none none none'
        },
        duration: 0.8,
        y: 35,
        opacity: 0,
        ease: 'power3.out',
        clearProps: 'transform,opacity'
      });

      // ScrollTrigger: Products Section Header Reveal
      gsap.from('.products-header', {
        scrollTrigger: {
          trigger: '.products-header',
          start: 'top 88%',
          toggleActions: 'play none none none'
        },
        duration: 0.7,
        y: 25,
        opacity: 0,
        ease: 'power3.out',
        clearProps: 'transform,opacity'
      });
    }
  }

  // -----------------------------------------------------------------
  // Multi-Currency System
  // -----------------------------------------------------------------
  const CURRENCIES = {
    USD: { symbol: '$', rate: 1.0, name: 'USD ($)' },
    INR: { symbol: '₹', rate: 83.50, name: 'INR (₹)' },
    EUR: { symbol: '€', rate: 0.92, name: 'EUR (€)' },
    GBP: { symbol: '£', rate: 0.79, name: 'GBP (£)' },
    CAD: { symbol: 'CA$', rate: 1.36, name: 'CAD (CA$)' },
    AUD: { symbol: 'A$', rate: 1.52, name: 'AUD (A$)' },
    JPY: { symbol: '¥', rate: 155.00, name: 'JPY (¥)' }
  };

  let currentCurrency = localStorage.getItem('app_currency') || 'INR';
  if (!CURRENCIES[currentCurrency]) currentCurrency = 'INR';

  if (currencySelector) {
    currencySelector.value = currentCurrency;
    currencySelector.addEventListener('change', (e) => {
      currentCurrency = e.target.value;
      localStorage.setItem('app_currency', currentCurrency);
      updateCurrencySymbol();
      renderProducts(allProducts);
      updateKPIs(allProducts);
      if (competitorModal && !competitorModal.classList.contains('hidden')) {
        renderCompetitorComparison();
      }
      if (chartModal && !chartModal.classList.contains('hidden') && currentModalHistory.length > 0) {
        renderChart(filterHistoryByTimeframe(currentModalHistory, currentActiveTimeframe), currentModalTargetUSD, currentModalForecast);
      }
      showToast(`Switched display currency to ${CURRENCIES[currentCurrency].name}`, 'info');
    });
  }

  function updateCurrencySymbol() {
    if (targetPriceSymbol) {
      targetPriceSymbol.textContent = CURRENCIES[currentCurrency].symbol;
    }
  }
  updateCurrencySymbol();

  function formatMoney(valUSD, nativePrice = null, nativeCurrency = null) {
    if (valUSD == null || isNaN(valUSD)) return '₹0.00';
    const curr = CURRENCIES[currentCurrency] || CURRENCIES.INR;

    // 1. If viewing in the product's native marketplace currency (e.g. INR product in INR mode, GBP in GBP mode):
    // Use the authentic scraped native_price directly without recalculating
    if (nativeCurrency && nativeCurrency === currentCurrency && nativePrice != null && !isNaN(nativePrice) && Number(nativePrice) > 0) {
      const decimals = currentCurrency === 'JPY' ? 0 : 2;
      const locale = currentCurrency === 'INR' ? 'en-IN' : undefined;
      return `${curr.symbol}${Number(nativePrice).toLocaleString(locale, { minimumFractionDigits: decimals, maximumFractionDigits: decimals })}`;
    }

    // 2. In ALL other cases (e.g. US product in INR mode, or INR product in USD mode):
    // Accurately convert the USD baseline price using the active currency exchange rate
    const converted = Number(valUSD) * curr.rate;
    const decimals = currentCurrency === 'JPY' ? 0 : 2;
    const locale = currentCurrency === 'INR' ? 'en-IN' : undefined;
    return `${curr.symbol}${converted.toLocaleString(locale, { minimumFractionDigits: decimals, maximumFractionDigits: decimals })}`;
  }

  // -----------------------------------------------------------------
  // Dynamic OS System Theme Auto-Detection & 1-Click Navbar Switcher
  // -----------------------------------------------------------------
  function updateThemeIcon(theme) {
    if (!themeToggleBtn) return;
    themeToggleBtn.innerHTML = theme === 'dark' 
      ? '<i class="fa-solid fa-sun" style="color: var(--accent-amber)"></i>' 
      : '<i class="fa-solid fa-moon"></i>';
  }

  function applyDynamicTheme() {
    const savedTheme = localStorage.getItem('app_theme') || localStorage.getItem('landing_theme') || 'dark';
    document.documentElement.setAttribute('data-theme', savedTheme);
    updateThemeIcon(savedTheme);
  }

  applyDynamicTheme();

  if (window.matchMedia) {
    window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', () => {
      if (!localStorage.getItem('app_theme') && !localStorage.getItem('landing_theme')) {
        applyDynamicTheme();
      }
    });
  }

  if (themeToggleBtn) {
    themeToggleBtn.addEventListener('click', () => {
      const current = document.documentElement.getAttribute('data-theme') || 'dark';
      const nextTheme = current === 'dark' ? 'light' : 'dark';
      document.documentElement.setAttribute('data-theme', nextTheme);
      localStorage.setItem('app_theme', nextTheme);
      localStorage.setItem('landing_theme', nextTheme);
      updateThemeIcon(nextTheme);
      showToast(`Switched theme to ${nextTheme === 'light' ? 'Light Architectural Mode ☀️' : 'Dark Monochrome Mode 🌙'}`, 'info');
    });
  }

  // -----------------------------------------------------------------
  // API Calls & Data Fetching
  // -----------------------------------------------------------------
  // -----------------------------------------------------------------
  // API Calls & Data Fetching
  // -----------------------------------------------------------------
  async function fetchProducts() {
    try {
      const res = await fetch('/api/products');
      const data = await res.json();
      if (data.status === 'success') {
        allProducts = data.products;
        renderProducts(allProducts);
        updateKPIs(allProducts);
      }
    } catch (err) {
      showToast('Error connecting to backend API', 'error');
    }
  }

  async function fetchSchedulerStatus() {
    try {
      const res = await fetch('/api/scheduler/status');
      const data = await res.json();
      if (data.status === 'success') {
        const s = data.scheduler;
        if (schedulerPillText) {
          schedulerPillText.textContent = s.running ? `Sync: Active (${s.interval_minutes}m)` : 'Sync: Paused';
        }
        if (schedulerStatusPill) {
          schedulerStatusPill.className = s.running ? 'scheduler-pill running' : 'scheduler-pill paused';
        }
        if (schedulerMenuStatusText) {
          schedulerMenuStatusText.textContent = s.running ? `Active (${s.interval_minutes}m)` : 'Paused';
        }
        if (toggleSchedulerBtn) {
          toggleSchedulerBtn.className = s.running ? 'toggle-switch-btn active' : 'toggle-switch-btn';
        }
        if (statScraperStatus) {
          statScraperStatus.innerHTML = s.running 
            ? `<span class="radar-dot"></span> Active (${s.interval_minutes}m)` 
            : `<span class="radar-dot paused"></span> Paused`;
        }
      }
    } catch (err) {
      console.warn('Error fetching scheduler status:', err);
    }
  }

  // -----------------------------------------------------------------
  // Smooth KPI Counter Roll-Up Animations
  // -----------------------------------------------------------------
  function animateCounter(el, targetValue, type = 'int') {
    if (!el) return;
    const prevStr = el.getAttribute('data-val') || '0';
    const startVal = parseFloat(prevStr) || 0;
    const endVal = parseFloat(targetValue) || 0;
    el.setAttribute('data-val', endVal);

    if (typeof gsap !== 'undefined') {
      const state = { val: startVal };
      gsap.to(state, {
        val: endVal,
        duration: 0.9,
        ease: 'power2.out',
        onUpdate: () => {
          if (type === 'currency') {
            el.textContent = formatMoney(state.val);
          } else if (type === 'pct') {
            el.textContent = `${state.val.toFixed(1)}%`;
          } else {
            el.textContent = Math.round(state.val).toLocaleString();
          }
        }
      });
    } else {
      if (type === 'currency') {
        el.textContent = formatMoney(endVal);
      } else if (type === 'pct') {
        el.textContent = `${endVal.toFixed(1)}%`;
      } else {
        el.textContent = Math.round(endVal).toLocaleString();
      }
    }
  }

  async function updateKPIs(products) {
    if (statTotalProducts) animateCounter(statTotalProducts, products.length, 'int');
    
    const priceDrops = products.filter(p => p.current_price <= (p.target_price || 0));
    if (statPriceDrops) animateCounter(statPriceDrops, priceDrops.length, 'int');

    try {
      const res = await fetch('/api/kpis');
      const data = await res.json();
      if (data.status === 'success') {
        const k = data.kpis;
        if (statTotalSavings) {
          animateCounter(statTotalSavings, k.total_savings, 'currency');
        }
        if (statAvgDiscount) {
          animateCounter(statAvgDiscount, k.avg_discount, 'pct');
        }
      }
    } catch (err) {
      const totalSavings = products.reduce((acc, p) => acc + (p.potential_savings || 0), 0);
      if (statTotalSavings) animateCounter(statTotalSavings, totalSavings, 'currency');
    }
  }

  // -----------------------------------------------------------------
  // Dynamic Inline SVG Sparklines Generator
  // -----------------------------------------------------------------
  function generateSparklineSvg(p) {
    const cur = parseFloat(p.current_price) || 100;
    const high = Math.max(parseFloat(p.highest_price) || cur, parseFloat(p.original_price) || cur, cur * 1.06);
    const low = Math.min(parseFloat(p.lowest_price) || cur, cur * 0.94);
    
    // Deterministic 6-point price history simulation based on product ID
    const seed = ((p.id || 1) * 37) % 100;
    const p1 = high * (0.96 + (seed % 5) * 0.01);
    const p2 = (high + cur) / 2 + ((seed % 2 === 0 ? 1 : -1) * (high - low) * 0.12);
    const p3 = Math.max(low, (high * 0.35 + cur * 0.65) + ((seed % 3 === 0 ? -1 : 1) * (high - low) * 0.08));
    const p4 = (low + cur) / 2 + ((seed % 4 === 0 ? 1 : -1) * (high - low) * 0.05);
    const p5 = low * (1.01 + (seed % 3) * 0.01);
    const p6 = cur;
    
    const values = [p1, p2, p3, p4, p5, p6];
    const min = Math.min(...values) * 0.99;
    const max = Math.max(...values) * 1.01;
    const range = (max - min) || 1;
    
    const width = 280;
    const height = 36;
    const pad = 4;
    
    const pts = values.map((val, idx) => {
      const x = Math.round((idx / (values.length - 1)) * (width - pad * 2) + pad);
      const y = Math.round(height - pad - ((val - min) / range) * (height - pad * 2));
      return { x, y, val };
    });
    
    const pathD = pts.reduce((acc, pt, i) => (i === 0 ? `M ${pt.x} ${pt.y}` : `${acc} L ${pt.x} ${pt.y}`), '');
    const areaD = `${pathD} L ${pts[pts.length - 1].x} ${height} L ${pts[0].x} ${height} Z`;
    
    const isDownTrend = p6 <= p1;
    const strokeColor = isDownTrend ? '#10b981' : '#e8caae';
    const gradId = `spark-grad-${p.id || Math.round(Math.random() * 1000)}`;
    const trendClass = isDownTrend ? 'trend-down' : 'trend-up';
    const deltaPct = Math.abs(((p6 - p1) / (p1 || 1)) * 100).toFixed(1);
    const trendIcon = isDownTrend ? 'fa-arrow-trend-down' : 'fa-arrow-trend-up';
    const trendLabel = isDownTrend ? `-${deltaPct}% 30d` : `+${deltaPct}% 30d`;
    
    return `
      <div class="card-sparkline-wrap">
        <div class="sparkline-header">
          <span class="sparkline-label"><i class="fa-solid fa-chart-line" style="color: var(--accent-biscuit)"></i> 30-Day Trajectory</span>
          <span class="sparkline-delta-pill ${trendClass}"><i class="fa-solid ${trendIcon}"></i> ${trendLabel}</span>
        </div>
        <svg class="sparkline-svg" viewBox="0 0 ${width} ${height}" preserveAspectRatio="none">
          <defs>
            <linearGradient id="${gradId}" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stop-color="${strokeColor}" stop-opacity="0.38"/>
              <stop offset="100%" stop-color="${strokeColor}" stop-opacity="0.0"/>
            </linearGradient>
          </defs>
          <path d="${areaD}" fill="url(#${gradId})" class="sparkline-area" />
          <path d="${pathD}" fill="none" stroke="${strokeColor}" class="sparkline-path" />
          <circle cx="${pts[pts.length - 1].x}" cy="${pts[pts.length - 1].y}" r="3.5" fill="${strokeColor}" class="sparkline-dot" />
        </svg>
      </div>
    `;
  }

  // -----------------------------------------------------------------
  // Interactive Card Pop-Up Hover & Dynamic Sheen (No Flip-Flop/Tilt)
  // -----------------------------------------------------------------
  function initCardPopup() {
    const cards = document.querySelectorAll('.product-card');
    cards.forEach(card => {
      card.onmouseenter = () => {
        card.style.transition = 'transform 0.28s cubic-bezier(0.34, 1.56, 0.64, 1), box-shadow 0.28s ease';
        card.style.transform = 'translateY(-10px) scale(1.03)';
      };

      card.onmousemove = (e) => {
        const rect = card.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;
        card.style.setProperty('--mouse-x', `${((x / rect.width) * 100).toFixed(1)}%`);
        card.style.setProperty('--mouse-y', `${((y / rect.height) * 100).toFixed(1)}%`);
      };
      
      card.onmouseleave = () => {
        card.style.transition = 'transform 0.35s cubic-bezier(0.34, 1.56, 0.64, 1), box-shadow 0.35s ease';
        card.style.transform = 'translateY(0px) scale(1)';
      };
    });
  }

  // -----------------------------------------------------------------
  // Intelligent Product DP (Display Picture) Resolver
  // -----------------------------------------------------------------
  function getProductDP(p) {
    if (p.image_url && !p.image_url.includes('placeholder.svg') && !p.image_url.includes('unsplash.com')) {
      return p.image_url;
    }
    const text = ((p.title || '') + ' ' + (p.category || '') + ' ' + (p.asin || '')).toLowerCase();
    if (text.includes('keyboard') || text.includes('mechanical') || text.includes('keychron') || text.includes('typing')) {
      return '/static/images/products/mechanical_keyboard.jpg';
    }
    if (text.includes('mouse') || text.includes('trackball') || text.includes('mx master') || text.includes('logitech')) {
      return '/static/images/products/mx_master_3s.jpg';
    }
    if (text.includes('dock') || text.includes('thunderbolt') || text.includes('anker 577') || text.includes('docking')) {
      return '/static/images/products/anker_dock.jpg';
    }
    if (text.includes('power bank') || text.includes('xiaomi') || text.includes('20000mah') || text.includes('charger')) {
      return '/static/images/products/xiaomi_powerbank.jpg';
    }
    if (text.includes('bose') || text.includes('qc45') || text.includes('quietcomfort')) {
      return '/static/images/products/bose_qc45.jpg';
    }
    if (text.includes('oneplus') || text.includes('nord') || text.includes('earbud') || text.includes('tws')) {
      return '/static/images/products/oneplus_buds_2.jpg';
    }
    if (text.includes('airpod')) {
      return '/static/images/products/airpods_pro_2.jpg';
    }
    if (text.includes('ch720n') || text.includes('wh-ch')) {
      return '/static/images/products/sony_whch720n.jpg';
    }
    if (text.includes('headphone') || text.includes('audio') || text.includes('sony') || text.includes('wh-1000')) {
      return '/static/images/products/sony_wh1000xm5.jpg';
    }
    if (text.includes('macbook pro') || text.includes('m4')) {
      return '/static/images/products/macbook_pro_m4.jpg';
    }
    if (text.includes('laptop') || text.includes('macbook') || text.includes('notebook') || text.includes('computer') || text.includes('pc') || text.includes('dell') || text.includes('asus') || text.includes('m3')) {
      return '/static/images/products/macbook_air_m3.jpg';
    }
    if (text.includes('shirt') || text.includes('apparel') || text.includes('clothing') || text.includes('analyst') || text.includes('data')) {
      return '/static/images/products/data_tshirt.jpg';
    }
    return '/static/images/products/sony_wh1000xm5.jpg';
  }

  // -----------------------------------------------------------------
  // Render Products Grid & Trigger GSAP Animations
  // -----------------------------------------------------------------
  function renderProducts(products) {
    const searchTerm = searchFilter ? searchFilter.value.toLowerCase().trim() : '';
    const cat = categoryFilter ? categoryFilter.value : 'ALL';
    const recFilter = recommendationFilter ? recommendationFilter.value : 'ALL';
    const sortVal = sortFilter ? sortFilter.value : 'DEFAULT';

    let filtered = products.filter(p => {
      const matchSearch = p.title.toLowerCase().includes(searchTerm) || p.asin.toLowerCase().includes(searchTerm);
      if (!matchSearch) return false;

      if (cat === 'DEALS' && !(p.current_price <= (p.target_price || 0))) {
        return false;
      }

      if (recFilter !== 'ALL') {
        if (p.recommendation !== recFilter) return false;
      }

      return true;
    });

    // Update Header Live Monitored Products Counter Badge
    const productCounterBadge = document.getElementById('productCounterBadge');
    if (productCounterBadge) {
      productCounterBadge.textContent = filtered.length;
    }

    // Smart Sorting
    if (sortVal === 'DISCOUNT_DESC') {
      filtered.sort((a, b) => (b.discount_pct || 0) - (a.discount_pct || 0));
    } else if (sortVal === 'SAVINGS_DESC') {
      filtered.sort((a, b) => (b.potential_savings || 0) - (a.potential_savings || 0));
    } else if (sortVal === 'PRICE_ASC') {
      filtered.sort((a, b) => (a.current_price || 0) - (b.current_price || 0));
    } else if (sortVal === 'PRICE_DESC') {
      filtered.sort((a, b) => (b.current_price || 0) - (a.current_price || 0));
    } else if (sortVal === 'NAME_ASC') {
      filtered.sort((a, b) => a.title.localeCompare(b.title));
    }

    if (filtered.length === 0) {
      productsGrid.innerHTML = '';
      if (searchTerm) {
        emptyState.innerHTML = `
          <div class="empty-state-icon"><i class="fa-solid fa-magnifying-glass"></i></div>
          <h3>No Monitored Products Found for "${escapeHtml(searchTerm)}"</h3>
          <p>This item is not yet in your tracked list. Click below to search all of Amazon in real-time:</p>
          <button id="searchAmazonFromEmptyBtn" class="btn btn-accent" style="margin-top: 12px;">
            <i class="fa-solid fa-bolt"></i> Live Search Amazon for "${escapeHtml(searchTerm)}"
          </button>
        `;
        const emptyBtn = document.getElementById('searchAmazonFromEmptyBtn');
        if (emptyBtn) {
          emptyBtn.addEventListener('click', () => {
            if (tabModeSearch) tabModeSearch.click();
            if (searchAmazonQueryInput) {
              searchAmazonQueryInput.value = searchTerm;
              executeLiveSearch(searchTerm);
            }
          });
        }
      } else {
        emptyState.innerHTML = `
          <div class="empty-state-icon"><i class="fa-solid fa-box-open"></i></div>
          <h3>No tracked products found</h3>
          <p>Add an Amazon product URL or click a Quick Add sample chip to start tracking!</p>
        `;
      }
      emptyState.classList.remove('hidden');
      return;
    }

    emptyState.classList.add('hidden');
    productsGrid.innerHTML = filtered.map(p => {
      const net = p.net_pricing || {};
      const bankOffers = net.bank_offers || [];
      const selectedBankCardId = appliedBankCards[p.id] || '';
      const activeBankCard = bankOffers.find(b => b.id === selectedBankCardId) || null;
      const bankDiscountVal = activeBankCard ? activeBankCard.discount_val : 0;
      const bankDiscountNative = activeBankCard ? activeBankCard.discount_val_native : null;

      const isIndianProduct = (p.currency === 'INR' || p.region === 'IN');
      const effectivePrice = Math.max(1, p.current_price - bankDiscountVal);
      const effectiveNativePrice = (isIndianProduct && p.native_price && p.current_price) 
        ? Math.max(1, p.native_price - (bankDiscountVal * (p.native_price / p.current_price))) 
        : null;

      const target = p.target_price || (p.current_price * 0.9);
      const diff = effectivePrice - target;
      const isDeal = diff <= 0;
      
      const targetNative = (isIndianProduct && p.native_price && p.current_price) 
        ? (target * (p.native_price / p.current_price)) 
        : null;
      const diffNative = (isIndianProduct && effectiveNativePrice != null && effectivePrice) 
        ? (effectiveNativePrice - (targetNative || target)) 
        : null;

      let statusText = '';
      let fillWidth = 100;
      let barClass = 'deal-pending';

      if (isDeal) {
        const dealNotes = [];
        if (activeBankCard) dealNotes.push(activeBankCard.bank_code || 'Card Offer');
        const noteText = dealNotes.length > 0 ? ` (${dealNotes.join(' + ')} Applied)` : '';
        statusText = `🔥 Deal Active! Price is ${formatMoney(Math.abs(diff), diffNative != null ? Math.abs(diffNative) : null, p.currency)} below target${noteText}`;
        fillWidth = 100;
        barClass = 'deal-active';
      } else {
        statusText = `🎯 Target Goal: Needs ${formatMoney(diff, diffNative, p.currency)} drop to trigger alert`;
        const basePrice = Math.max(p.original_price || p.current_price, p.current_price * 1.25);
        const progressPct = Math.max(15, Math.min(95, Math.round(((basePrice - effectivePrice) / (basePrice - target)) * 100)));
        fillWidth = isNaN(progressPct) ? 50 : progressPct;
        barClass = 'deal-pending';
      }

      const discountPct = p.discount_pct || (
        p.original_price && p.original_price > p.current_price
          ? Math.round(((p.original_price - p.current_price) / p.original_price) * 100)
          : 0
      );

      // Smart Recommendation
      const rec = p.recommendation || 'FAIR_PRICE';
      const recLabel = p.recommendation_label || (rec === 'BUY_NOW' ? 'Buy Now' : (rec === 'FAIR_PRICE' ? 'Fair Price' : 'Wait for Drop'));
      const recIcon = rec === 'BUY_NOW' ? 'fa-bolt' : (rec === 'FAIR_PRICE' ? 'fa-circle-check' : 'fa-clock');
      const recClass = rec === 'BUY_NOW' ? 'rec-buy-now' : (rec === 'FAIR_PRICE' ? 'rec-fair-price' : 'rec-wait');

      // Volatility
      const vol = (p.volatility || 'Stable').toLowerCase();
      const volTag = `<span class="volatility-tag vol-${vol}"><i class="fa-solid fa-wave-square"></i> ${p.volatility || 'Stable'}</span>`;

      // Regional Flag
      const regionBadge = p.region && p.region !== 'US' ? `<span class="region-badge">${p.region === 'IN' ? '🇮🇳 IN' : (p.region === 'UK' ? '🇬🇧 UK' : (p.region === 'CA' ? '🇨🇦 CA' : (p.region === 'DE' ? '🇩🇪 DE' : p.region)))}</span>` : '';

      // Potential Savings Tag
      const savingsBadge = p.potential_savings > 0 ? `<span class="savings-tag"><i class="fa-solid fa-piggy-bank"></i> Save ${formatMoney(p.potential_savings)}</span>` : '';

      // Deal Score Pill
      const dealScore = p.deal_score || 50;
      const dealLabel = p.deal_label || `🔥 ${dealScore}% Deal`;
      const dealScoreBadge = `<span class="deal-score-pill" title="${p.deal_label || 'Deal Score'}" style="font-size: 0.72rem; padding: 2px 8px; border-radius: 9999px; background: rgba(16, 185, 129, 0.2); color: #10b981; font-weight: 700; border: 1px solid rgba(16, 185, 129, 0.4);"><i class="fa-solid fa-fire"></i> ${dealLabel}</span>`;

      // 0. AI Purchasing Verdict Badge
      const verd = p.buying_verdict || {};
      const verdictBadge = verd.verdict 
        ? `<span class="badge-verdict ${verd.badge_class || 'verdict-fair'}" title="${escapeHtml(verd.rationale || '')}"><i class="fa-solid ${verd.icon || 'fa-circle-check'}"></i> ${verd.verdict_label || 'Buy'}</span>`
        : '';

      // 1. Deceptive Pricing & Fake Sale Detector Badge
      const dec = p.deceptive_pricing || {};
      let deceptiveBadge = '';
      if (dec.is_deceptive) {
        deceptiveBadge = `<span class="badge-deceptive" title="${escapeHtml(dec.summary || 'Artificial Price Hike')}"><i class="fa-solid fa-triangle-exclamation"></i> Fake Sale +${dec.inflation_pct || 0}%</span>`;
      } else if (dec.status === 'VERIFIED_MSRP') {
        deceptiveBadge = `<span class="badge-verified-msrp" title="${escapeHtml(dec.summary || 'Verified Street Price')}"><i class="fa-solid fa-tag"></i> Street Price</span>`;
      } else if (dec.status === 'ALL_TIME_LOW') {
        deceptiveBadge = `<span class="badge-authentic-deal" title="${escapeHtml(dec.summary || 'All-Time Low Price')}"><i class="fa-solid fa-bolt"></i> All-Time Low</span>`;
      } else if (discountPct > 0 || (dec.real_discount_pct && dec.real_discount_pct > 0)) {
        deceptiveBadge = `<span class="badge-authentic-deal" title="${escapeHtml(dec.summary || 'Verified Baseline Discount')}"><i class="fa-solid fa-shield-check"></i> Authentic Deal</span>`;
      }

      // 2. Review Authenticity Trust Badge
      const rev = p.review_intelligence || {};
      const trustBadge = rev.trust_grade 
        ? `<span class="trust-badge grade-${rev.trust_grade}" title="Authenticity: ${rev.authenticity_score || 90}% (${rev.trust_grade} Grade)"><i class="fa-solid fa-shield"></i> Trust: ${rev.trust_grade}</span>`
        : '';

      // 3. 7-Day ML Price Drop Predictor Probability Badge
      const dropPred = p.drop_prediction || {};
      const dropProbBadge = dropPred.probability_pct 
        ? `<span class="drop-prob-badge prob-${(dropPred.likelihood_tier || 'moderate').toLowerCase()}" title="${dropPred.rationale || 'Price Drop Probability'}"><i class="fa-solid fa-chart-line-down"></i> ${dropPred.probability_pct}% Drop</span>`
        : '';

      // 5. Multi-Item Basket Arbitrage Selector
      const isBasketChecked = basketSelectedIds.has(p.id);
      const basketCheckbox = `
        <label class="basket-checkbox-label ${isBasketChecked ? 'basket-checked' : ''}" title="Select item for multi-store basket arbitrage comparison">
          <input type="checkbox" class="basket-item-check" data-id="${p.id}" ${isBasketChecked ? 'checked' : ''}>
          <i class="fa-solid ${isBasketChecked ? 'fa-cart-shopping' : 'fa-cart-plus'}"></i>
          <span>Cart</span>
        </label>
      `;

      const resolvedImage = getProductDP(p);

      return `
        <div class="product-card glass ${isDeal ? 'deal-featured' : ''}" data-id="${p.id}">
          <div class="card-glare"></div>
          <div class="card-badges-header">
            <div style="display: flex; align-items: center; gap: 8px;">
              <span class="rec-badge ${recClass}"><i class="fa-solid ${recIcon}"></i> ${recLabel}</span>
              ${basketCheckbox}
            </div>
            <div class="card-meta-tags">
              ${verdictBadge}
              ${deceptiveBadge}
              ${trustBadge}
              ${dropProbBadge}
              ${dealScoreBadge}
              ${regionBadge}
              ${volTag}
              ${savingsBadge}
            </div>
          </div>

          <div class="card-top">
            <div class="product-img-wrapper">
              <img src="${resolvedImage}" alt="${p.title}" class="product-img" referrerpolicy="no-referrer" onerror="this.onerror=null; this.src='/static/images/products/sony_wh1000xm5.jpg';">
              <div class="rating-badge"><i class="fa-solid fa-star"></i> ${p.rating || '4.5'}</div>
            </div>
            <div class="card-details">
              <span class="product-category">${p.category || 'Electronics'} &bull; ASIN: ${p.asin}</span>
              <h4 class="product-title" title="${p.title}">${p.title}</h4>
              <div class="price-row">
                <span class="current-price ${activeBankCard ? 'price-discounted' : ''}">${formatMoney(effectivePrice, effectiveNativePrice, p.currency)}</span>
                ${activeBankCard ? `
                  <span class="original-price" style="text-decoration: line-through;" title="Original Amazon Price">${formatMoney(p.current_price, isIndianProduct ? p.native_price : null, p.currency)}</span>
                ` : (p.original_price ? `<span class="original-price">${formatMoney(p.original_price, isIndianProduct && p.native_price ? (p.native_price * 1.15) : null, p.currency)}</span>` : '')}
                ${activeBankCard ? `
                  <span class="badge-bank-applied" title="${activeBankCard.offer_desc}"><i class="fa-solid fa-credit-card"></i> -${formatMoney(bankDiscountVal, bankDiscountNative, p.currency)} ${activeBankCard.bank_code || 'Card'}</span>
                ` : ''}
                ${discountPct > 0 && !activeBankCard ? `<span class="deal-badge">-${discountPct}% OFF</span>` : ''}
                ${isDeal ? `<span class="deal-badge"><i class="fa-solid fa-fire"></i> Target Met!</span>` : ''}
              </div>

              <!-- Amazon Bank Card Offers Row -->
              ${bankOffers.length > 0 ? `
                <div class="amazon-bank-row ${activeBankCard ? 'bank-active' : ''}">
                  <div class="bank-row-header" data-id="${p.id}" title="Click to view all bank offers">
                    <span class="bank-badge"><i class="fa-solid fa-percent"></i> Bank Offer</span>
                    <span class="bank-title-text" title="${activeBankCard ? activeBankCard.offer_desc : 'Click to view bank offers'}">
                      ${activeBankCard ? `<strong>${activeBankCard.bank_name}:</strong> Save ${formatMoney(bankDiscountVal, bankDiscountNative, p.currency)}` : `Upto ${formatMoney(Math.max(...bankOffers.map(b => b.discount_val)), Math.max(...bankOffers.map(b => b.discount_val_native || b.discount_val)), p.currency)} discount on partner cards`}
                    </span>
                    <span class="bank-view-terms" data-id="${p.id}" title="View all partner bank card discounts">${bankOffers.length} offers &gt;</span>
                  </div>
                  <div class="bank-select-wrapper">
                    <select class="bank-card-dropdown" data-id="${p.id}" title="Choose your bank card to apply instant discount">
                      <option value="">No Card Applied (Full Price)</option>
                      ${bankOffers.map(b => `
                        <option value="${b.id}" ${selectedBankCardId === b.id ? 'selected' : ''}>
                          ${b.offer_title || 'Offer'}: ${b.bank_name} - Save ${formatMoney(b.discount_val, b.discount_val_native, p.currency)}
                        </option>
                      `).join('')}
                    </select>
                  </div>
                </div>
              ` : ''}
            </div>
          </div>

          ${generateSparklineSvg(p)}

          <div class="target-progress">
            <div class="target-status-badge ${isDeal ? 'status-deal' : 'status-pending'}">
              <span>${statusText}</span>
            </div>
            <div class="target-labels">
              <span>Alert Target: <strong>${formatMoney(target, targetNative, p.currency)}</strong></span>
              <span>30-Day Low: <strong>${formatMoney(p.lowest_price || p.current_price, (isIndianProduct && p.native_price && p.current_price && p.lowest_price) ? (p.lowest_price * (p.native_price / p.current_price)) : null, p.currency)}</strong></span>
            </div>
            <div class="progress-bar-bg" title="${fillWidth}% progress towards alert price">
              <div class="progress-bar-fill ${barClass}" style="width: ${fillWidth}%;"></div>
            </div>
          </div>

          <div class="card-actions">
            <!-- Tier 1: Timestamp & Quick Action Icons (Refresh, Alert, Delete) -->
            <div class="card-actions-meta">
              <span class="scraped-time" title="Last checked live on Amazon">
                <i class="fa-regular fa-clock"></i> ${p.last_scraped || 'Just now'}
              </span>
              <div class="quick-icons-group">
                <button class="btn btn-sm-icon btn-secondary refresh-single-btn" data-id="${p.id}" title="Re-check live price on Amazon">
                  <i class="fa-solid fa-arrows-rotate"></i>
                </button>
                ${currentUser ? `
                  <button class="btn btn-sm-icon btn-secondary test-alert-btn" data-id="${p.id}" title="Test Alert Email / Webhook">
                    <i class="fa-regular fa-bell"></i>
                  </button>
                ` : `
                  <button class="btn btn-sm-icon btn-secondary test-alert-btn auth-locked-btn" data-id="${p.id}" title="Log in to unlock email alerts">
                    <i class="fa-solid fa-lock"></i>
                  </button>
                `}
                <button class="btn btn-sm-icon btn-icon-danger delete-btn" data-id="${p.id}" title="Remove Item from Tracker">
                  <i class="fa-solid fa-trash-can"></i>
                </button>
              </div>
            </div>

            <!-- Tier 2: Primary Actions (Price History & Compare Stores) -->
            <div class="action-buttons-grid">
              <button class="btn btn-sm btn-secondary view-chart-btn btn-grid-action" data-id="${p.id}" title="Price Analytics & Time-Series History">
                <i class="fa-solid fa-chart-line" style="color: var(--accent-primary);"></i> Price History
              </button>
              <button class="btn btn-sm btn-secondary compare-stores-btn btn-grid-action" data-id="${p.id}" title="Compare prices across 18 Indian & Global stores">
                <i class="fa-solid fa-code-compare" style="color: var(--accent-biscuit);"></i> Compare Stores
              </button>
            </div>
          </div>
        </div>
      `;
    }).join('');

    // Attach Card Pop-Up & Sheen Interactions
    initCardPopup();

    // GSAP Staggered Spring Pop-Up Entrance for Cards (No Flip-Flop / Tilt)
    if (typeof gsap !== 'undefined') {
      gsap.fromTo('.product-card', 
        { opacity: 0, y: 40, scale: 0.7 },
        { 
          duration: 0.5, 
          opacity: 1, 
          y: 0, 
          scale: 1, 
          stagger: {
            each: 0.06,
            from: 'start'
          },
          ease: 'back.out(2)', 
          clearProps: 'transform,opacity,visibility' 
        }
      );
    }

    // Event Listeners
    document.querySelectorAll('.refresh-single-btn').forEach(b => {
      b.addEventListener('click', async (e) => {
        e.stopPropagation();
        const id = b.dataset.id;
        const icon = b.querySelector('i');
        if (icon) icon.classList.add('fa-spin');
        b.disabled = true;
        try {
          const res = await fetch(`/api/products/${id}/refresh`, { method: 'POST' });
          const data = await res.json();
          if (data.status === 'success') {
            showToast(data.message || 'Price refreshed!', 'success');
            fetchProducts();
          } else {
            showToast(data.message || 'Failed to refresh price', 'error');
          }
        } catch (err) {
          showToast('Error refreshing product price', 'error');
        } finally {
          if (icon) icon.classList.remove('fa-spin');
          b.disabled = false;
        }
      });
    });

    document.querySelectorAll('.view-chart-btn').forEach(b => {
      b.addEventListener('click', (e) => {
        e.preventDefault();
        e.stopPropagation();
        openChartModal(b.dataset.id);
      });
    });

    document.querySelectorAll('.compare-stores-btn').forEach(b => {
      b.addEventListener('click', (e) => {
        e.preventDefault();
        e.stopPropagation();
        openCompetitorModal(b.dataset.id);
      });
    });



    document.querySelectorAll('.bank-card-dropdown').forEach(sel => {
      sel.addEventListener('change', (e) => {
        e.stopPropagation();
        const id = parseInt(sel.dataset.id, 10);
        const cardId = sel.value;
        if (cardId) {
          applyBankCardOffer(id, cardId);
        } else {
          clearBankCardOffer(id);
        }
      });
    });

    document.querySelectorAll('.bank-view-terms, .bank-row-header').forEach(el => {
      el.addEventListener('click', (e) => {
        if (e.target.closest('.bank-card-dropdown')) return;
        e.preventDefault();
        e.stopPropagation();
        const id = el.dataset.id || el.closest('[data-id]')?.dataset.id;
        if (id) openBankOffersModal(id);
      });
    });

    document.querySelectorAll('.basket-item-check').forEach(cb => {
      cb.addEventListener('change', (e) => {
        e.stopPropagation();
        const id = parseInt(cb.dataset.id, 10);
        if (cb.checked) {
          basketSelectedIds.add(id);
        } else {
          basketSelectedIds.delete(id);
        }
        updateBasketFloatingBar();
      });
    });

    document.querySelectorAll('.test-alert-btn').forEach(b => {
      b.addEventListener('click', () => openAlertModal(b.dataset.id));
    });

    document.querySelectorAll('.delete-btn').forEach(b => {
      b.addEventListener('click', () => handleDeleteProduct(b.dataset.id));
    });
  }

  // -----------------------------------------------------------------
  // Add Product (URL & Live Search) & Quick Add Chips
  // -----------------------------------------------------------------
  async function addProductByUrl(url, targetPrice = null, metadata = {}) {
    if (!url) return false;

    showToast('Scraping product data from Amazon...', 'info');

    try {
      const payload = { url: url, target_price: targetPrice, ...metadata };
      const res = await fetch('/api/products/add', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      const data = await res.json();
      if (data.status === 'success') {
        showToast(`Successfully tracked: ${data.product.title.substring(0, 32)}...`, 'success');
        if (productUrlInput) productUrlInput.value = '';
        if (targetPriceInput) targetPriceInput.value = '';
        fetchProducts();
        return true;
      } else {
        showToast(data.message || 'Failed to add product', 'error');
        return false;
      }
    } catch (err) {
      showToast('Error adding product', 'error');
      return false;
    }
  }

  if (addProductForm) {
    addProductForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const url = productUrlInput.value.trim();
      let targetPrice = targetPriceInput.value;

      if (!url) return;

      if (targetPrice) {
        const rate = CURRENCIES[currentCurrency].rate;
        targetPrice = (parseFloat(targetPrice) / rate).toFixed(2);
      }

      await addProductByUrl(url, targetPrice);
    });
  }

  // Live Amazon Search Mode Toggles & Execution
  const tabModeUrl = document.getElementById('tabModeUrl');
  const tabModeSearch = document.getElementById('tabModeSearch');
  const searchAmazonContainer = document.getElementById('searchAmazonContainer');
  const searchAmazonForm = document.getElementById('searchAmazonForm');
  const searchAmazonQueryInput = document.getElementById('searchAmazonQueryInput');
  const searchAmazonRegionSelect = document.getElementById('searchAmazonRegionSelect');
  const liveSearchResults = document.getElementById('liveSearchResults');
  const searchAmazonSubmitBtn = document.getElementById('searchAmazonSubmitBtn');
  const searchSuggestionsBox = document.getElementById('searchSuggestionsBox');
  const suggestionChipsWrap = document.getElementById('suggestionChipsWrap');
  const searchAmazonTargetPreset = document.getElementById('searchAmazonTargetPreset');
  let searchDebounceTimer = null;

  if (tabModeUrl && tabModeSearch) {
    tabModeUrl.addEventListener('click', () => {
      tabModeUrl.classList.add('active');
      tabModeUrl.style.background = '';
      tabModeUrl.style.color = '';
      tabModeSearch.classList.remove('active');
      tabModeSearch.style.background = '';
      tabModeSearch.style.color = '';
      addProductForm.classList.remove('hidden');
      searchAmazonContainer.classList.add('hidden');
    });

    tabModeSearch.addEventListener('click', () => {
      tabModeSearch.classList.add('active');
      tabModeSearch.style.background = '';
      tabModeSearch.style.color = '';
      tabModeUrl.classList.remove('active');
      tabModeUrl.style.background = '';
      tabModeUrl.style.color = '';
      addProductForm.classList.add('hidden');
      searchAmazonContainer.classList.remove('hidden');
      if (searchAmazonQueryInput) searchAmazonQueryInput.focus();
      // If no search results currently rendered, automatically show full catalog
      if (!liveSearchResults.querySelector('.search-result-card')) {
        executeLiveSearch('');
      }
    });
  }

  // Live Search Autocomplete Suggestions
  async function fetchLiveSuggestions(val) {
    const q = (val || '').trim();
    if (!q || q.length < 2) {
      if (searchSuggestionsBox) searchSuggestionsBox.classList.add('hidden');
      return;
    }

    const region = searchAmazonRegionSelect ? searchAmazonRegionSelect.value : 'IN';
    try {
      const res = await fetch(`/api/search/suggestions?q=${encodeURIComponent(q)}&region=${region}`);
      const data = await res.json();
      if (data.status === 'success' && data.suggestions && data.suggestions.length > 0) {
        if (suggestionChipsWrap) {
          suggestionChipsWrap.innerHTML = data.suggestions.map(s => `
            <button type="button" class="suggestion-chip" data-query="${s}">
              <i class="fa-solid fa-magnifying-glass" style="font-size: 0.65rem; opacity: 0.7;"></i> ${s}
            </button>
          `).join('');

          suggestionChipsWrap.querySelectorAll('.suggestion-chip').forEach(btn => {
            btn.addEventListener('click', () => {
              const query = btn.dataset.query;
              if (searchAmazonQueryInput) searchAmazonQueryInput.value = query;
              if (searchSuggestionsBox) searchSuggestionsBox.classList.add('hidden');
              executeLiveSearch(query);
            });
          });
        }
        if (searchSuggestionsBox) searchSuggestionsBox.classList.remove('hidden');
      } else {
        if (searchSuggestionsBox) searchSuggestionsBox.classList.add('hidden');
      }
    } catch (err) {
      if (searchSuggestionsBox) searchSuggestionsBox.classList.add('hidden');
    }
  }

  let liveSearchDebounceTimer = null;
  let currentSearchAbortController = null;
  let currentSearchSeq = 0;

  if (searchAmazonQueryInput) {
    searchAmazonQueryInput.addEventListener('input', (e) => {
      const rawVal = e.target.value;
      const val = rawVal.trim();
      clearTimeout(searchDebounceTimer);
      searchDebounceTimer = setTimeout(() => {
        fetchLiveSuggestions(val);
      }, 200);

      // Instant live search execution as user types (450ms debounce, minimum 2 characters)
      clearTimeout(liveSearchDebounceTimer);
      if (val.length >= 2) {
        liveSearchDebounceTimer = setTimeout(() => {
          executeLiveSearch(val);
        }, 450);
      } else if (val.length === 0) {
        if (currentSearchAbortController) {
          try { currentSearchAbortController.abort(); } catch (e) {}
        }
        if (searchSuggestionsBox) searchSuggestionsBox.classList.add('hidden');
        if (liveSearchResults) {
          liveSearchResults.classList.add('hidden');
          liveSearchResults.innerHTML = '';
        }
      }
    });
  }

  // Trending search pill listeners
  document.querySelectorAll('.trend-search-pill').forEach(pill => {
    pill.addEventListener('click', () => {
      const q = pill.dataset.q;
      if (searchAmazonQueryInput) {
        searchAmazonQueryInput.value = q;
        if (searchSuggestionsBox) searchSuggestionsBox.classList.add('hidden');
        executeLiveSearch(q);
      }
    });
  });

  let currentSearchResults = [];
  let currentSearchActiveCategory = 'ALL';

  // Render search cards with category filter bar and target price calculators
  function renderLiveSearchCards(items, queryText, region) {
    if (!liveSearchResults) return;
    const defaultDiscountMultiplier = searchAmazonTargetPreset ? (parseFloat(searchAmazonTargetPreset.value) || 0.90) : 0.90;

    let filtered = items;
    if (currentSearchActiveCategory !== 'ALL') {
      filtered = items.filter(it => {
        const cat = (it.category || '').toLowerCase();
        const tit = (it.title || '').toLowerCase();
        if (currentSearchActiveCategory === 'laptop') return cat.includes('laptop') || cat.includes('computer') || tit.includes('macbook') || tit.includes('xps') || tit.includes('laptop');
        if (currentSearchActiveCategory === 'phone') return cat.includes('smartphone') || cat.includes('phone') || tit.includes('iphone') || tit.includes('galaxy') || tit.includes('pixel');
        if (currentSearchActiveCategory === 'audio') return cat.includes('audio') || cat.includes('headphone') || tit.includes('buds') || tit.includes('ear') || tit.includes('speaker') || tit.includes('sound');
        if (currentSearchActiveCategory === 'accessories') return cat.includes('accessories') || tit.includes('mouse') || tit.includes('keyboard') || tit.includes('dock') || tit.includes('power bank');
        if (currentSearchActiveCategory === 'kitchen') return cat.includes('kitchen') || tit.includes('coffee') || tit.includes('fryer') || tit.includes('pot');
        if (currentSearchActiveCategory === 'gaming') return cat.includes('gaming') || tit.includes('playstation') || tit.includes('switch') || tit.includes('console');
        return true;
      });
    }

    const titleLead = queryText ? `Found ${items.length} products for "${escapeHtml(queryText)}"` : `Browsing All Amazon Catalog Products (${items.length} items in ${region})`;

    const filterBarHtml = `
      <div class="search-results-meta-header" style="grid-column: 1/-1; display: flex; flex-wrap: wrap; justify-content: space-between; align-items: center; gap: 10px; margin-bottom: 8px; padding-bottom: 10px; border-bottom: 1px solid rgba(255,255,255,0.08);">
        <div style="font-size: 0.85rem; font-weight: 600; color: #cbd5e1; display: flex; align-items: center; gap: 6px;">
          <i class="fa-solid fa-layer-group text-amber" style="color: #f59e0b;"></i>
          <span>${titleLead}</span>
        </div>
        <div class="search-category-filters" style="display: flex; flex-wrap: wrap; gap: 5px;">
          <button type="button" class="btn btn-xs ${currentSearchActiveCategory === 'ALL' ? 'btn-primary' : 'btn-secondary'} search-cat-pill" data-cat="ALL">All (${items.length})</button>
          <button type="button" class="btn btn-xs ${currentSearchActiveCategory === 'laptop' ? 'btn-primary' : 'btn-secondary'} search-cat-pill" data-cat="laptop">💻 Laptops</button>
          <button type="button" class="btn btn-xs ${currentSearchActiveCategory === 'phone' ? 'btn-primary' : 'btn-secondary'} search-cat-pill" data-cat="phone">📱 Phones</button>
          <button type="button" class="btn btn-xs ${currentSearchActiveCategory === 'audio' ? 'btn-primary' : 'btn-secondary'} search-cat-pill" data-cat="audio">🎧 Audio</button>
          <button type="button" class="btn btn-xs ${currentSearchActiveCategory === 'accessories' ? 'btn-primary' : 'btn-secondary'} search-cat-pill" data-cat="accessories">⌨️ Accessories</button>
          <button type="button" class="btn btn-xs ${currentSearchActiveCategory === 'kitchen' ? 'btn-primary' : 'btn-secondary'} search-cat-pill" data-cat="kitchen">☕ Kitchen</button>
          <button type="button" class="btn btn-xs ${currentSearchActiveCategory === 'gaming' ? 'btn-primary' : 'btn-secondary'} search-cat-pill" data-cat="gaming">🎮 Gaming</button>
        </div>
      </div>
    `;

    if (filtered.length === 0) {
      liveSearchResults.innerHTML = filterBarHtml + `<div style="grid-column: 1/-1; text-align: center; padding: 24px; color: #94a3b8;">No products in this specific category. Click "All (${items.length})" to view all items.</div>`;
      liveSearchResults.querySelectorAll('.search-cat-pill').forEach(btn => {
        btn.addEventListener('click', () => {
          currentSearchActiveCategory = btn.dataset.cat;
          renderLiveSearchCards(items, queryText, region);
        });
      });
      return;
    }

    const cardsHtml = filtered.map((item, idx) => {
      const sym = item.symbol || '₹';
      const locale = item.currency === 'INR' ? 'en-IN' : undefined;
      const price = parseFloat(item.price) || 0;
      const priceStr = `${sym}${price.toLocaleString(locale, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
      const initialTarget = Math.round(price * defaultDiscountMultiplier * 100) / 100;
      const initialTargetStr = initialTarget.toFixed(2);
      const productPayload = JSON.stringify(item).replace(/"/g, '&quot;');

      return `
        <div class="search-result-card glass" data-index="${idx}" data-price="${price}" data-currency="${item.currency || 'INR'}">
          <div class="search-card-main">
            <img src="${item.image_url}" alt="${item.title}" class="search-card-img" onerror="this.onerror=null; this.src='/static/images/product-placeholder.svg'">
            <div class="search-card-info">
              <h5 class="search-card-title" title="${item.title}">${item.title}</h5>
              <div class="search-card-meta">
                <span class="search-card-price">${priceStr}</span>
                <span class="search-card-rating"><i class="fa-solid fa-star" style="color: var(--accent-amber);"></i> ${item.rating || 4.5}</span>
                <span class="search-card-region">${item.region || region}</span>
              </div>
            </div>
          </div>

          <!-- Price Set Option (Editable Target Alert Price & Quick % Shortcuts) -->
          <div class="search-target-box">
            <div class="search-target-header">
              <span class="search-target-label"><i class="fa-solid fa-bullseye" style="color: var(--accent-amber);"></i> Alert Target Price</span>
              <div class="search-pct-pills">
                <button type="button" class="search-pct-btn ${defaultDiscountMultiplier === 0.90 ? 'active' : ''}" data-pct="0.90">-10%</button>
                <button type="button" class="search-pct-btn ${defaultDiscountMultiplier === 0.85 ? 'active' : ''}" data-pct="0.85">-15%</button>
                <button type="button" class="search-pct-btn ${defaultDiscountMultiplier === 0.80 ? 'active' : ''}" data-pct="0.80">-20%</button>
                <button type="button" class="search-pct-btn ${defaultDiscountMultiplier === 0.75 ? 'active' : ''}" data-pct="0.75">-25%</button>
              </div>
            </div>
            <div class="search-target-input-row">
              <span class="search-target-symbol">${sym}</span>
              <input type="number" step="0.01" class="search-target-input" value="${initialTargetStr}" placeholder="Set alert target..." title="Enter your custom alert price">
            </div>
          </div>

          <button type="button" class="btn btn-sm btn-accent track-search-item-btn" data-url="${item.url}" data-price="${price}" data-product='${productPayload}'>
            <i class="fa-solid fa-plus"></i> Track with Target (<span class="btn-target-preview">${sym}${initialTargetStr}</span>)
          </button>
        </div>
      `;
    }).join('');

    liveSearchResults.innerHTML = filterBarHtml + cardsHtml;

    // Attach category filter listeners
    liveSearchResults.querySelectorAll('.search-cat-pill').forEach(btn => {
      btn.addEventListener('click', () => {
        currentSearchActiveCategory = btn.dataset.cat;
        renderLiveSearchCards(items, queryText, region);
      });
    });

    // Setup interactive target price adjustments for each card
    liveSearchResults.querySelectorAll('.search-result-card').forEach(card => {
      const itemPrice = parseFloat(card.dataset.price) || 0;
      const targetInput = card.querySelector('.search-target-input');
      const targetPreview = card.querySelector('.btn-target-preview');
      const sym = card.querySelector('.search-target-symbol')?.textContent || '₹';
      const pctBtns = card.querySelectorAll('.search-pct-btn');

      function updateTargetDisplay(val) {
        const num = parseFloat(val);
        if (!isNaN(num) && num > 0) {
          if (targetPreview) targetPreview.textContent = `${sym}${num.toFixed(2)}`;
        } else {
          if (targetPreview) targetPreview.textContent = `${sym}${(itemPrice * 0.9).toFixed(2)}`;
        }
      }

      pctBtns.forEach(pBtn => {
        pBtn.addEventListener('click', (ev) => {
          ev.stopPropagation();
          pctBtns.forEach(b => b.classList.remove('active'));
          pBtn.classList.add('active');
          const mult = parseFloat(pBtn.dataset.pct) || 0.90;
          const calcVal = (itemPrice * mult).toFixed(2);
          if (targetInput) targetInput.value = calcVal;
          updateTargetDisplay(calcVal);
        });
      });

      if (targetInput) {
        targetInput.addEventListener('input', () => {
          pctBtns.forEach(b => b.classList.remove('active'));
          updateTargetDisplay(targetInput.value);
        });
      }
    });

    liveSearchResults.querySelectorAll('.track-search-item-btn').forEach(btn => {
      btn.addEventListener('click', async (ev) => {
        const btnEl = ev.currentTarget;
        const card = btnEl.closest('.search-result-card');
        const targetInput = card?.querySelector('.search-target-input');
        const customTarget = targetInput ? parseFloat(targetInput.value) : null;
        const url = btnEl.dataset.url;
        const price = parseFloat(btnEl.dataset.price);
        let metadata = {};
        try {
          metadata = JSON.parse(btnEl.dataset.product || '{}');
        } catch (e) {}

        btnEl.disabled = true;
        btnEl.innerHTML = `<i class="fa-solid fa-spinner fa-spin"></i> Tracking...`;
        
        // Calculate target price in base USD
        let targetUSD = null;
        const itemCurrency = metadata.currency || 'INR';
        const rate = itemCurrency === 'INR' ? 83.50 : (CURRENCIES[itemCurrency]?.rate || 1.0);

        if (customTarget && !isNaN(customTarget) && customTarget > 0) {
          targetUSD = (customTarget / rate).toFixed(2);
        } else {
          const baseUSD = metadata.base_usd || (price / rate);
          targetUSD = (baseUSD * 0.90).toFixed(2);
        }

        const success = await addProductByUrl(url, targetUSD, metadata);
        if (success) {
          const sym = card?.querySelector('.search-target-symbol')?.textContent || '₹';
          const displayTarget = customTarget ? `${sym}${customTarget.toFixed(2)}` : '';
          btnEl.innerHTML = `<i class="fa-solid fa-circle-check"></i> Tracked at ${displayTarget}!`;
          btnEl.style.background = '#10b981';
        } else {
          btnEl.disabled = false;
          btnEl.innerHTML = `<i class="fa-solid fa-rotate-left"></i> Retry`;
        }
      });
    });
  }

  // Execute Live Search across Amazon Catalog with race-condition prevention & abort handling
  async function executeLiveSearch(query) {
    const q = (query || '').trim();
    if (!q || q.length < 2) {
      if (liveSearchResults) {
        liveSearchResults.classList.add('hidden');
        liveSearchResults.innerHTML = '';
      }
      return;
    }

    if (currentSearchAbortController) {
      try { currentSearchAbortController.abort(); } catch (e) {}
    }
    currentSearchAbortController = new AbortController();
    const searchId = ++currentSearchSeq;

    const region = searchAmazonRegionSelect ? searchAmazonRegionSelect.value : 'IN';

    if (searchAmazonSubmitBtn) {
      searchAmazonSubmitBtn.disabled = true;
      searchAmazonSubmitBtn.innerHTML = `<i class="fa-solid fa-spinner fa-spin"></i> Searching...`;
    }
    liveSearchResults.classList.remove('hidden');
    liveSearchResults.innerHTML = `<div style="grid-column: 1/-1; text-align: center; padding: 24px; color: #94a3b8;"><i class="fa-solid fa-spinner fa-spin"></i> Searching Amazon ${region} in real-time for "${escapeHtml(q)}"...</div>`;

    try {
      const res = await fetch(`/api/search?q=${encodeURIComponent(q)}&region=${region}&limit=40`, {
        signal: currentSearchAbortController.signal
      });
      const data = await res.json();
      if (searchId !== currentSearchSeq) {
        // Newer search initiated, discard stale response
        return;
      }
      if (data.status === 'success' && data.results && data.results.length > 0) {
        currentSearchResults = data.results;
        currentSearchActiveCategory = 'ALL';
        renderLiveSearchCards(currentSearchResults, q, region);
      } else {
        liveSearchResults.innerHTML = `<div style="grid-column: 1/-1; text-align: center; padding: 20px; color: #94a3b8;">No matching products found for "${escapeHtml(q)}". Try searching a brand or category (e.g. iPhone, Samsung, boAt, Nike, MacBook, Sony).</div>`;
      }
    } catch (err) {
      if (err.name === 'AbortError') {
        return; // Intentionally aborted by newer search
      }
      if (searchId === currentSearchSeq) {
        liveSearchResults.innerHTML = `<div style="grid-column: 1/-1; text-align: center; padding: 20px; color: #ef4444;">Search request failed. Please check network and try again.</div>`;
      }
    } finally {
      if (searchId === currentSearchSeq && searchAmazonSubmitBtn) {
        searchAmazonSubmitBtn.disabled = false;
        searchAmazonSubmitBtn.innerHTML = `<i class="fa-solid fa-magnifying-glass"></i> Search Products`;
      }
    }
  }

  if (searchAmazonForm) {
    searchAmazonForm.addEventListener('submit', (e) => {
      e.preventDefault();
      const q = searchAmazonQueryInput ? searchAmazonQueryInput.value.trim() : '';
      if (searchSuggestionsBox) searchSuggestionsBox.classList.add('hidden');
      executeLiveSearch(q);
    });
  }

  if (searchAmazonRegionSelect) {
    searchAmazonRegionSelect.addEventListener('change', () => {
      const q = searchAmazonQueryInput ? searchAmazonQueryInput.value.trim() : '';
      executeLiveSearch(q);
    });
  }

  if (searchAmazonTargetPreset) {
    searchAmazonTargetPreset.addEventListener('change', () => {
      const mult = parseFloat(searchAmazonTargetPreset.value) || 0.90;
      liveSearchResults.querySelectorAll('.search-result-card').forEach(card => {
        const itemPrice = parseFloat(card.dataset.price) || 0;
        const targetInput = card.querySelector('.search-target-input');
        const targetPreview = card.querySelector('.btn-target-preview');
        const sym = card.querySelector('.search-target-symbol')?.textContent || '₹';
        const calcVal = (itemPrice * mult).toFixed(2);
        if (targetInput) targetInput.value = calcVal;
        if (targetPreview) targetPreview.textContent = `${sym}${calcVal}`;
        card.querySelectorAll('.search-pct-btn').forEach(btn => {
          btn.classList.toggle('active', Math.abs(parseFloat(btn.dataset.pct) - mult) < 0.001);
        });
      });
    });
  }

  // -----------------------------------------------------------------
  // 1-Click Track Popular Presets Handler
  // -----------------------------------------------------------------
  document.querySelectorAll('.quick-add-chip').forEach(chip => {
    chip.addEventListener('click', async () => {
      if (typeof gsap !== 'undefined') {
        gsap.fromTo(chip, { scale: 0.92 }, { scale: 1, duration: 0.25, ease: 'elastic.out(1, 0.4)' });
      }
      const asin = chip.dataset.asin;
      const title = chip.dataset.title || 'Product';
      const presetTarget = chip.dataset.target || null;

      showToast(`Quick Tracking ${title}...`, 'info');
      chip.disabled = true;

      try {
        const res = await fetch('/api/products', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            url: chip.dataset.url || `https://www.amazon.com/dp/${asin}`,
            title: title,
            target_price: presetTarget
          })
        });
        const data = await res.json();
        if (data.status === 'success') {
          showToast(`⚡ Successfully tracked ${title}!`, 'success');
          await fetchProducts();
          fetchNotifications();
          setTimeout(() => {
            const card = document.querySelector(`[data-asin="${asin}"]`) || (data.product ? document.querySelector(`[data-id="${data.product.id}"]`) : null);
            if (card) {
              card.scrollIntoView({ behavior: 'smooth', block: 'center' });
              card.style.transition = 'box-shadow 0.4s ease, border-color 0.4s ease';
              card.style.boxShadow = '0 0 25px var(--accent-primary)';
              card.style.borderColor = 'var(--accent-primary)';
              setTimeout(() => {
                card.style.boxShadow = '';
                card.style.borderColor = '';
              }, 2200);
            }
          }, 350);
        } else {
          showToast(data.message || 'Could not track product', 'error');
        }
      } catch (err) {
        showToast('Network error tracking preset', 'error');
      } finally {
        chip.disabled = false;
      }
    });
  });

  // -----------------------------------------------------------------
  // Delete & Scrape All Actions
  // -----------------------------------------------------------------
  async function handleDeleteProduct(id) {
    if (!confirm('Are you sure you want to stop tracking this product?')) return;

    try {
      const res = await fetch(`/api/products/${id}`, { method: 'DELETE' });
      const data = await res.json();
      if (data.status === 'success') {
        showToast('Product removed from tracker', 'success');
        fetchProducts();
      }
    } catch (err) {
      showToast('Failed to delete product', 'error');
    }
  }

  scrapeAllBtn.addEventListener('click', async () => {
    scrapeAllBtn.disabled = true;
    scrapeAllBtn.querySelector('.spinner-icon').classList.add('spinning');
    showToast('Running live PricePilot check across all items...', 'info');

    try {
      const res = await fetch('/api/products/scrape-all', { method: 'POST' });
      const data = await res.json();
      if (data.status === 'success') {
        showToast(`Check complete! ${data.scraped_count} products updated. ${data.price_drops_detected} price drops detected!`, 'success');
        fetchProducts();
      }
    } catch (err) {
      showToast('Error running PricePilot batch check', 'error');
    } finally {
      scrapeAllBtn.disabled = false;
      scrapeAllBtn.querySelector('.spinner-icon').classList.remove('spinning');
    }
  });

  // -----------------------------------------------------------------
  // Price History Chart Modal & GSAP Pop
  // -----------------------------------------------------------------
  let currentModalHistory = [];
  let currentModalTargetUSD = 0;
  let currentActiveTimeframe = 'ALL';

  function filterHistoryByTimeframe(history, timeframe) {
    if (!history || history.length === 0) return [];
    if (timeframe === '7D') return history.slice(-7);
    if (timeframe === '1M') return history.slice(-30);
    if (timeframe === '3M') return history.slice(-90);
    if (timeframe === '1Y') return history.slice(-365);
    return history;
  }

  let currentModalForecast = null;

  function updateModalForecastBanner(forecast) {
    if (!forecast) return;
    const badge = document.getElementById('forecastSignalBadge');
    const predPrice = document.getElementById('forecastPredictedPrice');
    const range = document.getElementById('forecastPriceRange');
    const sma = document.getElementById('forecastSma7');
    const prob = document.getElementById('forecastDropProb');

    if (badge) {
      badge.textContent = forecast.drop_signal || 'Neutral Channel';
      const isHighDrop = forecast.drop_probability >= 60;
      badge.style.background = isHighDrop ? 'rgba(16, 185, 129, 0.2)' : 'rgba(56, 189, 248, 0.2)';
      badge.style.color = isHighDrop ? 'var(--accent-emerald)' : 'var(--accent-primary)';
      badge.style.borderColor = isHighDrop ? 'rgba(16, 185, 129, 0.4)' : 'rgba(56, 189, 248, 0.4)';
    }
    if (predPrice) predPrice.textContent = formatMoney(forecast.predicted_7d_price);
    if (range) range.textContent = `${formatMoney(forecast.predicted_range_min)} – ${formatMoney(forecast.predicted_range_max)}`;
    if (sma) sma.textContent = formatMoney(forecast.sma_7);
    if (prob) {
      prob.textContent = `${forecast.drop_probability}%`;
      prob.style.color = forecast.drop_probability >= 60 ? 'var(--accent-emerald)' : (forecast.drop_probability >= 40 ? 'var(--accent-amber)' : 'var(--accent-rose)');
    }
  }

  async function openChartModal(id) {
    chartModal.classList.remove('hidden');
    if (typeof gsap !== 'undefined') {
      gsap.fromTo('#chartModal .modal-content', { scale: 0.75, opacity: 0, y: 20 }, { scale: 1, opacity: 1, y: 0, duration: 0.4, ease: 'back.out(1.4)' });
    }

    // Reset timeframe buttons
    currentActiveTimeframe = 'ALL';
    document.querySelectorAll('.timeframe-btn').forEach(b => {
      if (b.dataset.range === 'ALL') {
        b.classList.add('active');
        b.style.background = 'var(--accent-purple, #8b5cf6)';
        b.style.color = 'white';
      } else {
        b.classList.remove('active');
        b.style.background = 'rgba(0,0,0,0.2)';
        b.style.color = 'inherit';
      }
    });

    const badge = document.getElementById('chartDealScoreBadge');
    if (badge) badge.innerHTML = `<i class="fa-solid fa-spinner fa-spin"></i> Calculating Deal Score...`;

    try {
      // Fetch history & deal intelligence in parallel
      const [histRes, dealRes] = await Promise.all([
        fetch(`/api/products/${id}/history`),
        fetch(`/api/products/${id}/deal-analysis`).catch(() => null)
      ]);

      const data = await histRes.json();
      if (data.status === 'success') {
        const prod = data.product;
        currentModalHistory = data.history || [];
        currentModalTargetUSD = prod.target_price || (prod.current_price * 0.9);
        currentModalForecast = data.forecast || null;

        modalProductTitle.textContent = prod.title;
        modalCurrentPrice.textContent = formatMoney(prod.current_price);
        modalTargetPrice.textContent = formatMoney(currentModalTargetUSD);
        modalLowestPrice.textContent = formatMoney(prod.lowest_price || prod.current_price);
        modalHighestPrice.textContent = formatMoney(prod.highest_price || prod.current_price);

        currentModalProductId = id;

        // Populate Top AI Buying Verdict Ribbon
        const verd = prod.buying_verdict || {};
        const vBanner = document.getElementById('modalBuyingVerdictBanner');
        const vIconCircle = document.getElementById('modalVerdictIconCircle');
        const vIcon = document.getElementById('modalVerdictIcon');
        const vTitle = document.getElementById('modalVerdictTitle');
        const vConf = document.getElementById('modalVerdictConfidence');
        const vRationale = document.getElementById('modalVerdictRationale');
        const vSavings = document.getElementById('modalVerdictSavingsVal');
        const vHorizon = document.getElementById('modalVerdictHorizon');

        if (vBanner) {
          vBanner.className = `modal-verdict-banner glass ${verd.badge_class || 'verdict-fair'}`;
        }
        if (vIconCircle) {
          vIconCircle.className = `verdict-icon-circle ${verd.badge_class || 'verdict-fair'}`;
        }
        if (vIcon) {
          vIcon.className = `fa-solid ${verd.icon || 'fa-circle-check'}`;
        }
        if (vTitle) {
          vTitle.textContent = (verd.verdict_label || 'FAIR BUY').toUpperCase();
          vTitle.className = `verdict-badge ${verd.badge_class || 'verdict-fair'}`;
        }
        if (vConf) {
          vConf.textContent = `${verd.confidence_pct || 85}% Confidence`;
        }
        if (vRationale) {
          vRationale.textContent = verd.rationale || 'Analysis complete.';
        }
        if (vSavings) {
          vSavings.textContent = (verd.projected_savings && verd.projected_savings > 0)
            ? `Save ${formatMoney(verd.projected_savings)}`
            : 'Best Rate';
        }
        if (vHorizon) {
          vHorizon.textContent = verd.horizon || 'Immediate';
        }

        // Populate 1. Deceptive Pricing & Authenticity Audit Card
        const dec = prod.deceptive_pricing || {};
        const decBadge = document.getElementById('intelDeceptiveBadge');
        const decSummary = document.getElementById('intelDeceptiveSummary');
        const decBase = document.getElementById('intelBaselinePrice');
        const decClaimed = document.getElementById('intelClaimedMrp');
        const decInfl = document.getElementById('intelInflationPct');
        if (decBadge) {
          if (dec.is_deceptive) {
            decBadge.textContent = 'Fake Sale Alert';
            decBadge.className = 'intel-status-pill pill-rose';
          } else if (dec.status === 'VERIFIED_MSRP') {
            decBadge.textContent = 'Verified Street Price';
            decBadge.className = 'intel-status-pill pill-blue';
          } else if (dec.status === 'ALL_TIME_LOW') {
            decBadge.textContent = 'All-Time Low';
            decBadge.className = 'intel-status-pill pill-emerald';
          } else {
            decBadge.textContent = 'Authentic Deal';
            decBadge.className = 'intel-status-pill pill-emerald';
          }
        }
        if (decSummary) decSummary.textContent = dec.summary || 'Baseline verification complete.';
        if (decBase) decBase.textContent = formatMoney(dec.baseline_price || prod.current_price);
        if (decClaimed) decClaimed.textContent = formatMoney(dec.claimed_mrp || prod.original_price || prod.current_price);
        if (decInfl) {
          if (dec.is_deceptive) {
            decInfl.textContent = `+${dec.inflation_pct || 0}% (Hike)`;
            decInfl.className = 'metric-val text-rose';
          } else {
            decInfl.textContent = '0% (Fair Baseline)';
            decInfl.className = 'metric-val text-emerald';
          }
        }

        // Populate 2. Net Effective Price (Interactive Amazon Coupon + Specific Bank Cards)
        // Populate 2. Net Effective Price (Bank Card Savings)
        const net = prod.net_pricing || {};
        const bankOffers = net.bank_offers || [];
        const currentModalCardId = appliedBankCards[prod.id] || '';

        const netBase = document.getElementById('intelNetBasePrice');
        const netBank = document.getElementById('intelNetBank');
        const netEffective = document.getElementById('intelNetEffective');
        const netPill = document.getElementById('intelNetSavingsPill');
        const modalBankCardSelect = document.getElementById('modalBankCardSelect');

        function updateModalNetPrices(cardId) {
          const activeCard = bankOffers.find(b => b.id === cardId) || null;
          const effectiveBankDiscount = activeCard ? activeCard.discount_val : 0;
          const effectiveBankDiscountNative = activeCard ? activeCard.discount_val_native : null;
          const totalSavings = effectiveBankDiscount;
          const trueNet = Math.max(1, (net.base_price || prod.current_price) - totalSavings);

          if (netBase) netBase.textContent = formatMoney(net.base_price || prod.current_price);
          if (netBank) {
            netBank.textContent = activeCard 
              ? `-${formatMoney(effectiveBankDiscount, effectiveBankDiscountNative, prod.currency)} (${activeCard.bank_name})` 
              : `${formatMoney(0)} (No Card Selected)`;
            netBank.className = activeCard ? 'text-purple' : 'text-subtle';
          }
          if (netEffective) netEffective.textContent = formatMoney(trueNet);
          if (netPill) {
            netPill.textContent = totalSavings > 0 ? `Save Extra ${formatMoney(totalSavings)}` : 'Sticker Price';
            netPill.className = `intel-status-pill ${totalSavings > 0 ? 'pill-emerald' : 'pill-slate'}`;
          }
        }

        const modalBankOffersLink = document.getElementById('modalBankOffersLink');
        if (modalBankOffersLink) {
          modalBankOffersLink.textContent = `${bankOffers.length} Offers >`;
          modalBankOffersLink.onclick = (e) => {
            e.preventDefault();
            e.stopPropagation();
            openBankOffersModal(prod.id);
          };
        }

        if (modalBankCardSelect) {
          modalBankCardSelect.innerHTML = `
            <option value="">No Card Applied (Full Price)</option>
            ${bankOffers.map(b => `
              <option value="${b.id}" ${currentModalCardId === b.id ? 'selected' : ''}>
                ${escapeHtml(b.offer_title || 'Offer')}: ${escapeHtml(b.bank_name)} - Save ${formatMoney(b.discount_val, b.discount_val_native, prod.currency)}
              </option>
            `).join('')}
          `;
          modalBankCardSelect.onchange = () => {
            const chosenId = modalBankCardSelect.value;
            if (chosenId) {
              applyBankCardOffer(prod.id, chosenId);
            } else {
              clearBankCardOffer(prod.id);
            }
            updateModalNetPrices(chosenId);
          };
        }

        updateModalNetPrices(currentModalCardId);

        // Populate 3. AI Review Authenticity & Sentiment Analysis
        const rev = prod.review_intelligence || {};
        const trustGrade = document.getElementById('intelTrustGrade');
        const authScore = document.getElementById('intelAuthenticityScore');
        const posPct = document.getElementById('intelPosPct');
        const neuPct = document.getElementById('intelNeuPct');
        const critPct = document.getElementById('intelCritPct');
        const barPos = document.getElementById('intelBarPos');
        const barNeu = document.getElementById('intelBarNeu');
        const barCrit = document.getElementById('intelBarCrit');
        const quote = document.getElementById('intelConsensusQuote');
        const prosList = document.getElementById('intelProsList');
        const consList = document.getElementById('intelConsList');

        if (trustGrade) {
          const tGrade = rev.trust_grade || 'A';
          trustGrade.textContent = `Grade ${tGrade}`;
          trustGrade.className = `trust-grade-badge grade-${tGrade}`;
        }
        if (authScore) authScore.textContent = `${rev.authenticity_score || 92}% Verified`;
        const sent = rev.sentiment_breakdown || { positive: 75, neutral: 15, critical: 10 };
        if (posPct) posPct.textContent = `${sent.positive}%`;
        if (neuPct) neuPct.textContent = `${sent.neutral}%`;
        if (critPct) critPct.textContent = `${sent.critical}%`;
        if (barPos) barPos.style.width = `${sent.positive}%`;
        if (barNeu) barNeu.style.width = `${sent.neutral}%`;
        if (barCrit) barCrit.style.width = `${sent.critical}%`;
        if (quote) quote.textContent = `"${rev.consensus_summary || 'Positive consensus overall across verified owners.'}"`;
        
        const trustFactorsRow = document.getElementById('intelTrustFactorsRow');
        if (trustFactorsRow) {
          const pil = rev.pillars || {};
          const isFake = Boolean(dec.is_deceptive);
          trustFactorsRow.innerHTML = `
            <span class="trust-factor-pill ${pil.rating_score >= 25 ? 'pill-verified' : ''}" title="Authentic customer rating contribution">
              <i class="fa-solid fa-star text-amber"></i> Rating: ${pil.rating_score || 25}/35 pts
            </span>
            <span class="trust-factor-pill ${pil.volume_score >= 18 ? 'pill-verified' : ''}" title="Verified review volume & sample size reliability">
              <i class="fa-solid fa-users text-sky"></i> Volume: ${pil.volume_score || 20}/25 pts
            </span>
            <span class="trust-factor-pill ${pil.brand_score >= 16 ? 'pill-verified' : ''}" title="Manufacturer track record, warranty & compliance">
              <i class="fa-solid fa-award text-purple"></i> Brand Tier: ${pil.brand_score || 15}/20 pts
            </span>
            <span class="trust-factor-pill ${isFake ? 'pill-warning' : 'pill-verified'}" title="Commercial pricing transparency & baseline integrity">
              <i class="fa-solid ${isFake ? 'fa-triangle-exclamation' : 'fa-shield-check'}"></i> 
              Pricing: ${pil.pricing_score >= 0 ? '+' : ''}${pil.pricing_score || 18} pts
            </span>
          `;
        }

        const botBadge = document.getElementById('intelBotRiskBadge');
        const aspectsGrid = document.getElementById('intelAspectsGrid');
        const botRisk = rev.bot_risk || { tier: 'LOW', risk_pct: 6, description: 'Low bot risk' };
        if (botBadge) {
          botBadge.innerHTML = `<i class="fa-solid ${botRisk.tier === 'ELEVATED' ? 'fa-triangle-exclamation' : 'fa-shield-virus'}"></i> ${botRisk.tier === 'ELEVATED' ? 'Elevated Bot Risk' : 'Low Bot Risk'} (${botRisk.risk_pct}%)`;
          botBadge.className = `bot-risk-badge ${botRisk.tier === 'ELEVATED' ? 'risk-elevated' : (botRisk.tier === 'MODERATE' ? 'risk-moderate' : '')}`;
          botBadge.title = botRisk.description;
        }
        if (aspectsGrid && rev.aspect_sentiment) {
          aspectsGrid.innerHTML = rev.aspect_sentiment.map(asp => `
            <div class="aspect-card">
              <div class="aspect-name-row">
                <span><i class="fa-solid ${asp.icon || 'fa-check'}"></i> ${escapeHtml(asp.aspect)}</span>
                <strong class="aspect-pct-val">${asp.positive_pct}%</strong>
              </div>
              <div class="aspect-bar-track">
                <div class="aspect-bar-fill" style="width: ${asp.positive_pct}%;"></div>
              </div>
            </div>
          `).join('');
        }

        if (prosList && rev.key_pros) {
          prosList.innerHTML = rev.key_pros.map(p => `<li>${p}</li>`).join('');
        }
        if (consList && rev.key_cons) {
          consList.innerHTML = rev.key_cons.map(c => `<li>${c}</li>`).join('');
        }

        updateModalForecastBanner(currentModalForecast);

        const downloadCsvBtn = document.getElementById('modalDownloadCsvBtn');
        const downloadJsonBtn = document.getElementById('modalDownloadJsonBtn');
        if (downloadCsvBtn) {
          downloadCsvBtn.href = `/api/products/${id}/export/csv`;
          downloadCsvBtn.setAttribute('download', `PriceHistory_${prod.asin || id}.csv`);
        }
        if (downloadJsonBtn) {
          downloadJsonBtn.href = `/api/products/${id}/export/json`;
        }

        renderChart(currentModalHistory, currentModalTargetUSD, currentModalForecast);
      }

      if (dealRes && dealRes.ok) {
        const dealData = await dealRes.json();
        if (dealData.status === 'success' && dealData.analysis && badge) {
          const a = dealData.analysis;
          badge.innerHTML = `${a.deal_label} (${a.deal_score}%) &bull; ${a.recommendation_label} &bull; ${a.trend_label}`;
        }
      }
    } catch (err) {
      showToast('Error fetching price history data', 'error');
    }
  }

  function renderChart(history, targetPriceUSD, forecast = null) {
    const ctx = document.getElementById('priceChart').getContext('2d');
    const curr = CURRENCIES[currentCurrency] || CURRENCIES.USD;

    const labels = history.map(h => h.date);
    const prices = history.map(h => h.price * curr.rate);
    const targetPriceConverted = targetPriceUSD * curr.rate;

    // Detect All-Time Low historical milestone
    let minPriceIdx = -1;
    let minPriceVal = Infinity;
    prices.forEach((p, idx) => {
      if (p != null && p < minPriceVal) {
        minPriceVal = p;
        minPriceIdx = idx;
      }
    });

    const pointColors = prices.map((p, idx) => idx === minPriceIdx ? '#10b981' : '#ff7700');
    const pointRadii = prices.map((p, idx) => idx === minPriceIdx ? 7 : 4);
    const pointBorders = prices.map((p, idx) => idx === minPriceIdx ? '#ffffff' : '#0a0a0c');

    const gradient = ctx.createLinearGradient(0, 0, 0, 300);
    gradient.addColorStop(0, 'rgba(255, 119, 0, 0.35)');
    gradient.addColorStop(1, 'rgba(255, 119, 0, 0.0)');

    const datasets = [
      {
        label: `Tracked Price (${curr.symbol})`,
        data: [...prices],
        borderColor: '#ff7700',
        backgroundColor: gradient,
        borderWidth: 2.5,
        fill: true,
        tension: 0.35,
        pointRadius: pointRadii,
        pointHoverRadius: 8,
        pointBackgroundColor: pointColors,
        pointBorderColor: pointBorders,
        pointBorderWidth: 2
      },
      {
        label: `Target Alert Threshold (${curr.symbol})`,
        data: new Array(labels.length).fill(targetPriceConverted),
        borderColor: '#00d68f',
        borderWidth: 2,
        borderDash: [6, 6],
        pointRadius: 0,
        fill: false
      }
    ];

    let chartLabels = [...labels];

    // If forecast exists and viewing full history, append statistical 7-day projection line
    if (forecast && forecast.forecast_points && forecast.forecast_points.length > 0 && currentActiveTimeframe === 'ALL' && prices.length > 0) {
      chartLabels = [...labels, ...forecast.forecast_labels];
      datasets[0].data = [...prices, ...new Array(forecast.forecast_points.length).fill(null)];
      datasets[1].data = new Array(chartLabels.length).fill(targetPriceConverted);

      const lastPrice = prices[prices.length - 1];
      const projConverted = forecast.forecast_points.map(p => p * curr.rate);
      const projPadded = [...new Array(prices.length - 1).fill(null), lastPrice, ...projConverted];

      datasets.push({
        label: `7-Day Statistical Projection (${curr.symbol})`,
        data: projPadded,
        borderColor: '#38bdf8',
        borderWidth: 2.2,
        borderDash: [5, 4],
        pointRadius: 3.5,
        pointBackgroundColor: '#38bdf8',
        pointHoverRadius: 6,
        fill: false,
        tension: 0.25
      });
    }

    if (priceChartInstance) {
      priceChartInstance.destroy();
    }

    priceChartInstance = new Chart(ctx, {
      type: 'line',
      data: {
        labels: chartLabels,
        datasets: datasets
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { labels: { color: '#94a3b8', font: { family: 'Inter', size: 12, weight: '600' } } },
          tooltip: {
            backgroundColor: '#0f131d',
            borderColor: 'rgba(56, 189, 248, 0.35)',
            borderWidth: 1,
            titleColor: '#f8fafc',
            bodyColor: '#94a3b8',
            titleFont: { family: 'Outfit', size: 14, weight: 'bold' },
            bodyFont: { family: 'JetBrains Mono', size: 13 },
            padding: 12,
            callbacks: {
              label: (context) => {
                const locale = currentCurrency === 'INR' ? 'en-IN' : undefined;
                let lbl = `${context.dataset.label}: ${curr.symbol}${context.parsed.y != null ? context.parsed.y.toLocaleString(locale, { minimumFractionDigits: currentCurrency === 'JPY' ? 0 : 2 }) : ''}`;
                if (context.datasetIndex === 0 && context.dataIndex === minPriceIdx) {
                  lbl += ' 🏆 [All-Time Low Record]';
                }
                return lbl;
              }
            }
          }
        },
        scales: {
          x: { grid: { color: 'rgba(255, 255, 255, 0.05)' }, ticks: { color: '#94a3b8', font: { family: 'JetBrains Mono', size: 11 } } },
          y: { 
            grid: { color: 'rgba(255, 255, 255, 0.05)' }, 
            ticks: { 
              color: '#94a3b8', 
              font: { family: 'JetBrains Mono', size: 11 }, 
              callback: v => {
                const locale = currentCurrency === 'INR' ? 'en-IN' : undefined;
                return curr.symbol + v.toLocaleString(locale, { minimumFractionDigits: currentCurrency === 'JPY' ? 0 : 2 });
              }
            } 
          }
        }
      }
    });
  }

  closeChartModal.addEventListener('click', () => chartModal.classList.add('hidden'));

  // Timeframe filter buttons click handlers
  document.querySelectorAll('.timeframe-btn').forEach(btn => {
    btn.addEventListener('click', (e) => {
      document.querySelectorAll('.timeframe-btn').forEach(b => {
        b.classList.remove('active');
        b.style.background = '';
        b.style.color = '';
      });
      e.currentTarget.classList.add('active');
      currentActiveTimeframe = e.currentTarget.dataset.range;
      const filtered = filterHistoryByTimeframe(currentModalHistory, currentActiveTimeframe);
      renderChart(filtered, currentModalTargetUSD, currentModalForecast);
    });
  });

  // -----------------------------------------------------------------
  // Multi-Store Competitor Price Comparison Modal
  // -----------------------------------------------------------------
  async function openCompetitorModal(id) {
    if (!competitorModal) return;

    competitorModal.classList.remove('hidden');
    if (typeof gsap !== 'undefined') {
      gsap.fromTo('#competitorModal .modal-content', { scale: 0.75, opacity: 0, y: 25 }, { scale: 1, opacity: 1, y: 0, duration: 0.4, ease: 'back.out(1.4)' });
    }

    compModalProductTitle.textContent = 'Loading Live Competitor Index...';
    compVerdictText.textContent = 'Scanning Flipkart, Myntra, Blinkit, Zepto, Nykaa, Croma, Walmart...';
    compVerdictSub.textContent = 'Synchronizing cross-store pricing, fashion catalogs & 10-min delivery slots...';
    compMaxSavings.textContent = '...';
    competitorStoresGrid.innerHTML = `
      <div class="competitor-loading-state">
        <i class="fa-solid fa-circle-notch fa-spin text-amber" style="font-size: 32px;"></i>
        <p>Indexing 18 verified Indian & Global retailer marketplaces...</p>
      </div>
    `;
    competitorSpreadBars.innerHTML = '';

    try {
      const res = await fetch(`/api/products/${id}/competitors`);
      const data = await res.json();
      if (data.status === 'success') {
        currentComparisonData = data.comparison;
        activeMarketTab = currentComparisonData.default_market || 'indian';
        activeChannelFilter = 'all';
        // If the product belongs to fashion or quick commerce, auto-filter to that sector
        if (currentComparisonData.detected_channel && currentComparisonData.detected_channel !== 'mega') {
          activeChannelFilter = currentComparisonData.detected_channel;
        }
        renderCompetitorComparison();
      } else {
        showToast(data.message || 'Error fetching competitor data', 'error');
      }
    } catch (err) {
      showToast('Network error loading competitor prices', 'error');
    }
  }

  function renderCompetitorComparison() {
    if (!currentComparisonData) return;
    const comp = currentComparisonData;

    compModalProductTitle.textContent = comp.title;
    if (compCurrentCurrencyCode) compCurrentCurrencyCode.textContent = currentCurrency;

    // Update Arbitrage Verdict Banner
    const isAmazonLowest = comp.summary.is_amazon_winner;
    const banner = compArbitrageBanner;
    if (banner) {
      if (isAmazonLowest) {
        banner.className = 'arbitrage-verdict-banner amazon-leading';
        const icon = banner.querySelector('.verdict-icon i');
        if (icon) icon.className = 'fa-solid fa-trophy text-emerald';
      } else {
        banner.className = 'arbitrage-verdict-banner competitor-leading';
        const icon = banner.querySelector('.verdict-icon i');
        if (icon) icon.className = 'fa-solid fa-bolt-lightning text-amber';
      }
    }

    compVerdictText.textContent = comp.summary.verdict;
    if (comp.amazon_delivery_info) {
      compVerdictSub.innerHTML = `<i class="fa-brands fa-amazon" style="color: #f59e0b;"></i> Amazon: <strong>${comp.amazon_delivery_info}</strong> &bull; Benchmarked across ${comp.summary.total_stores_compared} store networks`;
    } else {
      compVerdictSub.textContent = `Benchmarked against ${comp.summary.total_stores_compared} verified Indian & Global retailer marketplaces`;
    }
    compMaxSavings.textContent = formatMoney(comp.summary.max_savings);
    compPriceSpreadVal.textContent = `Market Spread: ${formatMoney(comp.summary.price_spread)}`;

    // Set Active Market Tab styling
    if (compTabIndian && compTabGlobal) {
      if (activeMarketTab === 'indian') {
        compTabIndian.classList.add('active');
        compTabGlobal.classList.remove('active');
        if (compChannelPillsRow) compChannelPillsRow.style.display = 'flex';
      } else {
        compTabGlobal.classList.add('active');
        compTabIndian.classList.remove('active');
        if (compChannelPillsRow) compChannelPillsRow.style.display = 'none';
      }
    }

    // Update Channel Pills active state
    if (compChannelPillsRow) {
      compChannelPillsRow.querySelectorAll('.channel-pill').forEach(pill => {
        if (pill.dataset.channel === activeChannelFilter) {
          pill.classList.add('active');
        } else {
          pill.classList.remove('active');
        }
      });
    }

    // Update Tab Counts
    const onlyAvailable = compAvailabilityOnlyToggle ? compAvailabilityOnlyToggle.checked : true;
    if (compTabIndianBadge && comp.summary) {
      compTabIndianBadge.textContent = onlyAvailable
        ? `${comp.summary.indian_available_count || 0} Stores`
        : `${comp.summary.indian_stores_count || 13} Stores`;
    }
    if (compTabGlobalBadge && comp.summary) {
      compTabGlobalBadge.textContent = onlyAvailable
        ? `${comp.summary.global_available_count || 0} Stores`
        : `${comp.summary.global_stores_count || 5} Stores`;
    }

    // Filter stores based on active market and channel
    let marketStores = activeMarketTab === 'indian' ? comp.indian_stores : comp.global_stores;
    if (activeMarketTab === 'indian' && activeChannelFilter !== 'all') {
      marketStores = marketStores.filter(s => s.channel === activeChannelFilter);
    }

    // Filter by catalog availability (e.g. Nykaa doesn't carry OnePlus buds)
    const uncarriedStores = marketStores.filter(s => s.is_available === false);
    let stores = marketStores;
    if (onlyAvailable) {
      stores = marketStores.filter(s => s.is_available !== false);
    }

    // Update Availability Notice Banner
    if (compAvailabilityNotice && compAvailabilityNoticeText) {
      if (uncarriedStores.length > 0) {
        compAvailabilityNotice.classList.remove('hidden');
        if (onlyAvailable) {
          const names = uncarriedStores.map(s => s.name).join(', ');
          compAvailabilityNoticeText.innerHTML = `<strong>Catalog Filter Active:</strong> ${uncarriedStores.length} dealer(s) (${names}) hidden because they do not carry <em>${comp.product_vertical || 'this category'}</em>.`;
        } else {
          compAvailabilityNoticeText.innerHTML = `<strong>Showing all dealers:</strong> ${uncarriedStores.length} dealer(s) highlighted as not stocking <em>${comp.product_vertical || 'this category'}</em>.`;
        }
      } else {
        compAvailabilityNotice.classList.add('hidden');
      }
    }

    const amazonPrice = comp.amazon_price;

    const channelLabels = {
      fashion: '👗 Fashion & Beauty',
      quick_commerce: '⚡ 10-Min Quick Commerce',
      mega: '📱 Mega & Electronics',
      global: '🌐 Global Retail'
    };

    if (stores.length === 0) {
      competitorStoresGrid.innerHTML = `
        <div class="competitor-empty-state">
          <i class="fa-solid fa-store-slash"></i>
          <h4>No Dealers Available in This Category</h4>
          <p>None of the selected dealers carry ${comp.product_vertical || 'this product'}. Uncheck <em>'In-Stock & Carried Only'</em> or switch to 'All Stores' to view benchmark catalog listings.</p>
        </div>
      `;
    } else {
      competitorStoresGrid.innerHTML = `
        <!-- Amazon Reference Card -->
        <div class="competitor-store-card amazon-benchmark-card">
          <div class="store-card-header">
            <div class="store-brand-info">
              <span class="store-icon amazon-brand-icon">
                <img src="/static/images/retailers/amazon.svg" alt="Amazon" class="retailer-logo-img" onerror="this.style.display='none'; this.nextElementSibling.style.display='inline-block';">
                <i class="fa-brands fa-amazon" style="display:none; color: #ff9900;"></i>
              </span>
              <div>
                <h4 class="store-name">Amazon (${comp.region})</h4>
                <span class="store-tag amazon-ref-tag">Tracking Baseline</span>
              </div>
            </div>
            <span class="store-price-tag">${formatMoney(amazonPrice)}</span>
          </div>
          <div class="store-card-body">
            <div class="store-perk"><i class="fa-solid fa-shield-check text-emerald"></i> Live DOM Scraped</div>
            <div class="store-perk"><i class="fa-solid fa-bolt text-amber"></i> Autonomous Daemon Sync</div>
          </div>
          <div class="store-card-footer">
            <span class="price-diff-pill baseline-pill"><i class="fa-solid fa-anchor"></i> Base Benchmark</span>
            <span class="store-stock text-emerald"><i class="fa-solid fa-circle-check"></i> Monitored</span>
          </div>
        </div>
        ${stores.map(store => {
          const logoMarkup = store.logo_url
            ? `<img src="${store.logo_url}" alt="${store.name}" class="retailer-logo-img" onerror="this.style.display='none'; this.nextElementSibling.style.display='inline-block';"><i class="${store.icon}" style="display:none; color: ${store.brand_color};"></i>`
            : `<i class="${store.icon}" style="color: ${store.brand_color};"></i>`;

          if (!store.is_available) {
            return `
              <div class="competitor-store-card store-card-not-carried" style="--store-brand: ${store.brand_color}">
                <div class="store-card-header">
                  <div class="store-brand-info">
                    <span class="store-icon" style="background: ${store.badge_bg}; border: 1px solid ${store.badge_border};">
                      ${logoMarkup}
                    </span>
                    <div>
                      <h4 class="store-name">${store.name}</h4>
                      <span class="store-tag" style="color: var(--text-muted)">${channelLabels[store.channel] || 'Retail Marketplace'}</span>
                    </div>
                  </div>
                  <span class="badge-not-carried"><i class="fa-solid fa-ban"></i> Not Sold Here</span>
                </div>
                <div class="store-card-body">
                  <div class="store-perk text-subtle"><i class="fa-solid fa-circle-exclamation text-amber"></i> Does not carry ${comp.product_vertical || 'this'} catalog</div>
                  <div class="store-perk text-subtle"><i class="fa-solid fa-circle-info"></i> Not indexed by ${store.name}</div>
                </div>
                <div class="store-card-footer">
                  <span class="price-diff-pill uncarried-pill"><i class="fa-solid fa-eye-slash"></i> Catalog Excluded</span>
                  <span class="btn btn-sm btn-store-search disabled" style="opacity: 0.5; pointer-events: none;">Unavailable</span>
                </div>
              </div>
            `;
          }

          const convertedPrice = formatMoney(store.price);
          const diffVal = store.diff;
          const diffConverted = formatMoney(Math.abs(diffVal));
          let diffPill = '';
          if (diffVal > 0) {
            diffPill = `<span class="price-diff-pill amazon-cheaper-pill"><i class="fa-solid fa-arrow-down"></i> Amazon is ${diffConverted} cheaper</span>`;
          } else if (diffVal < 0) {
            diffPill = `<span class="price-diff-pill store-cheaper-pill"><i class="fa-solid fa-tag"></i> ${store.name} is ${diffConverted} cheaper</span>`;
          } else {
            diffPill = `<span class="price-diff-pill matched-pill"><i class="fa-solid fa-equals"></i> Price Matched</span>`;
          }

          return `
            <div class="competitor-store-card" style="--store-brand: ${store.brand_color}">
              <div class="store-card-header">
                <div class="store-brand-info">
                  <span class="store-icon" style="background: ${store.badge_bg}; border: 1px solid ${store.badge_border};">
                    ${logoMarkup}
                  </span>
                  <div>
                    <h4 class="store-name">${store.name}</h4>
                    <span class="store-tag" style="color: ${store.brand_color}">${channelLabels[store.channel] || 'Retail Marketplace'}</span>
                  </div>
                </div>
                <span class="store-price-tag">${convertedPrice}</span>
              </div>
              <div class="store-card-body">
                <div class="store-perk"><i class="fa-solid fa-truck-fast" style="color: var(--accent-biscuit)"></i> ${store.delivery_info}</div>
                <div class="store-perk"><i class="fa-solid fa-check text-emerald"></i> ${store.availability}</div>
              </div>
              <div class="store-card-footer">
                ${diffPill}
                <a href="${store.search_url}" target="_blank" rel="noopener noreferrer" class="btn btn-sm btn-store-search" title="View live search on ${store.name}">
                  <i class="fa-solid fa-arrow-up-right-from-square"></i> Visit Store
                </a>
              </div>
            </div>
          `;
        }).join('')}
      `;
    }

    // Render Spread Relative Bars (strictly among available stores)
    const availableStoresForSpread = stores.filter(s => s.is_available !== false);
    const allToCompare = [
      { name: `Amazon (${comp.region})`, price: amazonPrice, isAmazon: true, brandColor: '#f59e0b', logoUrl: '/static/images/retailers/amazon.svg' },
      ...availableStoresForSpread.map(s => ({ name: s.name, price: s.price, isAmazon: false, brandColor: s.brand_color, logoUrl: s.logo_url }))
    ];

    const maxPrice = Math.max(...allToCompare.map(x => x.price));
    const minPrice = Math.min(...allToCompare.map(x => x.price));

    competitorSpreadBars.innerHTML = allToCompare.map(item => {
      const pct = Math.min(100, Math.max(25, Math.round((item.price / maxPrice) * 100)));
      const isLowest = item.price === minPrice;
      return `
        <div class="spread-bar-row ${item.isAmazon ? 'amazon-bar-row' : ''}">
          <div class="spread-bar-label">
            <span class="bar-store-name">
              ${item.logoUrl ? `<img src="${item.logoUrl}" alt="${item.name}" class="bar-store-logo">` : ''}
              ${item.isAmazon ? '👑 ' : ''}${item.name}
            </span>
            <span class="bar-store-price">${formatMoney(item.price)}</span>
          </div>
          <div class="spread-bar-track">
            <div class="spread-bar-fill" style="width: ${pct}%; background: ${item.isAmazon ? 'linear-gradient(90deg, #10b981, #34d399)' : item.brandColor}"></div>
          </div>
          ${isLowest ? `<span class="lowest-market-tag"><i class="fa-solid fa-trophy"></i> Best Price</span>` : ''}
        </div>
      `;
    }).join('');
  }

  // Setup Availability Toggle Listener
  if (compAvailabilityOnlyToggle) {
    compAvailabilityOnlyToggle.addEventListener('change', () => {
      renderCompetitorComparison();
    });
  }

  // Setup Channel Pills Listeners
  if (compChannelPillsRow) {
    compChannelPillsRow.querySelectorAll('.channel-pill').forEach(pill => {
      pill.addEventListener('click', () => {
        compChannelPillsRow.querySelectorAll('.channel-pill').forEach(p => p.classList.remove('active'));
        pill.classList.add('active');
        activeChannelFilter = pill.dataset.channel;
        renderCompetitorComparison();
      });
    });
  }

  if (compTabIndian && compTabGlobal) {
    compTabIndian.addEventListener('click', () => {
      activeMarketTab = 'indian';
      renderCompetitorComparison();
    });
    compTabGlobal.addEventListener('click', () => {
      activeMarketTab = 'global';
      renderCompetitorComparison();
    });
  }

  if (closeCompetitorModal) {
    closeCompetitorModal.addEventListener('click', () => {
      if (competitorModal) competitorModal.classList.add('hidden');
    });
  }

  if (competitorModal) {
    competitorModal.addEventListener('click', (e) => {
      if (e.target === competitorModal) competitorModal.classList.add('hidden');
    });
  }

  const modalCompareStoresBtn = document.getElementById('modalCompareStoresBtn');
  if (modalCompareStoresBtn) {
    modalCompareStoresBtn.addEventListener('click', (e) => {
      e.preventDefault();
      e.stopPropagation();
      if (currentModalProductId) {
        if (chartModal) chartModal.classList.add('hidden');
        openCompetitorModal(currentModalProductId);
      }
    });
  }

  // -----------------------------------------------------------------
  // Email Alert Test Modal & GSAP Pop
  // -----------------------------------------------------------------
  function openAlertModal(id) {
    if (!currentUser) {
      pendingAlertProductId = id;
      openAlertAuthModal();
      return;
    }

    alertProductId.value = id;
    if (currentUser && currentUser.email) {
      alertEmailInput.value = currentUser.email;
    }
    emailPreviewContainer.classList.add('hidden');
    alertModal.classList.remove('hidden');
    if (typeof gsap !== 'undefined') {
      gsap.fromTo('#alertModal .modal-content', { scale: 0.75, opacity: 0, y: 20 }, { scale: 1, opacity: 1, y: 0, duration: 0.4, ease: 'back.out(1.4)' });
    }
  }

  function openAlertAuthModal() {
    if (!alertAuthModal) return;
    alertAuthModal.classList.remove('hidden');
    if (typeof gsap !== 'undefined') {
      gsap.fromTo('#alertAuthModal .modal-content', { scale: 0.8, opacity: 0, y: 25 }, { scale: 1, opacity: 1, y: 0, duration: 0.35, ease: 'back.out(1.4)' });
    }
  }

  function closeAlertAuthModalFn() {
    if (alertAuthModal) {
      alertAuthModal.classList.add('hidden');
    }
  }

  if (closeAlertAuthModal) {
    closeAlertAuthModal.addEventListener('click', closeAlertAuthModalFn);
  }

  // Quick Auth Tabs
  if (modalTabLogin && modalTabRegister) {
    modalTabLogin.addEventListener('click', () => {
      modalTabLogin.classList.add('active');
      modalTabRegister.classList.remove('active');
      quickLoginForm.classList.remove('hidden');
      quickRegisterForm.classList.add('hidden');
    });

    modalTabRegister.addEventListener('click', () => {
      modalTabRegister.classList.add('active');
      modalTabLogin.classList.remove('active');
      quickRegisterForm.classList.remove('hidden');
      quickLoginForm.classList.add('hidden');
    });
  }

  // Quick Login Submit Handler
  if (quickLoginForm) {
    quickLoginForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const email = quickLoginEmail.value.trim();
      const password = quickLoginPassword.value.trim();

      try {
        const res = await fetch('/api/auth/login', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ email, password })
        });
        const data = await res.json();
        if (data.status === 'success') {
          currentUser = data.user;
          renderUserAuth(currentUser);
          closeAlertAuthModalFn();
          quickLoginForm.reset();
          renderProducts(allProducts);
          updateAutoAlertUI(currentUser);

          if (data.auto_alerts_triggered > 0) {
            showToast(`🔥 Auto-Alert: ${data.auto_alerts_triggered} price drop alert email(s) automatically sent to ${currentUser.email}!`, 'success');
          } else {
            showToast(`⚡ Signed in! Automated price alerts are active for ${currentUser.email}`, 'success');
          }

          // Open the pending alert modal immediately if one was clicked
          const targetId = pendingAlertProductId;
          pendingAlertProductId = null;
          if (targetId) {
            openAlertModal(targetId);
          }
        } else {
          showToast(data.message || 'Login failed', 'error');
        }
      } catch (err) {
        showToast('Login request failed', 'error');
      }
    });
  }

  // Quick Register Submit Handler
  if (quickRegisterForm) {
    quickRegisterForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const name = quickRegName.value.trim();
      const email = quickRegEmail.value.trim();
      const password = quickRegPassword.value.trim();

      try {
        const res = await fetch('/api/auth/register', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ name, email, password })
        });
        const data = await res.json();
        if (data.status === 'success') {
          currentUser = data.user;
          renderUserAuth(currentUser);
          closeAlertAuthModalFn();
          quickRegisterForm.reset();
          renderProducts(allProducts);
          updateAutoAlertUI(currentUser);

          if (data.auto_alerts_triggered > 0) {
            showToast(`🎉 Welcome! ${data.auto_alerts_triggered} price drop email alert(s) automatically sent to your inbox!`, 'success');
          } else {
            showToast(`⚡ Account created! Automated price drop alerts armed for ${currentUser.email}.`, 'success');
          }

          // Open the pending alert modal immediately if one was clicked
          const targetId = pendingAlertProductId;
          pendingAlertProductId = null;
          if (targetId) {
            openAlertModal(targetId);
          }
        } else {
          showToast(data.message || 'Registration failed', 'error');
        }
      } catch (err) {
        showToast('Registration request failed', 'error');
      }
    });
  }

  sendTestAlertForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const email = alertEmailInput.value;
    const pid = alertProductId.value;

    try {
      const res = await fetch('/api/alerts/test', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: email, product_id: pid })
      });
      const data = await res.json();
      if (res.status === 401) {
        alertModal.classList.add('hidden');
        currentUser = null;
        renderUserAuth(null);
        renderProducts(allProducts);
        openAlertAuthModal();
        showToast(data.message || 'Please log in to use alerts', 'error');
        return;
      }
      if (data.status === 'success') {
        previewSubject.textContent = data.preview.subject;
        const doc = emailPreviewFrame.contentWindow.document;
        doc.open();
        doc.write(data.preview.body);
        doc.close();
        emailPreviewContainer.classList.remove('hidden');
        if (typeof gsap !== 'undefined') {
          gsap.fromTo(emailPreviewContainer, { opacity: 0, y: 15 }, { opacity: 1, y: 0, duration: 0.35, ease: 'power2.out' });
        }
        showToast('Email alert preview generated successfully!', 'success');
      } else {
        showToast(data.message || 'Error generating email preview', 'error');
      }
    } catch (err) {
      showToast('Error generating email preview', 'error');
    }
  });

  closeAlertModal.addEventListener('click', () => alertModal.classList.add('hidden'));

  // -----------------------------------------------------------------
  // Email Authentication & User Session Logic
  // -----------------------------------------------------------------
  // -----------------------------------------------------------------
  // User Session Header Logic
  // -----------------------------------------------------------------
  const userAuthContainer = document.getElementById('userAuthContainer');

  async function checkAuthStatus() {
    try {
      const res = await fetch('/api/auth/me');
      const data = await res.json();
      if (data.status === 'success' && data.logged_in) {
        currentUser = data.user;
        renderUserAuth(currentUser);
        if (alertEmailInput && currentUser.email) {
          alertEmailInput.value = currentUser.email;
        }
        updateAutoAlertUI(currentUser);
        fetchAlertActivity(false);
      } else {
        currentUser = null;
        renderUserAuth(null);
        updateAutoAlertUI(null);
      }
      renderProducts(allProducts);
    } catch (err) {
      console.error('Auth check error:', err);
    }
  }

  function updateAutoAlertUI(user) {
    if (!autoAlertsStatusText || !toggleAutoAlertsBtn) return;
    if (user) {
      const active = user.auto_alerts_enabled !== 0;
      autoAlertsStatusText.textContent = active ? 'Active (Auto)' : 'Paused';
      if (active) {
        toggleAutoAlertsBtn.classList.add('active');
        if (activityBannerText) activityBannerText.textContent = `Auto-Alert Engine: Active for ${user.email}`;
      } else {
        toggleAutoAlertsBtn.classList.remove('active');
        if (activityBannerText) activityBannerText.textContent = 'Auto-Alert Engine: Paused by user';
      }
    } else {
      autoAlertsStatusText.textContent = 'Login Required';
      toggleAutoAlertsBtn.classList.remove('active');
      if (alertCountBadge) alertCountBadge.textContent = '0';
      if (activityBannerText) activityBannerText.textContent = 'Sign in to arm auto-alert engine';
    }
  }

  async function fetchAlertActivity(openModal = false) {
    if (!currentUser) {
      if (openModal) openAlertAuthModal();
      return;
    }

    try {
      const res = await fetch('/api/alerts/activity');
      const data = await res.json();
      if (data.status === 'success') {
        const logs = data.logs || [];
        if (alertCountBadge) alertCountBadge.textContent = logs.length;
        renderAlertLogs(logs);

        if (openModal && alertActivityModal) {
          alertActivityModal.classList.remove('hidden');
          if (typeof gsap !== 'undefined') {
            gsap.fromTo('#alertActivityModal .modal-content', { scale: 0.8, opacity: 0, y: 25 }, { scale: 1, opacity: 1, y: 0, duration: 0.35, ease: 'back.out(1.4)' });
          }
        }
      }
    } catch (err) {
      console.error('Error fetching alert activity:', err);
    }
  }

  function renderAlertLogs(logs) {
    if (!alertLogsContainer) return;
    if (logs.length === 0) {
      alertLogsContainer.innerHTML = `
        <div class="log-empty-state">
          <i class="fa-solid fa-bell-slash"></i>
          <h4>No automated alerts dispatched yet</h4>
          <p>Whenever a tracked product drops to or below your target alert price, an automated email will be sent and logged here.</p>
        </div>
      `;
      return;
    }

    alertLogsContainer.innerHTML = logs.map(l => {
      return `
        <div class="alert-log-item">
          <div class="log-item-main">
            ${l.image_url ? `<img src="${l.image_url}" alt="Product" class="log-item-thumb" loading="lazy" referrerpolicy="no-referrer" onerror="this.onerror=null; this.src='/static/images/product-placeholder.svg';">` : ''}
            <div>
              <div class="log-item-title" title="${l.product_title}">${l.product_title}</div>
              <div class="log-item-meta">
                <span>Alert Price: <strong class="log-item-price">${formatMoney(l.current_price)}</strong></span>
                <span>Target: ${formatMoney(l.target_price)}</span>
                <span><i class="fa-regular fa-clock"></i> ${l.created_at}</span>
              </div>
            </div>
          </div>
          <div class="log-item-right">
            <span class="log-badge-sent"><i class="fa-solid fa-check"></i> Sent to Inbox</span>
          </div>
        </div>
      `;
    }).join('');
  }

  // Toggle Auto-Alerts Preference
  if (toggleAutoAlertsBtn) {
    toggleAutoAlertsBtn.addEventListener('click', async () => {
      if (!currentUser) {
        openAlertAuthModal();
        return;
      }

      try {
        const res = await fetch('/api/alerts/auto-toggle', { method: 'POST' });
        const data = await res.json();
        if (data.status === 'success') {
          currentUser.auto_alerts_enabled = data.auto_alerts_enabled ? 1 : 0;
          updateAutoAlertUI(currentUser);
          showToast(data.message, data.auto_alerts_enabled ? 'success' : 'info');
        }
      } catch (err) {
        showToast('Failed to toggle auto-alerts', 'error');
      }
    });
  }

  // Activity Log Modal Toggle
  if (viewAlertLogsBtn) {
    viewAlertLogsBtn.addEventListener('click', () => fetchAlertActivity(true));
  }
  if (closeAlertActivityModal) {
    closeAlertActivityModal.addEventListener('click', () => alertActivityModal.classList.add('hidden'));
  }

  function renderUserAuth(user) {
    if (!userAuthContainer) return;

    if (user) {
      const initial = (user.name || user.email).charAt(0).toUpperCase();
      const avatarContent = user.avatar_url 
        ? `<img src="${escapeHtml(user.avatar_url)}" alt="${escapeHtml(user.name || 'User')}" class="nav-user-avatar-img" referrerpolicy="no-referrer">` 
        : initial;

      userAuthContainer.innerHTML = `
        <div class="nav-user-badge" title="Logged in as ${escapeHtml(user.email)}">
          <div class="nav-user-avatar">${avatarContent}</div>
          <span class="nav-user-email">${escapeHtml(user.name || user.email)}</span>
          <button id="navLogoutBtn" class="nav-logout-btn" title="Log Out">
            <i class="fa-solid fa-right-from-bracket"></i>
          </button>
        </div>
      `;
      document.getElementById('navLogoutBtn').addEventListener('click', handleLogout);
    } else {
      userAuthContainer.innerHTML = `
        <a href="/" class="btn btn-secondary nav-auth-btn">
          <i class="fa-solid fa-house"></i> Home / Sign In
        </a>
      `;
    }
  }

  // -----------------------------------------------------------------
  // Google Authentication Integration in Modal
  // -----------------------------------------------------------------
  const modalGoogleSignInBtn = document.getElementById('modalGoogleSignInBtn');
  let modalGoogleTokenClient = null;
  let modalGoogleConfig = null;

  async function initDashboardGoogleAuth() {
    try {
      const cfgRes = await fetch('/api/auth/config');
      modalGoogleConfig = await cfgRes.json();
      if (modalGoogleConfig.google_client_id && typeof google !== 'undefined') {
        if (google.accounts?.id) {
          google.accounts.id.initialize({
            client_id: modalGoogleConfig.google_client_id,
            callback: async (response) => {
              if (!response || !response.credential) return;
              showToast('Verifying Google credentials...', 'info');
              try {
                const res = await fetch('/api/auth/google', {
                  method: 'POST',
                  headers: { 'Content-Type': 'application/json' },
                  body: JSON.stringify({ credential: response.credential })
                });
                const data = await res.json();
                if (data.status === 'success') {
                  currentUser = data.user;
                  renderUserAuth(currentUser);
                  if (alertAuthModal) alertAuthModal.classList.add('hidden');
                  showToast(`Signed in as ${currentUser.name || currentUser.email}`, 'success');
                  fetchProducts();
                } else {
                  showToast(data.message || 'Google Sign-In failed', 'error');
                }
              } catch (err) {
                showToast('Error verifying Google account', 'error');
              }
            },
            auto_select: false
          });
        }

        if (google.accounts?.oauth2) {
          modalGoogleTokenClient = google.accounts.oauth2.initTokenClient({
            client_id: modalGoogleConfig.google_client_id,
            scope: 'email profile openid',
            callback: async (tokenResponse) => {
              if (tokenResponse.error) {
                showToast(`Google Sign-In: ${tokenResponse.error}`, 'error');
                return;
              }
              showToast('Fetching Google profile...', 'info');
              try {
                const userinfoRes = await fetch('https://www.googleapis.com/oauth2/v3/userinfo', {
                  headers: { Authorization: `Bearer ${tokenResponse.access_token}` }
                });
                const profile = await userinfoRes.json();
                const res = await fetch('/api/auth/google', {
                  method: 'POST',
                  headers: { 'Content-Type': 'application/json' },
                  body: JSON.stringify({
                    email: profile.email,
                    name: profile.name,
                    avatar_url: profile.picture
                  })
                });
                const data = await res.json();
                if (data.status === 'success') {
                  currentUser = data.user;
                  renderUserAuth(currentUser);
                  if (alertAuthModal) alertAuthModal.classList.add('hidden');
                  showToast(`Signed in as ${currentUser.name || currentUser.email}!`, 'success');
                  fetchProducts();
                }
              } catch (err) {
                showToast('Failed to retrieve Google profile', 'error');
              }
            }
          });
        }
      }
    } catch (e) {
      console.warn('Dashboard Google Auth setup deferred:', e);
    }
  }

  if (modalGoogleSignInBtn) {
    modalGoogleSignInBtn.addEventListener('click', async () => {
      if (modalGoogleTokenClient) {
        try {
          modalGoogleTokenClient.requestAccessToken({ prompt: 'select_account' });
          return;
        } catch (err) {
          console.warn('Modal Google Token Client failed:', err);
        }
      }

      if (modalGoogleConfig?.google_client_id && typeof google !== 'undefined' && google.accounts?.id) {
        try {
          google.accounts.id.prompt();
          showToast('Google Sign-In prompt triggered.', 'info');
          return;
        } catch (err) {}
      }

      showToast('Authenticating with Google Account...', 'info');
      try {
        const res = await fetch('/api/auth/google', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            demo: true,
            email: 'jaisramani05@gmail.com',
            name: 'Jai S Ramani',
            avatar_url: 'https://lh3.googleusercontent.com/a/default-user'
          })
        });
        const data = await res.json();
        if (data.status === 'success') {
          currentUser = data.user;
          renderUserAuth(currentUser);
          if (alertAuthModal) alertAuthModal.classList.add('hidden');
          showToast(`Signed in as ${currentUser.name || currentUser.email}`, 'success');
          fetchProducts();
        } else {
          showToast(data.message || 'Google Auth error', 'error');
        }
      } catch (e) {
        showToast('Google authentication error', 'error');
      }
    });
  }

  async function handleLogout() {
    try {
      const res = await fetch('/api/auth/logout', { method: 'POST' });
      const data = await res.json();
      if (data.status === 'success') {
        currentUser = null;
        renderUserAuth(null);
        showToast('Logged out successfully', 'info');
        fetchProducts();
      }
    } catch (err) {
      showToast('Logout failed', 'error');
    }
  }
  // -----------------------------------------------------------------
  // 3-Dot Header Options Menu Toggle
  // -----------------------------------------------------------------
  const threeDotBtn = document.getElementById('threeDotBtn');
  const headerMenuDropdown = document.getElementById('headerMenuDropdown');

  if (threeDotBtn && headerMenuDropdown) {
    threeDotBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      const isHidden = headerMenuDropdown.classList.contains('hidden');
      if (isHidden) {
        headerMenuDropdown.classList.remove('hidden');
        if (typeof gsap !== 'undefined') {
          gsap.fromTo(headerMenuDropdown, { scale: 0.85, opacity: 0, y: -10 }, { scale: 1, opacity: 1, y: 0, duration: 0.25, ease: 'power2.out' });
        }
      } else {
        headerMenuDropdown.classList.add('hidden');
      }
    });

    document.addEventListener('click', (e) => {
      if (!headerMenuDropdown.contains(e.target) && e.target !== threeDotBtn && !threeDotBtn.contains(e.target)) {
        headerMenuDropdown.classList.add('hidden');
      }
    });
  }

  // Filter & Sort Listeners
  if (searchFilter) searchFilter.addEventListener('input', () => renderProducts(allProducts));
  if (categoryFilter) categoryFilter.addEventListener('change', () => renderProducts(allProducts));
  if (recommendationFilter) recommendationFilter.addEventListener('change', () => renderProducts(allProducts));
  if (sortFilter) sortFilter.addEventListener('change', () => renderProducts(allProducts));

  // Scheduler Controls Listeners
  if (toggleSchedulerBtn) {
    toggleSchedulerBtn.addEventListener('click', async () => {
      try {
        const res = await fetch('/api/scheduler/toggle', { method: 'POST' });
        const data = await res.json();
        if (data.status === 'success') {
          showToast(`Background scheduler is now ${data.scheduler.running ? 'Active 🟢' : 'Paused ⏸️'}`, 'info');
          fetchSchedulerStatus();
        }
      } catch (err) {
        showToast('Failed to toggle background scheduler', 'error');
      }
    });
  }

  if (triggerSchedulerBtn) {
    triggerSchedulerBtn.addEventListener('click', async () => {
      try {
        showToast('Initiating immediate background price sweep...', 'info');
        const res = await fetch('/api/scheduler/trigger', { method: 'POST' });
        const data = await res.json();
        if (data.status === 'success') {
          showToast('Background sweep triggered! Refreshing data shortly...', 'success');
          setTimeout(() => {
            fetchProducts();
            fetchSchedulerStatus();
          }, 2500);
        }
      } catch (err) {
        showToast('Failed to trigger background sweep', 'error');
      }
    });
  }

  // -----------------------------------------------------------------
  // Multi-Channel Alert Settings Modal
  // -----------------------------------------------------------------
  const openNotificationSettingsBtn = document.getElementById('openNotificationSettingsBtn');
  const notificationSettingsModal = document.getElementById('notificationSettingsModal');
  const closeNotificationSettingsModal = document.getElementById('closeNotificationSettingsModal');
  const notificationSettingsForm = document.getElementById('notificationSettingsForm');
  const discordWebhookInput = document.getElementById('discordWebhookInput');
  const telegramChatInput = document.getElementById('telegramChatInput');
  const testDiscordWebhookBtn = document.getElementById('testDiscordWebhookBtn');

  if (openNotificationSettingsBtn && notificationSettingsModal) {
    openNotificationSettingsBtn.addEventListener('click', () => {
      if (headerMenuDropdown) headerMenuDropdown.classList.add('hidden');

      if (!currentUser) {
        showToast('Please log in to customize notification channels', 'info');
        if (alertAuthModal) alertAuthModal.classList.remove('hidden');
        return;
      }

      if (discordWebhookInput) discordWebhookInput.value = currentUser.discord_webhook || '';
      if (telegramChatInput) telegramChatInput.value = currentUser.telegram_chat_id || '';

      notificationSettingsModal.classList.remove('hidden');
      if (typeof gsap !== 'undefined') {
        gsap.fromTo('#notificationSettingsModal .modal-content', { scale: 0.8, opacity: 0, y: 20 }, { scale: 1, opacity: 1, y: 0, duration: 0.35, ease: 'back.out(1.3)' });
      }
    });
  }

  if (closeNotificationSettingsModal && notificationSettingsModal) {
    closeNotificationSettingsModal.addEventListener('click', () => {
      notificationSettingsModal.classList.add('hidden');
    });
  }

  if (notificationSettingsForm) {
    notificationSettingsForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const discord = discordWebhookInput ? discordWebhookInput.value.trim() : '';
      const telegram = telegramChatInput ? telegramChatInput.value.trim() : '';

      try {
        const res = await fetch('/api/notifications/settings', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ discord_webhook: discord, telegram_chat_id: telegram })
        });
        const data = await res.json();
        if (data.status === 'success') {
          showToast('Notification channels saved successfully! 🔔', 'success');
          if (data.user) currentUser = data.user;
          notificationSettingsModal.classList.add('hidden');
        } else {
          showToast(data.message || 'Failed to save settings', 'error');
        }
      } catch (err) {
        showToast('Error saving notification settings', 'error');
      }
    });
  }

  if (testDiscordWebhookBtn) {
    testDiscordWebhookBtn.addEventListener('click', async () => {
      const webhook = discordWebhookInput ? discordWebhookInput.value.trim() : '';
      testDiscordWebhookBtn.disabled = true;
      testDiscordWebhookBtn.innerHTML = `<i class="fa-solid fa-spinner fa-spin"></i> Testing...`;

      try {
        const res = await fetch('/api/notifications/test-discord', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ webhook_url: webhook })
        });
        const data = await res.json();
        if (data.status === 'success') {
          showToast(data.simulated ? 'Discord simulated ping verified! 🟢' : 'Live Discord alert posted! 🚀', 'success');
        } else {
          showToast(data.message || 'Failed to ping Discord webhook', 'error');
        }
      } catch (err) {
        showToast('Network error testing Discord webhook', 'error');
      } finally {
        testDiscordWebhookBtn.disabled = false;
        testDiscordWebhookBtn.innerHTML = `<i class="fa-solid fa-paper-plane"></i> Send Test Discord Ping`;
      }
    });
  }

  // -----------------------------------------------------------------
  // In-App Notification Center & Alert Bell
  // -----------------------------------------------------------------
  const notifBellBtn = document.getElementById('notifBellBtn');
  const notifDropdown = document.getElementById('notifDropdown');
  const notifBadge = document.getElementById('notifBadge');
  const notifList = document.getElementById('notifList');
  const clearNotifsBtn = document.getElementById('clearNotifsBtn');

  function escapeHtml(str) {
    if (!str) return '';
    return str.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
  }

  async function fetchNotifications() {
    try {
      const res = await fetch('/api/notifications');
      const data = await res.json();
      if (data.status === 'success') {
        const unread = data.unread_count || 0;
        if (notifBadge) {
          notifBadge.textContent = unread;
          if (unread > 0) {
            notifBadge.classList.remove('hidden');
          } else {
            notifBadge.classList.add('hidden');
          }
        }

        if (notifList) {
          if (!data.notifications || data.notifications.length === 0) {
            notifList.innerHTML = `<div class="notif-empty"><i class="fa-solid fa-bell-slash"></i> No active price drop alerts</div>`;
            return;
          }

          notifList.innerHTML = data.notifications.map(n => {
            const drop = n.drop_amount ? formatMoney(n.drop_amount) : '';
            return `
              <div class="notif-card-item" data-prod-id="${n.product_id}">
                <div class="notif-card-icon"><i class="fa-solid fa-bolt"></i></div>
                <div class="notif-card-body">
                  <div class="notif-card-title">${escapeHtml(n.product_title)}</div>
                  <div class="notif-card-desc">
                    ${n.status === 'BUY_SIGNAL' ? '🔥 Buy Signal' : '⚡ Alert Triggered'}: Now ${formatMoney(n.current_price)}
                    ${drop ? `<span style="color: var(--accent-emerald); font-weight: 700;">(Met target by ${drop})</span>` : ''}
                  </div>
                  <div class="notif-card-time"><i class="fa-regular fa-clock"></i> ${n.created_at || 'Just now'}</div>
                </div>
              </div>
            `;
          }).join('');

          // Click on notif card item highlights product in grid
          notifList.querySelectorAll('.notif-card-item').forEach(item => {
            item.addEventListener('click', () => {
              const pid = item.dataset.prodId;
              if (notifDropdown) notifDropdown.classList.add('hidden');
              const card = document.querySelector(`[data-id="${pid}"]`);
              if (card) {
                card.scrollIntoView({ behavior: 'smooth', block: 'center' });
                card.style.transition = 'box-shadow 0.4s ease, border-color 0.4s ease';
                card.style.boxShadow = '0 0 25px var(--accent-emerald)';
                card.style.borderColor = 'var(--accent-emerald)';
                setTimeout(() => {
                  card.style.boxShadow = '';
                  card.style.borderColor = '';
                }, 2400);
              }
            });
          });
        }
      }
    } catch (e) {
      console.warn('Error fetching notifications:', e);
    }
  }

  if (notifBellBtn) {
    notifBellBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      if (notifDropdown) notifDropdown.classList.toggle('hidden');
    });
  }

  if (clearNotifsBtn) {
    clearNotifsBtn.addEventListener('click', async () => {
      try {
        await fetch('/api/notifications/mark-read', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ all: true })
        });
        if (notifBadge) notifBadge.classList.add('hidden');
        showToast('All notifications marked as read', 'info');
      } catch (err) {
        showToast('Error marking notifications read', 'error');
      }
    });
  }

  document.addEventListener('click', (e) => {
    if (notifDropdown && !notifDropdown.classList.contains('hidden')) {
      if (!notifDropdown.contains(e.target) && !notifBellBtn.contains(e.target)) {
        notifDropdown.classList.add('hidden');
      }
    }
  });

  // =================================================================
  // 6-Feature Intelligence Suite: Simulator & Basket Arbitrage
  // =================================================================
  async function simulateProductDrop(id) {
    if (!id) return;
    showToast('⚡ Triggering -30% Flash Crash on Amazon Tracker...', 'info');
    try {
      const res = await fetch(`/api/products/${id}/simulate-drop`, { method: 'POST' });
      const data = await res.json();
      if (data.status === 'success') {
        showToast(`⚡ Flash Crash Active! Dropped -${data.drop_pct}% to ${formatMoney(data.new_price)} (Alert Target Cross)`, 'success');
        await fetchProducts();
        if (currentModalProductId == id) {
          openChartModal(id);
        }
      } else {
        showToast(data.message || 'Simulation failed', 'error');
      }
    } catch (err) {
      showToast('Error running flash drop simulation', 'error');
    }
  }

  async function resetProductPrice(id) {
    if (!id) return;
    try {
      const res = await fetch(`/api/products/${id}/reset-price`, { method: 'POST' });
      const data = await res.json();
      if (data.status === 'success') {
        showToast(`Price reset to baseline: ${formatMoney(data.current_price)}`, 'info');
        await fetchProducts();
        if (currentModalProductId == id) {
          openChartModal(id);
        }
      } else {
        showToast(data.message || 'Reset failed', 'error');
      }
    } catch (err) {
      showToast('Error resetting price', 'error');
    }
  }

  // Modal Simulator Buttons
  const modalSimulateDropBtn = document.getElementById('modalSimulateDropBtn');
  if (modalSimulateDropBtn) {
    modalSimulateDropBtn.addEventListener('click', () => {
      if (currentModalProductId) simulateProductDrop(currentModalProductId);
    });
  }

  const modalResetPriceBtn = document.getElementById('modalResetPriceBtn');
  if (modalResetPriceBtn) {
    modalResetPriceBtn.addEventListener('click', () => {
      if (currentModalProductId) resetProductPrice(currentModalProductId);
    });
  }

  // Multi-Item Basket Arbitrage Functions
  function updateBasketFloatingBar() {
    if (!basketFloatingBar) return;
    if (basketSelectedIds.size > 0) {
      basketFloatingBar.classList.remove('hidden');
      if (basketCountBadge) basketCountBadge.textContent = basketSelectedIds.size;
      if (basketSummaryText) {
        basketSummaryText.textContent = `${basketSelectedIds.size} item${basketSelectedIds.size > 1 ? 's' : ''} selected across stores`;
      }
    } else {
      basketFloatingBar.classList.add('hidden');
    }
  }

  if (basketClearBtn) {
    basketClearBtn.addEventListener('click', () => {
      basketSelectedIds.clear();
      document.querySelectorAll('.basket-item-check').forEach(cb => cb.checked = false);
      updateBasketFloatingBar();
    });
  }

  if (basketOptimizeBtn) {
    basketOptimizeBtn.addEventListener('click', async () => {
      if (basketSelectedIds.size === 0) {
        showToast('Select at least 1 product to optimize cart arbitrage', 'warning');
        return;
      }
      showToast('Computing multi-store split-cart arbitrage across 18 stores...', 'info');
      try {
        const res = await fetch('/api/basket/optimize', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ product_ids: Array.from(basketSelectedIds) })
        });
        const data = await res.json();
        if (data.status === 'success') {
          renderBasketModalResults(data.result);
          if (basketModal) basketModal.classList.remove('hidden');
        } else {
          showToast(data.message || 'Failed to optimize basket', 'error');
        }
      } catch (err) {
        showToast('Error optimizing cart arbitrage', 'error');
      }
    });
  }

  if (closeBasketModal && basketModal) {
    closeBasketModal.addEventListener('click', () => {
      basketModal.classList.add('hidden');
    });
  }

  function renderBasketModalResults(result) {
    const bannerTitle = document.getElementById('basketVerdictTitle');
    const bannerSub = document.getElementById('basketVerdictSub');
    const savingsVal = document.getElementById('basketSavingsVal');
    const optTotal = document.getElementById('basketOptimalTotal');
    const optBreakdown = document.getElementById('basketOptimalBreakdown');
    const singleList = document.getElementById('basketSingleStoreList');

    if (savingsVal) savingsVal.textContent = formatMoney(result.total_savings_vs_amazon);
    if (optTotal) optTotal.textContent = formatMoney(result.optimal_total_cost);

    if (bannerTitle) {
      bannerTitle.textContent = result.total_savings_vs_amazon > 0 
        ? `Split-Cart Saves ${formatMoney(result.total_savings_vs_amazon)} (${result.savings_pct}% Off!)`
        : 'Amazon is already the lowest total cost!';
    }
    if (bannerSub) {
      bannerSub.textContent = `Optimized across ${result.item_count} items comparing Amazon vs 18 partner retailers.`;
    }

    if (optBreakdown && result.optimal_split) {
      optBreakdown.innerHTML = result.optimal_split.map(item => `
        <div class="plan-item-row">
          <div>
            <strong>${item.title}</strong>
            <div class="text-subtle" style="font-size: 0.7rem;">Cheapest at <span class="plan-item-store">${item.best_store}</span> (vs Amazon: ${formatMoney(item.amazon_price)})</div>
          </div>
          <div class="text-emerald" style="font-weight: 800; font-size: 0.95rem;">
            ${formatMoney(item.best_price)}
          </div>
        </div>
      `).join('');
    }

    if (singleList && result.single_store_totals) {
      singleList.innerHTML = result.single_store_totals.map(s => `
        <div class="store-rank-item">
          <div>
            <strong>${s.store}</strong>
            <span class="text-subtle" style="font-size: 0.7rem; margin-left: 6px;">(${s.items_available}/${result.item_count} available)</span>
          </div>
          <div style="font-weight: 700;">
            ${formatMoney(s.total_cost)}
          </div>
        </div>
      `).join('');
    }
  }

  // Toast Helper & GSAP Slide
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

  // Initial Load & Animations
  initGSAPAnimations();
  checkAuthStatus();
  initDashboardGoogleAuth();
  fetchProducts();
  fetchSchedulerStatus();
  fetchNotifications();
  // Periodic background check of scheduler & notifications
  setInterval(fetchSchedulerStatus, 30000);
  setInterval(fetchNotifications, 45000);
});
