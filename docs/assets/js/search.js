/**
 * Search Functionality (lightweight)
 * - Builds an index from sidebar links and current page headings
 * - Provides simple substring search with result highlighting
 */

(function () {
  'use strict';

  function escapeHtml(text) {
    return String(text)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#39;');
  }

  function normalize(text) {
    return String(text).toLowerCase();
  }

  function highlight(text, query) {
    if (!query) return escapeHtml(text);
    const raw = String(text);
    const lower = raw.toLowerCase();
    const q = query.toLowerCase();

    const idx = lower.indexOf(q);
    if (idx === -1) return escapeHtml(raw);

    const before = escapeHtml(raw.slice(0, idx));
    const match = escapeHtml(raw.slice(idx, idx + q.length));
    const after = escapeHtml(raw.slice(idx + q.length));
    return `${before}<mark>${match}</mark>${after}`;
  }

  function buildIndex() {
    const data = [];

    // Sidebar links (primary index)
    const navLinks = document.querySelectorAll('.toc-link');
    navLinks.forEach((a) => {
      const title = (a.textContent || '').trim();
      const url = a.getAttribute('href');
      if (!title || !url) return;
      data.push({
        title,
        url,
        content: title,
        type: 'nav'
      });
    });

    // Current page headings (secondary index)
    const headings = document.querySelectorAll('.page-content h1, .page-content h2, .page-content h3');
    headings.forEach((h) => {
      const title = (h.textContent || '').trim();
      if (!title) return;
      const id = h.id ? `#${h.id}` : '';
      data.push({
        title,
        url: `${window.location.pathname}${id}`,
        content: title,
        type: 'heading'
      });
    });

    return data;
  }

  function createResultItem(item, query) {
    const titleHtml = highlight(item.title, query);
    const typeLabel = document.documentElement.lang === 'ja'
      ? (item.type === 'heading' ? '見出し' : '目次')
      : (item.type === 'heading' ? 'Heading' : 'TOC');

    return `
<a class="search-result-item" href="${escapeHtml(item.url)}">
  <div class="search-result-title">${titleHtml}</div>
  <div class="search-result-type">${escapeHtml(typeLabel)}</div>
</a>`;
  }

  function init() {
    const input = document.getElementById('search-input');
    const results = document.getElementById('search-results');

    if (!input || !results) return;

    const index = buildIndex();
    const MAX_RESULTS = 10;
    const MIN_LENGTH = 1;

    function hide() {
      results.classList.remove('active');
      results.innerHTML = '';
    }

    function show() {
      results.classList.add('active');
    }

    function search(query) {
      const q = query.trim();
      if (q.length < MIN_LENGTH) {
        hide();
        return;
      }

      const nq = normalize(q);
      const matched = [];

      for (const item of index) {
        const hay = normalize(item.title + ' ' + item.content);
        if (hay.includes(nq)) matched.push(item);
        if (matched.length >= MAX_RESULTS) break;
      }

      if (matched.length === 0) {
        const msg = document.documentElement.lang === 'ja'
          ? `「${escapeHtml(q)}」の検索結果はありません`
          : `No results found for "${escapeHtml(q)}"`;
        results.innerHTML = `<div class="search-no-results">${msg}</div>`;
        show();
        return;
      }

      results.innerHTML = matched.map((item) => createResultItem(item, q)).join('');
      show();
    }

    input.addEventListener('input', (e) => {
      search(e.target.value);
    });

    input.addEventListener('focus', () => {
      if (input.value.trim()) search(input.value);
    });

    document.addEventListener('click', (e) => {
      if (!e.target.closest('.search-container')) hide();
    });

    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape') {
        hide();
        input.blur();
      }
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
