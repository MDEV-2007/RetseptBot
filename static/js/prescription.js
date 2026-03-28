'use strict';

// ─────────────────────────────────────────────────────────────────────────────
// Shared utilities
// ─────────────────────────────────────────────────────────────────────────────

function lockScroll()   { document.body.style.overflow = 'hidden'; }
function unlockScroll() { document.body.style.overflow = ''; }

/** Wire a modal overlay: open/close on trigger buttons and backdrop click. */
function initOverlay(overlayId, openId, closeId) {
  var overlay = document.getElementById(overlayId);
  var openBtn = openId  ? document.getElementById(openId)  : null;
  var closeBtn = closeId ? document.getElementById(closeId) : null;
  if (!overlay) return null;

  function open()  { overlay.classList.add('open');    lockScroll(); }
  function close() { overlay.classList.remove('open'); unlockScroll(); }

  if (openBtn)  openBtn.addEventListener('click', open);
  if (closeBtn) closeBtn.addEventListener('click', close);
  overlay.addEventListener('click', function (e) {
    if (e.target === overlay) close();
  });

  return { open: open, close: close, overlay: overlay };
}


// ─────────────────────────────────────────────────────────────────────────────
// Language switcher
// ─────────────────────────────────────────────────────────────────────────────

(function () {
  document.querySelectorAll('.lang-sw').forEach(function (sw) {
    var btn   = sw.querySelector('.lang-sw-btn');
    var form  = sw.querySelector('#langForm');
    var input = sw.querySelector('#langInput');
    if (!btn) return;

    btn.addEventListener('click', function (e) {
      e.stopPropagation();
      sw.classList.toggle('open');
    });

    sw.querySelectorAll('.lang-opt').forEach(function (opt) {
      opt.addEventListener('click', function () {
        if (input) input.value = opt.dataset.lang;
        if (form)  form.submit();
      });
    });
  });

  document.addEventListener('click', function () {
    document.querySelectorAll('.lang-sw.open').forEach(function (sw) {
      sw.classList.remove('open');
    });
  });
})();


// ─────────────────────────────────────────────────────────────────────────────
// Profile dropdown (topbar + dashboard avatar → logout)
// ─────────────────────────────────────────────────────────────────────────────

(function () {
  // Supports multiple profile dropdowns on the same page (topbar + dashboard)
  [
    { profileId: 'topbarProfile', btnId: 'topbarAvatarBtn' },
    { profileId: 'dashProfile',   btnId: 'dashAvatarBtn'   },
  ].forEach(function (ids) {
    var profile = document.getElementById(ids.profileId);
    var btn     = document.getElementById(ids.btnId);
    if (!profile || !btn) return;

    btn.addEventListener('click', function (e) {
      e.stopPropagation();
      profile.classList.toggle('open');
    });

    document.addEventListener('click', function () {
      profile.classList.remove('open');
    });
  });
})();


// ─────────────────────────────────────────────────────────────────────────────
// Sidebar (mobile)
// ─────────────────────────────────────────────────────────────────────────────

(function () {
  var sidebar  = document.getElementById('sidebar');
  var backdrop = document.getElementById('sidebarBackdrop');
  var openBtn  = document.getElementById('topbarToggle');
  var closeBtn = document.getElementById('sidebarClose');
  if (!sidebar) return;

  function open() {
    sidebar.classList.add('open');
    if (backdrop) { backdrop.style.display = 'block'; backdrop.classList.add('visible'); }
    lockScroll();
  }

  function close() {
    sidebar.classList.remove('open');
    if (backdrop) {
      backdrop.classList.remove('visible');
      setTimeout(function () { backdrop.style.display = ''; }, 220);
    }
    unlockScroll();
  }

  if (openBtn)  openBtn.addEventListener('click', open);
  if (closeBtn) closeBtn.addEventListener('click', close);
  if (backdrop) backdrop.addEventListener('click', close);

  window.addEventListener('resize', function () {
    if (window.innerWidth > 768) close();
  });

  sidebar.querySelectorAll('.nav-link').forEach(function (link) {
    link.addEventListener('click', function () {
      if (window.innerWidth <= 768) close();
    });
  });
})();


