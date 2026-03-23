# app.py
import streamlit as st
import pandas as pd
import json, os, math
from v_i18n import TRANSLATIONS
from v_styles import apply_supreme_ui, load_vorteza_asset
from v_engine import VEngine
from v_visuals import render_3d_pro, get_pro_color

apply_supreme_ui()

if 'authorized' not in st.session_state: st.session_state.authorized = False
if not st.session_state.authorized:
    sys_key = str(st.secrets.get("password", "vorteza2026"))
    _, col, _ = st.columns([1, 1.8, 1])
    with col:
        with st.form("VAuth"):
            st.markdown("<h2 style='text-align:center;'>VORTEZA STACK</h2>", unsafe_allow_html=True)
            if st.text_input("GOLIATH MASTER CORE KEY", type="password") == sys_key:
                if st.form_submit_button("UNLOCK SYSTEM"): st.session_state.authorized = True; st.rerun()
    st.stop()

if 'v_manifest' not in st.session_state: st.session_state.v_manifest = []
if 'lang' not in st.session_state: st.session_state.lang = "PL"
T = TRANSLATIONS[st.session_state.lang]

def db_load():
    if os.path.exists('products.json'):
        with open('products.json', 'r', encoding='utf-8') as f: return json.load(f)
    return []

inventory = db_load()

FLEET = {
    "TIR Mega 13.6m": {"max_w": 24000, "L": 1360, "W": 248, "H": 300, "ax": 3, "cab": 230},
    "TIR Std 13.6m": {"max_w": 24000, "L": 1360, "W": 248, "H": 275, "ax": 3, "cab": 230},
    "Solo 9m Heavy": {"max_w": 9500, "L": 920, "W": 245, "H": 270, "ax": 2, "cab": 200}
}

with st.sidebar:
    st.session_state.lang = st.radio("JĘZYK", ["PL", "ENG", "DE", "ES"], horizontal=True)
    st.markdown(f"### 📡 {T['fleet']}")
    v_sel = st.selectbox(T['unit'], list(FLEET.keys()))
    veh = FLEET[v_sel]
    x_off = st.slider(T['offset'], 0, veh['L']-200, 0)
    
    st.divider()
    st.markdown(f"### 📐 {T['truss_calc']}")
    c1, c2 = st.columns(2)
    t2m, t3m = c1.number_input(T['truss_2m'], 0), c2.number_input(T['truss_3m'], 0)
    if st.button(T['add_truss']):
        p2 = {"name": "truss cart 14x2", "length": 200, "width": 60, "height": 240, "weight": 420, "canStack": False, "allowRotation": True, "itemsPerCase": 1}
        p3 = {"name": "truss cart 14x3", "length": 300, "width": 60, "height": 240, "weight": 630, "canStack": False, "allowRotation": True, "itemsPerCase": 1}
        for _ in range(math.ceil(t2m/14)): st.session_state.v_manifest.append(p2.copy())
        for _ in range(math.ceil(t3m/14)): st.session_state.v_manifest.append(p3.copy())
        st.rerun()

    st.divider()
    st.markdown(f"### 📥 {T['cargo']}")
    sku_list = [p['name'] for p in inventory]
    sku = st.selectbox(T['sku_sel'], sku_list, index=None)
    if sku:
        p_ref = next(i for i in inventory if i['name'] == sku)
        qty = st.number_input(T['qty'], 1, 1000, p_ref.get('itemsPerCase', 1))
        if st.button(T['append']):
            for _ in range(math.ceil(qty/p_ref.get('itemsPerCase', 1))): st.session_state.v_manifest.append(p_ref.copy())
            st.rerun()
    if st.button(T['purge']): st.session_state.v_manifest = []; st.rerun()

st.markdown("<h1>VORTEZA STACK</h1>", unsafe_allow_html=True)
tab_p, tab_i = st.tabs([f"📊 {T['planner']}", f"📦 {T['inventory']}"])

