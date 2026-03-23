# -*- coding: utf-8 -*-
"""
================================================================================
SYSTEM: VORTEZA STACK 
VERSION: 24.0 | APEX ULTIMATE PLUS
FIRM: VORTEZA SYSTEMS
STATUS: ENTERPRISE PRODUCTION READY | FULL MONOLITH SOURCE
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
# 1. ŚRODOWISKO I REJESTR INŻYNIERYJNY FLOTY
# ==============================================================================
st.set_page_config(
    page_title="VORTEZA STACK v24.0",
    layout="wide",
    initial_sidebar_state="expanded",
    page_icon="🕋"
)

# SPECYFIKACJA TECHNICZNA JEDNOSTEK TRANSPORTOWYCH VORTEZA
# Wymiary: cm | Masa: kg
FLEET_MASTER_DATA = {
    "TIR FTL Mega 13.6m": {
        "max_w": 24000, "L": 1360, "W": 248, "H": 300, 
        "ldm_max": 13.6, "axles": 3, "wheelbase": 850, "tare": 14500, "cab_l": 230
    },
    "TIR FTL Standard 13.6m": {
        "max_w": 24000, "L": 1360, "W": 248, "H": 275, 
        "ldm_max": 13.6, "axles": 3, "wheelbase": 850, "tare": 13800, "cab_l": 230
    },
    "Solo 9m Heavy Duty": {
        "max_w": 9500, "L": 920, "W": 245, "H": 270, 
        "ldm_max": 9.2, "axles": 2, "wheelbase": 550, "tare": 8500, "cab_l": 200
    },
    "Solo 7m Medium": {
        "max_w": 7000, "L": 720, "W": 245, "H": 260, 
        "ldm_max": 7.2, "axles": 2, "wheelbase": 480, "tare": 6200, "cab_l": 180
    },
    "BUS XL Express": {
        "max_w": 1300, "L": 485, "W": 175, "H": 220, 
        "ldm_max": 4.8, "axles": 2, "wheelbase": 320, "tare": 2250, "cab_l": 140
    }
}

# ==============================================================================
# 2. BRANDING VORTEZA & ADVANCED UI ENGINE
# ==============================================================================
def load_vorteza_asset_b64(file_path):
    """Bezpieczne ładowanie zasobów binarnych dla warstwy CSS."""
    try:
        if os.path.exists(file_path):
            with open(file_path, 'rb') as f:
                return base64.b64encode(f.read()).decode()
        return ""
    except: return ""

def inject_vorteza_stack_ui():
    """Wstrzykuje rygorystyczny design system VORTEZA STACK."""
    bg_data = load_vorteza_asset_b64('bg_vorteza.png')
    
    st.markdown(f"""
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;600;700&family=JetBrains+Mono:wght@300;400;500&display=swap');
            
            :root {{
                --v-copper: #B58863;
                --v-copper-glow: rgba(181, 136, 99, 0.4);
                --v-dark-obsidian: #020202;
                --v-panel-bg: rgba(6, 6, 6, 0.98);
                --v-border: rgba(181, 136, 99, 0.2);
                --v-neon-green: #00FF41;
                --v-alert-red: #FF3131;
            }}

            /* Globalna architektura wizualna */
            .stApp {{
                background-image: url("data:image/png;base64,{bg_data}");
                background-size: cover;
                background-attachment: fixed;
                color: #FFFFFF;
                font-family: 'Montserrat', sans-serif;
            }}

            /* System Kafelkowy VORTEZA STACK */
            .v-tile-apex {{
                background: var(--v-panel-bg);
                padding: 3rem;
                border: 1px solid var(--v-border);
                border-left: 15px solid var(--v-copper);
                box-shadow: 0 50px 120px rgba(0,0,0,1);
                margin-bottom: 3.5rem;
                backdrop-filter: blur(50px);
            }}

            section[data-testid="stSidebar"] {{
                background-color: rgba(3, 3, 3, 0.99) !important;
                border-right: 1px solid var(--v-border);
                width: 480px !important;
                backdrop-filter: blur(35px);
            }}

            h1, h2, h3 {{ 
                color: var(--v-copper) !important; 
                text-transform: uppercase; 
                letter-spacing: 12px !important; 
                font-weight: 700 !important; 
                text-shadow: 0 0 30px rgba(181, 136, 99, 0.3);
            }}

            /* Metryki Apex Inżynieryjne */
            [data-testid="stMetricValue"] {{ 
                color: var(--v-copper) !important; 
                font-family: 'JetBrains Mono', monospace !important; 
                font-size: 3.8rem !important;
                font-weight: 300 !important;
            }}
            [data-testid="stMetricLabel"] {{
                color: #666 !important;
                text-transform: uppercase;
                letter-spacing: 4px;
                font-weight: 700;
            }}

            /* Master Controllers (Przyciski) */
            .stButton > button {{
                background: linear-gradient(180deg, #0a0a0a, #1a1a1a);
                color: var(--v-copper);
                border: 2px solid var(--v-copper);
                padding: 1.8rem;
                text-transform: uppercase;
                letter-spacing: 10px;
                font-weight: 700;
                width: 100%;
                transition: 0.8s all cubic-bezier(0.19, 1, 0.22, 1);
                border-radius: 0;
            }}
            .stButton > button:hover {{
                background: var(--v-copper);
                color: #000;
                box-shadow: 0 0 120px rgba(181, 136, 99, 0.9);
                transform: translateY(-5px);
            }}

            /* Tabele Taktyczne */
            .v-table-tactical {{ 
                width: 100%; 
                border-collapse: collapse; 
                margin-top: 40px; 
                border: 1px solid #111;
            }}
            .v-table-tactical th {{ 
                background: #000;
                color: var(--v-copper); 
                text-align: left; 
                font-size: 0.85rem; 
                text-transform: uppercase; 
                border-bottom: 3px solid #333; 
                padding: 25px; 
                letter-spacing: 3px;
            }}
            .v-table-tactical td {{ 
                padding: 20px 25px; 
                border-bottom: 1px solid #111; 
                color: #CCC; 
                font-size: 1rem; 
            }}
            .v-table-tactical tr:hover {{ background: rgba(181,136,99,0.05); }}

            /* Load Balancer Visualization */
            .v-rail-track {{
                width: 100%; height: 35px; background: #050505; border-radius: 17px; position: relative; border: 2px solid #222; margin: 60px 0;
                box-shadow: inset 0 0 25px #000;
            }}
            .v-cog-pointer {{
                position: absolute; width: 10px; height: 70px; top: -17.5px; background: var(--v-neon-green); 
                box-shadow: 0 0 40px var(--v-neon-green); border-radius: 5px;
                transition: left 1.5s cubic-bezier(0.19, 1, 0.22, 1);
            }}
            
            /* Unit Status Badges */
            .v-badge-unit {{
                background: rgba(181,136,99,0.1);
                border: 1px solid var(--v-copper);
                padding: 20px;
                font-family: 'JetBrains Mono', monospace;
                font-size: 0.85rem;
                margin-bottom: 25px;
                color: var(--v-copper);
            }}

            /* Data Editor UI Fix */
            div[data-testid="stDataEditor"] {{
                background: rgba(10,10,10,0.9) !important;
                border: 1px solid var(--v-border) !important;
            }}
        </style>
    """, unsafe_allow_html=True)

# ==============================================================================
# 3. KONTROLA DOSTĘPU (VORTEZA AUTH PROTOCOL)
# ==============================================================================
def check_authorized_clearance():
    """Weryfikuje poświadczenia operatora systemu VORTEZA STACK."""
    if "authorized" not in st.session_state:
        st.session_state.authorized = False

    if not st.session_state.authorized:
        try:
            sys_key = str(st.secrets.get("password", "vorteza2026"))
        except:
            sys_key = "vorteza2026"

        st.markdown("<br><br><br><br><br><br><br>", unsafe_allow_html=True)
        _, col_auth, _ = st.columns([1, 2.5, 1])
        with col_auth:
            with st.form("StackAuthTerminal"):
                st.markdown("<h2 style='text-align:center;'>VORTEZA STACK</h2>", unsafe_allow_html=True)
                st.markdown("<p style='text-align:center; color:#333; font-size:0.75rem; letter-spacing:6px;'>ENCRYPTED ACCESS ONLY</p>", unsafe_allow_html=True)
                pwd_in = st.text_input("GOLIATH CORE SECURITY KEY", type="password")
                if st.form_submit_button("VALIDATE CREDENTIALS"):
                    if pwd_in == sys_key:
                        st.session_state.authorized = True
                        st.rerun()
                    else:
                        st.error("ACCESS DENIED: INVALID SYSTEM KEY DETECTED")
        return False
    return True

# ==============================================================================
# 4. CHROMATIC SKU ENGINE (STABILNY SILNIK KOLORÓW)
# ==============================================================================
def get_vorteza_sku_hex(sku_name):
    """Zwraca unikalny kolor metaliczny dla każdego SKU z palety industrialnej."""
    palette = [
        "#B58863", "#D4AF37", "#8E6A4D", "#5E4633", "#A67C52", 
        "#2C3E50", "#34495E", "#1A252F", "#16A085", "#27AE60",
        "#7F8C8D", "#95A5A6", "#BDC3C7", "#E67E22", "#D35400",
        "#C0392B", "#E74C3C", "#8E44AD", "#9B59B6", "#2980B9",
        "#F1C40F", "#2ECC71", "#3498DB", "#E67E22", "#1ABC9C"
    ]
    # Deterministyczne ziarno oparte na nazwie SKU
    random.seed(sum(ord(c) for c in sku_name))
    return random.choice(palette)

# ==============================================================================
# 5. RENDERER CAD-3D STACK (EXPLICIT VERTEX ENGINE v24.0)
# ==============================================================================
def build_box_cad_geometry(x, y, z, dx, dy, dz, color, name):
    """Tworzy matematycznie poprawną geometrię 3D dla pojedynczej jednostki."""
    # 8 Wierzchołków
    vx = [x, x+dx, x+dx, x, x, x+dx, x+dx, x]
    vy = [y, y, y+dy, y+dy, y, y, y+dy, y+dy]
    vz = [z, z, z, z, z+dz, z+dz, z+dz, z+dz]
    
    # 12 Trójkątów (6 ścian)
    i_map = [7, 0, 0, 0, 4, 4, 6, 6, 4, 0, 3, 2]
    j_map = [3, 4, 1, 2, 5, 6, 5, 2, 0, 1, 6, 3]
    k_map = [0, 7, 2, 3, 6, 7, 1, 1, 5, 5, 7, 6]
    
    mesh = go.Mesh3d(
        x=vx, y=vy, z=vz, i=i_map, j=j_map, k=k_map,
        color=color, opacity=0.99, name=name,
        flatshading=True, lighting=dict(ambient=0.4, diffuse=0.8, specular=1, roughness=0.1),
        hovertemplate=f"<b>{name}</b><br>D: {dx}cm W: {dy}cm H: {dz}cm<extra></extra>"
    )
    
    # Krawędzie Hi-Def (Outline)
    lx = [x, x+dx, x+dx, x, x, x, x+dx, x+dx, x, x, x+dx, x+dx, x+dx, x+dx, x, x]
    ly = [y, y, y+dy, y+dy, y, y, y, y+dy, y+dy, y+dy, y+dy, y, y, y+dy, y+dy, y]
    lz = [z, z, z, z, z, z+dz, z+dz, z, z, z+dz, z+dz, z+dz, z, z, z+dz, z+dz]
    
    lines = go.Scatter3d(
        x=lx, y=ly, z=lz, mode='lines',
        line=dict(color='black', width=3), hoverinfo='skip'
    )
    
    return [mesh, lines]

def render_vorteza_cad_3d(vehicle_specs, cargo_stacks):
    """Generuje kompletny inżynieryjny model 3D naczepy wraz z ładunkiem."""
    fig = go.Figure()
    L, W, H = vehicle_specs['L'], vehicle_specs['W'], vehicle_specs['H']

    # --- INFRASTRUKTURA POJAZDU (CAD DETAIL) ---
    # Podłoga i Rama główna
    fig.add_trace(go.Mesh3d(
        x=[0, L, L, 0], y=[0, 0, W, W], z=[-15, -15, -15, -15],
        color='#151515', opacity=1, hoverinfo='skip'
    ))
    
    # Koła, Osie i Felgi Miedziane
    axles = vehicle_specs.get('axles', 3)
    ax_dist = 145
    rear_base_x = L - 450 if L > 800 else L - 180
    
    for a in range(axles):
        ax_x = rear_base_x + (a * ax_dist)
        if ax_x < L:
            for side in [-40, W+25]:
                # Opona
                fig.add_trace(go.Mesh3d(
                    x=[ax_x-60, ax_x+60, ax_x+60, ax_x-60], y=[side, side, side+18, side+18], 
                    z=[-85, -85, -15, -15], color='#000', opacity=1, hoverinfo='skip'
                ))
                # Felga VORTEZA
                fig.add_trace(go.Mesh3d(
                    x=[ax_x-25, ax_x+25, ax_x+25, ax_x-25], y=[side-2, side-2, side, side], 
                    z=[-60, -60, -35, -35], color='#B58863', opacity=0.9, hoverinfo='skip'
                ))

    # Kabina Commander
    cab_l = vehicle_specs.get('cab_l', 230)
    fig.add_trace(go.Mesh3d(
        x=[-cab_l, 0, 0, -cab_l, -cab_l, 0, 0, -cab_l],
        y=[-45, -45, W+45, W+45, -45, -45, W+45, W+45],
        z=[0, 0, 0, 0, H*1.05, H*1.05, H*1.05, H*1.05],
        i=[7,0,0,0,4,4,6,6,4,0,3,2], j=[3,4,1,2,5,6,5,2,0,1,6,3], k=[0,7,2,3,6,7,1,1,5,5,7,6],
        color='#050505', opacity=1, name="UNIT_COMMAND_CAB"
    ))

    # Szkielet Naczepy (Miedziana Klatka)
    skeleton_lines = [
        ([0, L], [0, 0], [0, 0]), ([0, L], [W, W], [0, 0]), ([0, 0], [0, W], [0, 0]), ([L, L], [0, W], [0, 0]),
        ([0, 0], [0, 0], [0, H]), ([0, 0], [W, W], [0, H]), ([0, L], [0, 0], [H, H]), ([0, L], [W, W], [H, H]),
        ([L, L], [0, 0], [0, H]), ([L, L], [W, W], [0, H])
    ]
    for lx, ly, lz in skeleton_lines:
        fig.add_trace(go.Scatter3d(x=lx, y=ly, z=lz, mode='lines', line=dict(color='#B58863', width=12), hoverinfo='skip'))

    # --- RENDER ŁADUNKU (CHROMATIC CLUSTERS) ---
    for cluster in cargo_stacks:
        for unit in cluster['items']:
            x, y, z = cluster['x'], cluster['y'], unit['z']
            dx, dy, dz = unit['w_fit'], unit['l_fit'], unit['height']
            
            p_color = get_vorteza_sku_hex(unit['name'])
            cube_parts = build_box_cad_geometry(x, y, z, dx, dy, dz, p_color, unit['name'])
            for p in cube_parts:
                fig.add_trace(p)

    fig.update_layout(
        scene=dict(
            aspectmode='data', xaxis_visible=False, yaxis_visible=False, zaxis_visible=False,
            camera=dict(eye=dict(x=2.5, y=2.5, z=2.0)), bgcolor='rgba(0,0,0,0)'
        ),
        paper_bgcolor='rgba(0,0,0,0)', margin=dict(l=0, r=0, b=0, t=0), showlegend=False
    )
    return fig

# ==============================================================================
# 6. SILNIK PAKOWANIA V-ENGINE 24.0 (SUPREME OPTIMIZER)
# ==============================================================================
class V24SupremeEngine:
    """Zaawansowany algorytm pakowania 3D z kontrolą V-PERMIT i balansem X."""
    
    @staticmethod
    def solve(cargo_list, vehicle, x_offset=0):
        # Priorytetyzacja FFD: 1. No-Stack, 2. No-Rotation, 3. Powierzchnia podstawy
        items_sorted = sorted(cargo_list, 
                             key=lambda x: (not x.get('canStack', True), 
                                            not x.get('allowRotation', True), 
                                            x['width']*x['length']), 
                             reverse=True)
        
        placed_stacks = []
        failed_units = []
        total_weight = 0
        cx, cy, current_row_max_w = x_offset, 0, 0

        for unit in items_sorted:
            if total_weight + unit['weight'] > vehicle['max_w']:
                failed_units.append(unit); continue
            
            # STACKING LOGIC
            is_stacked = False
            if unit.get('canStack', True):
                for s in placed_stacks:
                    # Dopasowanie z uwzględnieniem ZABLOKOWANEJ rotacji
                    if unit.get('allowRotation', True):
                        dim_fit = (unit['width'] <= s['w'] and unit['length'] <= s['l']) or \
                                  (unit['length'] <= s['w'] and unit['width'] <= s['l'])
                    else:
                        dim_fit = (unit['width'] <= s['w'] and unit['length'] <= s['l'])
                    
                    if dim_fit and (s['curH'] + unit['height'] <= vehicle['H']):
                        u_copy = unit.copy(); u_copy['z'] = s['curH']
                        u_copy['w_fit'], u_copy['l_fit'] = s['w'], s['l']
                        s['items'].append(u_copy); s['curH'] += unit['height']
                        total_weight += unit['weight']; is_stacked = True; break
            
            if is_stacked: continue

            # FLOOR LOGIC + V-PERMIT ROTATION
            is_placed = False
            orientations = [(unit['width'], unit['length']), (unit['length'], unit['width'])] if unit.get('allowRotation', True) else [(unit['width'], unit['length'])]
            
            for fw, fl in orientations:
                if cy + fl <= vehicle['W'] and cx + fw <= vehicle['L']:
                    u_c = unit.copy(); u_c['z'] = 0; u_c['w_fit'], u_c['l_fit'] = fw, fl
                    placed_stacks.append({'x':cx, 'y':cy, 'w':fw, 'l':fl, 'curH':unit['height'], 'items':[u_c]})
                    cy += fl; current_row_max_w = max(current_row_max_w, fw)
                    total_weight += unit['weight']; is_placed = True; break
                elif cx + current_row_max_w + fw <= vehicle['L'] and fl <= vehicle['W']:
                    cx += current_row_max_w; cy = 0; current_row_max_w = fw
                    u_c = unit.copy(); u_c['z'] = 0; u_c['w_fit'], u_c['l_fit'] = fw, fl
                    placed_stacks.append({'x':cx, 'y':cy, 'w':fw, 'l':fl, 'curH':unit['height'], 'items':[u_c]})
                    cy += fl; total_weight += unit['weight']; is_placed = True; break
            
            if not is_placed: failed_units.append(unit)
        
        ldm_res = (max([s['x'] + s['w'] for s in placed_stacks]) / 100) if placed_stacks else 0
        return placed_stacks, total_weight, failed_units, ldm_res

# ==============================================================================
# 7. ANALITYKA INŻYNIERYJNA (TACTICAL LOAD BALANCER)
# ==============================================================================
def process_load_bal_ui(vehicle, stacks):
    """Oblicza środek ciężkości (CoG) i wizualizuje balans masy."""
    if not stacks: return
    
    t_moment, t_weight = 0, 0
    for s in stacks:
        for it in s['items']:
            item_center_x = s['x'] + (it['w_fit'] / 2)
            t_moment += (item_center_x * it['weight'])
            t_weight += it['weight']
    
    cog_x = t_moment / t_weight if t_weight > 0 else 0
    cog_p = (cog_x / vehicle['L']) * 100
    
    st.markdown("### ⚖️ CENTER OF GRAVITY ANALYSIS (CoG)")
    st.write(f"Położenie środka ciężkości ładunku: **{cog_x/100:.2f} m** od kabiny")
    
    marker_clr = "#00FF41" if 35 < cog_p < 65 else "#FF3131"
    
    st.markdown(f"""
        <div class="v-rail-track">
            <div class="v-cog-pointer" style="left: {cog_p}%; background: {marker_clr}; box-shadow: 0 0 40px {marker_clr};"></div>
            <div style="position:absolute; left:20px; top:50px; font-size:0.6rem; color:#888;">CABIN AXLES</div>
            <div style="position:absolute; right:20px; top:50px; font-size:0.6rem; color:#888;">REAR AXLES</div>
        </div>
        <br>
    """, unsafe_allow_html=True)
    
    if cog_p < 35: st.warning("ALARM: PRZECIĄŻENIE PRZODU. Zwiększ OFFSET ładunku.")
    elif cog_p > 65: st.warning("ALARM: ODCIĄŻENIE OSI SKRĘTNEJ. Zmniejsz OFFSET ładunku.")
    else: st.success("STATUS NOMINALNY: Balans masy optymalny.")

# ==============================================================================
# 8. DATA I/O (MASTER DB ENGINE)
# ==============================================================================
def db_core_load():
    if os.path.exists('products.json'):
        try:
            with open('products.json', 'r', encoding='utf-8') as f: return json.load(f)
        except: return []
    return []

def db_core_save(data):
    with open('products.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

# ==============================================================================
# 9. GŁÓWNA ARCHITEKTURA INTERFEJSU (VORTEZA STACK)
# ==============================================================================
def main():
    inject_vorteza_stack_ui()
    if not check_authorized_clearance(): return

    # Stan Manifestu i Inwentarza
    if 'v_manifest' not in st.session_state: st.session_state.v_manifest = []
    inventory = db_core_load()

    # --- TOP CONTROL BAR ---
    hc1, hc2, hc3 = st.columns([1, 4, 1])
    with hc1:
        logo_b64 = load_vorteza_asset_b64('logo_vorteza.png')
        if logo_b64: st.markdown(f'<img src="data:image/png;base64,{logo_b64}" width="180">', unsafe_allow_html=True)
        else: st.markdown("### VORTEZA")
    with hc2:
        st.markdown("<h1>VORTEZA STACK</h1>", unsafe_allow_html=True)
        st.markdown(f"<p style='color:#444; letter-spacing:8px; font-size:0.75rem; font-weight:600;'>APEX ULTIMATE PLUS v24.0 | STATUS: ACTIVE</p>", unsafe_allow_html=True)
    with hc3:
        if st.button("TERMINATE"):
            st.session_state.authorized = False; st.rerun()

    # --- SIDEBAR: MISSION CONTROL ---
    with st.sidebar:
        st.markdown("### 📡 FLEET CONSOLE")
        v_key = st.selectbox("TRANSPORT UNIT", list(FLEET_MASTER_DATA.keys()))
        veh = FLEET_MASTER_DATA[v_key]
        
        st.divider()
        st.markdown("### ⚖️ DYNAMIC POSITIONING")
        x_shift = st.slider("OFFSET OD ŚCIANY (cm)", 0, veh['L']-200, 0)
        st.caption("Skoryguj środek ciężkości przesuwając ładunek na tył.")
        
        st.divider()
        st.markdown("### 📥 CARGO ENTRY")
        p_titles = [p['name'] for p in inventory]
        sel_sku = st.selectbox("SKU SELECTOR SERVICE", p_titles, index=None)
        
        if sel_sku:
            p_ref = next(p for p in inventory if p['name'] == sel_sku)
            ipc = p_ref.get('itemsPerCase', 1)
            p_rot = p_ref.get('allowRotation', True)
            st.markdown(f"""
                <div class='v-badge-unit'>
                    SKU: {sel_sku}<br>STANDARD: {ipc} PCS/CASE<br>
                    OBRÓT: {'<span style="color:#00FF41">AUTHORIZED</span>' if p_rot else '<span style="color:#FF3131">LOCKED</span>'}
                </div>
            """, unsafe_allow_html=True)
            p_qty = st.number_input("QUANTITY (TOTAL PCS)", min_value=1, value=ipc)
            n_units = math.ceil(p_qty / ipc)
            if st.button("APPEND TO MANIFEST", type="primary"):
                for i in range(n_units):
                    u_entry = p_ref.copy()
                    u_entry['p_act'] = ipc if (i < n_units - 1 or p_qty % ipc == 0) else (p_qty % ipc)
                    st.session_state.v_manifest.append(u_entry)
                st.rerun()
        if st.button("PURGE ALL DATA"):
            st.session_state.v_manifest = []; st.rerun()

    # --- WORKSPACE TABS ---
    tab_planner, tab_db, tab_terminal = st.tabs(["📊 TACTICAL PLANNER", "📦 MASTER INVENTORY", "⚙️ SYSTEM LOGS"])

    # TAB 1: PLANNER & VISUALIZER
    with tab_planner:
        if st.session_state.v_manifest:
            k1, k2, k3, k4 = st.columns(4)
            total_kg = sum(float(u['weight']) for u in st.session_state.v_manifest)
            k1.metric("CASES", len(st.session_state.v_manifest))
            k2.metric("PCS TOTAL", sum(int(u.get('p_act', 1)) for u in st.session_state.v_manifest))
            k3.metric("GROSS WEIGHT", f"{total_kg} KG")
            k4.metric("UTILIZATION", f"{(total_kg/veh['max_w'])*100:.1f}%")

            rem_manifest = [dict(u) for u in st.session_state.v_manifest]
            assigned_fleet = []
            while rem_manifest:
                res_s, res_w, n_p, ldm_r = V24SupremeEngine.solve(rem_manifest, veh, x_offset=x_shift)
                if not res_s: st.error("CRITICAL: UNIT OVERSIZE DETECTED."); break
                assigned_fleet.append({"stacks": res_s, "weight": res_w, "ldm": ldm_r})
                rem_manifest = n_p

            for idx, truck in enumerate(assigned_fleet):
                st.markdown(f'<div class="v-tile-apex">', unsafe_allow_html=True)
                st.markdown(f"### MISSION UNIT #{idx+1} | {v_key}", unsafe_allow_html=True)
                v_col, d_col = st.columns([2.8, 1])
                with v_col:
                    st.plotly_chart(render_vorteza_cad_3d(veh, truck['stacks']), use_container_width=True)
                    process_load_bal_ui(veh, truck['stacks'])
                with d_col:
                    st.markdown("**OPERATIONAL KPI:**")
                    st.write(f"Zajęte LDM: **{truck['ldm']:.2f} m**")
                    st.write(f"Masa Netto: **{truck['weight']} kg**")
                    st.divider()
                    st.markdown("**MANIFEST ZAŁADUNKOWY:**")
                    # FIX: Poprawiony błąd KeyError kolumn
                    sku_agg = pd.Series([it['name'] for s in truck['stacks'] for it in s['items']]).value_counts().reset_index()
                    sku_agg.columns = ['SKU IDENTIFIER', 'QTY']
                    
                    h_table = '<table class="v-table-tactical"><tr><th>SKU</th><th>QTY</th></tr>'
                    for _, r in sku_agg.iterrows():
                        c_h = get_vorteza_sku_hex(r['SKU IDENTIFIER'])
                        h_table += f'<tr><td><span style="color:{c_h}">■</span> {r["SKU IDENTIFIER"]}</td><td>{r["QTY"]}</td></tr>'
                    st.markdown(h_table + '</table>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.info("VORTEZA STACK STATUS: WAITING FOR MISSION DATA.")

    # TAB 2: INVENTORY (CRUD)
    with tab_db:
        st.markdown("### 📦 GLOBAL SKU ARCHIVE ADMINISTRATION")
        with st.expander("➕ REGISTER NEW ASSET PROTOCOL"):
            with st.form("AddAssetSupreme"):
                fn = st.text_input("SKU Name / Identifier")
                c_i1, c_i2, c_i3 = st.columns(3)
                fl = c_i1.number_input("L (cm)", 120)
                fw = c_i2.number_input("W (cm)", 80)
                fh = c_i3.number_input("H (cm)", 100)
                col_w, col_i = st.columns(2)
                fm = col_w.number_input("Mass (kg)", 50)
                fi = col_i.number_input("Items Per Case (IPU)", 1)
                ca1, ca2 = st.columns(2)
                fs = ca1.checkbox("Stacking Permission", True)
                fr = ca2.checkbox("Rotation Authorized", True)
                if st.form_submit_button("COMMIT TO MASTER DATABASE"):
                    inventory.append({"name":fn,"length":fl,"width":fw,"height":fh,"weight":fm,"itemsPerCase":fi,"canStack":fs,"allowRotation":fr})
                    db_core_save(inventory); st.success("CORE SYNCED"); st.rerun()
        st.divider()
        if inventory:
            df_display = pd.DataFrame(inventory)
            edt_db = st.data_editor(df_display, use_container_width=True, num_rows="dynamic", key="v24_editor")
            if st.button("PUSH CHANGES TO ARCHIVE", type="primary"):
                db_core_save(edt_db.to_dict('records')); st.success("ARCHIVE SYNC COMPLETE")

    # TAB 3: LOGS
    with tab_terminal:
        st.code(f"SYSTEM: VORTEZA STACK v24.0\nCORE: Supreme-Apex-Optimizer\nTIME: {datetime.now()}\nSTATUS: Nominal", language="bash")

if __name__ == "__main__":
    main()

[
  {"id": 1, "name": "17-23\" - plastic case", "width": 80, "length": 60, "height": 20, "weight": 20, "canStack": true, "itemsPerCase": 1},
  {"id": 2, "name": "24-32\" - plastic case", "width": 60, "length": 40, "height": 20, "weight": 15, "canStack": true, "itemsPerCase": 1},
  {"id": 3, "name": "32\" - triple - STANDARD", "width": 90, "length": 50, "height": 70, "weight": 50, "canStack": true, "itemsPerCase": 3},
  {"id": 4, "name": "43\" - triple - STANDARD", "width": 112, "length": 42, "height": 80, "weight": 90, "canStack": true, "itemsPerCase": 3},
  {"id": 5, "name": "45\"-55\" - double - STANDARD", "width": 140, "length": 42, "height": 100, "weight": 150, "canStack": true, "itemsPerCase": 2},
  {"id": 6, "name": "60-65\" - double - STANDARD", "width": 160, "length": 40, "height": 230, "weight": 200, "canStack": false, "itemsPerCase": 2},
  {"id": 7, "name": "75-86\" - double - STANDARD", "width": 210, "length": 40, "height": 230, "weight": 230, "canStack": false, "itemsPerCase": 2},
  {"id": 8, "name": "98\" - double - STANDARD", "width": 250, "length": 70, "height": 230, "weight": 400, "canStack": false, "itemsPerCase": 1},
  {"id": 9, "name": "P1 lub 1.58 ABSEN", "width": 108, "length": 71, "height": 62, "weight": 103, "canStack": true, "itemsPerCase": 8},
  {"id": 10, "name": "P1.9 UNILUMIN UPAD IV / S-FLEX", "width": 117, "length": 57, "height": 79, "weight": 115, "canStack": true, "itemsPerCase": 8},
  {"id": 11, "name": "P2.6 UNILUMIN UPAD IV", "width": 117, "length": 57, "height": 79, "weight": 116, "canStack": true, "itemsPerCase": 8},
  {"id": 12, "name": "P2.6 UNILUMIN UPAD IV / C-CUBE", "width": 117, "length": 57, "height": 79, "weight": 125, "canStack": true, "itemsPerCase": 8},
  {"id": 13, "name": "P2.6 UNILUMIN UPAD IV / S-FLEX", "width": 117, "length": 57, "height": 79, "weight": 121, "canStack": true, "itemsPerCase": 8},
  {"id": 14, "name": "P2.06 frameLED (STANDARD / CORNERS)", "width": 86, "length": 62, "height": 100, "weight": 118, "canStack": true, "itemsPerCase": 10},
  {"id": 15, "name": "P2.06 frameLED (CURVED INNER / OUTER)", "width": 84, "length": 64, "height": 100, "weight": 76.5, "canStack": true, "itemsPerCase": 5},
  {"id": 16, "name": "P2 ESD 2,84 - STANDARD", "width": 110, "length": 60, "height": 80, "weight": 115, "canStack": true, "itemsPerCase": 8},
  {"id": 17, "name": "P2 ESD Corner - nonstandard", "width": 90, "length": 70, "height": 80, "weight": 104, "canStack": true, "itemsPerCase": 8},
  {"id": 18, "name": "P3.9 Yestech - STANDARD", "width": 114, "length": 60, "height": 80, "weight": 125, "canStack": true, "itemsPerCase": 10},
  {"id": 19, "name": "P2.6 Yestech - INDOOR", "width": 117, "length": 64, "height": 76, "weight": 122, "canStack": true, "itemsPerCase": 10},
  {"id": 20, "name": "P2.6 Yestech - INDOOR CUBE", "width": 117, "length": 64, "height": 76, "weight": 122, "canStack": true, "itemsPerCase": 10},
  {"id": 21, "name": "P3 Yestech Corner - nonstandard", "width": 120, "length": 60, "height": 80, "weight": 113, "canStack": true, "itemsPerCase": 12},
  {"id": 22, "name": "P2.9 Yestech FLOOR - STANDARD", "width": 114, "length": 60, "height": 76, "weight": 142, "canStack": true, "itemsPerCase": 10},
  {"id": 23, "name": "P3.9 HOXLED / TRANSPARENT", "width": 114, "length": 80, "height": 130, "weight": 144, "canStack": true, "itemsPerCase": 10},
  {"id": 24, "name": "NEC E326 - STANDARD", "width": 70, "length": 50, "height": 70, "weight": 90, "canStack": true, "itemsPerCase": 3},
  {"id": 25, "name": "NEC C431 - STANDARD", "width": 80, "length": 50, "height": 80, "weight": 120, "canStack": true, "itemsPerCase": 3},
  {"id": 26, "name": "NEC C501 - STANDARD", "width": 100, "length": 50, "height": 100, "weight": 140, "canStack": true, "itemsPerCase": 2},
  {"id": 27, "name": "NEC C551 - STANDARD", "width": 100, "length": 50, "height": 100, "weight": 140, "canStack": true, "itemsPerCase": 2},
  {"id": 28, "name": "SAMSUNG series 7 - STANDARD", "width": 110, "length": 50, "height": 60, "weight": 160, "canStack": true, "itemsPerCase": 2},
  {"id": 29, "name": "NEC C861 86\" - STANDARD", "width": 140, "length": 40, "height": 230, "weight": 210, "canStack": true, "itemsPerCase": 1},
  {"id": 30, "name": "NEC C981 98\" - STANDARD", "width": 170, "length": 70, "height": 230, "weight": 250, "canStack": true, "itemsPerCase": 1},
  {"id": 31, "name": "NEC X981 98\" TOUCHSCREEN - STANDARD", "width": 170, "length": 70, "height": 230, "weight": 250, "canStack": true, "itemsPerCase": 1},
  {"id": 32, "name": "case for accessories RED", "width": 120, "length": 60, "height": 80, "weight": 120, "canStack": true, "itemsPerCase": 5},
  {"id": 33, "name": "case for accessories ARUM", "width": 120, "length": 70, "height": 120, "weight": 140, "canStack": true, "itemsPerCase": 1},
  {"id": 34, "name": "case for accessories NEC", "width": 100, "length": 50, "height": 80, "weight": 120, "canStack": true, "itemsPerCase": 3},
  {"id": 35, "name": "ELSTAR L42 LED", "width": 80, "length": 50, "height": 50, "weight": 37, "canStack": true, "itemsPerCase": 5},
  {"id": 36, "name": "CAMEO PAR 64 LED", "width": 60, "length": 80, "height": 44, "weight": 50, "canStack": true, "itemsPerCase": 8},
  {"id": 37, "name": "FLASH PAR 64 LED", "width": 60, "length": 80, "height": 44, "weight": 50, "canStack": true, "itemsPerCase": 8},
  {"id": 38, "name": "PROLIGHTS / ECLEXPO FLOOD300W / DMX5", "width": 120, "length": 60, "height": 62, "weight": 88, "canStack": true, "itemsPerCase": 6},
  {"id": 39, "name": "PROLIGHTS / ASTRA HYBRID 330 / DMX-5", "width": 87, "length": 58, "height": 78, "weight": 120, "canStack": true, "itemsPerCase": 2},
  {"id": 40, "name": "GRANDMA 2 LIGHTING", "width": 102, "length": 33, "height": 93, "weight": 37, "canStack": false, "itemsPerCase": 1},
  {"id": 41, "name": "PROLIGHTS / ECLPROFILE CT+", "width": 1, "length": 1, "height": 1, "weight": 0.1, "canStack": true, "itemsPerCase": 1},
  {"id": 42, "name": "PROLIGHTS / JET SPOT4Z / DMX5", "width": 110, "length": 60, "height": 78, "weight": 131, "canStack": true, "itemsPerCase": 4},
  {"id": 43, "name": "PROLIGHTS / ASTRA WASH19 / DMX5", "width": 120, "length": 60, "height": 75, "weight": 134, "canStack": true, "itemsPerCase": 4},
  {"id": 44, "name": "PROLIGHTS / SOLAR 27Q / DMX5", "width": 120, "length": 60, "height": 113, "weight": 113, "canStack": true, "itemsPerCase": 10},
  {"id": 45, "name": "PROLIGHTS / STUDIO COB FC 150W RGB / DMX5", "width": 132, "length": 73, "height": 57, "weight": 95.4, "canStack": true, "itemsPerCase": 8},
  {"id": 46, "name": "CHAINMASTER / D8 PLUS / 320KG / 10M / ELECTRIC", "width": 80, "length": 60, "height": 97, "weight": 97, "canStack": true, "itemsPerCase": 2},
  {"id": 47, "name": "CHAINMASTER / D8 PLUS / 500KG / 32M / ELECTRIC", "width": 80, "length": 60, "height": 98, "weight": 98, "canStack": true, "itemsPerCase": 3},
  {"id": 48, "name": "MANUAL CHAIN HOIST (DELTA BLACK, DELTA YELLOW, EUROLITE, THIELE)", "width": 30, "length": 30, "height": 40, "weight": 40, "canStack": true, "itemsPerCase": 2},
  {"id": 49, "name": "speaker RCF 310", "width": 60, "length": 40, "height": 40, "weight": 40, "canStack": true, "itemsPerCase": 3},
  {"id": 50, "name": "speaker MASK 6", "width": 40, "length": 30, "height": 60, "weight": 60, "canStack": true, "itemsPerCase": 4},
  {"id": 51, "name": "truss cart 14x2 (200x60x335 cm)", "width": 200, "length": 60, "height": 350, "weight": 350, "canStack": false, "itemsPerCase": 1},
  {"id": 52, "name": "truss cart 14x3 (300x60x335 cm)", "width": 300, "length": 60, "height": 350, "weight": 350, "canStack": false, "itemsPerCase": 1},
  {"id": 53, "name": "truss corner", "width": 40, "length": 40, "height": 40, "weight": 40, "canStack": true, "itemsPerCase": 1},
  {"id": 54, "name": "Boxer Projector", "width": 110, "length": 60, "height": 185, "weight": 185, "canStack": false, "itemsPerCase": 1},
  {"id": 55, "name": "Beam 575 (karton)", "width": 50, "length": 30, "height": 60, "weight": 60, "canStack": true, "itemsPerCase": 3},
  {"id": 56, "name": "Laptop", "width": 40, "length": 10, "height": 50, "weight": 50, "canStack": true, "itemsPerCase": 1},
  {"id": 57, "name": "trap/ramp for van", "width": 240, "length": 10, "height": 100, "weight": 240, "canStack": false, "itemsPerCase": 1},
  {"id": 58, "name": "iiYama 46\" - TOUCHSCREEN - STANDARD", "width": 100, "length": 50, "height": 100, "weight": 140, "canStack": true, "itemsPerCase": 2},
  {"id": 59, "name": "NEC V554 TOUCHSCREEN - STANDARD", "width": 100, "length": 50, "height": 100, "weight": 140, "canStack": true, "itemsPerCase": 2},
  {"id": 60, "name": "Samsung UE43 - STANDARD", "width": 80, "length": 50, "height": 80, "weight": 120, "canStack": true, "itemsPerCase": 3},
  {"id": 61, "name": "LG 60 UH605V - STANDARD", "width": 110, "length": 40, "height": 230, "weight": 160, "canStack": true, "itemsPerCase": 2},
  {"id": 62, "name": "LG 65 UJ620V - STANDARD", "width": 110, "length": 40, "height": 230, "weight": 160, "canStack": true, "itemsPerCase": 2},
  {"id": 63, "name": "LG 75\" - STANDARD", "width": 140, "length": 40, "height": 230, "weight": 210, "canStack": true, "itemsPerCase": 1},
  {"id": 64, "name": "MULTIMEDIA TOTEM 55\"", "width": 100, "length": 60, "height": 210, "weight": 210, "canStack": false, "itemsPerCase": 1},
  {"id": 65, "name": "ALUSTAGE / AL34 / QUADRO-290 TRUSS / CORNERBLOCK - case", "width": 30, "length": 30, "height": 30, "weight": 10, "canStack": true, "itemsPerCase": 1},
  {"id": 66, "name": "ALUSTAGE / AL34 / QUADRO-290 TRUSS / L CORNER", "width": 50, "length": 30, "height": 50, "weight": 5, "canStack": true, "itemsPerCase": 1},
  {"id": 67, "name": "ALUSTAGE / AL34 / QUADRO-290 TRUSS FD / 0,21M", "width": 21, "length": 30, "height": 30, "weight": 3, "canStack": true, "itemsPerCase": 1},
  {"id": 68, "name": "ALUSTAGE / AL34 / QUADRO-290 TRUSS FD / 0,29M", "width": 30, "length": 30, "height": 50, "weight": 4, "canStack": true, "itemsPerCase": 1},
  {"id": 69, "name": "ALUSTAGE / AL34 / QUADRO-290 TRUSS FD / 0,5M", "width": 50, "length": 30, "height": 30, "weight": 4, "canStack": true, "itemsPerCase": 1},
  {"id": 70, "name": "ALUSTAGE / AL34 / QUADRO-290 TRUSS FD / 1M", "width": 100, "length": 30, "height": 30, "weight": 6, "canStack": true, "itemsPerCase": 1},
  {"id": 71, "name": "ALUSTAGE / AL34 / QUADRO-290 TRUSS FD / 2M", "width": 200, "length": 30, "height": 30, "weight": 11, "canStack": true, "itemsPerCase": 1},
  {"id": 72, "name": "ALUSTAGE / AL34 / QUADRO-290 TRUSS FD / 3M", "width": 300, "length": 30, "height": 30, "weight": 16, "canStack": true, "itemsPerCase": 1},
  {"id": 73, "name": "ALUSTAGE / AL34 / QUADRO-290 TRUSS FD / T - TYPE / 0,5x0,5m", "width": 50, "length": 30, "height": 50, "weight": 50, "canStack": true, "itemsPerCase": 8},
  {"id": 74, "name": "ALUSTAGE / AL34 / QUADRO-290 TRUSS FD / X - TYPE / 0,5x0,5m", "width": 50, "length": 30, "height": 50, "weight": 6, "canStack": true, "itemsPerCase": 8},
  {"id": 75, "name": "EUROTRUSS / FD34 / QUADRO-290 TRUSS FD / L - 90° TYPE / 0,5x0,5m", "width": 50, "length": 30, "height": 50, "weight": 50, "canStack": true, "itemsPerCase": 8},
  {"id": 76, "name": "EUROTRUSS / HD34 / QUADRO-290 TRUSS HD / L - 90° TYPE / 0,5x0,5m", "width": 80, "length": 10, "height": 80, "weight": 80, "canStack": true, "itemsPerCase": 1},
  {"id": 77, "name": "EUROTRUSS / HD34 / QUADRO-290 TRUSS HD / 0,5M", "width": 50, "length": 29, "height": 29, "weight": 18, "canStack": true, "itemsPerCase": 1},
  {"id": 78, "name": "EUROTRUSS / HD34 / QUADRO-290 TRUSS HD / 1M", "width": 100, "length": 29, "height": 29, "weight": 18, "canStack": true, "itemsPerCase": 1},
  {"id": 79, "name": "EUROTRUSS / HD34 / QUADRO-290 TRUSS HD / 2M", "width": 200, "length": 29, "height": 29, "weight": 18, "canStack": true, "itemsPerCase": 1},
  {"id": 80, "name": "EUROTRUSS / HD34 / QUADRO-290 TRUSS HD / 3M", "width": 300, "length": 29, "height": 29, "weight": 18, "canStack": true, "itemsPerCase": 1},
  {"id": 81, "name": "PROLIGHTS / ASTRA HYBRID 330 / DMX-5 (Case 2)", "width": 70, "length": 50, "height": 70, "weight": 50, "canStack": true, "itemsPerCase": 5},
  {"id": 82, "name": "PROLIGHTS / EclEXPO FLOOD300FC / RGBW / DMX-5", "width": 30, "length": 30, "height": 30, "weight": 40, "canStack": true, "itemsPerCase": 3},
  {"id": 83, "name": "CAMEO PAR-64 18x8W RGBW", "width": 60, "length": 50, "height": 50, "weight": 80, "canStack": true, "itemsPerCase": 3},
  {"id": 84, "name": "PROLIGHTS / JET SPOT4Z / DMX-5 (Case 3)", "width": 80, "length": 60, "height": 80, "weight": 140, "canStack": true, "itemsPerCase": 2},
  {"id": 85, "name": "TRUSS x HANGED CIRCLE Ø5m", "width": 300, "length": 60, "height": 170, "weight": 128, "canStack": false, "itemsPerCase": 1},
  {"id": 86, "name": "TRUSS x HANGED CIRCLE Ø6m", "width": 300, "length": 60, "height": 210, "weight": 140, "canStack": false, "itemsPerCase": 1},
  {"id": 87, "name": "TRUSS x HANGED CIRCLE Ø11m", "width": 300, "length": 60, "height": 210, "weight": 200, "canStack": false, "itemsPerCase": 1},
  {"id": 88, "name": "TRUSS x HANGED CIRCLE Ø19m", "width": 320, "length": 60, "height": 230, "weight": 220, "canStack": false, "itemsPerCase": 1},
  {"id": 89, "name": "P2.06 / frameLED / KABINET", "width": 86, "length": 62, "height": 100, "weight": 118, "canStack": true, "itemsPerCase": 10},
  {"id": 90, "name": "P1,86 LED MODULE / 320 x160MM FLEX V1", "width": 46, "length": 63, "height": 40, "weight": 20, "canStack": true, "itemsPerCase": 42},
  {"id": 91, "name": "P2.0 LED SPHERE / d=1,5m DOBRAC MALA SKRZYNIE", "width": 160, "length": 160, "height": 220, "weight": 450, "canStack": false, "itemsPerCase": 1},
  {"id": 92, "name": "P3.0 LED SPHERE 1 z 5", "width": 192, "length": 192, "height": 200, "weight": 400, "canStack": false, "itemsPerCase": 1},
  {"id": 93, "name": "P3.0 LED SPHERE 2 z 5", "width": 192, "length": 192, "height": 200, "weight": 400, "canStack": false, "itemsPerCase": 1},
  {"id": 94, "name": "P3.0 LED SPHERE 3 z 5", "width": 270, "length": 101, "height": 200, "weight": 400, "canStack": false, "itemsPerCase": 1},
  {"id": 95, "name": "P3.0 LED SPHERE 4 z 5", "width": 183, "length": 182, "height": 200, "weight": 400, "canStack": false, "itemsPerCase": 1},
  {"id": 96, "name": "P3.0 LED SPHERE 5 z 5", "width": 180, "length": 120, "height": 220, "weight": 400, "canStack": false, "itemsPerCase": 1},
  {"id": 97, "name": "P1.56 stackować na 2(!)", "width": 120, "length": 60, "height": 90, "weight": 125, "canStack": true, "itemsPerCase": 10},
  {"id": 98, "name": "CHAINMASTER D8PLUS (320KG)", "width": 46, "length": 22, "height": 13, "weight": 30, "canStack": true, "itemsPerCase": 1},
  {"id": 99, "name": "PODEST ALUDECK LIGHT 2 x 1M", "width": 200, "length": 100, "height": 20, "weight": 45, "canStack": true, "itemsPerCase": 1},
  {"id": 100, "name": "ALUMINIUM BLACK PIPE / 50 / 4M", "width": 400, "length": 6, "height": 6, "weight": 6, "canStack": true, "itemsPerCase": 1},
  {"id": 101, "name": "ALUMINIUM BLACK PIPE / 50 / 6M", "width": 600, "length": 6, "height": 6, "weight": 9, "canStack": true, "itemsPerCase": 1},
  {"id": 102, "name": "PROLIGHTS / ECLEXPO FLOOD300W / DMX-5 (Karton)", "width": 40, "length": 21, "height": 25, "weight": 5, "canStack": true, "itemsPerCase": 1},
  {"id": 103, "name": "VOGELS / PFW 6870 BLACK / SCISSOR MOUNT", "width": 29, "length": 5, "height": 6, "weight": 23, "canStack": true, "itemsPerCase": 1},
  {"id": 104, "name": "MULTIMEDIA TOTEM / 55\" / 4K / i5-12450H / 16GB / 1TB / Win10 / BLACK", "width": 100, "length": 80, "height": 200, "weight": 150, "canStack": false, "itemsPerCase": 1},
  {"id": 105, "name": "DELL OPTIPLEX 7050 MICRO D10U", "width": 19, "length": 4, "height": 19, "weight": 2, "canStack": true, "itemsPerCase": 1},
  {"id": 106, "name": "P1,29 lub 1.2 MODULED CABINET", "width": 94, "length": 60, "height": 100, "weight": 121, "canStack": true, "itemsPerCase": 8},
  {"id": 107, "name": "DICOLOR US-261", "width": 117, "length": 58, "height": 110, "weight": 118, "canStack": true, "itemsPerCase": 8},
  {"id": 108, "name": "DICOLOR US-390 (wys. 74, ale stackowane na 2!)", "width": 110, "length": 82, "height": 110, "weight": 87, "canStack": true, "itemsPerCase": 6},
  {"id": 109, "name": "KINETIC Q / WINCH DMX kule dodaj napęd!", "width": 110, "length": 56, "height": 70, "weight": 40, "canStack": true, "itemsPerCase": 16},
  {"id": 110, "name": "KINETIC Q / WINCH DMX napęd dodaj kule!", "width": 71, "length": 54, "height": 70, "weight": 20, "canStack": true, "itemsPerCase": 8},
  {"id": 111, "name": "P1.9 KINETIC LED CABINET / INDOOR", "width": 120, "length": 60, "height": 80, "weight": 95, "canStack": true, "itemsPerCase": 2},
  {"id": 112, "name": "creaTUBE/360/1,5M", "width": 150, "length": 30, "height": 30, "weight": 50, "canStack": true, "itemsPerCase": 50},
  {"id": 113, "name": "creaTUBE/360/0,5M", "width": 50, "length": 30, "height": 30, "weight": 50, "canStack": true, "itemsPerCase": 50},
  {"id": 114, "name": "creaTUBE/360/1M", "width": 100, "length": 30, "height": 30, "weight": 50, "canStack": true, "itemsPerCase": 50},
  {"id": 115, "name": "POWERBOX RACK 63A", "width": 71, "length": 55, "height": 70, "weight": 50, "canStack": true, "itemsPerCase": 1},
  {"id": 116, "name": "CHAINMASTER D8 PLUS 500 KG 24M", "width": 80, "length": 60, "height": 50, "weight": 110, "canStack": true, "itemsPerCase": 1},
  {"id": 117, "name": "CHAINMASTER D8 PLUS 320 KG 10M", "width": 80, "length": 60, "height": 50, "weight": 60, "canStack": true, "itemsPerCase": 2},
  {"id": 118, "name": "RACK MOTOR CONTROLLER 24DV 24 CHANNEL", "width": 71, "length": 55, "height": 97, "weight": 70, "canStack": true, "itemsPerCase": 50},
  {"id": 119, "name": "CHAMSYS/ QUICKQ 20", "width": 57, "length": 35, "height": 107, "weight": 6, "canStack": true, "itemsPerCase": 1},
  {"id": 120, "name": "LD SYSTEMS STINGER / 8 G3", "width": 120, "length": 40, "height": 80, "weight": 85, "canStack": true, "itemsPerCase": 4},
  {"id": 121, "name": "PRESONUS STUDIOLIVE 16.0.2 USB", "width": 41, "length": 40, "height": 14, "weight": 18, "canStack": true, "itemsPerCase": 1},
  {"id": 122, "name": "P2.9 OUTDOOR RENTAL", "width": 120, "length": 60, "height": 80, "weight": 120, "canStack": true, "itemsPerCase": 9},
  {"id": 123, "name": "TRUSS CIRCLE / QUADRO 290 HD / D= 19M / 20pcs", "width": 300, "length": 60, "height": 220, "weight": 85, "canStack": true, "itemsPerCase": 1},
  {"id": 124, "name": "TRUSS CIRCLE / QUADRO 290 HD / D= 15M / 16pcs", "width": 300, "length": 60, "height": 220, "weight": 85, "canStack": true, "itemsPerCase": 1},
  {"id": 125, "name": "TRUSS CIRCLE / QUADRO 290 HD / D= 11M / 12pcs", "width": 320, "length": 60, "height": 220, "weight": 85, "canStack": true, "itemsPerCase": 1},
  {"id": 126, "name": "TRUSS CIRCLE / QUADRO 290 HD / D= 8M / 8pcs", "width": 320, "length": 60, "height": 220, "weight": 85, "canStack": true, "itemsPerCase": 1},
  {"id": 127, "name": "TRUSS CIRCLE / QUADRO 290 HD / D= 7M", "width": 270, "length": 60, "height": 220, "weight": 85, "canStack": true, "itemsPerCase": 1},
  {"id": 128, "name": "TRUSS CIRCLE / QUADRO 290 HD / D= 6M", "width": 240, "length": 60, "height": 220, "weight": 85, "canStack": true, "itemsPerCase": 1},
  {"id": 129, "name": "TRUSS CIRCLE / QUADRO 290 HD / D= 5M", "width": 220, "length": 60, "height": 220, "weight": 85, "canStack": true, "itemsPerCase": 1},
  {"id": 130, "name": "TRUSS CIRCLE / QUADRO 290 HD / D= 4M / 4pcs", "width": 300, "length": 60, "height": 160, "weight": 85, "canStack": true, "itemsPerCase": 1},
  {"id": 131, "name": "ALUSTAGE / AL31 / UNO TRUSS / 1", "width": 100, "length": 5, "height": 5, "weight": 2, "canStack": true, "itemsPerCase": 1},
  {"id": 132, "name": "ALUSTAGE / AL31 / UNO TRUSS / 2", "width": 200, "length": 5, "height": 5, "weight": 4, "canStack": true, "itemsPerCase": 1},
  {"id": 133, "name": "ALUSTAGE / AL31 / UNO TRUSS / 3", "width": 300, "length": 5, "height": 5, "weight": 6, "canStack": true, "itemsPerCase": 1},
  {"id": 134, "name": "ALUSTAGE / AL32 / DUO-290 TRUSS / 0,5M", "width": 50, "length": 5, "height": 30, "weight": 2, "canStack": true, "itemsPerCase": 1},
  {"id": 135, "name": "ALUSTAGE / AL32 / DUO-290 TRUSS / 1M", "width": 100, "length": 5, "height": 30, "weight": 3, "canStack": true, "itemsPerCase": 1},
  {"id": 136, "name": "ALUSTAGE / AL32 / DUO-290 TRUSS / 2M", "width": 200, "length": 5, "height": 30, "weight": 5, "canStack": true, "itemsPerCase": 1},
  {"id": 137, "name": "ALLEN & HEATH ZED 10 AUDIO ANALOG MIXER", "width": 46, "length": 33, "height": 16, "weight": 5, "canStack": true, "itemsPerCase": 1},
  {"id": 138, "name": "SENDER - SCALER / NOVASTAR / MCTRL 4K", "width": 55, "length": 24, "height": 55, "weight": 20, "canStack": true, "itemsPerCase": 1},
  {"id": 139, "name": "LED WASHER / 16 X 10W / RGBW / 4 IN 1", "width": 116, "length": 58, "height": 52, "weight": 20, "canStack": true, "itemsPerCase": 5},
  {"id": 140, "name": "LED LIGHT BAR / 8 PL42199", "width": 115, "length": 67, "height": 38, "weight": 40, "canStack": true, "itemsPerCase": 8},
  {"id": 141, "name": "matrixLED cabinet / 0,5x0,5m", "width": 66, "length": 104, "height": 80, "weight": 84, "canStack": true, "itemsPerCase": 4},
  {"id": 142, "name": "P2.0 LED SPHERE / d=1,5m DOBRAC DUŻĄ SKRZYNIE", "width": 120, "length": 60, "height": 70, "weight": 150, "canStack": false, "itemsPerCase": 1}
]
