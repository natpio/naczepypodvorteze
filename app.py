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
from PIL import Image

st.set_page_config(
    page_title="VORTEZA STACK v16.0",
    layout="wide",
    initial_sidebar_state="expanded",
    page_icon="🕋"
)

FLEET_REGISTRY = {
    "TIR FTL (Mega 13.6m)": {
        "max_w": 24000, "L": 1360, "W": 248, "H": 300, 
        "ldm": 13.6, "axles": 3, "wheelbase": 850, "tare": 14500, "type": "FTL"
    },
    "TIR FTL (Standard 13.6m)": {
        "max_w": 24000, "L": 1360, "W": 248, "H": 275, 
        "ldm": 13.6, "axles": 3, "wheelbase": 850, "tare": 13800, "type": "FTL"
    },
    "Solo 9m (Heavy)": {
        "max_w": 9500, "L": 920, "W": 245, "H": 270, 
        "ldm": 9.2, "axles": 2, "wheelbase": 550, "tare": 8500, "type": "SOLO"
    },
    "Solo 7m (Medium)": {
        "max_w": 7000, "L": 720, "W": 245, "H": 260, 
        "ldm": 7.2, "axles": 2, "wheelbase": 480, "tare": 6200, "type": "SOLO"
    },
    "BUS XL (Express)": {
        "max_w": 1250, "L": 485, "W": 175, "H": 220, 
        "ldm": 4.8, "axles": 2, "wheelbase": 320, "tare": 2250, "type": "BUS"
    }
}

def get_bin_base64(bin_file):
    try:
        with open(bin_file, 'rb') as f:
            return base64.b64encode(f.read()).decode()
    except:
        return ""

def apply_vorteza_stack_theme():
    bg_b64 = get_bin_base64('bg_vorteza.png')
    st.markdown(f"""
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;600;700&family=JetBrains+Mono:wght@300;400;500&display=swap');
            
            .stApp {{
                background-image: url("data:image/png;base64,{bg_b64}");
                background-size: cover;
                background-attachment: fixed;
                color: #FFFFFF;
                font-family: 'Montserrat', sans-serif;
            }}
            
            :root {{
                --v-copper: #B58863;
                --v-dark-glass: rgba(8, 8, 8, 0.98);
                --v-border: rgba(181, 136, 99, 0.25);
            }}

            .v-panel {{
                background: var(--v-dark-glass);
                padding: 3rem;
                border: 1px solid var(--v-border);
                border-left: 15px solid var(--v-copper);
                box-shadow: 0 50px 150px rgba(0,0,0,0.95);
                margin-bottom: 4rem;
                backdrop-filter: blur(45px);
            }}

            section[data-testid="stSidebar"] {{
                background-color: rgba(4, 4, 4, 0.95) !important;
                border-right: 1px solid var(--v-border);
                backdrop-filter: blur(25px);
                width: 500px !important;
            }}

            h1, h2, h3 {{ color: var(--v-copper) !important; text-transform: uppercase; letter-spacing: 12px !important; font-weight: 700 !important; }}
            
            [data-testid="stMetricValue"] {{ 
                color: var(--v-copper) !important; 
                font-family: 'JetBrains Mono', monospace !important; 
                font-size: 3.8rem !important;
                text-shadow: 0 0 20px rgba(181, 136, 99, 0.3);
            }}

            .stButton > button {{
                background: linear-gradient(180deg, #0a0a0a, #1a1a1a);
                color: var(--v-copper);
                border: 1px solid var(--v-copper);
                padding: 1.5rem;
                text-transform: uppercase;
                letter-spacing: 8px;
                font-weight: 700;
                width: 100%;
                transition: 0.7s all;
                border-radius: 0;
            }}
            .stButton > button:hover {{
                background: var(--v-copper);
                color: black;
                box-shadow: 0 0 100px rgba(181, 136, 99, 1);
                transform: translateY(-5px);
            }}

            .v-table {{ width: 100%; border-collapse: collapse; margin-top: 40px; border: 1px solid #1a1a1a; }}
            .v-table th {{ background: #000; color: var(--v-copper); text-align: left; font-size: 0.8rem; text-transform: uppercase; border-bottom: 2px solid #333; padding: 25px; letter-spacing: 3px; }}
            .v-table td {{ padding: 20px 25px; border-bottom: 1px solid #111; color: #CCC; font-size: 0.95rem; }}
            
            .v-balance-container {{ width: 100%; background: #111; height: 40px; border-radius: 20px; position: relative; border: 1px solid #333; margin: 30px 0; }}
            .v-cog-indicator {{ position: absolute; width: 8px; height: 60px; top: -10px; background: #00FF41; box-shadow: 0 0 25px #00FF41; border-radius: 4px; }}
        </style>
    """, unsafe_allow_html=True)

