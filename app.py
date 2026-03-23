# -*- coding: utf-8 -*-
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
# 1. GLOBALNA KONFIGURACJA ŚRODOWISKA I FLOTY
# ==============================================================================
st.set_page_config(
    page_title="VORTEZA STACK v17.0",
    layout="wide",
    initial_sidebar_state="expanded",
    page_icon="🕋"
)

FLEET_REGISTRY = {
    "TIR FTL (Mega 13.6m)": {
        "max_w": 24000, "L": 1360, "W": 248, "H": 300, 
        "ldm": 13.6, "axles": 3, "wheelbase": 850, "tare": 14500, "cab_l": 240
    },
    "TIR FTL (Standard 13.6m)": {
        "max_w": 24000, "L": 1360, "W": 248, "H": 275, 
        "ldm": 13.6, "axles": 3, "wheelbase": 850, "tare": 13800, "cab_l": 240
    },
    "Solo 9m (Heavy Logistics)": {
        "max_w": 9500, "L": 920, "W": 245, "H": 270, 
        "ldm": 9.2, "axles": 2, "wheelbase": 550, "tare": 8500, "cab_l": 200
    },
    "Solo 7m (Medium Distribution)": {
        "max_w": 7000, "L": 720, "W": 245, "H": 260, 
        "ldm": 7.2, "axles": 2, "wheelbase": 480, "tare": 6200, "cab_l": 180
    },
    "BUS XL (Express)": {
        "max_w": 1250, "L": 485, "W": 175, "H": 220, 
        "ldm": 4.8, "axles": 2, "wheelbase": 320, "tare": 2250, "cab_l": 140
    }
}

# ==============================================================================
# 2. VORTEZA STACK BRANDING & CSS ENGINE
# ==============================================================================
def get_resource_as_base64(path):
    try:
        if os.path.exists(path):
            with open(path, 'rb') as f:
                return base64.b64encode(f.read()).decode()
        return ""
    except:
        return ""

def inject_vorteza_enterprise_ui():
    bg_data = get_resource_as_base64('bg_vorteza.png')
    
    st.markdown(f"""
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;600;700&family=JetBrains+Mono:wght@300;400;500&display=swap');
            
            :root {{
                --v-copper: #B58863;
                --v-copper-glow: rgba(181, 136, 99, 0.4);
                --v-dark-obsidian: #050505;
                --v-panel-bg: rgba(10, 10, 10, 0.96);
                --v-border: rgba(181, 136, 99, 0.25);
            }}

            .stApp {{
                background-image: url("data:image/png;base64,{bg_data}");
                background-size: cover;
                background-attachment: fixed;
                color: #F0F0F0;
                font-family: 'Montserrat', sans-serif;
            }}

            .v-stack-container {{
                background: var(--v-panel-bg);
                padding: 3rem;
                border: 1px solid var(--v-border);
                border-left: 12px solid var(--v-copper);
                box-shadow: 0 40px 100px rgba(0,0,0,0.9);
                margin-bottom: 3.5rem;
                backdrop-filter: blur(40px);
            }}

            section[data-testid="stSidebar"] {{
                background-color: rgba(3, 3, 3, 0.98) !important;
                border-right: 1px solid var(--v-border);
                width: 480px !important;
            }}

            h1, h2, h3 {{ 
                color: var(--v-copper) !important; 
                text-transform: uppercase; 
                letter-spacing: 10px !important; 
                font-weight: 700 !important; 
                text-shadow: 2px 2px 20px rgba(0,0,0,0.8);
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
                padding: 1.5rem;
                text-transform: uppercase;
                letter-spacing: 6px;
                font-weight: 700;
                width: 100%;
                transition: 0.5s cubic-bezier(0.4, 0, 0.2, 1);
                border-radius: 0;
            }}

            .stButton > button:hover {{
                background: var(--v-copper);
                color: black;
                box-shadow: 0 0 80px var(--v-copper-glow);
                transform: translateY(-3px);
            }}

            .v-data-table {{ 
                width: 100%; 
                border-collapse: collapse; 
                margin-top: 30px; 
                background: rgba(0,0,0,0.3);
            }}
            .v-data-table th {{ 
                color: var(--v-copper); 
                text-align: left; 
                font-size: 0.75rem; 
                text-transform: uppercase; 
                border-bottom: 2px solid #333; 
                padding: 20px; 
                letter-spacing: 3px;
            }}
            .v-data-table td {{ 
                padding: 18px 20px; 
                border-bottom: 1px solid #1a1a1a; 
                color: #CCC; 
                font-size: 0.9rem; 
            }}
            .v-data-table tr:hover {{ background: rgba(181,136,99,0.05); }}

            .v-cog-rail {{
                width: 100%;
                height: 25px;
                background: #111;
                border-radius: 12px;
                position: relative;
                border: 1px solid #333;
                margin: 40px 0;
            }}
            .v-cog-marker {{
                position: absolute;
                width: 6px;
                height: 45px;
                top: -10px;
                background: #00FF41;
                box-shadow: 0 0 20px #00FF41;
                border-radius: 3px;
            }}
            
            [data-testid="stExpander"] {{
                background: rgba(15,15,15,0.8) !important;
                border: 1px solid var(--v-border) !important;
            }}
        </style>
    """, unsafe_allow_html=True)

