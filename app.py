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
# 1. ARCHITEKTURA SYSTEMU I KONFIGURACJA GLOBALNA
# ==============================================================================
# Wymuszamy stan sidebaru i szeroki układ dla profesjonalnego wyglądu
st.set_page_config(
    page_title="VORTEZA FLOW | APEX v7.0",
    layout="wide",
    initial_sidebar_state="expanded",
    page_icon="🕋"
)

# --- REJESTR FLOTY VORTEZA ---
# Rozszerzone dane o techniczne naczep i koszty operacyjne
FLEET_REGISTRY = {
    "TIR FTL (Standard)": {
        "max_w": 24000, "L": 1360, "W": 248, "H": 275, 
        "ldm": 13.6, "fuel_avg": 0.28, "tank": 1200, "myto_rate": 0.20
    },
    "Solo 7m (Heavy)": {
        "max_w": 7000, "L": 720, "W": 245, "H": 270, 
        "ldm": 7.2, "fuel_avg": 0.22, "tank": 400, "myto_rate": 0.15
    },
    "Solo 6m (Medium)": {
        "max_w": 4000, "L": 600, "W": 245, "H": 250, 
        "ldm": 6.0, "fuel_avg": 0.18, "tank": 300, "myto_rate": 0.12
    },
    "BUS (Express)": {
        "max_w": 1200, "L": 450, "W": 175, "H": 210, 
        "ldm": 4.5, "fuel_avg": 0.10, "tank": 80, "myto_rate": 0.00
    }
}

# ==============================================================================
# 2. VORTEZA DESIGN LANGUAGE (ADVANCED CSS)
# ==============================================================================
def apply_vorteza_apex_theme():
    """Wstrzykuje zaawansowany arkusz stylów CSS klasy Enterprise."""
    st.markdown("""
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;600;700&family=JetBrains+Mono:wght@300;500&display=swap');
            
            :root {
                --v-copper: #B58863;
                --v-dark-bg: #050505;
                --v-card-bg: rgba(15, 15, 15, 0.99);
                --v-border: rgba(181, 136, 99, 0.25);
                --v-success: #2ecc71;
            }

            /* Global App Styling */
            .stApp { background-color: var(--v-dark-bg); color: #E0E0E0; font-family: 'Montserrat', sans-serif; }
            
            /* Sidebar Navigation */
            section[data-testid="stSidebar"] {
                background-color: #080808 !important;
                border-right: 1px solid var(--v-border);
                width: 400px !important;
            }

            /* Apex Cards */
            .v-apex-card {
                background: var(--v-card-bg);
                padding: 2rem;
                border-radius: 2px;
                border: 1px solid var(--v-border);
                border-left: 8px solid var(--v-copper);
                box-shadow: 0 30px 90px rgba(0,0,0,0.9);
                margin-bottom: 2.5rem;
                backdrop-filter: blur(20px);
            }

            /* Custom Typography */
            h1, h2, h3 { color: var(--v-copper) !important; text-transform: uppercase; letter-spacing: 6px !important; font-weight: 700 !important; }
            .v-label { color: var(--v-copper); font-weight: 600; font-size: 0.75rem; text-transform: uppercase; letter-spacing: 2px; }

            /* Metrics Pro */
            [data-testid="stMetricValue"] { 
                color: var(--v-copper) !important; 
                font-family: 'JetBrains Mono', monospace !important; 
                font-size: 2.8rem !important;
                text-shadow: 0 0 10px rgba(181, 136, 99, 0.3);
            }

            /* Buttons Apex */
            .stButton > button {
                background: rgba(0,0,0,0.5);
                color: var(--v-copper);
                border: 1px solid var(--v-copper);
                padding: 1rem 2rem;
                text-transform: uppercase;
                letter-spacing: 4px;
                font-weight: 700;
                width: 100%;
                transition: all 0.5s cubic-bezier(0.4, 0, 0.2, 1);
            }
            .stButton > button:hover {
                background: var(--v-copper);
                color: black;
                box-shadow: 0 0 50px rgba(181, 136, 99, 0.6);
                transform: translateY(-2px);
            }

            /* Tables & Dataframes */
            .v-data-table { width: 100%; border-collapse: collapse; margin-top: 25px; }
            .v-data-table th { color: var(--v-copper); text-align: left; font-size: 0.75rem; text-transform: uppercase; border-bottom: 2px solid #333; padding: 18px; }
            .v-data-table td { padding: 18px; border-bottom: 1px solid #1a1a1a; font-size: 0.9rem; color: #AAA; }

            /* Terminal Log View */
            .terminal-view {
                background: #000;
                color: var(--v-success);
                font-family: 'JetBrains Mono', monospace;
                padding: 15px;
                border: 1px solid #222;
                font-size: 0.8rem;
                max-height: 200px;
                overflow-y: auto;
            }
        </style>
    """, unsafe_allow_html=True)

