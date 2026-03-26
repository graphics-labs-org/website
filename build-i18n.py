#!/usr/bin/env python3
"""
build-i18n.py — Graphics Labs Multi-Language Build Script
=========================================================
Generates language-specific folders (/es/, /en/, /fr/, etc.) for each supported
language. Each folder contains copies of all HTML files with:
  - Correct <html lang="xx">
  - Translated <title> and <meta name="description">
  - <link rel="canonical"> pointing to the language-specific URL
  - <link rel="alternate" hreflang="xx"> for all supported languages
  - Adjusted relative paths for resources (JS, CSS, images)
  - Language-aware navigation links (HUB, back, language switcher)

The root index.html becomes a smart redirector that detects browser language
and redirects to the correct language folder.

Usage:
    python build-i18n.py

Run from the website root directory.
"""

import os
import re
import shutil
from pathlib import Path
from datetime import datetime

# ============================================================================
# CONFIGURATION
# ============================================================================

DOMAIN = "https://graphics-labs.org"
LANGUAGES = ['es', 'ca', 'en', 'fr', 'de', 'pt', 'it', 'nl', 'ja']
DEFAULT_LANG = 'es'

# Pages relative to root (the ones we generate per language)
# Format: (source_path, page_slug_for_url)
ROOT_PAGES = [
    ('index.html', ''),
]

LEGAL_PAGES = [
    ('legal.html', 'legal.html'),
    ('privacy.html', 'privacy.html'),
    ('cookies.html', 'cookies.html'),
]

HUB_PAGES = [
    ('labs/math-index.html', 'labs/math-index.html'),
    ('labs/geometria-sagrada-index.html', 'labs/geometria-sagrada-index.html'),
]

LAB_PAGES = [
    ('labs/arbol-vida/index.html', 'labs/arbol-vida/'),
    ('labs/chaos-lab/index.html', 'labs/chaos-lab/'),
    ('labs/chartres-labyrinth/index.html', 'labs/chartres-labyrinth/'),
    ('labs/collatz-lab/index.html', 'labs/collatz-lab/'),
    ('labs/cymatics-lab/index.html', 'labs/cymatics-lab/'),
    ('labs/double-pendulum/index.html', 'labs/double-pendulum/'),
    ('labs/flor-vida/index.html', 'labs/flor-vida/'),
    ('labs/fourier-lab/index.html', 'labs/fourier-lab/'),
    ('labs/fractal-explorer/index.html', 'labs/fractal-explorer/'),
    ('labs/game-of-life/index.html', 'labs/game-of-life/'),
    ('labs/golden-spiral/index.html', 'labs/golden-spiral/'),
    ('labs/harmonograph-lab/index.html', 'labs/harmonograph-lab/'),
    ('labs/magic-square/index.html', 'labs/magic-square/'),
    ('labs/mandala-mano/index.html', 'labs/mandala-mano/'),
    ('labs/metatron-cube/index.html', 'labs/metatron-cube/'),
    ('labs/modular-lab/index.html', 'labs/modular-lab/'),
    ('labs/phi-lab/index.html', 'labs/phi-lab/'),
    ('labs/pi-search/index.html', 'labs/pi-search/'),
    ('labs/solidos-platonicos/index.html', 'labs/solidos-platonicos/'),
    ('labs/sri-yantra/index.html', 'labs/sri-yantra/'),
    ('labs/toroide-vortex/index.html', 'labs/toroide-vortex/'),
    ('labs/ulam-spiral/index.html', 'labs/ulam-spiral/'),
]

ALL_PAGES = ROOT_PAGES + LEGAL_PAGES + HUB_PAGES + LAB_PAGES

# ============================================================================
# SEO METADATA PER PAGE PER LANGUAGE
# title and description for each page
# ============================================================================