# ==============================================================================
# 3. KONTROLA DOSTĘPU (SECURITY GATEWAY)
# ==============================================================================
def authenticate_terminal():
    if "authorized" not in st.session_state:
        st.session_state.authorized = False

    if not st.session_state.authorized:
        try:
            sys_key = str(st.secrets.get("password", "vorteza2026"))
        except:
            sys_key = "vorteza2026"

        st.markdown("<br><br><br><br><br><br>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1, 1.8, 1])
        with col2:
            with st.form("VortezaAuthGate"):
                st.markdown("<h2 style='text-align:center;'>VORTEZA STACK</h2>", unsafe_allow_html=True)
                st.markdown("<p style='text-align:center; color:#444; font-size:0.75rem; letter-spacing:5px;'>SECURITY AUTHORIZATION REQUIRED</p>", unsafe_allow_html=True)
                input_key = st.text_input("GOLIATH MASTER ACCESS KEY", type="password")
                if st.form_submit_button("VALIDATE SECURITY CLEARANCE"):
                    if input_key == sys_key:
                        st.session_state.authorized = True
                        st.rerun()
                    else:
                        st.error("ACCESS DENIED: INVALID CORE PROTOCOL KEY")
        return False
    return True

# ==============================================================================
# 4. CHROMATIC PRODUCT CORE (STABILNY SILNIK KOLORÓW)
# ==============================================================================
def get_vorteza_product_color(sku_name):
    palette = [
        "#B58863", "#D4AF37", "#8E6A4D", "#5E4633", "#A67C52", 
        "#2C3E50", "#34495E", "#1A252F", "#16A085", "#27AE60",
        "#7F8C8D", "#95A5A6", "#BDC3C7", "#7E4A35", "#C0392B",
        "#D35400", "#F39C12", "#2980B9", "#8E44AD", "#3D3D3D",
        "#E67E22", "#E74C3C", "#9B59B6", "#1ABC9C", "#2980B9"
    ]
    random.seed(sum(ord(char) for char in sku_name))
    return random.choice(palette)

# ==============================================================================
# 5. RENDERER CAD-3D STACK (ENGINE v17.0)
# ==============================================================================
def render_stack_visualizer(veh_data, cargo_stacks):
    fig = go.Figure()
    L, W, H = veh_data['L'], veh_data['W'], veh_data['H']

    # --- KONSTRUKCJA POJAZDU (CAD DETAIL) ---
    fig.add_trace(go.Mesh3d(x=[0, L, L, 0], y=[0, 0, W, W], z=[-15, -15, -15, -15], color='#101010', opacity=1, hoverinfo='skip'))
    
    # Koła i Osie
    num_axles = veh_data.get('axles', 3)
    rear_start = L - 400 if L > 800 else L - 180
    for i in range(num_axles):
        curr_axle_x = rear_start + (i * 140)
        if curr_axle_x < L:
            for side in [-38, W+22]:
                # Opona
                fig.add_trace(go.Mesh3d(
                    x=[curr_axle_x-55, curr_axle_x+55, curr_axle_x+55, curr_axle_x-55], 
                    y=[side, side, side+16, side+16], 
                    z=[-70, -70, -15, -15], color='#000', opacity=1, hoverinfo='skip'
                ))
                # Felga miedziana
                fig.add_trace(go.Mesh3d(
                    x=[curr_axle_x-22, curr_axle_x+22, curr_axle_x+22, curr_axle_x-22], 
                    y=[side-2, side-2, side, side], 
                    z=[-50, -50, -35, -35], color='#B58863', opacity=0.9, hoverinfo='skip'
                ))

    # Kabina Operatora
    cab_depth = veh_data.get('cab_l', 240)
    fig.add_trace(go.Mesh3d(
        x=[-cab_depth, 0, 0, -cab_depth, -cab_depth, 0, 0, -cab_depth],
        y=[-40, -40, W+40, W+40, -40, -40, W+40, W+40],
        z=[0, 0, 0, 0, H*1.05, H*1.05, H*1.05, H*1.05],
        i=[7,0,0,0,4,4,6,6,4,0,3,2], j=[3,4,1,2,5,6,5,2,0,1,6,3], k=[0,7,2,3,6,7,1,1,5,5,7,6],
        color='#020202', opacity=1, name="CORE_CABIN"
    ))

    # Szkielet Paki (Miedziany)
    edges = [
        ([0, L], [0, 0], [0, 0]), ([0, L], [W, W], [0, 0]), ([0, 0], [0, W], [0, 0]), ([L, L], [0, W], [0, 0]),
        ([0, 0], [0, 0], [0, H]), ([0, 0], [W, W], [0, H]), ([0, L], [0, 0], [H, H]), ([0, L], [W, W], [H, H]),
        ([L, L], [0, 0], [0, H]), ([L, L], [W, W], [0, H])
    ]
    for ex, ey, ez in edges:
        fig.add_trace(go.Scatter3d(x=ex, y=ey, z=ez, mode='lines', line=dict(color='#B58863', width=12), hoverinfo='skip'))

    # --- RENDER ŁADUNKU ---
    for stack in cargo_stacks:
        for it in stack['items']:
            x, y, z = stack['x'], stack['y'], it['z']
            dx, dy, dz = it['w_fit'], it['l_fit'], it['height']
            p_color = get_vorteza_product_color(it['name'])
            
            # Bryła 3D
            fig.add_trace(go.Mesh3d(
                x=[x,x+dx,x+dx,x,x,x+dx,x+dx,x], y=[y,y,y+dy,y+dy,y,y,y+dy,y+dy], 
                z=[z,z,z,z,z+dz,z+dz,z+dz,z+dz],
                i=[7,0,0,0,4,4,6,6,4,0,3,2], j=[3,4,1,2,5,6,5,2,0,1,6,3], k=[0,7,2,3,6,7,1,1,5,5,7,6],
                color=p_color, opacity=0.98, name=it['name']
            ))
            # Kontur
            fig.add_trace(go.Scatter3d(
                x=[x,x+dx,x+dx,x,x,x+dx,x+dx,x,x,x+dx,x+dx,x+dx,x+dx,x,x],
                y=[y,y,y+dy,y+dy,y,y,y,y+dy,y+dy,y+dy,y+dy,y,y,y+dy,y+dy,y],
                z=[z,z,z,z,z,z+dz,z+dz,z,z,z+dz,z+dz,z+dz,z,z,z+dz,z+dz],
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
# 6. SILNIK PAKOWANIA V-ENGINE 17.0 (V-PERMIT & STACK LOGIC)
# ==============================================================================
class V17StackEngine:
    @staticmethod
    def execute_solve(cargo_list, vehicle):
        # Priorytety FFD: 1. No-Stack, 2. No-Rotation, 3. Powierzchnia
        items_sorted = sorted(cargo_list, 
                             key=lambda x: (not x.get('canStack', True), 
                                            not x.get('allowRotation', True), 
                                            x['width']*x['length']), 
                             reverse=True)
        
        placed_clusters, failed_units, weight_acc = [], [], 0
        cx, cy, current_row_max_w = 0, 0, 0

        for unit in items_sorted:
            if weight_acc + unit['weight'] > vehicle['max_w']:
                failed_units.append(unit); continue
            
            # STACKING LOGIC
            is_stacked = False
            if unit.get('canStack', True):
                for s in placed_clusters:
                    if unit.get('allowRotation', True):
                        dim_fit = (unit['width'] <= s['w'] and unit['length'] <= s['l']) or \
                                  (unit['length'] <= s['w'] and unit['width'] <= s['l'])
                    else:
                        dim_fit = (unit['width'] <= s['w'] and unit['length'] <= s['l'])
                    
                    if dim_fit and (s['curH'] + unit['height'] <= vehicle['H']):
                        u_c = unit.copy(); u_c['z'] = s['curH']; u_c['w_fit'], u_c['l_fit'] = s['w'], s['l']
                        s['items'].append(u_c); s['curH'] += unit['height']; weight_acc += unit['weight']; is_stacked = True; break
            
            if is_stacked: continue

            # FLOOR LOGIC + V-PERMIT ROTATION
            is_placed = False
            orientations = [(unit['width'], unit['length']), (unit['length'], unit['width'])] if unit.get('allowRotation', True) else [(unit['width'], unit['length'])]
            
            for fw, fl in orientations:
                if cy + fl <= vehicle['W'] and cx + fw <= vehicle['L']:
                    u_c = unit.copy(); u_c['z'] = 0; u_c['w_fit'], u_c['l_fit'] = fw, fl
                    placed_clusters.append({'x':cx, 'y':cy, 'w':fw, 'l':fl, 'curH':unit['height'], 'items':[u_c]})
                    cy += fl; current_row_max_w = max(current_row_max_w, fw); weight_acc += unit['weight']; is_placed = True; break
                elif cx + current_row_max_w + fw <= vehicle['L'] and fl <= vehicle['W']:
                    cx += current_row_max_w; cy = 0; current_row_max_w = fw
                    u_c = unit.copy(); u_c['z'] = 0; u_c['w_fit'], u_c['l_fit'] = fw, fl
                    placed_clusters.append({'x':cx, 'y':cy, 'w':fw, 'l':fl, 'curH':unit['height'], 'items':[u_c]})
                    cy += fl; weight_acc += unit['weight']; is_placed = True; break
            
            if not is_placed: failed_units.append(unit)
        
        ldm_real = (max([s['x'] + s['w'] for s in placed_clusters]) / 100) if placed_clusters else 0
        return placed_clusters, weight_acc, failed_units, ldm_real

# ==============================================================================
# 7. ANALITYKA INŻYNIERYJNA (TACTICAL LOAD BALANCER)
# ==============================================================================
def render_load_balance_analytics(veh, stacks):
    if not stacks: return
    t_moment, t_mass = 0, 0
    for s in stacks:
        for it in s['items']:
            cx_item = s['x'] + (it['w_fit'] / 2)
            t_moment += (cx_item * it['weight'])
            t_mass += it['weight']
    
    cog_x = t_moment / t_mass if t_mass > 0 else 0
    cog_p = (cog_x / veh['L']) * 100
    
    st.markdown("### ⚖️ CENTER OF GRAVITY ANALYSIS (CoG)")
    st.write(f"Położenie środka ciężkości ładunku: **{cog_x/100:.2f} m** od ściany przedniej")
    
    m_color = "#00FF41" if 35 < cog_p < 65 else "#FF3131"
    st.markdown(f"""
        <div class="v-cog-rail">
            <div class="v-cog-marker" style="left: {cog_p}%;"></div>
            <div style="position:absolute; left:15px; top:50px; font-size:0.6rem; color:#888;">CABIN AXLES</div>
            <div style="position:absolute; right:15px; top:50px; font-size:0.6rem; color:#888;">REAR AXLES</div>
        </div>
        <br><br>
    """, unsafe_allow_html=True)
    
    if cog_p < 35: st.error("DETEKCJA: PRZECIĄŻENIE OSI NAPĘDOWYCH. PRZESUŃ TOWAR NA TYŁ.")
    elif cog_p > 65: st.error("DETEKCJA: ODCIĄŻENIE OSI SKRĘTNEJ. PRZESUŃ TOWAR NA PRZÓD.")
    else: st.success("STATUS: ROZKŁAD MASY OPTYMALNY DLA STABILNOŚCI ZESTAWU.")

# ==============================================================================
# 8. SYSTEM DATA PERSISTENCE (DB ENGINE)
# ==============================================================================
def io_load_inventory():
    try:
        with open('products.json', 'r', encoding='utf-8') as f: return json.load(f)
    except: return []

def io_save_inventory(data):
    with open('products.json', 'w', encoding='utf-8') as f: 
        json.dump(data, f, indent=4, ensure_ascii=False)

# ==============================================================================
# 9. ARCHITEKTURA INTERFEJSU (VORTEZA STACK COMMAND)
# ==============================================================================
def main():
    inject_vorteza_css()
    if not authenticate_terminal(): return

    if 'v_manifest' not in st.session_state: st.session_state.v_manifest = []
    inventory = io_load_inventory()

    # Nagłówek systemowy
    hc1, hc2, hc3 = st.columns([1, 4, 1])
    with hc1:
        logo_b64 = get_resource_as_base64('logo_vorteza.png')
        if logo_b64: st.markdown(f'<img src="data:image/png;base64,{logo_b64}" width="160">', unsafe_allow_html=True)
        else: st.markdown("### VORTEZA")
    with hc2:
        st.markdown("<h1>VORTEZA STACK</h1>", unsafe_allow_html=True)
        st.markdown(f"<p class='v-version-tag'>ENGINEERING INTERFACE v17.0 | {datetime.now().strftime('%H:%M:%S')}</p>", unsafe_allow_html=True)
    with hc3:
        if st.button("KILL SESSION"):
            st.session_state.authorized = False; st.rerun()

    # Mission Control Sidebar
    with st.sidebar:
        st.markdown("### 📡 FLEET CONSOLE")
        v_key = st.selectbox("ACTIVE TRANSPORT UNIT", list(FLEET_REGISTRY.keys()))
        veh = FLEET_REGISTRY[v_key]
        st.divider()
        
        st.markdown("### 📥 MANIFEST CONTROL")
        p_names = [p['name'] for p in inventory]
        sel_sku = st.selectbox("SKU SELECTOR", p_names, index=None)
        
        if sel_sku:
            p_ref = next(p for p in inventory if p['name'] == sel_sku)
            ipc = p_ref.get('itemsPerCase', 1)
            rot = p_ref.get('allowRotation', True)
            st.markdown(f"""
                <div style='background:rgba(181,136,99,0.1); border:1px solid var(--v-copper); padding:18px; font-size:0.75rem;'>
                    SKU: {sel_sku}<br>STANDARD: {ipc} PCS/CASE<br>
                    OBRÓT: {'<span style="color:#00FF41">DOZWOLONY</span>' if rot else '<span style="color:#FF3131">BLOKADA</span>'}
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
        if st.button("PURGE ALL DATA"):
            st.session_state.v_manifest = []; st.rerun()

    # Workspace Tabs
    tab_p, tab_b, tab_i, tab_l = st.tabs(["📊 STACK PLANNER", "⚖️ LOAD BALANCER", "📦 PRODUCT CORE", "⚙️ SYSTEM LOGS"])

    with tab_p:
        if st.session_state.v_manifest:
            m1, m2, m3, m4 = st.columns(4)
            t_mass = sum(float(u['weight']) for u in st.session_state.v_manifest)
            m1.metric("CASES", len(st.session_state.v_manifest))
            m2.metric("PCS TOTAL", sum(int(u.get('p_act', 1)) for u in st.session_state.v_manifest))
            m3.metric("GROSS WEIGHT", f"{t_mass} KG")
            m4.metric("UTILIZATION", f"{(t_mass/veh['max_w'])*100:.1f}%")

            rem_manifest = [dict(u) for u in st.session_state.v_manifest]
            fleet = []
            while rem_manifest:
                res_s, res_w, n_p, ldm_r = V17StackEngine.execute_solve(rem_manifest, veh)
                if not res_s: st.error("UNIT OVERSIZE"); break
                fleet.append({"stacks": res_s, "weight": res_w, "ldm": ldm_r})
                rem_manifest = n_p

            for idx, truck in enumerate(fleet):
                st.markdown(f'<div class="v-stack-panel">', unsafe_allow_html=True)
                st.markdown(f"### UNIT #{idx+1} | {v_key}", unsafe_allow_html=True)
                v_col, d_col = st.columns([2.8, 1])
                with v_col: st.plotly_chart(render_stack_visualizer(veh, truck['stacks']), use_container_width=True)
                with d_col:
                    st.markdown("**OPERATIONAL KPI**")
                    st.write(f"Zajęte LDM: **{truck['ldm']:.2f} m**")
                    st.write(f"Masa Ładunku: **{truck['weight']} kg**")
                    st.divider()
                    st.markdown("**CARGO MANIFEST**")
                    agg = pd.Series([it['name'] for s in truck['stacks'] for it in s['items']]).value_counts().reset_index()
                    agg.columns = ['SKU', 'QTY']
                    ht = '<table class="v-data-table"><tr><th>SKU</th><th>QTY</th></tr>'
                    for _, r in agg.iterrows():
                        c = get_vorteza_product_color(r['SKU'])
                        ht += f'<tr><td><span style="color:{c}">■</span> {r["SKU"]}</td><td>{r["QTY"]}</td></tr>'
                    st.markdown(ht + '</table>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
        else: st.info("VORTEZA STACK: WAITING FOR INJECTION...")

    with tab_b:
        if st.session_state.v_manifest:
            st.markdown('<div class="v-stack-panel">', unsafe_allow_html=True)
            res_s, _, _, _ = V17StackEngine.execute_solve(st.session_state.v_manifest, veh)
            render_load_balance_analytics(veh, res_s)
            st.markdown('</div>', unsafe_allow_html=True)
        else: st.warning("NO DATA TO ANALYZE")

    with tab_i:
        st.markdown("### 📦 PRODUCT MASTER DATABASE")
        with st.expander("➕ REGISTER NEW ASSET"):
            with st.form("AddP"):
                fn = st.text_input("SKU Name")
                c1, c2, c3 = st.columns(3)
                fl, fw, fh = c1.number_input("L (cm)", 120), c2.number_input("W (cm)", 80), c3.number_input("H (cm)", 100)
                fm, fi = st.number_input("Mass (kg)", 50), st.number_input("IPU", 1)
                ca1, ca2 = st.columns(2)
                fs, fr = ca1.checkbox("Stacking Permission", True), ca2.checkbox("Rotation Permission", True)
                if st.form_submit_button("COMMIT TO MASTER DB"):
                    inventory.append({"name":fn,"length":fl,"width":fw,"height":fh,"weight":fm,"itemsPerCase":fi,"canStack":fs,"allowRotation":fr})
                    io_save_inventory(inventory); st.success("CORE SYNCED"); st.rerun()
        st.divider()
        if inventory:
            df_e = pd.DataFrame(inventory)
            edt = st.data_editor(df_e, use_container_width=True, num_rows="dynamic")
            if st.button("PUSH CHANGES TO CLOUD"):
                io_save_inventory(edt.to_dict('records')); st.success("CLOUD SYNC COMPLETE")

    with tab_l:
        st.code(f"SYSTEM SESSION: {datetime.now()}\nFIRM: VORTEZA\nAPP: STACK v17.0\nSTATUS: Nominal", language="bash")

if __name__ == "__main__":
    main()