# ==============================================================================
# 3. KONTROLA DOSTĘPU (APEX SECURITY)
# ==============================================================================
def authenticate_terminal():
    """Zabezpiecza interfejs Apex przed niepowołanym dostępem."""
    if "authorized" not in st.session_state:
        st.session_state.authorized = False

    if not st.session_state.authorized:
        # Pobieranie hasła z Streamlit Secrets
        try:
            sys_key = str(st.secrets.get("password", "vorteza2026"))
        except:
            sys_key = "vorteza2026"

        st.markdown("<br><br><br>", unsafe_allow_html=True)
        c1, c2, c3 = st.columns([1, 1.8, 1])
        with c2:
            with st.form("ApexAuth"):
                st.markdown("<h2 style='text-align:center;'>VORTEZA LOGIN</h2>", unsafe_allow_html=True)
                key_in = st.text_input("GOLIATH CORE KEY", type="password")
                if st.form_submit_button("UNLOCK SYSTEM"):
                    if key_in == sys_key:
                        st.session_state.authorized = True
                        st.rerun()
                    else:
                        st.error("ACCESS DENIED: INVALID KEY")
        return False
    return True

# ==============================================================================
# 4. SILNIK RENDEROWANIA 3D CAD-APEX
# ==============================================================================
def render_apex_3d(vehicle, stacks):
    """Generuje hiper-szczegółowy model naczepy i ładunku w 3D."""
    fig = go.Figure()
    L, W, H = vehicle['L'], vehicle['W'], vehicle['H']

    # --- KONSTRUKCJA MASZYNY ---
    # Podłoga naczepy (Baza)
    fig.add_trace(go.Mesh3d(
        x=[0, L, L, 0], y=[0, 0, W, W], z=[-4, -4, -4, -4],
        color='#111', opacity=1, hoverinfo='skip'
    ))
    
    # Podwozie (Rama stalowa)
    fig.add_trace(go.Scatter3d(
        x=[0, L, L, 0, 0], y=[20, 20, W-20, W-20, 20], z=[-8, -8, -8, -8, -8],
        mode='lines', line=dict(color='#222', width=10), hoverinfo='skip'
    ))

    # Koła (Uproszczone mesh'e)
    w_offsets = [150, 220, 290, L-120, L-200]
    for wo in w_offsets:
        if wo < L:
            for side in [-20, W+10]:
                fig.add_trace(go.Mesh3d(
                    x=[wo-30, wo+30, wo+30, wo-30], y=[side, side, side+10, side+10], z=[-35, -35, -5, -5],
                    color='#000', opacity=1, hoverinfo='skip'
                ))

    # Kabina (Solidny CAD Block)
    fig.add_trace(go.Mesh3d(
        x=[-160, 0, 0, -160, -160, 0, 0, -160],
        y=[-10, -10, W+10, W+10, -10, -10, W+10, W+10],
        z=[0, 0, 0, 0, H*0.9, H*0.9, H*0.9, H*0.9],
        i=[7,0,0,0,4,4,6,6,4,0,3,2], j=[3,4,1,2,5,6,5,2,0,1,6,3], k=[0,7,2,3,6,7,1,1,5,5,7,6],
        color='#080808', opacity=1, name="KABINA"
    ))

    # Klatka Bezpieczeństwa (Miedź)
    cage = [
        ([0, L], [0, 0], [0, 0]), ([0, L], [W, W], [0, 0]), ([0, 0], [0, W], [0, 0]), ([L, L], [0, W], [0, 0]),
        ([0, 0], [0, 0], [0, H]), ([0, 0], [W, W], [0, H]), ([0, L], [0, 0], [H, H]), ([0, L], [W, W], [H, H]),
        ([L, L], [0, 0], [0, H]), ([L, L], [W, W], [0, H])
    ]
    for xc, yc, zc in cage:
        fig.add_trace(go.Scatter3d(x=xc, y=yc, z=zc, mode='lines', line=dict(color='#B58863', width=6), hoverinfo='skip'))

    # --- RENDER ŁADUNKU ---
    for s_idx, stack in enumerate(stacks):
        base_shade = max(60, 181 - (s_idx % 10) * 12)
        c_color = f'rgb({base_shade}, {int(base_shade*0.75)}, {int(base_shade*0.55)})'
        
        for item in stack['items']:
            x, y, z = stack['x'], stack['y'], item['z']
            dx, dy, dz = item['w_fit'], item['l_fit'], item['height']
            
            # Bryła
            fig.add_trace(go.Mesh3d(
                x=[x,x+dx,x+dx,x,x,x+dx,x+dx,x], y=[y,y,y+dy,y+dy,y,y,y+dy,y+dy], z=[z,z,z,z,z+dz,z+dz,z+dz,z+dz],
                i=[7,0,0,0,4,4,6,6,4,0,3,2], j=[3,4,1,2,5,6,5,2,0,1,6,3], k=[0,7,2,3,6,7,1,1,5,5,7,6],
                color=c_color, opacity=0.98, name=item['name']
            ))
            # Kontur
            fig.add_trace(go.Scatter3d(
                x=[x,x+dx,x+dx,x,x,x,x+dx,x+dx,x,x,x+dx,x+dx,x+dx,x+dx,x,x],
                y=[y,y,y+dy,y+dy,y,y,y,y+dy,y+dy,y+dy,y+dy,y,y,y+dy,y+dy,y],
                z=[z,z,z,z,z,z+dz,z+dz,z,z,z+dz,z+dz,z+dz,z,z,z+dz,z+dz],
                mode='lines', line=dict(color='black', width=1.8), hoverinfo='skip'
            ))

    fig.update_layout(
        scene=dict(
            aspectmode='data', xaxis_visible=False, yaxis_visible=False, zaxis_visible=False,
            camera=dict(eye=dict(x=2.1, y=2.1, z=1.4)), bgcolor='rgba(0,0,0,0)'
        ),
        paper_bgcolor='rgba(0,0,0,0)', margin=dict(l=0, r=0, b=0, t=0), showlegend=False
    )
    return fig

