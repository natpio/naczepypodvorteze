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

# ==============================================================================
# 1. SYSTEM CORE & INITIALIZATION
# ==============================================================================
st.set_page_config(
    page_title="VORTEZA FLOW | GOLIATH v6.0",
    layout="wide",
    initial_sidebar_state="expanded",
    page_icon="🏗️"
)

# Definicja Floty VORTEZA
FLEET_DB = {
    "TIR FTL (Standard)": {"max_w": 24000, "L": 1360, "W": 248, "H": 275, "ldm": 13.6, "type": "HEAVY"},
    "Solo 7m (Heavy)": {"max_w": 7000, "L": 720, "W": 245, "H": 270, "ldm": 7.2, "type": "MEDIUM"},
    "Solo 6m (Medium)": {"max_w": 3500, "L": 600, "W": 245, "H": 250, "ldm": 6.0, "type": "MEDIUM"},
    "BUS (Express)": {"max_w": 1100, "L": 450, "W": 175, "H": 210, "ldm": 4.5, "type": "LIGHT"}
}

# ==============================================================================
# 2. VORTEZA HIGH-END UI ENGINE (CSS)
# ==============================================================================
def apply_vorteza_theme_v6():
    """Wstrzykuje zaawansowany arkusz stylów CSS VORTEZA Systems."""
    st.markdown("""
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;700&family=JetBrains+Mono:wght@300;500&display=swap');
            
            :root {
                --v-copper: #B58863;
                --v-gold: #D4AF37;
                --v-dark-base: #050505;
                --v-card-bg: rgba(12, 12, 12, 0.98);
                --v-border: rgba(181, 136, 99, 0.3);
            }

            .stApp { background-color: var(--v-dark-base); color: #E0E0E0; font-family: 'Montserrat', sans-serif; }
            
            /* Sidebar Styling */
            section[data-testid="stSidebar"] {
                background-color: #080808 !important;
                border-right: 1px solid var(--v-border);
            }

            /* VORTEZA Cards */
            .v-container {
                background: var(--v-card-bg);
                padding: 2.5rem;
                border-radius: 4px;
                border: 1px solid var(--v-border);
                border-left: 6px solid var(--v-copper);
                box-shadow: 0 20px 60px rgba(0,0,0,0.8);
                margin-bottom: 2rem;
            }

            /* Headers */
            h1, h2, h3 { 
                color: var(--v-copper) !important; 
                text-transform: uppercase; 
                letter-spacing: 5px !important; 
                font-weight: 700 !important;
            }

            /* Metrics */
            [data-testid="stMetricValue"] { 
                color: var(--v-copper) !important; 
                font-family: 'JetBrains Mono', monospace !important; 
                font-size: 2.5rem !important;
            }

            /* Custom Buttons */
            .stButton > button {
                background: transparent;
                color: var(--v-copper);
                border: 1px solid var(--v-copper);
                padding: 1rem 2rem;
                text-transform: uppercase;
                letter-spacing: 3px;
                font-weight: 700;
                width: 100%;
                transition: 0.4s ease;
            }
            .stButton > button:hover {
                background: var(--v-copper);
                color: black;
                box-shadow: 0 0 40px rgba(181, 136, 99, 0.4);
            }

            /* Tables */
            .v-table-pro { width: 100%; border-collapse: collapse; margin-top: 20px; }
            .v-table-pro th { color: var(--v-copper); text-align: left; font-size: 0.75rem; text-transform: uppercase; border-bottom: 1px solid #444; padding: 15px; }
            .v-table-pro td { padding: 15px; border-bottom: 1px solid #151515; font-size: 0.9rem; color: #AAA; }

            /* Tooltips & Info */
            .v-info-box {
                background: rgba(181, 136, 99, 0.03);
                border: 1px solid var(--v-border);
                padding: 15px;
                border-radius: 4px;
                font-size: 0.8rem;
                color: #777;
            }
        </style>
    """, unsafe_allow_html=True)