// ─────────────────────────────────────────────────────────────────────────────
// Drug formset rows
// ─────────────────────────────────────────────────────────────────────────────

(function () {
  var addBtn     = document.getElementById('add-drug-row');
  var container  = document.getElementById('drug-rows');
  var emptyRow   = document.getElementById('empty-drug-row');
  var totalInput = document.querySelector('[name="items-TOTAL_FORMS"]');
  if (!addBtn || !container || !emptyRow || !totalInput) return;

  var total = parseInt(totalInput.value, 10);

  function wireRemoveBtn(row) {
    var btn = row.querySelector('.remove-drug-row');
    if (btn) btn.addEventListener('click', function () { row.remove(); });
  }

  addBtn.addEventListener('click', function () {
    var newRow = emptyRow.cloneNode(true);
    newRow.removeAttribute('id');
    newRow.style.display = '';
    newRow.classList.remove('drug-row-template');
    newRow.innerHTML = newRow.innerHTML.replace(/__prefix__/g, total);

    var label = newRow.querySelector('.row-num-label');
    if (label) label.textContent = total + 1;

    wireRemoveBtn(newRow);
    container.appendChild(newRow);
    totalInput.value = ++total;
    newRow.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
  });

  container.querySelectorAll('.remove-drug-row').forEach(function (btn) {
    btn.addEventListener('click', function () { btn.closest('.drug-row').remove(); });
  });
})();


// ─────────────────────────────────────────────────────────────────────────────
// Auto-dismiss alerts
// ─────────────────────────────────────────────────────────────────────────────

(function () {
  setTimeout(function () {
    document.querySelectorAll('.alert').forEach(function (el) {
      el.style.transition = 'opacity .4s, transform .4s';
      el.style.opacity    = '0';
      el.style.transform  = 'translateY(-6px)';
      setTimeout(function () { el.remove(); }, 420);
    });
  }, 5000);
})();


// ─────────────────────────────────────────────────────────────────────────────
// AJAX navigation
// ─────────────────────────────────────────────────────────────────────────────

(function () {
  var contentEl  = document.querySelector('.main-content');
  var titleEl    = document.querySelector('.topbar-title');
  var actionsEl  = document.querySelector('.topbar-actions');
  if (!contentEl) return;

  var busy = false;

  // Progress bar
  var bar = document.createElement('div');
  bar.style.cssText = [
    'position:fixed;top:0;left:0;height:3px;width:0',
    'background:var(--blue-600,#2563eb);z-index:9999',
    'opacity:0;pointer-events:none',
    'transition:width .25s ease,opacity .3s ease',
  ].join(';');
  document.body.appendChild(bar);

  function barStart() {
    bar.style.transition = 'width .25s ease';
    bar.style.opacity    = '1';
    bar.style.width      = '45%';
  }
  function barDone() {
    bar.style.transition = 'width .15s ease';
    bar.style.width      = '100%';
    setTimeout(function () {
      bar.style.opacity = '0';
      setTimeout(function () { bar.style.transition = 'none'; bar.style.width = '0'; }, 300);
    }, 150);
  }

  function syncTabs(url) {
    document.querySelectorAll('.bottom-tab, .nav-item').forEach(function (el) {
      var link = el.tagName === 'A' ? el : el.querySelector('a');
      if (!link) return;
      el.classList.toggle('active', link.href.split('?')[0] === url.split('?')[0]);
    });
  }

  function applyPage(data, url, push) {
    // data = compact JSON from AjaxNavMiddleware
    contentEl.innerHTML = data.main || '';
    if (data.bc) document.body.className = data.bc;
    if (titleEl   && data.navT) titleEl.innerHTML  = data.navT;
    if (actionsEl && data.navA) actionsEl.innerHTML = data.navA;

    var pageTitle = (data.title || 'MediScript') + ' — MediScript';
    document.title = pageTitle;
    if (push !== false) history.pushState({ url: url }, pageTitle, url);

    syncTabs(url);
    window.scrollTo(0, 0);

    // Swap flash messages
    var curMsgs = document.querySelector('.messages-container');
    if (data.msgs) {
      if (curMsgs) curMsgs.outerHTML = data.msgs;
      else         contentEl.insertAdjacentHTML('beforebegin', data.msgs);
    } else if (curMsgs) {
      curMsgs.remove();
    }

    barDone();
    contentEl.style.opacity = '1';
    busy = false;
  }

  function navigate(url, push) {
    if (busy || url === location.href) return;
    busy = true;
    barStart();
    contentEl.style.cssText += ';opacity:.4;transition:opacity .1s';

    fetch(url, { headers: { 'X-Ajax-Nav': '1' }, credentials: 'same-origin' })
      .then(function (res) {
        if (!res.ok) throw new Error(res.status);
        var ct = res.headers.get('Content-Type') || '';
        // Server returns compact JSON — much smaller than full HTML
        return ct.includes('application/json') ? res.json() : res.text();
      })
      .then(function (data) {
        if (typeof data === 'string') {
          // Fallback: server returned full HTML (no middleware)
          var doc = new DOMParser().parseFromString(data, 'text/html');
          var nm  = doc.querySelector('.main-content');
          if (!nm) { location.href = url; return; }
          applyPage({
            main:  nm.innerHTML,
            bc:    doc.body.className,
            title: doc.title.replace(' — MediScript', ''),
            navT:  (doc.querySelector('.topbar-title')  || {}).innerHTML || '',
            navA:  (doc.querySelector('.topbar-actions') || {}).innerHTML || '',
            msgs:  (doc.querySelector('.messages-container') || {}).outerHTML || '',
          }, url, push);
        } else {
          applyPage(data, url, push);
        }
      })
      .catch(function () { location.href = url; busy = false; });
  }

  document.querySelectorAll('.bottom-tab, .nav-link').forEach(function (el) {
    el.addEventListener('click', function (e) {
      e.preventDefault();
      navigate(el.href);
    });
  });

  window.addEventListener('popstate', function () { navigate(location.href, false); });
})();


