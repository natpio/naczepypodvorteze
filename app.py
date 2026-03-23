# -*- coding: utf-8 -*-
"""
================================================================================
SYSTEM: VORTEZA STACK
VERSION: 18.0 | ARCHITECT EDITION
FIRM: VORTEZA
================================================================================
AUTOR: VORTEZA AI PROTOCOL (PAID TIER)
OPIS: KOMPLEKSOWY SYSTEM OPTYMALIZACJI LOGISTYCZNEJ I INŻYNIERII TRANSPORTU
================================================================================
"""

import streamlit as st
import json
import plotly.graph_objects as go
import plotly.express as px
import math
import pandas as pd
import random
import base64
from datetime import datetime
import io
import os
from PIL import Image

# ==============================================================================
# 1. ARCHITEKTURA SYSTEMU I REJESTR FLOTY
# ==============================================================================
st.set_page_config(
    page_title="VORTEZA STACK v18.0",
    layout="wide",
    initial_sidebar_state="expanded",
    page_icon="🕋"
)

# SPECYFIKACJA FLOTY VORTEZA (PARAMETRY INŻYNIERYJNE)
FLEET_REGISTRY = {
    "TIR FTL (Mega 13.6m)": {
        "max_w": 24000, "L": 1360, "W": 248, "H": 300, 
        "ldm_cap": 13.6, "axles": 3, "wheelbase": 850, "tare": 14500,
        "cab_l": 220, "chassis_color": "#0a0a0a"
    },
    "TIR FTL (Standard 13.6m)": {
        "max_w": 24000, "L": 1360, "W": 248, "H": 275, 
        "ldm_cap": 13.6, "axles": 3, "wheelbase": 850, "tare": 13800,
        "cab_l": 220, "chassis_color": "#0d0d0d"
    },
    "Solo 9m (Heavy)": {
        "max_w": 9500, "L": 920, "W": 245, "H": 270, 
        "ldm_cap": 9.2, "axles": 2, "wheelbase": 550, "tare": 8500,
        "cab_l": 180, "chassis_color": "#111111"
    },
    "Solo 7m (Medium)": {
        "max_w": 7000, "L": 720, "W": 245, "H": 260, 
        "ldm_cap": 7.2, "axles": 2, "wheelbase": 480, "tare": 6200,
        "cab_l": 160, "chassis_color": "#151515"
    },
    "BUS XL (Express)": {
        "max_w": 1250, "L": 485, "W": 175, "H": 220, 
        "ldm_cap": 4.8, "axles": 2, "wheelbase": 320, "tare": 2250,
        "cab_l": 130, "chassis_color": "#000000"
    }
}

# ==============================================================================
# 2. DESIGN SYSTEM & CSS ENGINE (VORTEZA BRANDING)
# ==============================================================================
def load_resource_b64(file_path):
    try:
        if os.path.exists(file_path):
            with open(file_path, 'rb') as f:
                return base64.b64encode(f.read()).decode()
        return ""
    except:
        return ""

