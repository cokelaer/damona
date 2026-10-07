import jsyaml from "https://cdn.jsdelivr.net/npm/js-yaml@4.1.0/+esm";

const URL = "https://raw.githubusercontent.com/cokelaer/damona/refs/heads/main/damona/software/registry.yaml";
const $ = (s) => document.querySelector(s);
const tip = $("#tip");
const fmt = (b) => b >= 1e9 ? (b / 1e9).toFixed(1) + " GB" : b >= 1e6 ? Math.round(b / 1e6) + " MB" : Math.round(b / 1e3) + " KB";

function showTip(e, html) {
  tip.innerHTML = html; tip.style.opacity = 1;
  tip.style.left = Math.min(e.clientX + 12, innerWidth - 270) + "px"; tip.style.top = e.clientY + 14 + "px";
}
const hideTip = () => (tip.style.opacity = 0);
const esc = (s) => String(s).replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));

let tools = [], limit = 24;

function parse(reg) {
  return Object.entries(reg).map(([name, t]) => {
    const rel = Object.entries(t.releases || {}).map(([ver, r]) => ({
      ver: String(ver), size: r.filesize || 0, broken: !!r.broken, mislabelled: !!r.mislabelled, reason: r.reason || "",
      url: r.download || "", doi: r.doi || "", md5: r.md5sum || "", binaries: String(r.binaries || ""), mirrors: r.mirrors || {},
      get bad() { return this.broken || this.mislabelled; },
    }));
    return {
      name, binaries: String(t.binaries || t.binaires || [...new Set(rel.flatMap((r) => r.binaries.split(/\s+/)).filter(Boolean))].join(" ")), typoKey: "binaires" in t, rel,
      total: rel.reduce((a, r) => a + r.size, 0),
    };
  });
}

const badTip = (r) => r.broken ? "Marked broken in the registry" : `Mislabelled: ${r.reason || "see registry"}`;

function details(t) {
  const link = (u, txt) => `<a href="${esc(u)}" target="_blank" rel="noopener">${txt}</a>`;
  return `<table class="dt"><thead><tr><th>version</th><th>size</th><th>source</th><th>md5</th></tr></thead><tbody>` +
    t.rel.map((r) => {
      const src = [r.url.startsWith("http") ? link(r.url, "download") : esc(r.url || "–")]
        .concat(r.doi ? [link("https://doi.org/" + r.doi, "DOI")] : [])
        .concat(Object.entries(r.mirrors).map(([k, u]) => link(u, "mirror: " + esc(k)))).join(" · ");
      return `<tr${r.bad ? ` class="bad" data-tip="${esc(badTip(r))}"` : ""}><td>${esc(r.ver)}</td><td>${r.size ? fmt(r.size) : "–"}</td><td>${src}</td><td title="${esc(r.md5)}">${esc(r.md5.slice(0, 8)) || "–"}</td></tr>`;
    }).join("") + `</tbody></table>`;
}

/* ---------- search ---------- */
function render() {
  const q = $("#q").value.trim().toLowerCase();
  const terms = q.split(/\s+/).filter(Boolean);
  let rows = tools.filter((t) => terms.every((w) => (t.name + " " + t.binaries).toLowerCase().includes(w)));
  const s = $("#sort").value;
  rows.sort(s === "versions" ? (a, b) => b.rel.length - a.rel.length : s === "size" ? (a, b) => b.total - a.total : (a, b) => a.name.localeCompare(b.name));
  $("#count").textContent = `${rows.length} of ${tools.length} tools`;
  const more = rows.length - limit;
  $("#list").innerHTML = rows.length ? rows.slice(0, limit).map((t) => `
    <div class="tool" data-name="${esc(t.name)}">
      <h3 class="toggle" title="Show details">${esc(t.name)}<small>${t.rel.length} version${t.rel.length === 1 ? "" : "s"} · ${fmt(t.total)}</small></h3>
      <div class="bins" title="${esc(t.binaries)}">${esc(t.binaries) || "&nbsp;"}</div>
      <div class="vers">${t.rel.map((r) => `<span class="v${r.bad ? " bad" : ""}" data-v="${esc(r.ver)}"${r.bad ? ` data-tip="${esc(badTip(r))}"` : ""}>${esc(r.ver)}</span>`).join("")}</div>
      <div class="cmd"></div>
      <div class="det"></div>
    </div>`).join("") + (more > 0 ? `<button id="more" class="empty">Show ${more} more…</button>` : "") : `<div class="empty">No tool matches “${esc(q)}”.</div>`;
}

