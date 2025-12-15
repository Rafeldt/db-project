<!-- templates/db_visualization/index.html -->
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width,initial-scale=1" />
  <title>Database Visualization</title>

  <!-- D3 -->
  <script src="https://cdn.jsdelivr.net/npm/d3@7"></script>

  <style>
    :root {
      --bg: #0b0f17;
      --panel: rgba(255,255,255,.06);
      --panel2: rgba(255,255,255,.10);
      --text: rgba(255,255,255,.90);
      --muted: rgba(255,255,255,.65);
      --hair: rgba(255,255,255,.16);
      --link: rgba(255,255,255,.18);
      --link-hi: rgba(255,255,255,.75);
      --node: rgba(255,255,255,.55);
      --node-hi: rgba(255,255,255,.95);
      --danger: #ff6b6b;
    }

    html, body { height: 100%; }
    body {
      margin: 0;
      background: radial-gradient(1200px 800px at 20% 15%, rgba(120,140,255,.15), transparent 60%),
                  radial-gradient(900px 700px at 80% 30%, rgba(80,255,190,.08), transparent 55%),
                  var(--bg);
      color: var(--text);
      font-family: ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial, "Apple Color Emoji","Segoe UI Emoji";
      overflow: hidden;
    }

    header {
      position: absolute;
      top: 14px;
      left: 14px;
      right: 14px;
      display: flex;
      gap: 10px;
      align-items: center;
      justify-content: space-between;
      pointer-events: none; /* let svg still pan/zoom */
      z-index: 10;
    }

    .panel {
      pointer-events: auto;
      display: flex;
      gap: 10px;
      align-items: center;
      padding: 10px 12px;
      border: 1px solid var(--hair);
      background: var(--panel);
      border-radius: 14px;
      backdrop-filter: blur(10px);
      box-shadow: 0 10px 40px rgba(0,0,0,.35);
      max-width: min(920px, calc(100vw - 28px));
    }

    .title {
      font-weight: 650;
      letter-spacing: .2px;
      white-space: nowrap;
    }

    .meta {
      color: var(--muted);
      font-size: 13px;
      white-space: nowrap;
    }

    .controls {
      display: flex;
      gap: 10px;
      align-items: center;
      flex-wrap: wrap;
    }

    input[type="search"]{
      width: min(340px, 60vw);
      padding: 8px 10px;
      border-radius: 10px;
      border: 1px solid var(--hair);
      background: rgba(0,0,0,.25);
      color: var(--text);
      outline: none;
    }
    input[type="search"]::placeholder { color: rgba(255,255,255,.45); }

    button {
      padding: 8px 10px;
      border-radius: 10px;
      border: 1px solid var(--hair);
      background: rgba(255,255,255,.08);
      color: var(--text);
      cursor: pointer;
    }
    button:hover { background: rgba(255,255,255,.12); }
    button:active { transform: translateY(1px); }

    .hint {
      position: absolute;
      bottom: 12px;
      left: 14px;
      right: 14px;
      display: flex;
      justify-content: space-between;
      gap: 10px;
      z-index: 10;
      pointer-events: none;
    }
    .hint .panel { pointer-events: auto; }
    .small { font-size: 12px; color: var(--muted); }

    /* D3 styling */
    svg { width: 100vw; height: 100vh; display: block; }

    .link {
      fill: none;
      stroke: var(--link);
      stroke-width: 1;
      pointer-events: none;
    }
    .link.is-active {
      stroke: var(--link-hi);
      stroke-width: 1.6;
    }

    .node circle {
      r: 2.4;
      fill: var(--node);
    }
    .node.is-active circle,
    .node.is-match circle {
      fill: var(--node-hi);
      r: 3.2;
    }
    .node.is-dim circle { opacity: .18; }

    .label {
      font-size: 10px;
      fill: rgba(255,255,255,.70);
      user-select: none;
    }
    .node.is-active .label,
    .node.is-match .label {
      fill: rgba(255,255,255,.95);
      font-weight: 650;
    }
    .node.is-dim .label { opacity: .15; }

    .tooltip {
      position: absolute;
      pointer-events: none;
      padding: 10px 12px;
      background: rgba(0,0,0,.65);
      border: 1px solid rgba(255,255,255,.18);
      border-radius: 12px;
      backdrop-filter: blur(10px);
      color: var(--text);
      font-size: 12px;
      max-width: 360px;
      box-shadow: 0 12px 45px rgba(0,0,0,.45);
      opacity: 0;
      transform: translateY(4px);
      transition: opacity .12s ease, transform .12s ease;
      z-index: 20;
    }
    .tooltip strong { font-weight: 700; }
    .tooltip .muted { color: rgba(255,255,255,.7); }

    .error {
      color: var(--danger);
      font-weight: 650;
    }
  </style>
