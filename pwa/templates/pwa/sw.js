importScripts('https://storage.googleapis.com/workbox-cdn/releases/6.1.5/workbox-sw.js');

const OFFLINE_URL = '{{ offline_url }}';
const appShell = [
    '{{ icon_url }}',
    '{{ manifest_url }}',
    '{{ offline_url }}',
].map((partialUrl) => `${location.protocol}//${location.host}${partialUrl}`);


if (workbox) {
    workbox.setConfig({ debug: false });
    workbox.precaching.precacheAndRoute(appShell.map(url => ({
        url,
        revision: null,
    })));

    workbox.routing.registerRoute(({url}) => appShell.includes(url), new workbox.strategies.CacheOnly());

    workbox.routing.setCatchHandler(({ event }) => {
        console.log(event);

        switch (event.request.method) {
            case 'GET':
                return caches.match(OFFLINE_URL);
            default:
                return Response.error();
        }
    });
}
