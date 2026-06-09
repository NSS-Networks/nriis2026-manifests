#!/usr/bin/env python3
"""
Trinergy 5G Dashboard — v4
- แสดง 5GC pods (default namespace) + OAI RAN pods (oai-ran namespace)
- รันเป็น systemd service
- เข้าถึงผ่าน http://dashboard.5g.local (Nginx reverse proxy)
"""
import subprocess
import re
from flask import Flask, render_template_string
from datetime import datetime

app = Flask(__name__)

HTML = """<!DOCTYPE html>
<html lang="th">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Trinergy 5G Dashboard v1.9</title>
<style>
* { box-sizing: border-box; margin: 0; padding: 0; }
body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: #f0f2f5; color: #1a1a1a; }

/* ── Header ── */
.header {
    background: #0f1923;
    color: white;
    padding: 0.9rem 2rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-bottom: 2px solid #1D9E75;
}
.header-left { display: flex; align-items: center; gap: 14px; }
.header h1 { font-size: 18px; font-weight: 500; letter-spacing: 0.02em; }
.version-tag {
    font-size: 10px; font-weight: 600; padding: 2px 7px;
    background: #1D9E75; color: white; border-radius: 4px;
    letter-spacing: 0.06em;
}
.header-right { display: flex; align-items: center; gap: 16px; }
.last-update { font-size: 12px; color: #aaa; display: flex; align-items: center; gap: 8px; }
.live-dot {
    width: 7px; height: 7px; border-radius: 50%;
    background: #1D9E75; display: inline-block;
    animation: blink 1.5s infinite;
}
@keyframes blink { 0%,100%{opacity:1} 50%{opacity:0.2} }
.refresh-btn {
    background: #1D9E75; color: white; border: none;
    padding: 5px 14px; border-radius: 6px; cursor: pointer; font-size: 12px;
}
.refresh-btn:hover { background: #0F6E56; }

/* ── Layout ── */
.container { max-width: 1440px; margin: 0 auto; padding: 1.25rem 1.5rem; }

/* ── Summary cards ── */
.summary { display: grid; grid-template-columns: repeat(5, 1fr); gap: 10px; margin-bottom: 1.25rem; }
.metric {
    background: white; border-radius: 10px; padding: 0.9rem 1.1rem;
    border: 1px solid #e4e4e4;
}
.metric-label { font-size: 12px; color: #666; margin-bottom: 5px; font-weight: 500; }
.metric-value { font-size: 26px; font-weight: 500; line-height: 1; }
.metric-value.green  { color: #0a7a50; }
.metric-value.teal   { color: #0F6E56; }
.metric-value.red    { color: #c0392b; }
.metric-value.amber  { color: #b7600a; }
.metric-value.blue   { color: #185FA5; }

/* ── Section ── */
.section {
    background: white; border-radius: 10px;
    border: 1px solid #e4e4e4; margin-bottom: 1.25rem; overflow: hidden;
}
.section-header {
    padding: 0.75rem 1.25rem;
    border-bottom: 1px solid #f0f0f0;
    font-size: 12px; font-weight: 700; color: #333;
    text-transform: uppercase; letter-spacing: 0.06em;
    background: #fafafa;
    display: flex; align-items: center; gap: 10px;
}
/* OAI section header มีสีต่างออกไป */
.section-header.oai {
    background: #f0fbf6;
    border-bottom-color: #c5ead8;
    color: #0a5c3b;
}
.ns-badge {
    font-size: 10px; font-weight: 600; padding: 2px 8px;
    border-radius: 999px; text-transform: none; letter-spacing: 0;
}
.ns-default { background: #E6F1FB; color: #185FA5; border: 1px solid #c5ddf5; }
.ns-oai     { background: #d4f5e5; color: #0a5c3b; border: 1px solid #9fdcc0; }

/* ── Pod grids ── */
.pods-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(195px, 1fr));
    gap: 1px; background: #ebebeb;
}
.oai-pods-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(230px, 1fr));
    gap: 1px; background: #c5ead8;
}

/* ── Pod card (5GC) ── */
.pod-card {
    background: white; padding: 0.9rem 1.1rem;
    border-left: 4px solid #e0e0e0;
}
.pod-card.Running            { border-left-color: #1D9E75; }
.pod-card.Pending            { border-left-color: #BA7517; }
.pod-card.Error              { border-left-color: #E24B4A; }
.pod-card.CrashLoopBackOff   { border-left-color: #E24B4A; }
.pod-card.Terminating        { border-left-color: #888; }
.pod-card.Unknown            { border-left-color: #aaa; }

/* ── Pod card (OAI RAN) ── */
.oai-pod-card {
    background: #f6fdf9; padding: 0.9rem 1.1rem;
    border-left: 4px solid #c5ead8;
}
.oai-pod-card.Running          { border-left-color: #1D9E75; }
.oai-pod-card.Pending          { border-left-color: #BA7517; }
.oai-pod-card.Error            { border-left-color: #E24B4A; }
.oai-pod-card.CrashLoopBackOff { border-left-color: #E24B4A; }
.oai-pod-card.Unknown          { border-left-color: #aaa; }

.pod-name {
    font-size: 12px; font-weight: 500; margin-bottom: 3px;
    white-space: nowrap; overflow: hidden; text-overflow: ellipsis; color: #111;
}
.pod-component {
    font-size: 11px; color: #555; margin-bottom: 7px;
    text-transform: uppercase; letter-spacing: 0.05em; font-weight: 600;
}
.oai-component { color: #0F6E56; }

.status-pill {
    display: inline-flex; align-items: center; gap: 4px;
    font-size: 11px; padding: 2px 8px; border-radius: 999px; font-weight: 600;
}
.status-pill.Running          { background: #c8f0e0; color: #065535; }
.status-pill.Pending          { background: #FAEEDA; color: #7a4500; }
.status-pill.Error            { background: #FCEBEB; color: #8b0000; }
.status-pill.CrashLoopBackOff { background: #FCEBEB; color: #8b0000; }
.status-pill.Terminating      { background: #f0f0f0; color: #555; }
.status-pill.Unknown          { background: #e8e8e8; color: #444; }
.dot { width: 5px; height: 5px; border-radius: 50%; background: currentColor; }

.pod-meta { font-size: 11px; color: #666; margin-top: 5px; line-height: 1.6; }
.pod-ip   { font-size: 10px; color: #999; font-family: 'SF Mono','Fira Mono',monospace; margin-top: 2px; }

/* ── Side-by-side: nodes + topology ── */
.nodes-topo-row {
    display: grid;
    grid-template-columns: 360px 1fr;
    gap: 12px;
    margin-bottom: 1.25rem;
    align-items: start;
}
/* ── Nodes ── */
.node-row {
    display: flex; align-items: center; gap: 14px;
    padding: 0.9rem 1.25rem; flex-wrap: wrap;
    border-bottom: 1px solid #f5f5f5;
}
.node-row:last-child { border-bottom: none; }
.node-dot { width: 9px; height: 9px; border-radius: 50%; background: #1D9E75; flex-shrink: 0; }
.node-dot.NotReady { background: #E24B4A; }
.node-name   { font-size: 14px; font-weight: 600; }
.node-detail { font-size: 11px; color: #999; margin-top: 2px; }
.badge {
    font-size: 11px; padding: 2px 8px; border-radius: 999px;
    background: #E6F1FB; color: #185FA5; border: 1px solid #c5ddf5;
}
.badge.oai  { background: #d4f5e5; color: #0a5c3b; border-color: #9fdcc0; }
.badge.role { background: #f0f0f0; color: #444; border: 1px solid #ddd; }

/* ── Services table ── */
table { width: 100%; border-collapse: collapse; font-size: 12px; }
th {
    text-align: left; padding: 7px 14px;
    color: #444; font-size: 11px; font-weight: 700;
    border-bottom: 1px solid #eee; background: #fafafa;
    text-transform: uppercase; letter-spacing: 0.05em;
}
td { padding: 7px 14px; border-bottom: 1px solid #f5f5f5; }
tr:last-child td { border-bottom: none; }
tr:hover td { background: #fafafa; }
.mono { font-family: 'SF Mono','Fira Mono',monospace; font-size: 11px; color: #444; }
.port-tag {
    display: inline-block; font-size: 10px;
    background: #f0f0f0; border-radius: 4px;
    padding: 1px 5px; margin: 1px; color: #555;
    font-family: 'SF Mono','Fira Mono',monospace;
}

/* ── Network Topology Diagram ── */
.topology-section {
    background: white; border-radius: 10px;
    border: 1px solid #e4e4e4; margin-bottom: 1.25rem; overflow: hidden;
}
.topology-body {
    padding: 1.5rem;
    overflow-x: auto;
}
.topo-canvas {
    position: relative;
    min-width: 900px;
    height: 520px;
}
.topo-canvas svg {
    position: absolute; top: 0; left: 0;
    width: 100%; height: 100%;
    pointer-events: none;
    overflow: visible;
}
/* Server labels */
.server-label {
    position: absolute;
    font-size: 10px; font-weight: 700; color: #888;
    text-transform: uppercase; letter-spacing: 0.08em;
    padding: 3px 10px; background: #f5f5f5; border-radius: 4px;
    border: 1px solid #e0e0e0;
}
/* Topo pod box */
.topo-pod {
    position: absolute;
    background: white;
    border: 1.5px solid #d0d0d0;
    border-radius: 8px;
    padding: 7px 10px;
    min-width: 88px;
    text-align: center;
    box-shadow: 0 1px 4px rgba(0,0,0,0.07);
    transition: box-shadow 0.2s;
}
.topo-pod:hover { box-shadow: 0 3px 12px rgba(0,0,0,0.13); }
.topo-pod .topo-pod-name {
    font-size: 12px; font-weight: 700; color: #111;
    margin-bottom: 5px; white-space: nowrap;
}
.topo-pod .topo-status {
    font-size: 10px; font-weight: 600;
    padding: 2px 7px; border-radius: 999px;
    display: inline-block;
}
.topo-status.Running  { background: #c8f0e0; color: #065535; }
.topo-status.Unknown  { background: #e8e8e8; color: #222; }
.topo-status.NotRunning { background: #FCEBEB; color: #8b0000; }
.topo-status.Pending  { background: #FAEEDA; color: #7a4500; }
/* Hardware box */
.topo-hw {
    position: absolute;
    background: #f7f7f7;
    border: 1.5px dashed #aaa;
    border-radius: 8px;
    padding: 7px 10px;
    min-width: 100px;
    text-align: center;
}
.topo-hw .topo-pod-name { font-size: 11px; font-weight: 700; color: #333; margin-bottom: 4px; }
.topo-hw .topo-hw-sub   { font-size: 9px; color: #888; }
/* Edge label */
.edge-label {
    position: absolute;
    font-size: 9px; font-weight: 700;
    padding: 1px 5px; border-radius: 4px;
    pointer-events: none;
    white-space: nowrap;
    border: 1px solid #ccc;
}
.edge-label.sbi   { color: #7c3aed; background: #f3e8ff; border-color: #ddd6fe; }
.edge-label.n2n3  { color: #185FA5; background: #E6F1FB; border-color: #c5ddf5; }
.edge-label.xn    { color: #0a5c3b; background: #d4f5e5; border-color: #9fdcc0; }
.edge-label.radio { color: #b7600a; background: #FEF3C7; border-color: #fcd34d; }

.badge.virtual { background: #f3e8ff; color: #6d28d9; border: 1px solid #ddd6fe; }
.topo-vnode {
    position: absolute;
    background: white;
    border: 1.5px solid #d0d0d0;
    border-radius: 8px;
    padding: 7px 10px;
    min-width: 88px;
    text-align: center;
    box-shadow: 0 1px 4px rgba(0,0,0,0.07);
}
.topo-vnode .topo-pod-name { font-size: 12px; font-weight: 700; color: #111; margin-bottom: 3px; }
.topo-vnode .topo-vnode-sub { font-size: 9px; color: #888; margin-bottom: 4px; }

/* ── Empty state ── */
.empty-state {
    padding: 2rem; text-align: center;
    color: #aaa; font-size: 13px;
}

/* ── Responsive ── */
@media (max-width: 768px) {
    .summary { grid-template-columns: repeat(3, 1fr); }
}
@media (max-width: 480px) {
    .summary { grid-template-columns: repeat(2, 1fr); }
}
</style>
<script>
let countdown = {{ refresh }};
function tick() {
    countdown--;
    const el = document.getElementById('timer');
    if (el) el.textContent = countdown + 's';
    if (countdown <= 0) location.reload();
    else setTimeout(tick, 1000);
}
setTimeout(tick, 1000);
</script>
</head>
<body>

<div class="header">
    <div class="header-left">
        <h1>Trinergy 5G Dashboard</h1>
        <span class="version-tag">v1.9</span>
    </div>
    <div class="header-right">
        <span class="last-update">
            <span class="live-dot"></span>
            รีเฟรชใน <span id="timer">{{ refresh }}s</span>
            &nbsp;·&nbsp; อัปเดต: {{ updated }}
        </span>
        <button class="refresh-btn" onclick="location.reload()">รีเฟรช ↻</button>
    </div>
</div>

<div class="container">

    <!-- Summary -->
    <div class="summary">
        <div class="metric">
            <div class="metric-label">Pods ทั้งหมด</div>
            <div class="metric-value">{{ stats.total }}</div>
        </div>
        <div class="metric">
            <div class="metric-label">Running</div>
            <div class="metric-value green">{{ stats.running }}</div>
        </div>
        <div class="metric">
            <div class="metric-label">OAI RAN Pods</div>
            <div class="metric-value teal">{{ stats.oai_total }}</div>
        </div>
        <div class="metric">
            <div class="metric-label">มีปัญหา</div>
            <div class="metric-value {% if stats.problem > 0 %}red{% endif %}">{{ stats.problem }}</div>
        </div>
        <div class="metric">
            <div class="metric-label">Services</div>
            <div class="metric-value blue">{{ stats.services }}</div>
        </div>
    </div>

    <!-- Nodes + Topology side by side -->
    <div class="nodes-topo-row">
    <div style="display:flex; flex-direction:column;"><!-- left column: nodes + legend -->

    <!-- Nodes (left) -->
    <div class="section" style="margin-bottom:0;">
        <div class="section-header">Nodes</div>
        {% for node in nodes %}
        <div class="node-row">
            <div class="node-dot {{ '' if (node.status == 'Ready' or node.is_virtual) else 'NotReady' }}"></div>
            <div>
                <div class="node-name">{{ node.name }}</div>
                <div class="node-detail">
                    {{ node.version }} &nbsp;·&nbsp; {{ node.age }}
                    {% if node.ip %}&nbsp;·&nbsp; {{ node.ip }}{% endif %}
                </div>
            </div>
            <span class="badge">{{ 'Ready' if node.is_virtual else node.status }}</span>
            {% for role in node.roles %}
            <span class="badge role">{{ role }}</span>
            {% endfor %}
            {% if node.is_oai %}
            <span class="badge oai">OAI RAN</span>
            {% endif %}
            {% if node.is_virtual %}
            <span class="badge virtual">DU-Kubelet</span>
            {% endif %}
        </div>
        {% endfor %}
    </div>

    <!-- Interface Legend (middle column) -->
    <div class="section" style="margin-bottom:0;">
        <div class="section-header">Interface Legend</div>
        <div style="padding: 0.5rem 0.8rem; font-size: 10px; line-height: 1.8; display: grid; grid-template-columns: 1fr 1fr; gap: 0 8px;">
            <div><span class="edge-label n2n3" style="position:static;display:inline-block;margin-right:6px;">N2</span> NGAP / SCTP</div>
            <div><span class="edge-label n2n3" style="position:static;display:inline-block;margin-right:6px;">N3</span> GTP-U / UDP</div>
            <div><span class="edge-label n2n3" style="position:static;display:inline-block;margin-right:6px;">N4</span> PFCP / UDP</div>
            <div><span class="edge-label sbi" style="position:static;display:inline-block;margin-right:6px;">N11</span> HTTP/2 SBI</div>
            <div><span class="edge-label sbi" style="position:static;display:inline-block;margin-right:6px;">Nnrf</span> HTTP/2 SBI</div>
            <div><span class="edge-label sbi" style="position:static;display:inline-block;margin-right:6px;">Nausf</span> HTTP/2 SBI</div>
            <div><span class="edge-label sbi" style="position:static;display:inline-block;margin-right:6px;">Nudr</span> HTTP/2 SBI</div>
            <div><span class="edge-label xn" style="position:static;display:inline-block;margin-right:6px;">E1</span> E1AP / SCTP</div>
            <div><span class="edge-label xn" style="position:static;display:inline-block;margin-right:6px;">F1-C</span> F1AP / SCTP</div>
            <div><span class="edge-label xn" style="position:static;display:inline-block;margin-right:6px;">F1-U</span> GTP-U / UDP</div>
            <div><span class="edge-label radio" style="position:static;display:inline-block;margin-right:6px;">CPRI</span> RF / CPRI</div>
            <div><span class="edge-label radio" style="position:static;display:inline-block;margin-right:6px;">eCPRI</span> O-RAN 7.2 / UDP</div>
            <div><span class="edge-label sbi" style="position:static;display:inline-block;margin-right:6px;">VK</span> V-Kubelet</div>
        </div>
    </div>
    <div class="section" style="flex:1; display:flex; align-items:center; justify-content:center; padding: 0.85rem 1rem; margin-bottom:0;">
        <div style="font-size:16px; font-weight:700; color:#1D9E75; letter-spacing:0.12em; animation: blink 2s ease-in-out infinite;">NRIIS-Project</div>
    </div>
    </div><!-- /left column -->
    <!-- Network Topology Diagram (right) -->
    <div class="topology-section" style="margin-bottom:0;">
        <div class="section-header">
            Network Topology Diagram
            <span class="ns-badge ns-default">5G Core ↔ RAN ↔ Radio</span>
        </div>
        <div class="topology-body">
            <div class="topo-canvas" id="topoCanvas">

                <!-- SVG lines layer -->
                <svg id="topoSvg" xmlns="http://www.w3.org/2000/svg"></svg>

                <!-- ── SERVER 1: Open5GS 5GC ── -->
                <div class="server-label" style="left:10px; top:0px;">Server 1 — Open5GS 5GC</div>

                {% set topo_5gc = [
                    ('AMF',    80,   60),
                    ('SMF',    80,  145),
                    ('UPF',    80,  230),
                    ('NRF',   240,   60),
                    ('AUSF',  240,  145),
                    ('UDM',   240,  230),
                    ('UDR',   240,  315),
                    ('PCF',   380,   60),
                    ('NSSF',  380,  145),
                    ('BSF',   380,  230),
                    ('SCP',   380,  315),
                    ('MONGODB',510,  145),
                ] %}

                {% for fn, lx, ly in topo_5gc %}
                    {% set pod_status = pod_status_map.get(fn, 'Unknown') %}
                    {% set css_status = pod_status if pod_status in ['Running','Unknown','Pending'] else 'NotRunning' %}
                    <div class="topo-pod" id="pod-{{ fn }}"
                         style="left:{{ lx }}px; top:{{ ly }}px;">
                        <div class="topo-pod-name">{{ fn }}</div>
                        <span class="topo-status {{ css_status }}">{{ pod_status }}</span>
                    </div>
                {% endfor %}

                <!-- ── SERVER 2: OAI RAN ── -->
                <div class="server-label" style="left:650px; top:0px;">Server 2 — OAI RAN</div>

                {% set topo_ran = [
                    ('CU-CP', 660,  60),
                    ('CU-UP', 660, 145),
                ] %}

                {% for fn, lx, ly in topo_ran %}
                    {% set pod_status = 'Running' %}
                    {% set css_status = 'Running' %}
                    <div class="topo-pod" id="pod-{{ fn }}"
                         style="left:{{ lx }}px; top:{{ ly }}px;">
                        <div class="topo-pod-name">{{ fn }}</div>
                        <span class="topo-status {{ css_status }}">{{ pod_status }}</span>
                    </div>
                {% endfor %}

                <!-- ── DU V-NODE (V-Kubelet) แทน DU block เดิม ── -->
                <div class="server-label" style="left:650px; top:222px; font-size:9px;">V-Kubelet</div>
                {% set du_vnode_status = 'Running' %}
                {% set du_vnode_css = 'Running' %}
                <div class="topo-vnode" id="pod-DU-VNODE" style="left:660px; top:248px;">
                    <div class="topo-pod-name">DU V-NODE</div>
                    <span class="topo-status {{ du_vnode_css }}">{{ du_vnode_status }}</span>
                </div>

                <!-- ── Radio Hardware ── -->
                <div class="topo-hw" id="hw-usrp" style="left:830px; top:145px;">
                    <div class="topo-pod-name">USRP B206mini</div>
                    <div class="topo-hw-sub" style="color:#065535; background:#c8f0e0; border-radius:999px; padding:1px 7px; font-weight:700; display:inline-block;">Running</div>
                </div>
                <div class="topo-hw" id="hw-airspan" style="left:830px; top:268px;">
                    <div class="topo-pod-name">gNB Airspan</div>
                    <div class="topo-hw-sub">AirSpeed 2900</div>
                </div>

            </div><!-- /topo-canvas -->
        </div>
    </div><!-- /topology-section -->
        </div>
    </div><!-- /nodes-topo-row -->

    <script>
    // ── Draw SVG edges after DOM ready ──
    (function() {
        function center(el) {
            var r = el.getBoundingClientRect();
            var cr = document.getElementById('topoCanvas').getBoundingClientRect();
            return { x: r.left - cr.left + r.width/2, y: r.top - cr.top + r.height/2 };
        }
        function rightOf(el) {
            var r = el.getBoundingClientRect();
            var cr = document.getElementById('topoCanvas').getBoundingClientRect();
            return { x: r.right - cr.left, y: r.top - cr.top + r.height/2 };
        }
        function leftOf(el) {
            var r = el.getBoundingClientRect();
            var cr = document.getElementById('topoCanvas').getBoundingClientRect();
            return { x: r.left - cr.left, y: r.top - cr.top + r.height/2 };
        }

        function drawLine(svg, canvas, fromEl, toEl, iface, cssClass, offset) {
            offset = offset || {x: 0, y: 0};
            cssClass = cssClass || 'n2n3';
            var color = {'sbi':'#9333ea','n2n3':'#185FA5','xn':'#0a5c3b','radio':'#b7600a'}[cssClass] || '#94a3b8';
            var a = rightOf(fromEl), b = leftOf(toEl);
            var mx = (a.x + b.x) / 2;
            var path = document.createElementNS('http://www.w3.org/2000/svg','path');
            path.setAttribute('d', 'M'+a.x+','+a.y+' C'+mx+','+a.y+' '+mx+','+b.y+' '+b.x+','+b.y);
            path.setAttribute('stroke', color);
            path.setAttribute('stroke-width', cssClass==='sbi'?'1.2':'1.8');
            path.setAttribute('fill', 'none');
            path.setAttribute('stroke-dasharray', cssClass==='sbi'?'3,3':'none');
            svg.appendChild(path);

            if (iface) {
                // วาง label เหนือเส้น ใกล้ต้นทาง ไม่บัง status
                var lx = a.x + (b.x - a.x) * 0.15 + offset.x;
                var ly = a.y + (b.y - a.y) * 0.15 - 14 + offset.y;
                var div = document.createElement('div');
                div.className = 'edge-label ' + cssClass;
                div.textContent = iface;
                div.style.left = lx + 'px';
                div.style.top  = ly + 'px';
                canvas.appendChild(div);
            }
        }

        window.addEventListener('load', function() {
            var svg    = document.getElementById('topoSvg');
            var canvas = document.getElementById('topoCanvas');

            var get = function(id) { return document.getElementById('pod-'+id); };
            var hw  = function(id) { return document.getElementById('hw-'+id); };

            var amf=get('AMF'), smf=get('SMF'), upf=get('UPF');
            var nrf=get('NRF'), ausf=get('AUSF'), udm=get('UDM'), udr=get('UDR');
            var pcf=get('PCF'), nssf=get('NSSF'), bsf=get('BSF'), scp=get('SCP');
            var mongodb=get('MONGODB');
            var cucp=get('CU-CP'), cuup=get('CU-UP'), cudu=get('DU');
            var duvnode=get('DU-VNODE');
            var usrp=hw('usrp'), airspan=hw('airspan');

            // ── SBI (HTTP/2) ──
            if (amf && nrf)     drawLine(svg,canvas,amf,  nrf,  'Nnrf', 'sbi',{x:0,y:-16});
            if (smf && nrf)     drawLine(svg,canvas,smf,  nrf,  'Nnrf', 'sbi',{x:0,y:6});
            if (amf && ausf)    drawLine(svg,canvas,amf,  ausf, 'Nausf','sbi',{x:0,y:16});
            if (amf && smf)     drawLine(svg,canvas,amf,  smf,  'N11',  'sbi',{x:20,y:0});
            if (udm && udr)     drawLine(svg,canvas,udm,  udr,  'Nudr', 'sbi',{x:0,y:0});
            if (pcf && nrf)     drawLine(svg,canvas,pcf,  nrf,  'Npcf', 'sbi',{x:0,y:0});
            if (scp && nrf)     drawLine(svg,canvas,scp,  nrf,  'Nscp', 'sbi',{x:0,y:6});
            if (mongodb && udr) drawLine(svg,canvas,mongodb,udr,'',     'sbi',{x:0,y:0});

            // ── N4 SMF→UPF ──
            if (smf && upf)    drawLine(svg,canvas,smf,  upf,  'N4',   'n2n3',{x:0,y:0});

            // ── N2 AMF→CU-CP ──
            if (amf && cucp)   drawLine(svg,canvas,amf,  cucp, 'N2',   'n2n3',{x:0,y:-10});

            // ── N3 UPF→CU-UP ──
            if (upf && cuup)   drawLine(svg,canvas,upf,  cuup, 'N3',   'n2n3',{x:0,y:0});

            // ── RAN internal CU-CP ↔ CU-UP ──
            if (cucp && cuup)  drawLine(svg,canvas,cucp, cuup, 'E1',   'xn',{x:0,y:0});

            // ── CU-CP/CU-UP → DU-VNODE ──
            if (cucp && duvnode) drawLine(svg,canvas,cucp, duvnode, 'F1-C', 'xn',{x:0,y:-10});
            if (cuup && duvnode) drawLine(svg,canvas,cuup, duvnode, 'F1-U', 'xn',{x:0,y:8});

            // ── Fronthaul DU-VNODE → Hardware ──
            if (duvnode && usrp)    drawLine(svg,canvas,duvnode,usrp,   'CPRI', 'radio',{x:0,y:-10});
            if (duvnode && airspan) drawLine(svg,canvas,duvnode,airspan,'eCPRI','radio',{x:0,y:10});
        });
    })();
    </script>

    <!-- 5GC Pods -->
    <div class="section">
        <div class="section-header">
            Network Functions (5GC Pods)
            <span class="ns-badge ns-default">namespace: open5gs</span>
        </div>
        {% if pods %}
        <div class="pods-grid">
            {% for pod in pods %}
            <div class="pod-card {{ pod.status }}">
                <div class="pod-component">{{ pod.component }}</div>
                <div class="pod-name" title="{{ pod.name }}">{{ pod.name }}</div>
                <span class="status-pill {{ pod.status }}">
                    <span class="dot"></span>{{ pod.status }}
                </span>
                <div class="pod-meta">
                    Ready: {{ pod.ready }} &nbsp;·&nbsp; Restarts: {{ pod.restarts }}
                    <br>Age: {{ pod.age }}
                </div>
            </div>
            {% endfor %}
        </div>
        {% else %}
        <div class="empty-state">ไม่พบ pods ใน namespace: default</div>
        {% endif %}
    </div>

    <!-- OAI RAN Pods -->
    <div class="section">
        <div class="section-header oai">
            OAI RAN Pods
            <span class="ns-badge ns-oai">namespace: oai-ran</span>
        </div>
        {% if oai_pods %}
        <div class="oai-pods-grid">
            {% for pod in oai_pods %}
            <div class="oai-pod-card {{ pod.status }}">
                <div class="pod-component oai-component">{{ pod.component }}</div>
                <div class="pod-name" title="{{ pod.name }}">{{ pod.name }}</div>
                <span class="status-pill {{ pod.status }}">
                    <span class="dot"></span>{{ pod.status }}
                </span>
                <div class="pod-meta">
                    Ready: {{ pod.ready }} &nbsp;·&nbsp; Restarts: {{ pod.restarts }}
                    <br>Age: {{ pod.age }}
                </div>
                {% if pod.ip %}
                <div class="pod-ip">{{ pod.ip }} &nbsp;·&nbsp; {{ pod.node }}</div>
                {% endif %}
            </div>
            {% endfor %}
        </div>
        {% else %}
        <div class="empty-state">
            ยังไม่พบ pods ใน namespace: oai-ran
            — ตรวจสอบว่า OAI node join cluster แล้ว
        </div>
        {% endif %}
    </div>

    <!-- Services -->
    <div class="section">
        <div class="section-header">
            Services
            <span class="ns-badge ns-default">open5gs</span>
            <span class="ns-badge ns-oai">oai-ran</span>
        </div>
        {% if services %}
        <table>
            <thead>
                <tr>
                    <th>Service</th>
                    <th>Namespace</th>
                    <th>Type</th>
                    <th>Cluster IP</th>
                    <th>Port(s)</th>
                </tr>
            </thead>
            <tbody>
            {% for svc in services %}
            <tr>
                <td>{{ svc.name }}</td>
                <td><span class="ns-badge {% if svc.namespace == 'oai-ran' %}ns-oai{% else %}ns-default{% endif %}">{{ svc.namespace }}</span></td>
                <td>{{ svc.type }}</td>
                <td class="mono">{{ svc.ip }}</td>
                <td>{% for p in svc.ports %}<span class="port-tag">{{ p }}</span>{% endfor %}</td>
            </tr>
            {% endfor %}
            </tbody>
        </table>
        {% else %}
        <div class="empty-state">ไม่พบ services</div>
        {% endif %}
    </div>

</div>
</body>
</html>
"""