def inject_vorteza_stack_ui():
    bg_b64 = load_resource_b64('bg_vorteza.png')
    
    st.markdown(f"""
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;600;700&family=JetBrains+Mono:wght@300;400;500&display=swap');
            
            :root {{
                --v-copper: #B58863;
                --v-copper-bright: #d4a373;
                --v-dark-bg: #030303;
                --v-panel-bg: rgba(10, 10, 10, 0.97);
                --v-border: rgba(181, 136, 99, 0.3);
                --v-neon: #00FF41;
            }}

            .stApp {{
                background-image: url("data:image/png;base64,{bg_b64}");
                background-size: cover;
                background-attachment: fixed;
                color: #FFFFFF;
                font-family: 'Montserrat', sans-serif;
            }}

            .v-stack-panel {{
                background: var(--v-panel-bg);
                padding: 3.5rem;
                border-radius: 2px;
                border: 1px solid var(--v-border);
                border-left: 15px solid var(--v-copper);
                box-shadow: 0 50px 150px rgba(0,0,0,0.95);
                margin-bottom: 4rem;
                backdrop-filter: blur(50px);
            }}

            section[data-testid="stSidebar"] {{
                background-color: rgba(5, 5, 5, 0.98) !important;
                border-right: 1px solid var(--v-border);
                width: 500px !important;
                backdrop-filter: blur(30px);
            }}

            h1, h2, h3 {{ 
                color: var(--v-copper) !important; 
                text-transform: uppercase; 
                letter-spacing: 12px !important; 
                font-weight: 700 !important; 
                text-shadow: 3px 3px 25px rgba(0,0,0,0.7);
            }}

            [data-testid="stMetricValue"] {{ 
                color: var(--v-copper) !important; 
                font-family: 'JetBrains Mono', monospace !important; 
                font-size: 3.5rem !important;
                font-weight: 300 !important;
            }}

            .stButton > button {{
                background: linear-gradient(180deg, #0a0a0a, #151515);
                color: var(--v-copper);
                border: 1px solid var(--v-copper);
                padding: 1.6rem;
                text-transform: uppercase;
                letter-spacing: 8px;
                font-weight: 700;
                width: 100%;
                transition: 0.7s all cubic-bezier(0.19, 1, 0.22, 1);
                border-radius: 0;
            }}

            .stButton > button:hover {{
                background: var(--v-copper);
                color: #000;
                box-shadow: 0 0 100px rgba(181, 136, 99, 0.8);
                transform: translateY(-5px);
            }}

            .v-tactical-table {{ 
                width: 100%; 
                border-collapse: collapse; 
                margin-top: 40px; 
                border: 1px solid #1a1a1a;
            }}
            .v-tactical-table th {{ 
                background: #000;
                color: var(--v-copper); 
                text-align: left; 
                font-size: 0.85rem; 
                text-transform: uppercase; 
                border-bottom: 3px solid #333; 
                padding: 25px; 
                letter-spacing: 4px;
            }}
            .v-tactical-table td {{ 
                padding: 20px 25px; 
                border-bottom: 1px solid #111; 
                color: #CCC; 
                font-size: 1rem; 
            }}
            .v-tactical-table tr:hover {{ background: rgba(181,136,99,0.08); }}

            .v-cog-track {{
                width: 100%;
                height: 30px;
                background: #111;
                border-radius: 15px;
                position: relative;
                border: 1px solid #333;
                margin: 50px 0;
                box-shadow: inset 0 0 15px #000;
            }}
            .v-cog-pointer {{
                position: absolute;
                width: 8px;
                height: 55px;
                top: -12.5px;
                background: var(--v-neon);
                box-shadow: 0 0 30px var(--v-neon);
                border-radius: 4px;
            }}
            
            .v-unit-tag {{
                background: rgba(181,136,99,0.1);
                border: 1px solid var(--v-copper);
                padding: 20px;
                font-family: 'JetBrains Mono', monospace;
                font-size: 0.85rem;
                margin-bottom: 15px;
            }}
        </style>
    """, unsafe_allow_html=True)

# ==============================================================================
# 3. KONTROLA DOSTĘPU (SECURITY PROTOCOL)
# ==============================================================================
def check_stack_authorization():
    if "authorized" not in st.session_state:
        st.session_state.authorized = False

    if not st.session_state.authorized:
        try:
            pwd_target = str(st.secrets.get("password", "vorteza2026"))
        except:
            pwd_target = "vorteza2026"

        st.markdown("<br><br><br><br><br><br>", unsafe_allow_html=True)
        _, col_auth, _ = st.columns([1, 1.8, 1])
        with col_auth:
            with st.form("VortezaStackGate"):
                st.markdown("<h2 style='text-align:center;'>VORTEZA STACK</h2>", unsafe_allow_html=True)
                st.markdown("<p style='text-align:center; color:#333; font-size:0.8rem; letter-spacing:8px;'>MASTER ENCRYPTION KEY REQUIRED</p>", unsafe_allow_html=True)
                key_in = st.text_input("GOLIATH SECURITY PROTOCOL", type="password")
                if st.form_submit_button("VALIDATE CLEARANCE"):
                    if key_in == pwd_target:
                        st.session_state.authorized = True
                        st.rerun()
                    else:
                        st.error("ACCESS DENIED: INVALID SYSTEM KEY")
        return False
    return True

