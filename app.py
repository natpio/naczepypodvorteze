# app.py
import streamlit as st
import pandas as pd
import json, os, math
from v_i18n import TRANSLATIONS
from v_styles import apply_supreme_ui, load_vorteza_asset
from v_engine import VEngine
from v_visuals import render_3d_pro, get_pro_color

apply_supreme_ui()

if 'lang' not in st.session_state: st.session_state.lang = "PL"
if 'v_manifest' not in st.session_state: st.session_state.v_manifest = []
T = TRANSLATIONS[st.session_state.lang]

FLEET = {
    "TIR Mega 13.6m": {"max_w": 24000, "L": 1360, "W": 248, "H": 300, "ax": 3, "cab": 230},
    "TIR Standard 13.6m": {"max_w": 24000, "L": 1360, "W": 248, "H": 275, "ax": 3, "cab": 230},
    "Solo 9m Heavy": {"max_w": 9500, "L": 920, "W": 245, "H": 270, "ax": 2, "cab": 200}
}

# Sidebar
with st.sidebar:
    st.session_state.lang = st.radio("INTERFACE LANGUAGE", ["PL", "ENG", "DE", "ES"], horizontal=True)
    st.markdown(f"### 📡 {T['fleet']}")
    v_sel = st.selectbox(T['unit'], list(FLEET.keys()))
    veh = FLEET[v_sel]
    x_off = st.slider(T['offset'], 0, veh['L']-200, 0)
    
    st.divider()
    st.markdown(f"### 📐 {T['truss_calc']}")
    c1, c2 = st.columns(2)
    t2m = c1.number_input(T['truss_2m'], 0, 500, 0)
    t3m = c2.number_input(T['truss_3m'], 0, 500, 0)
    if st.button(T['add_truss'], type="secondary"):
        p2 = {"name": "truss cart 14x2", "length": 200, "width": 60, "height": 240, "weight": 420, "canStack": False, "allowRotation": True}
        p3 = {"name": "truss cart 14x3", "length": 300, "width": 60, "height": 240, "weight": 630, "canStack": False, "allowRotation": True}
        for _ in range(math.ceil(t2m/14)): st.session_state.v_manifest.append(p2.copy())
        for _ in range(math.ceil(t3m/14)): st.session_state.v_manifest.append(p3.copy())
        st.rerun()
    if st.button(T['purge']): st.session_state.v_manifest = []; st.rerun()

# Main Header
cl, cr = st.columns([5, 1])
with cl:
    logo = load_vorteza_asset('logo_vorteza.png')
    if logo: st.markdown(f'<img src="data:image/png;base64,{logo}" width="200">', unsafe_allow_html=True)
    else: st.markdown("<h1>VORTEZA STACK</h1>", unsafe_allow_html=True)

tab_p, tab_i = st.tabs([f"📊 {T['planner']}", f"📦 {T['inventory']}"])

with tab_p:
    if st.session_state.v_manifest:
        m1, m2, m3, m4 = st.columns(4)
        total_m = sum(float(u['weight']) for u in st.session_state.v_manifest)
        m1.metric(T['cases'], len(st.session_state.v_manifest))
        m2.metric(T['pcs'], sum(int(u.get('itemsPerCase', 1)) for u in st.session_state.v_manifest))
        m3.metric(T['weight'], f"{total_m} KG")
        m4.metric(T['util'], f"{(total_m/veh['max_w'])*100:.1f}%")

        rem = [dict(u) for u in st.session_state.v_manifest]
        fleet_res = []
        while rem:
            s, w, n, l = VEngine.pack(rem, veh, offset=x_off)
            if not s: break
            fleet_res.append({"s": s, "w": w, "l": l})
            rem = n

        for idx, truck in enumerate(fleet_res):
            st.markdown(f'<div class="v-tile-pro">', unsafe_allow_html=True)
            st.markdown(f"### MISSION UNIT #{idx+1} | {v_sel}")
            vc, dc = st.columns([2.8, 1])
            with vc:
                st.plotly_chart(render_3d_pro(veh, truck['s']), use_container_width=True)
                tm, tw = 0, 0
                for s_ in truck['s']:
                    for it in s_['items']: tm += (s_['x']+it['w_fit']/2)*it['weight']; tw += it['weight']
                cp = (tm/tw/veh['L'])*100 if tw > 0 else 0
                st.markdown(f"#### ⚖️ {T['cog']}")
                st.markdown(f'<div class="v-rail-track"><div class="v-cog-indicator" style="left:{cp}%;"></div></div><br>', unsafe_allow_html=True)
            with dc:
                st.markdown(f"**{T['kpi']}**")
                st.write(f"{T['ldm']}: **{truck['l']:.2f} m**")
                st.write(f"{T['weight']}: **{truck['w']} kg**")
                st.divider()
                st.markdown(f"**{T['manifest']}**")
                agg = pd.Series([it['name'] for s_box in truck['s'] for it in s_box['items']]).value_counts().reset_index()
                agg.columns = ['SKU', 'QTY']
                html = f'<table class="v-table-tactical"><tr><th>SKU</th><th>{T["qty"]}</th></tr>'
                for _, r in agg.iterrows():
                    html += f'<tr><td><span style="color:{get_pro_color(r["SKU"])}">■</span> {r["SKU"]}</td><td>{r["QTY"]}</td></tr>'
                st.markdown(html+'</table>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
    else: st.info("VORTEZA STACK: WAITING FOR MISSION DATA.")

with tab_i:
    st.markdown(f"### 📦 {T['inventory']}")
    # Dodaj tutaj obsługę pliku products.json jeśli go posiadasz