PAGE_TITLES = {
    '': {
        'es': 'Graphics Labs | Arte & Código — Experimentos Visuales Interactivos',
        'ca': 'Graphics Labs | Art & Codi — Experiments Visuals Interactius',
        'en': 'Graphics Labs | Art & Code — Interactive Visual Experiments',
        'fr': 'Graphics Labs | Art & Code — Expériences Visuelles Interactives',
        'de': 'Graphics Labs | Kunst & Code — Interaktive visuelle Experimente',
        'pt': 'Graphics Labs | Arte & Código — Experimentos Visuais Interativos',
        'it': 'Graphics Labs | Arte & Codice — Esperimenti Visivi Interattivi',
        'nl': 'Graphics Labs | Kunst & Code — Interactieve Visuele Experimenten',
        'ja': 'Graphics Labs | アート＆コード — インタラクティブなビジュアル実験',
    },
    'legal.html': {
        'es': 'Aviso Legal | Graphics Labs',
        'ca': 'Avís Legal | Graphics Labs',
        'en': 'Legal Notice | Graphics Labs',
        'fr': 'Mentions Légales | Graphics Labs',
        'de': 'Impressum | Graphics Labs',
        'pt': 'Aviso Legal | Graphics Labs',
        'it': 'Avviso Legale | Graphics Labs',
        'nl': 'Juridische Kennisgeving | Graphics Labs',
        'ja': '法的通知 | Graphics Labs',
    },
    'privacy.html': {
        'es': 'Política de Privacidad | Graphics Labs',
        'ca': 'Política de Privacitat | Graphics Labs',
        'en': 'Privacy Policy | Graphics Labs',
        'fr': 'Politique de Confidentialité | Graphics Labs',
        'de': 'Datenschutzrichtlinie | Graphics Labs',
        'pt': 'Política de Privacidade | Graphics Labs',
        'it': 'Informativa sulla Privacy | Graphics Labs',
        'nl': 'Privacybeleid | Graphics Labs',
        'ja': 'プライバシーポリシー | Graphics Labs',
    },
    'cookies.html': {
        'es': 'Política de Cookies | Graphics Labs',
        'ca': 'Política de Cookies | Graphics Labs',
        'en': 'Cookies Policy | Graphics Labs',
        'fr': 'Politique de Cookies | Graphics Labs',
        'de': 'Cookie-Richtlinie | Graphics Labs',
        'pt': 'Política de Cookies | Graphics Labs',
        'it': 'Cookie Policy | Graphics Labs',
        'nl': 'Cookiebeleid | Graphics Labs',
        'ja': 'Cookieポリシー | Graphics Labs',
    },
    'labs/math-index.html': {
        'es': 'Departamento de Matemáticas | Graphics Labs',
        'ca': 'Departament de Matemàtiques | Graphics Labs',
        'en': 'Mathematics Department | Graphics Labs',
        'fr': 'Département de Mathématiques | Graphics Labs',
        'de': 'Mathematik-Abteilung | Graphics Labs',
        'pt': 'Departamento de Matemática | Graphics Labs',
        'it': 'Dipartimento di Matematica | Graphics Labs',
        'nl': 'Afdeling Wiskunde | Graphics Labs',
        'ja': '数学部門 | Graphics Labs',
    },
    'labs/geometria-sagrada-index.html': {
        'es': 'Geometría Sagrada | Graphics Labs',
        'ca': 'Geometria Sagrada | Graphics Labs',
        'en': 'Sacred Geometry | Graphics Labs',
        'fr': 'Géométrie Sacrée | Graphics Labs',
        'de': 'Heilige Geometrie | Graphics Labs',
        'pt': 'Geometria Sagrada | Graphics Labs',
        'it': 'Geometria Sacra | Graphics Labs',
        'nl': 'Heilige Geometrie | Graphics Labs',
        'ja': '神聖幾何学 | Graphics Labs',
    },
}

