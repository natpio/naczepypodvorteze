# -*- coding: utf-8 -*-
"""
================================================================================
VORTEZA FLOW | KRAKEN EDITION v13.0
ULTIMATE LOGISTICS OPERATING SYSTEM & ENGINEERING TERMINAL
================================================================================
MODUŁ: V-PERMIT ROTATION CONTROL SYSTEM
STATUS: ENTERPRISE READY | PAID TIER ARCHITECTURE
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

# ==============================================================================
# 1. KRYTYCZNA KONFIGURACJA ŚRODOWISKA I FLOTY
# ==============================================================================
st.set_page_config(
    page_title="VORTEZA FLOW | KRAKEN v13.0",
    layout="wide",
    initial_sidebar_state="expanded",
    page_icon="🕋"
)

# REJESTR FLOTY KRAKEN (Pełna specyfikacja inżynieryjna z parametrami kosztowymi)
FLEET_MASTER_REGISTRY = {
    "TIR FTL (Mega 13.6m)": {
        "max_w": 24000, "L": 1360, "W": 248, "H": 300, 
        "ldm_max": 13.6, "fuel_avg": 0.32, "myto_eur": 0.22, "tank": 1200,
        "axles": 3, "tare": 14500, "cat": "HEAVY"
    },
    "TIR FTL (Standard 13.6m)": {
        "max_w": 24000, "L": 1360, "W": 248, "H": 275, 
        "ldm_max": 13.6, "fuel_avg": 0.28, "myto_eur": 0.20, "tank": 1000,
        "axles": 3, "tare": 13800, "cat": "HEAVY"
    },
    "Solo 9m (Heavy)": {
        "max_w": 9500, "L": 920, "W": 245, "H": 270, 
        "ldm_max": 9.2, "fuel_avg": 0.24, "myto_eur": 0.18, "tank": 500,
        "axles": 2, "tare": 8500, "cat": "MEDIUM"
    },
    "Solo 7m (Medium)": {
        "max_w": 7000, "L": 720, "W": 245, "H": 260, 
        "ldm_max": 7.2, "fuel_avg": 0.20, "myto_eur": 0.15, "tank": 400,
        "axles": 2, "tare": 6200, "cat": "MEDIUM"
    },
    "BUS XL (Express)": {
        "max_w": 1250, "L": 485, "W": 175, "H": 220, 
        "ldm_max": 4.8, "fuel_avg": 0.11, "myto_eur": 0.00, "tank": 90,
        "axles": 2, "tare": 2250, "cat": "LIGHT"
    }
}

# ==============================================================================
# 2. VORTEZA PRESTIGE DESIGN SYSTEM (ULTIMATE SCSS CORE)
# ==============================================================================
def apply_kraken_styling():
    """Wstrzykuje zaawansowany arkusz stylów marki VORTEZA KRAKEN."""
    st.markdown("""
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;600;700&family=JetBrains+Mono:wght@300;400;500&display=swap');
            
            :root {
                --v-copper: #B58863;
                --v-gold: #D4AF37;
                --v-obsidian: #010101;
                --v-card-bg: rgba(10, 10, 10, 0.98);
                --v-border-glow: rgba(181, 136, 99, 0.25);
                --v-danger: #FF3131;
                --v-success: #00FF41;
            }

            /* Global Architecture */
            .stApp { background-color: var(--v-obsidian); color: #FFFFFF; font-family: 'Montserrat', sans-serif; }
            
            /* Sidebar Engineering */
            section[data-testid="stSidebar"] {
                background-color: #040404 !important;
                border-right: 1px solid var(--v-border-glow);
                width: 500px !important;
            }

            /* Tactical Kraken Cards */
            .v-kraken-card {
                background: var(--v-card-bg);
                padding: 3.5rem;
                border-radius: 0px;
                border: 1px solid var(--v-border-glow);
                border-left: 20px solid var(--v-copper);
                box-shadow: 0 70px 180px rgba(0,0,0,1);
                margin-bottom: 5rem;
                backdrop-filter: blur(60px);
            }

            /* Headlines Protocols */
            h1, h2, h3 { 
                color: var(--v-copper) !important; 
                text-transform: uppercase; 
                letter-spacing: 15px !important; 
                font-weight: 700 !important; 
                text-shadow: 0 0 40px rgba(181, 136, 99, 0.4);
            }
            .v-label-small { color: #555; font-size: 0.65rem; letter-spacing: 5px; text-transform: uppercase; }

            /* Advanced Metrics */
            [data-testid="stMetricValue"] { 
                color: var(--v-copper) !important; 
                font-family: 'JetBrains Mono', monospace !important; 
                font-size: 4rem !important;
                font-weight: 300 !important;
            }
            [data-testid="stMetricLabel"] { color: #666; text-transform: uppercase; letter-spacing: 4px; font-weight: 700; }

            /* Interactive Master Controls */
            .stButton > button {
                background: linear-gradient(180deg, #080808 0%, #151515 100%);
                color: var(--v-copper);
                border: 2px solid var(--v-copper);
                padding: 1.8rem 4rem;
                text-transform: uppercase;
                letter-spacing: 10px;
                font-weight: 700;
                width: 100%;
                transition: 1s all cubic-bezier(0.19, 1, 0.22, 1);
                border-radius: 0;
            }
            .stButton > button:hover {
                background: var(--v-copper);
                color: #000;
                box-shadow: 0 0 120px rgba(181, 136, 99, 1);
                transform: translateY(-8px) scale(1.02);
            }

            /* Tactical Table Protocols */
            .v-tactical-table { width: 100%; border-collapse: collapse; margin-top: 50px; }
            .v-tactical-table th { background: #000; color: var(--v-copper); text-align: left; font-size: 0.85rem; text-transform: uppercase; border-bottom: 4px solid #222; padding: 30px; letter-spacing: 4px; }
            .v-tactical-table td { padding: 25px 30px; border-bottom: 1px solid #111; font-size: 1rem; color: #BBB; }
            .v-tactical-table tr:hover { background: rgba(181,136,99,0.06); }

            /* Unit Indicators */
            .v-permit-indicator {
                padding: 5px 12px;
                font-size: 0.7rem;
                font-weight: 700;
                letter-spacing: 2px;
                border-radius: 2px;
            }
            .v-permit-ok { background: rgba(0,255,65,0.1); color: #00FF41; border: 1px solid #00FF41; }
            .v-permit-no { background: rgba(255,49,49,0.1); color: #FF3131; border: 1px solid #FF3131; }

            /* Scrollbar Elite */
            ::-webkit-scrollbar { width: 4px; }
            ::-webkit-scrollbar-track { background: #000; }
            ::-webkit-scrollbar-thumb { background: var(--v-copper); }
        </style>
    """, unsafe_allow_html=True)

# ==============================================================================
# 3. KONTROLA BEZPIECZEŃSTWA (IMPERATOR SECURITY)
# ==============================================================================
def verify_kraken_access():
    """Zarządza autoryzacją dostępu do platformy Kraken."""
    if "authorized" not in st.session_state:
        st.session_state.authorized = False

    if not st.session_state.authorized:
        try:
            # Hasło pobierane z Streamlit Cloud Secrets
            sys_key = str(st.secrets.get("password", "vorteza2026"))
        except:
            sys_key = "vorteza2026"

        st.markdown("<br><br><br><br><br><br><br>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1, 2.5, 1])
        with col2:
            with st.form("KrakenAuth"):
                st.markdown("<h2 style='text-align:center;'>VORTEZA KRAKEN</h2>", unsafe_allow_html=True)
                st.markdown("<p style='text-align:center; color:#222; font-size:0.8rem; letter-spacing:6px;'>ENCRYPTED COMMAND TERMINAL</p>", unsafe_allow_html=True)
                pwd_in = st.text_input("GOLIATH MASTER AUTHENTICATION KEY", type="password", placeholder="ENTER CLEARANCE CODE")
                if st.form_submit_button("INITIALIZE MISSION PROTOCOL"):
                    if pwd_in == sys_key:
                        st.session_state.authorized = True
                        st.rerun()
                    else:
                        st.error("ACCESS DENIED: SECURITY BREACH DETECTED")
        return False
    return True

# ==============================================================================
# 4. CHROMATIC PRODUCT CORE (COLOUR LOGISTICS INTEL)
# ==============================================================================
def get_vorteza_color_map(name):
    """Generuje deterministyczny, unikalny kolor HEX dla każdego SKU."""
    industrial_palette = [
        "#B58863", "#D4AF37", "#8E6A4D", "#5E4633", "#A67C52", 
        "#2C3E50", "#34495E", "#1A252F", "#16A085", "#27AE60",
        "#7F8C8D", "#95A5A6", "#BDC3C7", "#E67E22", "#D35400",
        "#C0392B", "#E74C3C", "#8E44AD", "#9B59B6", "#2980B9"
    ]
    # Deterministyczne ziarno oparte na sumie ASCII nazwy
    random.seed(sum(ord(c) for c in name))
    return random.choice(industrial_palette)

# ==============================================================================
# 5. RENDERER CAD-3D KRAKEN (VISUAL ENGINE v13.0)
# ==============================================================================
def render_kraken_3d(veh_specs, cargo_stacks):
    """Generuje hiper-szczegółowy model naczepy z oświetleniem punktowym."""
    fig = go.Figure()
    L, W, H = veh_specs['L'], veh_specs['W'], veh_specs['H']

    # --- INFRASTRUKTURA POJAZDU (CAD DETAIL) ---
    # Podłoga i Rama Heavy-Duty
    fig.add_trace(go.Mesh3d(
        x=[0, L, L, 0], y=[0, 0, W, W], z=[-12, -12, -12, -12],
        color='#111111', opacity=1, hoverinfo='skip'
    ))
    
    # Koła i Zawieszenie (Render techniczny)
    axles = veh_specs.get('axles', 3)
    axle_spacing = 145
    rear_start = L - 350 if L > 700 else L - 180
    
    for i in range(axles):
        curr_x = rear_start + (i * axle_spacing)
        if curr_x < L:
            for side in [-35, W+18]:
                # Opona
                fig.add_trace(go.Mesh3d(
                    x=[curr_x-55, curr_x+55, curr_x+55, curr_x-55], 
                    y=[side, side, side+17, side+17], 
                    z=[-65, -65, -12, -12], color='#000000', opacity=1, hoverinfo='skip'
                ))
                # Felga miedziana
                fig.add_trace(go.Mesh3d(
                    x=[curr_x-25, curr_x+25, curr_x+25, curr_x-25], 
                    y=[side-2, side-2, side, side], 
                    z=[-50, -50, -25, -25], color='#B58863', opacity=0.9, hoverinfo='skip'
                ))

    # Kabina Dowodzenia (Goliath Command Block)
    cab_depth = 220
    fig.add_trace(go.Mesh3d(
        x=[-cab_depth, 0, 0, -cab_depth, -cab_depth, 0, 0, -cab_depth],
        y=[-30, -30, W+30, W+30, -30, -30, W+30, W+30],
        z=[0, 0, 0, 0, H*0.99, H*0.99, H*0.99, H*0.99],
        i=[7,0,0,0,4,4,6,6,4,0,3,2], j=[3,4,1,2,5,6,5,2,0,1,6,3], k=[0,7,2,3,6,7,1,1,5,5,7,6],
        color='#040404', opacity=1, name="UNIT_COMMAND_CAB"
    ))

    # Klatka Naczepy (Miedziany szkielet konstrukcyjny)
    skeleton = [
        ([0, L], [0, 0], [0, 0]), ([0, L], [W, W], [0, 0]),
        ([0, 0], [0, W], [0, 0]), ([L, L], [0, W], [0, 0]),
        ([0, 0], [0, 0], [0, H]), ([0, 0], [W, W], [0, H]),
        ([0, L], [0, 0], [H, H]), ([0, L], [W, W], [H, H]),
        ([L, L], [0, 0], [0, H]), ([L, L], [W, W], [0, H])
    ]
    for sx, sy, sz in skeleton:
        fig.add_trace(go.Scatter3d(x=sx, y=sy, z=sz, mode='lines', line=dict(color='#B58863', width=12), hoverinfo='skip'))

    # --- RENDER CLUSTERÓW ŁADUNKOWYCH (DYNAMIC COLORING + PERMIT VISUALS) ---
    for stack in cargo_stacks:
        for item in stack['items']:
            x, y, z = stack['x'], stack['y'], item['z']
            dx, dy, dz = item['w_fit'], item['l_fit'], item['height']
            
            p_color = get_vorteza_color_map(item['name'])
            
            # Bryła geometryczna produktu
            fig.add_trace(go.Mesh3d(
                x=[x,x+dx,x+dx,x,x,x+dx,x+dx,x], y=[y,y,y+dy,y+dy,y,y,y+dy,y+dy], 
                z=[z,z,z,z,z+dz,z+dz,z+dz,z+dz],
                i=[7,0,0,0,4,4,6,6,4,0,3,2], j=[3,4,1,2,5,6,5,2,0,1,6,3], k=[0,7,2,3,6,7,1,1,5,5,7,6],
                color=p_color, opacity=0.98, name=item['name'],
                hovertemplate=f"<b>{item['name']}</b><br>D: {dx}cm W: {dy}cm H: {dz}cm<br>ROTACJA: {'TAK' if item.get('allowRotation', True) else 'ZABLOKOWANA'}<extra></extra>"
            ))
            # Kontur Separacji (Hi-Res Edge Detection)
            fig.add_trace(go.Scatter3d(
                x=[x,x+dx,x+dx,x,x,x+dx,x+dx,x,x,x+dx,x+dx,x+dx,x+dx,x,x],
                y=[y,y,y+dy,y+dy,y,y,y+dy,y+dy,y+dy,y+dy,y+dy,y,y,y+dy,y+dy,y],
                z=[z,z,z,z,z,z+dz,z+dz,z,z,z+dz,z+dz,z+dz,z,z,z+dz,z+dz],
                mode='lines', line=dict(color='black', width=3), hoverinfo='skip'
            ))

    fig.update_layout(
        scene=dict(
            aspectmode='data', xaxis_visible=False, yaxis_visible=False, zaxis_visible=False,
            camera=dict(eye=dict(x=2.4, y=2.4, z=1.8)), bgcolor='rgba(0,0,0,0)'
        ),
        paper_bgcolor='rgba(0,0,0,0)', margin=dict(l=0, r=0, b=0, t=0), showlegend=False
    )
    return fig

# ==============================================================================
# 6. SILNIK PAKOWANIA V-ENGINE 13.0 (PERMIT-BASED ROTATION)
# ==============================================================================
class V13KrakenEngine:
    """Zaawansowany algorytm bin-packing z kontrolą systemu pozwoleń na obrót."""
    
    @staticmethod
    def solve(cargo_list, vehicle):
        # Priorytety: 1. No-Stack, 2. No-Rotation, 3. Pole powierzchni
        items_sorted = sorted(cargo_list, key=lambda x: (not x.get('canStack', True), not x.get('allowRotation', True), x['width']*x['length']), reverse=True)
        
        placed_stacks, failed_units, total_mass = [], [], 0
        cur_x, cur_y, cur_row_max_w = 0, 0, 0

        for unit in items_sorted:
            # Weryfikacja payloadu pojazdu
            if total_mass + unit['weight'] > vehicle['max_w']:
                failed_units.append(unit); continue
            
            # PROTOKÓŁ PIĘTROWANIA (Vertical Stacking)
            is_stacked = False
            if unit.get('canStack', True):
                for stack in placed_stacks:
                    # Dopasowanie wymiarowe z uwzględnieniem ZABLOKOWANEJ rotacji
                    if unit.get('allowRotation', True):
                        dim_match = (unit['width'] <= stack['w'] and unit['length'] <= stack['l']) or \
                                    (unit['length'] <= stack['w'] and unit['width'] <= stack['l'])
                    else:
                        # Brak zgody na obrót - musi pasować tak jak leży
                        dim_match = (unit['width'] <= stack['w'] and unit['length'] <= stack['l'])
                    
                    if dim_match and (stack['curH'] + unit['height'] <= vehicle['H']):
                        u_copy = unit.copy(); u_copy['z'] = stack['curH']
                        u_copy['w_fit'], u_copy['l_fit'] = stack['w'], stack['l']
                        stack['items'].append(u_copy); stack['curH'] += unit['height']
                        total_mass += unit['weight']; is_stacked = True; break
            
            if is_stacked: continue

            # PROTOKÓŁ PODŁOGI (Floor placement + V-PERMIT ROTATION)
            is_placed = False
            # Definiowanie dopuszczalnych orientacji
            if unit.get('allowRotation', True):
                orientations = [(unit['width'], unit['length']), (unit['length'], unit['width'])]
            else:
                orientations = [(unit['width'], unit['length'])] # Tylko jedna strona
            
            for fw, fl in orientations:
                if cur_y + fl <= vehicle['W'] and cur_x + fw <= vehicle['L']:
                    u_c = unit.copy(); u_c['z'] = 0; u_c['w_fit'], u_c['l_fit'] = fw, fl
                    placed_stacks.append({'x':cur_x, 'y':cur_y, 'w':fw, 'l':fl, 'curH':unit['height'], 'items':[u_c]})
                    cur_y += fl; cur_row_max_w = max(cur_row_max_w, fw)
                    total_mass += unit['weight']; is_placed = True; break
                elif cur_x + cur_row_max_w + fw <= vehicle['L'] and fl <= vehicle['W']:
                    cur_x += cur_row_max_w; cur_y = 0; cur_row_max_w = fw
                    u_c = unit.copy(); u_c['z'] = 0; u_c['w_fit'], u_c['l_fit'] = fw, fl
                    placed_stacks.append({'x':cur_x, 'y':cur_y, 'w':fw, 'l':fl, 'curH':unit['height'], 'items':[u_c]})
                    cur_y += fl; total_mass += unit['weight']; is_placed = True; break
            
            if not is_placed: failed_units.append(unit)
        
        # Real-time LDM Calculation
        ldm_res = (max([s['x'] + s['w'] for s in placed_stacks]) / 100) if placed_stacks else 0
        return placed_stacks, total_mass, failed_units, ldm_res

# ==============================================================================
# 7. ZARZĄDZANIE DANYMI I PERSYSTENCJA (DB ENGINE)
# ==============================================================================
def db_kraken_load():
    """Wczytuje globalną bazę towarową VORTEZA."""
    try:
        with open('products.json', 'r', encoding='utf-8') as f: return json.load(f)
    except: return []

def db_kraken_save(data):
    """Zapisuje zmiany w bazie towarowej."""
    with open('products.json', 'w', encoding='utf-8') as f: 
        json.dump(data, f, indent=4, ensure_ascii=False)

def log_kraken_event(message):
    """Rejestruje logi systemowe sesji."""
    if 'k_logs' not in st.session_state: st.session_state.k_logs = []
    ts = datetime.now().strftime("%H:%M:%S")
    st.session_state.k_logs.append(f"[{ts}] KRAKEN_EXE: {message}")

# ==============================================================================
# 8. ARCHITEKTURA INTERFEJSU (KRAKEN COMMAND CENTER)
# ==============================================================================
def main():
    apply_kraken_styling()
    
    if not verify_kraken_access(): return

    # Inicjalizacja Manifestu i Inwentarza
    if 'v_manifest' not in st.session_state: st.session_state.v_manifest = []
    inventory = db_kraken_load()

    # --- TOP CONTROL BAR ---
    h_col1, h_col2 = st.columns([7, 1])
    with h_col1:
        st.markdown("<h1>VORTEZA KRAKEN FLOW</h1>", unsafe_allow_html=True)
        st.markdown(f"<p class='v-label-small'>LOGISTICS COMMAND CENTER v13.0.1 | STATUS: OPERATIONAL | {datetime.now().strftime('%Y-%m-%d')}</p>", unsafe_allow_html=True)
    with h_col2:
        if st.button("TERMINATE"):
            st.session_state.authorized = False; st.rerun()

    # --- SIDEBAR: MISSION CONTROL ---
    with st.sidebar:
        st.markdown("### 📡 FLEET DEPLOYMENT")
        v_key = st.selectbox("FLEET UNIT SELECTOR", list(FLEET_MASTER_REGISTRY.keys()))
        veh = FLEET_MASTER_REGISTRY[v_key]
        
        st.markdown(f"""<div style='background:rgba(181,136,99,0.05); border:1px solid var(--v-copper); padding:20px; font-size:0.85rem; color:#888;'>
            <b>UNIT SPECS:</b><br>
            VOLUME: {veh['L']}x{veh['W']}x{veh['H']} CM<br>
            NET PAYLOAD: {veh['max_w']} KG<br>
            LDM CAPACITY: {veh['ldm_max']}
        </div>""", unsafe_allow_html=True)
        
        st.divider()
        st.markdown("### 📥 MISSION MANIFEST")
        p_names = [p['name'] for p in inventory]
        sel_sku = st.selectbox("SKU LOOKUP SERVICE", p_names, index=None)
        
        if sel_sku:
            p_obj = next(p for p in inventory if p['name'] == sel_sku)
            ipc = p_obj.get('itemsPerCase', 1)
            # Pokazujemy stan pozwolenia na obrót w sidebarze
            r_permit = p_obj.get('allowRotation', True)
            
            st.markdown(f"""
                <div class='v-tag'>
                    STANDARD: {ipc} PCS/CASE<br>
                    OBRÓT: {'<span style="color:#00FF41">DOZWOLONY</span>' if r_permit else '<span style="color:#FF3131">ZABLOKOWANY</span>'}
                </div>
            """, unsafe_allow_html=True)
            
            count_in = st.number_input("QUANTITY TO DISPATCH (PCS)", min_value=1, value=ipc)
            num_units = math.ceil(count_in / ipc)
            
            if st.button("PUSH TO MANIFEST", type="primary"):
                for i in range(num_units):
                    unit_entry = p_obj.copy()
                    unit_entry['p_actual'] = ipc if (i < num_units - 1 or count_in % ipc == 0) else (count_in % ipc)
                    st.session_state.v_manifest.append(unit_entry)
                log_kraken_event(f"Loaded {num_units} units of {sel_sku}")
                st.toast(f"MANIFEST SYNCED: {num_units} units added.")

        if st.button("PURGE MANIFEST"):
            st.session_state.v_manifest = []; log_kraken_event("Global manifest cleared."); st.rerun()

    # --- TABS ARCHITECTURE ---
    tab_planner, tab_inventory, tab_finance, tab_terminal = st.tabs(["📊 KRAKEN PLANNER", "📦 PRODUCT CORE", "💰 FINANCIAL INTEL", "⚙️ SYSTEM LOGS"])

    # --------------------------------------------------------------------------
    # TAB 1: KRAKEN PLANNER (3D RENDERING & ANALYTICS)
    # --------------------------------------------------------------------------
    with tab_planner:
        if st.session_state.v_manifest:
            # Manifest Dashboard KPI
            kpi_c1, kpi_c2, kpi_c3, kpi_c4 = st.columns(4)
            t_mass = sum(float(u['weight']) for u in st.session_state.v_manifest)
            t_cases = len(st.session_state.v_manifest)
            t_pcs = sum(int(u.get('p_actual', 1)) for u in st.session_state.v_manifest)
            
            kpi_c1.metric("CASES", t_cases)
            kpi_c2.metric("TOTAL PCS", t_pcs)
            kpi_c3.metric("GROSS WEIGHT", f"{t_mass} KG")
            kpi_c4.metric("WEIGHT UTIL", f"{(t_mass/veh['max_w'])*100:.1f}%")

            # Execution logic (Kraken Engine)
            rem_units = [dict(u) for u in st.session_state.v_manifest]
            fleet_allocation = []
            
            while rem_units:
                st_res, w_res, rem_res, ldm_res = V13KrakenEngine.solve(rem_units, veh)
                if not st_res:
                    st.error("LOGISTICS FAILURE: Unit exceeds fleet cargo box dimensions.")
                    break
                fleet_allocation.append({"stacks": st_res, "weight": w_res, "ldm": ldm_res})
                rem_units = rem_res

            st.markdown(f"### ASIGNED FLEET CAPACITY: {len(fleet_allocation)} JEDNOSTKI")
            
            for idx, truck in enumerate(fleet_allocation):
                st.markdown(f'<div class="v-kraken-card">', unsafe_allow_html=True)
                st.markdown(f"### TRANSPORT UNIT #{idx+1} | {v_key}", unsafe_allow_html=True)
                
                v_col, d_col = st.columns([2.5, 1])
                with v_col:
                    st.plotly_chart(render_kraken_3d(veh, truck['stacks']), use_container_width=True)
                with d_col:
                    st.markdown("**OPERATIONAL KPI**")
                    st.write(f"Mass Ratio: {(truck['weight']/veh['max_w'])*100:.1f}%")
                    st.write(f"Utilized LDM: {truck['ldm']:.2f} m")
                    st.write(f"Payload Weight: {truck['weight']} kg")
                    
                    st.divider()
                    st.markdown("**CARGO PACKING LIST**")
                    it_names = [it['name'] for s in truck['stacks'] for it in s['items']]
                    if it_names:
                        sum_df = pd.Series(it_names).value_counts().reset_index()
                        sum_df.columns = ['SKU', 'QTY']
                        
                        h_table = '<table class="v-tactical-table"><tr><th>SKU</th><th>QTY</th></tr>'
                        for _, r in sum_df.iterrows():
                            c = get_vorteza_color_map(r['SKU'])
                            h_table += f'<tr><td><span style="color:{c};">■</span> {r["SKU"]}</td><td>{r["QTY"]}</td></tr>'
                        st.markdown(h_table+'</table>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.info("KRAKEN PROTOCOL: WAITING FOR MANIFEST INJECTION...")

    # --------------------------------------------------------------------------
    # TAB 2: PRODUCT CORE (INVENTORY CRUD)
    # --------------------------------------------------------------------------
    with tab_inventory:
        st.markdown("### 📦 GLOBAL PRODUCT DATABASE ADMINISTRATION")
        
        with st.expander("➕ DEFINE NEW ASSET SPECIFICATION"):
            with st.form("NewKrakenAsset"):
                f_name = st.text_input("Product Identifier / SKU")
                ci1, ci2, ci3 = st.columns(3)
                f_l = ci1.number_input("L (cm)", 120)
                f_w = ci2.number_input("W (cm)", 80)
                f_h = ci3.number_input("H (cm)", 100)
                ci4, ci5 = st.columns(2)
                f_mass = ci4.number_input("Mass (kg)", 100)
                f_ipc = ci5.number_input("Pcs/Case", 1)
                
                st.markdown("**V-PERMIT PERMISSIONS:**")
                ck1, ck2 = st.columns(2)
                f_stk = ck1.checkbox("Vertical Stacking Approved", value=True)
                f_rot = ck2.checkbox("Horizontal Rotation Allowed", value=True)
                
                if st.form_submit_button("COMMIT TO MASTER DB"):
                    inventory.append({
                        "name": f_name, "length": f_l, "width": f_w, "height": f_h, 
                        "weight": f_mass, "itemsPerCase": f_ipc, "canStack": f_stk, "allowRotation": f_rot
                    })
                    db_kraken_save(inventory)
                    log_kraken_event(f"New asset registered in DB: {f_name}")
                    st.success("CORE DATABASE SYNCHRONIZED."); st.rerun()

        st.divider()
        if inventory:
            st.markdown("**GLOBAL INVENTORY ARCHIVE**")
            df_core = pd.DataFrame(inventory)
            # Zaawansowany edytor z obsługą bool (canStack, allowRotation)
            ed_archive = st.data_editor(df_core, use_container_width=True, num_rows="dynamic", key="kraken_db_editor")
            if st.button("PUSH CHANGES TO CLOUD"):
                db_kraken_save(ed_archive.to_dict('records'))
                log_kraken_event("Global inventory database manually override sync.")
                st.success("DATABASE STATUS: SYNCHRONIZED SUCCESSFULLY."); st.rerun()
        else:
            st.warning("DATABASE STATUS: NO ASSETS DETECTED.")

    # --------------------------------------------------------------------------
    # TAB 3: FINANCIAL INTEL (MISSION COST)
    # --------------------------------------------------------------------------
    with tab_finance:
        st.markdown("### 💰 MISSION COST SIMULATION")
        cf1, cf2 = st.columns(2)
        with cf1:
            st.markdown('<div class="v-kraken-card">', unsafe_allow_html=True)
            dist_km = st.number_input("Route Distance (KM)", 10, 10000, 1500)
            fuel_price = st.number_input("Current ON Price (PLN/L)", 4.0, 12.0, 6.45)
            euro_val = st.number_input("Exchange Rate (EUR/PLN)", 4.0, 5.0, 4.32)
            st.markdown('</div>', unsafe_allow_html=True)
        with cf2:
            st.markdown('<div class="v-kraken-card">', unsafe_allow_html=True)
            # Logistics Algorithms
            f_need = dist_km * veh['fuel_avg']
            c_fuel = f_need * fuel_price
            c_toll = dist_km * veh['myto_eur'] * euro_val
            c_total = c_fuel + c_toll
            
            st.markdown(f"**PROJECTED COSTS FOR: {v_key}**")
            st.write(f"Fuel Consumption: {f_need:.1f} Liters")
            st.write(f"Fuel Charges: {c_fuel:,.2f} PLN")
            st.write(f"Toll Charges (Est): {c_toll:,.2f} PLN")
            st.divider()
            st.markdown(f"#### TOTAL OPERATING COST: <span style='color:var(--v-copper);'>{c_total:,.2f} PLN</span>", unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

    # --------------------------------------------------------------------------
    # TAB 4: SYSTEM TERMINAL LOGS
    # --------------------------------------------------------------------------
    with tab_terminal:
        st.markdown("### ⚙️ KRAKEN SYSTEM TERMINAL")
        if 'k_logs' in st.session_state:
            log_str = "\n".join(st.session_state.k_logs[::-1])
            st.code(log_str, language="bash")
        else:
            st.write("Initializing logs archive...")

if __name__ == "__main__":
    main()
