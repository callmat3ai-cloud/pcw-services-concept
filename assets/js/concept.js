/* Preview enhancement only. Form handler and endpoint remain in main.js. */
(() => {
  'use strict';
  let active = null;
  let returnFocus = null;
  const focusable = 'a[href],button:not([disabled]),input:not([disabled]),select:not([disabled]),textarea:not([disabled]),[tabindex="0"]';
  function updateFragment() {
    let id;
    try { id = decodeURIComponent(location.hash.slice(1)); } catch (_) { id = ''; }
    const target = document.getElementById(id);
    const next = target && target.classList.contains('modal') ? target : null;
    if (active && active !== next) { active.setAttribute('aria-hidden','true'); active = null; document.body.style.overflow = ''; if (returnFocus) returnFocus.focus({preventScroll:true}); }
    if (next && active !== next) {
      returnFocus = document.activeElement;
      active = next;
      next.setAttribute('aria-hidden','false');
      document.body.style.overflow = 'hidden';
      next.focus({preventScroll:true});
    }
    if (target && !next) {
      for (let p = target.parentElement; p; p = p.parentElement) if (p.tagName === 'DETAILS') p.open = true;
      if (id === 'estimate') { const details = target.querySelector('details'); if (details) details.open = true; }
    }
  }
  function closeDialog() { if (active) { const close = active.querySelector('.modal-close'); if (close) close.click(); else history.back(); } }
  document.addEventListener('keydown', event => {
    if (event.key === 'Escape' && active) { event.preventDefault(); closeDialog(); }
    if (event.key === 'Tab' && active) {
      const all = [...active.querySelectorAll(focusable)].filter(el => el.getClientRects().length);
      if (!all.length) { event.preventDefault(); return; }
      if (event.shiftKey && (document.activeElement === all[0] || document.activeElement === active)) { event.preventDefault(); all.at(-1).focus(); }
      else if (!event.shiftKey && (document.activeElement === all.at(-1) || document.activeElement === active)) { event.preventDefault(); all[0].focus(); }
    }
  });
  document.addEventListener('click', event => {
    if (active && event.target === active) closeDialog();
    const anchor=event.target.closest('a[href^="#"]');
    if(anchor && !anchor.closest('.modal')) returnFocus=anchor;
  });
  window.addEventListener('hashchange',updateFragment);
  document.addEventListener('DOMContentLoaded', () => {
    updateFragment();
    document.querySelectorAll('.explorer-search').forEach(input => {
      const explorer = input.closest('.service-explorer');
      const cards = [...explorer.querySelectorAll('.dir-card')];
      const status = explorer.querySelector('.explorer-status');
      const filter = () => {
        const value = input.value.trim().toLocaleLowerCase();
        let visible = 0;
        cards.forEach(card => { const match = card.textContent.toLocaleLowerCase().includes(value); card.hidden = !match; if (match) visible++; });
        status.textContent = value ? (visible ? `${visible} matching services` : 'No matching services. Try a different search.') : `${cards.length} services`;
      };
      input.addEventListener('input',filter);filter();
    });
  });
})();
