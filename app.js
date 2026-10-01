const state = {
  categories: [],
  schools: new Map(),
  leaderboard: [],
  selectedSchoolId: localStorage.getItem('ksl_school_id') || null,
  pendingClicks: 0,
  sessionClicks: 0,
  sendInFlight: false,
  audio: null,
  openedLeaderboardOnce: false,
  lastLeaderboardCounts: new Map(),
};

const $ = (id) => document.getElementById(id);
const fmt = (n) => new Intl.NumberFormat('ru-RU').format(n);

function toast(message) {
  const el = $('toast');
  el.textContent = message;
  el.classList.add('show');
  clearTimeout(toast.timer);
  toast.timer = setTimeout(() => el.classList.remove('show'), 2200);
}

function animateNumber(el, target, duration = 360) {
  const from = Number(el.dataset.value || el.textContent.replace(/\D/g, '') || 0);
  if (from === target) return;
  const start = performance.now();
  el.dataset.value = String(target);
  const tick = (now) => {
    const p = Math.min(1, (now - start) / duration);
    const eased = 1 - Math.pow(1 - p, 3);
    const value = Math.round(from + (target - from) * eased);
    el.textContent = fmt(value);
    if (p < 1) requestAnimationFrame(tick);
  };
  requestAnimationFrame(tick);
}

async function api(url, options = {}) {
  const res = await fetch(url, { credentials: 'same-origin', ...options });
  if (!res.ok) throw new Error((await res.text()) || `HTTP ${res.status}`);
  return res.json();
}

async function bootstrap() {
  try {
    await api('/api/session');
    const data = await api('/api/schools');
    state.categories = data.categories;
    data.categories.forEach(category => category.schools.forEach(s => state.schools.set(s.id, s)));
    renderCategories();
    if (state.selectedSchoolId && state.schools.has(state.selectedSchoolId)) {
      showRememberedSchoolButton();
    }
  } catch (err) {
    console.error(err);
    toast('Не удалось загрузить список учебных заведений');
  }

  $('leaderboardToggle').addEventListener('click', toggleLeaderboard);
  $('aboutBtn').addEventListener('click', openAbout);
  $('changeSchoolBtn').addEventListener('click', backToSelection);
  $('heroClickArea').addEventListener('pointerdown', handleClick, { passive: true });
  document.querySelectorAll('[data-close]').forEach(el => el.addEventListener('click', () => closeSheet(el.dataset.close)));

  setInterval(() => { refreshLeaderboard().catch(console.error); }, 5000);
  setInterval(() => { refreshStats().catch(console.error); }, 30000);
  setInterval(() => { sendClicks().catch(console.error); heartbeat().catch(console.error); }, 7000);
  setInterval(() => { heartbeat().catch(console.error); }, 25000);

  window.addEventListener('pagehide', () => flushBeacon());
  document.addEventListener('visibilitychange', () => { if (document.visibilityState === 'hidden') flushBeacon(); });
}

const CATEGORY_LABELS = {
  universities: 'ВУЗы',
  colleges: 'Колледжи и техникумы',
  lyceums_gymnasiums: 'Лицеи, гимназии и школы-интернаты',
  private_schools: 'Частные школы',
  general_schools: 'Общеобразовательные школы',
};

function renderCategories() {
  const grid = $('categoryGrid');
  grid.innerHTML = '';
  state.categories.forEach(category => {
    const btn = document.createElement('button');
    btn.className = 'category-card';
    btn.innerHTML = `<strong>${escapeHtml(category.name)}</strong><span>Выбрать учебное заведение</span><span class="count">${category.schools.length} вариантов</span>`;
    btn.addEventListener('click', () => openCategory(category));
    grid.appendChild(btn);
  });
}

function showRememberedSchoolButton() {
  const btn = $('rememberedSchoolBtn');
  const school = state.schools.get(state.selectedSchoolId);
  if (!school) return;
  btn.textContent = `Продолжить с «${school.name}»`;
  btn.classList.remove('hidden');
  btn.onclick = () => selectSchool(school.id);
}

function openCategory(category) {
  const grid = $('categoryGrid');
  grid.innerHTML = '';
  const title = document.createElement('div');
  title.style.gridColumn = '1 / -1';
  title.innerHTML = `<div class="eyebrow">КАТЕГОРИЯ</div><h2 style="font-size:32px; margin:6px 0 4px; letter-spacing:-.04em">${escapeHtml(category.name)}</h2><p style="color:var(--muted);margin-bottom:8px">Выберите своё учебное заведение</p>`;
  grid.appendChild(title);
  category.schools.forEach(school => {
    const btn = document.createElement('button');
    btn.className = 'category-card';
    btn.innerHTML = `<strong>${escapeHtml(school.name)}</strong><span>Открыть страницу и начать кликать</span>`;
    btn.addEventListener('click', () => selectSchool(school.id));
    grid.appendChild(btn);
  });
  const back = document.createElement('button');
  back.className = 'secondary-button';
  back.textContent = '← Назад к категориям';
  back.onclick = renderCategories;
  grid.appendChild(back);
}

