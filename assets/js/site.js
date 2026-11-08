/* PCW concept site — navigation and dialog behaviour.
   Content is fully usable without this file. */
(function () {
  'use strict';

  document.documentElement.classList.add('js');

  var drawer = document.getElementById('drawer');
  var openBtn = document.querySelector('[data-drawer-open]');
  var closeBtn = document.querySelector('[data-drawer-close]');
  var lastFocus = null;

  function openDrawer() {
    if (!drawer) return;
    lastFocus = document.activeElement;
    drawer.dataset.open = 'true';
    drawer.setAttribute('aria-hidden', 'false');
    if (openBtn) openBtn.setAttribute('aria-expanded', 'true');
    document.documentElement.style.overflow = 'hidden';
    var first = drawer.querySelector('a, button');
    if (first) first.focus();
  }

  function closeDrawer() {
    if (!drawer) return;
    drawer.dataset.open = 'false';
    drawer.setAttribute('aria-hidden', 'true');
    if (openBtn) openBtn.setAttribute('aria-expanded', 'false');
    document.documentElement.style.overflow = '';
    if (lastFocus && lastFocus.focus) lastFocus.focus();
  }

  if (openBtn) openBtn.addEventListener('click', openDrawer);
  if (closeBtn) closeBtn.addEventListener('click', closeDrawer);

  document.addEventListener('keydown', function (e) {
    if (e.key !== 'Escape') return;
    if (drawer && drawer.dataset.open === 'true') {
      closeDrawer();
      return;
    }
    if (location.hash.indexOf('#proj-') === 0 || location.hash.indexOf('#prop-') === 0) {
      location.hash = '';
    }
  });

  // Close a fragment dialog when its backdrop is clicked or its close link is used.
  document.addEventListener('click', function (e) {
    var modal = e.target.closest ? e.target.closest('.modal') : null;
    if (!modal) return;
    if (e.target === modal || (e.target.closest && e.target.closest('.modal__close'))) {
      if (e.target.closest('.modal__close')) e.preventDefault();
      location.hash = '';
    }
  });

  // Keep dialogs reachable by keyboard: focus the card when opened by fragment.
  window.addEventListener('hashchange', function () {
    var target = document.querySelector(location.hash);
    if (target && target.classList.contains('modal')) {
      var card = target.querySelector('.modal__card');
      if (card) {
        card.setAttribute('tabindex', '-1');
        card.focus({ preventScroll: true });
      }
    }
  });
})();
