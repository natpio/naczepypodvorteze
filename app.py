import streamlit as st
import json
import plotly.graph_objects as go
import math
import pandas as pd
import random
import base64
from PIL import Image

# =========================================================
# 1. KONFIGURACJA I SEKRETY
# =========================================================
try:
    USER_DB = st.secrets["credentials"]["usernames"]
except:
    USER_DB = {"admin": "admin123"} # Testowy fallback

VEHICLES = {
    "BUS (3.5t)": {"maxWeight": 1100, "L": 450, "W": 170, "H": 210, "color": "#475569"},
    "Solo 6m": {"maxWeight": 3500, "L": 600, "W": 245, "H": 250, "color": "#1e293b"},
    "Solo 7m": {"maxWeight": 7000, "L": 720, "W": 245, "H": 270, "color": "#0f172a"},
    "TIR FTL": {"maxWeight": 24000, "L": 1360, "W": 248, "H": 270, "color": "#000000"}
}

# =========================================================
# 2. STYLIZACJA VORTEZA (ADVANCED CSS)
# =========================================================
def apply_vorteza_theme():
    st.markdown("""
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;700&display=swap');
            :root {
                --v-copper: #B58863;
                --v-dark: #0E0E0E;
                --v-panel: rgba(20, 20, 20, 0.95);
                --v-text: #E0E0E0;
            }
            .stApp { background-color: var(--v-dark); color: var(--v-text); font-family: 'Montserrat', sans-serif; }
            h1, h2, h3, .stSubheader { color: var(--v-copper) !important; text-transform: uppercase; letter-spacing: 2px; font-weight: 700 !important; }
            .vorteza-card {
                background-color: var(--v-panel); padding: 25px; border-radius: 5px;
                border-left: 5px solid var(--v-copper); box-shadow: 0 10px 40px rgba(0,0,0,0.8);
                backdrop-filter: blur(15px); margin-bottom: 20px;
            }
            [data-testid="stMetricValue"] { color: var(--v-copper) !important; font-size: 1.8rem !important; font-weight: 700 !important; }
            label[data-testid="stWidgetLabel"] { color: var(--v-copper) !important; text-transform: uppercase; font-size: 0.8rem !important; font-weight: 700 !important; }
            .stButton > button {
                background-color: rgba(0, 0, 0, 0.7); color: var(--v-copper); border: 1px solid var(--v-copper);
                font-weight: 700; text-transform: uppercase; width: 100%; transition: 0.3s;
            }
            .stButton > button:hover { background-color: var(--v-copper); color: black; }
            .unit-box { background-color: rgba(181, 136, 99, 0.1); border: 1px solid var(--v-copper); padding: 10px; border-radius: 4px; font-size: 0.85rem; margin-bottom: 10px; }
        </style>
    """, unsafe_allow_html=True)

