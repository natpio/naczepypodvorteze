# app.py
import streamlit as st
import pandas as pd
import json, os, math
from v_i18n import TRANSLATIONS
from v_styles import apply_supreme_ui, load_vorteza_b64
from v_engine import VEngine
from v_visuals import render_3d, get_v_color

apply_supreme_ui()

if 'lang' not in st.session_state: st.session_state.lang = "PL"
if 'manifest' not in st.session_state: st.session_state.manifest = []
T = TRANSLATIONS[st.session_state.lang]

# Flota
FLEET = {
    "TIR FTL Mega 13.6m": {"max_w": 24000, "L": 1360, "W": 248, "H": 300, "ax": 3, "cab": 230},
    "Solo 9m Heavy": {"max_w": 9500, "L": 920, "W": 245, "H": 270, "ax": 2, "cab": 200}
}

# Sidebar
with st.sidebar:
    st.session_state.lang = st.radio("JĘZYK / LANGUAGE", ["PL", "ENG", "DE", "ES"], horizontal=True)
    st.markdown(f"### 📡 {T['fleet']}")
    v_sel = st.selectbox(T['unit'], list(FLEET.keys()))
    veh = FLEET[v_sel]
    x_off = st.slider(T['offset'], 0, veh['L']-200, 0)
    
    st.divider()
    st.markdown(f"### 📐 {T['truss_calc']}")
    t2m = st.number_input(T['truss_2m'], 0, 500, 0)
    if st.button(T['add_truss']):
        p2 = {"name": "truss cart 14x2", "length": 200, "width": 60, "height": 240, "weight": 420, "canStack": False, "allowRotation": True}
        for _ in range(math.ceil(t2m/14)): st.session_state.manifest.append(p2.copy())
        st.rerun()

# Główny ekran
st.markdown(f"<h1>VORTEZA STACK</h1>", unsafe_allow_html=True)
tab_p, tab_i = st.tabs([f"📊 {T['planner']}", f"📦 {T['inventory']}"])

with tab_p:
    if st.session_state.manifest:
        s, w, n, l = VEngine.pack(st.session_state.manifest, veh, offset=x_off)
        st.markdown('<div class="v-tile-pro">', unsafe_allow_html=True)
        st.plotly_chart(render_3d(veh, s), use_container_width=True)
        
        # Balans Masy
        tm, tw = 0, 0
        for st_ in s:
            for it in st_['items']: tm += (st_['x']+it['w_fit']/2)*it['weight']; tw += it['weight']
        cp = (tm/tw/veh['L'])*100 if tw > 0 else 0
        st.markdown(f'<div class="v-rail-track"><div class="v-cog-indicator" style="left:{cp}%;"></div></div>', unsafe_allow_html=True)
        
        # Tabela
        agg = pd.Series([u['name'] for s_ in s for u in s_['items']]).value_counts().reset_index()
        agg.columns = ['SKU', 'QTY']
        st.table(agg)
        st.markdown('</div>', unsafe_allow_html=True)
