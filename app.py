# -*- coding: utf-8 -*-
"""
================================================================================
SYSTEM: VORTEZA STACK 
VERSION: 28.0 | OMNI APEX ELITE
FIRM: VORTEZA SYSTEMS
STATUS: ENTERPRISE PRODUCTION READY | FULL SOURCE CODE | NO SHORTCUTS
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
# 1. ŚRODOWISKO I REJESTR TECHNICZNY FLOTY
# ==============================================================================
st.set_page_config(
    page_title="VORTEZA STACK v28.0",
    layout="wide",
    initial_sidebar_state="expanded",
    page_icon="🕋"
)

# SPECYFIKACJA TECHNICZNA JEDNOSTEK TRANSPORTOWYCH VORTEZA
# L, W, H w cm | max_w, tare w kg | cab_l: długość kabiny
FLEET_REGISTRY = {
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
def get_resource_as_base64(file_path):
    """Bezpieczne ładowanie zasobów binarnych dla warstwy CSS i HTML."""
    try:
        if os.path.exists(file_path):
            with open(file_path, 'rb') as f:
                return base64.b64encode(f.read()).decode()
        return ""
    except Exception:
        return ""

def inject_vorteza_supreme_ui():
    """Wstrzykuje rygorystyczny design system VORTEZA STACK."""
    bg_data = get_resource_as_base64('bg_vorteza.png')
    
    st.markdown(f"""
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;600;700&family=JetBrains+Mono:wght@300;400;500&display=swap');
            
            :root {{
                --v-copper: #B58863;
                --v-copper-glow: rgba(181, 136, 99, 0.4);
                --v-dark-obsidian: #020202;
                --v-panel-bg: rgba(8, 8, 8, 0.98);
                --v-border: rgba(181, 136, 99, 0.2);
                --v-neon-green: #00FF41;
            }}

            .stApp {{
                background-image: url("data:image/png;base64,{bg_data}");
                background-size: cover;
                background-attachment: fixed;
                color: #FFFFFF;
                font-family: 'Montserrat', sans-serif;
            }}

            /* TILE SYSTEM */
            .v-tile-apex {{
                background: var(--v-panel-bg);
                padding: 2.5rem;
                border: 1px solid var(--v-border);
                border-left: 15px solid var(--v-copper);
                box-shadow: 0 40px 100px rgba(0,0,0,1);
                margin-bottom: 3.5rem;
                backdrop-filter: blur(50px);
            }}

            section[data-testid="stSidebar"] {{
                background-color: rgba(3, 3, 3, 0.99) !important;
                border-right: 1px solid var(--v-border);
                width: 480px !important;
                backdrop-filter: blur(35px);
            }}

            h1, h2, h3 {{ color: var(--v-copper) !important; text-transform: uppercase; letter-spacing: 10px !important; font-weight: 700 !important; }}

            [data-testid="stMetricValue"] {{ 
                color: var(--v-copper) !important; 
                font-family: 'JetBrains Mono', monospace !important; 
                font-size: 3.8rem !important;
                font-weight: 300 !important;
            }}

            /* Przyciski Inżynieryjne */
            .stButton > button {{
                background: linear-gradient(180deg, #0a0a0a, #1a1a1a);
                color: var(--v-copper);
                border: 2px solid var(--v-copper);
                padding: 1.8rem;
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

            /* Tabele V-Tactical */
            .v-table-tactical {{ 
                width: 100%; 
                border-collapse: collapse; 
                margin-top: 40px; 
                border: 1px solid #111;
            }}
            .v-table-tactical th {{ 
                background: #000; color: var(--v-copper); text-align: left; font-size: 0.85rem; text-transform: uppercase; border-bottom: 3px solid #333; padding: 25px; 
            }}
            .v-table-tactical td {{ padding: 20px 25px; border-bottom: 1px solid #111; color: #CCC; font-size: 1rem; }}
            .v-table-tactical tr:hover {{ background: rgba(181,136,99,0.05); }}

            /* Load Balancer Visualization */
            .v-rail-track {{
                width: 100%; height: 35px; background: #050505; border-radius: 17px; position: relative; border: 2px solid #222; margin: 60px 0;
                box-shadow: inset 0 0 25px #000;
            }}
            .v-cog-pointer {{
                position: absolute; width: 12px; height: 75px; top: -20px; background: var(--v-neon-green); 
                box-shadow: 0 0 45px var(--v-neon-green); border-radius: 6px;
                transition: left 1.5s cubic-bezier(0.19, 1, 0.22, 1);
            }}

            /* Status Tags */
            .v-status-badge {{
                background: rgba(181,136,99,0.05);
                border: 1px solid var(--v-copper);
                padding: 15px;
                margin-bottom: 20px;
                font-family: 'JetBrains Mono', monospace;
                font-size: 0.8rem;
            }}
        </style>
    """, unsafe_allow_html=True)

# ==============================================================================
# 3. KONTROLA BEZPIECZEŃSTWA (AUTH GATEWAY)
# ==============================================================================
def verify_stack_security():
    """Weryfikuje poświadczenia operatora systemu VORTEZA STACK."""
    if "authorized" not in st.session_state:
        st.session_state.authorized = False

    if not st.session_state.authorized:
        try:
            sys_key = str(st.secrets.get("password", "vorteza2026"))
        except Exception:
            sys_key = "vorteza2026"

        st.markdown("<br><br><br><br><br><br><br>", unsafe_allow_html=True)
        _, col_auth, _ = st.columns([1, 2.5, 1])
        with col_auth:
            with st.form("VortezaAuthGate"):
                st.markdown("<h2 style='text-align:center;'>VORTEZA STACK</h2>", unsafe_allow_html=True)
                st.markdown("<p style='text-align:center; color:#333; font-size:0.8rem; letter-spacing:8px;'>MASTER ENCRYPTION KEY REQUIRED</p>", unsafe_allow_html=True)
                pwd_in = st.text_input("GOLIATH MASTER AUTHENTICATION", type="password")
                if st.form_submit_button("VALIDATE SECURITY CLEARANCE"):
                    if pwd_in == sys_key:
                        st.session_state.authorized = True
                        st.rerun()
                    else:
                        st.error("ACCESS DENIED")
        return False
    return True

# ==============================================================================
# 4. CHROMATIC SKU ENGINE
# ==============================================================================
def get_vorteza_color(sku_name):
    """Zwraca unikalny kolor metaliczny dla każdego SKU bazując na jego nazwie."""
    palette = [
        "#B58863", "#D4AF37", "#8E6A4D", "#5E4633", "#A67C52", 
        "#2C3E50", "#34495E", "#1A252F", "#16A085", "#27AE60",
        "#7F8C8D", "#95A5A6", "#BDC3C7", "#7E4A35", "#C0392B",
        "#D35400", "#F39C12", "#2980B9", "#8E44AD", "#3D3D3D"
    ]
    random.seed(sum(ord(c) for c in sku_name))
    return random.choice(palette)

# ==============================================================================
# 5. RENDERER CAD-3D STACK (EXPLICIT VERTEX ENGINE v28.0)
# ==============================================================================
def build_cube_geometry(x, y, z, dx, dy, dz, color, name):
    """Tworzy matematycznie poprawną geometrię 3D prostopadłościanu przy użyciu trójkątów."""
    # 8 Wierzchołków bryły
    vx = [x, x+dx, x+dx, x, x, x+dx, x+dx, x]
    vy = [y, y, y+dy, y+dy, y, y, y+dy, y+dy]
    vz = [z, z, z, z, z+dz, z+dz, z+dz, z+dz]
    
    # 12 Trójkątów (6 ścian po 2 trójkąty)
    # i, j, k to indeksy wierzchołków tworzących ściany
    i = [7, 0, 0, 0, 4, 4, 6, 6, 4, 0, 3, 2]
    j = [3, 4, 1, 2, 5, 6, 5, 2, 0, 1, 6, 3]
    k = [0, 7, 2, 3, 6, 7, 1, 1, 5, 5, 7, 6]
    
    mesh = go.Mesh3d(
        x=vx, y=vy, z=vz, i=i, j=j, k=k,
        color=color, opacity=0.99, name=name,
        flatshading=True, lighting=dict(ambient=0.4, diffuse=0.8, specular=1),
        hovertemplate=f"<b>{name}</b><br>D: {dx}cm W: {dy}cm H: {dz}cm<extra></extra>"
    )
    
    # Obrys krawędzi (Outline Scatter3d)
    lx = [x, x+dx, x+dx, x, x, x, x+dx, x+dx, x, x, x+dx, x+dx, x+dx, x+dx, x, x]
    ly = [y, y, y+dy, y+dy, y, y, y, y+dy, y+dy, y+dy, y+dy, y, y, y+dy, y+dy, y]
    lz = [z, z, z, z, z, z+dz, z+dz, z, z, z+dz, z+dz, z+dz, z, z, z+dz, z+dz]
    
    lines = go.Scatter3d(x=lx, y=ly, z=lz, mode='lines', line=dict(color='black', width=3), hoverinfo='skip')
    return [mesh, lines]

def render_vorteza_cad_3d(vehicle_specs, cargo_stacks):
    """Generuje kompletny inżynieryjny model 3D naczepy wraz z ładunkiem."""
    fig = go.Figure()
    L, W, H = vehicle_specs['L'], vehicle_specs['W'], vehicle_specs['H']

    # --- KONSTRUKCJA NACZEPY ---
    # Podłoga (Main Floor)
    fig.add_trace(go.Mesh3d(x=[0, L, L, 0], y=[0, 0, W, W], z=[-15, -15, -15, -15], color='#151515', opacity=1, hoverinfo='skip'))
    
    # Koła i Osie
    ax_dist = 145
    rear_x = L - 450 if L > 800 else L - 180
    for a in range(vehicle_specs.get('axles', 3)):
        ax_x = rear_x + (a * ax_dist)
        if ax_x < L:
            for side in [-40, W+25]:
                # Opona
                fig.add_trace(go.Mesh3d(x=[ax_x-60, ax_x+60, ax_x+60, ax_x-60], y=[side, side, side+18, side+18], z=[-85, -85, -15, -15], color='#000', opacity=1, hoverinfo='skip'))
                # Felga miedziana
                fig.add_trace(go.Mesh3d(x=[ax_x-25, ax_x+25, ax_x+25, ax_x-25], y=[side-2, side-2, side, side], z=[-60, -60, -35, -35], color='#B58863', opacity=0.9, hoverinfo='skip'))

    # Kabina Commander
    cab_l = vehicle_specs.get('cab_l', 230)
    fig.add_trace(go.Mesh3d(x=[-cab_l, 0, 0, -cab_l, -cab_l, 0, 0, -cab_l], y=[-45, -45, W+45, W+45], z=[0, 0, 0, 0, H*1.05, H*1.05, H*1.05, H*1.05], i=[7,0,0,0,4,4,6,6,4,0,3,2], j=[3,4,1,2,5,6,5,2,0,1,6,3], k=[0,7,2,3,6,7,1,1,5,5,7,6], color='#050505', opacity=1))

    # Klatka miedziana (Skeleton)
    skeleton = [([0, L], [0, 0], [0, 0]), ([0, L], [W, W], [0, 0]), ([0, 0], [0, W], [0, 0]), ([L, L], [0, W], [0, 0]),
                ([0, 0], [0, 0], [0, H]), ([0, 0], [W, W], [0, H]), ([0, L], [0, 0], [H, H]), ([0, L], [W, W], [H, H])]
    for lx, ly, lz in skeleton:
        fig.add_trace(go.Scatter3d(x=lx, y=ly, z=lz, mode='lines', line=dict(color='#B58863', width=12), hoverinfo='skip'))

    # --- RENDER TOWARU ---
    for cluster in cargo_stacks:
        for unit in cluster['items']:
            parts = build_cube_geometry(cluster['x'], cluster['y'], unit['z'], unit['w_fit'], unit['l_fit'], unit['height'], get_vorteza_color(unit['name']), unit['name'])
            for p in parts: fig.add_trace(p)

    fig.update_layout(scene=dict(aspectmode='data', xaxis_visible=False, yaxis_visible=False, zaxis_visible=False, camera=dict(eye=dict(x=2.5, y=2.5, z=2.0))), paper_bgcolor='rgba(0,0,0,0)', margin=dict(l=0, r=0, b=0, t=0), showlegend=False)
    return fig

# ==============================================================================
# 6. SILNIK PAKOWANIA V-ENGINE 28.0 (OMNI OPTIMIZER)
# ==============================================================================
class V28SupremeEngine:
    """Zaawansowany algorytm pakowania 3D z pełną kontrolą parametrów."""
    
    @staticmethod
    def solve_mission(cargo_list, vehicle, x_offset=0):
        # Priorytetyzacja: 1. No-Stack, 2. No-Rotation, 3. Area (L*W)
        items_sorted = sorted(cargo_list, key=lambda x: (not x.get('canStack', True), not x.get('allowRotation', True), x['width']*x['length']), reverse=True)
        placed_stacks, failed, mass_acc = [], [], 0
        cx, cy, current_row_max_w = x_offset, 0, 0

        for unit in items_sorted:
            # Walidacja wagi dopuszczalnej
            if mass_acc + unit['weight'] > vehicle['max_w']:
                failed.append(unit); continue
            
            # FAZA 1: STACKING (Piętrowanie pionowe)
            integrated = False
            if unit.get('canStack', True):
                for s in placed_stacks:
                    rot_p = unit.get('allowRotation', True)
                    fit = (unit['width'] <= s['w'] and unit['length'] <= s['l']) or (unit['length'] <= s['w'] and unit['width'] <= s['l']) if rot_p else (unit['width'] <= s['w'] and unit['length'] <= s['l'])
                    if fit and (s['curH'] + unit['height'] <= vehicle['H']):
                        u_copy = unit.copy(); u_copy['z'] = s['curH']; u_copy['w_fit'], u_copy['l_fit'] = s['w'], s['l']
                        s['items'].append(u_copy); s['curH'] += unit['height']; mass_acc += unit['weight']; integrated = True; break
            
            if integrated: continue

            # FAZA 2: FLOOR (Układanie na podłodze)
            placed = False
            orientations = [(unit['width'], unit['length']), (unit['length'], unit['width'])] if unit.get('allowRotation', True) else [(unit['width'], unit['length'])]
            for fw, fl in orientations:
                if cy + fl <= vehicle['W'] and cx + fw <= vehicle['L']:
                    u_c = unit.copy(); u_c['z'] = 0; u_c['w_fit'], u_c['l_fit'] = fw, fl
                    placed_stacks.append({'x':cx, 'y':cy, 'w':fw, 'l':fl, 'curH':unit['height'], 'items':[u_c]})
                    cy += fl; current_row_max_w = max(current_row_max_w, fw); mass_acc += unit['weight']; placed = True; break
                elif cx + current_row_max_w + fw <= vehicle['L'] and fl <= vehicle['W']:
                    cx += current_row_max_w; cy = 0; current_row_max_w = fw
                    u_c = unit.copy(); u_c['z'] = 0; u_c['w_fit'], u_c['l_fit'] = fw, fl
                    placed_stacks.append({'x':cx, 'y':cy, 'w':fw, 'l':fl, 'curH':unit['height'], 'items':[u_c]})
                    cy += fl; mass_acc += unit['weight']; placed = True; break
            if not placed: failed.append(unit)
        
        ldm_real = (max([s['x'] + s['w'] for s in placed_stacks]) / 100) if placed_stacks else 0
        return placed_stacks, mass_acc, failed, ldm_real

# ==============================================================================
# 7. ANALITYKA CoG
# ==============================================================================
def process_load_balancer(veh, stacks):
    """Wylicza i wizualizuje balans masy na osiach."""
    if not stacks: return
    t_mom, t_w = 0, 0
    for s in stacks:
        for it in s['items']:
            t_mom += (s['x'] + it['w_fit']/2) * it['weight']
            t_w += it['weight']
    cog_p = (t_mom / t_w / veh['L']) * 100 if t_w > 0 else 0
    st.markdown("### ⚖️ CENTER OF GRAVITY ANALYSIS (CoG)")
    clr = "#00FF41" if 35 < cog_p < 65 else "#FF3131"
    st.markdown(f'<div class="v-rail-track"><div class="v-cog-pointer" style="left:{cog_p}%; background:{clr}; box-shadow:0 0 40px {clr};"></div></div>', unsafe_allow_html=True)
    if cog_p < 35: st.warning("ALARM: NACISK NA PRZÓD (OSIE CIĄGNIKA). SKORYGUJ OFFSET.")
    elif cog_p > 65: st.warning("ALARM: NACISK NA TYŁ (OSIE NACZEPY). PRZESUŃ TOWAR DO PRZODU.")
    else: st.success("BALANCE OPTYMALNY.")

# ==============================================================================
# 8. DATA I/O
# ==============================================================================
def db_load():
    """Wczytuje bazę SKU."""
    if os.path.exists('products.json'):
        try:
            with open('products.json', 'r', encoding='utf-8') as f: return json.load(f)
        except Exception: return []
    return []

def db_save(data):
    """Zapisuje bazę SKU."""
    with open('products.json', 'w', encoding='utf-8') as f: json.dump(data, f, indent=4, ensure_ascii=False)

# ==============================================================================
# 9. GŁÓWNA ARCHITEKTURA (VORTEZA STACK)
# ==============================================================================
def main():
    inject_vorteza_supreme_ui()
    if not verify_stack_security(): return
    if 'v_manifest' not in st.session_state: st.session_state.v_manifest = []
    inventory = db_load()

    # HEADER
    hc1, hc2, hc3 = st.columns([1, 4, 1])
    with hc1:
        l_data = get_resource_as_base64('logo_vorteza.png')
        if l_data: st.markdown(f'<img src="data:image/png;base64,{l_data}" width="180">', unsafe_allow_html=True)
    with hc2:
        st.markdown("<h1>VORTEZA STACK</h1>")
        st.markdown(f"<p style='color:#444; letter-spacing:8px; font-size:0.75rem; font-weight:600;'>v28.0 OMNI APEX ELITE | STATUS: OPERATIONAL</p>", unsafe_allow_html=True)
    with hc3:
        if st.button("TERMINATE"): st.session_state.authorized = False; st.rerun()

    # SIDEBAR
    with st.sidebar:
        st.markdown("### 📡 FLEET CONSOLE")
        v_key = st.selectbox("POJAZD DOCELOWY", list(FLEET_REGISTRY.keys()))
        veh = FLEET_REGISTRY[v_key]
        x_off_val = st.slider("OFFSET OD ŚCIANY (cm)", 0, veh['L']-200, 0, key="x_offset")
        
        st.divider()
        st.markdown("### 📐 V-TRUSS CALCULATOR")
        c_t1, c_t2 = st.columns(2)
        t2m = c_t1.number_input("KRATY 2M (SZT)", 0, 400, 0)
        t3m = c_t2.number_input("KRATY 3M (SZT)", 0, 400, 0)
        
        if st.button("PRZELICZ I DODAJ WÓZKI", type="secondary"):
            c2m = math.ceil(t2m / 14)
            c3m = math.ceil(t3m / 14)
            
            # DEFINICJE WÓZKÓW (H=240 CM - UREALNIONA)
            p51 = {"name": "truss cart 14x2", "length": 200, "width": 60, "height": 240, "weight": 420, "canStack": False, "allowRotation": True}
            p52 = {"name": "truss cart 14x3", "length": 300, "width": 60, "height": 240, "weight": 630, "canStack": False, "allowRotation": True}
            
            for _ in range(c2m): st.session_state.v_manifest.append(p51.copy())
            for _ in range(c3m): st.session_state.v_manifest.append(p52.copy())
            st.toast(f"DODANO: {c2m} wózków 2m oraz {c3m} wózków 3m.")

        st.divider()
        st.markdown("### 📥 MANUAL ENTRY")
        sku_titles = [p['name'] for p in inventory]
        sel_sku = st.selectbox("SKU SELECTOR", sku_titles, index=None)
        if sel_sku:
            p_ref = next(p for p in inventory if p['name'] == sel_sku)
            qty = st.number_input("SZTUKI", 1, 1000, p_ref.get('itemsPerCase', 1))
            if st.button("APPEND TO MANIFEST", type="primary"):
                n_u = math.ceil(qty / p_ref.get('itemsPerCase', 1))
                for _ in range(n_u): 
                    u_entry = p_ref.copy()
                    u_entry['p_act'] = p_ref.get('itemsPerCase', 1)
                    st.session_state.v_manifest.append(u_entry)
                st.rerun()
        if st.button("GLOBAL PURGE"): st.session_state.v_manifest = []; st.rerun()

    # WORKSPACE
    tab_p, tab_i, tab_l = st.tabs(["📊 TACTICAL PLANNER", "📦 MASTER INVENTORY", "⚙️ SYSTEM LOGS"])

    with tab_p:
        if st.session_state.v_manifest:
            # DASHBOARD KPI
            m1, m2, m3, m4 = st.columns(4)
            total_mass = sum(float(u['weight']) for u in st.session_state.v_manifest)
            m1.metric("CASES", len(st.session_state.v_manifest))
            m2.metric("PCS TOTAL", sum(int(u.get('p_act', 1)) for u in st.session_state.v_manifest if 'p_act' in u))
            m3.metric("GROSS MASS", f"{total_mass} KG")
            m4.metric("UTILIZATION", f"{(total_mass/veh['max_w'])*100:.1f}%")

            # CORE ENGINE CALCULATION
            rem_units = [dict(u) for u in st.session_state.v_manifest]
            fleet_assigned = []
            while rem_units:
                res_s, res_w, n_p, ldm_r = V28SupremeEngine.solve_mission(rem_units, veh, x_offset=st.session_state.x_offset)
                if not res_s: st.error("CRITICAL: UNIT OVERSIZE DETECTED."); break
                fleet_assigned.append({"stacks": res_s, "weight": res_w, "ldm": ldm_r})
                rem_units = n_p

            # RENDERING
            for idx, truck in enumerate(fleet_assigned):
                st.markdown(f'<div class="v-tile-apex">', unsafe_allow_html=True)
                st.markdown(f"### MISSION UNIT #{idx+1} | {v_key}")
                
                v_col, d_col = st.columns([2.8, 1])
                with v_col:
                    st.plotly_chart(render_vorteza_cad_3d(veh, truck['stacks']), use_container_width=True)
                    process_load_balancer(veh, truck['stacks'])
                with d_col:
                    st.markdown("**KPI DATA:**")
                    st.write(f"Zajęte LDM: **{truck['ldm']:.2f} m**")
                    st.write(f"Masa Netto: **{truck['weight']} kg**")
                    st.write(f"Zapas Masy: **{veh['max_w'] - truck['weight']} kg**")
                    st.divider()
                    st.markdown("**MANIFEST ZAŁADUNKOWY:**")
                    # Agregacja i poprawiony błąd KeyError
                    agg_df = pd.Series([it['name'] for s in truck['stacks'] for it in s['items']]).value_counts().reset_index()
                    agg_df.columns = ['SKU', 'QTY']
                    
                    html_table = '<table class="v-table-tactical"><tr><th>SKU</th><th>QTY</th></tr>'
                    for _, r in agg_df.iterrows():
                        c_h = get_vorteza_color(r['SKU'])
                        html_table += f'<tr><td><span style="color:{c_h}">■</span> {r["SKU"]}</td><td>{r["QTY"]}</td></tr>'
                    st.markdown(html_table + '</table>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.info("VORTEZA STACK: READY FOR MISSION DATA. INJECT MANIFEST VIA SIDEBAR.")

    with tab_i:
        st.markdown("### 📦 PRODUCT MASTER ARCHIVE")
        df_inv = pd.DataFrame(inventory)
        if not df_inv.empty:
            edt_session = st.data_editor(df_inv, use_container_width=True, num_rows="dynamic", key="v28_editor")
            if st.button("PUSH CHANGES TO CLOUD", type="primary"):
                db_save(edt_session.to_dict('records'))
                st.success("SYNC SUCCESSFUL")
        
        st.divider()
        with st.expander("➕ REGISTER NEW SKU"):
            with st.form("AddSKU"):
                fn = st.text_input("Name")
                c1, c2, c3 = st.columns(3)
                fl, fw, fh = c1.number_input("L", 120), c2.number_input("W", 80), c3.number_input("H", 100)
                fm, fi = st.number_input("Weight", 50), st.number_input("IPU", 1)
                ca1, ca2 = st.columns(2)
                fs, fr = ca1.checkbox("Stackable", True), ca2.checkbox("Rotatable", True)
                if st.form_submit_button("COMMIT"):
                    inventory.append({"name":fn,"length":fl,"width":fw,"height":fh,"weight":fm,"itemsPerCase":fi,"canStack":fs,"allowRotation":fr})
                    db_save(inventory); st.rerun()

    with tab_l:
        st.code(f"SYSTEM: VORTEZA STACK v28.0\nCORE: APEX-OMNI\nTIME: {datetime.now()}\nSTATUS: Nominal", language="bash")

if __name__ == "__main__":
    main()