# ─────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────

def run_kubectl(args: list[str]) -> str:
    try:
        result = subprocess.run(
            ["kubectl"] + args,
            capture_output=True, text=True, timeout=10
        )
        return result.stdout.strip()
    except Exception:
        return ""


def parse_component_name(pod_name: str, strip_prefix: str = "") -> str:
    """ตัด hash suffix ท้าย pod name แล้ว strip prefix ที่ระบุ"""
    name = re.sub(r'-[a-z0-9]{8,10}-[a-z0-9]{5}$', '', pod_name)
    if strip_prefix:
        name = name.replace(strip_prefix, "")
    return name.upper()


def get_pods(namespace: str = "open5gs") -> list[dict]:
    """ดึง pods จาก namespace ที่ระบุ (default = open5gs)"""
    args = ["get", "pods", "--no-headers", "-o", "wide", "-n", namespace]

    out = run_kubectl(args)
    pods = []
    for line in out.splitlines():
        parts = line.split()
        if len(parts) < 5:
            continue
        name     = parts[0]
        ready    = parts[1]
        status   = parts[2]
        restarts = parts[3]
        age      = parts[4]
        ip       = parts[5] if len(parts) > 5 else ""
        node     = parts[6] if len(parts) > 6 else ""

        if namespace == "oai-ran":
            component = parse_component_name(name, strip_prefix="oai-")
        else:
            component = parse_component_name(name, strip_prefix="open5gs-")


        pods.append({
            "name":     name,
            "component": component,
            "ready":    ready,
            "status":   status,
            "restarts": restarts,
            "age":      age,
            "ip":       ip if ip not in ("", "<none>") else "",
            "node":     node,
        })
    return pods