with tab_p:
    if st.session_state.v_manifest:
        k1, k2, k3, k4 = st.columns(4)
        tm_tot = sum(float(u['weight']) for u in st.session_state.v_manifest)
        k1.metric(T['cases'], len(st.session_state.v_manifest))
        k2.metric(T['pcs'], sum(int(u.get('itemsPerCase', 1)) for u in st.session_state.v_manifest))
        k3.metric(T['weight'], f"{tm_tot} KG")
        k4.metric(T['util'], f"{(tm_tot/veh['max_w'])*100:.1f}%")
        rem = [dict(u) for u in st.session_state.v_manifest]
        fleet_res = []
        while rem:
            s, w, n, l = VEngine.pack(rem, veh, offset=x_off)
            if not s: break
            fleet_res.append({"s": s, "w": w, "l": l}); rem = n
        for idx, unit in enumerate(fleet_res):
            st.markdown(f'<div class="v-tile-pro">', unsafe_allow_html=True)
            st.markdown(f"### MISSION UNIT #{idx+1} | {v_sel}")
            vc, dc = st.columns([2.8, 1])
            with vc:
                st.plotly_chart(render_3d_pro(veh, unit['s']), use_container_width=True)
                tm, tw = 0, 0
                for s_ in unit['s']:
                    for it in s_['items']: tm += (s_['x']+it['w_fit']/2)*it['weight']; tw += it['weight']
                cp = (tm/tw/veh['L'])*100 if tw > 0 else 0
                st.markdown(f"#### ⚖️ {T['cog']}")
                st.markdown(f'<div class="v-rail-track"><div class="v-cog-indicator" style="left:{cp}%;"></div></div><br>', unsafe_allow_html=True)
            with dc:
                st.markdown(f"**{T['kpi']}**")
                st.write(f"{T['ldm']}: **{unit['l']:.2f} m**")
                st.write(f"{T['weight']}: **{unit['w']} kg**")
                st.divider()
                st.markdown(f"**{T['manifest']}**")
                agg = pd.Series([u['name'] for s_ in unit['s'] for u in s_['items']]).value_counts().reset_index()
                agg.columns = ['SKU', 'QTY']
                html = f'<table class="v-table-tactical"><tr><th>SKU</th><th>{T["qty"]}</th></tr>'
                for _, r in agg.iterrows():
                    html += f'<tr><td><span style="color:{get_pro_color(r["SKU"])}">■</span> {r["SKU"]}</td><td>{r["QTY"]}</td></tr>'
                st.markdown(html+'</table>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
    else: st.info("VORTEZA STACK: WAITING FOR MISSION DATA.")

with tab_i:
    st.markdown(f"### 📦 {T['inventory']}")
    if inventory:
        df_inv = pd.DataFrame(inventory)
        edt = st.data_editor(df_inv, use_container_width=True, num_rows="dynamic", key="v35_editor")
        if st.button(T['sync']):
            with open('products.json', 'w', encoding='utf-8') as f: json.dump(edt.to_dict('records'), f, indent=4, ensure_ascii=False)
            st.success("SYNC OK")
    else:
        st.warning("BRAK DANYCH. DODAJ PRODUKT PONIŻEJ.")
    with st.expander(f"➕ {T['add_new']}"):
        with st.form("NewProd"):
            fn = st.text_input("Name / SKU")
            c1, c2, c3 = st.columns(3)
            fl, fw, fh = c1.number_input(T['length'], 120), c2.number_input(T['width'], 80), c3.number_input(T['height'], 100)
            fm, fi = st.number_input("Weight (kg)", 50), st.number_input("IPU (pcs/case)", 1)
            if st.form_submit_button("ADD TO DB"):
                inventory.append({"name":fn,"length":fl,"width":fw,"height":fh,"weight":fm,"itemsPerCase":fi,"canStack":True,"allowRotation":True})
                with open('products.json', 'w', encoding='utf-8') as f: json.dump(inventory, f, indent=4, ensure_ascii=False)
                st.rerun()
