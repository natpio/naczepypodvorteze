import streamlit as st
import json
import plotly.graph_objects as go
import math
import pandas as pd
import random
import base64

# =========================================================
# 1. AUTORYZACJA I KONFIGURACJA (FIXED FOR MOBILE)
# =========================================================
def check_vorteza_auth():
    if "v_auth" not in st.session_state:
        st.session_state.v_auth = False

    if not st.session_state.v_auth:
        try:
            master_pwd = str(st.secrets.get("password", st.secrets.get("credentials", {}).get("password", "vorteza2026")))
        except Exception:
            st.error("BŁĄD KRYTYCZNY: Brak hasła w Secrets.")
            return False

        c1, c2, c3 = st.columns([0.1, 0.8, 0.1]) # Lepszy balans na mobile
        with c2:
            st.markdown("<br><br>", unsafe_allow_html=True)
            with st.form("VortezaSecureLogin"):
                st.markdown("<h2 style='text-align:center; color:#B58863;'>VORTEZA SYSTEMS</h2>", unsafe_allow_html=True)
                input_pwd = st.text_input("ACCESS KEY", type="password")
                submit = st.form_submit_button("AUTORYZUJ")
                if submit:
                    if input_pwd == master_pwd:
                        st.session_state.v_auth = True
                        st.rerun()
                    else:
                        st.error("Błędny klucz.")
        return False
    return True

VEHICLES = {
    "TIR FTL (13.6m)": {"maxWeight": 24000, "L": 1360, "W": 248, "H": 275},
    "Solo 7m": {"maxWeight": 7000, "L": 720, "W": 245, "H": 270},
    "Solo 6m": {"maxWeight": 3500, "L": 600, "W": 245, "H": 250},
    "BUS": {"maxWeight": 1100, "L": 450, "W": 175, "H": 210}
}

# =========================================================
# 2. VORTEZA STYLE PRO (Z POPRAWKAMI MOBILE)
# =========================================================
def apply_vorteza_ui():
    st.markdown("""
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;700&display=swap');
            
            :root {
                --v-copper: #B58863;
                --v-dark-bg: #0A0A0A;
                --v-panel: rgba(20, 20, 20, 0.98);
            }

            .stApp { background-color: var(--v-dark-bg); color: #E0E0E0; font-family: 'Montserrat', sans-serif; }
            h1, h2, h3 { color: var(--v-copper) !important; text-transform: uppercase; letter-spacing: 2px; }

            .vorteza-card {
                background: var(--v-panel); padding: 1.5rem; border-radius: 2px;
                border-left: 4px solid var(--v-copper); box-shadow: 10px 10px 30px rgba(0,0,0,0.5);
                margin-bottom: 1rem;
            }

            [data-testid="stMetricValue"] { color: var(--v-copper) !important; font-size: 1.8rem !important; }
            
            /* Styl paska bocznego dla Mobile */
            [data-testid="stSidebar"] { background-color: #111 !important; border-right: 1px solid var(--v-copper); }
            
            .stButton > button {
                background: transparent; color: var(--v-copper); border: 1px solid var(--v-copper);
                border-radius: 0px; text-transform: uppercase; width: 100%; font-weight: 700;
            }
            .stButton > button:hover { background: var(--v-copper); color: black; }
            
            .v-table { width: 100%; border-collapse: collapse; }
            .v-table th { color: var(--v-copper); text-align: left; font-size: 0.7rem; border-bottom: 1px solid #333; padding: 8px; }
            .v-table td { padding: 8px; border-bottom: 1px solid #151515; font-size: 0.8rem; }
        </style>
    """, unsafe_allow_html=True)

# =========================================================
# 3. SILNIK WIZUALIZACJI I PAKOWANIA (V-ENGINE)
# =========================================================
def render_vorteza_3d(vehicle_data, cargo_stacks):
    fig = go.Figure()
    L, W, H = vehicle_data['L'], vehicle_data['W'], vehicle_data['H']
    fig.add_trace(go.Mesh3d(x=[0, L, L, 0], y=[0, 0, W, W], z=[-2, -2, -2, -2], color='#1a1a1a', opacity=1))
    
    # Szkielet
    edges = [([0, L], [0, 0], [0, 0]), ([0, L], [W, W], [0, 0]), ([0, 0], [0, W], [0, 0]), ([L, L], [0, W], [0, 0]),
             ([0, 0], [0, 0], [0, H]), ([0, 0], [W, W], [0, H]), ([0, L], [0, 0], [H, H]), ([0, L], [W, W], [H, H])]
    for xe, ye, ze in edges:
        fig.add_trace(go.Scatter3d(x=xe, y=ye, z=ze, mode='lines', line=dict(color='#B58863', width=2), hoverinfo='skip'))

    for s_idx, stack in enumerate(cargo_stacks):
        c_color = f'rgb({181-s_idx%5*20}, {136-s_idx%5*15}, {99-s_idx%5*10})'
        for item in stack['items']:
            x, y, z = stack['x'], stack['y'], item['z']
            dx, dy, dz = item['w_fit'], item['l_fit'], item['height']
            fig.add_trace(go.Mesh3d(x=[x,x+dx,x+dx,x,x,x+dx,x+dx,x], y=[y,y,y+dy,y+dy,y,y,y+dy,y+dy], z=[z,z,z,z,z+dz,z+dz,z+dz,z+dz],
                                   i=[7,0,0,0,4,4,6,6,4,0,3,2], j=[3,4,1,2,5,6,5,2,0,1,6,3], k=[0,7,2,3,6,7,1,1,5,5,7,6], color=c_color, opacity=0.9))

    fig.update_layout(scene=dict(aspectmode='data', xaxis_visible=False, yaxis_visible=False, zaxis_visible=False),
                      paper_bgcolor='rgba(0,0,0,0)', margin=dict(l=0,r=0,b=0,t=0), showlegend=False)
    return fig

