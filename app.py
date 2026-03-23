# -*- coding: utf-8 -*-
"""
================================================================================
SYSTEM: VORTEZA STACK 
VERSION: 23.0 | APEX ULTIMATE
FIRM: VORTEZA SYSTEMS
STATUS: ENTERPRISE PRODUCTION READY | FULL SOURCE CODE
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
# 1. ARCHITEKTURA ŚRODOWISKA I REJESTR INŻYNIERYJNY FLOTY
# ==============================================================================
st.set_page_config(
    page_title="VORTEZA STACK v23.0",
    layout="wide",
    initial_sidebar_state="expanded",
    page_icon="🕋"
)

# PEŁNA SPECYFIKACJA TECHNICZNA FLOTY VORTEZA
# L, W, H w cm | max_w, tare w kg
FLEET_REGISTRY = {
    "TIR FTL Mega 13.6m": {
        "max_w": 24000, "L": 1360, "W": 248, "H": 300, 
        "ldm_max": 13.6, "axles": 3, "wheelbase": 850, "tare": 14500, "cab_l": 220
    },
    "TIR FTL Standard 13.6m": {
        "max_w": 24000, "L": 1360, "W": 248, "H": 275, 
        "ldm_max": 13.6, "axles": 3, "wheelbase": 850, "tare": 13800, "cab_l": 220
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
        "max_w": 1250, "L": 485, "W": 175, "H": 220, 
        "ldm_max": 4.8, "axles": 2, "wheelbase": 320, "tare": 2250, "cab_l": 140
    }
}

# ==============================================================================
# 2. BRANDING VORTEZA & ADVANCED CSS ENGINE
# ==============================================================================
def get_resource_b64(file_path):
    """Bezpieczne ładowanie zasobów binarnych do wstrzyknięcia w CSS."""
    try:
        if os.path.exists(file_path):
            with open(file_path, 'rb') as f:
                return base64.b64encode(f.read()).decode()
        return ""
    except: return ""

def inject_vorteza_supreme_ui():
    """Wstrzykuje rygorystyczny design system VORTEZA STACK."""
    bg_data = get_resource_b64('bg_vorteza.png')
    
    st.markdown(f"""
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;600;700&family=JetBrains+Mono:wght@300;400;500&display=swap');
            
            :root {{
                --v-copper: #B58863;
                --v-copper-bright: #d4a373;
                --v-copper-glow: rgba(181, 136, 99, 0.4);
                --v-dark-obsidian: #030303;
                --v-panel-bg: rgba(8, 8, 8, 0.98);
                --v-border: rgba(181, 136, 99, 0.2);
                --v-neon-green: #00FF41;
                --v-alert-red: #FF3131;
            }}

            /* Globalna Architektura Wizualna */
            .stApp {{
                background-image: url("data:image/png;base64,{bg_data}");
                background-size: cover;
                background-attachment: fixed;
                color: #F5F5F5;
                font-family: 'Montserrat', sans-serif;
            }}

            /* System Kafelkowy VORTEZA STACK */
            .v-tile-pro {{
                background: var(--v-panel-bg);
                padding: 2.5rem;
                border: 1px solid var(--v-border);
                border-left: 12px solid var(--v-copper);
                box-shadow: 0 40px 100px rgba(0,0,0,0.95);
                margin-bottom: 2.5rem;
                backdrop-filter: blur(45px);
            }}

            section[data-testid="stSidebar"] {{
                background-color: rgba(3, 3, 3, 0.99) !important;
                border-right: 1px solid var(--v-border);
                width: 480px !important;
                backdrop-filter: blur(30px);
            }}

            h1, h2, h3 {{ 
                color: var(--v-copper) !important; 
                text-transform: uppercase; 
                letter-spacing: 10px !important; 
                font-weight: 700 !important; 
                text-shadow: 4px 4px 20px rgba(0,0,0,0.9);
            }}

            [data-testid="stMetricValue"] {{ 
                color: var(--v-copper) !important; 
                font-family: 'JetBrains Mono', monospace !important; 
                font-size: 3.6rem !important;
                font-weight: 300 !important;
            }}
            [data-testid="stMetricLabel"] {{
                color: #777 !important;
                text-transform: uppercase;
                letter-spacing: 4px;
                font-weight: 600;
            }}

            /* Kontrolery Interaktywne */
            .stButton > button {{
                background: linear-gradient(180deg, #0a0a0a, #151515);
                color: var(--v-copper);
                border: 2px solid var(--v-copper);
                padding: 1.6rem;
                text-transform: uppercase;
                letter-spacing: 8px;
                font-weight: 700;
                width: 100%;
                transition: 0.8s all cubic-bezier(0.19, 1, 0.22, 1);
                border-radius: 0;
            }}
            .stButton > button:hover {{
                background: var(--v-copper);
                color: #000;
                box-shadow: 0 0 120px var(--v-copper-glow);
                transform: translateY(-5px);
            }}

            /* Tabele Inżynieryjne */
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
                padding: 22px; 
                letter-spacing: 4px;
            }}
            .v-tactical-table td {{ 
                padding: 18px 22px; 
                border-bottom: 1px solid #111; 
                color: #CCC; 
                font-size: 1rem; 
            }}
            .v-tactical-table tr:hover {{ background: rgba(181,136,99,0.06); }}

            /* Load Balancer Visualization */
            .v-rail-track {{
                width: 100%; height: 35px; background: #080808; border-radius: 17px; position: relative; border: 2px solid #222; margin: 60px 0;
                box-shadow: inset 0 0 25px #000;
            }}
            .v-cog-pointer {{
                position: absolute; width: 12px; height: 75px; top: -20px; background: var(--v-neon-green); 
                box-shadow: 0 0 45px var(--v-neon-green); border-radius: 6px;
                transition: left 1.5s cubic-bezier(0.19, 1, 0.22, 1);
            }}
            
            /* Status Tags */
            .v-status-badge {{
                background: rgba(181,136,99,0.1);
                border: 1px solid var(--v-copper);
                padding: 18px;
                font-family: 'JetBrains Mono', monospace;
                font-size: 0.8rem;
                margin-bottom: 20px;
                line-height: 1.6;
            }}

            /* Scrollbar Tuning */
            ::-webkit-scrollbar {{ width: 5px; }}
            ::-webkit-scrollbar-track {{ background: #050505; }}
            ::-webkit-scrollbar-thumb {{ background: var(--v-copper); }}
        </style>
    """, unsafe_allow_html=True)

# ==============================================================================
# 3. KONTROLA DOSTĘPU (SECURITY PROTOCOL)
# ==============================================================================
def check_stack_security_clearance():
    """Weryfikuje uprawnienia dostępu do VORTEZA STACK."""
    if "authorized" not in st.session_state:
        st.session_state.authorized = False

    if not st.session_state.authorized:
        try:
            # Pobieranie klucza z Streamlit Cloud Secrets
            sys_key = str(st.secrets.get("password", "vorteza2026"))
        except:
            sys_key = "vorteza2026"

        st.markdown("<br><br><br><br><br><br><br>", unsafe_allow_html=True)
        _, col_auth, _ = st.columns([1, 2.5, 1])
        with col_auth:
            with st.form("VortezaAuthGate"):
                st.markdown("<h2 style='text-align:center;'>VORTEZA STACK</h2>", unsafe_allow_html=True)
                st.markdown("<p style='text-align:center; color:#333; font-size:0.8rem; letter-spacing:8px;'>MASTER ENCRYPTION KEY REQUIRED</p>", unsafe_allow_html=True)
                pwd_in = st.text_input("GOLIATH CORE AUTHENTICATION", type="password")
                if st.form_submit_button("VALIDATE SECURITY CLEARANCE"):
                    if pwd_in == sys_key:
                        st.session_state.authorized = True
                        st.rerun()
                    else:
                        st.error("FATAL ERROR: SECURITY BREACH DETECTED - INVALID KEY")
        return False
    return True

# ==============================================================================
# 4. CHROMATIC SKU ENGINE (STABILNY SILNIK KOLORÓW)
# ==============================================================================
def get_vorteza_sku_color(sku_name):
    """Zwraca unikalny kolor metaliczny dla każdego SKU bazując na jego nazwie."""
    metallic_palette = [
        "#B58863", "#D4AF37", "#8E6A4D", "#5E4633", "#A67C52", 
        "#2C3E50", "#34495E", "#1A252F", "#16A085", "#27AE60",
        "#7F8C8D", "#95A5A6", "#BDC3C7", "#7E4A35", "#C0392B",
        "#D35400", "#F39C12", "#2980B9", "#8E44AD", "#3D3D3D",
        "#2C3E50", "#E67E22", "#E74C3C", "#1ABC9C", "#F1C40F"
    ]
    # Deterministyczne ziarno oparte na nazwie produktu
    random.seed(sum(ord(c) for c in sku_name))
    return random.choice(metallic_palette)

# ==============================================================================
# 5. RENDERER CAD-3D STACK (ULTIMATE ENGINE v23.0)
# ==============================================================================
def generate_cube_mesh(x, y, z, dx, dy, dz, color, name, opacity=0.98):
    """Generuje matematycznie poprawną siatkę Mesh3d dla pojedynczej skrzyni."""
    # 8 Wierzchołków
    v_x = [x, x+dx, x+dx, x, x, x+dx, x+dx, x]
    v_y = [y, y, y+dy, y+dy, y, y, y+dy, y+dy]
    v_z = [z, z, z, z, z+dz, z+dz, z+dz, z+dz]
    
    # 12 Trójkątów (6 ścian)
    i = [7, 0, 0, 0, 4, 4, 6, 6, 4, 0, 3, 2]
    j = [3, 4, 1, 2, 5, 6, 5, 2, 0, 1, 6, 3]
    k = [0, 7, 2, 3, 6, 7, 1, 1, 5, 5, 7, 6]
    
    mesh = go.Mesh3d(
        x=v_x, y=v_y, z=v_z, i=i, j=j, k=k,
        color=color, opacity=opacity, name=name,
        flatshading=True, lighting=dict(ambient=0.5, diffuse=1, roughness=0.1, specular=1, fresnel=0.2),
        lightposition=dict(x=1000, y=1000, z=1000),
        hovertemplate=f"<b>{name}</b><br>D: {dx}cm W: {dy}cm H: {dz}cm<extra></extra>"
    )
    
    # Krawędzie (Line plot) dla separacji wizualnej
    line_x = [x, x+dx, x+dx, x, x, x, x+dx, x+dx, x, x, x+dx, x+dx, x+dx, x+dx, x, x]
    line_y = [y, y, y+dy, y+dy, y, y, y, y+dy, y+dy, y+dy, y+dy, y, y, y+dy, y+dy, y]
    line_z = [z, z, z, z, z, z+dz, z+dz, z, z, z+dz, z+dz, z+dz, z, z, z+dz, z+dz]
    
    lines = go.Scatter3d(
        x=line_x, y=line_y, z=line_z, mode='lines',
        line=dict(color='black', width=3), hoverinfo='skip'
    )
    
    return [mesh, lines]

def render_stack_pro_3d(vehicle_data, cargo_stacks):
    """Generuje inżynieryjny model 3D naczepy wraz z ładunkiem."""
    fig = go.Figure()
    L, W, H = vehicle_data['L'], vehicle_data['W'], vehicle_data['H']

    # --- INFRASTRUKTURA POJAZDU (CAD DETAIL) ---
    # Podłoga naczepy (Płyta główna)
    fig.add_trace(go.Mesh3d(
        x=[0, L, L, 0], y=[0, 0, W, W], z=[-15, -15, -15, -15],
        color='#111111', opacity=1, hoverinfo='skip'
    ))
    
    # Koła i Inżynieria Zawieszenia
    ax_count = vehicle_data.get('axles', 3)
    ax_dist = 148
    rear_start_pos = L - 450 if L > 800 else L - 180
    
    for a_idx in range(ax_count):
        curr_axle_x = rear_start_pos + (a_idx * ax_dist)
        if curr_axle_x < L:
            for side_offset in [-40, W+25]:
                # Opona CAD High-Poly
                fig.add_trace(go.Mesh3d(
                    x=[curr_axle_x-60, curr_axle_x+60, curr_axle_x+60, curr_axle_x-60], 
                    y=[side_offset, side_offset, side_offset+18, side_offset+18], 
                    z=[-80, -80, -15, -15], color='#050505', opacity=1, hoverinfo='skip'
                ))
                # Felga Miedziana VORTEZA
                fig.add_trace(go.Mesh3d(
                    x=[curr_axle_x-25, curr_axle_x+25, curr_axle_x+25, curr_axle_x-25], 
                    y=[side_offset-2, side_offset-2, side_offset, side_offset], 
                    z=[-55, -55, -35, -35], color='#B58863', opacity=0.9, hoverinfo='skip'
                ))

    # Kabina Operatora (Goliath Command)
    cab_depth = vehicle_data.get('cab_l', 240)
    fig.add_trace(go.Mesh3d(
        x=[-cab_depth, 0, 0, -cab_depth, -cab_depth, 0, 0, -cab_depth],
        y=[-45, -45, W+45, W+45, -45, -45, W+45, W+45],
        z=[0, 0, 0, 0, H*1.05, H*1.05, H*1.05, H*1.05],
        i=[7,0,0,0,4,4,6,6,4,0,3,2], j=[3,4,1,2,5,6,5,2,0,1,6,3], k=[0,7,2,3,6,7,1,1,5,5,7,6],
        color='#020202', opacity=1, name="UNIT_COMMAND_CAB"
    ))

    # Szkielet Naczepy (Copper Cage Architecture)
    cage_lines = [
        ([0, L], [0, 0], [0, 0]), ([0, L], [W, W], [0, 0]), ([0, 0], [0, W], [0, 0]), ([L, L], [0, W], [0, 0]),
        ([0, 0], [0, 0], [0, H]), ([0, 0], [W, W], [0, H]), ([0, L], [0, 0], [H, H]), ([0, L], [W, W], [H, H]),
        ([L, L], [0, 0], [0, H]), ([L, L], [W, W], [0, H])
    ]
    for px, py, pz in cage_lines:
        fig.add_trace(go.Scatter3d(x=px, y=py, z=pz, mode='lines', line=dict(color='#B58863', width=12), hoverinfo='skip'))

    # --- RENDER ŁADUNKU (CHROMATIC MAPPING) ---
    for cluster in cargo_stacks:
        for unit in cluster['items']:
            x, y, z = cluster['x'], cluster['y'], unit['z']
            dx, dy, dz = unit['w_fit'], unit['l_fit'], unit['height']
            
            p_color = get_vorteza_sku_color(unit['name'])
            # Generowanie bryły
            cube_elements = generate_cube_mesh(x, y, z, dx, dy, dz, p_color, unit['name'])
            for element in cube_elements:
                fig.add_trace(element)

    fig.update_layout(
        scene=dict(
            aspectmode='data', xaxis_visible=False, yaxis_visible=False, zaxis_visible=False,
            camera=dict(eye=dict(x=2.5, y=2.5, z=2.2), projection=dict(type='perspective')),
            bgcolor='rgba(0,0,0,0)'
        ),
        paper_bgcolor='rgba(0,0,0,0)', margin=dict(l=0, r=0, b=0, t=0), showlegend=False
    )
    return fig

# ==============================================================================
# 6. SILNIK PAKOWANIA V-ENGINE 23.0 (ULTIMATE OPTIMIZER)
# ==============================================================================
class V23StackEngine:
    """Zaawansowany algorytm pakowania 3D z kontrolą V-PERMIT i balansem X."""
    
    @staticmethod
    def solve_manifest(cargo_list, vehicle, x_offset=0):
        # Priorytetyzacja: 1. No-Stack, 2. No-Rotation, 3. Pole powierzchni (L*W)
        items_sorted = sorted(cargo_list, 
                             key=lambda x: (not x.get('canStack', True), 
                                            not x.get('allowRotation', True), 
                                            x['width']*x['length']), 
                             reverse=True)
        
        placed_clusters = []
        failed_units = []
        mass_accumulator = 0
        cx, cy, current_row_max_w = x_offset, 0, 0

        for unit in items_sorted:
            # Weryfikacja masy dopuszczalnej
            if mass_accumulator + unit['weight'] > vehicle['max_w']:
                failed_units.append(unit); continue
            
            # PROTOKÓŁ PIĘTROWANIA (Vertical Integration)
            integrated = False
            if unit.get('canStack', True):
                for cluster in placed_clusters:
                    # Dopasowanie wymiarowe z uwzględnieniem ZABLOKOWANEJ rotacji
                    if unit.get('allowRotation', True):
                        dim_match = (unit['width'] <= cluster['w'] and unit['length'] <= cluster['l']) or \
                                  (unit['length'] <= cluster['w'] and unit['width'] <= cluster['l'])
                    else:
                        dim_match = (unit['width'] <= cluster['w'] and unit['length'] <= cluster['l'])
                    
                    if dim_match and (cluster['curH'] + unit['height'] <= vehicle['H']):
                        u_copy = unit.copy(); u_copy['z'] = cluster['curH']
                        u_copy['w_fit'], u_copy['l_fit'] = cluster['w'], cluster['l']
                        cluster['items'].append(u_copy); cluster['curH'] += unit['height']
                        mass_accumulator += unit['weight']; integrated = True; break
            
            if integrated: continue

            # PROTOKÓŁ PODŁOGI (Floor placement + V-PERMIT ROTATION)
            placed = False
            # Orientacje dopuszczalne
            if unit.get('allowRotation', True):
                orientations = [(unit['width'], unit['length']), (unit['length'], unit['width'])]
            else:
                orientations = [(unit['width'], unit['length'])]
            
            for fw, fl in orientations:
                # Szukanie miejsca w rzędzie (oś Y)
                if cy + fl <= vehicle['W'] and cx + fw <= vehicle['L']:
                    u_c = unit.copy(); u_c['z'] = 0; u_c['w_fit'], u_c['l_fit'] = fw, fl
                    placed_clusters.append({'x':cx, 'y':cy, 'w':fw, 'l':fl, 'curH':unit['height'], 'items':[u_c]})
                    cy += fl; current_row_max_w = max(current_row_max_w, fw)
                    mass_accumulator += unit['weight']; placed = True; break
                # Przeskok do nowego rzędu (oś X)
                elif cx + current_row_max_w + fw <= vehicle['L'] and fl <= vehicle['W']:
                    cx += current_row_max_w; cy = 0; current_row_max_w = fw
                    u_c = unit.copy(); u_c['z'] = 0; u_c['w_fit'], u_c['l_fit'] = fw, fl
                    placed_clusters.append({'x':cx, 'y':cy, 'w':fw, 'l':fl, 'curH':unit['height'], 'items':[u_c]})
                    cy += fl; mass_accumulator += unit['weight']; placed = True; break
            
            if not placed: failed_units.append(unit)
        
        # Real-time LDM Calculation
        ldm_res = (max([s['x'] + s['w'] for s in placed_clusters]) / 100) if placed_clusters else 0
        return placed_clusters, mass_accumulator, failed_units, ldm_res

# ==============================================================================
# 7. ANALITYKA INŻYNIERYJNA (TACTICAL LOAD BALANCER)
# ==============================================================================
def process_cog_analysis_ui(vehicle, stacks):
    """Oblicza fizyczny środek ciężkości (CoG) i symuluje nacisk na osie."""
    if not stacks: return
    
    total_moment = 0
    total_weight = 0
    
    for s in stacks:
        for it in s['items']:
            # Obliczanie środka geometrycznego przedmiotu na osi X
            item_cx = s['x'] + (it['w_fit'] / 2)
            total_moment += (item_cx * it['weight'])
            total_weight += it['weight']
    
    cog_x = total_moment / total_weight if total_weight > 0 else 0
    cog_percent = (cog_x / vehicle['L']) * 100
    
    st.markdown("### ⚖️ CENTER OF GRAVITY ANALYSIS (CoG)")
    st.write(f"Położenie środka ciężkości ładunku: **{cog_x/100:.2f} m** od ściany przedniej")
    
    # Kolor marker'a (Green/Red)
    marker_color = "#00FF41" if 35 < cog_percent < 65 else "#FF3131"
    
    st.markdown(f"""
        <div class="v-rail-track">
            <div class="v-cog-pointer" style="left: {cog_percent}%; background: {marker_color}; box-shadow: 0 0 40px {marker_color};"></div>
            <div style="position:absolute; left:20px; top:45px; font-size:0.65rem; color:#888;">DRIVE AXLES (CAB)</div>
            <div style="position:absolute; right:20px; top:45px; font-size:0.65rem; color:#888;">TRAILER AXLES (REAR)</div>
        </div>
        <br>
    """, unsafe_allow_html=True)
    
    if cog_percent < 35:
        st.error("ALARM: PRZECIĄŻENIE OSI PRZEDNICH. Użyj suwaka OFFSET w panelu bocznym, aby dociążyć tył naczepy.")
    elif cog_percent > 65:
        st.error("ALARM: ODCIĄŻENIE OSI STERUJĄCEJ. Zmniejsz OFFSET lub usuń towar z tyłu naczepy.")
    else:
        st.success("STATUS NOMINALNY: Rozkład masy optymalny dla bezpiecznego transportu.")

# ==============================================================================
# 8. DATA PERSISTENCE & GLOBAL SKR (DB ENGINE)
# ==============================================================================
def db_core_load_vorteza():
    """Wczytuje globalną bazę SKU z pliku JSON."""
    if os.path.exists('products.json'):
        try:
            with open('products.json', 'r', encoding='utf-8') as f: return json.load(f)
        except: return []
    return []

def db_core_save_vorteza(data):
    """Archiwizuje zmiany w bazie SKU na dysku."""
    with open('products.json', 'w', encoding='utf-8') as f: 
        json.dump(data, f, indent=4, ensure_ascii=False)

# ==============================================================================
# 9. ARCHITEKTURA INTERFEJSU (VORTEZA STACK COMMAND)
# ==============================================================================
def main():
    inject_vorteza_supreme_ui()
    if not check_stack_security_clearance(): return

    # Stan Manifestu i Inwentarza
    if 'v_manifest' not in st.session_state: st.session_state.v_manifest = []
    inventory_db = db_core_load_vorteza()

    # --- TOP CONTROL NAVBAR ---
    hc1, hc2, hc3 = st.columns([1, 5, 1])
    with hc1:
        logo_data = get_resource_b64('logo_vorteza.png')
        if logo_data: st.markdown(f'<img src="data:image/png;base64,{logo_data}" width="180">', unsafe_allow_html=True)
        else: st.markdown("### VORTEZA")
    with hc2:
        st.markdown("<h1>VORTEZA STACK</h1>", unsafe_allow_html=True)
        st.markdown(f"<p style='color:#444; font-size:0.75rem; letter-spacing:8px; font-weight:600;'>SUPREME ARCHITECT EDITION v23.0 | CORE STATUS: NOMINAL</p>", unsafe_allow_html=True)
    with hc3:
        if st.button("TERMINATE"):
            st.session_state.authorized = False; st.rerun()

    # --- SIDEBAR: MISSION CONTROL ---
    with st.sidebar:
        st.markdown("### 📡 FLEET CONSOLE")
        v_sel_key = st.selectbox("ACTIVE TRANSPORT UNIT", list(FLEET_REGISTRY.keys()))
        veh = FLEET_REGISTRY[v_sel_key]
        
        st.divider()
        st.markdown("### ⚖️ DYNAMIC POSITIONING")
        # Suwak OFFSETU - Klucz do Load Balancera
        v_offset = st.slider("OFFSET OD ŚCIANY (cm)", 0, veh['L']-200, 0)
        st.caption("Przesuń ładunek na tył naczepy, aby skorygować środek ciężkości.")
        
        st.divider()
        st.markdown("### 📥 MANIFEST INJECTION")
        sku_list = [p['name'] for p in inventory_db]
        selected_sku = st.selectbox("SKU SELECTOR SERVICE", sku_list, index=None)
        
        if selected_sku:
            p_ref = next(p for p in inventory_db if p['name'] == selected_sku)
            ipc = p_ref.get('itemsPerCase', 1)
            p_rot = p_ref.get('allowRotation', True)
            st.markdown(f"""
                <div class='v-status-badge'>
                    <b>SKU:</b> {selected_sku}<br>
                    <b>STANDARD:</b> {ipc} PCS/UNIT<br>
                    <b>ROTACJA:</b> {'<span style="color:#00FF41">AUTHORIZED</span>' if p_rot else '<span style="color:#FF3131">LOCKED</span>'}
                </div>
            """, unsafe_allow_html=True)
            
            qty_in = st.number_input("QUANTITY TO SHIP (PCS)", min_value=1, value=ipc)
            num_units = math.ceil(qty_in / ipc)
            
            if st.button("APPEND TO MISSION MANIFEST", type="primary"):
                for i in range(num_units):
                    u_entry = p_ref.copy()
                    u_entry['p_actual'] = ipc if (i < num_units - 1 or qty_in % ipc == 0) else (qty_in % ipc)
                    st.session_state.v_manifest.append(u_entry)
                st.rerun()

        if st.button("GLOBAL PURGE"):
            st.session_state.v_manifest = []; st.rerun()

    # --- WORKSPACE TABS ARCHITECTURE ---
    tab_planner, tab_db, tab_terminal = st.tabs(["📊 TACTICAL PLANNER", "📦 MASTER INVENTORY", "⚙️ SYSTEM LOGS"])

    # --------------------------------------------------------------------------
    # TAB 1: PLANNER (CAD-3D & BALANCER)
    # --------------------------------------------------------------------------
    with tab_planner:
        if st.session_state.v_manifest:
            # Global KPI Stats
            kpi1, kpi2, kpi3, kpi4 = st.columns(4)
            total_mass = sum(float(u['weight']) for u in st.session_state.v_manifest)
            kpi1.metric("CASES", len(st.session_state.v_manifest))
            kpi2.metric("PCS TOTAL", sum(int(u.get('p_actual', 1)) for u in st.session_state.v_manifest))
            kpi3.metric("GROSS MASS", f"{total_mass} KG")
            kpi4.metric("UTILIZATION", f"{(total_mass/veh['max_w'])*100:.1f}%")

            # Execution logic (Assigment to Fleet)
            rem_units = [dict(u) for u in st.session_state.v_manifest]
            fleet_allocation = []
            
            while rem_units:
                clusters, mass_sum, failed, ldm_res = V23StackEngine.solve_manifest(rem_units, veh, x_offset=v_offset)
                if not clusters: st.error("CRITICAL ERROR: UNIT OVERSIZE DETECTED."); break
                fleet_allocation.append({"stacks": clusters, "weight": mass_sum, "ldm": ldm_res})
                rem_units = failed

            st.markdown(f"### ASIGNED FLEET CAPACITY: {len(fleet_allocation)} JEDNOSTKI")
            
            for idx, truck in enumerate(fleet_allocation):
                st.markdown(f'<div class="v-tile-pro">', unsafe_allow_html=True)
                st.markdown(f"### MISSION UNIT #{idx+1} | {v_sel_key}", unsafe_allow_html=True)
                
                viz_col, dat_col = st.columns([2.8, 1])
                with viz_col:
                    st.plotly_chart(render_stack_pro_3d(veh, truck['stacks']), use_container_width=True)
                    # Load Balancer zintegrowany z kafelkiem
                    process_cog_analysis_ui(veh, truck['stacks'])
                
                with dat_col:
                    st.markdown("**OPERATIONAL KPI**")
                    st.write(f"Zajęte LDM: **{truck['ldm']:.2f} m**")
                    st.write(f"Masa Ładunku: **{truck['weight']} kg**")
                    st.write(f"Zapas Masy: **{veh['max_w'] - truck['weight']} kg**")
                    
                    st.divider()
                    st.markdown("**CARGO MANIFEST DETAILS**")
                    sku_counts = pd.Series([it['name'] for s in truck['stacks'] for it in s['items']]).value_counts().reset_index()
                    sku_counts.columns = ['SKU IDENTIFIER', 'QTY']
                    
                    html_table = '<table class="v-tactical-table"><tr><th>SKU</th><th>UNIT QTY</th></tr>'
                    for _, r in sku_counts.iterrows():
                        c_hex = get_vorteza_sku_color(r['SKU IDENTIFIER'])
                        html_table += f'<tr><td><span style="color:{c_hex}">■</span> {r["SKU IDENTIFIER"]}</td><td>{r["UNIT QTY"]}</td></tr>'
                    st.markdown(html_table + '</table>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.info("VORTEZA STACK STATUS: WAITING FOR MISSION DATA. INJECT MANIFEST VIA SIDEBAR.")

    # --------------------------------------------------------------------------
    # TAB 2: MASTER INVENTORY (CRUD)
    # --------------------------------------------------------------------------
    with tab_db:
        st.markdown("### 📦 PRODUCT ARCHITECTURE ADMINISTRATION")
        
        with st.expander("➕ REGISTER NEW CARGO SPECIFICATION"):
            with st.form("AddAssetSupreme"):
                fn = st.text_input("Product Identifier (SKU Name)")
                c_i1, c_i2, c_i3 = st.columns(3)
                f_l = c_i1.number_input("Length (cm)", 120)
                f_w = c_i2.number_input("Width (cm)", 80)
                f_h = c_i3.number_input("Height (cm)", 100)
                c_i4, c_i5 = st.columns(2)
                f_m = c_i4.number_input("Mass (kg)", 100)
                f_i = c_i5.number_input("Items Per Unit (IPU)", 1)
                ca1, ca2 = st.columns(2)
                fs = ca1.checkbox("Stacking Permission", True)
                fr = ca2.checkbox("Rotation Authorized", True)
                if st.form_submit_button("COMMIT TO MASTER DATABASE"):
                    inventory_db.append({
                        "name": fn, "length": f_l, "width": f_w, "height": f_h, 
                        "weight": f_m, "itemsPerCase": f_i, "canStack": fs, "allowRotation": fr
                    })
                    db_core_save_vorteza(inventory_db)
                    st.success("PROTOCOL SUCCESS: Database synchronized."); st.rerun()

        st.divider()
        if inventory_db:
            st.markdown("**GLOBAL INVENTORY ARCHIVE**")
            df_edit = pd.DataFrame(inventory_db)
            edt_session = st.data_editor(df_edit, use_container_width=True, num_rows="dynamic", key="supreme_db_editor")
            if st.button("PUSH LOCAL CHANGES TO CLOUD", type="primary"):
                db_core_save_vorteza(edt_session.to_dict('records'))
                st.success("DATABASE STATUS: SYNCHRONIZED SUCCESSFULLY.")
        else:
            st.warning("DATABASE STATUS: NO ASSETS DETECTED IN ARCHIVE.")

    # --------------------------------------------------------------------------
    # TAB 3: SYSTEM TERMINAL
    # --------------------------------------------------------------------------
    with tab_terminal:
        st.code(f"SYSTEM: VORTEZA STACK v23.0\nFIRM: VORTEZA SYSTEMS\nSESSION_START: {datetime.now()}\nLOGISTICS_CORE: Supreme-Apex\nSTATUS: Operational Nominal", language="bash")

if __name__ == "__main__":
    main()