# =========================================================
# 3. SILNIK WIZUALIZACJI 3D (Z PODŁOGĄ I KABINĄ)
# =========================================================
def draw_truck_ultimate(vehicle, stacks):
    fig = go.Figure()
    v_l, v_w, v_h = vehicle['L'], vehicle['W'], vehicle['H']
    
    # Podłoga i Kabina
    fig.add_trace(go.Mesh3d(x=[0, v_l, v_l, 0], y=[0, 0, v_w, v_w], z=[-2, -2, -2, -2], color='#2c3e50', opacity=1, hoverinfo='skip'))
    fig.add_trace(go.Mesh3d(x=[-120, 0, 0, -120, -120, 0, 0, -120], y=[0, 0, v_w, v_w], z=[0, 0, 0, 0, v_h*0.8, v_h*0.8, v_h*0.8, v_h*0.8], color='#1a1a1a', opacity=1, hoverinfo='skip'))
    
    # Obrys paki
    lines = [([0, v_l], [0, 0], [0, 0]), ([0, v_l], [v_w, v_w], [0, 0]), ([0, 0], [0, v_w], [0, 0]), ([v_l, v_l], [0, v_w], [0, 0]),
             ([0, 0], [0, 0], [0, v_h]), ([0, 0], [v_w, v_w], [0, v_h]), ([0, v_l], [0, 0], [v_h, v_h]), ([0, v_l], [v_w, v_w], [v_h, v_h])]
    for x_c, y_c, z_c in lines:
        fig.add_trace(go.Scatter3d(x=x_c, y=y_c, z=z_c, mode='lines', line=dict(color='#B58863', width=3), hoverinfo='skip'))

    # Ładunek
    for s in stacks:
        for it in s['items']:
            x, y, z = s['x'], s['y'], it['z']
            dx, dy, dz = (it['width'], it['length'], it['height']) if it['width'] == s['w'] else (it['length'], it['width'], it['height'])
            
            fig.add_trace(go.Mesh3d(
                x=[x, x+dx, x+dx, x, x, x+dx, x+dx, x], y=[y, y, y+dy, y+dy, y, y, y+dy, y+dy], z=[z, z, z, z, z+dz, z+dz, z+dz, z+dz],
                i=[7,0,0,0,4,4,6,6,4,0,3,2], j=[3,4,1,2,5,6,5,2,0,1,6,3], k=[0,7,2,3,6,7,1,1,5,5,7,6],
                color='#B58863', opacity=0.9, name=it['name']
            ))
            fig.add_trace(go.Scatter3d(
                x=[x, x+dx, x+dx, x, x, x, x+dx, x+dx, x, x, x+dx, x+dx, x+dx, x+dx, x, x],
                y=[y, y, y+dy, y+dy, y, y, y, y+dy, y+dy, y+dy, y+dy, y, y, y+dy, y+dy, y],
                z=[z, z, z, z, z, z+dz, z+dz, z, z, z+dz, z+dz, z+dz, z, z, z+dz, z+dz],
                mode='lines', line=dict(color='black', width=2), hoverinfo='skip'
            ))

    fig.update_layout(scene=dict(aspectmode='data', xaxis_visible=False, yaxis_visible=False, zaxis_visible=False,
                                 camera=dict(eye=dict(x=1.8, y=1.8, z=1.2))), margin=dict(l=0, r=0, b=0, t=0), showlegend=False, paper_bgcolor='rgba(0,0,0,0)')
    return fig

# =========================================================
# 4. SILNIK PAKOWANIA I LOGIKA BIZNESOWA
# =========================================================
def pack_items(cargo, veh):
    items = sorted(cargo, key=lambda x: (not x.get('canStack', True), x['width']*x['length']), reverse=True)
    stacks, not_p, w_sum, x, y, row_w = [], [], 0, 0, 0, 0
    for it in items:
        if w_sum + it['weight'] > veh['maxWeight']: not_p.append(it); continue
        stacked = False
        if it.get('canStack', True):
            for s in stacks:
                if ((it['width']<=s['w'] and it['length']<=s['l']) or (it['length']<=s['w'] and it['width']<=s['l'])) and (s['curH']+it['height'] <= veh['H']):
                    it_c = it.copy(); it_c['z'] = s['curH']; s['items'].append(it_c); s['curH']+=it['height']; w_sum+=it['weight']; stacked=True; break
        if not stacked:
            for fw, fl in [(it['width'], it['length']), (it['length'], it['width'])]:
                if y + fl <= veh['W'] and x + fw <= veh['L']:
                    it_c = it.copy(); it_c['z'] = 0; stacks.append({'x':x, 'y':y, 'w':fw, 'l':fl, 'curH':it['height'], 'items':[it_c]}); y+=fl; row_w=max(row_w, fw); w_sum+=it['weight']; stacked=True; break
                elif x + row_w + fw <= veh['L'] and fl <= veh['W']:
                    x+=row_w; y=0; row_w=fw; it_c = it.copy(); it_c['z'] = 0; stacks.append({'x':x, 'y':y, 'w':fw, 'l':fl, 'curH':it['height'], 'items':[it_c]}); y+=fl; w_sum+=it['weight']; stacked=True; break
            if not stacked: not_p.append(it)
    ldm = (max([s['x'] + s['w'] for s in stacks]) / 100) if stacks else 0
    return stacks, w_sum, not_p, ldm