def get_network_interfaces() -> list[dict]:
    """ดึง IP และ interface ของแต่ละ node ผ่าน kubectl"""
    nodes = []
    try:
        out = subprocess.run(["ip", "-o", "addr", "show"], capture_output=True, text=True).stdout
        ifaces = []
        for line in out.splitlines():
            parts = line.split()
            if len(parts) < 4: continue
            iface = parts[1]
            if iface == "lo": continue
            family = parts[2]
            addr = parts[3].split("/")[0]
            ifaces.append({"iface": iface, "family": family, "ip": addr, "node": "open5gs-master"})
        nodes.extend(ifaces)
    except Exception as e:
        pass
    return nodes

def get_nodes() -> list[dict]:
    out = run_kubectl(["get", "nodes", "--no-headers", "-o", "wide"])
    nodes = []
    for line in out.splitlines():
        parts = line.split()
        if len(parts) < 5:
            continue
        name    = parts[0]
        status  = parts[1]
        roles_raw = parts[2]
        age     = parts[3]
        version = parts[4]
        ip      = parts[5] if len(parts) > 5 else ""
        roles = roles_raw.split(",") if roles_raw != "<none>" else ["worker"]

        nodes.append({
            "name":       name,
            "status":     status,
            "roles":      roles,
            "version":    version,
            "age":        age,
            "ip":         ip,
            "is_oai":     name == "trinergy-oai",
            "is_virtual": name == "du-vnode",
        })
    return nodes


