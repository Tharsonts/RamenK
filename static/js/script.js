// RamenK Digital Menu JavaScript

// Mobile sidebar toggle
function toggleSidebar() {
    const sidebar = document.getElementById('sidebar');
    sidebar.classList.toggle('open');
}

// Optimized scroll to section with reduced animation time for better performance
function scrollToSection(sectionId) {
    const element = document.getElementById(sectionId);
    if (element) {
        // Use native smooth scrolling for better performance
        element.scrollIntoView({ 
            behavior: 'smooth', 
            block: 'start',
            inline: 'nearest'
        });
        
        // Update active navigation
        updateActiveNavigation(sectionId);
    }
    
    // Close mobile sidebar after navigation
    if (window.innerWidth <= 768) {
        const sidebar = document.getElementById('sidebar');
        sidebar.classList.remove('open');
    }
}

// Cache for performance optimization
const sectionCache = new Map();
const observerOptions = {
    root: null,
    rootMargin: '-20% 0px -20% 0px',
    threshold: 0.1
};

// Optimized active navigation update function
function updateActiveNavigation(activeId) {
    // Use cached elements for better performance
    if (!sectionCache.has('navLinks')) {
        sectionCache.set('navLinks', document.querySelectorAll('.sidebar-menu-link'));
    }
    
    const navLinks = sectionCache.get('navLinks');
    navLinks.forEach(link => {
        link.classList.remove('active');
        if (link.getAttribute('href') === `#${activeId}`) {
            link.classList.add('active');
            // Ensure active item is visible in sidebar
            const sidebarNav = link.closest('.sidebar-navigation');
            if (sidebarNav) {
                const linkRect = link.getBoundingClientRect();
                const navRect = sidebarNav.getBoundingClientRect();
                
                if (linkRect.bottom > navRect.bottom || linkRect.top < navRect.top) {
                    link.scrollIntoView({ 
                        behavior: 'smooth', 
                        block: 'center'
                    });
                }
            }
        }
    });
}

