function toggleSidebar(){const s=document.getElementById('sidebar');if(s)s.classList.toggle('open')}

(() => {
  const root = document.documentElement;
  const themeButton = document.getElementById('themeToggle');
  const themeKey = 'intercity-dairy-theme';

  function setTheme(theme) {
    const selected = theme === 'dark' ? 'dark' : 'light';
    root.dataset.theme = selected;
    try { localStorage.setItem(themeKey, selected); } catch (_) {}
    if (themeButton) {
      themeButton.textContent = selected === 'dark' ? '☀️' : '🌙';
      themeButton.setAttribute('aria-label', selected === 'dark' ? 'Switch to light theme' : 'Switch to dark theme');
      themeButton.title = selected === 'dark' ? 'Switch to light theme' : 'Switch to dark theme';
    }
    const themeColor = document.querySelector('meta[name="theme-color"]');
    if (themeColor) themeColor.content = selected === 'dark' ? '#111917' : '#1688bd';
  }

  let savedTheme = '';
  try { savedTheme = localStorage.getItem(themeKey) || ''; } catch (_) {}
  setTheme(savedTheme || (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'));
  if (themeButton) themeButton.addEventListener('click', () => setTheme(root.dataset.theme === 'dark' ? 'light' : 'dark'));

  const prompt = document.getElementById('installPrompt');
  const installButton = document.getElementById('installAction');
  const dismissButton = document.getElementById('installDismiss');
  const help = document.getElementById('installPromptHelp');
  const copy = document.getElementById('installPromptText');
  if (!prompt || !installButton || !dismissButton) return;

  let installEvent = null;
  const isStandalone = () => window.matchMedia('(display-mode: standalone)').matches || window.navigator.standalone === true;
  const dismissedKey = 'intercity-dairy-install-dismissed';

  function wasDismissed() {
    try { return localStorage.getItem(dismissedKey) === '1'; } catch (_) { return false; }
  }
  function showPrompt(manualInstructions = false) {
    if (isStandalone() || wasDismissed()) return;
    prompt.hidden = false;
    installButton.hidden = !installEvent;
    help.hidden = !manualInstructions;
    if (manualInstructions) {
      copy.textContent = 'Install this app on your home screen for quicker access.';
      help.textContent = /iPad|iPhone|iPod/.test(navigator.userAgent)
        ? 'In Safari, tap Share, then “Add to Home Screen”.'
        : 'Open your browser menu and choose “Install app” or “Add to Home screen”.';
    }
  }

  window.addEventListener('beforeinstallprompt', (event) => {
    event.preventDefault();
    installEvent = event;
    showPrompt(false);
  });
  window.addEventListener('appinstalled', () => {
    prompt.hidden = true;
    installEvent = null;
    try { localStorage.removeItem(dismissedKey); } catch (_) {}
  });

  installButton.addEventListener('click', async () => {
    if (!installEvent) return;
    installEvent.prompt();
    try { await installEvent.userChoice; } catch (_) {}
    installEvent = null;
    prompt.hidden = true;
  });
  dismissButton.addEventListener('click', () => {
    prompt.hidden = true;
    try { localStorage.setItem(dismissedKey, '1'); } catch (_) {}
  });

  if (!isStandalone() && !wasDismissed()) {
    if (/iPad|iPhone|iPod/.test(navigator.userAgent) && /Safari/i.test(navigator.userAgent) && !/CriOS|FxiOS|EdgiOS/i.test(navigator.userAgent)) {
      window.addEventListener('load', () => setTimeout(() => showPrompt(true), 1800));
    }
    // Android/Chromium browsers show the prompt only after the browser confirms
    // that this site meets installability requirements via beforeinstallprompt.
  }
})();

if('serviceWorker' in navigator){window.addEventListener('load',()=>navigator.serviceWorker.register('/sw.js').catch(()=>{}))}
document.querySelectorAll('form').forEach(form=>{form.addEventListener('submit',()=>{const b=form.querySelector('button[type="submit"],button:not([type])');if(b&&b.dataset.noLoading!=='true'){b.disabled=true;setTimeout(()=>b.disabled=false,5000)}})})
