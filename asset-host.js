/* Large authored assets stay in Git; Pages serves the lightweight review UI.
 * This ref contains every excluded asset. Keep it pinned when preparing a new publication.
 */
(() => {
  'use strict';
  const assetRef = 'b1ab56e5c8a65b5484f9cc008be7961e8724a67e';
  const assetBase = `https://raw.githubusercontent.com/recdpz/ravedio-avatar-previews/${assetRef}/`;
  const pagePrefix = location.hostname === 'recdpz.github.io' ? '/ravedio-avatar-previews/' : '/';
  const extensions = /\.(?:glb|blend|zip|png|exr)$/i;
  const localAssets = ['127.0.0.1', 'localhost', '[::1]'].includes(location.hostname);
  function resolve(value) {
    if (localAssets) return value;
    if (typeof value !== 'string' && !(value instanceof URL)) return value;
    let url;
    try { url = new URL(String(value), document.baseURI); } catch { return value; }
    if (url.origin !== location.origin || !url.pathname.startsWith(pagePrefix) || !extensions.test(url.pathname)) return value;
    return assetBase + url.pathname.slice(pagePrefix.length) + url.search + url.hash;
  }
  const fetchOriginal = window.fetch;
  window.fetch = function(input, init) {
    if (input instanceof Request) {
      const url = resolve(input.url);
      if (url !== input.url) input = new Request(url, input);
    } else input = resolve(input);
    return fetchOriginal.call(this, input, init);
  };
  const openOriginal = XMLHttpRequest.prototype.open;
  XMLHttpRequest.prototype.open = function(method, url, ...args) {
    return openOriginal.call(this, method, resolve(url), ...args);
  };
  for (const [prototype, key] of [[HTMLImageElement.prototype, 'src'], [HTMLAnchorElement.prototype, 'href']]) {
    const property = Object.getOwnPropertyDescriptor(prototype, key);
    Object.defineProperty(prototype, key, {
      ...property,
      set(value) {
        const url = resolve(value);
        if (key === 'src' && String(url).startsWith(assetBase) && !this.crossOrigin) this.crossOrigin = 'anonymous';
        property.set.call(this, url);
      }
    });
  }
  const setAttributeOriginal = Element.prototype.setAttribute;
  Element.prototype.setAttribute = function(name, value) {
    if ((this instanceof HTMLImageElement && name.toLowerCase() === 'src') ||
        (this instanceof HTMLAnchorElement && name.toLowerCase() === 'href')) {
      const url = resolve(value);
      if (this instanceof HTMLImageElement && String(url).startsWith(assetBase) && !this.crossOrigin) this.crossOrigin = 'anonymous';
      value = url;
    }
    return setAttributeOriginal.call(this, name, value);
  };
  // Older comparison pages create image/download galleries from HTML strings.
  function resolveMarkup(value) {
    if (typeof value !== 'string') return value;
    return value.replace(/\b(src|href)\s*=\s*(["'])(.*?)\2/gi,
      (_, name, quote, url) => `${name}=${quote}${resolve(url)}${quote}`)
      .replace(/<img\b[^>]*>/gi, tag => tag.includes(assetBase) && !/\bcrossorigin\s*=/i.test(tag)
        ? tag.replace(/^<img\b/i, '<img crossorigin="anonymous"') : tag);
  }
  const innerHTMLOriginal = Object.getOwnPropertyDescriptor(Element.prototype, 'innerHTML');
  Object.defineProperty(Element.prototype, 'innerHTML', {
    ...innerHTMLOriginal,
    set(value) { innerHTMLOriginal.set.call(this, resolveMarkup(value)); }
  });
  const adjacentOriginal = Element.prototype.insertAdjacentHTML;
  Element.prototype.insertAdjacentHTML = function(position, value) {
    return adjacentOriginal.call(this, position, resolveMarkup(value));
  };
  window.ravedioAssetHost = Object.freeze({assetRef, assetBase, resolve});
})();
