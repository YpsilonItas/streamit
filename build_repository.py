"""Genera sito statico e repository Kodi; solo libreria standard Python."""
import argparse
import hashlib
import html
from pathlib import Path
import shutil
import zipfile
import xml.etree.ElementTree as ET
from urllib.parse import urlparse


def build(base_url, output):
    base_url = base_url.rstrip('/')
    if urlparse(base_url).scheme != 'https' or not urlparse(base_url).netloc:
        raise ValueError('Serve un URL HTTPS pubblico.')
    source = Path(__file__).resolve().parent / 'plugin.video.streamit'
    addon = ET.parse(source / 'addon.xml').getroot()
    output.mkdir(parents=True, exist_ok=True)
    repo = ET.Element('addon', id='repository.streamit', name='StreamIt Repository',
                      version=addon.get('version'), **{'provider-name': 'StreamIt'})
    requires = ET.SubElement(repo, 'requires')
    ET.SubElement(requires, 'import', addon='xbmc.addon', version='19.0.0')
    extension = ET.SubElement(repo, 'extension', point='xbmc.addon.repository', name='StreamIt')
    directory = ET.SubElement(extension, 'dir', minversion='19.0.0')
    index_url = 'https://raw.githubusercontent.com/YpsilonItas/streamit/main/kodi'
    ET.SubElement(directory, 'info').text = index_url + '/addons-' + repo.get('version') + '.xml'
    ET.SubElement(directory, 'checksum', verify='sha256').text = index_url + '/addons-' + repo.get('version') + '.xml.sha256'
    ET.SubElement(directory, 'datadir').text = base_url + '/'
    meta = ET.SubElement(repo, 'extension', point='xbmc.addon.metadata')
    ET.SubElement(meta, 'summary', lang='it_IT').text = 'Installazione e aggiornamenti di StreamIt'
    ET.SubElement(meta, 'description', lang='it_IT').text = 'Repository personale StreamIt per Kodi 19 e successivi.'
    ET.SubElement(meta, 'platform').text = 'all'
    ET.SubElement(meta, 'license').text = 'GPL-2.0-or-later'
    assets = ET.SubElement(meta, 'assets')
    icon_name = 'icon-' + addon.get('version') + '.png'
    ET.SubElement(assets, 'icon').text = icon_name
    repo_xml = ET.tostring(repo, encoding='utf-8', xml_declaration=True)
    icon = source / 'resources/media/icon.png'
    repo_dir = output / 'repository.streamit'
    repo_dir.mkdir(exist_ok=True)
    repo_zip = repo_dir / ('repository.streamit-' + repo.get('version') + '.zip')
    with zipfile.ZipFile(repo_zip, 'w', zipfile.ZIP_DEFLATED) as archive:
        archive.writestr('repository.streamit/', b'')
        archive.writestr('repository.streamit/addon.xml', repo_xml)
        archive.write(icon, 'repository.streamit/' + icon_name)
    (repo_dir / 'addon.xml').write_bytes(repo_xml)
    shutil.copy2(icon, repo_dir / 'icon.png')
    shutil.copy2(icon, repo_dir / icon_name)
    shutil.copy2(repo_zip, output / repo_zip.name)
    shutil.copy2(repo_zip, output / 'repository.streamit-1.0.0.zip')
    addon_dir = output / addon.get('id')
    addon_dir.mkdir(exist_ok=True)
    addon_zip = addon_dir / (addon.get('id') + '-' + addon.get('version') + '.zip')
    with zipfile.ZipFile(addon_zip, 'w', zipfile.ZIP_STORED) as archive:
        archive.writestr(source.name + '/', b'')
        for path in sorted(source.rglob('*')):
            if '__pycache__' in path.parts or path.suffix == '.pyc':
                continue
            name = path.relative_to(source.parent).as_posix()
            if path.is_dir():
                archive.writestr(name + '/', b'')
            else:
                archive.write(path, name)
    # Kodi legge le immagini dal percorso dichiarato nel manifest.
    for asset in addon.findall('./extension[@point="xbmc.addon.metadata"]/assets/*'):
        if asset.text:
            dest = addon_dir / asset.text
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source / asset.text, dest)
    shutil.copy2(source / 'addon.xml', addon_dir / 'addon.xml')
    listing = ET.Element('addons')
    listing.extend([repo, addon])
    xml = ET.tostring(listing, encoding='utf-8', xml_declaration=True)
    (output / 'addons.xml').write_bytes(xml)
    (output / 'addons.xml.sha256').write_text(hashlib.sha256(xml).hexdigest(), encoding='ascii')
    shutil.copy2(output / 'addons.xml', output / ('addons-' + repo.get('version') + '.xml'))
    shutil.copy2(output / 'addons.xml.sha256', output / ('addons-' + repo.get('version') + '.xml.sha256'))
    (output / '.nojekyll').touch()
    link = addon_zip.relative_to(output).as_posix()
    page = '<!doctype html>\n<html lang="it">\n<head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">\n<meta name="description" content="StreamIt By Ema. Un addon per Kodi.">\n<title>StreamIt · By Ema</title>\n<style>\n:root{color-scheme:dark;--bg:#0a1019;--panel:#121c29;--text:#edf4fa;--muted:#9aabbc;--accent:#76ead5;--line:#243346}*{box-sizing:border-box}html{scroll-behavior:smooth}body{margin:0;background:var(--bg);color:var(--text);font:16px/1.6 system-ui,-apple-system,Segoe UI,sans-serif}a{color:inherit;text-decoration:none}a:focus-visible,button:focus-visible{outline:3px solid var(--accent);outline-offset:5px}.wrap{max-width:1120px;margin:auto;padding:0 28px}header{border-bottom:1px solid var(--line)}nav{display:flex;justify-content:space-between;align-items:center;min-height:90px;gap:20px}.brand{display:flex;align-items:center;gap:14px;font-size:21px;font-weight:750}.brand img{width:44px;height:44px;border-radius:12px}.navlinks{display:flex;gap:26px;color:var(--muted);font-size:14px}.navlinks a:hover{color:var(--accent)}.hero{display:grid;grid-template-columns:1.5fr 1fr;gap:60px;align-items:center;padding:90px 0 70px}.eyebrow{color:var(--accent);font-size:12px;font-weight:750;letter-spacing:.16em;text-transform:uppercase}h1{font-size:clamp(42px,6vw,74px);line-height:1.06;letter-spacing:-.055em;margin:18px 0 25px}h1 span{color:var(--accent)}.lead{font-size:19px;color:var(--muted);max-width:520px}.actions{display:flex;gap:12px;flex-wrap:wrap;margin:30px 0 16px}.button{display:inline-flex;justify-content:center;align-items:center;gap:10px;min-height:50px;padding:12px 22px;border-radius:12px;font-weight:700;background:var(--accent);color:#09201b;border:1px solid var(--accent)}.button.secondary{background:transparent;color:var(--text);border-color:var(--line)}.button:hover{filter:brightness(1.1)}.version{color:var(--muted);font-size:13px}.logo-card{position:relative;padding:32px;background:linear-gradient(135deg,#162b35,#121b2a);border:1px solid #2d4653;border-radius:32px;transform:rotate(3deg);box-shadow:0 30px 70px #0005}.logo-card img{display:block;width:100%;border-radius:22px}.logo-card p{text-align:center;color:var(--muted);margin:20px 0 0;font-size:13px;letter-spacing:.12em}.features{display:grid;grid-template-columns:repeat(3,1fr);gap:18px;margin:0 0 75px}.card{background:var(--panel);border:1px solid var(--line);border-radius:18px;padding:26px}.card img{width:48px;height:48px;border-radius:12px;margin-bottom:12px}.card h2{font-size:21px;margin:0 0 8px}.card p{margin:0;color:var(--muted);font-size:15px}.install{border-top:1px solid var(--line);padding:60px 0 70px}.section-head{display:flex;justify-content:space-between;align-items:end;gap:20px;margin-bottom:26px}.section-head h2{font-size:32px;letter-spacing:-.025em;margin:8px 0 0}.section-head p{color:var(--muted);max-width:400px;margin:0}.source{display:flex;align-items:center;justify-content:space-between;gap:14px;padding:18px 20px;border:1px solid var(--line);background:var(--panel);border-radius:14px;margin-bottom:25px}.source code{overflow-wrap:anywhere;color:var(--accent);font-size:15px}.source button{cursor:pointer;border:1px solid var(--line);background:#1b2a3a;color:var(--text);padding:10px 16px;border-radius:9px;font:inherit}.steps{display:grid;grid-template-columns:repeat(3,1fr);gap:24px;list-style:none;padding:0;counter-reset:step}.steps li{counter-increment:step;color:var(--muted)}.steps li:before{content:\'0\' counter(step);display:block;color:var(--accent);font-weight:700;font-size:14px;margin-bottom:10px}.steps strong{display:block;color:var(--text);margin-bottom:7px}.note{font-size:13px;color:var(--muted);margin:26px 0 0}footer{border-top:1px solid var(--line);padding:24px 0;color:var(--muted);font-size:13px}.footer-inner{display:flex;justify-content:space-between;gap:20px}.status{min-height:24px;color:var(--accent);font-size:13px} @media(max-width:720px){.wrap{padding:0 20px}.hero{grid-template-columns:1fr;padding:55px 0 40px;gap:35px}.logo-card{max-width:290px;margin:0 auto;transform:none}.features,.steps{grid-template-columns:1fr}.features{margin-bottom:40px}.section-head{display:block}.section-head p{margin-top:14px}.navlinks{gap:14px}.brand{font-size:18px}.source{align-items:flex-start}.footer-inner{flex-direction:column;gap:6px}.install{padding-top:40px}}@media(prefers-reduced-motion:reduce){html{scroll-behavior:auto}}\n</style></head>\n<body>\n<header><nav class="wrap"><a class="brand" href="./"><img src="repository.streamit/icon-{{VERSION}}.png" alt="">StreamIt</a><div class="navlinks"><a href="#installazione">Installazione</a><a href="https://github.com/YpsilonItas/streamit">GitHub ↗</a></div></nav></header>\n<main class="wrap">\n<section class="hero"><div><div class="eyebrow">Per Kodi 19 e successivi · By Ema</div><h1>StreamIt.<br><span>By Ema.</span></h1><p class="lead">Un addon per Kodi.</p><div class="actions"><a class="button" href="{{REPO_LINK}}">↓ Scarica repository</a><a class="button secondary" href="{{ADDON_LINK}}">ZIP addon</a></div><p class="version">StreamIt {{VERSION}} · Repository {{REPO_VERSION}}</p></div><div class="logo-card"><img src="repository.streamit/icon-{{VERSION}}.png" alt="Logo StreamIt By Ema"><p>MADE FOR YOUR SCREEN</p></div></section>\n\n<section class="install" id="installazione"><div class="section-head"><div><div class="eyebrow">Pronto in tre passaggi</div><h2>Portalo su Kodi.</h2></div><p>Usa il repository per ricevere gli aggiornamenti secondo le impostazioni di Kodi.</p></div><div class="source"><code id="source-url">{{BASE_URL}}</code><button type="button" id="copy">Copia URL</button></div><div class="status" id="copy-status" role="status" aria-live="polite"></div><ol class="steps"><li><strong>Aggiungi la sorgente</strong>In Gestione file → Aggiungi sorgente, incolla l’indirizzo qui sopra e chiamala StreamIt.</li><li><strong>Installa il repository</strong>Add-on → Installa da file ZIP → StreamIt → <a href="{{REPO_LINK}}">{{REPO_LINK}}</a>.</li><li><strong>Apri StreamIt</strong>Installa da repository → StreamIt Repository → Add-on video → StreamIt → Installa.</li></ol><p class="note">Se necessario, abilita le origini sconosciute nelle impostazioni di Kodi.</p></section>\n</main><footer><div class="wrap footer-inner"><span>StreamIt · By Ema</span><span>I proprietari di questo add-on non ospitano né distribuiscono nessuno dei contenuti visualizzabili tramite questo add-on né hanno alcuna affiliazione con i fornitori di contenuti.</span></div></footer>\n<script>document.getElementById(\'copy\').addEventListener(\'click\',async()=>{const status=document.getElementById(\'copy-status\');try{await navigator.clipboard.writeText(document.getElementById(\'source-url\').textContent);status.textContent=\'URL copiato.\'}catch(error){status.textContent=\'Seleziona e copia manualmente l’indirizzo qui sopra.\'}});</script>\n</body></html>\n'
    for key, value in {"BASE_URL": base_url + "/", "VERSION": addon.get("version"), "REPO_VERSION": repo.get("version"), "REPO_LINK": repo_zip.name, "ADDON_LINK": link, "ASSETS": addon.get("id") + "/resources/media/categories"}.items():
        page = page.replace("{{" + key + "}}", html.escape(value, quote=True))
    (output / "index.html").write_text(page, encoding="utf-8")
    shutil.copytree(source / "resources/media/categories", addon_dir / "resources/media/categories", dirs_exist_ok=True)
    for path in (repo_zip, addon_zip):
        with zipfile.ZipFile(path) as archive:
            assert archive.testzip() is None
    print('Repository generato:', output)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--base-url', required=True)
    parser.add_argument('--output', default='_site', type=Path)
    args = parser.parse_args()
    build(args.base_url, args.output)