# ==============================================================================
# 4. CHROMATIC PRODUCT ENGINE (PRODUCT MAPPING)
# ==============================================================================
def get_sku_chromatic_hex(sku_name):
    palette = [
        "#B58863", "#D4AF37", "#8E6A4D", "#5E4633", "#A67C52", 
        "#2C3E50", "#34495E", "#1A252F", "#16A085", "#27AE60",
        "#7F8C8D", "#95A5A6", "#BDC3C7", "#E67E22", "#D35400",
        "#C0392B", "#E74C3C", "#8E44AD", "#9B59B6", "#2980B9"
    ]
    random.seed(sum(ord(c) for c in sku_name))
    return random.choice(palette)

# ==============================================================================
# 5. RENDERER CAD-3D STACK (VISUAL ENGINE v18.0)
# ==============================================================================
def render_stack_cad_3d(vehicle, cargo_clusters):
    fig = go.Figure()
    L, W, H = vehicle['L'], vehicle['W'], vehicle['H']

    # --- KONSTRUKCJA POJAZDU ---
    # Podwozie (Main Chassis)
    fig.add_trace(go.Mesh3d(x=[0, L, L, 0], y=[0, 0, W, W], z=[-15, -15, -15, -15], color='#121212', opacity=1, hoverinfo='skip'))
    
    # Koła i Inżynieria Zawieszenia
    num_ax = vehicle.get('axles', 3)
    ax_dist = 142
    start_x = L - 420 if L > 800 else L - 180
    for i in range(num_ax):
        cx = start_x + (i * ax_dist)
        if cx < L:
            for side in [-38, W+22]:
                # Opona CAD
                fig.add_trace(go.Mesh3d(
                    x=[cx-55, cx+55, cx+55, cx-55], y=[side, side, side+16, side+16], 
                    z=[-75, -75, -15, -15], color='#000', opacity=1, hoverinfo='skip'
                ))
                # Felga Miedziana
                fig.add_trace(go.Mesh3d(
                    x=[cx-25, cx+25, cx+25, cx-25], y=[side-2, side-2, side, side], 
                    z=[-55, -55, -35, -35], color='#B58863', opacity=0.9, hoverinfo='skip'
                ))

    # Kabina Commander
    cab_depth = vehicle.get('cab_l', 240)
    fig.add_trace(go.Mesh3d(
        x=[-cab_depth, 0, 0, -cab_depth, -cab_depth, 0, 0, -cab_depth],
        y=[-45, -45, W+45, W+45, -45, -45, W+45, W+45],
        z=[0, 0, 0, 0, H*1.08, H*1.08, H*1.08, H*1.08],
        i=[7,0,0,0,4,4,6,6,4,0,3,2], j=[3,4,1,2,5,6,5,2,0,1,6,3], k=[0,7,2,3,6,7,1,1,5,5,7,6],
        color='#020202', opacity=1, name="COMMANDER_CAB"
    ))

    # Szkielet Konstrukcyjny (Copper Frame)
    cage = [
        ([0, L], [0, 0], [0, 0]), ([0, L], [W, W], [0, 0]), ([0, 0], [0, W], [0, 0]), ([L, L], [0, W], [0, 0]),
        ([0, 0], [0, 0], [0, H]), ([0, 0], [W, W], [0, H]), ([0, L], [0, 0], [H, H]), ([0, L], [W, W], [H, H]),
        ([L, L], [0, 0], [0, H]), ([L, L], [W, W], [0, H])
    ]
    for px, py, pz in cage:
        fig.add_trace(go.Scatter3d(x=px, y=py, z=pz, mode='lines', line=dict(color='#B58863', width=12), hoverinfo='skip'))

    # --- RENDER CARGO (CHROMATIC LAYERS) ---
    for cluster in cargo_clusters:
        for unit in cluster['items']:
            x, y, z = cluster['x'], cluster['y'], unit['z']
            dx, dy, dz = unit['w_fit'], unit['l_fit'], unit['height']
            u_color = get_sku_chromatic_hex(unit['name'])
            
            # Box Unit
            fig.add_trace(go.Mesh3d(
                x=[x,x+dx,x+dx,x,x,x+dx,x+dx,x], y=[y,y,y+dy,y+dy,y,y,y+dy,y+dy], 
                z=[z,z,z,z,z+dz,z+dz,z+dz,z+dz],
                i=[7,0,0,0,4,4,6,6,4,0,3,2], j=[3,4,1,2,5,6,5,2,0,1,6,3], k=[0,7,2,3,6,7,1,1,5,5,7,6],
                color=u_color, opacity=0.98, name=unit['name']
            ))
            # Edge Highlighting
            fig.add_trace(go.Scatter3d(
                x=[x,x+dx,x+dx,x,x,x+dx,x+dx,x,x,x+dx,x+dx,x+dx,x+dx,x,x],
                y=[y,y,y+dy,y+dy,y,y,y,y+dy,y+dy,y+dy,y+dy,y,y,y+dy,y+dy,y],
                z=[z,z,z,z,z,z+dz,z+dz,z,z,z+dz,z+dz,z+dz,z,z,z+dz,z+dz],
                mode='lines', line=dict(color='black', width=3), hoverinfo='skip'
            ))

    fig.update_layout(
        scene=dict(
            aspectmode='data', xaxis_visible=False, yaxis_visible=False, zaxis_visible=False,
            camera=dict(eye=dict(x=2.5, y=2.5, z=2.2)), bgcolor='rgba(0,0,0,0)'
        ),
        paper_bgcolor='rgba(0,0,0,0)', margin=dict(l=0, r=0, b=0, t=0), showlegend=False
    )
    return fig