// ─────────────────────────────────────────────────────────────────────────────
// Link prefetch on hover / touchstart
// ─────────────────────────────────────────────────────────────────────────────

(function () {
  var prefetched = new Set();

  function prefetch(url) {
    if (!url || prefetched.has(url)) return;
    try {
      if (new URL(url).origin !== location.origin) return;
    } catch (_) { return; }
    prefetched.add(url);
    var link = document.createElement('link');
    link.rel  = 'prefetch';
    link.href = url;
    document.head.appendChild(link);
  }

  function onPointer(e) {
    var a = e.target.closest('a[href]');
    if (!a) return;
    var href = a.getAttribute('href');
    if (!href || href === '#' || href.startsWith('javascript')) return;
    prefetch(a.href);
  }

  document.addEventListener('touchstart', onPointer, { passive: true });
  document.addEventListener('mouseover',  onPointer, { passive: true });
})();


// ─────────────────────────────────────────────────────────────────────────────
// Swipe navigation  (right = back, left = forward)
// ─────────────────────────────────────────────────────────────────────────────

(function () {
  var THRESHOLD = 50;
  var MAX_VERT  = 60;
  var MAX_MS    = 500;

  var startX, startY, startTime;
  var active = false;

  function makeHint(side) {
    var el = document.createElement('div');
    el.className = 'swipe-nav-hint swipe-nav-hint--' + side;
    el.innerHTML = side === 'left'
      ? '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="15 18 9 12 15 6"/></svg>'
      : '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="9 18 15 12 9 6"/></svg>';
    document.body.appendChild(el);
    return el;
  }

  var hintBack = makeHint('left');
  var hintFwd  = makeHint('right');

  function setHint(show) {
    hintBack.classList.toggle('swipe-nav-hint--visible', show === 'back');
    hintFwd.classList.toggle('swipe-nav-hint--visible',  show === 'fwd');
  }

  function reset() {
    active = false;
    startX = startY = startTime = null;
    setHint(null);
  }

  document.addEventListener('touchstart', function (e) {
    if (e.touches.length !== 1) return;
    startX    = e.touches[0].clientX;
    startY    = e.touches[0].clientY;
    startTime = Date.now();
    active    = true;
  }, { passive: true });

  document.addEventListener('touchmove', function (e) {
    if (!active) return;
    var dx = e.touches[0].clientX - startX;
    var dy = e.touches[0].clientY - startY;
    if (Math.abs(dy) > MAX_VERT) { reset(); return; }
    if      (dx >  30) setHint('back');
    else if (dx < -30) setHint('fwd');
    else               setHint(null);
  }, { passive: true });

  document.addEventListener('touchend', function (e) {
    if (!active) return;
    var dx = e.changedTouches[0].clientX - startX;
    var dy = e.changedTouches[0].clientY - startY;
    var dt = Date.now() - startTime;
    reset();
    if (Math.abs(dx) < THRESHOLD || Math.abs(dy) > MAX_VERT || dt > MAX_MS) return;
    if (dx > 0) history.back();
    else        history.forward();
  }, { passive: true });

  document.addEventListener('touchcancel', reset, { passive: true });
})();


