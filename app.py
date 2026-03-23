# -*- coding: utf-8 -*-
"""
================================================================================
SYSTEM: VORTEZA STACK 
VERSION: 21.0 | CORE ARCHITECT
FIRM: VORTEZA SYSTEMS
STATUS: ENTERPRISE READY | FULL SOURCE
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
# 1. INITIALIZATION & GLOBAL CONFIGURATION
# ==============================================================================
st.set_page_config(
    page_title="VORTEZA STACK v21.0",
    layout="wide",
    initial_sidebar_state="expanded",
    page_icon="🕋"
)

# REJESTR FLOTY VORTEZA (DANE INŻYNIERYJNE)
FLEET_DB = {
    "TIR Mega 13.6m": {
        "max_w": 24000, "L": 1360, "W": 248, "H": 300, 
        "ldm_max": 13.6, "axles": 3, "wheelbase": 850, "tare": 14500, "cab_l": 240
    },
    "TIR Standard 13.6m": {
        "max_w": 24000, "L": 1360, "W": 248, "H": 275, 
        "ldm_max": 13.6, "axles": 3, "wheelbase": 850, "tare": 13800, "cab_l": 240
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
# 2. BRANDING & STYLE ENGINE
# ==============================================================================
def get_base64_resource(path):
    try:
        if os.path.exists(path):
            with open(path, 'rb') as f:
                return base64.b64encode(f.read()).decode()
        return ""
    except: return ""

def apply_vorteza_pro_theme():
    bg_data = get_base64_resource('bg_vorteza.png')
    st.markdown(f"""
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;600;700&family=JetBrains+Mono:wght@300;400;500&display=swap');
            
            :root {{
                --v-copper: #B58863;
                --v-copper-glow: rgba(181, 136, 99, 0.4);
                --v-dark-obsidian: #050505;
                --v-panel-bg: rgba(10, 10, 10, 0.98);
                --v-border: rgba(181, 136, 99, 0.2);
            }}

            .stApp {{
                background-image: url("data:image/png;base64,{bg_data}");
                background-size: cover;
                background-attachment: fixed;
                color: #F8F8F8;
                font-family: 'Montserrat', sans-serif;
            }}

            /* TILE SYSTEM - DASHBOARD FIRST */
            .v-tile {{
                background: var(--v-panel-bg);
                padding: 2rem;
                border-radius: 2px;
                border: 1px solid var(--v-border);
                border-left: 10px solid var(--v-copper);
                box-shadow: 0 40px 100px rgba(0,0,0,0.9);
                margin-bottom: 2rem;
                backdrop-filter: blur(40px);
            }}

            section[data-testid="stSidebar"] {{
                background-color: rgba(4, 4, 4, 0.98) !important;
                border-right: 1px solid var(--v-border);
                width: 480px !important;
                backdrop-filter: blur(25px);
            }}

            h1, h2, h3 {{ 
                color: var(--v-copper) !important; 
                text-transform: uppercase; 
                letter-spacing: 8px !important; 
                font-weight: 700 !important; 
                text-shadow: 2px 2px 15px rgba(0,0,0,0.8);
            }}

            [data-testid="stMetricValue"] {{ 
                color: var(--v-copper) !important; 
                font-family: 'JetBrains Mono', monospace !important; 
                font-size: 3.5rem !important;
            }}

            .stButton > button {{
                background: linear-gradient(180deg, #0a0a0a, #151515);
                color: var(--v-copper);
                border: 1px solid var(--v-copper);
                padding: 1.4rem;
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
            }}
            .v-data-table td {{ 
                padding: 16px 18px; 
                border-bottom: 1px solid #1a1a1a; 
                color: #CCC; 
                font-size: 0.9rem; 
            }}

            .v-cog-rail {{
                width: 100%; height: 25px; background: #0a0a0a; border-radius: 12px; position: relative; border: 1px solid #333; margin: 40px 0;
            }}
            .v-cog-pointer {{
                position: absolute; width: 8px; height: 50px; top: -12.5px; background: #00FF41; box-shadow: 0 0 30px #00FF41; border-radius: 4px;
            }}
        </style>
    """, unsafe_allow_html=True)

# ==============================================================================
# 3. SECURITY PROTOCOL
# ==============================================================================
def check_system_access():
    if "authorized" not in st.session_state: st.session_state.authorized = False
    if not st.session_state.authorized:
        try: master_key = str(st.secrets.get("password", "vorteza2026"))
        except: master_key = "vorteza2026"
        st.markdown("<br><br><br><br><br>", unsafe_allow_html=True)
        _, col, _ = st.columns([1, 1.8, 1])
        with col:
            with st.form("VortezaAuthGate"):
                st.markdown("<h2 style='text-align:center;'>VORTEZA STACK</h2>", unsafe_allow_html=True)
                pwd_in = st.text_input("GOLIATH MASTER AUTHENTICATION KEY", type="password")
                if st.form_submit_button("VALIDATE SECURITY CLEARANCE"):
                    if pwd_in == master_key:
                        st.session_state.authorized = True
                        st.rerun()
                    else: st.error("ACCESS DENIED")
        return False
    return True

# ==============================================================================
# 4. DATA PERSISTENCE & CORE UTILS
# ==============================================================================
def load_vorteza_inventory():
    if os.path.exists('products.json'):
        with open('products.json', 'r', encoding='utf-8') as f: return json.load(f)
    return []

def save_vorteza_inventory(data):
    with open('products.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def get_chromatic_sku_color(sku_name):
    palette = ["#B58863", "#D4AF37", "#8E6A4D", "#5E4633", "#A67C52", "#2C3E50", "#34495E", "#1A252F", "#16A085", "#27AE60", "#7F8C8D", "#95A5A6", "#BDC3C7", "#7E4A35"]
    random.seed(sum(ord(c) for c in sku_name))
    return random.choice(palette)

# ==============================================================================
# 5. CORE ENGINES (PACKING & VISUALS)
# ==============================================================================
class V21StackEngine:
    @staticmethod
    def solve(cargo, veh, x_offset=0):
        items = sorted(cargo, key=lambda x: (not x.get('canStack', True), not x.get('allowRotation', True), x['width']*x['length']), reverse=True)
        stacks, failed, weight_acc = [], [], 0
        cx, cy, current_row_max_w = x_offset, 0, 0

        for unit in items:
            if weight_acc + unit['weight'] > veh['max_w']:
                failed.append(unit); continue
            
            # STACKING PROTOCOL
            stacked = False
            if unit.get('canStack', True):
                for s in stacks:
                    rot_p = unit.get('allowRotation', True)
                    fit = (unit['width'] <= s['w'] and unit['length'] <= s['l']) or (unit['length'] <= s['w'] and unit['width'] <= s['l']) if rot_p else (unit['width'] <= s['w'] and unit['length'] <= s['l'])
                    if fit and (s['curH'] + unit['height'] <= veh['H']):
                        u_c = unit.copy(); u_c['z'] = s['curH']; u_c['w_fit'], u_c['l_fit'] = s['w'], s['l']
                        s['items'].append(u_c); s['curH'] += unit['height']; weight_acc += unit['weight']; stacked = True; break
            
            if stacked: continue

            # FLOOR PROTOCOL
            placed = False
            rots = [(unit['width'], unit['length']), (unit['length'], unit['width'])] if unit.get('allowRotation', True) else [(unit['width'], unit['length'])]
            for fw, fl in rots:
                if cy + fl <= veh['W'] and cx + fw <= veh['L']:
                    u_c = unit.copy(); u_c['z'] = 0; u_c['w_fit'], u_c['l_fit'] = fw, fl
                    stacks.append({'x':cx, 'y':cy, 'w':fw, 'l':fl, 'curH':unit['height'], 'items':[u_c]})
                    cy += fl; current_row_max_w = max(current_row_max_w, fw); weight_acc += unit['weight']; placed = True; break
                elif cx + current_row_max_w + fw <= veh['L'] and fl <= veh['W']:
                    cx += current_row_max_w; cy = 0; current_row_max_w = fw
                    u_c = unit.copy(); u_c['z'] = 0; u_c['w_fit'], u_c['l_fit'] = fw, fl
                    stacks.append({'x':cx, 'y':cy, 'w':fw, 'l':fl, 'curH':unit['height'], 'items':[u_c]})
                    cy += fl; weight_acc += unit['weight']; placed = True; break
            if not placed: failed.append(unit)
        
        ldm = (max([s['x'] + s['w'] for s in stacks]) / 100) if stacks else 0
        return stacks, weight_acc, failed, ldm

def render_vorteza_cad_pro(veh, stacks):
    fig = go.Figure()
    L, W, H = veh['L'], veh['W'], veh['H']
    
    # CHASSIS & FLOOR
    fig.add_trace(go.Mesh3d(x=[0,L,L,0], y=[0,0,W,W], z=[-15,-15,-15,-15], color='#101010', opacity=1, hoverinfo='skip'))
    
    # CABIN
    c_l = veh.get('cab_l', 240)
    fig.add_trace(go.Mesh3d(x=[-c_l,0,0,-c_l], y=[-40,-40,W+40,W+40], z=[0,0,H*1.05,H*1.05], color='#020202', opacity=1, name="CORE_CABIN"))

    # SKELETON (COPPER)
    edges = [([0,L],[0,0],[0,0]), ([0,L],[W,W],[0,0]), ([0,0],[0,W],[0,0]), ([L,L],[0,W],[0,0]),
             ([0,0],[0,0],[0,H]), ([0,0],[W,W],[0,H]), ([0,L],[0,0],[H,H]), ([0,L],[W,W],[H,H])]
    for ex, ey, ez in edges:
        fig.add_trace(go.Scatter3d(x=ex, y=ey, z=ez, mode='lines', line=dict(color='#B58863', width=12), hoverinfo='skip'))

    # WHEELS
    ax_start = L - 400 if L > 800 else L - 180
    for i in range(veh.get('ax', 3)):
        px = ax_start + (i * 145)
        if px < L:
            for side in [-38, W+22]:
                fig.add_trace(go.Mesh3d(x=[px-55, px+55, px+55, px-55], y=[side, side, side+18, side+18], z=[-75, -75, -15, -15], color='#000', opacity=1, hoverinfo='skip'))
                fig.add_trace(go.Mesh3d(x=[px-22, px+22, px+22, px-22], y=[side-2, side-2, side, side], z=[-55, -55, -35, -35], color='#B58863', opacity=0.9, hoverinfo='skip'))

    # CARGO
    for s in stacks:
        for it in s['items']:
            x, y, z = s['x'], s['y'], it['z']
            dx, dy, dz = it['w_fit'], it['l_fit'], it['height']
            clr = get_chromatic_sku_color(it['name'])
            fig.add_trace(go.Mesh3d(x=[x,x+dx,x+dx,x,x,x+dx,x+dx,x], y=[y,y,y+dy,y+dy,y,y,y+dy,y+dy], z=[z,z,z+dz,z+dz,z,z,z+dz,z+dz],
                                   i=[7,0,0,0,4,4,6,6,4,0,3,2], j=[3,4,1,2,5,6,5,2,0,1,6,3], k=[0,7,2,3,6,7,1,1,5,5,7,6], color=clr, opacity=0.98, name=it['name']))
            fig.add_trace(go.Scatter3d(x=[x,x+dx,x+dx,x,x,x+dx,x+dx,x,x,x+dx,x+dx,x+dx,x+dx,x,x], y=[y,y,y+dy,y+dy,y,y,y+dy,y+dy,y+dy,y+dy,y+dy,y,y,y+dy,y+dy,y],
                                     z=[z,z,z+dz,z+dz,z,z,z+dz,z+dz,z+dz,z+dz,z+dz,z,z,z+dz,z+dz], mode='lines', line=dict(color='black', width=3), hoverinfo='skip'))

    fig.update_layout(scene=dict(aspectmode='data', xaxis_visible=False, yaxis_visible=False, zaxis_visible=False, camera=dict(eye=dict(x=2.5, y=2.5, z=2.0))), 
                      paper_bgcolor='rgba(0,0,0,0)', margin=dict(l=0, r=0, b=0, t=0), showlegend=False)
    return fig

# ==============================================================================
# 6. MAIN APPLICATION WORKFLOW
# ==============================================================================
def main():
    apply_vorteza_pro_theme()
    if not check_system_access(): return

    if 'manifest' not in st.session_state: st.session_state.manifest = []
    inventory = load_vorteza_inventory()

    # HEADER SYSTEM
    h_col1, h_col2 = st.columns([5, 1])
    with h_col1:
        logo_b64 = get_base64('logo_vorteza.png')
        if logo_b64: st.markdown(f'<img src="data:image/png;base64,{logo_b64}" width="220">', unsafe_allow_html=True)
        else: st.markdown("<h1>VORTEZA STACK</h1>", unsafe_allow_html=True)
    with h_col2:
        if st.button("TERMINATE SESSION"): st.session_state.authorized = False; st.rerun()

    # SIDEBAR CONTROL COCKPIT
    with st.sidebar:
        st.markdown("### 📡 FLEET COMMAND")
        v_key = st.selectbox("ACTIVE TRANSPORT UNIT", list(FLEET_DB.keys()))
        veh = FLEET_DB[v_key]
        
        st.divider()
        st.markdown("### ⚖️ LOAD BALANCING")
        x_off = st.slider("FRONT OFFSET (cm)", 0, veh['L']-200, 0)
        
        st.divider()
        st.markdown("### 📥 MISSION MANIFEST")
        sel_sku = st.selectbox("SKU SELECTOR", [p['name'] for p in inventory], index=None)
        if sel_sku:
            p_ref = next(p for p in inventory if p['name'] == sel_sku)
            ipc = p_ref.get('itemsPerCase', 1)
            st.markdown(f"<div style='background:rgba(181,136,99,0.1); border:1px solid var(--v-copper); padding:15px; font-size:0.75rem;'><b>SKU:</b> {sel_sku}<br><b>UNIT:</b> {ipc} PCS<br><b>ROTATION:</b> {'AUTHORIZED' if p_ref.get('allowRotation') else 'LOCKED'}</div>", unsafe_allow_html=True)
            qty = st.number_input("QUANTITY (TOTAL PCS)", min_value=1, value=ipc)
            if st.button("APPEND TO MANIFEST", type="primary"):
                n_units = math.ceil(qty / ipc)
                for i in range(n_units):
                    u = p_ref.copy()
                    u['p_act'] = ipc if (i < n_units-1 or qty % ipc == 0) else (qty % ipc)
                    st.session_state.manifest.append(u)
                st.rerun()
        if st.button("PURGE ALL DATA"): st.session_state.manifest = []; st.rerun()

    # TABS SYSTEM
    tab_op, tab_db = st.tabs(["🚀 OPERATION DASHBOARD", "📦 MASTER INVENTORY"])

    with tab_op:
        if st.session_state.manifest:
            # DASHBOARD KPI
            k1, k2, k3, k4 = st.columns(4)
            t_w = sum(float(u['weight']) for u in st.session_state.manifest)
            k1.metric("CASES", len(st.session_state.manifest))
            k2.metric("PCS TOTAL", sum(int(u.get('p_act', 1)) for u in st.session_state.manifest))
            k3.metric("GROSS MASS", f"{t_w} KG")
            k4.metric("UTILIZATION", f"{(t_w/veh['max_w'])*100:.1f}%")

            # CORE CALCULATION
            rem = [dict(u) for u in st.session_state.manifest]
            fleet = []
            while rem:
                res_s, res_w, n_p, ldm_r = StackEngineV21.pack(rem, veh, offset=x_off)
                if not res_s: st.error("CRITICAL: UNIT OVERSIZE DETECTED"); break
                fleet.append({"s": res_s, "w": res_w, "l": ldm_r})
                rem = n_p

            # RENDERING PER UNIT
            for i, truck in enumerate(fleet):
                st.markdown(f'<div class="v-tile">', unsafe_allow_html=True)
                st.markdown(f"### MISSION UNIT #{i+1} | {v_key}")
                
                v_col, d_col = st.columns([2.5, 1])
                with v_col: st.plotly_chart(render_vorteza_cad_pro(veh, truck['s']), use_container_width=True)
                with d_col:
                    st.markdown("**OPERATIONAL KPI**")
                    st.write(f"Zajęte LDM: **{truck['l']:.2f} m**")
                    st.write(f"Masa Netto: **{truck['w']} kg**")
                    
                    st.divider()
                    st.markdown("**CENTER OF GRAVITY (CoG)**")
                    t_mom, t_mass = 0, 0
                    for s in truck['s']:
                        for it in s['items']:
                            t_mom += (s['x'] + it['w_fit']/2) * it['weight']
                            t_mass += it['weight']
                    cog_p = (t_mom / t_mass / veh['L']) * 100 if t_mass > 0 else 0
                    st.markdown(f'<div class="v-cog-rail"><div class="v-cog-pointer" style="left:{cog_p}%;"></div></div>', unsafe_allow_html=True)
                    if cog_p < 35: st.error("AXLE OVERLOAD RISK (FRONT)")
                    elif cog_p > 65: st.error("STEERING INSTABILITY RISK (REAR)")
                    else: st.success("BALANCE NOMINAL")
                
                with st.expander("VIEW DETAILED PACKING LIST"):
                    df_agg = pd.Series([it['name'] for s in truck['s'] for it in s['items']]).value_counts().reset_index()
                    df_agg.columns = ['SKU', 'QTY']
                    st.table(df_agg)
                st.markdown('</div>', unsafe_allow_html=True)
        else: st.info("VORTEZA STACK: WAITING FOR MISSION DATA. INJECT CARGO VIA SIDEBAR.")

    with tab_db:
        st.markdown("### 📦 GLOBAL PRODUCT ARCHIVE")
        df_inv = pd.DataFrame(inventory)
        if not df_inv.empty:
            edt = st.data_editor(df_inv, use_container_width=True, num_rows="dynamic", key="v_editor")
            if st.button("SYNC MASTER DATABASE", type="primary"):
                save_vorteza_inventory(edt.to_dict('records'))
                st.success("PROTOCOL SUCCESS: Database synchronized.")
        
        st.divider()
        with st.expander("➕ REGISTER NEW SKU TO ARCHIVE"):
            with st.form("NewSKU"):
                fn = st.text_input("SKU Name / Identifier")
                c1, c2, c3 = st.columns(3)
                fl, fw, fh = c1.number_input("L (cm)", 120), c2.number_input("W (cm)", 80), c3.number_input("H (cm)", 100)
                col_w, col_i = st.columns(2)
                fm = col_w.number_input("Mass (kg)", 100)
                fi = col_i.number_input("Items Per Case (IPC)", 1)
                stk, rot = st.checkbox("Stacking Permission", True), st.checkbox("Rotation Permission", True)
                if st.form_submit_button("COMMIT TO CORE"):
                    inventory.append({"name":fn,"length":fl,"width":fw,"height":fh,"weight":fm,"itemsPerCase":fi,"canStack":stk,"allowRotation":rot})
                    save_vorteza_inventory(inventory); st.rerun()

if __name__ == "__main__":
    main()