function selectSchool(id) {
  const school = state.schools.get(id);
  if (!school) return;
  state.selectedSchoolId = id;
  localStorage.setItem('ksl_school_id', id);
  const key = `ksl_session_clicks_${id}`;
  state.sessionClicks = Number(sessionStorage.getItem(key) || 0);
  state.pendingClicks = 0;
  state.lastLeaderboardCounts.clear();
  animateNumber($('sessionClicks'), state.sessionClicks, 0);
  $('selectionView').classList.add('hidden');
  $('schoolView').classList.remove('hidden');
  $('categoryLabel').textContent = school.category_label;
  $('schoolName').textContent = school.name;
  $('heroMobileSource').srcset = school.images.mobile;
  $('heroImage').src = school.images.desktop;
  $('heroImage').alt = school.name;
  refreshLeaderboard().catch(console.error);
  refreshStats().catch(console.error);
  loadAbout().catch(console.error);
}

function backToSelection() {
  closeSheet('leaderboard');
  closeSheet('about');
  $('schoolView').classList.add('hidden');
  $('selectionView').classList.remove('hidden');
  renderCategories();
  showRememberedSchoolButton();
}

function handleClick(event) {
  if (!state.selectedSchoolId) return;
  state.pendingClicks += 1;
  state.sessionClicks += 1;
  sessionStorage.setItem(`ksl_session_clicks_${state.selectedSchoolId}`, String(state.sessionClicks));
  animateNumber($('sessionClicks'), state.sessionClicks);
  spawnFloat(event);
  playClickSound();
}

function spawnFloat(event) {
  const area = $('heroClickArea').getBoundingClientRect();
  const x = event.clientX - area.left;
  const y = event.clientY - area.top;
  const el = document.createElement('span');
  el.className = 'float-number';
  el.textContent = '+1';
  el.style.left = `${Math.max(12, Math.min(area.width - 12, x))}px`;
  el.style.top = `${Math.max(12, Math.min(area.height - 12, y))}px`;
  $('floatLayer').appendChild(el);
  el.addEventListener('animationend', () => el.remove(), { once: true });
}

function playClickSound() {
  try {
    if (!state.audio) state.audio = new Audio('/assets/branding/sounds/pop.mp3');
    state.audio.currentTime = 0;
    const promise = state.audio.play();
    if (promise?.catch) promise.catch(() => {});
  } catch {}
}

async function sendClicks() {
  if (!state.pendingClicks || !state.selectedSchoolId || state.sendInFlight) return;
  state.sendInFlight = true;
  const batch = state.pendingClicks;
  try {
    const result = await api('/api/clicks', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ school_id: state.selectedSchoolId, clicks: batch }),
    });
    state.pendingClicks = Math.max(0, state.pendingClicks - batch);
    if (result.rejected > 0) {
      state.sessionClicks = Math.max(0, state.sessionClicks - result.rejected);
      sessionStorage.setItem(`ksl_session_clicks_${state.selectedSchoolId}`, String(state.sessionClicks));
      animateNumber($('sessionClicks'), state.sessionClicks);
      toast(`Сервер не засчитал ${fmt(result.rejected)} кликов: лимит ${fmt(result.limit_per_minute)}/мин.`);
    }
    refreshLeaderboard().catch(console.error);
  } catch (err) {
    console.warn('Click sync failed', err);
  } finally {
    state.sendInFlight = false;
  }
}

function flushBeacon() {
  if (!state.pendingClicks || !state.selectedSchoolId || !navigator.sendBeacon) return;
  const batch = state.pendingClicks;
  const body = JSON.stringify({ school_id: state.selectedSchoolId, clicks: batch });
  const blob = new Blob([body], { type: 'application/json' });
  if (navigator.sendBeacon('/api/clicks', blob)) state.pendingClicks = 0;
}

async function heartbeat() {
  await api('/api/heartbeat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ school_id: state.selectedSchoolId }),
  });
}