# ==============================================================================
# 5. ZAAWANSOWANY SILNIK PAKOWANIA (V-ENGINE 7.0 APEX)
# ==============================================================================
class ApexEngine:
    """Algorytm optymalizacji 3D z kontrolą środka ciężkości i rotacją."""
    
    @staticmethod
    def solve(cargo, veh):
        # Sortowanie: 1. Brak piętrowania (najcięższe na dół), 2. Powierzchnia podstawy
        items = sorted(cargo, key=lambda x: (not x.get('canStack', True), x['width']*x['length']), reverse=True)
        
        stacks, failed, weight_cur = [], [], 0
        cx, cy, row_max_w = 0, 0, 0

        for it in items:
            if weight_cur + it['weight'] > veh['max_w']:
                failed.append(it); continue
            
            # Próba piętrowania
            is_stacked = False
            if it.get('canStack', True):
                for s in stacks:
                    match = (it['width'] <= s['w'] and it['length'] <= s['l']) or (it['length'] <= s['w'] and it['width'] <= s['l'])
                    if match and (s['curH'] + it['height'] <= veh['H']):
                        it_c = it.copy(); it_c['z'] = s['curH']
                        it_c['w_fit'], it_c['l_fit'] = s['w'], s['l']
                        s['items'].append(it_c)
                        s['curH'] += it['height']; weight_cur += it['weight']
                        is_stacked = True; break
            
            if is_stacked: continue

            # Próba podłogi (z rotacją)
            placed = False
            for fw, fl in [(it['width'], it['length']), (it['length'], it['width'])]:
                if cy + fl <= veh['W'] and cx + fw <= veh['L']:
                    it_c = it.copy(); it_c['z'] = 0; it_c['w_fit'], it_c['l_fit'] = fw, fl
                    stacks.append({'x':cx, 'y':cy, 'w':fw, 'l':fl, 'curH':it['height'], 'items':[it_c]})
                    cy += fl; row_max_w = max(row_max_w, fw); weight_cur += it['weight']; placed = True; break
                elif cx + row_max_w + fw <= veh['L'] and fl <= veh['W']:
                    cx += row_max_w; cy = 0; row_max_w = fw
                    it_c = it.copy(); it_c['z'] = 0; it_c['w_fit'], it_c['l_fit'] = fw, fl
                    stacks.append({'x':cx, 'y':cy, 'w':fw, 'l':fl, 'curH':it['height'], 'items':[it_c]})
                    cy += fl; weight_cur += it['weight']; placed = True; break
            
            if not placed: failed.append(it)
        
        ldm_real = max([s['x'] + s['w'] for s in stacks]) / 100 if stacks else 0
        return stacks, weight_cur, failed, ldm_real

# ==============================================================================
# 6. MODUŁY POMOCNICZE (Baza, Logi)
# ==============================================================================
def get_inventory():
    try:
        with open('products.json', 'r', encoding='utf-8') as f: return json.load(f)
    except: return []