# ==============================================================================
# 3. SECURITY & AUTHENTICATION
# ==============================================================================
def authenticate():
    """Zarządza dostępem do terminala Goliath na podstawie hasła."""
    if "authorized" not in st.session_state:
        st.session_state.authorized = False

    if not st.session_state.authorized:
        try:
            # Klucz z Twoich Secrets
            master_key = str(st.secrets.get("password", "vorteza2026"))
        except:
            master_key = "vorteza2026"

        st.markdown("<br><br><br>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1, 1.5, 1])
        with col2:
            with st.form("TerminalAuth"):
                st.markdown("<h2 style='text-align:center;'>VORTEZA LOGIN</h2>", unsafe_allow_html=True)
                key_input = st.text_input("GOLIATH ACCESS KEY", type="password")
                if st.form_submit_button("INITIALIZE SYSTEM"):
                    if key_input == master_key:
                        st.session_state.authorized = True
                        st.rerun()
                    else:
                        st.error("ACCESS DENIED: INVALID CORE KEY")
        return False
    return True

# ==============================================================================
# 4. ADVANCED 3D RENDER ENGINE (CAD-STYLE)
# ==============================================================================
def render_goliath_3d(vehicle, stacks):
    """Renderuje hiper-szczegółowy model 3D pojazdu i ładunku."""
    fig = go.Figure()
    L, W, H = vehicle['L'], vehicle['W'], vehicle['H']

    # --- KONSTRUKCJA POJAZDU (CAD) ---
    # Podłoga naczepy
    fig.add_trace(go.Mesh3d(
        x=[0, L, L, 0], y=[0, 0, W, W], z=[-3, -3, -3, -3],
        color='#151515', opacity=1, hoverinfo='skip'
    ))
    
    # Koła (Uproszczone cylindry)
    wheel_pos = [150, 200, 250, L-100, L-150]
    for wp in wheel_pos:
        if wp < L:
            fig.add_trace(go.Mesh3d(
                x=[wp-20, wp+20, wp+20, wp-20], y=[-10, -10, 0, 0], z=[-30, -30, -3, -3],
                color='#000', opacity=1, hoverinfo='skip'
            ))
            fig.add_trace(go.Mesh3d(
                x=[wp-20, wp+20, wp+20, wp-20], y=[W, W, W+10, W+10], z=[-30, -30, -3, -3],
                color='#000', opacity=1, hoverinfo='skip'
            ))

    # Kabina (Solidny Mesh)
    fig.add_trace(go.Mesh3d(
        x=[-150, 0, 0, -150, -150, 0, 0, -150],
        y=[-5, -5, W+5, W+5, -5, -5, W+5, W+5],
        z=[0, 0, 0, 0, H*0.85, H*0.85, H*0.85, H*0.85],
        i=[7,0,0,0,4,4,6,6,4,0,3,2], j=[3,4,1,2,5,6,5,2,0,1,6,3], k=[0,7,2,3,6,7,1,1,5,5,7,6],
        color='#0a0a0a', opacity=1, name="UNIT_CAB"
    ))

    # Ramka paki (Struktura miedziana)
    cage = [
        ([0, L], [0, 0], [0, 0]), ([0, L], [W, W], [0, 0]), ([0, 0], [0, W], [0, 0]), ([L, L], [0, W], [0, 0]),
        ([0, 0], [0, 0], [0, H]), ([0, 0], [W, W], [0, H]), ([0, L], [0, 0], [H, H]), ([0, L], [W, W], [H, H]),
        ([L, L], [0, 0], [0, H]), ([L, L], [W, W], [0, H])
    ]
    for xc, yc, zc in cage:
        fig.add_trace(go.Scatter3d(x=xc, y=yc, z=zc, mode='lines', line=dict(color='#B58863', width=5), hoverinfo='skip'))

    # --- RENDER ŁADUNKU ---
    for s_idx, stack in enumerate(stacks):
        base_shade = 181 - (s_idx % 8) * 10
        cargo_color = f'rgb({base_shade}, {int(base_shade*0.75)}, {int(base_shade*0.55)})'
        
        for item in stack['items']:
            x, y, z = stack['x'], stack['y'], item['z']
            dx, dy, dz = item['w_fit'], item['l_fit'], item['height']
            
            # Bryła paczki
            fig.add_trace(go.Mesh3d(
                x=[x, x+dx, x+dx, x, x, x+dx, x+dx, x],
                y=[y, y, y+dy, y+dy, y, y, y+dy, y+dy],
                z=[z, z, z, z, z+dz, z+dz, z+dz, z+dz],
                i=[7,0,0,0,4,4,6,6,4,0,3,2], j=[3,4,1,2,5,6,5,2,0,1,6,3], k=[0,7,2,3,6,7,1,1,5,5,7,6],
                color=cargo_color, opacity=0.98, name=item['name']
            ))
            # Krawędzie paczki
            fig.add_trace(go.Scatter3d(
                x=[x,x+dx,x+dx,x,x,x,x+dx,x+dx,x,x,x+dx,x+dx,x+dx,x+dx,x,x],
                y=[y,y,y+dy,y+dy,y,y,y,y+dy,y+dy,y+dy,y+dy,y,y,y+dy,y+dy,y],
                z=[z,z,z,z,z,z+dz,z+dz,z,z,z+dz,z+dz,z+dz,z,z,z+dz,z+dz],
                mode='lines', line=dict(color='black', width=1.5), hoverinfo='skip'
            ))

    fig.update_layout(
        scene=dict(
            aspectmode='data',
            xaxis_visible=False, yaxis_visible=False, zaxis_visible=False,
            camera=dict(eye=dict(x=1.9, y=1.9, z=1.3)),
            bgcolor='rgba(0,0,0,0)'
        ),
        paper_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=0, r=0, b=0, t=0),
        showlegend=False
    )
    return fig