async function refreshLeaderboard() {
  const data = await api('/api/leaderboard');

  const previousCounts = state.lastLeaderboardCounts;
  const hadBaseline = previousCounts.size > 0;
  const selectedPrevious = state.selectedSchoolId ? previousCounts.get(state.selectedSchoolId) : undefined;
  const firstRects = snapshotLeaderboardRows();

  state.leaderboard = data.items;
  const leader = state.leaderboard[0];
  if (leader) {
    $('leaderName').textContent = leader.name;
    animateNumber($('leaderClicks'), leader.clicks);
  }

  const mine = state.leaderboard.find(x => x.id === state.selectedSchoolId);
  $('myRank').textContent = mine ? `#${mine.rank}` : '—';
  renderLeaderboardRows(state.leaderboard, firstRects);

  if (hadBaseline && mine && Number.isFinite(selectedPrevious)) {
    const delta = mine.clicks - selectedPrevious;
    if (delta > 0) showLeaderboardDelta(delta);
  }

  state.lastLeaderboardCounts = new Map(state.leaderboard.map(item => [item.id, item.clicks]));
}

function snapshotLeaderboardRows() {
  const list = $('leaderboardList');
  const rects = new Map();
  list.querySelectorAll('.leader-row').forEach(row => {
    rects.set(row.dataset.id, row.getBoundingClientRect());
  });
  return rects;
}

function animateLeaderboardReorder(firstRects) {
  if (!firstRects.size || !Element.prototype.animate) return;
  const list = $('leaderboardList');
  list.querySelectorAll('.leader-row').forEach(row => {
    const first = firstRects.get(row.dataset.id);
    if (!first) return;
    const last = row.getBoundingClientRect();
    const dx = first.left - last.left;
    const dy = first.top - last.top;
    if (Math.abs(dx) < 1 && Math.abs(dy) < 1) return;
    row.animate(
      [
        { transform: `translate3d(${dx}px, ${dy}px, 0)` },
        { transform: 'translate3d(0, 0, 0)' },
      ],
      { duration: 520, easing: 'cubic-bezier(.2,.8,.2,1)' }
    );
  });
}

function renderLeaderboardRows(items, firstRects = new Map()) {
  const list = $('leaderboardList');
  const existing = new Map([...list.children].map(el => [el.dataset.id, el]));
  items.forEach(item => {
    let row = existing.get(item.id);
    if (!row) {
      row = document.createElement('div');
      row.className = 'leader-row';
      row.dataset.id = item.id;
      row.innerHTML = `<div class="leader-rank"></div><div><div class="leader-name"></div><div class="leader-meta"></div></div><div class="leader-count"></div>`;
    }
    row.classList.toggle('active', item.id === state.selectedSchoolId);
    row.querySelector('.leader-rank').textContent = item.rank;
    row.querySelector('.leader-name').textContent = item.name;
    row.querySelector('.leader-meta').textContent = CATEGORY_LABELS[item.category] || item.category;
    row.querySelector('.leader-count').textContent = `${fmt(item.clicks)} кликов`;
    list.appendChild(row);
  });
  animateLeaderboardReorder(firstRects);
  if (state.openedLeaderboardOnce === false) {
    state.openedLeaderboardOnce = true;
  }
}

function showLeaderboardDelta(delta) {
  const el = $('leaderboardDelta');
  el.textContent = `+${fmt(delta)}`;
  el.classList.remove('show');
  void el.offsetWidth;
  el.classList.add('show');
}

function toggleLeaderboard() {
  const open = $('leaderboardSheet').classList.contains('open');
  if (open) closeSheet('leaderboard');
  else openSheet('leaderboard');
}

function openSheet(name) {
  const el = $(name === 'leaderboard' ? 'leaderboardSheet' : 'aboutSheet');
  el.classList.add('open');
  el.setAttribute('aria-hidden', 'false');
  if (name === 'leaderboard') {
    $('leaderboardToggle').setAttribute('aria-expanded', 'true');
    setTimeout(scrollToMine, 120);
  }
}

function closeSheet(name) {
  const el = $(name === 'leaderboard' ? 'leaderboardSheet' : 'aboutSheet');
  el.classList.remove('open');
  el.setAttribute('aria-hidden', 'true');
  if (name === 'leaderboard') $('leaderboardToggle').setAttribute('aria-expanded', 'false');
}

function scrollToMine() {
  const row = $('leaderboardList').querySelector(`[data-id="${CSS.escape(state.selectedSchoolId || '')}"]`);
  if (row) row.scrollIntoView({ block: 'center', behavior: 'smooth' });
}

async function openAbout() {
  await loadAbout();
  openSheet('about');
}

async function loadAbout() {
  const data = await api('/api/about');
  $('aboutTitle').textContent = data.title;
  $('aboutText').textContent = data.text;
}

async function refreshStats() {
  const data = await api('/api/stats');
  animateNumber($('statUsers'), data.users);
  animateNumber($('statActive'), data.active_users);
  animateNumber($('statClicks'), data.total_clicks);
}

function escapeHtml(value) {
  return String(value).replace(/[&<>'"]/g, ch => ({'&':'&amp;','<':'&lt;','>':'&gt;',"'":'&#039;','"':'&quot;'}[ch]));
}

bootstrap();