// ─────────────────────────────────────────────────────────────────────────────
// Telegram send modal
// ─────────────────────────────────────────────────────────────────────────────

(function () {
  var modal = initOverlay('tgModal', 'tgPickerBtn', 'tgModalClose');
  if (!modal) return;

  var usernameInput  = document.getElementById('tgUsernameInput');
  var recipientInput = document.getElementById('tgRecipientInput');
  var sendBtn        = document.getElementById('tgSendBtn');
  var contacts       = modal.overlay.querySelectorAll('.tg-contact-item');

  function setRecipient(value) {
    recipientInput.value = value;
    sendBtn.disabled     = !value;
  }

  function filterContacts(query) {
    var q = query.toLowerCase().replace(/^@/, '');
    contacts.forEach(function (btn) {
      var name  = (btn.getAttribute('data-name')     || '').toLowerCase();
      var uname = (btn.getAttribute('data-username') || '').toLowerCase();
      btn.style.display = (!q || name.includes(q) || uname.includes(q)) ? '' : 'none';
    });
  }

  if (usernameInput) {
    usernameInput.addEventListener('input', function () {
      var val = usernameInput.value.trim().replace(/^@/, '');
      contacts.forEach(function (b) { b.classList.remove('selected'); });
      filterContacts(val);
      setRecipient(val);
    });
  }

  contacts.forEach(function (btn) {
    btn.addEventListener('click', function () {
      contacts.forEach(function (b) { b.classList.remove('selected'); });
      btn.classList.add('selected');
      var uname = btn.getAttribute('data-username') || '';
      if (usernameInput) usernameInput.value = uname;
      setRecipient(uname);
      filterContacts(uname);
    });
  });
})();


// ─────────────────────────────────────────────────────────────────────────────
// Share bottom sheet
// ─────────────────────────────────────────────────────────────────────────────

(function () {
  var modal = initOverlay('shareOverlay', 'shareBtn', 'shareClose');
  if (!modal) return;

  var copyBtn = document.getElementById('shareCopyBtn');
  var badge   = document.getElementById('copiedBadge');

  function showCopied() {
    if (!badge) return;
    badge.classList.add('show');
    setTimeout(function () { badge.classList.remove('show'); }, 2000);
  }

  function copyToClipboard(text) {
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(text).then(showCopied);
      return;
    }
    // Fallback for older WebViews
    var ta = document.createElement('textarea');
    ta.value = text;
    ta.style.cssText = 'position:fixed;opacity:0';
    document.body.appendChild(ta);
    ta.focus();
    ta.select();
    try { document.execCommand('copy'); showCopied(); } catch (_) {}
    document.body.removeChild(ta);
  }

  if (copyBtn) {
    copyBtn.addEventListener('click', function () {
      copyToClipboard(copyBtn.getAttribute('data-url'));
    });
  }
})();


// ─────────────────────────────────────────────────────────────────────────────
// PDF download — open in external browser when inside Telegram WebApp
// ─────────────────────────────────────────────────────────────────────────────

(function () {
  function init() {
    var tg = window.Telegram && window.Telegram.WebApp;
    if (!tg || !tg.initData) return;  // not inside a Telegram WebApp

    document.querySelectorAll('a.js-pdf-dl').forEach(function (link) {
      link.addEventListener('click', function (e) {
        e.preventDefault();
        tg.openLink(link.href, { try_instant_view: false });
      });
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
