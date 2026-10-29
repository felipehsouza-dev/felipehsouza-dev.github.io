"""Gera o site estático em dist/ a partir de content/*.json e src/.

Uso:
    py build.py            # gera dist/
    py build.py --serve    # gera e abre um servidor local em http://localhost:8000

Só usa a biblioteca padrão do Python.
"""

import datetime as dt
import functools
import html
import http.server
import json
import os
import shutil
import sys
from pathlib import Path
from string import Template
from urllib.parse import urlparse

ROOT = Path(__file__).parent
CONTENT = ROOT / "content"
SRC = ROOT / "src"
DIST = ROOT / "dist"

STATUS_LABEL = {
    "concluido": "Concluído",
    "em-teste": "Em teste",
    "em-andamento": "Em andamento",
    "planejado": "Planejado",
}


def esc(text):
    return html.escape(str(text), quote=True)


def load_json(name):
    with open(CONTENT / name, encoding="utf-8") as f:
        return json.load(f)


def status_badge(status):
    if status not in STATUS_LABEL:
        raise ValueError(f"Status desconhecido: {status!r}. Use: {', '.join(STATUS_LABEL)}")
    return f'<span class="status status-{status}">{STATUS_LABEL[status]}</span>'


def tags(items):
    lis = "".join(f'<li class="tag">{esc(t)}</li>' for t in items)
    return f'<ul class="tags" aria-label="Tecnologias">{lis}</ul>'


def project_href(root, p):
    return f"{root}projetos/{p['slug']}/"


# ---------- Página inicial ----------

def featured_card(p, root):
    points = "".join(f"<li>{esc(x)}</li>" for x in p["construi"][:3])
    result = f'<p class="result">{esc(p["resultado"])}</p>' if p.get("resultado") else ""
    return f"""
      <article class="card">
        <div class="meta-row">{status_badge(p["status"])}<span class="category">{esc(p["categoria"])}</span></div>
        <h3><a href="{project_href(root, p)}">{esc(p["titulo"])}</a></h3>
        <p class="summary">{esc(p["resumo"])}</p>
        <ul class="points">{points}</ul>
        {result}
        {tags(p["tecnologias"])}
        <span class="more" aria-hidden="true">Ver detalhes →</span>
      </article>"""


def project_row(p, root):
    return f"""
        <li class="project-row">
          <div>
            <h4><a href="{project_href(root, p)}">{esc(p["titulo"])}</a></h4>
            <p class="summary">{esc(p["resumo"])}</p>
          </div>
          <div class="side">
            <div class="meta-row">{status_badge(p["status"])}<span class="category">{esc(p["categoria"])}</span></div>
            {tags(p["tecnologias"])}
          </div>
        </li>"""


def contact_links(contatos):
    links = []
    if contatos.get("email"):
        links.append(f'<a class="btn btn-primary" href="mailto:{esc(contatos["email"])}">Enviar e-mail</a>')
    if contatos.get("linkedin"):
        links.append(f'<a class="btn btn-ghost" href="{esc(contatos["linkedin"])}" rel="me noopener">LinkedIn</a>')
    if contatos.get("github"):
        links.append(f'<a class="btn btn-ghost" href="{esc(contatos["github"])}" rel="me noopener">GitHub</a>')
    return "\n        ".join(links)