PAGE_DESCRIPTIONS = {
    '': {
        'es': 'Laboratorio de experimentos visuales interactivos. Geometría sagrada, fractales, cimática, matemáticas y arte generativo.',
        'ca': "Laboratori d'experiments visuals interactius. Geometria sagrada, fractals, cimàtica, matemàtiques i art generatiu.",
        'en': 'Interactive visual experiments laboratory. Sacred geometry, fractals, cymatics, mathematics and generative art.',
        'fr': "Laboratoire d'expériences visuelles interactives. Géométrie sacrée, fractales, cymatique, mathématiques et art génératif.",
        'de': 'Labor für interaktive visuelle Experimente. Heilige Geometrie, Fraktale, Kymatik, Mathematik und generative Kunst.',
        'pt': 'Laboratório de experimentos visuais interativos. Geometria sagrada, fractais, cimática, matemática e arte generativa.',
        'it': 'Laboratorio di esperimenti visivi interattivi. Geometria sacra, frattali, cimatica, matematica e arte generativa.',
        'nl': 'Laboratorium voor interactieve visuele experimenten. Heilige geometrie, fractals, cymatica, wiskunde en generatieve kunst.',
        'ja': 'インタラクティブな視覚実験ラボ。神聖幾何学、フラクタル、サイマティクス、数学、ジェネレーティブアート。',
    },
    'legal.html': {lang: 'Aviso legal y condiciones de uso de Graphics Labs.' for lang in LANGUAGES},
    'privacy.html': {lang: 'Política de privacidad de Graphics Labs. Información sobre el tratamiento de datos.' for lang in LANGUAGES},
    'cookies.html': {lang: 'Política de cookies de Graphics Labs. Información sobre las cookies utilizadas.' for lang in LANGUAGES},
    'labs/math-index.html': {
        'es': 'Cuadrados mágicos, secuencias numéricas, fractales y la belleza de las matemáticas visuales. Laboratorio interactivo.',
        'ca': 'Quadrats màgics, seqüències numèriques, fractals i la bellesa de les matemàtiques visuals. Laboratori interactiu.',
        'en': 'Magic squares, number sequences, fractals and the beauty of visual mathematics. Interactive laboratory.',
        'fr': 'Carrés magiques, suites numériques, fractales et la beauté des mathématiques visuelles. Laboratoire interactif.',
        'de': 'Magische Quadrate, Zahlenfolgen, Fraktale und die Schönheit der visuellen Mathematik. Interaktives Labor.',
        'pt': 'Quadrados mágicos, sequências numéricas, fractais e a beleza da matemática visual. Laboratório interativo.',
        'it': 'Quadrati magici, sequenze numeriche, frattali e la bellezza della matematica visiva. Laboratorio interattivo.',
        'nl': 'Magische vierkanten, getallenreeksen, fractals en de schoonheid van visuele wiskunde. Interactief laboratorium.',
        'ja': '魔方陣、数列、フラクタル、そしてビジュアル数学の美しさ。インタラクティブラボ。',
    },
    'labs/geometria-sagrada-index.html': {
        'es': 'Explorador de geometría sagrada interactivo: Sri Yantra, Flor de la Vida, Metatrón, Sólidos Platónicos y más.',
        'ca': "Explorador de geometria sagrada interactiu: Sri Yantra, Flor de la Vida, Metatró, Sòlids Platònics i més.",
        'en': 'Interactive sacred geometry explorer: Sri Yantra, Flower of Life, Metatron, Platonic Solids and more.',
        'fr': "Explorateur de géométrie sacrée interactif : Sri Yantra, Fleur de Vie, Métatron, Solides platoniciens et plus.",
        'de': 'Interaktiver heiliger Geometrie-Explorer: Sri Yantra, Blume des Lebens, Metatron, Platonische Körper und mehr.',
        'pt': 'Explorador de geometria sagrada interativo: Sri Yantra, Flor da Vida, Metatron, Sólidos Platônicos e mais.',
        'it': 'Esploratore di geometria sacra interattivo: Sri Yantra, Fiore della Vita, Metatron, Solidi Platonici e altro.',
        'nl': 'Interactieve heilige geometrie-verkenner: Sri Yantra, Bloem des Levens, Metatron, Platonische lichamen en meer.',
        'ja': 'インタラクティブな神聖幾何学エクスプローラー：シュリ・ヤントラ、生命の花、メタトロン、プラトン立体など。',
    },
}

# For lab pages, generate generic titles/descriptions based on the folder name
def get_lab_title(slug, lang):
    """Generate a title for a lab page based on its folder name."""
    if slug in PAGE_TITLES:
        return PAGE_TITLES[slug].get(lang, PAGE_TITLES[slug].get('en', ''))
    # Generic: use folder name
    lab_name = slug.replace('labs/', '').replace('/', '').replace('-', ' ').title()
    return f"{lab_name} | Graphics Labs"

