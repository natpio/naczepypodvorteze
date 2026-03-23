# -*- coding: utf-8 -*-
"""
================================================================================
SYSTEM: VORTEZA STACK 
VERSION: 22.0 | SUPREME EDITION
FIRM: VORTEZA SYSTEMS
STATUS: PRODUCTION READY | FULL SOURCE CODE
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
# 1. ARCHITEKTURA ŚRODOWISKA I DEFINICJE INŻYNIERYJNE
# ==============================================================================
st.set_page_config(
    page_title="VORTEZA STACK v22.0",
    layout="wide",
    initial_sidebar_state="expanded",
    page_icon="🕋"
)

# REJESTR FLOTY VORTEZA (PEŁNA SPECYFIKACJA TECHNICZNA)
FLEET_REGISTRY = {
    "TIR Mega 13.6m": {
        "max_w": 24000, "L": 1360, "W": 248, "H": 300, 
        "ldm_max": 13.6, "axles": 3, "wheelbase": 850, "tare": 14500, "cab_l": 220
    },
    "TIR Standard 13.6m": {
        "max_w": 24000, "L": 1360, "W": 248, "H": 275, 
        "ldm_max": 13.6, "axles": 3, "wheelbase": 850, "tare": 13800, "cab_l": 220
    },
    "Solo 9m Heavy": {
        "max_w": 9500, "L": 920, "W": 245, "H": 270, 
        "ldm_max": 9.2, "axles": 2, "wheelbase": 550, "tare": 8500, "cab_l": 200
    },
    "Solo 7m Medium": {
        "max_w": 7000, "L": 720, "W": 245, "H": 260, 
        "ldm_max": 7.2, "axles": 2, "wheelbase": 480, "tare": 6200, "cab_l": 180
    },
    "Express BUS XL": {
        "max_w": 1250, "L": 485, "W": 175, "H": 220, 
        "ldm_max": 4.8, "axles": 2, "wheelbase": 320, "tare": 2250, "cab_l": 140
    }
}

# ==============================================================================
# 2. BRANDING I SILNIK WIZUALNY (CSS/BASE64)
# ==============================================================================
def load_vorteza_b64(path):
    """Bezpieczne ładowanie zasobów binarnych do systemu UI."""
    try:
        if os.path.exists(path):
            with open(path, 'rb') as f:
                return base64.b64encode(f.read()).decode()
        return ""
    except: return ""

def apply_supreme_vorteza_ui():
    """Wstrzykuje rygorystyczną stylizację VORTEZA STACK."""
    bg_b64 = load_vorteza_b64('bg_vorteza.png')
    
    st.markdown(f"""
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;600;700&family=JetBrains+Mono:wght@300;400;500&display=swap');
            
            :root {{
                --v-copper: #B58863;
                --v-copper-glow: rgba(181, 136, 99, 0.4);
                --v-dark-obsidian: #040404;
                --v-panel-bg: rgba(10, 10, 10, 0.98);
                --v-border: rgba(181, 136, 99, 0.2);
                --v-neon: #00FF41;
            }}

            .stApp {{
                background-image: url("data:image/png;base64,{bg_b64}");
                background-size: cover;
                background-attachment: fixed;
                color: #FDFDFD;
                font-family: 'Montserrat', sans-serif;
            }}

            /* TILE DASHBOARD SYSTEM */
            .v-tile {{
                background: var(--v-panel-bg);
                padding: 2.5rem;
                border: 1px solid var(--v-border);
                border-left: 10px solid var(--v-copper);
                box-shadow: 0 40px 100px rgba(0,0,0,0.9);
                margin-bottom: 2rem;
                backdrop-filter: blur(50px);
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
                letter-spacing: 8px !important; 
                font-weight: 700 !important; 
                text-shadow: 3px 3px 20px rgba(0,0,0,0.8);
            }}

            [data-testid="stMetricValue"] {{ 
                color: var(--v-copper) !important; 
                font-family: 'JetBrains Mono', monospace !important; 
                font-size: 3.5rem !important;
            }}

            /* PRZYCISKI VORTEZA */
            .stButton > button {{
                background: linear-gradient(180deg, #0a0a0a, #151515);
                color: var(--v-copper);
                border: 1px solid var(--v-copper);
                padding: 1.5rem;
                text-transform: uppercase;
                letter-spacing: 6px;
                font-weight: 700;
                width: 100%;
                transition: 0.6s all cubic-bezier(0.19, 1, 0.22, 1);
                border-radius: 0;
            }}
            .stButton > button:hover {{
                background: var(--v-copper);
                color: black;
                box-shadow: 0 0 80px var(--v-copper-glow);
                transform: translateY(-3px);
            }}

            /* TABELE TACTICAL */
            .v-data-table {{ 
                width: 100%; 
                border-collapse: collapse; 
                margin-top: 30px; 
            }}
            .v-data-table th {{ 
                color: var(--v-copper); 
                text-align: left; 
                font-size: 0.75rem; 
                text-transform: uppercase; 
                border-bottom: 2px solid #333; 
                padding: 18px; 
                letter-spacing: 2px;
                background: rgba(0,0,0,0.5);
            }}
            .v-data-table td {{ 
                padding: 16px 18px; 
                border-bottom: 1px solid #1a1a1a; 
                color: #CCC; 
                font-size: 0.9rem; 
            }}
            .v-data-table tr:hover {{ background: rgba(181,136,99,0.05); }}

            /* ANALIZA BALANSU (CoG) */
            .v-rail {{
                width: 100%; height: 25px; background: #0a0a0a; border-radius: 12px; position: relative; border: 1px solid #333; margin: 40px 0;
            }}
            .v-marker {{
                position: absolute; width: 8px; height: 50px; top: -12.5px; background: #00FF41; box-shadow: 0 0 30px #00FF41; border-radius: 4px;
                transition: left 1s ease-in-out;
            }}
        </style>
    """, unsafe_allow_html=True)

# ==============================================================================
# 3. SYSTEM BEZPIECZEŃSTWA (AUTH GATEWAY)
# ==============================================================================
def authenticate_vorteza_stack():
    """Weryfikuje uprawnienia dostępu do terminala STACK."""
    if "authorized" not in st.session_state:
        st.session_state.authorized = False

    if not st.session_state.authorized:
        try:
            # Pobieranie hasła z Streamlit Secrets
            sys_key = str(st.secrets.get("password", "vorteza2026"))
        except:
            sys_key = "vorteza2026"

        st.markdown("<br><br><br><br><br><br>", unsafe_allow_html=True)
        _, col, _ = st.columns([1, 1.8, 1])
        with col:
            with st.form("VortezaAuthGate"):
                st.markdown("<h2 style='text-align:center;'>VORTEZA STACK</h2>", unsafe_allow_html=True)
                st.markdown("<p style='text-align:center; color:#444; font-size:0.75rem; letter-spacing:5px;'>SECURITY CLEARANCE REQUIRED</p>", unsafe_allow_html=True)
                pwd_in = st.text_input("GOLIATH MASTER AUTHENTICATION KEY", type="password")
                if st.form_submit_button("VALIDATE SECURITY CLEARANCE"):
                    if pwd_in == sys_key:
                        st.session_state.authorized = True
                        st.rerun()
                    else:
                        st.error("ACCESS DENIED: INVALID KEY")
        return False
    return True

# ==============================================================================
# 4. DATA PERSISTENCE (IO ENGINE)
# ==============================================================================
def db_load_inventory():
    """Wczytuje globalną bazę SKU VORTEZA."""
    if os.path.exists('products.json'):
        try:
            with open('products.json', 'r', encoding='utf-8') as f: return json.load(f)
        except: return []
    return []

def db_save_inventory(data):
    """Zapisuje zmiany w bazie SKU na stałe."""
    with open('products.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def get_chromatic_color(sku_name):
    """Generuje unikalny, metaliczny kolor dla każdego SKU."""
    palette = [
        "#B58863", "#D4AF37", "#8E6A4D", "#5E4633", "#A67C52", 
        "#2C3E50", "#34495E", "#1A252F", "#16A085", "#27AE60",
        "#7F8C8D", "#95A5A6", "#BDC3C7", "#7E4A35", "#C0392B",
        "#D35400", "#F39C12", "#2980B9", "#8E44AD", "#3D3D3D"
    ]
    random.seed(sum(ord(c) for c in sku_name))
    return random.choice(palette)

# ==============================================================================
# 5. SUPREME PACKING ENGINE (V-ENGINE 22.0)
# ==============================================================================
class SupremeStackEngine:
    """Silnik optymalizacji 3D z pełną kontrolą parametrów technicznych."""
    
    @staticmethod
    def execute_packing(cargo, veh, x_offset=0):
        # Priorytety FFD: 1. Non-stackable, 2. Non-rotatable, 3. Base Area (L*W)
        sorted_cargo = sorted(cargo, 
                             key=lambda x: (not x.get('canStack', True), 
                                            not x.get('allowRotation', True), 
                                            x['width']*x['length']), 
                             reverse=True)
        
        placed_stacks = []
        failed_units = []
        weight_accumulator = 0
        cx, cy, current_row_max_w = x_offset, 0, 0

        for unit in sorted_cargo:
            # Weryfikacja payloadu
            if weight_accumulator + unit['weight'] > veh['max_w']:
                failed_units.append(unit); continue
            
            # FAZA 1: PIĘTROWANIE (Vertical Stacking)
            integrated = False
            if unit.get('canStack', True):
                for s in placed_stacks:
                    # Sprawdzenie czy produkt na górę pasuje wymiarowo (z uwzględnieniem jego pozwoleń)
                    if unit.get('allowRotation', True):
                        dim_match = (unit['width'] <= s['w'] and unit['length'] <= s['l']) or \
                                  (unit['length'] <= s['w'] and unit['width'] <= s['l'])
                    else:
                        dim_match = (unit['width'] <= s['w'] and unit['length'] <= s['l'])
                    
                    if dim_match and (s['curH'] + unit['height'] <= veh['H']):
                        u_copy = unit.copy()
                        u_copy['z'] = s['curH']
                        u_copy['w_fit'], u_copy['l_fit'] = s['w'], s['l']
                        s['items'].append(u_copy)
                        s['curH'] += unit['height']
                        weight_accumulator += unit['weight']
                        integrated = True; break
            
            if integrated: continue

            # FAZA 2: PODŁOGA (Floor placement + V-PERMIT ROTATION)
            placed_on_floor = False
            orientations = [(unit['width'], unit['length']), (unit['length'], unit['width'])] if unit.get('allowRotation', True) else [(unit['width'], unit['length'])]
            
            for fw, fl in orientations:
                # Szukanie miejsca w rzędzie (oś Y)
                if cy + fl <= veh['W'] and cx + fw <= veh['L']:
                    u_c = unit.copy(); u_c['z'] = 0; u_c['w_fit'], u_c['l_fit'] = fw, fl
                    placed_stacks.append({'x':cx, 'y':cy, 'w':fw, 'l':fl, 'curH':unit['height'], 'items':[u_c]})
                    cy += fl; current_row_max_w = max(current_row_max_w, fw)
                    weight_accumulator += unit['weight']; placed_on_floor = True; break
                # Przeskok do nowego rzędu (oś X)
                elif cx + current_row_max_w + fw <= veh['L'] and fl <= veh['W']:
                    cx += current_row_max_w; cy = 0; current_row_max_w = fw
                    u_c = unit.copy(); u_c['z'] = 0; u_c['w_fit'], u_c['l_fit'] = fw, fl
                    placed_stacks.append({'x':cx, 'y':cy, 'w':fw, 'l':fl, 'curH':unit['height'], 'items':[u_c]})
                    cy += fl; weight_accumulator += unit['weight']; placed_on_floor = True; break
            
            if not placed_on_floor: failed_units.append(unit)
        
        # Kalkulacja realnego wykorzystania LDM
        ldm_real = (max([s['x'] + s['w'] for s in placed_stacks]) / 100) if placed_stacks else 0
        return placed_stacks, weight_accumulator, failed_units, ldm_real

# ==============================================================================
# 6. RENDERER CAD-3D SUPREME (INŻYNIERYJNY MODEL)
# ==============================================================================
def render_vorteza_supreme_3d(veh_data, cargo_stacks):
    """Generuje hiper-detaliczny model CAD 3D zestawu transportowego."""
    fig = go.Figure()
    L, W, H = veh_data['L'], veh_data['W'], veh_data['H']

    # --- INFRASTRUKTURA POJAZDU ---
    # Podłoga naczepy
    fig.add_trace(go.Mesh3d(x=[0, L, L, 0], y=[0, 0, W, W], z=[-15, -15, -15, -15], color='#121212', opacity=1, hoverinfo='skip'))
    
    # Inżynieria kół i osi
    axles = veh_data.get('axles', 3)
    ax_dist = 145
    rear_start = L - 400 if L > 800 else L - 180
    for i in range(axles):
        ax_x = rear_start + (i * ax_dist)
        if ax_x < L:
            for side in [-38, W+22]:
                # Opona
                fig.add_trace(go.Mesh3d(
                    x=[ax_x-55, ax_x+55, ax_x+55, ax_x-55], y=[side, side, side+18, side+18], 
                    z=[-75, -75, -15, -15], color='#000000', opacity=1, hoverinfo='skip'
                ))
                # Felga miedziana VORTEZA
                fig.add_trace(go.Mesh3d(
                    x=[ax_x-22, ax_x+22, ax_x+22, ax_x-22], y=[side-2, side-2, side, side], 
                    z=[-50, -50, -35, -35], color='#B58863', opacity=0.9, hoverinfo='skip'
                ))

    # Kabina Commander (Solid Render)
    cab_l = veh_data.get('cab_l', 220)
    fig.add_trace(go.Mesh3d(
        x=[-cab_l, 0, 0, -cab_l, -cab_l, 0, 0, -cab_l],
        y=[-45, -45, W+45, W+45, -45, -45, W+45, W+45],
        z=[0, 0, 0, 0, H*1.05, H*1.05, H*1.05, H*1.05],
        i=[7,0,0,0,4,4,6,6,4,0,3,2], j=[3,4,1,2,5,6,5,2,0,1,6,3], k=[0,7,2,3,6,7,1,1,5,5,7,6],
        color='#020202', opacity=1, name="UNIT_COMMAND_CAB"
    ))

    # Szkielet Paki (Copper Skeleton)
    cage = [
        ([0, L], [0, 0], [0, 0]), ([0, L], [W, W], [0, 0]), ([0, 0], [0, W], [0, 0]), ([L, L], [0, W], [0, 0]),
        ([0, 0], [0, 0], [0, H]), ([0, 0], [W, W], [0, H]), ([0, L], [0, 0], [H, H]), ([0, L], [W, W], [H, H]),
        ([L, L], [0, 0], [0, H]), ([L, L], [W, W], [0, H])
    ]
    for px, py, pz in cage:
        fig.add_trace(go.Scatter3d(x=px, y=py, z=pz, mode='lines', line=dict(color='#B58863', width=12), hoverinfo='skip'))

    # --- RENDER ŁADUNKU ---
    for stack in cargo_stacks:
        for it in stack['items']:
            x, y, z = stack['x'], stack['y'], it['z']
            dx, dy, dz = it['w_fit'], it['l_fit'], it['height']
            p_clr = get_chromatic_color(it['name'])
            
            # Bryła 3D
            fig.add_trace(go.Mesh3d(
                x=[x,x+dx,x+dx,x,x,x+dx,x+dx,x], y=[y,y,y+dy,y+dy,y,y,y+dy,y+dy], 
                z=[z,z,z+dz,z+dz,z,z,z+dz,z+dz],
                i=[7,0,0,0,4,4,6,6,4,0,3,2], j=[3,4,1,2,5,6,5,2,0,1,6,3], k=[0,7,2,3,6,7,1,1,5,5,7,6],
                color=p_clr, opacity=0.98, name=it['name']
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
            camera=dict(eye=dict(x=2.5, y=2.5, z=2.2)), bgcolor='rgba(0,0,0,0)'
        ),
        paper_bgcolor='rgba(0,0,0,0)', margin=dict(l=0, r=0, b=0, t=0), showlegend=False
    )
    return fig

# ==============================================================================
# 7. ANALITYKA TACTICAL (LOAD BALANCER & CoG)
# ==============================================================================
def render_tactical_bal_analysis(veh, stacks):
    """Wykonuje obliczenia fizyczne środka ciężkości ładunku."""
    if not stacks: return
    
    total_moment = 0
    total_weight = 0
    
    for s in stacks:
        for it in s['items']:
            cx_item = s['x'] + (it['w_fit'] / 2)
            total_moment += (cx_item * it['weight'])
            total_weight += it['weight']
    
    cog_x = total_moment / total_weight if total_weight > 0 else 0
    cog_pct = (cog_x / veh['L']) * 100
    
    st.markdown("### ⚖️ TACTICAL LOAD BALANCE (CoG)")
    st.write(f"Pozycja środka ciężkości: **{cog_x/100:.2f} m** od kabiny")
    
    # Kolor marker'a zależny od bezpieczeństwa
    m_clr = "#00FF41" if 35 < cog_pct < 65 else "#FF3131"
    
    st.markdown(f"""
        <div class="v-rail">
            <div class="v-marker" style="left: {cog_pct}%;"></div>
            <div style="position:absolute; left:15px; top:40px; font-size:0.6rem; color:#888;">CABIN AXLES</div>
            <div style="position:absolute; right:15px; top:40px; font-size:0.6rem; color:#888;">REAR AXLES</div>
        </div>
        <br>
    """, unsafe_allow_html=True)
    
    if cog_pct < 35:
        st.warning("OSTRZEŻENIE: PRZECIĄŻENIE OSI PRZEDNICH. Użyj suwaka OFFSET, aby przesunąć masę na tył.")
    elif cog_pct > 65:
        st.warning("OSTRZEŻENIE: ODCIĄŻENIE OSI STERUJĄCEJ. Przesuń towar bliżej kabiny.")
    else:
        st.success("STATUS NOMINALNY: Rozkład masy optymalny.")

# ==============================================================================
# 8. ARCHITEKTURA INTERFEJSU (MAIN COCKPIT)
# ==============================================================================
def main():
    apply_supreme_vorteza_ui()
    if not authenticate_vorteza_stack(): return

    # Stan sesji (Manifest + Baza)
    if 'v_manifest' not in st.session_state: st.session_state.v_manifest = []
    inventory = db_load_inventory()

    # --- TOP CONTROL BAR ---
    hc1, hc2, hc3 = st.columns([1, 4, 1])
    with hc1:
        logo_b64 = load_vorteza_b64('logo_vorteza.png')
        if logo_b64: st.markdown(f'<img src="data:image/png;base64,{logo_b64}" width="180">', unsafe_allow_html=True)
        else: st.markdown("### VORTEZA")
    with hc2:
        st.markdown("<h1>VORTEZA STACK</h1>", unsafe_allow_html=True)
        st.markdown(f"<p style='color:#444; letter-spacing:5px; font-size:0.75rem; font-weight:600;'>SUPREME LOGISTICS ARCHITECTURE v22.0 | {datetime.now().strftime('%H:%M')}</p>", unsafe_allow_html=True)
    with hc3:
        if st.button("TERMINATE"):
            st.session_state.authorized = False; st.rerun()

    # --- SIDEBAR: MISSION CONTROL ---
    with st.sidebar:
        st.markdown("### 📡 FLEET CONSOLE")
        v_sel = st.selectbox("POJAZD DOCELOWY", list(FLEET_REGISTRY.keys()))
        veh = FLEET_REGISTRY[v_sel]
        
        st.divider()
        st.markdown("### ⚖️ DYNAMIC POSITIONING")
        x_shift = st.slider("OFFSET OD ŚCIANY (cm)", 0, veh['L']-200, 0)
        st.caption("Ustaw dystans od przedniej ściany, aby skorygować CoG.")
        
        st.divider()
        st.markdown("### 📥 MANIFEST CONTROL")
        p_names = [p['name'] for p in inventory]
        sel_sku = st.selectbox("BROWSE SKU", p_names, index=None)
        
        if sel_sku:
            p_ref = next(p for p in inventory if p['name'] == sel_sku)
            ipc = p_ref.get('itemsPerCase', 1)
            rot = p_ref.get('allowRotation', True)
            st.markdown(f"""
                <div style='background:rgba(181,136,99,0.1); border:1px solid var(--v-copper); padding:18px; font-size:0.75rem;'>
                    SKU: {sel_sku}<br>STANDARD: {ipc} PCS/CASE<br>
                    OBRÓT: {'<span style="color:#00FF41">AUTHORIZED</span>' if rot else '<span style="color:#FF3131">LOCKED</span>'}
                </div>
            """, unsafe_allow_html=True)
            p_qty = st.number_input("QUANTITY (PCS)", min_value=1, value=ipc)
            n_units = math.ceil(p_qty / ipc)
            if st.button("APPEND TO MANIFEST", type="primary"):
                for i in range(n_units):
                    u = p_ref.copy()
                    u['p_act'] = ipc if (i < n_units - 1 or p_qty % ipc == 0) else (p_qty % ipc)
                    st.session_state.v_manifest.append(u)
                st.rerun()
        if st.button("PURGE MANIFEST"):
            st.session_state.v_manifest = []; st.rerun()

    # --- WORKSPACE TABS ---
    tab_p, tab_i, tab_l = st.tabs(["📊 STACK PLANNER", "📦 MASTER INVENTORY", "⚙️ SYSTEM LOGS"])

    # TAB 1: PLANNER & BALANCER
    with tab_p:
        if st.session_state.v_manifest:
            # DASHBOARD KPI
            m1, m2, m3, m4 = st.columns(4)
            total_kg = sum(float(u['weight']) for u in st.session_state.v_manifest)
            m1.metric("CASES", len(st.session_state.v_manifest))
            m2.metric("PCS TOTAL", sum(int(u.get('p_act', 1)) for u in st.session_state.v_manifest))
            m3.metric("GROSS MASS", f"{total_kg} KG")
            m4.metric("UTILIZATION", f"{(total_kg/veh['max_w'])*100:.1f}%")

            # CORE ENGINE RUN
            rem = [dict(u) for u in st.session_state.v_manifest]
            fleet = []
            while rem:
                res_s, res_w, n_p, ldm_r = SupremeStackEngine.execute_packing(rem, veh, x_offset=x_shift)
                if not res_s: st.error("CRITICAL: UNIT OVERSIZE DETECTED"); break
                fleet.append({"stacks": res_s, "weight": res_w, "ldm": ldm_r})
                rem = n_p

            # RENDERING
            for idx, truck in enumerate(fleet):
                st.markdown(f'<div class="v-tile">', unsafe_allow_html=True)
                st.markdown(f"### MISSION UNIT #{idx+1} | {v_sel}")
                
                v_col, d_col = st.columns([2.8, 1])
                with v_col:
                    st.plotly_chart(render_vorteza_supreme_3d(veh, truck['stacks']), use_container_width=True)
                    render_tactical_bal_analysis(veh, truck['stacks'])
                with d_col:
                    st.markdown("**OPERATIONAL KPI**")
                    st.write(f"Zajęte LDM: **{truck['ldm']:.2f} m**")
                    st.write(f"Masa Netto: **{truck['weight']} kg**")
                    st.divider()
                    st.markdown("**PACKING MANIFEST**")
                    agg = pd.Series([it['name'] for s in truck['stacks'] for it in s['items']]).value_counts().reset_index()
                    agg.columns = ['SKU', 'QTY']
                    h_table = '<table class="v-data-table"><tr><th>SKU</th><th>QTY</th></tr>'
                    for _, r in agg.iterrows():
                        c = get_chromatic_color(r['SKU'])
                        h_table += f'<tr><td><span style="color:{c}">■</span> {r["SKU"]}</td><td>{r["QTY"]}</td></tr>'
                    st.markdown(h_table + '</table>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.info("VORTEZA STACK: WAITING FOR MISSION DATA...")

    # TAB 2: INVENTORY (CRUD)
    with tab_i:
        st.markdown("### 📦 PRODUCT MASTER ARCHIVE")
        with st.expander("➕ REGISTER NEW SKU TO ARCHIVE"):
            with st.form("AddP"):
                fn = st.text_input("Product Name / SKU")
                c1, c2, c3 = st.columns(3)
                fl, fw, fh = c1.number_input("L (cm)", 120), c2.number_input("W (cm)", 80), c3.number_input("H (cm)", 100)
                col_w, col_i = st.columns(2)
                fm = col_w.number_input("Mass (kg)", 50)
                fi = col_i.number_input("Items Per Case (IPC)", 1)
                ca1, ca2 = st.columns(2)
                fs, fr = ca1.checkbox("Stacking Permission", True), ca2.checkbox("Rotation Permission", True)
                if st.form_submit_button("COMMIT TO CORE"):
                    inventory.append({"name":fn,"length":fl,"width":fw,"height":fh,"weight":fm,"itemsPerCase":fi,"canStack":fs,"allowRotation":fr})
                    db_save_inventory(inventory); st.success("CORE DATABASE SYNCHRONIZED"); st.rerun()
        
        st.divider()
        if inventory:
            df_i = pd.DataFrame(inventory)
            edt = st.data_editor(df_i, use_container_width=True, num_rows="dynamic", key="supreme_editor")
            if st.button("PUSH CHANGES TO CLOUD", type="primary"):
                db_save_inventory(edt.to_dict('records'))
                st.success("SYNC COMPLETE")

    # TAB 3: SYSTEM LOGS
    with tab_l:
        st.code(f"VORTEZA STACK SUPREME v22.0\nSYSTEM: CORE_ARCHITECT\nTIME: {datetime.now()}\nSTATUS: Nominal", language="bash")

if __name__ == "__main__":
    main()