def check_system_auth():
    if "v_auth" not in st.session_state:
        st.session_state.v_auth = False

    if not st.session_state.v_auth:
        try:
            pwd_master = str(st.secrets.get("password", "vorteza2026"))
        except:
            pwd_master = "vorteza2026"

        st.markdown("<br><br><br><br><br><br>", unsafe_allow_html=True)
        _, col, _ = st.columns([1, 1.8, 1])
        with col:
            with st.form("StackAuth"):
                st.markdown("<h2 style='text-align:center;'>VORTEZA STACK</h2>", unsafe_allow_html=True)
                st.markdown("<p style='text-align:center; color:#444; font-size:0.75rem; letter-spacing:6px;'>ENCRYPTED ACCESS</p>", unsafe_allow_html=True)
                u_input = st.text_input("ACCESS KEY", type="password")
                if st.form_submit_button("VALIDATE CLEARANCE"):
                    if u_input == pwd_master:
                        st.session_state.v_auth = True
                        st.rerun()
                    else:
                        st.error("INVALID KEY")
        return False
    return True

def get_product_color_hex(name):
    palette = [
        "#B58863", "#D4AF37", "#8E6A4D", "#5E4633", "#A67C52", 
        "#2C3E50", "#34495E", "#1A252F", "#16A085", "#27AE60",
        "#7F8C8D", "#95A5A6", "#BDC3C7", "#E67E22", "#D35400",
        "#C0392B", "#E74C3C", "#8E44AD", "#9B59B6", "#2980B9"
    ]
    random.seed(sum(ord(c) for c in name))
    return random.choice(palette)

class V16Engine:
    @staticmethod
    def pack(cargo, vehicle):
        items = sorted(cargo, key=lambda x: (not x.get('canStack', True), not x.get('allowRotation', True), x['width']*x['length']), reverse=True)
        
        stacks, failed, mass_sum = [], [], 0
        cx, cy, row_max_w = 0, 0, 0

        for unit in items:
            if mass_sum + unit['weight'] > vehicle['max_w']:
                failed.append(unit); continue
            
            is_stacked = False
            if unit.get('canStack', True):
                for s in stacks:
                    if unit.get('allowRotation', True):
                        fit = (unit['width'] <= s['w'] and unit['length'] <= s['l']) or (unit['length'] <= s['w'] and unit['width'] <= s['l'])
                    else:
                        fit = (unit['width'] <= s['w'] and unit['length'] <= s['l'])
                    
                    if fit and (s['curH'] + unit['height'] <= vehicle['H']):
                        u_copy = unit.copy(); u_copy['z'] = s['curH']
                        u_copy['w_fit'], u_copy['l_fit'] = s['w'], s['l']
                        s['items'].append(u_copy); s['curH'] += unit['height']
                        mass_sum += unit['weight']; is_stacked = True; break
            
            if is_stacked: continue

            placed_floor = False
            rots = [(unit['width'], unit['length']), (unit['length'], unit['width'])] if unit.get('allowRotation', True) else [(unit['width'], unit['length'])]
            
            for fw, fl in rots:
                if cy + fl <= vehicle['W'] and cx + fw <= vehicle['L']:
                    u_c = unit.copy(); u_c['z'] = 0; u_c['w_fit'], u_c['l_fit'] = fw, fl
                    stacks.append({'x':cx, 'y':cy, 'w':fw, 'l':fl, 'curH':unit['height'], 'items':[u_c]})
                    cy += fl; row_max_w = max(row_max_w, fw); mass_sum += unit['weight']; placed_floor = True; break
                elif cx + row_max_w + fw <= vehicle['L'] and fl <= vehicle['W']:
                    cx += row_max_w; cy = 0; row_max_w = fw
                    u_c = unit.copy(); u_c['z'] = 0; u_c['w_fit'], u_c['l_fit'] = fw, fl
                    stacks.append({'x':cx, 'y':cy, 'w':fw, 'l':fl, 'curH':unit['height'], 'items':[u_c]})
                    cy += fl; mass_sum += unit['weight']; placed_floor = True; break
            
            if not placed_floor: failed.append(unit)

        ldm = (max([s['x'] + s['w'] for s in stacks]) / 100) if stacks else 0
        return stacks, mass_sum, failed, ldm

