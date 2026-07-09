// Vanilla-JS replacement for what used to be React state: dark/light theme,
// sticky navbar shrink-on-scroll, mobile menu, and FAQ accordions.
//
// There's no client-side user/client mode toggle anymore — mode is decided
// server-side by URL (/ vs /client/, see core.context_processors.site_content)
// and rendered into the page as <html data-mode="user|client">. This file
// just reads that attribute to pick the right accent colors; it never
// changes the mode itself.

const ACCENTS = {
  user: {
    dark: { border: "rgba(16,185,129,0.4)", bg: "rgba(16,185,129,0.1)", navBg: "rgba(13,157,110,0.1)", text: "#34d399", texture: "#10b981" },
    light: { border: "#6ee7b7", bg: "rgba(16,185,129,0.1)", navBg: "rgba(13,157,110,0.1)", text: "#059669", texture: "#059669" },
  },
  client: {
    dark: { border: "rgba(244,63,94,0.4)", bg: "rgba(244,63,94,0.1)", navBg: "rgba(207,54,80,0.1)", text: "#fb7185", texture: "#f43f5e" },
    light: { border: "#fda4af", bg: "rgba(244,63,94,0.1)", navBg: "rgba(207,54,80,0.1)", text: "#e11d48", texture: "#e11d48" },
  },
};

function getTheme() {
  return localStorage.getItem("taxon-theme") || "light";
}

function getMode() {
  return document.documentElement.getAttribute("data-mode") || "user";
}

function applyTheme(theme) {
  document.documentElement.classList.toggle("dark", theme === "dark");
  localStorage.setItem("taxon-theme", theme);
  document.querySelectorAll("[data-theme-icon]").forEach((el) => {
    el.setAttribute("data-lucide", theme === "dark" ? "sun" : "moon");
  });
  if (window.lucide) lucide.createIcons();
}

function applyAccentColors() {
  const mode = getMode();
  const theme = getTheme() === "dark" ? "dark" : "light";
  const c = ACCENTS[mode][theme];
  document.documentElement.style.setProperty("--accent-border", c.border);
  document.documentElement.style.setProperty("--accent-bg", c.bg);
  document.documentElement.style.setProperty("--accent-nav-bg", c.navBg);
  document.documentElement.style.setProperty("--accent-text", c.text);
  document.documentElement.style.setProperty("--accent-texture", c.texture);
}

function initNavScroll() {
  const nav = document.getElementById("site-nav");
  if (!nav) return;
  const onScroll = () => nav.classList.toggle("nav-scrolled", window.scrollY > 24);
  onScroll();
  window.addEventListener("scroll", onScroll, { passive: true });
}

function initMobileMenu() {
  const btn = document.getElementById("mobile-menu-btn");
  const menu = document.getElementById("mobile-menu");
  if (!btn || !menu) return;
  btn.addEventListener("click", () => menu.classList.toggle("hidden"));
}

function initAccountMenu() {
  const btn = document.getElementById("account-menu-btn");
  const menu = document.getElementById("account-menu");
  if (!btn || !menu) return;
  btn.addEventListener("click", (e) => {
    e.stopPropagation();
    menu.classList.toggle("hidden");
  });
  document.addEventListener("click", () => menu.classList.add("hidden"));
  menu.addEventListener("click", (e) => e.stopPropagation());
}

function initFaqAccordion() {
  document.querySelectorAll("[data-faq-item]").forEach((item) => {
    const btn = item.querySelector("[data-faq-toggle]");
    const panel = item.querySelector("[data-faq-panel]");
    const icon = item.querySelector("[data-faq-icon]");
    if (!btn || !panel) return;
    btn.addEventListener("click", () => {
      const isOpen = !panel.classList.contains("hidden");
      panel.classList.toggle("hidden", isOpen);
      if (icon) icon.style.transform = isOpen ? "rotate(0deg)" : "rotate(180deg)";
    });
  });
}