# ==============================================================================
# 6. RDZEŃ OPTYMALIZACJI (V-ENGINE 18.0 STACK)
# ==============================================================================
class V18StackEngine:
    @staticmethod
    def pack_optimization(cargo_list, vehicle):
        # Sortowanie: No-Stack > No-Rotation > Powierzchnia
        sorted_cargo = sorted(cargo_list, 
                             key=lambda x: (not x.get('canStack', True), 
                                            not x.get('allowRotation', True), 
                                            x['width']*x['length']), 
                             reverse=True)
        
        stacks, rejected, mass_sum = [], [], 0
        cur_x, cur_y, row_max_w = 0, 0, 0

        for unit in sorted_cargo:
            if mass_sum + unit['weight'] > vehicle['max_w']:
                rejected.append(unit); continue
            
            # PROTOKÓŁ STACKINGU
            integrated = False
            if unit.get('canStack', True):
                for s in stacks:
                    if unit.get('allowRotation', True):
                        fit = (unit['width'] <= s['w'] and unit['length'] <= s['l']) or \
                              (unit['length'] <= s['w'] and unit['width'] <= s['l'])
                    else:
                        fit = (unit['width'] <= s['w'] and unit['length'] <= s['l'])
                    
                    if fit and (s['curH'] + unit['height'] <= vehicle['H']):
                        it_c = unit.copy(); it_c['z'] = s['curH']; it_c['w_fit'], it_c['l_fit'] = s['w'], s['l']
                        s['items'].append(it_c); s['curH'] += unit['height']; mass_sum += unit['weight']; integrated = True; break
            
            if integrated: continue

            # PROTOKÓŁ FLOOR + PERMIT ROTATION
            placed = False
            orientations = [(unit['width'], unit['length']), (unit['length'], unit['width'])] if unit.get('allowRotation', True) else [(unit['width'], unit['length'])]
            
            for fw, fl in orientations:
                if cur_y + fl <= vehicle['W'] and cur_x + fw <= vehicle['L']:
                    it_c = unit.copy(); it_c['z'] = 0; it_c['w_fit'], it_c['l_fit'] = fw, fl
                    stacks.append({'x':cur_x, 'y':cur_y, 'w':fw, 'l':fl, 'curH':unit['height'], 'items':[it_c]})
                    cur_y += fl; row_max_w = max(row_max_w, fw); mass_sum += unit['weight']; placed = True; break
                elif cur_x + row_max_w + fw <= vehicle['L'] and fl <= vehicle['W']:
                    cur_x += row_max_w; cur_y = 0; row_max_w = fw
                    it_c = unit.copy(); it_c['z'] = 0; it_c['w_fit'], it_c['l_fit'] = fw, fl
                    stacks.append({'x':cur_x, 'y':cur_y, 'w':fw, 'l':fl, 'curH':unit['height'], 'items':[it_c]})
                    cur_y += fl; mass_sum += unit['weight']; placed = True; break
            
            if not placed: rejected.append(unit)
        
        ldm_real = (max([s['x'] + s['w'] for s in stacks]) / 100) if stacks else 0
        return stacks, mass_sum, rejected, ldm_real

