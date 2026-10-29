# Portfólio · Felipe H. Souza

Site estático do meu portfólio de IA, automação e dados. O HTML é gerado por um script Python
(`build.py`, só biblioteca padrão) a partir de arquivos JSON.

## Estrutura

```
content/
  site.json        nome, posicionamento, sobre, foto, contatos, "Como eu trabalho", stack
  projetos.json    projetos (cada um vira card + página própria)
  img/felipe.jpg   foto do topo
src/
  base.html        molde das páginas (cabeçalho, rodapé, SEO, Open Graph)
  styles.css       visual (modo claro e escuro automático)
  favicon.svg
build.py           gera tudo em dist/
.github/workflows/deploy.yml   build e deploy no GitHub Pages
```

## Editar o conteúdo

Edite só os arquivos em `content/`. Não precisa mexer em código.

- **Projeto novo:** copie um bloco em `projetos.json` e troque o `slug` (vira a URL, sem espaços nem acentos).
- **status:** `concluido`, `em-teste`, `em-andamento` ou `planejado`.
- **destaque:** `true` coloca o projeto nos cards grandes (use até 3).
- **publicar:** `false` esconde o projeto sem apagar.
- **resultado** e **contexto** vazios (`""`) não aparecem no site.
- Campos `_todo` e `_como_editar` são só anotações; o site ignora.

## Rodar localmente

Requer Python 3.10 ou superior.

```bash
py build.py --serve
```

Abra http://localhost:8000. Depois de editar algum arquivo, pare com Ctrl+C e rode de novo.
(No Linux/macOS use `python3` em vez de `py`.)

## Publicar no GitHub Pages (recomendado)

1. No GitHub, crie um repositório público chamado **`felipehsouza-dev.github.io`** (sem README).
   Com esse nome, o site fica em `https://felipehsouza-dev.github.io`.
2. Na pasta do projeto:
   ```bash
   git init -b main
   git add .
   git commit -m "Primeira versão do portfólio"
   git remote add origin https://github.com/felipehsouza-dev/felipehsouza-dev.github.io.git
   git push -u origin main
   ```
3. No repositório: **Settings → Pages → Build and deployment → Source: GitHub Actions**.
4. Abra a aba **Actions** e aguarde o workflow "Deploy no GitHub Pages" ficar verde
   (rode de novo se o primeiro falhou antes do passo 3). O link aparece no job `deploy`.
5. A partir daí, cada `git push` na `main` publica sozinho.

Se usar outro nome de repositório (ex.: `portfolio`), a URL vira
`https://felipehsouza-dev.github.io/portfolio` e é preciso atualizar `site_url` em `content/site.json`.

### Domínio próprio (opcional)

1. Compre o domínio e, em **Settings → Pages → Custom domain**, informe o domínio.
2. No provedor do domínio, crie os registros DNS que o GitHub indicar.
3. Atualize `site_url` em `content/site.json` e faça push.

## Alternativas

As duas usam o mesmo comando de build. Conecte o repositório do GitHub no painel e configure:

| | Cloudflare Pages | Vercel |
|---|---|---|
| Framework preset | None | Other |
| Build command | `python build.py` | `python3 build.py` |
| Output directory | `dist` | `dist` |

Depois do primeiro deploy, troque `site_url` em `content/site.json` pela URL gerada
(ex.: `https://nome.pages.dev` ou `https://nome.vercel.app`) e faça push de novo.

## Licença

O código (`build.py`, `src/`, `.github/`) está sob a [licença MIT](LICENSE).
O conteúdo de `content/` (textos, descrições dos projetos e foto) tem todos os direitos
reservados e não pode ser reutilizado sem permissão.