def home_main(site, projetos, root):
    destaques = [p for p in projetos if p["destaque"]]
    demais = [p for p in projetos if not p["destaque"]]
    focos = "".join(f"<li>{esc(f)}</li>" for f in site.get("focos", []))
    principles = "".join(
        f'<li><h3>{esc(i["titulo"])}</h3><p>{esc(i["texto"])}</p></li>' for i in site["como_trabalho"]
    )
    stack = "".join(
        f'<div><dt>{esc(g["grupo"])}</dt><dd>{tags(g["itens"])}</dd></div>' for g in site["stack"]
    )
    contatos = site["contatos"]
    email = f'<p class="contact-email">{esc(contatos["email"])}</p>' if contatos.get("email") else ""
    others = ""
    if demais:
        others = f"""
    <h3 class="others-title">Outros projetos</h3>
    <ul class="project-list">{"".join(project_row(p, root) for p in demais)}
    </ul>"""

    avatar = ""
    if site.get("avatar", {}).get("arquivo"):
        a = site["avatar"]
        avatar = (f'<img class="avatar" src="{root}assets/{esc(Path(a["arquivo"]).name)}" '
                  f'alt="{esc(a.get("alt", ""))}" width="240" height="240" fetchpriority="high">')

    return f"""
<section class="hero" aria-labelledby="hero-title">
  <div class="wrap hero-grid">
    {avatar}
    <div>
    <p class="kicker">Desenvolvedor Python · IA aplicada</p>
    <h1 id="hero-title">{esc(site["nome"])}</h1>
    <p class="lead">{esc(site["posicionamento"])}</p>
    <p class="about">{esc(site["sobre"])}</p>
    <ul class="focus-list" aria-label="Áreas de foco">{focos}</ul>
    <div class="actions">
      <a class="btn btn-primary" href="#projetos">Ver projetos</a>
      <a class="btn btn-ghost" href="#contato">Contato</a>
    </div>
    </div>
  </div>
</section>

<section id="projetos" aria-labelledby="projetos-title">
  <div class="wrap">
    <div class="section-head">
      <p class="kicker">Projetos</p>
      <h2 id="projetos-title" class="section-title">O que eu construí</h2>
      <p class="section-intro">Cada projeto mostra o problema, o que foi feito e o status atual. Projetos do trabalho são descritos sem dados reais.</p>
    </div>
    <div class="featured">{"".join(featured_card(p, root) for p in destaques)}
    </div>{others}
  </div>
</section>

<section id="como-trabalho" aria-labelledby="como-title">
  <div class="wrap">
    <div class="section-head">
      <p class="kicker">Método</p>
      <h2 id="como-title" class="section-title">Como eu trabalho com IA</h2>
    </div>
    <ol class="principles">{principles}</ol>
  </div>
</section>

<section id="stack" aria-labelledby="stack-title">
  <div class="wrap">
    <div class="section-head">
      <p class="kicker">Stack</p>
      <h2 id="stack-title" class="section-title">Ferramentas que uso</h2>
    </div>
    <dl class="stack">{stack}</dl>
  </div>
</section>

<section id="contato" aria-labelledby="contato-title">
  <div class="wrap">
    <div class="contact-box">
      <p class="kicker">Contato</p>
      <h2 id="contato-title" class="section-title">Vamos conversar sobre IA e automação</h2>
      <p class="section-intro">Aberto a vagas e projetos de agentes de IA, automação e desenvolvimento Python.</p>
      <div class="contact-links">
        {contact_links(contatos)}
      </div>
      {email}
    </div>
  </div>
</section>"""


# ---------- Página de projeto ----------

def project_main(p, prev_p, next_p, root):
    def section(title, body):
        return f"<h2>{title}</h2>{body}" if body else ""

    construi = "".join(f"<li>{esc(x)}</li>" for x in p["construi"])
    body = "".join([
        section("Problema", f"<p>{esc(p['problema'])}</p>" if p.get("problema") else ""),
        section("O que construí", f"<ul>{construi}</ul>" if p["construi"] else ""),
        section("Resultado", f"<p>{esc(p['resultado'])}</p>" if p.get("resultado") else ""),
    ])
    contexto = f'<p class="notice">{esc(p["contexto"])}</p>' if p.get("contexto") else ""

    pager = ""
    if prev_p:
        pager += f'<a href="{project_href(root, prev_p)}"><span>← Anterior</span>{esc(prev_p["titulo"])}</a>'
    if next_p:
        pager += f'<a class="next" href="{project_href(root, next_p)}"><span>Próximo →</span>{esc(next_p["titulo"])}</a>'

    return f"""
<article class="project-page">
  <div class="wrap">
    <nav class="crumbs" aria-label="Navegação"><a href="{root}#projetos">← Todos os projetos</a></nav>
    <div class="meta-row">{status_badge(p["status"])}<span class="category">{esc(p["categoria"])}</span></div>
    <h1>{esc(p["titulo"])}</h1>
    <p class="lead">{esc(p["resumo"])}</p>
    <div class="project-layout">
      <div class="prose">{body}{contexto}</div>
      <dl class="facts">
        <div><dt>Status</dt><dd>{status_badge(p["status"])}</dd></div>
        <div><dt>Tecnologias</dt><dd>{tags(p["tecnologias"])}</dd></div>
        <div><dt>Área</dt><dd>{esc(p["categoria"])}</dd></div>
      </dl>
    </div>
    <nav class="pager" aria-label="Outros projetos">{pager}</nav>
  </div>
</article>"""


# ---------- Montagem ----------

def person_jsonld(site, url):
    same_as = [site["contatos"][k] for k in ("github", "linkedin") if site["contatos"].get(k)]
    data = {
        "@context": "https://schema.org",
        "@type": "Person",
        "name": site["nome"],
        "url": url,
        "jobTitle": "Desenvolvedor Python",
        "sameAs": same_as,
    }
    return f'<script type="application/ld+json">{json.dumps(data, ensure_ascii=False)}</script>'


