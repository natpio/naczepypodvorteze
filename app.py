# -*- coding: utf-8 -*-
"""
================================================================================
VORTEZA PRIME | IMPERATOR EDITION v11.0
SYSTEM OPERACYJNY LOGISTYKI 3D I ZARZĄDZANIA FLOTĄ
================================================================================
KOD CHRONIONY PROTOKOŁEM VORTEZA SYSTEMS 2026
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
import time
import os

# ==============================================================================
# 1. KRYTYCZNA KONFIGURACJA ŚRODOWISKA
# ==============================================================================
st.set_page_config(
    page_title="VORTEZA PRIME | IMPERATOR v11.0",
    layout="wide",
    initial_sidebar_state="expanded",
    page_icon="🕋"
)

# REJESTR FLOTY IMPERATOR (Dane techniczne, inżynieryjne i finansowe)
FLEET_MASTER_DATA = {
    "TIR FTL (Mega High-Cube)": {
        "max_w": 24000, "L": 1360, "W": 248, "H": 300, 
        "ldm_max": 13.6, "fuel_avg": 0.32, "myto_eur": 0.22, "tank": 1200,
        "axles": 3, "wheelbase": 800, "tare_weight": 14000,
        "desc": "Naczepa o podwyższonej kubaturze do transportu objętościowego."
    },
    "TIR FTL (Standard Curtain)": {
        "max_w": 24000, "L": 1360, "W": 248, "H": 275, 
        "ldm_max": 13.6, "fuel_avg": 0.28, "myto_eur": 0.20, "tank": 1000,
        "axles": 3, "wheelbase": 800, "tare_weight": 13500,
        "desc": "Standardowa naczepa typu firanka (curtain-side)."
    },
    "Solo 9m (Heavy Logistics)": {
        "max_w": 9500, "L": 920, "W": 245, "H": 270, 
        "ldm_max": 9.2, "fuel_avg": 0.24, "myto_eur": 0.18, "tank": 500,
        "axles": 2, "wheelbase": 550, "tare_weight": 8500,
        "desc": "Ciężkie podwozie do dystrybucji regionalnej i krajowej."
    },
    "Solo 7m (Medium Distribution)": {
        "max_w": 7000, "L": 720, "W": 245, "H": 260, 
        "ldm_max": 7.2, "fuel_avg": 0.20, "myto_eur": 0.15, "tank": 400,
        "axles": 2, "wheelbase": 480, "tare_weight": 6000,
        "desc": "Zwrotne podwozie dystrybucyjne o średniej ładowności."
    },
    "BUS XL (Express Courier)": {
        "max_w": 1200, "L": 485, "W": 175, "H": 220, 
        "ldm_max": 4.8, "fuel_avg": 0.11, "myto_eur": 0.00, "tank": 90,
        "axles": 2, "wheelbase": 380, "tare_weight": 2300,
        "desc": "Pojazd dostawczy do transportu ekspresowego i dedykowanego."
    }
}

# ==============================================================================
# 2. VORTEZA PRIME DESIGN LANGUAGE (ADVANCED SCSS-LIKE CSS)
# ==============================================================================
def apply_prime_imperator_styling():
    """Wstrzykuje zaawansowany arkusz stylów marki VORTEZA PRIME."""
    st.markdown("""
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;600;700&family=JetBrains+Mono:wght@300;400;500&display=swap');
            
            :root {
                --v-copper: #B58863;
                --v-gold: #D4AF37;
                --v-dark-black: #030303;
                --v-panel-bg: rgba(14, 14, 14, 0.99);
                --v-border: rgba(181, 136, 99, 0.2);
                --v-success: #00FF41;
                --v-warning: #FFCC00;
                --v-danger: #FF3131;
            }

            /* Global App Architecture */
            .stApp { background-color: var(--v-dark-black); color: #F8F8F8; font-family: 'Montserrat', sans-serif; }
            
            /* Sidebar Navigation - Imperator Layout */
            section[data-testid="stSidebar"] {
                background-color: #060606 !important;
                border-right: 1px solid var(--v-border);
                width: 460px !important;
            }

            /* Containers & Tactical Cards */
            .v-prime-card {
                background: var(--v-panel-bg);
                padding: 2.8rem;
                border-radius: 2px;
                border: 1px solid var(--v-border);
                border-left: 12px solid var(--v-copper);
                box-shadow: 0 50px 120px rgba(0,0,0,1);
                margin-bottom: 3.5rem;
                backdrop-filter: blur(40px);
                transition: transform 0.3s ease;
            }
            .v-prime-card:hover { border-color: var(--v-copper); }

            /* Typography protocols */
            h1, h2, h3 { 
                color: var(--v-copper) !important; 
                text-transform: uppercase; 
                letter-spacing: 10px !important; 
                font-weight: 700 !important; 
                text-shadow: 0 0 20px rgba(181, 136, 99, 0.2);
            }
            .v-status-line { color: #555; font-size: 0.75rem; letter-spacing: 5px; text-transform: uppercase; font-weight: 500; }

            /* Data Visualization / Metrics */
            [data-testid="stMetricValue"] { 
                color: var(--v-copper) !important; 
                font-family: 'JetBrains Mono', monospace !important; 
                font-size: 3.5rem !important;
                font-weight: 300 !important;
            }
            [data-testid="stMetricLabel"] { color: #888; text-transform: uppercase; letter-spacing: 2px; font-weight: 600; }

            /* Interactive Controllers (Buttons) */
            .stButton > button {
                background: linear-gradient(145deg, #0a0a0a, #151515);
                color: var(--v-copper);
                border: 1px solid var(--v-copper);
                padding: 1.4rem 2.5rem;
                text-transform: uppercase;
                letter-spacing: 6px;
                font-weight: 700;
                width: 100%;
                transition: 0.6s all cubic-bezier(0.19, 1, 0.22, 1);
                border-radius: 0;
            }
            .stButton > button:hover {
                background: var(--v-copper);
                color: black;
                box-shadow: 0 0 80px rgba(181, 136, 99, 0.8);
                transform: translateY(-4px);
            }

            /* Tactical Data Tables */
            .v-tactical-table { width: 100%; border-collapse: collapse; margin-top: 35px; border: 1px solid #1a1a1a; }
            .v-tactical-table th { background: #0a0a0a; color: var(--v-copper); text-align: left; font-size: 0.75rem; text-transform: uppercase; border-bottom: 2px solid #333; padding: 22px; letter-spacing: 2px; }
            .v-tactical-table td { padding: 18px 22px; border-bottom: 1px solid #111; font-size: 0.9rem; color: #BBB; }
            .v-tactical-table tr:hover { background: rgba(181,136,99,0.03); }

            /* Unit Tags */
            .v-tag {
                background: rgba(181,136,99,0.08);
                border: 1px solid var(--v-copper);
                padding: 15px;
                font-size: 0.85rem;
                color: var(--v-copper);
                margin: 15px 0;
                font-family: 'JetBrains Mono', monospace;
            }

            /* Terminal View Protocols */
            .v-terminal-output {
                background: #000;
                color: #00FF41;
                font-family: 'JetBrains Mono', monospace;
                padding: 20px;
                border: 1px solid #222;
                font-size: 0.8rem;
                max-height: 350px;
                overflow-y: auto;
                box-shadow: inset 0 0 20px rgba(0,255,65,0.1);
            }
        </style>
    """, unsafe_allow_html=True)

# ==============================================================================
# 3. KONTROLA BEZPIECZEŃSTWA (IMPERATOR SECURITY PROTOCOL)
# ==============================================================================
def verify_system_access():
    """Zarządza autoryzacją dostępu do platformy Imperator."""
    if "authorized" not in st.session_state:
        st.session_state.authorized = False

    if not st.session_state.authorized:
        try:
            # Hasło z Secrets Streamlit
            master_key = str(st.secrets.get("password", "vorteza2026"))
        except:
            master_key = "vorteza2026"

        st.markdown("<br><br><br><br><br>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            with st.form("ImperatorAuth"):
                st.markdown("<h2 style='text-align:center;'>VORTEZA PRIME LOGIN</h2>", unsafe_allow_html=True)
                st.markdown("<p style='text-align:center; color:#555; font-size:0.8rem; letter-spacing:4px;'>RESTRICTED ACCESS AREA</p>", unsafe_allow_html=True)
                key_in = st.text_input("GOLIATH MASTER PROTOCOL KEY", type="password", placeholder="Wprowadź kod")
                if st.form_submit_button("VALIDATE KEY"):
                    if key_in == master_key:
                        st.session_state.authorized = True
                        st.rerun()
                    else:
                        st.error("VALIDATION FAILED: UNAUTHORIZED ACCESS")
        return False
    return True

# ==============================================================================
# 4. CHROMATIC CORE (PRODUCT COLOR INTELLIGENCE)
# ==============================================================================
def get_imperator_color(name):
    """Zwraca unikalny kolor dla produktu, zapewniając spójność wizualną."""
    # Definicja sztywnej palety barw sequential do analityki (fix AttributeError)
    palette_list = [
        "#B58863", "#D4AF37", "#8E6A4D", "#5E4633", "#A67C52", 
        "#34495E", "#2C3E50", "#1A252F", "#4A4A4A", "#2F2F2F",
        "#7F8C8D", "#95A5A6", "#BDC3C7", "#27AE60", "#2980B9",
        "#8E44AD", "#C0392B", "#D35400", "#F39C12", "#16A085",
        "#F1C40F", "#E67E22", "#E74C3C", "#9B59B6", "#1ABC9C"
    ]
    # Deterministyczne ziarno oparte na nazwie
    random.seed(sum(ord(c) for c in name))
    return random.choice(palette_list)

# ==============================================================================
# 5. RENDERER CAD-3D IMPERATOR (ENGINE v11.0)
# ==============================================================================
def render_imperator_3d(vehicle_data, cargo_stacks):
    """Generuje kompletny techniczny model 3D pojazdu wraz z ładunkiem."""
    fig = go.Figure()
    L, W, H = vehicle_data['L'], vehicle_data['W'], vehicle_data['H']

    # --- INFRASTRUKTURA POJAZDU (DETALE INŻYNIERYJNE) ---
    # Podłoga Naczepy (Fundament stalowy)
    fig.add_trace(go.Mesh3d(
        x=[0, L, L, 0], y=[0, 0, W, W], z=[-8, -8, -8, -8],
        color='#181818', opacity=1, hoverinfo='skip'
    ))
    
    # Koła i Osie (Dynamiczny render CAD)
    num_axles = vehicle_data.get('axles', 3)
    axle_spacing = 130
    start_pos = L - 300 if L > 500 else L - 150
    
    for i in range(num_axles):
        curr_x = start_pos + (i * axle_spacing)
        if curr_x < L:
            for side in [-25, W+15]:
                fig.add_trace(go.Mesh3d(
                    x=[curr_x-45, curr_x+45, curr_x+45, curr_x-45], 
                    y=[side, side, side+10, side+10], 
                    z=[-55, -55, -8, -8], color='#000000', opacity=1, hoverinfo='skip'
                ))

    # Kabina Kierowcy (Goliath Command Center)
    cab_l = 180
    fig.add_trace(go.Mesh3d(
        x=[-cab_l, 0, 0, -cab_l, -cab_l, 0, 0, -cab_l],
        y=[-20, -20, W+20, W+20, -20, -20, W+20, W+20],
        z=[0, 0, 0, 0, H*0.98, H*0.98, H*0.98, H*0.98],
        i=[7,0,0,0,4,4,6,6,4,0,3,2], j=[3,4,1,2,5,6,5,2,0,1,6,3], k=[0,7,2,3,6,7,1,1,5,5,7,6],
        color='#040404', opacity=1, name="CORE_COMMAND_CAB"
    ))

    # Klatka Naczepy (Miedziany szkielet konstrukcyjny)
    cage_points = [
        ([0, L], [0, 0], [0, 0]), ([0, L], [W, W], [0, 0]),
        ([0, 0], [0, W], [0, 0]), ([L, L], [0, W], [0, 0]),
        ([0, 0], [0, 0], [0, H]), ([0, 0], [W, W], [0, H]),
        ([0, L], [0, 0], [H, H]), ([0, L], [W, W], [H, H]),
        ([L, L], [0, 0], [0, H]), ([L, L], [W, W], [0, H])
    ]
    for px, py, pz in cage_points:
        fig.add_trace(go.Scatter3d(x=px, y=py, z=pz, mode='lines', line=dict(color='#B58863', width=8), hoverinfo='skip'))

    # --- RENDER ŁADUNKU (DYNAMIC CHROMATIC MAPPING) ---
    for stack in cargo_stacks:
        for item in stack['items']:
            x, y, z = stack['x'], stack['y'], item['z']
            dx, dy, dz = item['w_fit'], item['l_fit'], item['height']
            
            p_color = get_imperator_color(item['name'])
            
            # Bryła produktu 3D
            fig.add_trace(go.Mesh3d(
                x=[x,x+dx,x+dx,x,x,x+dx,x+dx,x], y=[y,y,y+dy,y+dy,y,y,y+dy,y+dy], 
                z=[z,z,z,z,z+dz,z+dz,z+dz,z+dz],
                i=[7,0,0,0,4,4,6,6,4,0,3,2], j=[3,4,1,2,5,6,5,2,0,1,6,3], k=[0,7,2,3,6,7,1,1,5,5,7,6],
                color=p_color, opacity=0.98, name=item['name'],
                hovertemplate=f"<b>{item['name']}</b><br>D: {dx}cm W: {dy}cm H: {dz}cm<br>WAGA: {item['weight']}kg<extra></extra>"
            ))
            # Kontur Separacji (Edge Highlights)
            fig.add_trace(go.Scatter3d(
                x=[x,x+dx,x+dx,x,x,x+dx,x+dx,x,x,x+dx,x+dx,x+dx,x+dx,x,x],
                y=[y,y,y+dy,y+dy,y,y,y,y+dy,y+dy,y+dy,y+dy,y,y,y+dy,y+dy,y],
                z=[z,z,z,z,z,z+dz,z+dz,z,z,z+dz,z+dz,z+dz,z,z,z+dz,z+dz],
                mode='lines', line=dict(color='black', width=2), hoverinfo='skip'
            ))

    fig.update_layout(
        scene=dict(
            aspectmode='data', xaxis_visible=False, yaxis_visible=False, zaxis_visible=False,
            camera=dict(eye=dict(x=2.0, y=2.0, z=1.4)), bgcolor='rgba(0,0,0,0)'
        ),
        paper_bgcolor='rgba(0,0,0,0)', margin=dict(l=0, r=0, b=0, t=0), showlegend=False
    )
    return fig

# ==============================================================================
# 6. MASTER PACKING ENGINE (V-ENGINE 11.0 IMPERATOR)
# ==============================================================================
class ImperatorEngine:
    """Zaawansowany algorytm optymalizacji załadunku z analizą wektorową."""
    
    @staticmethod
    def execute(cargo, vehicle):
        # Sortowanie: 1. Non-stackable (Foundation), 2. Powierzchnia podstawy (L*W)
        sorted_cargo = sorted(cargo, key=lambda x: (not x.get('canStack', True), x['width']*x['length']), reverse=True)
        
        stacks, failed, weight_accumulator = [], [], 0
        cx, cy, current_row_max_w = 0, 0, 0

        for it in sorted_cargo:
            # Walidacja masy dopuszczalnej
            if weight_accumulator + it['weight'] > vehicle['max_w']:
                failed.append(it); continue
            
            # Faza 1: Piętrowanie (Vertical Stacking)
            stacked = False
            if it.get('canStack', True):
                for s in stacks:
                    # Dopasowanie z rotacją 90 st.
                    dim_match = (it['width'] <= s['w'] and it['length'] <= s['l']) or \
                                (it['length'] <= s['w'] and it['width'] <= s['l'])
                    
                    if dim_match and (s['curH'] + it['height'] <= vehicle['H']):
                        it_c = it.copy(); it_c['z'] = s['curH']
                        it_c['w_fit'], it_c['l_fit'] = s['w'], s['l']
                        s['items'].append(it_c); s['curH'] += it['height']
                        weight_accumulator += it['weight']; stacked = True; break
            
            if stacked: continue

            # Faza 2: Położenie na podłodze (Floor Optimization)
            placed = False
            orientations = [(it['width'], it['length']), (it['length'], it['width'])]
            
            for fw, fl in orientations:
                if cy + fl <= vehicle['W'] and cx + fw <= vehicle['L']:
                    it_c = it.copy(); it_c['z'] = 0; it_c['w_fit'], it_c['l_fit'] = fw, fl
                    stacks.append({'x':cx, 'y':cy, 'w':fw, 'l':fl, 'curH':it['height'], 'items':[it_c]})
                    cy += fl; current_row_max_w = max(current_row_max_w, fw)
                    weight_accumulator += it['weight']; placed = True; break
                elif cx + current_row_max_w + fw <= vehicle['L'] and fl <= vehicle['W']:
                    cx += current_row_max_w; cy = 0; current_row_max_w = fw
                    it_c = it.copy(); it_c['z'] = 0; it_c['w_fit'], it_c['l_fit'] = fw, fl
                    stacks.append({'x':cx, 'y':cy, 'w':fw, 'l':fl, 'curH':it['height'], 'items':[it_c]})
                    cy += fl; weight_accumulator += it['weight']; placed = True; break
            
            if not placed: failed.append(it)
        
        # Kalkulacja LDM real-time
        ldm_real = (max([s['x'] + s['w'] for s in stacks]) / 100) if stacks else 0
        return stacks, weight_accumulator, failed, ldm_real

# ==============================================================================
# 7. ZARZĄDZANIE DANYMI I LOGOWANIE SYSTEMOWE
# ==============================================================================
def db_core_load():
    """Wczytuje globalny inwentarz produktów."""
    try:
        with open('products.json', 'r', encoding='utf-8') as f: return json.load(f)
    except: return []

def db_core_save(data):
    """Zapisuje zmiany w globalnym inwentarzu."""
    with open('products.json', 'w', encoding='utf-8') as f: 
        json.dump(data, f, indent=4, ensure_ascii=False)

def log_terminal_event(msg):
    """Rejestruje zdarzenia w terminalu sesji."""
    if 'imperator_logs' not in st.session_state: st.session_state.imperator_logs = []
    ts = datetime.now().strftime("%H:%M:%S")
    st.session_state.imperator_logs.append(f"[{ts}] PROT_ID_{random.randint(100,999)}: {msg}")

# ==============================================================================
# 8. ARCHITEKTURA INTERFEJSU (IMPERATOR COMMAND CENTER)
# ==============================================================================
def main():
    apply_prime_imperator_styling()
    
    if not verify_system_access(): return

    # Inicjalizacja Manifestu i Bazy Inwentarza
    if 'v_manifest' not in st.session_state: st.session_state.v_manifest = []
    inventory = db_core_load()

    # --- TOP CONTROL BAR ---
    h_col1, h_col2 = st.columns([6, 1])
    with h_col1:
        st.markdown("<h1>VORTEZA PRIME IMPERATOR</h1>", unsafe_allow_html=True)
        st.markdown(f"<p class='v-status-line'>LOGISTICS COMMAND CENTER v11.0.2 | {datetime.now().strftime('%Y-%m-%d %H:%M')}</p>", unsafe_allow_html=True)
    with h_col2:
        if st.button("TERMINATE PROTOCOL"):
            st.session_state.authorized = False; st.rerun()

    # --- SIDEBAR COMMAND MODULE ---
    with st.sidebar:
        st.markdown("### 📡 FLEET COMMAND")
        v_sel_key = st.selectbox("TRANSPORT UNIT SELECTOR", list(FLEET_MASTER_DATA.keys()))
        veh = FLEET_MASTER_DATA[v_sel_key]
        
        st.markdown(f"""<div class='v-tag'>
            MODEL: {v_sel_key}<br>
            LOADBOX: {veh['L']}x{veh['W']}x{veh['H']} CM<br>
            PAYLOAD: {veh['max_w']} KG<br>
            MAX LDM: {veh['ldm_max']}
        </div>""", unsafe_allow_html=True)
        
        st.divider()
        st.markdown("### 📥 MANIFEST INJECTION")
        p_titles = [p['name'] for p in inventory]
        sel_prod = st.selectbox("PRODUCT LOOKUP SERVICE", p_titles, index=None)
        
        if sel_prod:
            p_ref = next(p for p in inventory if p['name'] == sel_prod)
            ipc = p_ref.get('itemsPerCase', 1)
            st.markdown(f"<p style='color:var(--v-copper); font-size:0.8rem; font-weight:700;'>PACKAGING STANDARD: {ipc} PCS</p>", unsafe_allow_html=True)
            p_qty_total = st.number_input("QUANTITY TO SHIP (PCS)", min_value=1, value=ipc)
            num_units = math.ceil(p_qty_total / ipc)
            
            if st.button("APPEND TO MISSION MANIFEST", type="primary"):
                for i in range(num_units):
                    unit_entry = p_ref.copy()
                    unit_entry['actual_pcs'] = ipc if (i < num_units - 1 or p_qty_total % ipc == 0) else (p_qty_total % ipc)
                    st.session_state.v_manifest.append(unit_entry)
                log_terminal_event(f"Injected {num_units} units of {sel_prod}")
                st.toast(f"Synchronized: {num_units} units added to manifest.")

        if st.button("PURGE ALL MANIFEST DATA"):
            st.session_state.v_manifest = []; log_terminal_event("Global manifest purge executed."); st.rerun()

    # --- WORKSPACE TABS ARCHITECTURE ---
    tab_p, tab_i, tab_f, tab_l = st.tabs(["📊 TACTICAL PLANNER", "📦 MASTER INVENTORY", "💰 FINANCIAL INTEL", "⚙️ TERMINAL LOGS"])

    # --------------------------------------------------------------------------
    # TAB 1: TACTICAL PLANNER (OPTIMIZATION & 3D)
    # --------------------------------------------------------------------------
    with tab_p:
        if st.session_state.v_manifest:
            # Global Manifest KPI Dashboard
            kpi_col1, kpi_col2, kpi_col3, kpi_col4 = st.columns(4)
            t_weight = sum(float(u['weight']) for u in st.session_state.v_manifest)
            t_units = len(st.session_state.v_manifest)
            t_pcs = sum(int(u.get('actual_pcs', 1)) for u in st.session_state.v_manifest)
            
            kpi_col1.metric("TOTAL UNITS", t_units)
            kpi_col2.metric("TOTAL PIECES", t_pcs)
            kpi_col3.metric("GROSS MASS", f"{t_weight} KG")
            kpi_col4.metric("WEIGHT UTIL", f"{(t_weight/veh['max_w'])*100:.1f}%")

            # Execution logic for Fleet Assignment
            manifest_rem = [dict(u) for u in st.session_state.v_manifest]
            fleet_allocation = []
            
            while manifest_rem:
                st_res, w_res, rem_res, ldm_res = ImperatorEngine.execute(manifest_rem, veh)
                if not st_res:
                    st.error("LOGISTICS FAILURE: Item dimensions exceed fleet capability.")
                    break
                fleet_allocation.append({"stacks": st_res, "weight": w_res, "ldm": ldm_res})
                manifest_rem = rem_res

            st.markdown(f"### ASIGNED FLEET CAPACITY: {len(fleet_allocation)} POJAZD(Y)")
            
            # Rendering results per assigned vehicle
            for idx, truck in enumerate(fleet_allocation):
                st.markdown(f'<div class="v-prime-card">', unsafe_allow_html=True)
                st.markdown(f"### TRANSPORT UNIT #{idx+1} | {v_sel_key}", unsafe_allow_html=True)
                
                viz_c, dat_c = st.columns([2.2, 1])
                with viz_c:
                    st.plotly_chart(render_imperator_3d(veh, truck['stacks']), use_container_width=True)
                with dat_c:
                    st.markdown("**OPERATIONAL KPI**")
                    st.write(f"Utilized Weight: {truck['weight']} / {veh['max_w']} kg")
                    st.write(f"Utilized LDM: {truck['ldm']:.2f} m")
                    st.write(f"Mass Factor: {(truck['weight']/veh['max_w'])*100:.1f}%")
                    
                    st.divider()
                    st.markdown("**CARGO MANIFEST DETAILS**")
                    manifest_names = [it['name'] for s in truck['stacks'] for it in s['items']]
                    if manifest_names:
                        agg_df = pd.Series(manifest_names).value_counts().reset_index()
                        agg_df.columns = ['SKU', 'QTY']
                        
                        html_table = '<table class="v-tactical-table"><tr><th>SKU IDENTIFIER</th><th>UNIT QTY</th></tr>'
                        for _, r in agg_df.iterrows():
                            # Pobranie koloru z Color Engine dla spójności
                            c = get_imperator_color(r['SKU'])
                            html_table += f'<tr><td><span style="color:{c};">■</span> {r["SKU"]}</td><td>{r["QTY"]}</td></tr>'
                        st.markdown(html_table+'</table>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.info("PROTOCOL STATUS: WAITING FOR MANIFEST INJECTION...")

    # --------------------------------------------------------------------------
    # TAB 2: MASTER INVENTORY (CRUD MANAGEMENT)
    # --------------------------------------------------------------------------
    with tab_i:
        st.markdown("### 📦 PRODUCT ARCHITECTURE ADMINISTRATION")
        
        with st.expander("➕ REGISTER NEW ASSET SPECIFICATION"):
            with st.form("NewAssetForm"):
                f_name = st.text_input("Product SKU / Asset Name")
                c_i1, c_i2, c_i3 = st.columns(3)
                f_l = c_i1.number_input("Length (cm)", 120)
                f_w = c_i2.number_input("Width (cm)", 80)
                f_h = c_i3.number_input("Height (cm)", 100)
                c_i4, c_i5 = st.columns(2)
                f_mass = c_i4.number_input("Mass (kg)", 100)
                f_ipc = c_i5.number_input("Items Per Unit (IPC)", 1)
                f_stk = st.checkbox("Vertical Stacking Approved", value=True)
                
                if st.form_submit_button("COMMIT TO MASTER DATABASE"):
                    inventory.append({
                        "name": f_name, "length": f_l, "width": f_w, "height": f_h, 
                        "weight": f_mass, "itemsPerCase": f_ipc, "canStack": f_stk
                    })
                    db_core_save(inventory)
                    log_terminal_event(f"New asset registered: {f_name}")
                    st.success("PROTOCOL SUCCESS: Database synchronized."); st.rerun()

        st.divider()
        if inventory:
            st.markdown("**GLOBAL INVENTORY ARCHIVE**")
            df_display = pd.DataFrame(inventory)
            # Zaawansowany edytor danych
            edited_archive = st.data_editor(df_display, use_container_width=True, num_rows="dynamic", key="imperator_db_editor")
            if st.button("PUSH LOCAL CHANGES TO CLOUD"):
                db_core_save(edited_archive.to_dict('records'))
                log_terminal_event("Global inventory database manually synchronized.")
                st.success("DATABASE STATUS: SYNCHRONIZED SUCCESSFULLY.")
        else:
            st.warning("DATABASE STATUS: NO ASSETS DETECTED.")

    # --------------------------------------------------------------------------
    # TAB 3: FINANCIAL INTELLIGENCE & COSTS
    # --------------------------------------------------------------------------
    with tab_f:
        st.markdown("### 💰 MISSION COST SIMULATION")
        cf1, cf2 = st.columns(2)
        with cf1:
            st.markdown('<div class="v-prime-card">', unsafe_allow_html=True)
            dist_km = st.number_input("Route Distance (KM)", 10, 10000, 1500)
            fuel_p = st.number_input("Current Fuel Price (PLN/L)", 4.0, 12.0, 6.45)
            euro_val = st.number_input("Exchange Rate (EUR/PLN)", 4.0, 5.0, 4.32)
            st.markdown('</div>', unsafe_allow_html=True)
        with cf2:
            st.markdown('<div class="v-prime-card">', unsafe_allow_html=True)
            # Financial Algorithms
            f_consumption = dist_km * veh['fuel_avg']
            f_cost = f_consumption * fuel_p
            toll_cost = dist_km * veh['myto_eur'] * euro_val
            maintenance = dist_km * 0.15 # 0.15 PLN/KM amortyzacja
            total_cost_calc = f_cost + toll_cost + maintenance
            
            st.markdown(f"**PROJECTED COSTS FOR: {v_sel_key}**")
            st.write(f"Fuel Consumption: {f_consumption:.1f} Liters")
            st.write(f"Fuel Charges: {f_cost:,.2f} PLN")
            st.write(f"Toll Charges (Est): {toll_cost:,.2f} PLN")
            st.write(f"Maintenance/Tires: {maintenance:,.2f} PLN")
            st.divider()
            st.markdown(f"#### TOTAL OPERATING COST: <span style='color:var(--v-copper);'>{total_cost_calc:,.2f} PLN</span>", unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

    # --------------------------------------------------------------------------
    # TAB 4: SYSTEM TERMINAL LOGS
    # --------------------------------------------------------------------------
    with tab_l:
        st.markdown("### ⚙️ IMPERATOR SYSTEM TERMINAL")
        if 'imperator_logs' in st.session_state:
            log_str = "\n".join(st.session_state.imperator_logs[::-1])
            st.code(log_str, language="bash")
        else:
            st.write("Initializing logs archive...")

if __name__ == "__main__":
    main()