def render_vorteza_cad_3d(veh, stacks):
    fig = go.Figure()
    L, W, H = veh['L'], veh['W'], veh['H']

    # CHASSIS
    fig.add_trace(go.Mesh3d(x=[0, L, L, 0], y=[0, 0, W, W], z=[-15, -15, -15, -15], color='#111', opacity=1, hoverinfo='skip'))
    
    # WHEELS & AXLES
    ax_count = veh.get('axles', 3)
    ax_start = L - 380 if L > 700 else L - 180
    for i in range(ax_count):
        px = ax_start + (i * 140)
        if px < L:
            for side in [-38, W+20]:
                fig.add_trace(go.Mesh3d(x=[px-55, px+55, px+55, px-55], y=[side, side, side+18, side+18], z=[-70, -70, -15, -15], color='#000', opacity=1, hoverinfo='skip'))
                fig.add_trace(go.Mesh3d(x=[px-22, px+22, px+22, px-22], y=[side-2, side-2, side, side], z=[-50, -50, -30, -30], color='#B58863', opacity=0.9, hoverinfo='skip'))

    # CABIN MESH
    fig.add_trace(go.Mesh3d(x=[-240, 0, 0, -240, -240, 0, 0, -240], y=[-35, -35, W+35, W+35, -35, -35, W+35, W+35], z=[0, 0, 0, 0, H*1.05, H*1.05, H*1.05, H*1.05], i=[7,0,0,0,4,4,6,6,4,0,3,2], j=[3,4,1,2,5,6,5,2,0,1,6,3], k=[0,7,2,3,6,7,1,1,5,5,7,6], color='#030303', opacity=1, name="CABIN_CORE"))
    
    # SKELETON
    edges = [([0, L], [0, 0], [0, 0]), ([0, L], [W, W], [0, 0]), ([0, 0], [0, W], [0, 0]), ([L, L], [0, W], [0, 0]),
             ([0, 0], [0, 0], [0, H]), ([0, 0], [W, W], [0, H]), ([0, L], [0, 0], [H, H]), ([0, L], [W, W], [H, H]),
             ([L, L], [0, 0], [0, H]), ([L, L], [W, W], [0, H])]
    for ex, ey, ez in edges:
        fig.add_trace(go.Scatter3d(x=ex, y=ey, z=ez, mode='lines', line=dict(color='#B58863', width=12), hoverinfo='skip'))

    # CARGO CLUSTERS
    for s in stacks:
        for it in s['items']:
            x, y, z = s['x'], s['y'], it['z']
            dx, dy, dz = it['w_fit'], it['l_fit'], it['height']
            fig.add_trace(go.Mesh3d(
                x=[x,x+dx,x+dx,x,x,x+dx,x+dx,x], y=[y,y,y+dy,y+dy,y,y,y+dy,y+dy], z=[z,z,z+dz,z+dz,z,z,z+dz,z+dz],
                i=[7,0,0,0,4,4,6,6,4,0,3,2], j=[3,4,1,2,5,6,5,2,0,1,6,3], k=[0,7,2,3,6,7,1,1,5,5,7,6],
                color=get_product_color_hex(it['name']), opacity=0.98, name=it['name']
            ))
            fig.add_trace(go.Scatter3d(
                x=[x,x+dx,x+dx,x,x,x+dx,x+dx,x,x,x+dx,x+dx,x+dx,x+dx,x,x],
                y=[y,y,y+dy,y+dy,y,y,y,y+dy,y+dy,y+dy,y+dy,y,y,y+dy,y+dy,y],
                z=[z,z,z,z,z,z+dz,z+dz,z,z,z+dz,z+dz,z+dz,z,z,z+dz,z+dz],
                mode='lines', line=dict(color='black', width=3), hoverinfo='skip'
            ))

    fig.update_layout(scene=dict(aspectmode='data', xaxis_visible=False, yaxis_visible=False, zaxis_visible=False, camera=dict(eye=dict(x=2.5, y=2.5, z=2.0))), paper_bgcolor='rgba(0,0,0,0)', margin=dict(l=0, r=0, b=0, t=0), showlegend=False)
    return fig