def render(base, site, *, root, url, title, description, main, og_type="website", head_extra=""):
    og_image = ""
    if site.get("avatar", {}).get("arquivo"):
        img_url = f'{site["site_url"].rstrip("/")}/assets/{Path(site["avatar"]["arquivo"]).name}'
        og_image = (f'<meta property="og:image" content="{esc(img_url)}">\n'
                    f'<meta property="og:image:alt" content="{esc(site["avatar"].get("alt", ""))}">')
    return base.substitute(
        og_image=og_image,
        lang=site["idioma"],
        title=esc(title),
        description=esc(description),
        url=esc(url),
        og_type=og_type,
        site_name=esc(site["nome"]),
        root=root,
        head_extra=head_extra,
        main=main,
        year=dt.date.today().year,
    )


def write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def clean_dist():
    # Apaga arquivos e tenta apagar pastas vazias. Pastas travadas (OneDrive,
    # Explorer aberto) ficam e são reaproveitadas no build.
    if not DIST.exists():
        return
    for path in sorted(DIST.rglob("*"), key=lambda x: len(x.parts), reverse=True):
        try:
            path.unlink() if path.is_file() else path.rmdir()
        except OSError:
            pass


def build():
    site = load_json("site.json")
    projetos = [p for p in load_json("projetos.json")["projetos"] if p.get("publicar", True)]
    base = Template((SRC / "base.html").read_text(encoding="utf-8"))
    site_url = site["site_url"].rstrip("/")
    base_path = urlparse(site_url).path.rstrip("/") + "/"

    clean_dist()
    (DIST / "assets").mkdir(parents=True, exist_ok=True)
    shutil.copy(SRC / "styles.css", DIST / "assets" / "styles.css")
    shutil.copy(SRC / "favicon.svg", DIST / "assets" / "favicon.svg")
    if site.get("avatar", {}).get("arquivo"):
        avatar = CONTENT / site["avatar"]["arquivo"]
        shutil.copy(avatar, DIST / "assets" / avatar.name)
    write(DIST / ".nojekyll", "")

    home_url = site_url + "/"
    write(DIST / "index.html", render(
        base, site, root="./", url=home_url,
        title=site["titulo_pagina"], description=site["descricao"],
        main=home_main(site, projetos, "./"),
        head_extra=person_jsonld(site, home_url),
    ))

    urls = [home_url]
    for i, p in enumerate(projetos):
        url = f"{site_url}/projetos/{p['slug']}/"
        urls.append(url)
        prev_p = projetos[i - 1] if i > 0 else None
        next_p = projetos[i + 1] if i + 1 < len(projetos) else None
        write(DIST / "projetos" / p["slug"] / "index.html", render(
            base, site, root="../../", url=url, og_type="article",
            title=f"{p['titulo']} · {site['nome']}", description=p["resumo"],
            main=project_main(p, prev_p, next_p, "../../"),
        ))

    # 404 usa caminho absoluto porque o GitHub Pages a serve em qualquer URL.
    write(DIST / "404.html", render(
        base, site, root=base_path, url=home_url,
        title=f"Página não encontrada · {site['nome']}", description=site["descricao"],
        main=f"""
<section class="not-found"><div class="wrap">
  <h1>Página não encontrada</h1>
  <p>O endereço pode ter mudado. Os projetos estão na página inicial.</p>
  <a class="btn btn-primary" href="{base_path}">Voltar ao início</a>
</div></section>""",
        head_extra='<meta name="robots" content="noindex">',
    ))

    today = dt.date.today().isoformat()
    entries = "".join(f"  <url><loc>{esc(u)}</loc><lastmod>{today}</lastmod></url>\n" for u in urls)
    write(DIST / "sitemap.xml",
          '<?xml version="1.0" encoding="UTF-8"?>\n'
          '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
          f"{entries}</urlset>\n")
    write(DIST / "robots.txt", f"User-agent: *\nAllow: /\n\nSitemap: {site_url}/sitemap.xml\n")

    print(f"Site gerado em {DIST} ({len(projetos)} projetos, {len(urls)} URLs no sitemap).")


def serve(port=8000):
    handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(DIST))
    with http.server.ThreadingHTTPServer(("127.0.0.1", port), handler) as httpd:
        print(f"Servindo em http://localhost:{port}  (Ctrl+C para parar)")
        httpd.serve_forever()


if __name__ == "__main__":
    build()
    if "--serve" in sys.argv:
        serve(int(os.environ.get("PORT", 8000)))
