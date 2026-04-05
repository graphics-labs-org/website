
        function setLang(lang) {
            const l = lang.toLowerCase();
            localStorage.setItem('gl_lang', l);
            const t = translations[l] || translations['es'];

            // 1. Update elements with data-i18n attribute
            document.querySelectorAll('[data-i18n]').forEach(el => {
                const key = el.getAttribute('data-i18n');
                if (t[key]) {
                    if (el.tagName === 'INPUT' || el.tagName === 'TEXTAREA') {
                        el.placeholder = t[key];
                    } else {
                        el.innerHTML = t[key];
                    }
                }
            });

            // 2. Proactive mapping for IDs (backwards compatibility)
            Object.keys(t).forEach(key => {
                const hKey = key.replace('_', '-');
                const possibleIds = [
                    key, hKey, 
                    'txt-' + key, 'txt-' + hKey, 
                    'lbl-' + key, 'lbl-' + hKey, 
                    'btn-' + key, 'btn-' + hKey,
                    'info-h-' + key, 'info-p-' + key,
                    'link-' + key, 'footer-' + key
                ];
                possibleIds.forEach(id => {
                    const el = document.getElementById(id);
                    if (el) {
                        if (t[key].includes('<')) el.innerHTML = t[key];
                        else el.innerText = t[key];
                    }
                });
            });

            // 3. Update alternate links (Canonical/SEO)
            document.querySelectorAll('link[hreflang]').forEach(link => {
                const targetLang = link.getAttribute('hreflang');
                if (targetLang === 'x-default') return;
                const pathParts = window.location.pathname.split('/');
                const langIndex = pathParts.findIndex(p => ['es','ca','en','fr','de','pt','it','nl','ja'].includes(p));
                if (langIndex !== -1) {
                    pathParts[langIndex] = targetLang;
                    link.href = window.location.origin + pathParts.join('/');
                }
            });

            // 4. Highlight active language buttons
            document.querySelectorAll('.lang-switch button, .lang-btn').forEach(btn => {
                const bId = btn.id.replace('btn-', '');
                btn.classList.toggle('active', bId === l || btn.innerText.toLowerCase() === l);
            });
        }
        window.setLang = setLang;