# ==============================================================================
# 7. ANALITYKA INŻYNIERYJNA (BALANCER)
# ==============================================================================
def process_load_balancer_ui(veh, stacks):
    if not stacks: return
    mom_total, weight_total = 0, 0
    for s in stacks:
        for it in s['items']:
            cx = s['x'] + (it['w_fit'] / 2)
            mom_total += (cx * it['weight'])
            weight_total += it['weight']
    
    cog_x = mom_total / weight_total if weight_total > 0 else 0
    cog_p = (cog_x / veh['L']) * 100
    
    st.markdown("### ⚖️ MASS DISTRIBUTION ANALYSIS (CoG)")
    st.write(f"Położenie środka ciężkości ładunku: **{cog_x/100:.2f} m** od ściany przedniej")
    
    marker_clr = "#00FF41" if 35 < cog_p < 65 else "#FF3131"
    st.markdown(f"""
        <div class="v-cog-track">
            <div class="v-cog-pointer" style="left: {cog_p}%;"></div>
            <div style="position:absolute; left:20px; top:45px; font-size:0.65rem; color:#888;">FRONT AXLES</div>
            <div style="position:absolute; right:20px; top:45px; font-size:0.65rem; color:#888;">REAR AXLES</div>
        </div>
        <br><br>
    """, unsafe_allow_html=True)
    
    if cog_p < 35: st.error("DETEKCJA: PRZECIĄŻENIE OSI PRZEDNICH. PRZESUŃ ŁADUNEK DO TYŁU.")
    elif cog_p > 65: st.error("DETEKCJA: ODCIĄŻENIE OSI STERUJĄCEJ. PRZESUŃ ŁADUNEK DO PRZODU.")
    else: st.success("STATUS: ROZKŁAD MASY NOMINALNY.")

# ==============================================================================
# 8. DATA I/O (MASTER DB)
# ==============================================================================
def db_master_load():
    try:
        if os.path.exists('products.json'):
            with open('products.json', 'r', encoding='utf-8') as f: return json.load(f)
        return []
    except: return []

def db_master_save(data):
    with open('products.json', 'w', encoding='utf-8') as f: 
        json.dump(data, f, indent=4, ensure_ascii=False)