# ==============================================================================
# 5. PACKING ENGINE V-6 (OPTIMIZATION LOGIC)
# ==============================================================================
class V6Engine:
    """Zaawansowany algorytm pakowania 3D z obsługą priorytetów i rotacji."""
    
    @staticmethod
    def pack(cargo, vehicle):
        # Sortowanie: 1. Brak możliwości piętrowania (ciężkie), 2. Powierzchnia podstawy
        items = sorted(cargo, key=lambda x: (not x.get('canStack', True), x['width']*x['length']), reverse=True)
        
        stacks = []
        not_packed = []
        current_w = 0
        cx, cy, row_w = 0, 0, 0

        for it in items:
            if current_w + it['weight'] > vehicle['max_w']:
                not_packed.append(it); continue
            
            # Próba piętrowania
            is_stacked = False
            if it.get('canStack', True):
                for s in stacks:
                    fit = (it['width'] <= s['w'] and it['length'] <= s['l']) or (it['length'] <= s['w'] and it['width'] <= s['l'])
                    if fit and (s['curH'] + it['height'] <= vehicle['H']):
                        it_c = it.copy(); it_c['z'] = s['curH']
                        it_c['w_fit'], it_c['l_fit'] = s['w'], s['l']
                        s['items'].append(it_c)
                        s['curH'] += it['height']
                        current_w += it['weight']; is_stacked = True; break
            
            if is_stacked: continue

            # Próba podłogi (z rotacją)
            placed = False
            orientations = [(it['width'], it['length']), (it['length'], it['width'])]
            for fw, fl in orientations:
                if cy + fl <= vehicle['W'] and cx + fw <= vehicle['L']:
                    it_c = it.copy(); it_c['z'] = 0; it_c['w_fit'], it_c['l_fit'] = fw, fl
                    stacks.append({'x':cx, 'y':cy, 'w':fw, 'l':fl, 'curH':it['height'], 'items':[it_c]})
                    cy += fl; row_w = max(row_w, fw); current_w += it['weight']; placed = True; break
                elif cx + row_w + fw <= vehicle['L'] and fl <= vehicle['W']:
                    cx += row_w; cy = 0; row_w = fw
                    it_c = it.copy(); it_c['z'] = 0; it_c['w_fit'], it_c['l_fit'] = fw, fl
                    stacks.append({'x':cx, 'y':cy, 'w':fw, 'l':fl, 'curH':it['height'], 'items':[it_c]})
                    cy += fl; current_w += it['weight']; placed = True; break
            
            if not placed: not_packed.append(it)
        
        ldm = max([s['x'] + s['w'] for s in stacks]) / 100 if stacks else 0
        return stacks, current_w, not_packed, ldm

