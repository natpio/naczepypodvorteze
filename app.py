import streamlit as st
import json
import plotly.graph_objects as go
import math
import pandas as pd
import numpy as np

# --- 1. CONFIG & ULTRA-DARK THEME ---
st.set_page_config(
    page_title="SQM LOGISTICS COMMAND", 
    page_icon="⚡", 
    layout="wide", 
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&family=Inter:wght@400;800&display=swap');
    
    :root {
        --neon-blue: #00f2ff;
        --neon-red: #ff0055;
        --bg-dark: #020617;
        --card-bg: #0f172a;
    }

    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    .main { background-color: var(--bg-dark); color: #e2e8f0; }
    
    /* Neonowe metryki */
    div[data-testid="stMetricValue"] {
        font-family: 'JetBrains Mono', monospace;
        color: var(--neon-blue) !important;
        text-shadow: 0 0 10px rgba(0, 242, 255, 0.5);
        font-size: 32px !important;
    }
    
    /* Karty kontenerów */
    .st-emotion-cache-12w0u9p {
        background-color: var(--card-bg) !important;
        border: 1px solid #1e293b !important;
        border-radius: 20px !important;
        box-shadow: 0 10px 30px rgba(0,0,0,0.5) !important;
    }

    /* Przyciski */
    .stButton>button {
        background: linear-gradient(90deg, #3b82f6, #06b6d4);
        border: none;
        border-radius: 12px;
        color: white;
        font-weight: 800;
        letter-spacing: 1px;
        padding: 0.7rem;
        transition: all 0.3s ease;
    }
    
    .stButton>button:hover {
        transform: scale(1.02);
        box-shadow: 0 0 20px rgba(6, 182, 212, 0.6);
    }

    /* Sidebar Customization */
    section[data-testid="stSidebar"] {
        background-color: #020617;
        border-right: 1px solid #1e293b;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. AUTHENTICATION ---
def check_password():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    if not st.session_state.authenticated:
        col1, col2, col3 = st.columns([1, 1.2, 1])
        with col2:
            st.markdown(f"<div style='text-align: center; margin-top: 50px;'><h1 style='color: var(--neon-blue);'>SYSTEM LOGIN</h1></div>", unsafe_allow_html=True)
            try:
                master_password = str(st.secrets["password"])
            except:
                st.error("SYSTEM ERROR: Missing 'password' in secrets.")
                return False
            
            with st.form("Terminal_Login"):
                pwd = st.text_input("ACCESS CODE", type="password")
                if st.form_submit_button("INITIALIZE SYSTEM"):
                    if pwd == master_password:
                        st.session_state.authenticated = True
                        st.rerun()
                    else: st.error("ACCESS DENIED")
            return False
    return True

# --- 3. LOGISTICS DATA ---
VEHICLES = {
    "FTL MEGA (3m)": {"maxWeight": 24000, "L": 1360, "W": 248, "H": 300},
    "FTL STANDARD": {"maxWeight": 24000, "L": 1360, "W": 248, "H": 270},
    "SOLO 18EP": {"maxWeight": 7000, "L": 720, "W": 245, "H": 260},
    "BUS 10EP": {"maxWeight": 1100, "L": 490, "W": 220, "H": 240}
}

def load_products():
    try:
        with open('products.json', 'r', encoding='utf-8') as f:
            return sorted(json.load(f), key=lambda x: x.get('name', ''))
    except:
        return [
            {"name": "EPAL 120x80", "width": 80, "length": 120, "height": 140, "weight": 450, "canStack": True},
            {"name": "SCREEN CASE X2", "width": 120, "length": 65, "height": 110, "weight": 220, "canStack": True},
            {"name": "AUDIO RACK L", "width": 60, "length": 80, "height": 120, "weight": 180, "canStack": False}
        ]

# --- 4. PACKING ENGINE ---
def calculate_packing(cargo, veh):
    placed_stacks = []
    not_placed = []
    total_w = 0
    max_x = 0
    
    items = sorted(cargo, key=lambda x: (x['length']*x['width']), reverse=True)
    x_pos, y_pos, row_w = 0, 0, 0

    for item in items:
        if total_w + item['weight'] > veh['maxWeight']:
            not_placed.append(item)
            continue
            
        stacked = False
        if item.get('canStack', True):
            for s in placed_stacks:
                dim_match = (item['width'] == s['width'] and item['length'] == s['length']) or \
                            (item['width'] == s['length'] and item['length'] == s['width'])
                if dim_match and s['canStackBase'] and (s['curH'] + item['height'] <= veh['H']):
                    it_c = item.copy()
                    it_c['z'] = s['curH']
                    s['items'].append(it_c)
                    s['curH'] += item['height']
                    total_w += item['weight']
                    stacked = True; break
        if stacked: continue

        # New Stack Logic
        for w, l in [(item['width'], item['length']), (item['length'], item['width'])]:
            if y_pos + l <= veh['W'] and x_pos + w <= veh['L']:
                it_c = item.copy()
                it_c['z'] = 0
                placed_stacks.append({'x': x_pos, 'y': y_pos, 'width': w, 'length': l, 'curH': item['height'], 'canStackBase': item.get('canStack', True), 'items': [it_c]})
                y_pos += l
                row_w = max(row_w, w)
                total_w += item['weight']
                max_x = max(max_x, x_pos + row_w)
                stacked = True; break
            elif x_pos + row_w + w <= veh['L'] and l <= veh['W']:
                x_pos += row_w; y_pos = 0; row_w = w
                it_c = item.copy()
                it_c['z'] = 0
                placed_stacks.append({'x': x_pos, 'y': y_pos, 'width': w, 'length': l, 'curH': item['height'], 'canStackBase': item.get('canStack', True), 'items': [it_c]})
                y_pos += l
                total_w += item['weight']
                max_x = max(max_x, x_pos + row_w)
                stacked = True; break
        
        if not stacked: not_placed.append(item)

    return placed_stacks, total_w, not_placed, max_x/100

# --- 5. THE "GHOST" NEON VISUALIZER ---
def draw_neon_3d(stacks, veh):
    fig = go.Figure()
    L, W, H = veh['L'], veh['W'], veh['H']

    # 1. Floor & Center of Gravity calculation
    total_mom_x = 0
    total_mass = 0
    
    # Floor Mesh
    fig.add_trace(go.Mesh3d(x=[0, L, L, 0], y=[0, 0, W, W], z=[0, 0, 0, 0], color='#0f172a', opacity=1, hoverinfo='skip'))

    for s in stacks:
        for it in s['items']:
            x0, y0, z0 = s['x'], s['y'], it['z']
            dx, dy, dz = s['width'], s['length'], it['height']
            
            # CoG calculation
            total_mom_x += (x0 + dx/2) * it['weight']
            total_mass += it['weight']

            # Box Mesh
            fig.add_trace(go.Mesh3d(
                x=[x0, x0+dx, x0+dx, x0, x0, x0+dx, x0+dx, x0],
                y=[y0, y0, y0+dy, y0+dy, y0, y0, y0+dy, y0+dy],
                z=[z0, z0, z0, z0, z0+dz, z0+dz, z0+dz, z0+dz],
                i=[7,0,0,0,4,4,6,6,4,0,3,2], j=[3,4,1,2,5,6,5,2,0,1,6,3], k=[0,7,2,3,6,7,1,1,5,5,7,6],
                opacity=0.85, color='#3b82f6', flatshading=True, name=it['name']
            ))
            
            # Box Neon Edges
            edges = [([x0,x0+dx,x0+dx,x0,x0],[y0,y0,y0+dy,y0+dy,y0],[z0+dz,z0+dz,z0+dz,z0+dz,z0+dz])]
            for ex, ey, ez in edges:
                fig.add_trace(go.Scatter3d(x=ex, y=ey, z=ez, mode='lines', line=dict(color='#00f2ff', width=3), hoverinfo='skip'))

    # 2. Vehicle Chassis (Neon Outline)
    chassis = [
        ([0, L, L, 0, 0], [0, 0, W, W, 0], [0, 0, 0, 0, 0]), # Bottom
        ([0, L, L, 0, 0], [0, 0, W, W, 0], [H, H, H, H, H]), # Top
        ([0,0],[0,0],[0,H]), ([L,L],[0,0],[0,H]), ([L,L],[W,W],[0,H]), ([0,0],[W,W],[0,H]) # Pillars
    ]
    for cx, cy, cz in chassis:
        fig.add_trace(go.Scatter3d(x=cx, y=cy, z=cz, mode='lines', line=dict(color='rgba(0, 242, 255, 0.2)', width=2), hoverinfo='skip'))

    # 3. Center of Gravity Marker
    if total_mass > 0:
        cog_x = total_mom_x / total_mass
        fig.add_trace(go.Scatter3d(x=[cog_x], y=[W/2], z=[2], mode='markers', marker=dict(size=10, color='#ff0055', symbol='diamond'), name="Środek Ciężkości"))

    fig.update_layout(
        scene=dict(
            xaxis=dict(title='DL', backgroundcolor="#020617", gridcolor="#1e293b", color="white"),
            yaxis=dict(title='SZER', backgroundcolor="#020617", gridcolor="#1e293b", color="white"),
            zaxis=dict(title='WYS', backgroundcolor="#020617", gridcolor="#1e293b", color="white"),
            aspectmode='manual', aspectratio=dict(x=L/W*0.5, y=1, z=H/W*0.6)
        ),
        margin=dict(l=0, r=0, b=0, t=0), paper_bgcolor='rgba(0,0,0,0)', showlegend=False
    )
    return fig

# --- 6. COMMAND CENTER UI ---
if check_password():
    if 'cargo' not in st.session_state: st.session_state.cargo = []
    prods = load_products()

    with st.sidebar:
        st.markdown("<h1 style='color: #00f2ff; font-size: 20px;'>SQM COMMAND v4.0</h1>", unsafe_allow_html=True)
        v_name = st.selectbox("UNIT SELECTION", list(VEHICLES.keys()))
        veh = VEHICLES[v_name]
        
        st.divider()
        st.subheader("📦 LOAD INPUT")
        p_sel = st.selectbox("GEAR SELECT", [p['name'] for p in prods], index=None)
        p_qty = st.number_input("QUANTITY", min_value=1, value=1)
        
        if st.button("EXECUTE ADD") and p_sel:
            ref = next(p for p in prods if p['name'] == p_sel)
            for _ in range(p_qty): st.session_state.cargo.append(ref.copy())
            st.rerun()
        
        if st.button("CLEAR ALL", type="secondary"):
            st.session_state.cargo = []
            st.rerun()

    if st.session_state.cargo:
        # Packing Logic
        rem = [dict(i) for i in st.session_state.cargo]
        trucks = []
        while rem:
            s, w, np, ldm = calculate_packing(rem, veh)
            if not s: break
            trucks.append({"stacks": s, "weight": w, "ldm": ldm})
            rem = np

        # Dashboard
        for idx, t in enumerate(trucks):
            st.markdown(f"<div style='border-left: 5px solid var(--neon-blue); padding-left: 15px; margin-bottom: 20px;'><h3>UNIT #{idx+1} | {v_name}</h3></div>", unsafe_allow_html=True)
            
            c1, c2, c3 = st.columns([1, 1, 2.5])
            with c1:
                st.metric("TOTAL WEIGHT", f"{t['weight']} KG")
                st.metric("LDM USED", f"{t['ldm']:.2f} M")
            with c2:
                # Weight Load Gauge
                load_pct = (t['weight']/veh['maxWeight'])
                st.write("**DMC LOAD**")
                st.progress(min(load_pct, 1.0))
                st.write(f"{int(load_pct*100)}% Capacity")
                
            with c3:
                st.plotly_chart(draw_neon_3d(t['stacks'], veh), use_container_width=True, key=f"plot_{idx}")
            
            # Inventory Table
            all_it = [it for s in t['stacks'] for it in s['items']]
            inv_df = pd.DataFrame(all_it).groupby('name').size().reset_index(name='COUNT')
            with st.expander(f"VIEW UNIT #{idx+1} MANIFEST"):
                st.table(inv_df)
            st.divider()
            
        if rem:
            st.error(f"SYSTEM ALERT: {len(rem)} items remain unassigned due to weight/size limits.")
    else:
        st.info("AWAITING INPUT... CONNECT GEAR TO INITIALIZE LOAD PLAN.")