# =========================================================
# 5. GŁÓWNA APLIKACJA
# =========================================================
st.set_page_config(page_title="VORTEZA FLOW PRO", layout="wide")
apply_vorteza_theme()

if "authenticated" not in st.session_state: st.session_state.authenticated = False

if not st.session_state.authenticated:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.form("Login"):
            st.markdown("<h3 style='text-align: center;'>VORTEZA ACCESS</h3>", unsafe_allow_html=True)
            u = st.text_input("Użytkownik"); p = st.text_input("Hasło", type="password")
            if st.form_submit_button("AUTORYZUJ"):
                if u in USER_DB and USER_DB[u] == p: st.session_state.authenticated = True; st.rerun()
else:
    # Header
    c_l, c_t, c_lo = st.columns([1, 4, 1])
    with c_t: st.markdown("<h1 style='margin-bottom:0;'>VORTEZA FLOW</h1><p style='color:#666;'>SYSTEMS | LOGISTICS PLANNER 2026</p>", unsafe_allow_html=True)
    with c_lo: 
        if st.button("WYLOGUJ"): st.session_state.authenticated = False; st.rerun()

    if 'cargo' not in st.session_state: st.session_state.cargo = []
    
    with st.sidebar:
        st.subheader("OPERACJE")
        v_name = st.selectbox("FLOTA", list(VEHICLES.keys()))
        veh = VEHICLES[v_name]
        st.divider()
        try:
            with open('products.json', 'r', encoding='utf-8') as f: all_p = json.load(f)
        except: all_p = []
        
        p_name = st.selectbox("PRODUKT", [p['name'] for p in all_p], index=None)
        if p_name:
            p_data = next(p for p in all_p if p['name'] == p_name)
            ipc = p_data.get('itemsPerCase', 1)
            st.markdown(f'<div class="unit-box">📦 <b>Standard: {ipc} szt. / opak.</b></div>', unsafe_allow_html=True)
            count = st.number_input("SZTUKI", min_value=1, value=ipc)
            num_c = math.ceil(count / ipc)
            if st.button("DODAJ DO MANIFESTU"):
                for i in range(num_c):
                    c = p_data.copy()
                    c['pcs'] = ipc if (i < num_c - 1 or count % ipc == 0) else (count % ipc)
                    st.session_state.cargo.append(c)
                st.rerun()
        if st.button("RESETUJ MANIFEST"): st.session_state.cargo = []; st.rerun()

    if st.session_state.cargo:
        # Metryki
        total_pcs = sum(int(c.get('pcs', c.get('itemsPerCase', 1))) for c in st.session_state.cargo)
        total_w = sum(float(c.get('weight', 0)) for c in st.session_state.cargo)
        
        m1, m2, m3 = st.columns(3)
        m1.metric("OPAKOWANIA", len(st.session_state.cargo))
        m2.metric("SZTUKI ŁĄCZNIE", f"{total_pcs} szt.")
        m3.metric("WAGA CAŁKOWITA", f"{total_w} kg")

        # Pakowanie
        remaining = [dict(c) for c in st.session_state.cargo]
        fleet = []
        while remaining:
            res_s, res_w, rem, ldm = pack_items(remaining, veh)
            if not res_s: break
            fleet.append({"stacks": res_s, "weight": res_w, "ldm": ldm})
            remaining = rem

        for i, truck in enumerate(fleet):
            st.markdown(f'<div class="vorteza-card"><h3>POJAZD #{i+1} | {v_name} | LDM: {truck["ldm"]:.2f}</h3>', unsafe_allow_html=True)
            cv, cd = st.columns([2, 1])
            with cv: st.plotly_chart(draw_truck_ultimate(veh, truck['stacks']), use_container_width=True)
            with cd:
                items = [it['name'] for s in truck['stacks'] for it in s['items']]
                st.write("**ZAWARTOŚĆ:**")
                st.table(pd.Series(items).value_counts().reset_index().rename(columns={"index":"Produkt", "count":"Opakowań"}))
            st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.info("System gotowy. Dodaj produkty do manifestu.")
