// ── Scroll progress bar
const bar = document.getElementById('progress-bar');
window.addEventListener('scroll', () => {
  const pct = (window.scrollY / (document.body.scrollHeight - window.innerHeight)) * 100;
  bar.style.width = pct + '%';
  document.getElementById('navbar').classList.toggle('scrolled', window.scrollY > 60);
});

// ── Mobile nav
const hamburger = document.getElementById('hamburger');
const mobileNav = document.getElementById('mobileNav');
const mobileClose = document.getElementById('mobileClose');
hamburger.addEventListener('click', () => mobileNav.classList.add('open'));
mobileClose.addEventListener('click', () => mobileNav.classList.remove('open'));
document.querySelectorAll('.mobile-link').forEach(l => l.addEventListener('click', () => mobileNav.classList.remove('open')));

// ── Scroll reveal
const ro = new IntersectionObserver((entries) => {
  entries.forEach((e, i) => {
    if (e.isIntersecting) {
      setTimeout(() => e.target.classList.add('visible'), i * 80);
      ro.unobserve(e.target);
    }
  });
}, { threshold: 0.10 });
document.querySelectorAll('.reveal,.reveal-left,.reveal-right').forEach(el => ro.observe(el));

// ── Animated counter
function animateCounter(el) {
  const target = parseInt(el.dataset.count);
  const sfx = el.dataset.sfx || '';
  const K = target === 10000;
  let curr = 0;
  const step = Math.ceil(target / 70);
  const t = setInterval(() => {
    curr = Math.min(curr + step, target);
    el.textContent = K ? Math.round(curr / 1000) + 'K+' : curr + sfx;
    if (curr >= target) clearInterval(t);
  }, 25);
}
const co = new IntersectionObserver((entries) => {
  entries.forEach(e => {
    if (e.isIntersecting) { animateCounter(e.target); co.unobserve(e.target); }
  });
}, { threshold: 0.5 });
document.querySelectorAll('.hsc-num').forEach(el => co.observe(el));

// ── Testimonials
const vCards = document.querySelectorAll('.vt-video-card');
const quoteCard = document.getElementById('activeQuote');
const quoteText = document.getElementById('quoteText');
const quoteName = document.getElementById('quoteName');
const quoteCond = document.getElementById('quoteCond');
const modal = document.getElementById('vid-modal');
const iframe = document.getElementById('modal-iframe');



// Card hover
vCards.forEach(card => {
  // Show quote on hover
  card.addEventListener('mouseenter', () => {
    quoteText.textContent = '"' + card.dataset.quote + '"';
    quoteName.textContent = card.dataset.name;
    quoteCond.textContent = card.dataset.cond;
    quoteCard.style.display = 'block';
    // Trigger reflow for animation
    void quoteCard.offsetWidth; 
    quoteCard.classList.add('visible');
  });

  // Open modal on click
  card.addEventListener('click', () => {
iframe.src =
`https://www.youtube.com/embed/${card.dataset.video}`;
    modal.style.display = 'flex';
  });
});

// Close modal
document.getElementById('close-modal').addEventListener('click', () => {
  modal.style.display = 'none';
  iframe.src = '';
});
modal.addEventListener('click', (e) => {
  if(e.target === modal) {
    modal.style.display = 'none';
    iframe.src = '';
  }
});

// ── FAQ accordion
document.querySelectorAll('.faq-item').forEach(item => {
  item.querySelector('.faq-q').addEventListener('click', () => {
    const isOpen = item.classList.contains('open');
    document.querySelectorAll('.faq-item').forEach(i => i.classList.remove('open'));
    if (!isOpen) item.classList.add('open');
  });
});

// ── Form submit
function handleSubmit(e) {
  e.preventDefault();
  const btn = document.getElementById('form-submit');
  btn.textContent = 'Submitting...';
  btn.disabled = true;
  setTimeout(() => {
    document.getElementById('consultationForm').style.display = 'none';
    document.getElementById('form-success').style.display = 'block';
  }, 1200);
}

// ── Smooth scroll
document.querySelectorAll('a[href^="#"]').forEach(a => {
  a.addEventListener('click', e => {
    const t = document.querySelector(a.getAttribute('href'));
    if (t) { e.preventDefault(); window.scrollTo({ top: t.getBoundingClientRect().top + window.scrollY - 96, behavior: 'smooth' }); }
  });
});
// ── Carousel Controls
const vtGrid = document.getElementById('vtGrid');
const vtPrev = document.getElementById('vtPrev');
const vtNext = document.getElementById('vtNext');
if(vtPrev && vtNext && vtGrid) {
  vtPrev.addEventListener('click', () => { vtGrid.scrollBy({ left: -window.innerWidth * 0.3, behavior: 'smooth' }); });
  vtNext.addEventListener('click', () => { vtGrid.scrollBy({ left: window.innerWidth * 0.3, behavior: 'smooth' }); });
}