def get_lab_description(slug, lang):
    """Generate a description for lab pages."""
    if slug in PAGE_DESCRIPTIONS:
        return PAGE_DESCRIPTIONS[slug].get(lang, PAGE_DESCRIPTIONS[slug].get('en', ''))
    lab_name = slug.replace('labs/', '').replace('/', '').replace('-', ' ').title()
    descs = {
        'es': f'Laboratorio interactivo de {lab_name}. Experimenta con arte generativo y matemáticas visuales en Graphics Labs.',
        'ca': f'Laboratori interactiu de {lab_name}. Experimenta amb art generatiu i matemàtiques visuals a Graphics Labs.',
        'en': f'Interactive {lab_name} laboratory. Experiment with generative art and visual mathematics at Graphics Labs.',
        'fr': f'Laboratoire interactif de {lab_name}. Expérimentez avec l\'art génératif et les mathématiques visuelles sur Graphics Labs.',
        'de': f'Interaktives {lab_name}-Labor. Experimentieren Sie mit generativer Kunst und visueller Mathematik bei Graphics Labs.',
        'pt': f'Laboratório interativo de {lab_name}. Experimente com arte generativa e matemática visual no Graphics Labs.',
        'it': f'Laboratorio interattivo di {lab_name}. Sperimenta con arte generativa e matematica visiva su Graphics Labs.',
        'nl': f'Interactief {lab_name}-laboratorium. Experimenteer met generatieve kunst en visuele wiskunde bij Graphics Labs.',
        'ja': f'{lab_name}インタラクティブラボ。Graphics Labsでジェネレーティブアートとビジュアル数学を体験してください。',
    }
    return descs.get(lang, descs['en'])


# ============================================================================
# BUILD LOGIC
# ============================================================================

def get_canonical_url(lang, page_slug):
    """Get the canonical URL for a page in a specific language."""
    if page_slug == '':
        return f"{DOMAIN}/{lang}/"
    elif page_slug.endswith('/'):
        return f"{DOMAIN}/{lang}/{page_slug}"
    else:
        return f"{DOMAIN}/{lang}/{page_slug}"

def generate_hreflang_tags(page_slug):
    """Generate hreflang link tags for all languages."""
    tags = []
    for lang in LANGUAGES:
        url = get_canonical_url(lang, page_slug)
        tags.append(f'    <link rel="alternate" hreflang="{lang}" href="{url}" />')
    # x-default points to default language
    default_url = get_canonical_url(DEFAULT_LANG, page_slug)
    tags.append(f'    <link rel="alternate" hreflang="x-default" href="{default_url}" />')
    return '\n'.join(tags)

def compute_depth(source_path):
    """Compute how many directory levels deep the file is from root."""
    return source_path.count('/')

def adjust_relative_paths(html, source_path, lang):
    """
    Adjust relative paths in HTML for the language subfolder.
    Files in /es/ need to go up one level to reach root resources.
    Files in /es/labs/ need to go up two levels, etc.
    """
    depth = compute_depth(source_path)
    # The language folder adds one level of depth
    # So we need "../" prefix to go from /lang/... back to root
    prefix = "../"  # from /lang/ back to root
    
    # For files in labs subdirectories, they already use relative paths
    # like ../languages.js (from labs/math-index.html) or ../../index.html (from labs/magic-square/)
    # We need to adjust these so they work from /lang/labs/... 
    
    # Actually, the simplest approach: 
    # Since the lang folder files will reference resources at root level,
    # we adjust all relative paths to add the right number of ../
    
    return html

