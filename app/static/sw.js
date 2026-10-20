const CACHE = 'intercity-dairy-static-v6';
const SHELL = [
  '/manifest.json',
  '/static/css/app.css',
  '/static/js/app.js',
  '/static/icons/icon.jfif',
  '/static/icons/intercity-dairy-farm.jfif'
];

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE)
      .then((cache) => cache.addAll(SHELL))
      .then(() => self.skipWaiting())
  );
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys()
      .then((keys) => Promise.all(
        keys.filter((key) => key !== CACHE).map((key) => caches.delete(key))
      ))
      .then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', (event) => {
  const request = event.request;
  if (request.method !== 'GET') return;

  const url = new URL(request.url);
  // Never cache HTML pages, API responses, or cross-origin requests: pages may
  // contain private farm/customer data tied to the currently signed-in user.
  const isStaticAsset = url.origin === self.location.origin &&
    (url.pathname.startsWith('/static/') || url.pathname === '/manifest.json');

  if (!isStaticAsset) return;

  event.respondWith(
    fetch(request).then((response) => {
      if (response.ok) {
        const copy = response.clone();
        caches.open(CACHE).then((cache) => cache.put(request, copy));
      }
      return response;
    }).catch(async () => {
      const cached = await caches.match(request);
      return cached || new Response('This asset is unavailable offline.', {
        status: 503,
        headers: { 'Content-Type': 'text/plain; charset=utf-8' }
      });
    })
  );
});
