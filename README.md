# Damona registry site

Source of <https://cokelaer.github.io/damona/>, a searchable registry of the
Singularity containers available through [Damona](https://github.com/cokelaer/damona).
This is the `gh-pages` branch; the Python package lives on `main`.

The page is a Jekyll site (theme `jekyll-theme-cayman`). At load time,
`assets/js/registry.js` fetches `damona/software/registry.yaml` from the `main`
branch and builds the tool list, stats and health checks in the browser. To
update the registry content, edit `registry.yaml` on `main`, not this branch.

## Layout

- `index.html`: page structure
- `assets/js/registry.js`: registry parsing, search, version details, charts
- `assets/css/style.scss`: styling
- `_layouts/default.html`, `_config.yml`: Jekyll layout and settings

## Run locally

Requires Ruby and Bundler. The site is served by GitHub Pages without a
`Gemfile`, so create one locally (do not commit it unless you want to):

```ruby
source "https://rubygems.org"
gem "github-pages", group: :jekyll_plugins
gem "webrick"
```

Then:

```bash
bundle install
bundle exec jekyll serve
```

Open <http://127.0.0.1:4000/damona/>. The `/damona/` prefix comes from
`baseurl` in `_config.yml`. Edits to files are rebuilt automatically;
`_config.yml` changes need a restart.

The registry is fetched from GitHub at runtime, so you need network access
even when serving locally.

## Deploy

Push to `gh-pages`. GitHub Pages rebuilds in a minute or two.

## FAQ

**I pushed a change but the live site looks half-updated. For example, new CSS but old behaviour.**
The browser has cached an old `registry.js` while fetching the new CSS. Hard-refresh
(Ctrl+Shift+R, or Cmd+Shift+R on macOS) or open the page in a private window.

**How do I get the container URL to use in a pipeline?**
Click a tool, then click a version. Two boxes appear: the `damona install tool:version`
command and, under "Use in your pipeline", the container download URL. Click a
box to copy its content.

**A version has no URL box.**
Its release in `registry.yaml` has no `download` field.

**The tool list says "Could not load registry".**
The browser could not fetch `registry.yaml` from `raw.githubusercontent.com`. Check
your network and that the file exists on `main`.

**`jekyll serve` fails with `cannot load such file -- webrick`.**
Ruby 3+ no longer bundles it. Add `gem "webrick"` to your `Gemfile`.

**Commit blocked with "No .pre-commit-config.yaml file was found".**
This branch has no pre-commit config but a global hook is installed. Commit with
`PRE_COMMIT_ALLOW_NO_CONFIG=1 git commit ...`.