def patch_html_for_lang(html, source_path, page_slug, lang):
    """
    Patch an HTML file for a specific language:
    1. Set <html lang="xx">
    2. Add/replace <title>
    3. Add/replace <meta name="description">
    4. Add <link rel="canonical">
    5. Add <link rel="alternate" hreflang="xx">
    6. Inject language auto-detection script
    7. Modify setLang() to also update URL
    """
    
    title = get_lab_title(page_slug, lang)
    description = get_lab_description(page_slug, lang)
    canonical_url = get_canonical_url(lang, page_slug)
    hreflang_tags = generate_hreflang_tags(page_slug)
    
    # 1. Set <html lang="xx">
    html = re.sub(r'<html\s+lang="[^"]*"', f'<html lang="{lang}"', html)
    
    # 2. Replace <title>
    html = re.sub(r'<title>[^<]*</title>', f'<title>{title}</title>', html)
    
    # 3. Add or replace <meta name="description">
    if re.search(r'<meta\s+name="description"', html):
        html = re.sub(
            r'<meta\s+name="description"\s+content="[^"]*"\s*/?>',
            f'<meta name="description" content="{description}">',
            html
        )
    else:
        # Insert after <meta name="viewport">
        html = re.sub(
            r'(<meta\s+name="viewport"[^>]*>)',
            f'\\1\n    <meta name="description" content="{description}">',
            html
        )
    
    # 4. Add or replace canonical
    if re.search(r'<link\s+rel="canonical"', html):
        html = re.sub(
            r'<link\s+rel="canonical"\s+href="[^"]*"\s*/?>',
            f'<link rel="canonical" href="{canonical_url}" />',
            html
        )
    else:
        # Insert before </head>
        html = html.replace(
            '</head>',
            f'    <link rel="canonical" href="{canonical_url}" />\n</head>'
        )
    
    # 5. Add hreflang tags (remove old ones first)
    html = re.sub(r'\s*<link\s+rel="alternate"\s+hreflang="[^"]*"\s+href="[^"]*"\s*/?\>\n?', '', html)
    html = html.replace(
        '</head>',
        f'\n{hreflang_tags}\n</head>'
    )
    
    # 6. Inject the language-from-URL detection + switcher override
    lang_upper = lang.upper()
    lang_switcher_script = f'''
    <script>
    // --- i18n URL Router ---
    (function() {{
        window.__GL_LANG = '{lang}';
        window.__GL_LANG_UPPER = '{lang_upper}';
        window.__GL_LANGS = {str(LANGUAGES)};
        
        // Override localStorage to always use URL-based language
        localStorage.setItem('gl_lang', '{lang}');
        
        // Language switcher: navigate to the equivalent page in the target language folder
        window.switchLangUrl = function(targetLang) {{
            var path = window.location.pathname;
            // Replace current lang segment with target lang
            var newPath = path.replace(/^\\/({"|".join(LANGUAGES)})\\//, '/' + targetLang.toLowerCase() + '/');
            if (newPath === path) {{
                // Fallback: prepend lang
                newPath = '/' + targetLang.toLowerCase() + '/';
            }}
            window.location.href = newPath + window.location.hash;
        }};
        
        // Auto-call setLang on DOMContentLoaded to apply translations
        // Some labs use uppercase keys (ES/EN), others lowercase (es/en)
        document.addEventListener('DOMContentLoaded', function() {{
            if (typeof setLang === 'function') {{
                // Try uppercase first (used by most lab pages with inline translations)
                try {{ setLang('{lang_upper}'); }} catch(e) {{}}
                // Also try lowercase (used by magic-square style pages)
                try {{ setLang('{lang}'); }} catch(e) {{}}
            }}
        }});
    }})();
    </script>'''
    
    # Insert after <head> opening or after charset meta
    html = re.sub(
        r'(<meta\s+charset="UTF-8"\s*/?>)',
        f'\\1{lang_switcher_script}',
        html,
        count=1
    )
    
    # 7. Update language switcher buttons to use switchLangUrl()
    # Pattern 1: onclick="setLang('xx')" (lowercase)
    for l in LANGUAGES:
        html = html.replace(
            f"onclick=\"setLang('{l}')\"",
            f"onclick=\"switchLangUrl('{l}')\""
        )
    # Pattern 2: onclick="setLang('XX')" (uppercase, used in cymatics etc)
    for l in LANGUAGES:
        html = html.replace(
            f"onclick=\"setLang('{l.upper()}')\"",
            f"onclick=\"switchLangUrl('{l}')\""
        )
    
    # 8. Fix relative paths to resources
    # Files in lang subfolders need adjusted paths to reach root resources
    depth = compute_depth(source_path)
    
    if source_path == 'index.html':
        # Root index.html -> /lang/index.html: needs ../ to reach root
        # JS files: src="languages.js" -> src="../languages.js"
        html = html.replace('src="languages.js"', 'src="../languages.js"')
        html = html.replace('src="labs-config.js"', 'src="../labs-config.js"')
        # Lab links: href="labs/xxx" -> href="../labs/xxx" — NO! These should go to /lang/labs/xxx
        # Actually keep lab links relative since we'll have the labs in the lang folder too
        # Legal links: href="legal.html" -> stays relative (will be in /lang/legal.html)
        
    elif source_path.startswith('labs/') and source_path.count('/') == 1:
        # Hub pages like labs/math-index.html -> /lang/labs/math-index.html
        # src="../languages.js" -> src="../../languages.js"
        html = html.replace('src="../languages.js"', 'src="../../languages.js"')
        html = html.replace('src="../translations/', 'src="../../translations/')
        # Back link: href="../index.html" -> stays (goes to /lang/index.html — but wait,
        # /lang/index.html exists so this is correct)
        # Legal: href="../legal.html" -> stays (goes to /lang/legal.html)
        # Lab links inside: href="magic-square/index.html" -> stays relative
        # Thumbnail images
        html = re.sub(r'src="(thumbnail-[^"]*\.png)"', r'src="../../labs/\1"', html)
        
    elif source_path.startswith('labs/') and source_path.count('/') == 2:
        # Individual lab pages like labs/magic-square/index.html -> /lang/labs/magic-square/index.html
        # src="../../languages.js" -> would need to go up to root: src="../../../languages.js"
        # but actually some use inline translations, so we need to check
        # Links: href="../../index.html" -> needs to become "../../../index.html"... 
        # Wait — BUT we have /lang/index.html, so ../../index.html from /lang/labs/magic-square/ 
        # goes to /lang/index.html. That's correct!
        
        # Actually let's think about this more carefully:
        # File at: /lang/labs/magic-square/index.html
        # ../../index.html -> /lang/index.html ✓ 
        # ../../legal.html -> /lang/legal.html ✓
        # ../math-index.html -> /lang/labs/math-index.html ✓
        # ../../languages.js -> /lang/languages.js ✗ (doesn't exist there!)
        
        # So we need to fix paths to root JS/resource files
        # ../../languages.js -> needs to go to root: ../../../languages.js
        html = html.replace('src="../../languages.js"', 'src="../../../languages.js"')
        html = html.replace('src="../../translations/', 'src="../../../translations/')
    
    elif source_path in ['legal.html', 'privacy.html', 'cookies.html']:
        # Legal pages at root -> /lang/legal.html
        # href="index.html" -> stays (goes to /lang/index.html)
        pass
    
    return html


