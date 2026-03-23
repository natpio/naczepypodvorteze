# -*- coding: utf-8 -*-
"""
================================================================================
SYSTEM: VORTEZA STACK 
VERSION: 20.0 | OMNI ARCHITECT
FIRM: VORTEZA SYSTEMS
================================================================================
INDUSTRIAL GRADE LOGISTICS & 3D ENGINEERING ENGINE
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
# 1. ARCHITEKTURA SYSTEMU I KONFIGURACJA FLOTY
# ==============================================================================
st.set_page_config(
    page_title="VORTEZA STACK v20.0",
    layout="wide",
    initial_sidebar_state="expanded",
    page_icon="🕋"
)

# REJESTR FLOTY VORTEZA (DANE INŻYNIERYJNE)
FLEET_REGISTRY = {
    "TIR FTL (Mega 13.6m)": {
        "max_w": 24000, "L": 1360, "W": 248, "H": 300, 
        "ldm_max": 13.6, "axles": 3, "wheelbase": 850, "tare": 14500,
        "cab_l": 220, "axle_load_limit": 8000
    },
    "TIR FTL (Standard 13.6m)": {
        "max_w": 24000, "L": 1360, "W": 248, "H": 275, 
        "ldm_max": 13.6, "axles": 3, "wheelbase": 850, "tare": 13800,
        "cab_l": 220, "axle_load_limit": 8000
    },
    "Solo 9m (Heavy Logistics)": {
        "max_w": 9500, "L": 920, "W": 245, "H": 270, 
        "ldm_max": 9.2, "axles": 2, "wheelbase": 550, "tare": 8500,
        "cab_l": 180, "axle_load_limit": 6000
    },
    "Solo 7m (Medium Distribution)": {
        "max_w": 7000, "L": 720, "W": 245, "H": 260, 
        "ldm_max": 7.2, "axles": 2, "wheelbase": 480, "tare": 6200,
        "cab_l": 160, "axle_load_limit": 5000
    },
    "BUS XL (Express Courier)": {
        "max_w": 1250, "L": 485, "W": 175, "H": 220, 
        "ldm_max": 4.8, "axles": 2, "wheelbase": 320, "tare": 2250,
        "cab_l": 130, "axle_load_limit": 1500
    }
}

# ==============================================================================
# 2. VORTEZA STACK BRANDING & CSS ENGINE
# ==============================================================================
def get_image_base64(path):
    """Bezpieczne ładowanie zasobów do CSS."""
    try:
        if os.path.exists(path):
            with open(path, 'rb') as f:
                return base64.b64encode(f.read()).decode()
        return ""
    except:
        return ""

def inject_vorteza_stack_ui():
    """Wstrzykuje kompletny, rygorystyczny design system VORTEZA STACK."""
    bg_b64 = get_image_base64('bg_vorteza.png')
    
    st.markdown(f"""
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;600;700&family=JetBrains+Mono:wght@300;400;500&display=swap');
            
            :root {{
                --v-copper: #B58863;
                --v-copper-glow: rgba(181, 136, 99, 0.4);
                --v-dark-obsidian: #030303;
                --v-panel-bg: rgba(8, 8, 8, 0.97);
                --v-border: rgba(181, 136, 99, 0.25);
                --v-neon: #00FF41;
                --v-danger: #FF3131;
            }}

            /* Główna architektura wizualna */
            .stApp {{
                background-image: url("data:image/png;base64,{bg_b64}");
                background-size: cover;
                background-attachment: fixed;
                color: #FFFFFF;
                font-family: 'Montserrat', sans-serif;
            }}

            /* Panele systemowe STACK */
            .v-stack-panel {{
                background: var(--v-panel-bg);
                padding: 3.5rem;
                border-radius: 2px;
                border: 1px solid var(--v-border);
                border-left: 15px solid var(--v-copper);
                box-shadow: 0 60px 150px rgba(0,0,0,0.95);
                margin-bottom: 4rem;
                backdrop-filter: blur(50px);
            }}

            /* Sidebar Engineering */
            section[data-testid="stSidebar"] {{
                background-color: rgba(4, 4, 4, 0.98) !important;
                border-right: 1px solid var(--v-border);
                width: 500px !important;
                backdrop-filter: blur(30px);
            }}

            /* Nagłówki */
            h1, h2, h3 {{ 
                color: var(--v-copper) !important; 
                text-transform: uppercase; 
                letter-spacing: 12px !important; 
                font-weight: 700 !important; 
                text-shadow: 3px 3px 25px rgba(0,0,0,0.7);
            }}

            /* Metryki Apex */
            [data-testid="stMetricValue"] {{ 
                color: var(--v-copper) !important; 
                font-family: 'JetBrains Mono', monospace !important; 
                font-size: 3.8rem !important;
                font-weight: 300 !important;
            }}
            [data-testid="stMetricLabel"] {{
                text-transform: uppercase;
                letter-spacing: 3px;
                color: #888 !important;
            }}

            /* Kontrolery (Przyciski) */
            .stButton > button {{
                background: linear-gradient(180deg, #0a0a0a, #151515);
                color: var(--v-copper);
                border: 1px solid var(--v-copper);
                padding: 1.8rem;
                text-transform: uppercase;
                letter-spacing: 8px;
                font-weight: 700;
                width: 100%;
                transition: 0.7s all cubic-bezier(0.19, 1, 0.22, 1);
                border-radius: 0;
            }}
            .stButton > button:hover {{
                background: var(--v-copper);
                color: black;
                box-shadow: 0 0 100px rgba(181, 136, 99, 1);
                transform: translateY(-5px);
            }}

            /* Tabele systemowe V-TACTICAL */
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

            /* Inżynieryjny Load Balancer */
            .v-cog-rail {{
                width: 100%;
                height: 35px;
                background: #0a0a0a;
                border-radius: 17px;
                position: relative;
                border: 2px solid #222;
                margin: 60px 0;
                box-shadow: inset 0 0 20px #000;
            }}
            .v-cog-pointer {{
                position: absolute;
                width: 10px;
                height: 65px;
                top: -15px;
                background: var(--v-neon);
                box-shadow: 0 0 40px var(--v-neon);
                border-radius: 5px;
                transition: left 1s cubic-bezier(0.19, 1, 0.22, 1);
            }}
            
            .v-status-tag {{
                background: rgba(181,136,99,0.1);
                border: 1px solid var(--v-copper);
                padding: 20px;
                font-family: 'JetBrains Mono', monospace;
                font-size: 0.85rem;
                margin-bottom: 20px;
            }}
        </style>
    """, unsafe_allow_html=True)

# ==============================================================================
# 3. KONTROLA BEZPIECZEŃSTWA (SECURITY GATEWAY)
# ==============================================================================
def authenticate_stack_access():
    """Weryfikuje uprawnienia dostępu do terminala VORTEZA STACK."""
    if "authorized" not in st.session_state:
        st.session_state.authorized = False

    if not st.session_state.authorized:
        try:
            # Pobieranie hasła z Streamlit Cloud Secrets
            sys_key = str(st.secrets.get("password", "vorteza2026"))
        except:
            sys_key = "vorteza2026"

        st.markdown("<br><br><br><br><br><br>", unsafe_allow_html=True)
        _, col_auth, _ = st.columns([1, 1.8, 1])
        with col_auth:
            with st.form("VortezaAuthProtocol"):
                st.markdown("<h2 style='text-align:center;'>VORTEZA STACK</h2>", unsafe_allow_html=True)
                st.markdown("<p style='text-align:center; color:#333; font-size:0.8rem; letter-spacing:8px;'>MASTER ENCRYPTION KEY REQUIRED</p>", unsafe_allow_html=True)
                pwd_in = st.text_input("GOLIATH AUTHENTICATION KEY", type="password")
                if st.form_submit_button("VALIDATE SECURITY CLEARANCE"):
                    if pwd_in == sys_key:
                        st.session_state.authorized = True
                        st.rerun()
                    else:
                        st.error("FATAL ERROR: SECURITY BREACH - INVALID SYSTEM KEY")
        return False
    return True

# ==============================================================================
# 4. CHROMATIC SKU ENGINE (STABILNY SILNIK BARW)
# ==============================================================================
def get_sku_color_map(sku_name):
    """Zwraca stały, unikalny kolor metaliczny dla każdego SKU."""
    palette = [
        "#B58863", "#D4AF37", "#8E6A4D", "#5E4633", "#A67C52", 
        "#2C3E50", "#34495E", "#1A252F", "#16A085", "#27AE60",
        "#7F8C8D", "#95A5A6", "#BDC3C7", "#7E4A35", "#C0392B",
        "#D35400", "#F39C12", "#2980B9", "#8E44AD", "#3D3D3D"
    ]
    # Deterministyczne ziarno oparte na nazwie produktu
    random.seed(sum(ord(c) for c in sku_name))
    return random.choice(palette)

# ==============================================================================
# 5. RENDERER CAD-3D STACK (ENGINE v20.0)
# ==============================================================================
def render_stack_visualizer_3d(vehicle_specs, cargo_clusters):
    """Generuje techniczny model 3D naczepy w standardzie VORTEZA CAD."""
    fig = go.Figure()
    L, W, H = vehicle_specs['L'], vehicle_specs['W'], vehicle_specs['H']

    # --- KONSTRUKCJA POJAZDU (CAD DETAIL) ---
    # Podłoga i Rama główna
    fig.add_trace(go.Mesh3d(x=[0, L, L, 0], y=[0, 0, W, W], z=[-15, -15, -15, -15], color='#111', opacity=1, hoverinfo='skip'))
    
    # Inżynieria kół i osi
    axles = vehicle_specs.get('axles', 3)
    ax_spacing = 145
    rear_pos_start = L - 420 if L > 800 else L - 180
    
    for i in range(axles):
        px = rear_pos_start + (i * ax_spacing)
        if px < L:
            for side in [-38, W+22]:
                # Opona CAD
                fig.add_trace(go.Mesh3d(
                    x=[px-55, px+55, px+55, px-55], y=[side, side, side+18, side+18], 
                    z=[-75, -75, -15, -15], color='#000', opacity=1, hoverinfo='skip'
                ))
                # Felga Miedziana
                fig.add_trace(go.Mesh3d(
                    x=[px-25, px+25, px+25, px-25], y=[side-2, side-2, side, side], 
                    z=[-55, -55, -35, -35], color='#B58863', opacity=0.9, hoverinfo='skip'
                ))

    # Kabina Commander (Solid Block)
    c_l = vehicle_specs.get('cab_l', 240)
    fig.add_trace(go.Mesh3d(
        x=[-c_l, 0, 0, -c_l, -c_l, 0, 0, -c_l],
        y=[-45, -45, W+45, W+45, -45, -45, W+45, W+45],
        z=[0, 0, 0, 0, H*1.05, H*1.05, H*1.05, H*1.05],
        i=[7,0,0,0,4,4,6,6,4,0,3,2], j=[3,4,1,2,5,6,5,2,0,1,6,3], k=[0,7,2,3,6,7,1,1,5,5,7,6],
        color='#020202', opacity=1, name="COMMAND_CAB"
    ))

    # Szkielet Naczepy (Copper Cage)
    skeleton = [
        ([0, L], [0, 0], [0, 0]), ([0, L], [W, W], [0, 0]),
        ([0, 0], [0, W], [0, 0]), ([L, L], [0, W], [0, 0]),
        ([0, 0], [0, 0], [0, H]), ([0, 0], [W, W], [0, H]),
        ([0, L], [0, 0], [H, H]), ([0, L], [W, W], [H, H]),
        ([L, L], [0, 0], [0, H]), ([L, L], [W, W], [0, H])
    ]
    for sx, sy, sz in skeleton:
        fig.add_trace(go.Scatter3d(x=sx, y=sy, z=sz, mode='lines', line=dict(color='#B58863', width=12), hoverinfo='skip'))

    # --- RENDER CARGO (DYNAMIC CHROMATIC MAPPING) ---
    for cluster in cargo_clusters:
        for unit in cluster['items']:
            x, y, z = cluster['x'], cluster['y'], unit['z']
            dx, dy, dz = unit['w_fit'], unit['l_fit'], unit['height']
            p_color = get_sku_color_map(unit['name'])
            
            # Bryła 3D produktu
            fig.add_trace(go.Mesh3d(
                x=[x,x+dx,x+dx,x,x,x+dx,x+dx,x], y=[y,y,y+dy,y+dy,y,y,y+dy,y+dy], 
                z=[z,z,z+dz,z+dz,z,z,z+dz,z+dz],
                i=[7,0,0,0,4,4,6,6,4,0,3,2], j=[3,4,1,2,5,6,5,2,0,1,6,3], k=[0,7,2,3,6,7,1,1,5,5,7,6],
                color=p_color, opacity=0.98, name=unit['name'],
                hovertemplate=f"<b>{unit['name']}</b><br>D: {dx}cm W: {dy}cm H: {dz}cm<br>ROTACJA: {'TAK' if unit.get('allowRotation', True) else 'NIE'}<extra></extra>"
            ))
            # Kontur Separacji (Edge detection)
            fig.add_trace(go.Scatter3d(
                x=[x,x+dx,x+dx,x,x,x+dx,x+dx,x,x,x+dx,x+dx,x+dx,x+dx,x,x],
                y=[y,y,y+dy,y+dy,y,y,y+dy,y+dy,y+dy,y+dy,y+dy,y,y,y+dy,y+dy,y],
                z=[z,z,z+dz,z+dz,z,z,z+dz,z+dz,z+dz,z+dz,z+dz,z,z,z+dz,z+dz],
                mode='lines', line=dict(color='black', width=3), hoverinfo='skip'
            ))

    fig.update_layout(
        scene=dict(
            aspectmode='data', xaxis_visible=False, yaxis_visible=False, zaxis_visible=False,
            camera=dict(eye=dict(x=2.5, y=2.5, z=2.0)), bgcolor='rgba(0,0,0,0)'
        ),
        paper_bgcolor='rgba(0,0,0,0)', margin=dict(l=0, r=0, b=0, t=0), showlegend=False
    )
    return fig

# ==============================================================================
# 6. SILNIK PAKOWANIA V-ENGINE 20.0 (V-PERMIT & OFFSET CONTROL)
# ==============================================================================
class V20StackEngine:
    """Zaawansowany algorytm pakowania 3D z kontrolą pozwoleń i przesunięcia X."""
    
    @staticmethod
    def execute_solve(cargo_list, vehicle, x_offset=0):
        # Priorytetyzacja: 1. No-Stack, 2. No-Rotation, 3. Pole podstawy (L*W)
        items_sorted = sorted(cargo_list, 
                             key=lambda x: (not x.get('canStack', True), 
                                            not x.get('allowRotation', True), 
                                            x['width']*x['length']), 
                             reverse=True)
        
        placed_stacks = []
        failed_units = []
        accumulated_mass = 0
        cx, cy, current_row_max_w = x_offset, 0, 0

        for unit in items_sorted:
            # Weryfikacja payloadu
            if accumulated_mass + unit['weight'] > vehicle['max_w']:
                failed_units.append(unit); continue
            
            # PROTOKÓŁ PIĘTROWANIA (Vertical Integration)
            is_stacked = False
            if unit.get('canStack', True):
                for s in placed_stacks:
                    # Dopasowanie z uwzględnieniem ZABLOKOWANEJ rotacji
                    if unit.get('allowRotation', True):
                        dim_match = (unit['width'] <= s['w'] and unit['length'] <= s['l']) or \
                                  (unit['length'] <= s['w'] and unit['width'] <= s['l'])
                    else:
                        dim_match = (unit['width'] <= s['w'] and unit['length'] <= s['l'])
                    
                    if dim_match and (s['curH'] + unit['height'] <= vehicle['H']):
                        u_copy = unit.copy(); u_copy['z'] = s['curH']
                        u_copy['w_fit'], u_copy['l_fit'] = s['w'], s['l']
                        s['items'].append(u_copy); s['curH'] += unit['height']
                        accumulated_mass += unit['weight']; is_stacked = True; break
            
            if is_stacked: continue

            # PROTOKÓŁ PODŁOGI (Floor placement + V-PERMIT ROTATION)
            is_placed = False
            if unit.get('allowRotation', True):
                orientations = [(unit['width'], unit['length']), (unit['length'], unit['width'])]
            else:
                orientations = [(unit['width'], unit['length'])]
            
            for fw, fl in orientations:
                if cy + fl <= vehicle['W'] and cx + fw <= vehicle['L']:
                    u_c = unit.copy(); u_c['z'] = 0; u_c['w_fit'], u_c['l_fit'] = fw, fl
                    placed_stacks.append({'x':cx, 'y':cy, 'w':fw, 'l':fl, 'curH':unit['height'], 'items':[u_c]})
                    cy += fl; current_row_max_w = max(current_row_max_w, fw)
                    accumulated_mass += unit['weight']; is_placed = True; break
                elif cx + current_row_max_w + fw <= vehicle['L'] and fl <= vehicle['W']:
                    cx += current_row_max_w; cy = 0; current_row_max_w = fw
                    u_c = unit.copy(); u_c['z'] = 0; u_c['w_fit'], u_c['l_fit'] = fw, fl
                    placed_stacks.append({'x':cx, 'y':cy, 'w':fw, 'l':fl, 'curH':unit['height'], 'items':[u_c]})
                    cy += fl; accumulated_mass += unit['weight']; is_placed = True; break
            
            if not is_placed: failed_units.append(unit)
        
        ldm_res = (max([s['x'] + s['w'] for s in placed_stacks]) / 100) if placed_stacks else 0
        return placed_stacks, accumulated_mass, failed_units, ldm_res

# ==============================================================================
# 7. ANALITYKA INŻYNIERYJNA (TACTICAL LOAD BALANCER)
# ==============================================================================
def render_tactical_load_balancer(vehicle, stacks):
    """Oblicza środek ciężkości (CoG) i symuluje nacisk na osie."""
    if not stacks: return
    
    total_moment = 0
    total_weight = 0
    
    for s in stacks:
        for it in s['items']:
            item_center_x = s['x'] + (it['w_fit'] / 2)
            total_moment += (item_center_x * it['weight'])
            total_weight += it['weight']
    
    cog_x = total_moment / total_weight if total_weight > 0 else 0
    cog_pct = (cog_x / vehicle['L']) * 100
    
    st.markdown("### ⚖️ CENTER OF GRAVITY ANALYSIS (CoG)")
    st.write(f"Położenie środka ciężkości ładunku: **{cog_x/100:.2f} m** od ściany przedniej")
    
    marker_color = "#00FF41" if 35 < cog_pct < 65 else "#FF3131"
    
    st.markdown(f"""
        <div class="v-cog-rail">
            <div class="v-cog-pointer" style="left: {cog_pct}%;"></div>
            <div style="position:absolute; left:20px; top:45px; font-size:0.65rem; color:#888;">DRIVE AXLES (PRZÓD)</div>
            <div style="position:absolute; right:20px; top:45px; font-size:0.65rem; color:#888;">TRAILER AXLES (TYŁ)</div>
        </div>
        <br><br>
    """, unsafe_allow_html=True)
    
    if cog_pct < 35:
        st.error("ALARM: PRZECIĄŻENIE OSI NAPĘDOWYCH. Użyj suwaka OFFSET w panelu bocznym, aby przesunąć towar na tył.")
    elif cog_pct > 65:
        st.error("ALARM: ODCIĄŻENIE OSI STERUJĄCEJ. Zmniejsz OFFSET lub usuń towar z tyłu naczepy.")
    else:
        st.success("STATUS NOMINALNY: Rozkład masy optymalny dla stabilności zestawu.")

# ==============================================================================
# 8. DATA I/O & SYSTEM PERSISTENCE
# ==============================================================================
def db_io_load():
    try:
        if os.path.exists('products.json'):
            with open('products.json', 'r', encoding='utf-8') as f: return json.load(f)
        return []
    except: return []

def db_io_save(data):
    with open('products.json', 'w', encoding='utf-8') as f: 
        json.dump(data, f, indent=4, ensure_ascii=False)

# ==============================================================================
# 9. GŁÓWNA ARCHITEKTURA INTERFEJSU (VORTEZA STACK)
# ==============================================================================
def main():
    inject_vorteza_stack_ui()
    if not authenticate_stack_access(): return

    # Stan Manifestu i Inwentarza
    if 'v_manifest' not in st.session_state: st.session_state.v_manifest = []
    inventory_db = db_io_load()

    # --- TOP CONTROL BAR ---
    hc1, hc2, hc3 = st.columns([1, 4, 1])
    with hc1:
        logo_b64 = get_image_base64('logo_vorteza.png')
        if logo_b64: st.markdown(f'<img src="data:image/png;base64,{logo_b64}" width="180">', unsafe_allow_html=True)
        else: st.markdown("### VORTEZA")
    with hc2:
        st.markdown("<h1>VORTEZA STACK</h1>", unsafe_allow_html=True)
        st.markdown(f"<p class='v-version-tag' style='color:#444; font-size:0.7rem; letter-spacing:5px;'>v20.0 OMNI ARCHITECT | CORE STATUS: NOMINAL | {datetime.now().strftime('%H:%M')}</p>", unsafe_allow_html=True)
    with hc3:
        if st.button("TERMINATE"):
            st.session_state.authorized = False; st.rerun()

    # --- SIDEBAR: MISSION COMMAND ---
    with st.sidebar:
        st.markdown("### 📡 FLEET CONSOLE")
        v_sel_key = st.selectbox("TRANSPORT UNIT SELECTOR", list(FLEET_REGISTRY.keys()))
        veh = FLEET_REGISTRY[v_sel_key]
        
        st.divider()
        st.markdown("### ⚖️ DYNAMIC POSITIONING")
        # Suwak przesunięcia ładunku dla Load Balancera
        v_offset = st.slider("OFFSET OD ŚCIANY (cm)", 0, veh['L']-200, 0)
        st.caption("Przesuń ładunek na tył, aby skorygować balans osi.")
        
        st.divider()
        st.markdown("### 📥 MANIFEST INJECTION")
        p_names = [p['name'] for p in inventory_db]
        sel_sku = st.selectbox("SKU SELECTOR", p_names, index=None)
        
        if sel_sku:
            p_ref = next(p for p in inventory_db if p['name'] == sel_sku)
            ipc = p_ref.get('itemsPerCase', 1)
            p_rot = p_ref.get('allowRotation', True)
            st.markdown(f"""
                <div class='v-status-tag'>
                    SKU: {sel_sku}<br>
                    IPU: {ipc} PCS/CASE<br>
                    ROTACJA: {'<span style="color:#00FF41">AUTHORIZED</span>' if p_rot else '<span style="color:#FF3131">LOCKED</span>'}
                </div>
            """, unsafe_allow_html=True)
            
            qty_in = st.number_input("QUANTITY TO SHIP (PCS)", min_value=1, value=ipc)
            num_units = math.ceil(qty_in / ipc)
            
            if st.button("APPEND TO MANIFEST", type="primary"):
                for i in range(num_units):
                    u_entry = p_ref.copy()
                    u_entry['p_act'] = ipc if (i < num_units - 1 or qty_in % ipc == 0) else (qty_in % ipc)
                    st.session_state.v_manifest.append(u_entry)
                st.rerun()

        if st.button("PURGE ALL DATA"):
            st.session_state.v_manifest = []; st.rerun()

    # --- WORKSPACE TABS ---
    tab_p, tab_b, tab_i, tab_l = st.tabs(["📊 STACK PLANNER", "⚖️ LOAD BALANCER", "📦 PRODUCT CORE", "⚙️ SYSTEM LOGS"])

    # TAB 1: PLANNER
    with tab_p:
        if st.session_state.v_manifest:
            k1, k2, k3, k4 = st.columns(4)
            total_kg = sum(float(u['weight']) for u in st.session_state.v_manifest)
            k1.metric("UNITS", len(st.session_state.v_manifest))
            k2.metric("PCS TOTAL", sum(int(u.get('p_act', 1)) for u in st.session_state.v_manifest))
            k3.metric("GROSS MASS", f"{total_kg} KG")
            k4.metric("UTILIZATION", f"{(total_kg/veh['max_w'])*100:.1f}%")

            # Przeliczenie planu z uwzględnieniem offsetu
            rem_units = [dict(u) for u in st.session_state.v_manifest]
            fleet_assigned = []
            while rem_units:
                st_res, w_res, n_p, ldm_res = V20StackEngine.execute_solve(rem_units, veh, x_offset=v_offset)
                if not st_res: st.error("LOGISTICS FAILURE: UNIT OVERSIZE DETECTED."); break
                fleet_assigned.append({"stacks": st_res, "weight": w_res, "ldm": ldm_res})
                rem_units = n_p

            for idx, truck in enumerate(fleet_assigned):
                st.markdown(f'<div class="v-stack-panel">', unsafe_allow_html=True)
                st.markdown(f"### MISSION UNIT #{idx+1} | {v_sel_key}", unsafe_allow_html=True)
                v_col, d_col = st.columns([2.8, 1])
                with v_col: st.plotly_chart(render_stack_visualizer_3d(veh, truck['stacks']), use_container_width=True)
                with d_col:
                    st.markdown("**OPERATIONAL KPI**")
                    st.write(f"Zajęte LDM: **{truck['ldm']:.2f} m**")
                    st.write(f"Masa Ładunku: **{truck['weight']} kg**")
                    st.divider()
                    st.markdown("**CARGO MANIFEST**")
                    counts = pd.Series([it['name'] for s in truck['stacks'] for it in s['items']]).value_counts().reset_index()
                    counts.columns = ['SKU', 'QTY']
                    html_table = '<table class="v-tactical-table"><tr><th>SKU</th><th>QTY</th></tr>'
                    for _, r in counts.iterrows():
                        c_hex = get_sku_color_map(r['SKU'])
                        html_table += f'<tr><td><span style="color:{c_hex}">■</span> {r["SKU"]}</td><td>{r["QTY"]}</td></tr>'
                    st.markdown(html_table + '</table>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
        else: st.info("VORTEZA STACK: WAITING FOR MANIFEST INJECTION...")

    # TAB 2: LOAD BALANCER
    with tab_b:
        if st.session_state.v_manifest:
            st.markdown('<div class="v-stack-panel">', unsafe_allow_html=True)
            res_st, _, _, _ = V20StackEngine.execute_solve(st.session_state.v_manifest, veh, x_offset=v_offset)
            render_tactical_load_balancer(veh, res_st)
            st.markdown('</div>', unsafe_allow_html=True)
        else: st.warning("NO DATA TO ANALYZE.")

    # TAB 3: PRODUCT CORE (CRUD)
    with tab_i:
        st.markdown("### 📦 PRODUCT ARCHITECTURE ADMINISTRATION")
        with st.expander("➕ REGISTER NEW ASSET PROTOCOL"):
            with st.form("AddAssetCore"):
                fn = st.text_input("Product Identifier (SKU)")
                ci1, ci2, ci3 = st.columns(3)
                fl, fw, fh = ci1.number_input("L (cm)", 120), ci2.number_input("W (cm)", 80), ci3.number_input("H (cm)", 100)
                fm, fi = st.number_input("Mass (kg)", 50), st.number_input("IPU", 1)
                ca1, ca2 = st.columns(2)
                fs, fr = ca1.checkbox("Stacking Permission", True), ca2.checkbox("Rotation Authorized", True)
                if st.form_submit_button("COMMIT TO MASTER DATABASE"):
                    inventory_db.append({"name":fn,"length":fl,"width":fw,"height":fh,"weight":fm,"itemsPerCase":fi,"canStack":fs,"allowRotation":fr})
                    db_io_save(inventory_db); st.success("CORE DATABASE SYNCHRONIZED"); st.rerun()
        st.divider()
        if inventory_db:
            df_display = pd.DataFrame(inventory_db)
            edt_db = st.data_editor(df_display, use_container_width=True, num_rows="dynamic")
            if st.button("PUSH LOCAL CHANGES TO CLOUD"):
                db_io_save(edt_db.to_dict('records')); st.success("ARCHIVE SYNC COMPLETE")

    # TAB 4: SYSTEM LOGS
    with tab_l:
        st.code(f"SYSTEM: VORTEZA STACK v20.0\nARCH: Omni-Architect\nSESSION: {datetime.now()}\nSTATUS: Nominal", language="bash")

if __name__ == "__main__":
    main()