def vorteza_engine(cargo_list, vehicle):
    items = sorted(cargo_list, key=lambda x: (not x.get('canStack', True), x['width']*x['length']), reverse=True)
    stacks, failed, w_sum, cx, cy, row_w = [], [], 0, 0, 0, 0
    for it in items:
        if w_sum + it['weight'] > vehicle['maxWeight']: failed.append(it); continue
        stacked = False
        if it.get('canStack', True):
            for s in stacks:
                if ((it['width']<=s['w'] and it['length']<=s['l']) or (it['length']<=s['w'] and it['width']<=s['l'])) and (s['curH']+it['height'] <= vehicle['H']):
                    it_c = it.copy(); it_c['z']=s['curH']; it_c['w_fit'], it_c['l_fit']=s['w'], s['l']; s['items'].append(it_c); s['curH']+=it['height']; w_sum+=it['weight']; stacked=True; break
        if not stacked:
            for fw, fl in [(it['width'], it['length']), (it['length'], it['width'])]:
                if cy+fl <= vehicle['W'] and cx+fw <= vehicle['L']:
                    it_c = it.copy(); it_c['z']=0; it_c['w_fit'], it_c['l_fit']=fw, fl; stacks.append({'x':cx, 'y':cy, 'w':fw, 'l':fl, 'curH':it['height'], 'items':[it_c]}); cy+=fl; row_w=max(row_w, fw); w_sum+=it['weight']; stacked=True; break
                elif cx+row_w+fw <= vehicle['L'] and fl <= vehicle['W']:
                    cx+=row_w; cy=0; row_w=fw; it_c = it.copy(); it_c['z']=0; it_c['w_fit'], it_c['l_fit']=fw, fl; stacks.append({'x':cx, 'y':cy, 'w':fw, 'l':fl, 'curH':it['height'], 'items':[it_c]}); cy+=fl; w_sum+=it['weight']; stacked=True; break
            if not stacked: failed.append(it)
    return stacks, w_sum, failed, (max([s['x']+s['w'] for s in stacks])/100 if stacks else 0)

# =========================================================
# 4. GŁÓWNA APLIKACJA
# =========================================================
# KLUCZOWE: initial_sidebar_state="expanded" wymusza otwarcie paska na mobile
st.set_page_config(page_title="VORTEZA FLOW PRO", layout="wide", initial_sidebar_state="expanded")
apply_vorteza_ui()

if check_vorteza_auth():
    # Header
    c_h, c_l = st.columns([4, 1])
    with c_h: st.markdown("<h1>VORTEZA FLOW</h1><p style='color:#666; font-size:0.7rem;'>PRO EDITION v3.2</p>", unsafe_allow_html=True)
    with c_l: 
        if st.button("LOGOUT"): st.session_state.v_auth = False; st.rerun()

    if 'v_cargo' not in st.session_state: st.session_state.v_cargo = []

    with st.sidebar:
        st.markdown("### PANEL OPERACYJNY")
        v_sel = st.selectbox("FLOTA", list(VEHICLES.keys()))
        veh = VEHICLES[v_sel]
        st.divider()
        try:
            with open('products.json', 'r', encoding='utf-8') as f: db = json.load(f)
        except: db = []
        
        p_name = st.selectbox("PRODUKT", [p['name'] for p in db], index=None)
        if p_name:
            p_ref = next(p for p in db if p['name'] == p_name)
            ipc = p_ref.get('itemsPerCase', 1)
            p_qty = st.number_input("SZTUKI", min_value=1, value=ipc)
            n_c = math.ceil(p_qty / ipc)
            if st.button("DODAJ DO MANIFESTU"):
                for i in range(n_c):
                    c = p_ref.copy()
                    c['p_actual'] = ipc if (i < n_c - 1 or p_qty % ipc == 0) else (p_qty % ipc)
                    st.session_state.v_cargo.append(c)
                st.rerun()
        if st.button("RESETUJ SYSTEM"): st.session_state.v_cargo = []; st.rerun()

    if st.session_state.v_cargo:
        # Metryki
        total_kg = sum(float(c.get('weight', 0)) for c in st.session_state.v_cargo)
        m1, m2, m3 = st.columns(3)
        m1.metric("OPAKOWANIA", len(st.session_state.v_cargo))
        m2.metric("WAGA", f"{total_kg} KG")
        m3.metric("LDM (EST.)", f"{(total_kg/veh['maxWeight'])*(veh['L']/100):.2f}")

        # Pakowanie
        rem = [dict(c) for c in st.session_state.v_cargo]
        fleet = []
        while rem:
            s, w, n, l = vorteza_engine(rem, veh)
            if not s: break
            fleet.append({"stacks":s, "weight":w, "ldm":l})
            rem = n

        for idx, truck in enumerate(fleet):
            st.markdown(f'<div class="vorteza-card"><h3>POJAZD #{idx+1} | {v_sel}</h3>', unsafe_allow_html=True)
            st.plotly_chart(render_vorteza_3d(veh, truck['stacks']), use_container_width=True)
            st.markdown(f"LDM: **{truck['ldm']:.2f}** | WAGA: **{truck['weight']} KG**", unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="vorteza-card" style="text-align:center;">GOTOWY DO PRACY. OCZEKIWANIE NA DANE...</div>', unsafe_allow_html=True)