// ---------------------------------------------------------------------
// Contact Sales / Contact Support forms (core/home.html): on a successful
// submit, play an origami "sent like a paper plane" animation instead of
// a full page reload — flash the panel solid, then a solid-color proxy
// ("paper") the same size/position folds itself through an A4-ratio-derived
// sequence (flat sheet -> crease -> corners folded to a peak -> tapered
// triangle -> folded-in-half stand-in -> right-pointing dart) and flies off
// to the right, while the real form (with real inputs) hides underneath.
// Once it's off-screen, the real form resets and fades back in as a fresh
// translucent panel. See .contact-panel/.contact-flash/.contact-hidden/
// .contact-paper/.contact-entering + the contact-origami keyframes in
// static/css/site.css — those clip-path shapes were plotted and scrubbed
// frame-by-frame before landing here, so don't hand-edit the polygons
// without re-checking they still tween without self-intersecting.
//
// This is progressive enhancement on top of the existing server-rendered
// flow: any failure (validation error, network error, JS disabled) falls
// back to a normal form submission, which Django still handles exactly as
// before (full reload, inline errors, messages banner).
// ---------------------------------------------------------------------

// If the sales form's paper has a real (visible, on-screen) Contact Sales
// nav button to target, aims the flight at it: the transform-origin corner
// of the folded paper (its "nose", see transform-origin: 85% 50% above)
// ends up centered on the button, shrunk down to roughly the button's size.
// The flight is two-legged so it reads as nose-first, not sideways: a mid
// waypoint that's almost pure horizontal travel (the plane's nose sits at
// its rightmost point, so +x *is* "forward"), then a climbing curve into
// the final approach. Returns the CSS custom properties to set on the
// paper, or null to fall back to the keyframes' default off-screen throw.
function computeFlyToButtonVars(form, formRect) {
  if (form.dataset.contactForm !== "sales") return null;
  const button = document.getElementById("contact-sales-nav-btn");
  if (!button) return null;
  const buttonRect = button.getBoundingClientRect();
  // Hidden on mobile (class="hidden sm:inline-flex") collapses to a
  // zero-size rect — treat that as "no target" and fall back.
  if (buttonRect.width === 0 || buttonRect.height === 0) return null;

  const ORIGIN_X = 0.85;
  const ORIGIN_Y = 0.5;
  const noseX = formRect.left + ORIGIN_X * formRect.width;
  const noseY = formRect.top + ORIGIN_Y * formRect.height;
  const dx = buttonRect.left + buttonRect.width / 2 - noseX;
  const dy = buttonRect.top + buttonRect.height / 2 - noseY;

  const scale = Math.max(0.12, Math.min(0.35, buttonRect.width / formRect.width));

  return {
    // Mid waypoint: mostly the nose's own forward (+x) direction, only a
    // hint of climb — straight-line flight before the turn.
    midX: `${dx * 0.55}px`,
    midY: `${dy * 0.08}px`,
    midRot: "-4deg",
    midScale: String(Math.min(0.9, (1 + scale) / 2)),
    // Final approach: the rest of the distance, banking into a climb.
    x: `${dx}px`,
    y: `${dy}px`,
    rot: "-20deg",
    scale: String(scale),
    button,
  };
}