def build_lang_folder(lang, root_dir):
    """Build the complete language folder for a given language."""
    lang_dir = os.path.join(root_dir, lang)
    
    for source_path, page_slug in ALL_PAGES:
        # For index.html, prefer index.original.html (the real page)
        # because index.html may have been replaced by the redirector
        if source_path == 'index.html':
            original_file = os.path.join(root_dir, 'index.original.html')
            if os.path.exists(original_file):
                source_file = original_file
            else:
                source_file = os.path.join(root_dir, source_path)
        else:
            source_file = os.path.join(root_dir, source_path)
        
        if not os.path.exists(source_file):
            print(f"  ⚠ SKIP (not found): {source_path}")
            continue
        
        # Determine destination path
        dest_path = os.path.join(lang_dir, source_path)
        dest_dir = os.path.dirname(dest_path)
        os.makedirs(dest_dir, exist_ok=True)
        
        # Read source HTML
        with open(source_file, 'r', encoding='utf-8') as f:
            html = f.read()
        
        # Patch HTML for this language
        html = patch_html_for_lang(html, source_path, page_slug, lang)
        
        # Write patched HTML
        with open(dest_path, 'w', encoding='utf-8') as f:
            f.write(html)
        
        print(f"  ✓ {lang}/{source_path}")


def build_root_redirector(root_dir):
    """Create a root index.html that redirects to the correct language."""
    hreflang_tags = generate_hreflang_tags('')
    
    redirector_html = f'''<!DOCTYPE html>
<html lang="{DEFAULT_LANG}">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Graphics Labs | Art & Code</title>
    <meta name="description" content="Interactive visual experiments laboratory. Sacred geometry, fractals, cymatics, mathematics and generative art.">
    <link rel="canonical" href="{DOMAIN}/{DEFAULT_LANG}/" />
{hreflang_tags}
    <script>
    (function() {{
        var supported = {str(LANGUAGES)};
        var defaultLang = '{DEFAULT_LANG}';
        
        // Check localStorage first
        var saved = null;
        try {{ saved = localStorage.getItem('gl_lang'); }} catch(e) {{}}
        
        // Then check browser language
        var browserLang = (navigator.language || navigator.userLanguage || '').substring(0, 2).toLowerCase();
        
        var lang = defaultLang;
        if (saved && supported.indexOf(saved) !== -1) {{
            lang = saved;
        }} else if (supported.indexOf(browserLang) !== -1) {{
            lang = browserLang;
        }}
        
        window.location.replace('/' + lang + '/');
    }})();
    </script>
    <noscript>
        <meta http-equiv="refresh" content="0;url=/{DEFAULT_LANG}/">
    </noscript>
</head>
<body>
    <p>Redirecting... <a href="/{DEFAULT_LANG}/">Click here</a> if not redirected.</p>
</body>
</html>'''
    
    dest = os.path.join(root_dir, 'index.html')
    # Backup original
    backup = os.path.join(root_dir, 'index.original.html')
    if os.path.exists(dest) and not os.path.exists(backup):
        shutil.copy2(dest, backup)
        print(f"  📦 Backed up original index.html -> index.original.html")
    
    with open(dest, 'w', encoding='utf-8') as f:
        f.write(redirector_html)
    print(f"  ✓ Root index.html (redirector)")


