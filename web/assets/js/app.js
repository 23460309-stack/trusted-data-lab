(function () {
  "use strict";
  var D = window.DATOS || {};
  var NS = "http://www.w3.org/2000/svg";
  var tip = document.getElementById("tip");
  var MESES = ["Ene","Feb","Mar","Abr","May","Jun","Jul","Ago","Sep","Oct","Nov","Dic"];

  // ---------- utilidades ----------
  function el(n, a, p) { var e = document.createElementNS(NS, n); for (var k in a) e.setAttribute(k, a[k]); if (p) p.appendChild(e); return e; }
  function css(v) { return "var(--" + v + ")"; }
  function fmt(x, d) { return x == null || isNaN(x) ? "–" : Number(x).toLocaleString("es-MX", { minimumFractionDigits: d, maximumFractionDigits: d }); }
  function col(rows, pred) { if (!rows || !rows.length) return null; var ks = Object.keys(rows[0]); for (var i = 0; i < ks.length; i++) if (pred(ks[i].toLowerCase())) return ks[i]; return null; }
  function num(v) { return typeof v === "number" ? v : null; }
  function mostrar(ev, html) { tip.textContent = html; tip.hidden = false; tip.style.left = Math.min(ev.clientX + 14, window.innerWidth - 200) + "px"; tip.style.top = (ev.clientY + 14) + "px"; }
  function ocultar() { tip.hidden = true; }
  function vacio(id, msg) { var c = document.getElementById(id); c.innerHTML = ""; var p = document.createElement("p"); p.className = "vacio"; p.textContent = msg; c.appendChild(p); }

  // ---------- preparar serie mensual ----------
  var oro = D.oro || [];
  var cFecha = col(oro, function (k) { return k === "fecha" || k === "mes" || k === "periodo" || k.indexOf("fecha") >= 0; });
  var cInpc = col(oro, function (k) { return k.indexOf("inpc") >= 0 && !/var|pct|infl|tasa|z_|zscore/.test(k); });
  var cFix = col(oro, function (k) { return /(^|_)fix($|_)|tipo_cambio|usd/.test(k) && !/var|pct|z_/.test(k); });
  var cVar = col(oro, function (k) { return /var.*(anual|yoy|12)|infl.*anual|anual.*(var|infl)/.test(k); });
  var serie = [];
  oro.forEach(function (r) {
    var f = String(r[cFecha] || "").slice(0, 7);
    if (!/^\d{4}-\d{2}$/.test(f)) return;
    serie.push({ f: f, inpc: num(r[cInpc]), fix: num(r[cFix]), v: cVar ? num(r[cVar]) : null });
  });
  serie.sort(function (a, b) { return a.f < b.f ? -1 : 1; });
  serie.forEach(function (s, i) {
    if (s.v == null && i >= 12 && s.inpc != null && serie[i - 12].inpc) s.v = (s.inpc / serie[i - 12].inpc - 1) * 100;
    s.m = i > 0 && s.inpc != null && serie[i - 1].inpc ? (s.inpc / serie[i - 1].inpc - 1) * 100 : null;
  });

  // ---------- gráfico de línea ----------
  function linea(id, datos, clave, color, dec, unidad) {
    var cont = document.getElementById(id); cont.innerHTML = "";
    var pts = datos.filter(function (d) { return d[clave] != null; });
    if (pts.length < 2) { vacio(id, "Sin datos suficientes para esta serie."); return; }
    var W = 560, H = 280, m = { l: 48, r: 14, t: 12, b: 28 };
    var ys = pts.map(function (d) { return d[clave]; });
    var mn = Math.min.apply(null, ys), mx = Math.max.apply(null, ys);
    if (mn === mx) { mn -= 1; mx += 1; }
    var pad = (mx - mn) * 0.08; mn -= pad; mx += pad;
    var sx = function (i) { return m.l + i * (W - m.l - m.r) / (pts.length - 1); };
    var sy = function (v) { return H - m.b - (v - mn) / (mx - mn) * (H - m.t - m.b); };
    var svg = el("svg", { viewBox: "0 0 " + W + " " + H, role: "img", tabindex: "0", "aria-label": "Gráfico de línea, " + pts.length + " puntos, de " + pts[0].f + " a " + pts[pts.length - 1].f }, cont);
    var ej = el("g", { "class": "ejes" }, svg);
    for (var t = 0; t <= 4; t++) {
      var v = mn + (mx - mn) * t / 4, y = sy(v);
      el("line", { x1: m.l, x2: W - m.r, y1: y, y2: y, stroke: css("rejilla"), "stroke-width": 1 }, ej);
      var tx = el("text", { x: m.l - 6, y: y + 4, "text-anchor": "end" }, ej); tx.textContent = fmt(v, dec);
    }
    el("line", { x1: m.l, x2: W - m.r, y1: H - m.b, y2: H - m.b, stroke: css("base"), "stroke-width": 1 }, ej);
    var n = Math.min(6, pts.length);
    for (var k = 0; k < n; k++) {
      var i = Math.round(k * (pts.length - 1) / (n - 1));
      var lb = el("text", { x: sx(i), y: H - 8, "text-anchor": k === 0 ? "start" : k === n - 1 ? "end" : "middle" }, ej);
      lb.textContent = pts[i].f;
    }
    var d = pts.map(function (p, i) { return (i ? "L" : "M") + sx(i).toFixed(1) + " " + sy(p[clave]).toFixed(1); }).join("");
    el("path", { d: d, fill: "none", stroke: css(color), "stroke-width": 2, "stroke-linejoin": "round", "stroke-linecap": "round" }, svg);
    var li = pts.length - 1;
    el("circle", { cx: sx(li), cy: sy(pts[li][clave]), r: 4, fill: css(color), stroke: css("sup"), "stroke-width": 2 }, svg);
    var cruz = el("line", { y1: m.t, y2: H - m.b, stroke: css("base"), "stroke-width": 1, visibility: "hidden" }, svg);
    var dot = el("circle", { r: 5, fill: css(color), stroke: css("sup"), "stroke-width": 2, visibility: "hidden" }, svg);
    var idx = li;
    function poner(i, ev) {
      idx = Math.max(0, Math.min(pts.length - 1, i));
      var x = sx(idx), y = sy(pts[idx][clave]);
      cruz.setAttribute("x1", x); cruz.setAttribute("x2", x); cruz.setAttribute("visibility", "visible");
      dot.setAttribute("cx", x); dot.setAttribute("cy", y); dot.setAttribute("visibility", "visible");
      var txt = pts[idx].f + ": " + fmt(pts[idx][clave], dec) + (unidad || "");
      if (ev) mostrar(ev, txt); else { var r = svg.getBoundingClientRect(); mostrar({ clientX: r.left + x / W * r.width, clientY: r.top + y / H * r.height }, txt); }
    }
    svg.addEventListener("mousemove", function (ev) {
      var r = svg.getBoundingClientRect(), x = (ev.clientX - r.left) / r.width * W;
      poner(Math.round((x - m.l) / (W - m.l - m.r) * (pts.length - 1)), ev);
    });
    svg.addEventListener("mouseleave", function () { cruz.setAttribute("visibility", "hidden"); dot.setAttribute("visibility", "hidden"); ocultar(); });
    svg.addEventListener("keydown", function (ev) {
      if (ev.key === "ArrowLeft") { poner(idx - 1); ev.preventDefault(); }
      if (ev.key === "ArrowRight") { poner(idx + 1); ev.preventDefault(); }
    });
    svg.addEventListener("blur", function () { ocultar(); });
  }

  // ---------- barras horizontales ----------
  function barras(id, items, color, dec, unidad) {
    var cont = document.getElementById(id); cont.innerHTML = "";
    if (!items.length) { vacio(id, "Sin datos."); return; }
    var W = 560, fila = 30, H = items.length * fila + 10, tope = 150;
    var mx = Math.max.apply(null, items.map(function (i) { return Math.abs(i.v); })) || 1;
    var svg = el("svg", { viewBox: "0 0 " + W + " " + H, role: "img", "aria-label": "Gráfico de barras" }, cont);
    items.forEach(function (it, i) {
      var y = i * fila + 4, w = Math.max(2, Math.abs(it.v) / mx * (W - tope - 60));
      var t = el("text", { x: tope - 8, y: y + 15, "text-anchor": "end", "class": "etq" }, svg); t.textContent = it.n;
      var r = el("rect", { x: tope, y: y + 3, width: w, height: 18, rx: 4, fill: css(color) }, svg);
      var v = el("text", { x: tope + w + 6, y: y + 16, "class": "etq" }, svg); v.textContent = fmt(it.v, dec);
      r.addEventListener("mousemove", function (ev) { mostrar(ev, it.n + ": " + fmt(it.v, dec) + (unidad || "")); });
      r.addEventListener("mouseleave", ocultar);
    });
  }

  // ---------- mapa ----------
  function mapa() {
    var G = D.municipios_geo, T = D.tiendas || [];
    if (!G || !G.features) { vacio("c-mapa", "Falta datos/plata/municipios_colima.geojson"); return; }
    var cLat = col(T, function (k) { return k === "lat" || k === "latitud" || k === "latitude"; });
    var cLon = col(T, function (k) { return k === "lon" || k === "lng" || k === "long" || k === "longitud" || k === "longitude"; });
    var cMun = col(T, function (k) { return k.indexOf("municipio") >= 0 || k === "nom_mun"; });
    var props = G.features[0].properties || {}, pk = null;
    Object.keys(props).forEach(function (k) { if (!pk && /nom|mun/i.test(k) && typeof props[k] === "string") pk = k; });
    var anillos = function (g) { return g.type === "Polygon" ? [g.coordinates] : g.coordinates; };
    var minx = 1e9, maxx = -1e9, miny = 1e9, maxy = -1e9;
    G.features.forEach(function (f) { anillos(f.geometry).forEach(function (p) { p[0].forEach(function (c) { minx = Math.min(minx, c[0]); maxx = Math.max(maxx, c[0]); miny = Math.min(miny, c[1]); maxy = Math.max(maxy, c[1]); }); }); });
    var k = Math.cos((miny + maxy) / 2 * Math.PI / 180), W = 560, H = Math.round(W * (maxy - miny) / ((maxx - minx) * k));
    H = Math.min(H, 520);
    var esc = Math.min(W / ((maxx - minx) * k), H / (maxy - miny));
    var px = function (lon) { return (lon - minx) * k * esc + 6; }, py = function (lat) { return (maxy - lat) * esc + 6; };
    var cuenta = {};
    T.forEach(function (t) { var m = cMun ? String(t[cMun]) : ""; cuenta[m] = (cuenta[m] || 0) + 1; });
    var cont = document.getElementById("c-mapa"); cont.innerHTML = "";
    var svg = el("svg", { viewBox: "0 0 " + (W + 12) + " " + (H + 12), role: "img", "aria-label": "Mapa de tiendas por municipio de Colima" }, cont);
    var mxc = Math.max.apply(null, Object.keys(cuenta).map(function (m) { return cuenta[m]; }).concat([1]));
    var rampa = ["s1", "s2", "s3", "s4", "s5"];
    G.features.forEach(function (f) {
      var nom = pk ? String(f.properties[pk]) : "", c = cuenta[nom] || 0;
      var d = anillos(f.geometry).map(function (p) { return p.map(function (r) { return r.map(function (q, i) { return (i ? "L" : "M") + px(q[0]).toFixed(1) + " " + py(q[1]).toFixed(1); }).join("") + "Z"; }).join(""); }).join("");
      var p = el("path", { d: d, fill: css(rampa[Math.min(4, Math.floor(c / mxc * 4.999))]), stroke: css("sup"), "stroke-width": 1.5, "fill-rule": "evenodd" }, svg);
      p.addEventListener("mousemove", function (ev) { mostrar(ev, nom + ": " + c + " tiendas"); });
      p.addEventListener("mouseleave", ocultar);
    });
    var n = 0;
    if (cLat && cLon) T.forEach(function (t) {
      if (typeof t[cLat] !== "number" || typeof t[cLon] !== "number") return; n++;
      el("circle", { cx: px(t[cLon]), cy: py(t[cLat]), r: 2.6, fill: css("c2"), stroke: css("sup"), "stroke-width": 1 }, svg);
    });
    document.getElementById("mapa-nota").textContent = "Puntos = " + n + " tiendas (OpenStreetMap). Color del municipio = número de tiendas.";
  }

  // ---------- ranking ----------
  function ranking() {
    var R = D.tiendas_municipio || [];
    var cM = col(R, function (k) { return k.indexOf("municipio") >= 0 || k === "nom_mun"; });
    var cN = col(R, function (k) { return /tiendas|total|conteo|n_|num|cantidad/.test(k) && !/pct|per|dens/.test(k); }) || col(R, function (k) { return k !== (cM || "").toLowerCase() && typeof R[0][k] === "number"; });
    var items = R.filter(function (r) { return typeof r[cN] === "number"; }).map(function (r) { return { n: String(r[cM]), v: r[cN] }; }).sort(function (a, b) { return b.v - a.v; });
    if (!items.length) { // respaldo: contar desde tiendas
      var T = D.tiendas || [], cm = col(T, function (k) { return k.indexOf("municipio") >= 0; }), c = {};
      T.forEach(function (t) { var m = String(t[cm]); c[m] = (c[m] || 0) + 1; });
      items = Object.keys(c).map(function (m) { return { n: m, v: c[m] }; }).sort(function (a, b) { return b.v - a.v; });
    }
    barras("c-rank", items, "c1", 0, " tiendas");
  }

  // ---------- estacionalidad ----------
  function estacionalidad() {
    var s = Array(12).fill(0), c = Array(12).fill(0);
    serie.forEach(function (p) { if (p.m != null) { var i = +p.f.slice(5) - 1; s[i] += p.m; c[i]++; } });
    var items = MESES.map(function (n, i) { return { n: n, v: c[i] ? s[i] / c[i] : 0 }; });
    if (!c.some(Boolean)) { vacio("c-est", "Sin datos."); return; }
    var cont = document.getElementById("c-est"); cont.innerHTML = "";
    var W = 560, H = 260, m = { l: 40, r: 10, t: 14, b: 26 };
    var mx = Math.max.apply(null, items.map(function (i) { return Math.abs(i.v); })) * 1.15 || 1;
    var cy = (H - m.t - m.b) / 2 + m.t, bw = (W - m.l - m.r) / 12;
    var svg = el("svg", { viewBox: "0 0 " + W + " " + H, role: "img", "aria-label": "Estacionalidad mensual" }, cont);
    el("line", { x1: m.l, x2: W - m.r, y1: cy, y2: cy, stroke: css("base") }, svg);
    var ej = el("g", { "class": "ejes" }, svg);
    [mx, -mx].forEach(function (v) { var t = el("text", { x: m.l - 6, y: cy - v / mx * (cy - m.t) + 4, "text-anchor": "end" }, ej); t.textContent = fmt(v, 2); });
    items.forEach(function (it, i) {
      var h = Math.abs(it.v) / mx * (cy - m.t), x = m.l + i * bw + bw * .2, y = it.v >= 0 ? cy - h : cy;
      var r = el("rect", { x: x, y: y, width: bw * .6, height: Math.max(1, h), rx: 3, fill: css("c1") }, svg);
      var t = el("text", { x: x + bw * .3, y: H - 8, "text-anchor": "middle" }, ej); t.textContent = it.n;
      r.addEventListener("mousemove", function (ev) { mostrar(ev, it.n + ": " + fmt(it.v, 2) + " %"); });
      r.addEventListener("mouseleave", ocultar);
    });
  }

  // ---------- tablas genéricas ----------
  function tabla(cont, rows, max) {
    if (!rows || !rows.length) { var p = document.createElement("p"); p.className = "vacio"; p.textContent = "Sin datos."; cont.appendChild(p); return; }
    var ks = Object.keys(rows[0]), t = document.createElement("table"), h = t.createTHead().insertRow();
    ks.forEach(function (k) { var th = document.createElement("th"); th.textContent = k; h.appendChild(th); });
    var b = t.createTBody();
    rows.slice(-max).forEach(function (r) { var tr = b.insertRow(); ks.forEach(function (k) { tr.insertCell().textContent = r[k] == null ? "" : r[k]; }); });
    cont.appendChild(t);
  }
  function calidad() {
    var cont = document.getElementById("calidad");
    [["Puerta de calidad (series económicas)", D.puerta], ["Puerta de calidad (OpenStreetMap)", D.puerta_osm], ["Linaje mensual (últimos registros)", D.linaje], ["Manifiesto de la capa Bronce", D.manifiesto]].forEach(function (x) {
      var d = document.createElement("div"), h = document.createElement("h3"), w = document.createElement("div");
      h.textContent = x[0]; w.className = "tabla-wrap"; d.appendChild(h); d.appendChild(w); cont.appendChild(d); tabla(w, x[1], 8);
    });
  }

  // ---------- KPIs y hero ----------
  function kpis() {
    var u = serie[serie.length - 1] || {}, ult = function (k) { for (var i = serie.length - 1; i >= 0; i--) if (serie[i][k] != null) return serie[i]; return {}; };
    var v = ult("v"), fx = ult("fix"), ip = ult("inpc");
    document.getElementById("hero-cifra").textContent = v.v != null ? fmt(v.v, 2) + " %" : "–";
    document.getElementById("hero-nota").textContent = v.f ? "Último dato disponible: " + v.f : "Sin datos de inflación todavía.";
    var T = D.tiendas || [], M = {}, cm = col(T, function (k) { return k.indexOf("municipio") >= 0; });
    T.forEach(function (t) { M[t[cm]] = 1; });
    var items = [[fmt(ip.inpc, 3), "INPC más reciente (" + (ip.f || "–") + ")"], [fmt(fx.fix, 2), "MXN por USD (" + (fx.f || "–") + ")"], [String(T.length), "Tiendas en OpenStreetMap"], [String(Object.keys(M).length), "Municipios con datos"], [String(serie.length), "Meses en la serie Oro"]];
    var c = document.getElementById("kpis");
    items.forEach(function (i) { var d = document.createElement("div"); d.className = "kpi"; var b = document.createElement("b"), s = document.createElement("span"); b.textContent = i[0]; s.textContent = i[1]; d.appendChild(b); d.appendChild(s); c.appendChild(d); });
  }

  // ---------- periodo ----------
  function dibujar(n) {
    var datos = n ? serie.slice(-n) : serie;
    linea("c-inpc", datos, "inpc", "c1", 2, "");
    linea("c-var", datos, "v", "c2", 2, " %");
    linea("c-fix", datos, "fix", "c3", 2, " MXN");
  }
  document.querySelectorAll(".filtros button").forEach(function (b) {
    b.addEventListener("click", function () {
      document.querySelectorAll(".filtros button").forEach(function (x) { x.setAttribute("aria-pressed", "false"); });
      b.setAttribute("aria-pressed", "true"); dibujar(+b.dataset.n);
    });
  });

  document.getElementById("generado").textContent = D.generado_utc ? "Datos generados: " + D.generado_utc : "";
  var tw = document.getElementById("tabla-oro"); tabla(tw, oro, 120);
  kpis(); dibujar(0); estacionalidad(); mapa(); ranking(); calidad();
})();