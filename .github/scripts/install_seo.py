from pathlib import Path
import json, sys

ROOT = Path('.')
INDEX = ROOT / 'index.html'
ROBOTS = ROOT / 'robots.txt'
SITEMAP = ROOT / 'sitemap.xml'
BASE = 'https://mralehsas.github.io/HELIOGUARD-ARABIA/'
TITLE = 'الدرع الشمسي العربي | HELIOGUARD ARABIA — مراقبة الطقس الفضائي'
DESC = 'الدرع الشمسي العربي HELIOGUARD ARABIA منصة عربية لمراقبة الطقس الفضائي والنشاط الشمسي والرياح الشمسية وBz وBt وKp والتوهجات الشمسية وCME من مصادر NASA وNOAA. إعداد وتطوير الفيزيائي عمر الباز.'

REQUIRED = [
    f'<title>{TITLE}</title>',
    f'<link rel="canonical" href="{BASE}" />',
    '<meta name="robots" content="index,follow,max-image-preview:large,max-snippet:-1,max-video-preview:-1" />',
    '<meta property="og:title"',
    '<meta property="og:description"',
    '<meta property="og:url"',
    '<meta name="twitter:card" content="summary_large_image" />',
    '"@type":"WebApplication"',
    '"name":"الدرع الشمسي العربي — HELIOGUARD ARABIA"',
]

def test():
    s = INDEX.read_text(encoding='utf-8')
    missing = [x for x in REQUIRED if x not in s]
    if not ROBOTS.exists(): missing.append('robots.txt')
    if not SITEMAP.exists(): missing.append('sitemap.xml')
    if ROBOTS.exists():
        r = ROBOTS.read_text(encoding='utf-8')
        for x in ['User-agent: *','Allow: /','Sitemap: '+BASE+'sitemap.xml']:
            if x not in r: missing.append('robots:'+x)
    if SITEMAP.exists():
        sm = SITEMAP.read_text(encoding='utf-8')
        for x in [BASE, BASE+'docs/HELIOGUARD_ARABIA_Scientific_Guide_AR_EN.html']:
            if x not in sm: missing.append('sitemap:'+x)
    if missing:
        print('SEO contract NOT satisfied:')
        for x in missing: print(' -', x)
        return 1
    print('SEO contract: GREEN')
    return 0

def apply():
    s = INDEX.read_text(encoding='utf-8')
    old_desc = '<meta name="description" content="HELIOGUARD ARABIA — لوحة عربية حيّة لمراقبة الطقس الفضائي من مصادر NASA وNOAA الرسمية." />'
    old_title = '<title>HELIOGUARD ARABIA v1.0.3 — Disconnected Start</title>'
    if old_desc not in s:
        raise SystemExit('Expected existing description marker not found; refusing unsafe patch.')
    if old_title not in s:
        raise SystemExit('Expected existing title marker not found; refusing unsafe patch.')
    s = s.replace(old_desc, f'<meta name="description" content="{DESC}" />', 1)
    s = s.replace(old_title, f'<title>{TITLE}</title>', 1)
    insertion = f'''\n  <meta name="robots" content="index,follow,max-image-preview:large,max-snippet:-1,max-video-preview:-1" />\n  <meta name="author" content="الفيزيائي عمر الباز" />\n  <link rel="canonical" href="{BASE}" />\n  <meta property="og:type" content="website" />\n  <meta property="og:locale" content="ar_AR" />\n  <meta property="og:site_name" content="HELIOGUARD ARABIA" />\n  <meta property="og:title" content="{TITLE}" />\n  <meta property="og:description" content="{DESC}" />\n  <meta property="og:url" content="{BASE}" />\n  <meta property="og:image" content="{BASE}assets/helioguard-mark.svg" />\n  <meta name="twitter:card" content="summary_large_image" />\n  <meta name="twitter:title" content="{TITLE}" />\n  <meta name="twitter:description" content="{DESC}" />\n  <script type="application/ld+json">{{"@context":"https://schema.org","@type":"WebApplication","name":"الدرع الشمسي العربي — HELIOGUARD ARABIA","alternateName":"HELIOGUARD ARABIA","url":"{BASE}","description":"{DESC}","applicationCategory":"ScienceApplication","operatingSystem":"Web","inLanguage":["ar","en"],"author":{{"@type":"Person","name":"الفيزيائي عمر الباز"}},"creator":{{"@type":"Person","name":"الفيزيائي عمر الباز"}},"isAccessibleForFree":true,"offers":{{"@type":"Offer","price":"0","priceCurrency":"USD"}}}}</script>'''
    anchor = f'<title>{TITLE}</title>'
    s = s.replace(anchor, anchor + insertion, 1)
    INDEX.write_text(s, encoding='utf-8')

    ROBOTS.write_text(
        'User-agent: *\nAllow: /\n\nSitemap: '+BASE+'sitemap.xml\n',
        encoding='utf-8'
    )
    SITEMAP.write_text('''<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n  <url><loc>'''+BASE+'''</loc><changefreq>daily</changefreq><priority>1.0</priority></url>\n  <url><loc>'''+BASE+'''docs/HELIOGUARD_ARABIA_Scientific_Guide_AR_EN.html</loc><changefreq>monthly</changefreq><priority>0.8</priority></url>\n  <url><loc>'''+BASE+'''docs/HELIOGUARD_ARABIA_Scientific_Guide_AR_EN.pdf</loc><changefreq>monthly</changefreq><priority>0.7</priority></url>\n</urlset>\n''', encoding='utf-8')
    print('SEO patch applied.')

if __name__ == '__main__':
    mode = sys.argv[1] if len(sys.argv) > 1 else 'test'
    if mode == 'test': raise SystemExit(test())
    if mode == 'apply': apply(); raise SystemExit(0)
    raise SystemExit('usage: install_seo.py [test|apply]')
