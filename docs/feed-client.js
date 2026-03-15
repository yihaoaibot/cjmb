(() => {
  const state = JSON.parse(document.getElementById('page-state')?.textContent || '{}');
  const initialUpdatedAt = state.updated || '';
  const html = document.documentElement;
  const savedTheme = localStorage.getItem('cjmb-theme');
  if (savedTheme === 'dark') html.classList.add('dark');
  const searchInput = document.getElementById('searchInput');
  const refreshBtn = document.getElementById('refreshBtn');
  const themeBtn = document.getElementById('themeBtn');
  const notice = document.getElementById('updateNotice');
  const noticeRefreshBtn = document.getElementById('noticeRefreshBtn');
  function applyThemeToggle(){ html.classList.toggle('dark'); localStorage.setItem('cjmb-theme', html.classList.contains('dark') ? 'dark' : 'light'); }
  function refreshPage(){ window.location.reload(); }
  function filterCards(){ const q = (searchInput?.value || '').toLowerCase().trim(); document.querySelectorAll('.item').forEach(item => { const hay = item.dataset.search || ''; item.style.display = !q || hay.includes(q) ? '' : 'none'; }); }
  function toggleItem(btn){ const text = btn.parentElement.querySelector('.text'); const expanded = btn.dataset.expanded === '1'; if (expanded) { text.textContent = text.dataset.short || ''; btn.dataset.expanded = '0'; btn.textContent = '展开全文'; } else { text.textContent = text.dataset.full || ''; btn.dataset.expanded = '1'; btn.textContent = '收起'; } }
  let autoReloading = false;
  async function checkForUpdates(){
    try {
      const res = await fetch('./meta.json?ts=' + Date.now(), { cache: 'no-store' });
      if (!res.ok) return;
      const meta = await res.json();
      if (meta.updated_at && meta.updated_at !== initialUpdatedAt) {
        if (notice) notice.style.display = 'flex';
        if (!autoReloading) {
          autoReloading = true;
          setTimeout(() => window.location.reload(), 800);
        }
      }
    } catch {}
  }
  searchInput?.addEventListener('input', filterCards);
  refreshBtn?.addEventListener('click', refreshPage);
  themeBtn?.addEventListener('click', applyThemeToggle);
  noticeRefreshBtn?.addEventListener('click', refreshPage);
  document.querySelectorAll('.toggle').forEach(btn => btn.addEventListener('click', () => toggleItem(btn)));
  setInterval(checkForUpdates, 60000);
})();