document.addEventListener('DOMContentLoaded', function() {
    
    // Performance optimization: Cache DOM elements
    const sidebar = document.getElementById('sidebar');
    const mobileToggle = document.querySelector('.mobile-toggle');
    const menuSections = document.querySelectorAll('.menu-section');
    
    // Initialize Intersection Observer for better performance
    const sectionObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                updateActiveNavigation(entry.target.id);
            }
        });
    }, observerOptions);
    
    // Observe all sections
    menuSections.forEach(section => {
        sectionObserver.observe(section);
    });
    
    // Optimize mobile sidebar toggle with event delegation
    if (mobileToggle) {
        mobileToggle.addEventListener('click', function(e) {
            e.preventDefault();
            sidebar.classList.toggle('open');
        });
    }
    
    // Close sidebar when clicking outside on mobile
    document.addEventListener('click', function(e) {
        if (window.innerWidth <= 768 && 
            sidebar.classList.contains('open') && 
            !sidebar.contains(e.target) && 
            !mobileToggle.contains(e.target)) {
            sidebar.classList.remove('open');
        }
    });
    
    // Optimize scroll performance with throttling
    let scrollTimeout;
    window.addEventListener('scroll', function() {
        if (scrollTimeout) {
            clearTimeout(scrollTimeout);
        }
        scrollTimeout = setTimeout(handleScroll, 16); // ~60fps
    }, { passive: true });
    
    if (mobileNavBtn) {
        mobileNavBtn.addEventListener('click', function() {
            mobileNav.classList.add('active');
            document.body.style.overflow = 'hidden';
        });
    }
    
    if (closeMobileNav) {
        closeMobileNav.addEventListener('click', function() {
            mobileNav.classList.remove('active');
            document.body.style.overflow = '';
        });
    }
    
    // Close mobile nav when clicking outside
    if (mobileNav) {
        mobileNav.addEventListener('click', function(e) {
            if (e.target === mobileNav) {
                mobileNav.classList.remove('active');
                document.body.style.overflow = '';
            }
        });
    }
    
    // Close mobile nav when clicking on a link
    const mobileNavLinks = document.querySelectorAll('.mobile-nav-link');
    mobileNavLinks.forEach(link => {
        link.addEventListener('click', function() {
            mobileNav.classList.remove('active');
            document.body.style.overflow = '';
        });
    });
    
    // Smooth scrolling for navigation links
    const navLinks = document.querySelectorAll('.nav-link, .mobile-nav-link, .nav-category-title');
    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const targetId = this.getAttribute('href').substring(1);
            let targetElement = document.getElementById(targetId);
            
            // If element not found, try to find the parent category
            if (!targetElement) {
                const categoryMappings = {
                    'porcoes': 'porcoes-acompanhamentos',
                    'acompanhamentos': 'porcoes-acompanhamentos', 
                    'toppings': 'porcoes-acompanhamentos',
                    'sushis': 'sushi-bar',
                    'temakis': 'sushi-bar',
                    'sashimis': 'sushi-bar',
                    'hossomakis': 'sushi-bar',
                    'uramakis': 'sushi-bar',
                    'combinados': 'sushi-bar',
                    'domburis-sushi': 'sushi-bar',
                    'bebidas': 'bebidas-drinks',
                    'cervejas': 'bebidas-drinks',
                    'caipirinhas': 'bebidas-drinks',
                    'doses-garrafas': 'bebidas-drinks',
                    'coqueteis-drinks': 'bebidas-drinks',
                    'sobremesas': 'sobremesas-especiais',
                    'delicias-obatchian': 'sobremesas-especiais',
                    'espetinhos': 'sobremesas-especiais'
                };
                
                // Try to find the specific section first
                targetElement = document.getElementById(targetId);
                
                // If still not found, look for category
                if (!targetElement && categoryMappings[targetId]) {
                    targetElement = document.getElementById(categoryMappings[targetId]);
                }
            }
            
            if (targetElement) {
                const headerOffset = 120;
                const elementPosition = targetElement.offsetTop;
                const offsetPosition = elementPosition - headerOffset;
                
                window.scrollTo({
                    top: offsetPosition,
                    behavior: 'smooth'
                });
                
                // Close mobile nav if open
                if (mobileNav && mobileNav.classList.contains('active')) {
                    mobileNav.classList.remove('active');
                    document.body.style.overflow = '';
                }
                
                // Add active class to clicked link
                navLinks.forEach(l => l.classList.remove('active'));
                this.classList.add('active');
            } else {
                console.log('Element not found even with fallback:', targetId);
                // Fallback: scroll to first category if nothing found
                const firstCategory = document.querySelector('.menu-category');
                if (firstCategory) {
                    firstCategory.scrollIntoView({ behavior: 'smooth' });
                }
            }
        });
    });
    
    // Active navigation highlighting
    function updateActiveNavigation() {
        const sections = document.querySelectorAll('.menu-section, .menu-category');
        const navLinks = document.querySelectorAll('.nav-link, .nav-category-title');
        
        let current = '';
        const scrollY = window.pageYOffset;
        
        sections.forEach(section => {
            const sectionTop = section.offsetTop - 150;
            const sectionHeight = section.clientHeight;
            
            if (scrollY >= sectionTop && scrollY < sectionTop + sectionHeight) {
                current = section.getAttribute('id');
            }
        });
        
        navLinks.forEach(link => {
            link.classList.remove('active');
            if (link.getAttribute('href') === `#${current}`) {
                link.classList.add('active');
            }
        });
    }
    
    // Throttled scroll event listener
    let ticking = false;
    function handleScroll() {
        if (!ticking) {
            requestAnimationFrame(function() {
                updateActiveNavigation();
                ticking = false;
            });
            ticking = true;
        }
    }
    
    window.addEventListener('scroll', handleScroll);
    
    // Intersection Observer for section animations
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const sectionObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    }, observerOptions);
    
    // Observe all menu sections
    const menuSections = document.querySelectorAll('.menu-section');
    menuSections.forEach(section => {
        sectionObserver.observe(section);
    });
    
    // Menu item card hover effect enhancement
    const menuCards = document.querySelectorAll('.menu-item-card');
    menuCards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-8px) scale(1.02)';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0) scale(1)';
        });
    });
    
    // Keyboard navigation support
    document.addEventListener('keydown', function(e) {
        // Close mobile nav with Escape key
        if (e.key === 'Escape' && mobileNav.classList.contains('active')) {
            mobileNav.classList.remove('active');
            document.body.style.overflow = '';
        }
        
        // Navigation with arrow keys
        if (e.key === 'ArrowUp' || e.key === 'ArrowDown') {
            const activeLink = document.querySelector('.nav-link.active');
            if (activeLink) {
                const allLinks = Array.from(document.querySelectorAll('.nav-link'));
                const currentIndex = allLinks.indexOf(activeLink);
                
                let nextIndex;
                if (e.key === 'ArrowUp') {
                    nextIndex = currentIndex > 0 ? currentIndex - 1 : allLinks.length - 1;
                } else {
                    nextIndex = currentIndex < allLinks.length - 1 ? currentIndex + 1 : 0;
                }
                
                allLinks[nextIndex].click();
                e.preventDefault();
            }
        }
    });
    
    // Performance optimization: Lazy load background pattern
    function loadBackgroundPattern() {
        const pattern = document.querySelector('.background-pattern');
        if (pattern) {
            // Add a slight delay to ensure page is loaded
            setTimeout(() => {
                pattern.style.opacity = '0.03';
            }, 500);
        }
    }
    
    // Call after page load
    if (document.readyState === 'complete') {
        loadBackgroundPattern();
    } else {
        window.addEventListener('load', loadBackgroundPattern);
    }
    
    // Add subtle parallax effect to header
    function parallaxEffect() {
        const header = document.querySelector('.header-section');
        const scrolled = window.pageYOffset;
        const rate = scrolled * -0.5;
        
        if (header && scrolled < header.offsetHeight) {
            header.style.transform = `translate3d(0, ${rate}px, 0)`;
        }
    }
    
    // Throttled parallax scroll
    let parallaxTicking = false;
    function handleParallaxScroll() {
        if (!parallaxTicking) {
            requestAnimationFrame(function() {
                parallaxEffect();
                parallaxTicking = false;
            });
            parallaxTicking = true;
        }
    }
    
    window.addEventListener('scroll', handleParallaxScroll);
    
    // Close sidebar when clicking outside
    document.addEventListener('click', function(event) {
        const sidebar = document.getElementById('sidebar');
        const toggle = document.querySelector('.sidebar-toggle');
        
        if (window.innerWidth <= 768 && 
            sidebar && toggle &&
            !sidebar.contains(event.target) && 
            !toggle.contains(event.target)) {
            sidebar.classList.remove('open');
        }
    });

    // Update active navigation on scroll
    function updateActiveNavigation() {
        const sections = document.querySelectorAll('.menu-section');
        const navLinks = document.querySelectorAll('.sidebar-menu-link');
        
        let current = '';
        sections.forEach((section) => {
            const sectionTop = section.getBoundingClientRect().top;
            if (sectionTop <= 200) {
                current = section.getAttribute('id');
            }
        });

        navLinks.forEach((link) => {
            link.classList.remove('active');
            if (link.getAttribute('href') === '#' + current) {
                link.classList.add('active');
            }
        });
    }

    // Throttled scroll event for active navigation
    let scrollTimeout;
    window.addEventListener('scroll', function() {
        if (scrollTimeout) {
            clearTimeout(scrollTimeout);
        }
        scrollTimeout = setTimeout(updateActiveNavigation, 100);
    });

    // Initialize active navigation on page load
    updateActiveNavigation();
    
    // Add loading animation completion
    setTimeout(() => {
        document.body.classList.add('loaded');
    }, 100);
    
    console.log('RamenK Modern Japanese Menu loaded successfully!');
});

// Service Worker registration for offline functionality (optional)
if ('serviceWorker' in navigator) {
    window.addEventListener('load', function() {
        // Only register if service worker file exists
        fetch('/sw.js', { method: 'HEAD' })
            .then(() => {
                navigator.serviceWorker.register('/sw.js')
                    .then(registration => {
                        console.log('SW registered: ', registration);
                    })
                    .catch(registrationError => {
                        console.log('SW registration failed: ', registrationError);
                    });
            })
            .catch(() => {
                // Service worker file doesn't exist, skip registration
                console.log('Service worker not available');
            });
    });
}

// Utility function for touch devices
function isTouchDevice() {
    return (('ontouchstart' in window) ||
            (navigator.maxTouchPoints > 0) ||
            (navigator.msMaxTouchPoints > 0));
}

// Enhance touch interactions
if (isTouchDevice()) {
    document.body.classList.add('touch-device');
    
    // Add touch feedback to cards
    menuCards.forEach(card => {
        card.addEventListener('touchstart', function() {
            this.classList.add('touch-active');
        });
        
        card.addEventListener('touchend', function() {
            setTimeout(() => {
                this.classList.remove('touch-active');
            }, 150);
        });
    });
}