def build_sitemap(root_dir):
    """Generate a comprehensive sitemap with hreflang annotations."""
    now = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S+00:00')
    
    urls = []
    for source_path, page_slug in ALL_PAGES:
        # Priority based on page type
        if page_slug == '':
            priority = '1.00'
        elif page_slug in ['labs/math-index.html', 'labs/geometria-sagrada-index.html']:
            priority = '0.80'
        elif page_slug in ['legal.html', 'privacy.html', 'cookies.html']:
            priority = '0.30'
        else:
            priority = '0.64'
        
        for lang in LANGUAGES:
            canonical = get_canonical_url(lang, page_slug)
            
            # Build xhtml:link alternates
            alternates = []
            for alt_lang in LANGUAGES:
                alt_url = get_canonical_url(alt_lang, page_slug)
                alternates.append(f'    <xhtml:link rel="alternate" hreflang="{alt_lang}" href="{alt_url}" />')
            alt_url = get_canonical_url(DEFAULT_LANG, page_slug)
            alternates.append(f'    <xhtml:link rel="alternate" hreflang="x-default" href="{alt_url}" />')
            
            url_entry = f'''<url>
  <loc>{canonical}</loc>
  <lastmod>{now}</lastmod>
  <priority>{priority}</priority>
{chr(10).join(alternates)}
</url>'''
            urls.append(url_entry)
    
    sitemap = f'''<?xml version="1.0" encoding="UTF-8"?>
<urlset
      xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"
      xmlns:xhtml="http://www.w3.org/1999/xhtml"
      xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
      xsi:schemaLocation="http://www.sitemaps.org/schemas/sitemap/0.9
            http://www.sitemaps.org/schemas/sitemap/0.9/sitemap.xsd">
<!-- Generated by build-i18n.py -->

{chr(10).join(urls)}

</urlset>'''
    
    with open(os.path.join(root_dir, 'sitemap.xml'), 'w', encoding='utf-8') as f:
        f.write(sitemap)
    print(f"  ✓ sitemap.xml ({len(urls)} URLs)")


def clean_lang_folders(root_dir):
    """Remove existing language folders before rebuilding."""
    for lang in LANGUAGES:
        lang_dir = os.path.join(root_dir, lang)
        if os.path.exists(lang_dir):
            shutil.rmtree(lang_dir)
            print(f"  🗑  Cleaned /{lang}/")


def main():
    root_dir = os.path.dirname(os.path.abspath(__file__))
    
    print("=" * 60)
    print("🌍 Graphics Labs — Multi-Language Build")
    print("=" * 60)
    print(f"Root: {root_dir}")
    print(f"Languages: {', '.join(LANGUAGES)}")
    print(f"Default: {DEFAULT_LANG}")
    print(f"Pages: {len(ALL_PAGES)}")
    print()
    
    # 1. Clean old builds
    print("🧹 Cleaning old language folders...")
    clean_lang_folders(root_dir)
    print()
    
    # 2. Build each language folder
    for lang in LANGUAGES:
        print(f"📁 Building /{lang}/...")
        build_lang_folder(lang, root_dir)
    print()
    
    # 3. Build root redirector
    print("🏠 Building root redirector...")
    build_root_redirector(root_dir)
    print()
    
    # 4. Build sitemap
    print("🗺  Building sitemap...")
    build_sitemap(root_dir)
    print()
    
    # Summary
    total_files = len(ALL_PAGES) * len(LANGUAGES) + 1  # +1 for redirector
    print("=" * 60)
    print(f"✅ Build complete! Generated {total_files} files")
    print(f"   across {len(LANGUAGES)} language folders.")
    print()
    print("📝 Next steps:")
    print("   1. Test locally: python -m http.server 8000")
    print("   2. Commit and push to GitHub")
    print("   3. Resubmit sitemap.xml in Google Search Console")
    print("=" * 60)


if __name__ == '__main__':
    main()