# ==============================================================================
# 9. GŁÓWNA ARCHITEKTURA INTERFEJSU (VORTEZA STACK)
# ==============================================================================
def main():
    inject_vorteza_stack_ui()
    if not check_stack_authorization(): return

    if 'v_manifest' not in st.session_state: st.session_state.v_manifest = []
    inventory = db_master_load()

    # NAGŁÓWEK SYSTEMOWY Z LOGO
    col_l, col_t, col_e = st.columns([1, 4, 1])
    with col_l:
        logo_b64 = load_resource_b64('logo_vorteza.png')
        if logo_b64: st.markdown(f'<img src="data:image/png;base64,{logo_b64}" width="180">', unsafe_allow_html=True)
        else: st.markdown("### VORTEZA")
    with col_t:
        st.markdown("<h1>VORTEZA STACK</h1>", unsafe_allow_html=True)
        st.markdown(f"<p class='v-version-tag'>ENGINEERING SYSTEM v18.0.2 | STATUS: NOMINAL | {datetime.now().strftime('%H:%M')}</p>", unsafe_allow_html=True)
    with col_e:
        if st.button("TERMINATE"):
            st.session_state.authorized = False; st.rerun()

    # SIDEBAR: PANEL DOWODZENIA
    with st.sidebar:
        st.markdown("### 📡 FLEET COMMAND")
        v_key = st.selectbox("TRANSPORT UNIT SELECTOR", list(FLEET_REGISTRY.keys()))
        veh = FLEET_REGISTRY[v_key]
        st.divider()
        
        st.markdown("### 📥 MANIFEST INJECTION")
        p_titles = [p['name'] for p in inventory]
        sel_sku = st.selectbox("SKU SELECTOR SERVICE", p_titles, index=None)
        
        if sel_sku:
            p_ref = next(p for p in inventory if p['name'] == sel_sku)
            ipc = p_ref.get('itemsPerCase', 1)
            p_rot = p_ref.get('allowRotation', True)
            st.markdown(f"""
                <div class='v-unit-tag'>
                    SKU: {sel_sku}<br>
                    IPU: {ipc} PCS/UNIT<br>
                    PERMIT: {'<span style="color:#00FF41">AUTHORIZED</span>' if p_rot else '<span style="color:#FF3131">LOCKED</span>'}
                </div>
            """, unsafe_allow_html=True)
            p_qty = st.number_input("QUANTITY (PCS)", min_value=1, value=ipc)
            n_units = math.ceil(p_qty / ipc)
            if st.button("APPEND TO MISSION MANIFEST", type="primary"):
                for i in range(n_units):
                    u = p_ref.copy()
                    u['p_act'] = ipc if (i < n_units - 1 or p_qty % ipc == 0) else (p_qty % ipc)
                    st.session_state.v_manifest.append(u)
                st.rerun()
        if st.button("GLOBAL PURGE"):
            st.session_state.v_manifest = []; st.rerun()

    # TABS WORKSPACE
    tab_planner, tab_balancer, tab_db, tab_terminal = st.tabs(["📊 STACK PLANNER", "⚖️ LOAD BALANCER", "📦 PRODUCT CORE", "⚙️ SYSTEM LOGS"])

    with tab_planner:
        if st.session_state.v_manifest:
            k1, k2, k3, k4 = st.columns(4)
            t_m = sum(float(u['weight']) for u in st.session_state.v_manifest)
            k1.metric("UNITS", len(st.session_state.v_manifest))
            k2.metric("PCS TOTAL", sum(int(u.get('p_act', 1)) for u in st.session_state.v_manifest))
            k3.metric("GROSS MASS", f"{t_m} KG")
            k4.metric("UTILIZATION", f"{(t_m/veh['max_w'])*100:.1f}%")

            rem_manifest = [dict(u) for u in st.session_state.v_manifest]
            fleet_assigned = []
            while rem_manifest:
                res_st, res_w, n_p, ldm_r = V18StackEngine.pack_optimization(rem_manifest, veh)
                if not res_st: st.error("CRITICAL: UNIT OVERSIZE DETECTED"); break
                fleet_assigned.append({"stacks": res_st, "weight": res_w, "ldm": ldm_r})
                rem_manifest = n_p

            for idx, truck in enumerate(fleet_assigned):
                st.markdown(f'<div class="v-stack-panel">', unsafe_allow_html=True)
                st.markdown(f"### MISSION UNIT #{idx+1} | {v_key}", unsafe_allow_html=True)
                v_col, d_col = st.columns([2.8, 1])
                with v_col: st.plotly_chart(render_stack_cad_3d(veh, truck['stacks']), use_container_width=True)
                with d_col:
                    st.markdown("**KPI OPERACYJNE:**")
                    st.write(f"Zajęte LDM: **{truck['ldm']:.2f} m**")
                    st.write(f"Masa Ładunku: **{truck['weight']} kg**")
                    st.divider()
                    st.markdown("**MANIFEST ZAŁADUNKOWY:**")
                    counts = pd.Series([it['name'] for s in truck['stacks'] for it in s['items']]).value_counts().reset_index()
                    counts.columns = ['SKU', 'QTY']
                    ht = '<table class="v-tactical-table"><tr><th>SKU IDENTIFIER</th><th>QTY</th></tr>'
                    for _, r in counts.iterrows():
                        c = get_sku_chromatic_hex(r['SKU'])
                        ht += f'<tr><td><span style="color:{c}">■</span> {r["SKU"]}</td><td>{r["QTY"]}</td></tr>'
                    st.markdown(ht + '</table>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
        else: st.info("VORTEZA STACK: WAITING FOR MISSION DATA...")

    with tab_balancer:
        if st.session_state.v_manifest:
            st.markdown('<div class="v-stack-panel">', unsafe_allow_html=True)
            res_st, _, _, _ = V18StackEngine.pack_optimization(st.session_state.v_manifest, veh)
            process_load_balancer_ui(veh, res_st)
            st.markdown('</div>', unsafe_allow_html=True)
        else: st.warning("NO MANIFEST DATA FOR BALANCE ANALYSIS.")

    with tab_db:
        st.markdown("### 📦 PRODUCT ARCHITECTURE ADMINISTRATION")
        with st.expander("➕ REGISTER NEW ASSET PROTOCOL"):
            with st.form("AddAsset"):
                fn = st.text_input("Product Identifier (SKU)")
                c1, c2, c3 = st.columns(3)
                fl, fw, fh = c1.number_input("L (cm)", 120), c2.number_input("W (cm)", 80), c3.number_input("H (cm)", 100)
                fm, fi = st.number_input("Mass (kg)", 50), st.number_input("IPU", 1)
                ca1, ca2 = st.columns(2)
                fs, fr = ca1.checkbox("Stacking Approved", True), ca2.checkbox("Rotation Authorized", True)
                if st.form_submit_button("COMMIT TO MASTER DB"):
                    inventory.append({"name":fn,"length":fl,"width":fw,"height":fh,"weight":fm,"itemsPerCase":fi,"canStack":fs,"allowRotation":fr})
                    db_master_save(inventory); st.success("CORE SYNCED"); st.rerun()
        st.divider()
        if inventory:
            df_display = pd.DataFrame(inventory)
            edt_db = st.data_editor(df_display, use_container_width=True, num_rows="dynamic")
            if st.button("PUSH CHANGES TO ARCHIVE"):
                db_master_save(edt_db.to_dict('records')); st.success("ARCHIVE SYNC COMPLETE")

    with tab_terminal:
        st.code(f"VORTEZA STACK v18.0\nSYSTEM: Titan-v18\nSESSION: {datetime.now()}\nSTATUS: Nominal", language="bash")

if __name__ == "__main__":
    main()
