(function () {
    'use strict';

    const header = document.getElementById('siteHeader');
    if (!header) return;


    let lastScrollY = window.scrollY;
    let ticking = false;
    const HIDE_AFTER = 120;

    function handleScroll() {
        const currentScrollY = window.scrollY;

        header.classList.toggle('header--scrolled', currentScrollY > 10);

        const scrollingDown = currentScrollY > lastScrollY;
        const pastThreshold = currentScrollY > HIDE_AFTER;

        if (scrollingDown && pastThreshold) {
            header.classList.add('header--hidden');
            closeProfileMenu();     // fecha dropdowns abertos ao esconder o header
            closeMobilePanel();
        } else {
            header.classList.remove('header--hidden');
        }

        lastScrollY = currentScrollY;
        ticking = false;
    }

    window.addEventListener('scroll', function () {
        if (!ticking) {
            window.requestAnimationFrame(handleScroll);
            ticking = true;
        }
    }, { passive: true });

    const navToggle = document.getElementById('navToggle');
    const mobilePanel = document.getElementById('mobilePanel');

    function closeMobilePanel() {
        if (!navToggle || !mobilePanel) return;
        navToggle.classList.remove('is-open');
        mobilePanel.classList.remove('is-open');
        navToggle.setAttribute('aria-expanded', 'false');
    }

    if (navToggle && mobilePanel) {
        navToggle.addEventListener('click', function () {
            const isOpen = mobilePanel.classList.toggle('is-open');
            navToggle.classList.toggle('is-open', isOpen);
            navToggle.setAttribute('aria-expanded', String(isOpen));
        });
    }


    const searchIconBtn = document.getElementById('searchIconBtn');
    const mobileSearchInput = document.getElementById('mobileSearchInput');

    if (searchIconBtn && mobilePanel && mobileSearchInput) {
        searchIconBtn.addEventListener('click', function () {
            const isOpen = mobilePanel.classList.contains('is-open');
            if (!isOpen) {
                mobilePanel.classList.add('is-open');
                navToggle.classList.add('is-open');
            }

            window.setTimeout(function () { mobileSearchInput.focus(); }, 150);
        });
    }


    const profileMenu = document.getElementById('profileMenu');
    const avatarBtn = document.getElementById('avatarBtn');

    function closeProfileMenu() {
        if (profileMenu) profileMenu.classList.remove('is-open');
        if (avatarBtn) avatarBtn.setAttribute('aria-expanded', 'false');
    }

    if (profileMenu && avatarBtn) {
        avatarBtn.addEventListener('click', function (event) {
            event.stopPropagation();
            const isOpen = profileMenu.classList.toggle('is-open');
            avatarBtn.setAttribute('aria-expanded', String(isOpen));
        });

        document.addEventListener('click', function (event) {
            if (!profileMenu.contains(event.target)) closeProfileMenu();
        });

        document.addEventListener('keydown', function (event) {
            if (event.key === 'Escape') closeProfileMenu();
        });
    }

    const YourSpaceAuth = {
        get state() {
            return document.body.dataset.auth === 'user' ? 'user' : 'guest';
        },
        set(state) {
            document.body.dataset.auth = state === 'user' ? 'user' : 'guest';
        },
        toggle() {
            this.set(this.state === 'user' ? 'guest' : 'user');
        }
    };

    window.YourSpaceAuth = YourSpaceAuth;

    document.querySelectorAll('[data-demo-auth-toggle]').forEach(function (btn) {
        btn.addEventListener('click', function () {
            YourSpaceAuth.toggle();
        });
    });

})();