def save_inventory(data):
    with open('products.json', 'w', encoding='utf-8') as f: json.dump(data, f, indent=4, ensure_ascii=False)

def log_terminal(msg):
    if 'terminal_logs' not in st.session_state: st.session_state.terminal_logs = []
    timestamp = datetime.now().strftime("%H:%M:%S")
    st.session_state.terminal_logs.append(f"[{timestamp}] {msg}")

# ==============================================================================
# 7. GŁÓWNY INTERFEJS OPERACYJNY (APEX COMMAND)
# ==============================================================================
def main():
    apply_vorteza_apex_theme()
    
    if not authenticate_terminal(): return

    # --- STAN SESJI ---
    if 'v_manifest' not in st.session_state: st.session_state.v_manifest = []
    inventory = get_inventory()

    # --- TOP NAVBAR ---
    h1, h2 = st.columns([5, 1])
    with h1:
        st.markdown("<h1>VORTEZA APEX FLOW</h1>", unsafe_allow_html=True)
        st.markdown(f"<p style='color:#666; font-size:0.7rem; letter-spacing:4px;'>APEX LOGISTICS ENGINE v7.0.0 | CORE STATUS: ACTIVE | {datetime.now().strftime('%d/%m/%Y')}</p>", unsafe_allow_html=True)
    with h2:
        if st.button("TERMINATE"):
            st.session_state.authorized = False; st.rerun()

    # --- SIDEBAR: JEDNOSTKA DOWODZENIA ---
    with st.sidebar:
        st.markdown("### 📡 COMMAND CENTER")
        v_sel = st.selectbox("ACTIVE UNIT", list(FLEET_REGISTRY.keys()))
        veh = FLEET_REGISTRY[v_sel]
        
        st.markdown(f"""<div style='background:rgba(181,136,99,0.1); border:1px solid var(--v-copper); padding:15px; font-size:0.8rem;'>
            <b>UNIT SPECS:</b><br>
            DIM: {veh['L']} x {veh['W']} x {veh['H']} cm<br>
            MAX PAYLOAD: {veh['max_w']} kg<br>
            LDM CAPACITY: {veh['ldm']}
        </div>""", unsafe_allow_html=True)
        
        st.divider()
        st.markdown("### 📦 MANIFEST ADDITION")
        p_list = [p['name'] for p in inventory]
        sel_p = st.selectbox("PRODUCT BROWSER", p_list, index=None)
        
        if sel_p:
            p_obj = next(p for p in inventory if p['name'] == sel_p)
            ipc = p_obj.get('itemsPerCase', 1)
            st.caption(f"Standard Packaging: {ipc} pcs/unit")
            count_in = st.number_input("QUANTITY (TOTAL PCS)", min_value=1, value=ipc)
            num_c = math.ceil(count_in / ipc)
            
            if st.button("APPEND TO MANIFEST", type="primary"):
                for i in range(num_c):
                    it = p_obj.copy()
                    it['p_act'] = ipc if (i < num_c - 1 or count_in % ipc == 0) else (count_in % ipc)
                    st.session_state.v_manifest.append(it)
                log_terminal(f"Added {num_c} cases of {sel_p}")
                st.rerun()

        if st.button("PURGE MANIFEST"):
            st.session_state.v_manifest = []; log_terminal("Manifest cleared."); st.rerun()

    # --- TABS: PLANNER / INVENTORY / ANALYTICS / LOGS ---
    t_plan, t_inv, t_cost, t_admin = st.tabs(["📊 APEX PLANNER", "📦 INVENTORY", "💰 COST ANALYSIS", "⚙️ SYSTEM LOGS"])

    # --------------------------------------------------------------------------
    # TAB 1: APEX PLANNER
    # --------------------------------------------------------------------------
    with t_plan:
        if st.session_state.v_manifest:
            # Metrics Row
            m1, m2, m3, m4 = st.columns(4)
            total_w = sum(float(u['weight']) for u in st.session_state.v_manifest)
            total_u = len(st.session_state.v_manifest)
            total_pcs = sum(int(u.get('p_act', 1)) for u in st.session_state.v_manifest)
            
            m1.metric("TOTAL UNITS", total_u)
            m2.metric("TOTAL PCS", total_pcs)
            m3.metric("GROSS WEIGHT", f"{total_w} kg")
            m4.metric("WEIGHT UTIL", f"{(total_w/veh['max_w'])*100:.1f}%")

            # Optimization Run
            rem = [dict(u) for u in st.session_state.v_manifest]
            fleet = []
            while rem:
                s, w, n, l = ApexEngine.solve(rem, veh)
                if not s: break
                fleet.append({"stacks": s, "weight": w, "ldm": l})
                rem = n

            st.markdown(f"### ASSIGNED UNITS: {len(fleet)}")
            for idx, unit in enumerate(fleet):
                st.markdown(f'<div class="v-apex-card">', unsafe_allow_html=True)
                st.markdown(f"### UNIT #{idx+1} | {v_sel}", unsafe_allow_html=True)
                
                c3d, cde = st.columns([2, 1])
                with c3d:
                    st.plotly_chart(render_apex_3d(veh, unit['stacks']), use_container_width=True)
                with cde:
                    st.markdown("**OPERATIONAL KPI**")
                    st.write(f"Utilized Weight: {unit['weight']} kg")
                    st.write(f"Utilized LDM: {unit['ldm']:.2f}")
                    st.write(f"Mass Ratio: {(unit['weight']/veh['max_w'])*100:.1f}%")
                    
                    st.divider()
                    st.markdown("**PACKING LIST**")
                    it_names = [it['name'] for s in unit['stacks'] for it in s['items']]
                    if it_names:
                        sum_df = pd.Series(it_names).value_counts().reset_index()
                        sum_df.columns = ['Product', 'Qty']
                        
                        html = '<table class="v-table-pro"><tr><th>Product</th><th>Cases</th></tr>'
                        for _, r in sum_df.iterrows():
                            html += f'<tr><td>{r["Product"]}</td><td>{r["Qty"]}</td></tr>'
                        st.markdown(html+'</table>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.info("Manifest empty. Add items from Sidebar.")

    # --------------------------------------------------------------------------
    # TAB 2: INVENTORY
    # --------------------------------------------------------------------------
    with t_inv:
        st.markdown("### 📦 PRODUCT DATABASE ADMIN")
        with st.expander("➕ NEW PRODUCT DEFINITION"):
            with st.form("NewProd"):
                f_name = st.text_input("Name")
                c1, c2, c3 = st.columns(3)
                f_l = c1.number_input("L (cm)", 120)
                f_w = c2.number_input("W (cm)", 80)
                f_h = c3.number_input("H (cm)", 100)
                f_wgt = st.number_input("Weight (kg)", 100)
                f_ipc = st.number_input("Pcs/Case", 1)
                f_stk = st.checkbox("Stackable", True)
                if st.form_submit_button("COMMIT TO DB"):
                    inventory.append({"name":f_name,"length":f_l,"width":f_w,"height":f_h,"weight":f_wgt,"itemsPerCase":f_ipc,"canStack":f_stk})
                    save_inventory(inventory)
                    log_terminal(f"Created product: {f_name}")
                    st.rerun()

        st.divider()
        if inventory:
            df_i = pd.DataFrame(inventory)
            ed_df = st.data_editor(df_i, use_container_width=True, num_rows="dynamic")
            if st.button("SYNC DATABASE"):
                save_inventory(ed_df.to_dict('records'))
                log_terminal("Database synchronized.")
                st.success("Sync Complete.")

    # --------------------------------------------------------------------------
    # TAB 3: COST ANALYSIS
    # --------------------------------------------------------------------------
    with t_cost:
        st.markdown("### 💰 TRANSPORT COST SIMULATOR")
        c1, c2 = st.columns(2)
        with c1:
            dist = st.number_input("Total Distance (km)", 0, 5000, 500)
            fuel_p = st.number_input("Fuel Price (PLN/L)", 0.0, 10.0, 6.5)
        with c2:
            st.markdown(f"**Calculated for: {v_sel}**")
            total_f = dist * veh['fuel_avg']
            cost_f = total_f * fuel_p
            cost_m = dist * veh['myto_rate'] * 4.3 # PLN
            
            st.markdown(f"""<div class='v-apex-card'>
                Fuel Required: <b>{total_f:.1f} L</b><br>
                Fuel Cost: <b>{cost_f:.2f} PLN</b><br>
                Tolls (Est.): <b>{cost_m:.2f} PLN</b><br><hr>
                <b>TOTAL EST: {(cost_f + cost_m):.2f} PLN</b>
            </div>""", unsafe_allow_html=True)

    # --------------------------------------------------------------------------
    # TAB 4: SYSTEM LOGS
    # --------------------------------------------------------------------------
    with t_admin:
        st.markdown("### ⚙️ TERMINAL LOGS")
        logs = "\n".join(st.session_state.get('terminal_logs', ["System Initialized..."]))
        st.markdown(f'<div class="terminal-view">{logs}</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