$("#list").addEventListener("click", (e) => {
  const h = e.target.closest(".toggle"), v = e.target.closest(".v"), c = e.target.closest(".cmd");
  if (h) {
    const card = h.closest(".tool"), det = card.querySelector(".det");
    if (!det.innerHTML) det.innerHTML = details(tools.find((t) => t.name === card.dataset.name));
    card.classList.toggle("open");
    return;
  }
  if (c) { navigator.clipboard?.writeText(c.textContent); c.dataset.old = c.textContent; c.textContent = "copied"; setTimeout(() => (c.textContent = c.dataset.old), 800); return; }
  if (!v) return;
  const card = v.closest(".tool"), cmd = card.querySelector(".cmd");
  cmd.textContent = `damona install ${card.dataset.name}:${v.dataset.v}`;
  cmd.classList.add("on");
});
$("#list").addEventListener("click", (e) => { if (e.target.id === "more") { limit = Infinity; render(); } });
$("#q").addEventListener("input", () => { limit = 24; render(); });
$("#sort").addEventListener("change", render);

/* ---------- stats ---------- */
function colChart(el, items, { w = 440, h = 200 }) {
  const m = { l: 30, b: 34, t: 16 }, max = Math.max(...items.map((i) => i.value));
  const bw = (w - m.l) / items.length;
  el.innerHTML = `<svg viewBox="0 0 ${w} ${h}" role="img"><line class="axis" x1="${m.l}" x2="${w}" y1="${h - m.b}" y2="${h - m.b}"/>` +
    items.map((it, i) => {
      const bh = (it.value / max) * (h - m.b - m.t), x = m.l + i * bw, y = h - m.b - bh;
      return `<g><rect class="mark" x="${x + 3}" y="${y}" width="${bw - 6}" height="${bh}" rx="3"/>
        <text class="val" x="${x + bw / 2}" y="${y - 4}" text-anchor="middle">${it.value}</text>
        <text x="${x + bw / 2}" y="${h - m.b + 16}" text-anchor="middle">${esc(it.label)}</text>
        <rect class="hit" x="${x}" y="${m.t}" width="${bw}" height="${h - m.b - m.t}" fill="transparent" data-tip="${esc(it.tip)}"/></g>`;
    }).join("") + `</svg>`;
}

function stats() {
  const all = tools.flatMap((t) => t.rel.map((r) => ({ ...r, tool: t.name })));
  const sized = all.filter((r) => r.size);
  const total = sized.reduce((a, r) => a + r.size, 0);
  const tiles = [
    [tools.length, "tools"], [all.length, "versions"], [(all.length / tools.length).toFixed(1), "versions / tool (avg)"],
    [fmt(total), "total image size"],
  ];
  const sorted = sized.map((r) => r.size).sort((a, b) => a - b);
  tiles.push([fmt(sorted[Math.floor(sorted.length / 2)]), "median image size"]);
  $("#tiles").innerHTML = tiles.map(([v, l]) => `<div class="tile"><b>${v}</b><span>${l}</span></div>`).join("");

  const tedges = [0, 50e6, 100e6, 250e6, 500e6, 1e9, 2e9, Infinity], tnames = ["<50MB", "100MB", "250MB", "500MB", "1GB", "2GB", ">2GB"];
  colChart($("#c-size"), tnames.map((n, i) => {
    const inBin = tools.filter((t) => t.total >= tedges[i] && t.total < tedges[i + 1]);
    const ex = [...inBin].sort((x, y) => y.total - x.total).slice(0, 5).map((t) => esc(t.name)).join(", ");
    return { label: n, value: inBin.length, tip: `${inBin.length} tools ${n.startsWith("<") || n.startsWith(">") ? n : "< " + n}${ex ? "<br>" + ex + (inBin.length > 5 ? ", …" : "") : ""}` };
  }), { w: 900, h: 220 });

  const vc = {}; tools.forEach((t) => (vc[t.rel.length] = (vc[t.rel.length] || 0) + 1));
  const vmax = Math.max(...Object.keys(vc).map(Number));
  const vitems = []; for (let n = 1; n <= Math.min(vmax, 9); n++) vitems.push({ label: String(n), value: vc[n] || 0, tip: `${vc[n] || 0} tools with ${n} version${n > 1 ? "s" : ""}` });
  if (vmax > 9) { const v = Object.entries(vc).filter(([n]) => n > 9).reduce((a, [, c]) => a + c, 0); vitems.push({ label: "10+", value: v, tip: `${v} tools with 10+ versions` }); }
  colChart($("#c-vers"), vitems, {});

  const edges = [0, 25e6, 50e6, 100e6, 250e6, 500e6, 1e9, Infinity], names = ["<25MB", "50MB", "100MB", "250MB", "500MB", "1GB", ">1GB"];
  const ditems = names.map((n, i) => {
    const c = sorted.filter((s) => s >= edges[i] && s < edges[i + 1]).length;
    return { label: n, value: c, tip: `${c} images ${n.startsWith("<") || n.startsWith(">") ? n : "< " + n}` };
  });
  colChart($("#c-dist"), ditems, {});
}

