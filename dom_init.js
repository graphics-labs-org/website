
        document.addEventListener('DOMContentLoaded', () => {
            const pathParts = window.location.pathname.split('/');
            const urlLang = pathParts.find(p => ['es', 'ca', 'en', 'fr', 'de', 'pt', 'it', 'nl', 'ja'].includes(p));
            const lang = urlLang || localStorage.getItem('gl_lang') || 'es';
            setLang(lang);
        });
