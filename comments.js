(function() {
  const CONFIG = {
    repo: 'spfpt/spfpt.github.io',
    repoId: 'R_kgDOSihTqA',
    category: 'General',
    categoryId: 'DIC_kwDOSihTqM4C9heN'
  };

  function currentTheme() {
    const explicit = document.documentElement.getAttribute('data-theme');
    if (explicit === 'light' || explicit === 'dark') return explicit;
    return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
  }

  function giscusTheme() {
    return currentTheme() === 'dark' ? 'dark_dimmed' : 'light';
  }

  function setGiscusTheme() {
    const frame = document.querySelector('iframe.giscus-frame');
    if (!frame) return;
    frame.contentWindow.postMessage({
      giscus: { setConfig: { theme: giscusTheme() } }
    }, 'https://giscus.app');
  }

  function injectStyles() {
    const style = document.createElement('style');
    style.textContent = `
      .comments {
        max-width: 60rem;
        margin: 4rem auto 0;
        padding-top: 2.4rem;
        border-top: 1px solid var(--rule);
      }
      .comments-title {
        font-weight: 600;
        font-size: 1.45rem;
        line-height: 1.2;
        letter-spacing: -0.015em;
        color: var(--ink);
        margin: 0 0 1.35rem;
      }
    `;
    document.head.appendChild(style);
  }

  function injectComments() {
    const article = document.querySelector('main.article');
    if (!article || article.querySelector('.comments')) return;

    injectStyles();

    const section = document.createElement('section');
    section.className = 'comments';
    section.setAttribute('aria-labelledby', 'comments-title');
    section.innerHTML = '<p class="comments-title" id="comments-title">Comments</p><div class="comments-frame"></div>';
    article.appendChild(section);

    const giscus = document.createElement('script');
    Object.entries({
      src: 'https://giscus.app/client.js',
      'data-repo': CONFIG.repo,
      'data-repo-id': CONFIG.repoId,
      'data-category': CONFIG.category,
      'data-category-id': CONFIG.categoryId,
      'data-mapping': 'pathname',
      'data-strict': '0',
      'data-reactions-enabled': '1',
      'data-emit-metadata': '0',
      'data-input-position': 'bottom',
      'data-theme': giscusTheme(),
      'data-lang': 'en',
      'data-loading': 'lazy',
      crossorigin: 'anonymous',
      async: ''
    }).forEach(([name, value]) => giscus.setAttribute(name, value));
    section.querySelector('.comments-frame').appendChild(giscus);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', injectComments);
  } else {
    injectComments();
  }

  new MutationObserver(setGiscusTheme).observe(document.documentElement, {
    attributes: true,
    attributeFilter: ['data-theme']
  });

  window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', setGiscusTheme);
})();