/* ---------- registry health ---------- */
function health() {
  const rels = tools.flatMap((t) => t.rel.map((r) => ({ ...r, tool: t.name, label: `${t.name}:${r.ver}`, bad: r.broken || r.mislabelled })));
  const byMd5 = {};
  rels.filter((r) => r.md5).forEach((r) => (byMd5[r.md5] = (byMd5[r.md5] || []).concat(r.label)));
  const dup = Object.values(byMd5).filter((l) => l.length > 1).flat();
  const checks = [
    ["Marked broken", "Versions flagged broken in the registry.", rels.filter((r) => r.broken).map((r) => r.label)],
    ["Mislabelled", "Versions whose key does not match the image content.", rels.filter((r) => r.mislabelled).map((r) => r.label)],
    ["Missing file size", "No filesize recorded, so the size stats ignore them.", rels.filter((r) => !r.size).map((r) => r.label)],
    ["Missing DOI", "No Zenodo DOI for this version.", rels.filter((r) => !r.doi).map((r) => r.label)],
    ["Not hosted on Zenodo", "Download URL is not a Zenodo file (for example docker://).", rels.filter((r) => !/zenodo\.org/.test(r.url)).map((r) => r.label)],
    ["Duplicate md5", "Several versions share the same image checksum.", dup],
    ["No binaries listed", "Tool entry without a binaries field.", tools.filter((t) => !t.binaries).map((t) => t.name)],
    ["Typo in field name", "Entry uses binaires instead of binaries.", tools.filter((t) => t.typoKey).map((t) => t.name)],
  ];
  const todo = checks.filter((c) => c[2].length).length;
  $("#health").innerHTML = `<p class="hsum">${todo ? `${todo} of ${checks.length} checks need attention` : "All checks pass"}</p>` +
    checks.map(([title, desc, items]) => `<details class="hc${items.length ? "" : " ok"}"${items.length ? "" : " open"}>
      <summary><span class="hi">${items.length ? "⚠" : "✓"}</span> ${esc(title)} <b>${items.length}</b></summary>
      <p>${esc(desc)}</p>${items.length ? `<div class="vers">${items.map((i) => `<span class="v static">${esc(i)}</span>`).join("")}</div>` : ""}
    </details>`).join("");
}

document.addEventListener("mousemove", (e) => {
  const t = e.target.closest?.("[data-tip]");
  t ? showTip(e, t.dataset.tip) : hideTip();
});

try {
  const res = await fetch(URL);
  if (!res.ok) throw new Error(res.status);
  tools = parse(jsyaml.load(await res.text()));
  render(); stats(); health();
} catch (err) {
  $("#list").innerHTML = `<div class="err">Could not load registry (${esc(err.message)}). Try again later.</div>`;
}