def get_services() -> list[dict]:
    svcs = []
    for ns in ["open5gs", "oai-ran"]:
        out = run_kubectl(["get", "svc", "--no-headers", "-n", ns])
        for line in out.splitlines():
            parts = line.split()
            if len(parts) < 5:
                continue
            name = parts[0]
            if name == "kubernetes":
                continue
            svcs.append({
                "name":      name,
                "namespace": ns,
                "type":      parts[1],
                "ip":        parts[2],
                "ports":     parts[4].split(",") if len(parts) > 4 else [],
            })
    return svcs


# ─────────────────────────────────────────────
# Route
# ─────────────────────────────────────────────

@app.route("/")
def dashboard():
    pods     = get_pods(namespace="open5gs")
    oai_pods = get_pods(namespace="oai-ran")
    nodes    = get_nodes()
    services = get_services()
    ifaces   = get_network_interfaces()

    all_pods = pods + oai_pods
    stats = {
        "total":     len(all_pods),
        "running":   sum(1 for p in all_pods if p["status"] == "Running"),
        "oai_total": len(oai_pods),
        "problem":   sum(1 for p in all_pods if p["status"] != "Running"),
        "services":  len(services),
    }

    # สร้าง dict สำหรับ topology diagram: component -> status
    pod_status_map = {p["component"]: p["status"] for p in pods}
    oai_status_map = {p["component"]: p["status"] for p in oai_pods}
    # map oai-du-vnode → DU-VNODE สำหรับ topology
    for p in oai_pods:
        if p["name"] == "oai-du-vnode":
            oai_status_map["DU-VNODE"] = p["status"]

    return render_template_string(
        HTML,
        pods=pods,
        oai_pods=oai_pods,
        nodes=nodes,
        services=services,
        stats=stats,
        ifaces=ifaces,
        updated=datetime.now().strftime("%H:%M:%S"),
        refresh=30,
        pod_status_map=pod_status_map,
        oai_status_map=oai_status_map,
    )


if __name__ == "__main__":
    print("Trinergy 5G Dashboard v1.9 — http://0.0.0.0:8085")
    app.run(host="0.0.0.0", port=8085, debug=False)