function playSentAnimation(form, message) {
  const panel = form; // the form itself carries accent-border/accent-bg — the "green section"
  const section = form.closest("section");
  if (!section) {
    form.reset();
    return;
  }

  const FLASH_MS = 220;
  const FOLD_MS = 1450;

  // 1. Flash to a solid, full-opacity accent color.
  panel.classList.add("contact-flash");

  let paper = null;
  let flyTarget = null;

  window.setTimeout(() => {
    // 2. Swap in a same-size, same-position solid-color "paper" proxy and
    // hide the real form underneath it — folding real <input> elements
    // would just look broken, so the proxy does the folding instead.
    const formRect = form.getBoundingClientRect();
    const sectionRect = section.getBoundingClientRect();

    paper = document.createElement("div");
    paper.className = "contact-paper";
    paper.style.left = `${formRect.left - sectionRect.left}px`;
    paper.style.top = `${formRect.top - sectionRect.top}px`;
    paper.style.width = `${formRect.width}px`;
    paper.style.height = `${formRect.height}px`;
    section.appendChild(paper);

    // For the sales form, aim the flight at the Contact Sales nav button
    // instead of throwing the plane off-screen (the keyframes' fallback).
    flyTarget = computeFlyToButtonVars(form, formRect);
    if (flyTarget) {
      paper.style.setProperty("--fly-mid-x", flyTarget.midX);
      paper.style.setProperty("--fly-mid-y", flyTarget.midY);
      paper.style.setProperty("--fly-mid-rot", flyTarget.midRot);
      paper.style.setProperty("--fly-mid-scale", flyTarget.midScale);
      paper.style.setProperty("--fly-x", flyTarget.x);
      paper.style.setProperty("--fly-y", flyTarget.y);
      paper.style.setProperty("--fly-rot", flyTarget.rot);
      paper.style.setProperty("--fly-scale", flyTarget.scale);
    }

    panel.classList.remove("contact-flash");
    panel.classList.add("contact-hidden");

    // Next frame, so the browser registers the paper's start state before
    // the animation class kicks the transition off.
    requestAnimationFrame(() => paper.classList.add("contact-flying"));
  }, FLASH_MS);

  window.setTimeout(() => {
    // 3. Paper's flown off (or been absorbed) — clean it up, reset the
    // form, and fade a fresh, translucent panel back in for another
    // submission.
    if (paper) paper.remove();
    form.reset();
    panel.classList.remove("contact-hidden");
    panel.classList.add("contact-entering");

    // The plane just vanished into the nav button — flash its border like
    // it absorbed the impact.
    if (flyTarget) {
      flyTarget.button.classList.remove("nav-absorb-flash");
      // eslint-disable-next-line no-unused-expressions
      void flyTarget.button.offsetWidth; // restart the animation if it's still running
      flyTarget.button.classList.add("nav-absorb-flash");
      window.setTimeout(() => flyTarget.button.classList.remove("nav-absorb-flash"), 600);
    }

    const status = form.querySelector("[data-contact-status]");
    if (status && message) {
      status.textContent = message;
      status.classList.remove("hidden");
      status.classList.remove("opacity-0");
      window.setTimeout(() => status.classList.add("opacity-0"), 2600);
    }

    const submitBtn = form.querySelector('button[type="submit"]');
    if (submitBtn) submitBtn.disabled = false;

    window.setTimeout(() => panel.classList.remove("contact-entering"), 500);
  }, FLASH_MS + FOLD_MS);
}

function initContactForms() {
  document.querySelectorAll("[data-contact-form]").forEach((form) => {
    form.classList.add("contact-panel");
    form.addEventListener("submit", async (e) => {
      e.preventDefault();
      const submitBtn = form.querySelector('button[type="submit"]');
      if (submitBtn) submitBtn.disabled = true;

      let data = null;
      let ok = false;
      try {
        const resp = await fetch(form.getAttribute("action") || window.location.pathname, {
          method: "POST",
          body: new FormData(form),
          headers: { "X-Requested-With": "XMLHttpRequest" },
        });
        try {
          data = await resp.json();
        } catch (_) {
          data = null;
        }
        ok = resp.ok && data && data.ok;
      } catch (_) {
        ok = false;
      }

      if (!ok) {
        // Fall back to a normal submission so Django's usual validation/
        // error rendering takes over. form.submit() doesn't re-fire the
        // "submit" event, so this can't loop back into this handler.
        form.submit();
        return;
      }

      playSentAnimation(form, data.message);
    });
  });
}

document.addEventListener("DOMContentLoaded", () => {
  applyTheme(getTheme());
  applyAccentColors();
  initNavScroll();
  initMobileMenu();
  initAccountMenu();
  initFaqAccordion();
  initContactForms();

  const themeBtn = document.getElementById("theme-toggle-btn");
  if (themeBtn) {
    themeBtn.addEventListener("click", () => {
      applyTheme(getTheme() === "dark" ? "light" : "dark");
      applyAccentColors(); // refresh accent colors for the new theme
    });
  }

  if (window.lucide) lucide.createIcons();
});