def run_load_bal_logic(veh, stacks):
    if not stacks: return
    t_moment, t_weight = 0, 0
    for s in stacks:
        for it in s['items']:
            item_cx = s['x'] + (it['w_fit'] / 2)
            t_moment += (item_cx * it['weight'])
            t_weight += it['weight']
    cog_x = t_moment / t_weight if t_weight > 0 else 0
    cog_p = (cog_x / veh['L']) * 100
    st.markdown("### ⚖️ CENTER OF GRAVITY ANALYSIS")
    st.write(f"V-COG Position: **{cog_x/100:.2f} m** from front wall")
    marker_color = "#00FF41" if 35 < cog_p < 65 else "#FF3131"
    st.markdown(f"""
        <div class="v-balance-container">
            <div class="v-cog-indicator" style="left: {cog_p}%;"></div>
            <div style="position:absolute; left:20px; top:45px; font-size:0.65rem; color:#666;">AXLE FRONT</div>
            <div style="position:absolute; right:20px; top:45px; font-size:0.65rem; color:#666;">AXLE REAR</div>
        </div>
        <br><br>
    """, unsafe_allow_html=True)
    if cog_p < 35: st.error("DANGER: EXCESSIVE FRONT LOAD. AXLE OVERLOAD RISK.")
    elif cog_p > 65: st.error("DANGER: EXCESSIVE REAR LOAD. STEERING INSTABILITY.")
    else: st.success("NOMINAL: MASS DISTRIBUTION OPTIMIZED.")

