/* ============================================
   TrustDrive — Interactive Animation Engine
   ============================================ */

document.addEventListener('DOMContentLoaded', () => {

    /* ── 1. SCROLL REVEAL (IntersectionObserver) ── */
    const revealObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('active');
            }
        });
    }, { threshold: 0.1, rootMargin: '0px 0px -40px 0px' });

    document.querySelectorAll('.reveal').forEach(el => revealObserver.observe(el));

    /* Stagger children */
    document.querySelectorAll('.stagger-children').forEach(parent => {
        Array.from(parent.children).forEach((child, i) => {
            child.style.transitionDelay = `${i * 0.1}s`;
            child.classList.add('reveal', 'reveal-up');
            revealObserver.observe(child);
        });
    });


    /* ── 2. NAVBAR — Scroll morph ── */
    const navbar = document.querySelector('.navbar');
    if (navbar) {
        window.addEventListener('scroll', () => {
            if (window.scrollY > 50) {
                navbar.classList.add('navbar-scrolled');
            } else {
                navbar.classList.remove('navbar-scrolled');
            }
        }, { passive: true });
    }











    /* ── 6. ANIMATED COUNTER for stat numbers ── */
    function animateCounter(el) {
        const target = parseInt(el.dataset.count);
        const suffix = el.dataset.suffix || '';
        const duration = 1600;
        const step = 16;
        const increment = target / (duration / step);
        let current = 0;
        const timer = setInterval(() => {
            current += increment;
            if (current >= target) {
                current = target;
                clearInterval(timer);
            }
            el.textContent = Math.floor(current).toLocaleString() + suffix;
        }, step);
    }

    const counterObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting && !entry.target.dataset.counted) {
                entry.target.dataset.counted = 'true';
                animateCounter(entry.target);
            }
        });
    }, { threshold: 0.5 });

    document.querySelectorAll('[data-count]').forEach(el => counterObserver.observe(el));


    /* ── 7. IMAGE PARALLAX on scroll (sections with .parallax-img) ── */
    const parallaxImgs = document.querySelectorAll('.parallax-img');
    if (parallaxImgs.length) {
        window.addEventListener('scroll', () => {
            parallaxImgs.forEach(img => {
                const rect = img.getBoundingClientRect();
                const offset = (window.innerHeight / 2 - rect.top - rect.height / 2) * 0.12;
                img.style.transform = `translateY(${offset}px)`;
            });
        }, { passive: true });
    }


    /* ── 8. SMOOTH ACTIVE NAV LINK highlight ── */
    const currentPath = window.location.pathname;
    document.querySelectorAll('.nav-link').forEach(link => {
        if (link.getAttribute('href') === currentPath) {
            link.classList.add('nav-link-active');
        }
    });


    /* ── 9. SERVICE / FEATURE CARD icon bounce on hover ── */
    document.querySelectorAll('.service-card').forEach(card => {
        const icon = card.querySelector('i, .service-icon');
        if (!icon) return;
        card.addEventListener('mouseenter', () => {
            icon.style.animation = 'iconBounce 0.5s ease';
        });
        card.addEventListener('animationend', () => {
            icon.style.animation = '';
        }, { capture: false });
        icon.addEventListener('animationend', () => {
            icon.style.animation = '';
        });
    });








    /* ── 13. SMOOTH ENTRANCE for alert/flash messages ── */
    document.querySelectorAll('.alert').forEach((el, i) => {
        el.style.animationDelay = `${i * 0.1}s`;
        el.classList.add('alert-animate-in');
        setTimeout(() => {
            el.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
            el.style.opacity = '0';
            el.style.transform = 'translateY(-10px)';
            setTimeout(() => el.remove(), 500);
        }, 5000 + i * 100);
    });

});