# ==============================================================================
# 6. INVENTORY & DATA PERSISTENCE
# ==============================================================================
def load_v_inventory():
    try:
        with open('products.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return []

def save_v_inventory(data):
    with open('products.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

# ==============================================================================
# 7. MAIN INTERFACE (GOLIATH CONTROL CENTER)
# ==============================================================================
def main():
    apply_vorteza_theme_v6()
    
    if not authenticate():
        return

    # --- SESSION STATE ---
    if 'v_manifest' not in st.session_state: st.session_state.v_manifest = []
    inventory = load_v_inventory()

    # --- TOP NAVBAR ---
    h_col1, h_col2 = st.columns([5, 1])
    with h_col1:
        st.markdown("<h1>VORTEZA GOLIATH FLOW</h1>", unsafe_allow_html=True)
        st.markdown(f"<p style='color:#666; font-size:0.7rem; letter-spacing:3px;'>INTEGRATED LOGISTICS COMMAND | v6.0.25 | {datetime.now().strftime('%H:%M:%S')}</p>", unsafe_allow_html=True)
    with h_col2:
        if st.button("TERMINATE"):
            st.session_state.authorized = False; st.rerun()

    # --- SIDEBAR CONTROL ---
    with st.sidebar:
        st.markdown("### 🛰️ MISSION CONTROL")
        v_sel_name = st.selectbox("ACTIVE FLEET UNIT", list(FLEET_DB.keys()))
        veh_active = FLEET_DB[v_sel_name]
        
        st.markdown(f"""<div class='v-info-box'>SPEC: {veh_active['L']}x{veh_active['W']}x{veh_active['H']} cm<br>PAYLOAD: {veh_active['max_w']} kg</div>""", unsafe_allow_html=True)
        
        st.divider()
        st.markdown("### ➕ ADD TO MANIFEST")
        p_names = [p['name'] for p in inventory]
        sel_p_name = st.selectbox("SELECT PRODUCT", p_names, index=None)
        
        if sel_p_name:
            p_obj = next(p for p in inventory if p['name'] == sel_p_name)
            ipc = p_obj.get('itemsPerCase', 1)
            st.caption(f"Standard: {ipc} pcs/case")
            in_qty = st.number_input("QUANTITY (PCS)", min_value=1, value=ipc)
            n_cases = math.ceil(in_qty / ipc)
            
            if st.button("APPEND TO MANIFEST", type="primary"):
                for i in range(n_cases):
                    unit = p_obj.copy()
                    unit['p_real'] = ipc if (i < n_cases - 1 or in_qty % ipc == 0) else (in_qty % ipc)
                    st.session_state.v_manifest.append(unit)
                st.toast("Manifest updated.")

        if st.button("PURGE MANIFEST"):
            st.session_state.v_manifest = []; st.rerun()

    # --- MAIN DASHBOARD TABS ---
    tab_planner, tab_inventory, tab_analytics = st.tabs(["📊 PLANNER", "📦 INVENTORY", "📈 ANALYTICS"])

    # --------------------------------------------------------------------------
    # TAB 1: PLANNER
    # --------------------------------------------------------------------------
    with tab_planner:
        if st.session_state.v_manifest:
            # Metrics
            total_w = sum(float(u['weight']) for u in st.session_state.v_manifest)
            total_u = len(st.session_state.v_manifest)
            
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("UNITS", total_u)
            m2.metric("WEIGHT", f"{total_w} kg")
            m3.metric("UTILIZATION", f"{(total_w/veh_active['max_w'])*100:.1f}%")
            m4.metric("LDM (EST.)", f"{(total_w/veh_active['max_w'])*(veh_active['L']/100):.2f}")

            # Optimization
            rem_cargo = [dict(u) for u in st.session_state.v_manifest]
            fleet_plan = []
            
            while rem_cargo:
                stacks, w_res, not_p, ldm_r = V6Engine.pack(rem_cargo, veh_active)
                if not stacks: break
                fleet_plan.append({"stacks": stacks, "weight": w_res, "ldm": ldm_r})
                rem_cargo = not_p

            # Results
            for idx, unit in enumerate(fleet_plan):
                st.markdown(f'<div class="v-container">', unsafe_allow_html=True)
                st.markdown(f"### UNIT #{idx+1} | {v_sel_name}", unsafe_allow_html=True)
                
                c_3d, c_dat = st.columns([2, 1])
                with c_3d:
                    st.plotly_chart(render_goliath_3d(veh_active, unit['stacks']), use_container_width=True)
                with c_dat:
                    st.markdown("**OPERATIONAL DATA**")
                    st.write(f"Payload: {unit['weight']} / {veh_active['max_w']} kg")
                    st.write(f"LDM: {unit['ldm']:.2f} m")
                    
                    st.divider()
                    st.markdown("**PACKING LIST**")
                    u_items = [it['name'] for s in unit['stacks'] for it in s['items']]
                    if u_items:
                        counts = pd.Series(u_items).value_counts().reset_index()
                        counts.columns = ['Product', 'Qty']
                        st.table(counts)
                st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.info("Manifest empty. Please add items via mission control.")

    # --------------------------------------------------------------------------
    # TAB 2: INVENTORY (CRUD)
    # --------------------------------------------------------------------------
    with tab_inventory:
        st.markdown("### 📦 GLOBAL PRODUCT DATABASE")
        
        with st.expander("➕ ADD NEW PRODUCT TO DATABASE"):
            with st.form("AddProduct"):
                f_name = st.text_input("Product Name")
                c1, c2, c3 = st.columns(3)
                f_l = c1.number_input("Length (cm)", value=120)
                f_w = c2.number_input("Width (cm)", value=80)
                f_h = c3.number_input("Height (cm)", value=100)
                f_weight = st.number_input("Weight (kg)", value=100)
                f_ipc = st.number_input("Items Per Case", value=1)
                f_stack = st.checkbox("Can Stack", value=True)
                
                if st.form_submit_button("SAVE TO DATABASE"):
                    new_p = {"name": f_name, "length": f_l, "width": f_w, "height": f_h, "weight": f_weight, "itemsPerCase": f_ipc, "canStack": f_stack}
                    inventory.append(new_p)
                    save_v_inventory(inventory)
                    st.success("Database updated.")
                    st.rerun()

        st.divider()
        if inventory:
            df_inv = pd.DataFrame(inventory)
            edited_df = st.data_editor(df_inv, use_container_width=True, num_rows="dynamic", key="inv_editor")
            if st.button("SYNC DATABASE CHANGES"):
                save_v_inventory(edited_df.to_dict('records'))
                st.success("System synchronized.")
        else:
            st.warning("Inventory empty.")

    # --------------------------------------------------------------------------
    # TAB 3: ANALYTICS
    # --------------------------------------------------------------------------
    with tab_analytics:
        st.markdown("### 📈 PERFORMANCE ANALYTICS")
        if st.session_state.v_manifest:
            an_df = pd.DataFrame(st.session_state.v_cargo if 'v_cargo' in st.session_state else st.session_state.v_manifest)
            
            c1, c2 = st.columns(2)
            with c1:
                fig_pie = px.pie(an_df, names='name', title="Weight Distribution by Product", hole=0.4, color_discrete_sequence=px.colors.sequential.Copper)
                st.plotly_chart(fig_pie, use_container_width=True)
            with c2:
                fig_bar = px.bar(an_df, x='name', y='weight', title="Total Mass per Item Group", color='weight', color_continuous_scale='Copper')
                st.plotly_chart(fig_bar, use_container_width=True)
        else:
            st.info("No data available for analysis.")

if __name__ == "__main__":
    main()
