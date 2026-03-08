function setLang(lang) {
    // 1. Prioridad: Español por defecto si el idioma solicitado no existe
    if (!translations || !translations[lang]) lang = 'es';
    
    localStorage.setItem('gl_lang', lang);

    // 2. FUSIÓN DE DICCIONARIOS: Unimos el principal con los mundos si existen
    // Esto permite que cada lab tenga su propio archivo sin tocar el principal
    const t = { 
        ...translations[lang], 
        ...(typeof mathWorld !== 'undefined' ? mathWorld[lang] : {}),
        ...(typeof cymaticsWorld !== 'undefined' ? cymaticsWorld[lang] : {}),
        ...(typeof geometryWorld !== 'undefined' ? geometryWorld[lang] : {})
    };

    // 3. ACTUALIZACIÓN DEL DOM
    document.querySelectorAll('[data-i18n]').forEach(el => {
        const path = el.getAttribute('data-i18n').split('.');
        let text = t;
        path.forEach(key => { if (text) text = text[key]; });
        
        if (text) {
            if (el.tagName === 'A' || el.tagName === 'BUTTON' || el.classList.contains('btn-lab')) {
                el.innerText = text;
            } else {
                el.innerText = text;
            }
        }
    });

    // 4. ESTADO DE BOTONES
    document.querySelectorAll('.lang-switch button').forEach(btn => {
        btn.classList.remove('active');
        if (btn.id === `btn-${lang}`) btn.classList.add('active');
    });
    document.documentElement.lang = lang;
}

document.addEventListener('DOMContentLoaded', () => {
    const savedLang = localStorage.getItem('gl_lang') || 'es';
    setLang(savedLang);
});