def main():
    apply_vorteza_stack_ui = apply_vorteza_stack_theme()
    if not check_system_auth(): return

    if 'v_manifest' not in st.session_state: st.session_state.v_manifest = []
    
    try:
        with open('products.json', 'r', encoding='utf-8') as f: inv_db = json.load(f)
    except: inv_db = []

    h_col1, h_col2, h_col3 = st.columns([1, 4, 1])
    with h_col1:
        try: st.image('logo_vorteza.png', width=180)
        except: st.markdown("### VORTEZA")
    with h_col2:
        st.markdown("<h1>VORTEZA STACK</h1>", unsafe_allow_html=True)
        st.markdown(f"<p class='v-version-tag'>v16.0 | SYSTEM NOMINAL | {datetime.now().strftime('%H:%M')}</p>", unsafe_allow_html=True)
    with h_col3:
        if st.button("KILL SESSION"):
            st.session_state.v_auth = False; st.rerun()

    with st.sidebar:
        st.markdown("### 📡 FLEET CONSOLE")
        v_key = st.selectbox("ACTIVE TRANSPORT UNIT", list(FLEET_REGISTRY.keys()))
        veh = FLEET_REGISTRY[v_key]
        
        st.divider()
        st.markdown("### 📥 MANIFEST CONTROL")
        sku_list = [p['name'] for p in inv_db]
        sel_sku = st.selectbox("SKU SELECTOR", sku_list, index=None)
        
        if sel_sku:
            p_ref = next(p for p in inv_db if p['name'] == sel_sku)
            ipc = p_ref.get('itemsPerCase', 1)
            rot = p_ref.get('allowRotation', True)
            st.markdown(f"""
                <div style='background:rgba(181,136,99,0.1); border:1px solid var(--v-copper); padding:18px; font-size:0.75rem;'>
                    SKU: {sel_sku}<br>
                    IPU: {ipc} PCS/UNIT<br>
                    ROTATION: {'<span style="color:#00FF41">AUTHORIZED</span>' if rot else '<span style="color:#FF3131">LOCKED</span>'}
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

    t_plan, t_bal, t_inv, t_log = st.tabs(["📊 PLANNER", "⚖️ LOAD BALANCER", "📦 PRODUCT CORE", "⚙️ TERMINAL"])

    with t_plan:
        if st.session_state.v_manifest:
            k1, k2, k3, k4 = st.columns(4)
            total_m = sum(float(u['weight']) for u in st.session_state.v_manifest)
            k1.metric("UNITS", len(st.session_state.v_manifest))
            k2.metric("PCS TOTAL", sum(int(u.get('p_act', 1)) for u in st.session_state.v_manifest))
            k3.metric("GROSS MASS", f"{total_m} KG")
            k4.metric("UTILIZATION", f"{(total_m/veh['max_w'])*100:.1f}%")

            rem_manifest = [dict(u) for u in st.session_state.v_manifest]
            fleet = []
            while rem_manifest:
                res_s, res_w, n_p, ldm_r = V16Engine.pack(rem_manifest, veh)
                if not res_s: 
                    st.error("LOGISTICS FAILURE: UNIT OVERSIZE."); break
                fleet.append({"stacks": res_s, "weight": res_w, "ldm": ldm_r})
                rem_manifest = n_p

            for i, unit in enumerate(fleet):
                st.markdown(f'<div class="v-panel">', unsafe_allow_html=True)
                st.markdown(f"### UNIT #{i+1} | {v_key}", unsafe_allow_html=True)
                v_col, d_col = st.columns([2.8, 1])
                with v_col: st.plotly_chart(render_vorteza_cad_3d(veh, unit['stacks']), use_container_width=True)
                with d_col:
                    st.markdown("**OPERATIONAL KPI**")
                    st.write(f"Occupied LDM: **{unit['ldm']:.2f} m**")
                    st.write(f"Mass: **{unit['weight']} kg**")
                    st.divider()
                    st.markdown("**MANIFEST DATA**")
                    agg = pd.Series([it['name'] for s in unit['stacks'] for it in s['items']]).value_counts().reset_index()
                    agg.columns = ['SKU', 'QTY']
                    h_table = '<table class="v-table"><tr><th>SKU</th><th>QTY</th></tr>'
                    for _, r in agg.iterrows():
                        c = get_product_color_hex(r['SKU'])
                        h_table += f'<tr><td><span style="color:{c}">■</span> {r["SKU"]}</td><td>{r["QTY"]}</td></tr>'
                    st.markdown(h_table + '</table>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
        else: st.info("VORTEZA STACK: WAITING FOR MANIFEST...")

    with t_bal:
        if st.session_state.v_manifest:
            st.markdown('<div class="v-panel">', unsafe_allow_html=True)
            res_s, _, _, _ = V16Engine.pack(st.session_state.v_manifest, veh)
            run_load_bal_logic(veh, res_s)
            st.markdown('</div>', unsafe_allow_html=True)
        else: st.warning("NO MANIFEST DATA DETECTED.")

    with t_inv:
        st.markdown("### 📦 PRODUCT ARCHITECTURE ADMIN")
        with st.expander("➕ REGISTER NEW CARGO ASSET"):
            with st.form("AddP"):
                fn = st.text_input("Product Name")
                c1, c2, c3 = st.columns(3)
                fl, fw, fh = c1.number_input("L", 120), c2.number_input("W", 80), c3.number_input("H", 100)
                fm, fi = st.number_input("Weight", 100), st.number_input("IPU", 1)
                ca1, ca2 = st.columns(2)
                fs, fr = ca1.checkbox("Stackable", True), ca2.checkbox("Rotatable", True)
                if st.form_submit_button("COMMIT TO CORE"):
                    inv_db.append({"name":fn,"length":fl,"width":fw,"height":fh,"weight":fm,"itemsPerCase":fi,"canStack":fs,"allowRotation":fr})
                    with open('products.json', 'w', encoding='utf-8') as f: json.dump(inv_db, f, indent=4, ensure_ascii=False)
                    st.success("CORE SYNCED"); st.rerun()

        st.divider()
        if inv_db:
            df_e = pd.DataFrame(inv_db)
            edt = st.data_editor(df_e, use_container_width=True, num_rows="dynamic")
            if st.button("PUSH CHANGES TO CLOUD"):
                with open('products.json', 'w', encoding='utf-8') as f: 
                    json.dump(edt.to_dict('records'), f, indent=4, ensure_ascii=False)
                st.success("CLOUD SYNC COMPLETE")

    with t_log:
        st.code(f"VORTEZA STACK v16.0 | SESSION_START: {datetime.now()}\nSTATUS: Nominal\nCORE_VERSION: Titan-v16", language="bash")

if __name__ == "__main__":
    main()