</head>

<body>
  <header>
    <div class="panel" style="flex:1; min-width: 280px;">
      <div style="display:flex; flex-direction:column; gap:2px;">
        <div class="title">Database Visualization</div>
        <div id="status" class="meta">Loading…</div>
      </div>
    </div>

    <div class="panel controls">
      <input id="search" type="search" placeholder="Search (e.g. users:12 or :12 or users)" />
      <button id="reset">Reset view</button>
      <button id="clear">Clear highlight</button>
    </div>
  </header>

  <svg id="viz" role="img" aria-label="Database visualization"></svg>
  <div id="tooltip" class="tooltip"></div>

  <div class="hint">
    <div class="panel small">
      Drag to pan • Scroll to zoom • Hover a row to highlight its cross-table references • Click to lock/unlock selection
    </div>
    <div class="panel small">
      Tip: This page expects <code>/api/db-visualization</code> to return <code>{ tree, links }</code>
    </div>
  </div>

  <script>
    const svg = d3.select("#viz");
    const tooltip = d3.select("#tooltip");
    const statusEl = document.getElementById("status");
    const searchEl = document.getElementById("search");
    const resetBtn = document.getElementById("reset");
    const clearBtn = document.getElementById("clear");

    const W = () => window.innerWidth;
    const H = () => window.innerHeight;

    let g, linkSel, nodeSel, labelSel;
    let zoomBehavior;
    let lockedId = null;

    function setStatus(html) {
      statusEl.innerHTML = html;
    }

    function showTooltip(evt, html) {
      tooltip.html(html);
      const pad = 12;
      const x = Math.min(evt.clientX + 12, window.innerWidth - 380);
      const y = Math.min(evt.clientY + 12, window.innerHeight - 140);
      tooltip
        .style("left", x + "px")
        .style("top", y + "px")
        .style("opacity", 1)
        .style("transform", "translateY(0px)");
    }

    function hideTooltip() {
      tooltip
        .style("opacity", 0)
        .style("transform", "translateY(4px)");
    }

    function safeText(s) {
      return (s == null) ? "" : String(s)
        .replaceAll("&","&amp;")
        .replaceAll("<","&lt;")
        .replaceAll(">","&gt;")
        .replaceAll('"',"&quot;")
        .replaceAll("'","&#039;");
    }

    function initZoom() {
      zoomBehavior = d3.zoom()
        .scaleExtent([0.35, 6])
        .on("zoom", (event) => g.attr("transform", event.transform));

      svg.call(zoomBehavior);
    }

    function resetView() {
      svg.transition().duration(300).call(zoomBehavior.transform, d3.zoomIdentity);
    }

    function buildAdjacency(validLinks) {
      // Map: leafId -> Set(connectedLeafId)
      const adj = new Map();
      const add = (a, b) => {
        if (!adj.has(a)) adj.set(a, new Set());
        adj.get(a).add(b);
      };
      for (const l of validLinks) {
        add(l.sourceId, l.targetId);
        add(l.targetId, l.sourceId);
      }
      return adj;
    }

    function clearHighlight() {
      lockedId = null;
      nodeSel.classed("is-active", false).classed("is-dim", false);
      linkSel.classed("is-active", false);
    }

    function applyHighlight(id, adj) {
      // Highlight id + its neighbors + incident links, dim everything else
      const neighbors = adj.get(id) || new Set();

      nodeSel
        .classed("is-active", d => d.data.id === id || neighbors.has(d.data.id))
        .classed("is-dim", d => !(d.data.id === id || neighbors.has(d.data.id)));

      linkSel.classed("is-active", d => d.sourceId === id || d.targetId === id);
    }

    function applySearchMatch(query) {
      const q = query.trim().toLowerCase();
      nodeSel.classed("is-match", false);
      if (!q) return;

      nodeSel.classed("is-match", d => {
        const id = (d.data.id || "").toLowerCase();
        const t = (d.data.table || "").toLowerCase();
        const pk = String(d.data.pk ?? "").toLowerCase();

        // Allow quick patterns:
        // - "table:12" matches full id
        // - ":12" matches any pk
        // - "table" matches table name
        return id.includes(q) || t.includes(q) || (q.startsWith(":") && pk === q.slice(1));
      });
    }

    function resizeViewBox() {
      svg.attr("viewBox", [ -W()/2, -H()/2, W(), H() ]);
    }

    function buildViz(tree, links) {
      svg.selectAll("*").remove();
      resizeViewBox();

      g = svg.append("g");

      initZoom();
      resetView();

      // Cluster layout (radial)
      const radius = Math.min(W(), H()) * 0.42;
      const root = d3.hierarchy(tree, d => d.children);

      d3.cluster().size([2 * Math.PI, radius])(root);

      const leaves = root.leaves();
      const leafById = new Map(leaves.map(d => [d.data.id, d]));

      const validLinks = links
        .map(l => {
          const s = leafById.get(l.source);
          const t = leafById.get(l.target);
          if (!s || !t) return null;
          return {
            source: s,
            target: t,
            sourceId: l.source,
            targetId: l.target,
            meta: l
          };
        })
        .filter(Boolean);

      const adj = buildAdjacency(validLinks);

      const line = d3.lineRadial()
        .curve(d3.curveBundle.beta(0.85))
        .radius(d => d.y)
        .angle(d => d.x);

      // Links
      linkSel = g.append("g")
        .attr("stroke-linecap", "round")
        .selectAll("path")
        .data(validLinks)
        .join("path")
        .attr("class", "link")
        .attr("d", d => line(d.source.path(d.target)));

      // Nodes (leaves only)
      nodeSel = g.append("g")
        .selectAll("g")
        .data(leaves)
        .join("g")
        .attr("class", "node")
        .attr("transform", d => {
          const a = d.x - Math.PI / 2;
          return `rotate(${(a * 180 / Math.PI)}) translate(${d.y},0)`;
        });

      nodeSel.append("circle");

      // Labels
      labelSel = nodeSel.append("text")
        .attr("class", "label")
        .attr("dy", "0.31em")
        .attr("x", d => (d.x < Math.PI ? 6 : -6))
        .attr("text-anchor", d => (d.x < Math.PI ? "start" : "end"))
        .attr("transform", d => (d.x < Math.PI ? null : "rotate(180)"))
        .text(d => {
          // show "table:pk" compactly
          const t = d.data.table ?? "";
          const pk = d.data.pk ?? d.data.name ?? "";
          return `${t}:${pk}`;
        });

      // Interaction
      nodeSel
        .on("mousemove", (event, d) => {
          const id = d.data.id;
          const neighbors = adj.get(id) || new Set();
          const deg = neighbors.size;

          showTooltip(event, `
            <div><strong>${safeText(d.data.id)}</strong></div>
            <div class="muted">table: <strong>${safeText(d.data.table)}</strong> • pk: <strong>${safeText(d.data.pk)}</strong></div>
            <div class="muted">cross-table connections: <strong>${deg}</strong></div>
            ${lockedId ? `<div class="muted">(selection locked — click node to unlock)</div>` : ``}
          `);
        })
        .on("mouseleave", () => {
          hideTooltip();
          if (!lockedId) clearHighlight();
        })
        .on("mouseenter", (event, d) => {
          if (lockedId) return;
          applyHighlight(d.data.id, adj);
        })
        .on("click", (event, d) => {
          const id = d.data.id;
          if (lockedId === id) {
            lockedId = null;
            clearHighlight();
          } else {
            lockedId = id;
            applyHighlight(id, adj);
          }
        });

      // Controls
      resetBtn.onclick = () => resetView();
      clearBtn.onclick = () => { clearHighlight(); applySearchMatch(searchEl.value); };

      searchEl.addEventListener("input", () => {
        applySearchMatch(searchEl.value);
      });

      // Helpful stats
      const tableCount = (tree.children || []).length;
      setStatus(
        `Schema: <strong>${safeText(tree.name || "db")}</strong> • ` +
        `Tables: <strong>${tableCount}</strong> • ` +
        `Rows (leaf nodes): <strong>${leaves.length}</strong> • ` +
        `Cross-table edges: <strong>${validLinks.length}</strong>`
      );

      // Keep view responsive
      window.addEventListener("resize", () => {
        resizeViewBox();
      }, { passive: true });
    }

    // Load from your Flask endpoint
    fetch("/api/db-visualization")
      .then(r => {
        if (!r.ok) throw new Error("HTTP " + r.status);
        return r.json();
      })
      .then(data => {
        if (!data || !data.tree || !data.links) {
          throw new Error("Response must be { tree, links }");
        }
        buildViz(data.tree, data.links);
      })
      .catch(err => {
        setStatus(`<span class="error">Failed to load:</span> ${safeText(err.message)}`);
        console.error(err);
      });
  </script>
</body>
</html>
