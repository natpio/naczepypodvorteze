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
# 1. GLOBALNA ARCHITEKTURA I KONFIGURACJA SYSTEMOWA
# ==============================================================================
# Wymuszamy stan interfejsu odpowiedni dla stacji roboczej lub terminala mobilnego
st.set_page_config(
    page_title="VORTEZA FLOW | OMNIA v8.0",
    layout="wide",
    initial_sidebar_state="expanded",
    page_icon="🕋"
)

# --- REJESTR FLOTY VORTEZA SYSTEMS ---
# Szczegółowa specyfikacja techniczna jednostek transportowych
FLEET_SPEC = {
    "TIR FTL (Mega)": {
        "max_w": 24000, "L": 1360, "W": 248, "H": 300, 
        "ldm": 13.6, "fuel_avg": 0.30, "myto": 0.22, "tank": 1200
    },
    "TIR FTL (Standard)": {
        "max_w": 24000, "L": 1360, "W": 248, "H": 275, 
        "ldm": 13.6, "fuel_avg": 0.28, "myto": 0.20, "tank": 1000
    },
    "Solo 9m (Heavy)": {
        "max_w": 9000, "L": 920, "W": 245, "H": 270, 
        "ldm": 9.2, "fuel_avg": 0.24, "myto": 0.18, "tank": 500
    },
    "Solo 7m (Medium)": {
        "max_w": 7000, "L": 720, "W": 245, "H": 260, 
        "ldm": 7.2, "fuel_avg": 0.20, "myto": 0.15, "tank": 400
    },
    "BUS (Express XL)": {
        "max_w": 1200, "L": 485, "W": 175, "H": 220, 
        "ldm": 4.8, "fuel_avg": 0.11, "myto": 0.00, "tank": 90
    }
}

# ==============================================================================
# 2. VORTEZA PRESTIGE DESIGN SYSTEM (ADVANCED CSS)
# ==============================================================================
def apply_vorteza_omnia_theme():
    """Wstrzykuje zaawansowany arkusz stylów CSS VORTEZA Omna Edition."""
    st.markdown("""
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;600;700&family=JetBrains+Mono:wght@300;500&display=swap');
            
            :root {
                --v-copper: #B58863;
                --v-copper-dim: rgba(181, 136, 99, 0.4);
                --v-dark-bg: #050505;
                --v-card-bg: rgba(12, 12, 12, 0.99);
                --v-border: rgba(181, 136, 99, 0.2);
                --v-text-gold: #D4AF37;
            }

            /* Global App Base */
            .stApp { 
                background-color: var(--v-dark-bg); 
                color: #F0F0F0; 
                font-family: 'Montserrat', sans-serif; 
            }
            
            /* Sidebar Optimization */
            section[data-testid="stSidebar"] {
                background-color: #080808 !important;
                border-right: 1px solid var(--v-border);
                width: 420px !important;
            }

            /* Omnia High-End Cards */
            .v-omnia-card {
                background: var(--v-card-bg);
                padding: 2.5rem;
                border-radius: 2px;
                border: 1px solid var(--v-border);
                border-left: 10px solid var(--v-copper);
                box-shadow: 0 40px 120px rgba(0,0,0,1);
                margin-bottom: 3rem;
                backdrop-filter: blur(25px);
            }

            /* Typography */
            h1, h2, h3 { 
                color: var(--v-copper) !important; 
                text-transform: uppercase; 
                letter-spacing: 8px !important; 
                font-weight: 700 !important; 
                text-shadow: 4px 4px 8px rgba(0,0,0,0.8);
            }
            .v-sub { color: #555; font-size: 0.7rem; letter-spacing: 3px; font-weight: 400; }

            /* Metrics & KPI */
            [data-testid="stMetricValue"] { 
                color: var(--v-copper) !important; 
                font-family: 'JetBrains Mono', monospace !important; 
                font-size: 3rem !important;
                font-weight: 500 !important;
            }

            /* Buttons & Interactivity */
            .stButton > button {
                background: rgba(10, 10, 10, 0.8);
                color: var(--v-copper);
                border: 1px solid var(--v-copper);
                padding: 1.2rem 2.5rem;
                text-transform: uppercase;
                letter-spacing: 5px;
                font-weight: 700;
                width: 100%;
                transition: 0.5s cubic-bezier(0.19, 1, 0.22, 1);
            }
            .stButton > button:hover {
                background: var(--v-copper);
                color: black;
                box-shadow: 0 0 60px rgba(181, 136, 99, 0.7);
                transform: scale(1.02);
            }

            /* Pro Tables */
            .v-table-pro { width: 100%; border-collapse: collapse; margin-top: 30px; }
            .v-table-pro th { 
                color: var(--v-copper); 
                text-align: left; 
                font-size: 0.7rem; 
                text-transform: uppercase; 
                border-bottom: 2px solid #333; 
                padding: 20px; 
                letter-spacing: 2px;
            }
            .v-table-pro td { padding: 18px 20px; border-bottom: 1px solid #151515; font-size: 0.9rem; color: #AAA; }

            /* Inventory Tooltip */
            .unit-box {
                background: rgba(181, 136, 99, 0.02);
                border: 1px solid var(--v-copper-dim);
                padding: 15px;
                margin: 15px 0;
                font-size: 0.8rem;
                color: #888;
                border-radius: 1px;
            }
        </style>
    """, unsafe_allow_html=True)

# ==============================================================================
# 3. KONTROLA DOSTĘPU (SECURE GATEWAY)
# ==============================================================================
def authenticate_vorteza():
    """Zarządza autoryzacją dostępu na podstawie hasła systemowego."""
    if "authorized" not in st.session_state:
        st.session_state.authorized = False

    if not st.session_state.authorized:
        try:
            # Hasło pobierane z Streamlit Secrets
            sys_pass = str(st.secrets.get("password", "vorteza2026"))
        except:
            sys_pass = "vorteza2026"

        st.markdown("<br><br><br>", unsafe_allow_html=True)
        c1, c2, c3 = st.columns([1, 1.8, 1])
        with c2:
            with st.form("OmniaAuth"):
                st.markdown("<h2 style='text-align:center;'>VORTEZA LOGIN</h2>", unsafe_allow_html=True)
                st.markdown("<p style='text-align:center; color:#444; font-size:0.7rem;'>SECURITY CLEARANCE REQUIRED</p>", unsafe_allow_html=True)
                k_in = st.text_input("GOLIATH MASTER KEY", type="password")
                if st.form_submit_button("UNLOCK TERMINAL"):
                    if k_in == sys_pass:
                        st.session_state.authorized = True
                        st.rerun()
                    else:
                        st.error("ACCESS DENIED: INCORRECT CORE KEY")
        return False
    return True

# ==============================================================================
# 4. CHROMATYCZNY SILNIK KOLORÓW (PRODUCT COLOR ENGINE)
# ==============================================================================
def get_vorteza_color(name):
    """Generuje stabilny, unikalny kolor dla każdego produktu bazując na jego nazwie."""
    # Paleta "Vorteza Industrial" - odcienie miedzi, złota, szarości i głębokich błękitów
    palette = [
        "#B58863", "#D4AF37", "#8E6A4D", "#5E4633", "#A67C52", 
        "#4A4A4A", "#2F2F2F", "#1A252F", "#2C3E50", "#34495E",
        "#7F8C8D", "#95A5A6", "#BDC3C7", "#7E4A35", "#C0392B",
        "#D35400", "#F39C12", "#27AE60", "#2980B9", "#8E44AD"
    ]
    # Używamy hasha nazwy produktu jako ziarna dla generatora, aby kolor był zawsze ten sam
    random.seed(sum(ord(c) for c in name))
    return random.choice(palette)

# ==============================================================================
# 5. RENDERER 3D CAD-OMNIA (VISUAL ENGINE)
# ==============================================================================
def render_omnia_3d(vehicle, stacks):
    """Generuje zaawansowany model 3D naczepy z unikalnym kolorowaniem produktów."""
    fig = go.Figure()
    L, W, H = vehicle['L'], vehicle['W'], vehicle['H']

    # --- INFRASTRUKTURA POJAZDU ---
    # Podstawa naczepy (Chassis)
    fig.add_trace(go.Mesh3d(
        x=[0, L, L, 0], y=[0, 0, W, W], z=[-5, -5, -5, -5],
        color='#111', opacity=1, hoverinfo='skip'
    ))
    
    # Koła (Modelowanie techniczne)
    wheel_pos = [150, 220, 290, L-100, L-170]
    for wp in wheel_pos:
        if wp < L:
            for side in [-25, W+15]:
                fig.add_trace(go.Mesh3d(
                    x=[wp-35, wp+35, wp+35, wp-35], y=[side, side, side+10, side+10], 
                    z=[-40, -40, -5, -5], color='#000', opacity=1, hoverinfo='skip'
                ))

    # Kabina (Industrial Block CAD)
    fig.add_trace(go.Mesh3d(
        x=[-160, 0, 0, -160, -160, 0, 0, -160],
        y=[-15, -15, W+15, W+15, -15, -15, W+15, W+15],
        z=[0, 0, 0, 0, H*0.9, H*0.9, H*0.9, H*0.9],
        i=[7,0,0,0,4,4,6,6,4,0,3,2], j=[3,4,1,2,5,6,5,2,0,1,6,3], k=[0,7,2,3,6,7,1,1,5,5,7,6],
        color='#050505', opacity=1, name="COMMAND_CAB"
    ))

    # Klatka Naczepy (Miedziane krawędzie konstrukcyjne)
    cage = [
        ([0, L], [0, 0], [0, 0]), ([0, L], [W, W], [0, 0]), ([0, 0], [0, W], [0, 0]), ([L, L], [0, W], [0, 0]),
        ([0, 0], [0, 0], [0, H]), ([0, 0], [W, W], [0, H]), ([0, L], [0, 0], [H, H]), ([0, L], [W, W], [H, H]),
        ([L, L], [0, 0], [0, H]), ([L, L], [W, W], [0, H])
    ]
    for xc, yc, zc in cage:
        fig.add_trace(go.Scatter3d(x=xc, y=yc, z=zc, mode='lines', line=dict(color='#B58863', width=5), hoverinfo='skip'))

    # --- RENDER ŁADUNKU (DYNAMIC COLORS) ---
    for stack in stacks:
        for item in stack['items']:
            x, y, z = stack['x'], stack['y'], item['z']
            dx, dy, dz = item['w_fit'], item['l_fit'], item['height']
            
            # Pobieramy unikalny kolor dla tego produktu
            p_color = get_vorteza_color(item['name'])
            
            # Bryła produktu
            fig.add_trace(go.Mesh3d(
                x=[x,x+dx,x+dx,x,x,x+dx,x+dx,x], y=[y,y,y+dy,y+dy,y,y,y+dy,y+dy], 
                z=[z,z,z,z,z+dz,z+dz,z+dz,z+dz],
                i=[7,0,0,0,4,4,6,6,4,0,3,2], j=[3,4,1,2,5,6,5,2,0,1,6,3], k=[0,7,2,3,6,7,1,1,5,5,7,6],
                color=p_color, opacity=0.98, name=item['name']
            ))
            # Kontur dla czytelności (Krawędzie)
            fig.add_trace(go.Scatter3d(
                x=[x,x+dx,x+dx,x,x,x,x+dx,x+dx,x,x,x+dx,x+dx,x+dx,x+dx,x,x],
                y=[y,y,y+dy,y+dy,y,y,y,y+dy,y+dy,y+dy,y+dy,y,y,y+dy,y+dy,y],
                z=[z,z,z,z,z,z+dz,z+dz,z,z,z+dz,z+dz,z+dz,z,z,z+dz,z+dz],
                mode='lines', line=dict(color='black', width=1.5), hoverinfo='skip'
            ))

    fig.update_layout(
        scene=dict(
            aspectmode='data', xaxis_visible=False, yaxis_visible=False, zaxis_visible=False,
            camera=dict(eye=dict(x=2.2, y=2.2, z=1.5)), bgcolor='rgba(0,0,0,0)'
        ),
        paper_bgcolor='rgba(0,0,0,0)', margin=dict(l=0, r=0, b=0, t=0), showlegend=False
    )
    return fig

# ==============================================================================
# 6. RDZEŃ OPTYMALIZACJI (V-ENGINE 8.0)
# ==============================================================================
class V8Engine:
    """Zaawansowany algorytm bin packing z kontrolą wielu parametrów."""
    
    @staticmethod
    def pack(cargo, veh):
        # Priorytetyzacja: 1. Brak możliwości piętrowania (ciężkie), 2. Pole powierzchni (L*W)
        sorted_items = sorted(cargo, key=lambda x: (not x.get('canStack', True), x['width']*x['length']), reverse=True)
        
        stacks, failed, weight_sum = [], [], 0
        cx, cy, current_row_max_w = 0, 0, 0

        for it in sorted_items:
            # Sprawdzenie masy dopuszczalnej
            if weight_sum + it['weight'] > veh['max_w']:
                failed.append(it); continue
            
            # Próba piętrowania (Stacking Logic)
            stacked = False
            if it.get('canStack', True):
                for s in stacks:
                    # Sprawdzenie wymiarów z uwzględnieniem rotacji 90 st.
                    dim_match = (it['width'] <= s['w'] and it['length'] <= s['l']) or (it['length'] <= s['w'] and it['width'] <= s['l'])
                    if dim_match and (s['curH'] + it['height'] <= veh['H']):
                        it_c = it.copy(); it_c['z'] = s['curH']
                        it_c['w_fit'], it_c['l_fit'] = s['w'], s['l']
                        s['items'].append(it_c); s['curH'] += it['height']
                        weight_sum += it['weight']; stacked = True; break
            
            if stacked: continue

            # Próba zajęcia nowej powierzchni podłogi (Floor Logic)
            placed = False
            orientations = [(it['width'], it['length']), (it['length'], it['width'])]
            for fw, fl in orientations:
                if cy + fl <= veh['W'] and cx + fw <= veh['L']:
                    it_c = it.copy(); it_c['z'] = 0; it_c['w_fit'], it_c['l_fit'] = fw, fl
                    stacks.append({'x':cx, 'y':cy, 'w':fw, 'l':fl, 'curH':it['height'], 'items':[it_c]})
                    cy += fl; current_row_max_w = max(current_row_max_w, fw); weight_sum += it['weight']; placed = True; break
                elif cx + current_row_max_w + fw <= veh['L'] and fl <= veh['W']:
                    cx += current_row_max_w; cy = 0; current_row_max_w = fw
                    it_c = it.copy(); it_c['z'] = 0; it_c['w_fit'], it_c['l_fit'] = fw, fl
                    stacks.append({'x':cx, 'y':cy, 'w':fw, 'l':fl, 'curH':it['height'], 'items':[it_c]})
                    cy += fl; weight_sum += it['weight']; placed = True; break
            
            if not placed: failed.append(it)
        
        ldm_real = max([s['x'] + s['w'] for s in stacks]) / 100 if stacks else 0
        return stacks, weight_sum, failed, ldm_real

# ==============================================================================
# 7. ZARZĄDZANIE DANYMI (INVENTORY MODULE)
# ==============================================================================
def load_db():
    try:
        with open('products.json', 'r', encoding='utf-8') as f: return json.load(f)
    except: return []

def save_db(data):
    with open('products.json', 'w', encoding='utf-8') as f: json.dump(data, f, indent=4, ensure_ascii=False)

# ==============================================================================
# 8. GŁÓWNA APLIKACJA (OMNIA CONTROL CENTER)
# ==============================================================================
def main():
    apply_vorteza_omnia_theme()
    
    if not authenticate_vorteza(): return

    # Inicjalizacja Manifestu w sesji
    if 'v_manifest' not in st.session_state: st.session_state.v_manifest = []
    inventory = load_db()

    # --- TOP NAVBAR ---
    h_col1, h_col2 = st.columns([5, 1])
    with h_col1:
        st.markdown("<h1>VORTEZA OMNIA FLOW</h1>", unsafe_allow_html=True)
        st.markdown(f"<p class='v-sub'>INTEGRATED COMMAND TERMINAL | v8.0.01 | STATUS: ONLINE</p>", unsafe_allow_html=True)
    with h_col2:
        if st.button("TERMINATE SESSION"):
            st.session_state.authorized = False; st.rerun()

    # --- SIDEBAR CONTROL ---
    with st.sidebar:
        st.markdown("### 🛰️ COMMAND CENTER")
        v_sel_name = st.selectbox("SELECT FLEET UNIT", list(FLEET_SPEC.keys()))
        veh_active = FLEET_SPEC[v_sel_name]
        
        st.markdown(f"""<div class='unit-box'>
            <b>UNIT SPECS:</b><br>
            VOLUME: {veh_active['L']}x{veh_active['W']}x{veh_active['H']} cm<br>
            PAYLOAD: {veh_active['max_w']} kg<br>
            LDM: {veh_active['ldm']}
        </div>""", unsafe_allow_html=True)
        
        st.divider()
        st.markdown("### 📥 MANIFEST INPUT")
        p_names = [p['name'] for p in inventory]
        sel_p_name = st.selectbox("BROWSE INVENTORY", p_names, index=None)
        
        if sel_p_name:
            p_obj = next(p for p in inventory if p['name'] == sel_p_name)
            ipc = p_obj.get('itemsPerCase', 1)
            st.markdown(f"<p style='color:var(--v-copper); font-size:0.7rem;'>PACKAGING: {ipc} pcs/case</p>", unsafe_allow_html=True)
            in_qty = st.number_input("TOTAL PCS TO SHIP", min_value=1, value=ipc)
            n_cases = math.ceil(in_qty / ipc)
            
            if st.button("APPEND TO MANIFEST", type="primary"):
                for i in range(n_cases):
                    unit = p_obj.copy()
                    # Przeliczenie realnej liczby sztuk w każdym opakowaniu
                    unit['p_actual'] = ipc if (i < n_cases - 1 or in_qty % ipc == 0) else (in_qty % ipc)
                    st.session_state.v_manifest.append(unit)
                st.toast(f"Synchronized: {n_cases} cases added.")

        if st.button("PURGE MANIFEST DATA"):
            st.session_state.v_manifest = []; st.rerun()

    # --- MAIN VIEW TABS ---
    tab_plan, tab_inv, tab_fin, tab_ana = st.tabs(["📊 PLANNER", "📦 INVENTORY", "💰 COSTS", "📈 ANALYTICS"])

    # --------------------------------------------------------------------------
    # TAB 1: PLANNER ZAŁADUNKU
    # --------------------------------------------------------------------------
    with tab_plan:
        if st.session_state.v_manifest:
            # Metrics Dash
            total_w = sum(float(u['weight']) for u in st.session_state.v_manifest)
            total_pcs = sum(int(u.get('p_actual', 1)) for u in st.session_state.v_manifest)
            
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("CASES", len(st.session_state.v_manifest))
            m2.metric("PCS TOTAL", total_pcs)
            m3.metric("GROSS WEIGHT", f"{total_w} kg")
            m4.metric("WEIGHT UTIL", f"{(total_w/veh_active['max_w'])*100:.1f}%")

            # Packing Execution
            rem_cargo = [dict(u) for u in st.session_state.v_manifest]
            fleet_plan = []
            
            while rem_cargo:
                stacks, w_res, not_p, ldm_r = V8Engine.pack(rem_cargo, veh_active)
                if not stacks: break
                fleet_plan.append({"stacks": stacks, "weight": w_res, "ldm": ldm_r})
                rem_cargo = not_p

            st.markdown(f"### ASSIGNED FLEET UNITS: {len(fleet_plan)}")
            
            for idx, unit in enumerate(fleet_plan):
                st.markdown(f'<div class="v-omnia-card">', unsafe_allow_html=True)
                st.markdown(f"### UNIT #{idx+1} | {v_sel_name}", unsafe_allow_html=True)
                
                c_3d, c_dat = st.columns([2, 1])
                with c_3d:
                    st.plotly_chart(render_omnia_3d(veh_active, unit['stacks']), use_container_width=True)
                with c_dat:
                    st.markdown("**OPERATIONAL PERFORMANCE**")
                    st.write(f"Mass Utilization: {(unit['weight']/veh_active['max_w'])*100:.1f}%")
                    st.write(f"LDM Occupied: {unit['ldm']:.2f} m")
                    
                    st.divider()
                    st.markdown("**DETAILED PACKING LIST**")
                    u_items = [it['name'] for s in unit['stacks'] for it in s['items']]
                    if u_items:
                        counts = pd.Series(u_items).value_counts().reset_index()
                        counts.columns = ['Product', 'Cases']
                        
                        html = '<table class="v-table-pro"><tr><th>SKU</th><th>UNIT QTY</th></tr>'
                        for _, r in counts.iterrows():
                            html += f'<tr><td>{r["Product"]}</td><td>{r["Cases"]}</td></tr>'
                        st.markdown(html+'</table>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.info("Manifest empty. Add items via Command Center.")

    # --------------------------------------------------------------------------
    # TAB 2: INVENTORY MANAGEMENT
    # --------------------------------------------------------------------------
    with tab_inv:
        st.markdown("### 📦 PRODUCT CORE DATABASE")
        
        with st.expander("➕ DEFINE NEW PRODUCT SKR"):
            with st.form("AddP"):
                f_name = st.text_input("Product Name / SKU")
                c1, c2, c3 = st.columns(3)
                f_l = c1.number_input("L (cm)", 120)
                f_w = c2.number_input("W (cm)", 80)
                f_h = c3.number_input("H (cm)", 100)
                f_weight = st.number_input("Weight (kg)", 50)
                f_ipc = st.number_input("Items/Case", 1)
                f_stk = st.checkbox("Stackable Unit", True)
                if st.form_submit_button("COMMIT TO CORE"):
                    inventory.append({"name": f_name, "length": f_l, "width": f_w, "height": f_h, "weight": f_weight, "itemsPerCase": f_ipc, "canStack": f_stk})
                    save_db(inventory)
                    st.success("Synchronized."); st.rerun()

        st.divider()
        if inventory:
            df_i = pd.DataFrame(inventory)
            ed_df = st.data_editor(df_i, use_container_width=True, num_rows="dynamic")
            if st.button("PUSH DATABASE CHANGES"):
                save_db(ed_df.to_dict('records'))
                st.success("Global database updated.")
        else:
            st.warning("Database empty.")

    # --------------------------------------------------------------------------
    # TAB 3: FINANCIAL ANALYSIS
    # --------------------------------------------------------------------------
    with tab_fin:
        st.markdown("### 💰 TRANSPORT COST INTELLIGENCE")
        c1, c2 = st.columns(2)
        with c1:
            st.markdown('<div class="v-omnia-card">', unsafe_allow_html=True)
            dist = st.number_input("Total Route Distance (km)", 100, 5000, 1000)
            fuel_price = st.number_input("ON Price (PLN/L)", 5.0, 10.0, 6.45)
            st.markdown('</div>', unsafe_allow_html=True)
        with c2:
            st.markdown('<div class="v-omnia-card">', unsafe_allow_html=True)
            total_fuel = dist * veh_active['fuel_avg']
            fuel_cost = total_fuel * fuel_price
            tolls = dist * veh_active['myto'] * 4.35 # Przelicznik EUR->PLN
            
            st.markdown(f"**Calculated for: {v_sel_name}**")
            st.write(f"Fuel Consumption: {total_fuel:.1f} L")
            st.write(f"Fuel Cost: {fuel_cost:.2f} PLN")
            st.write(f"EU Tolls (Est): {tolls:.2f} PLN")
            st.divider()
            st.markdown(f"#### TOTAL OPERATING COST: <span style='color:var(--v-copper);'>{(fuel_cost + tolls):,.2f} PLN</span>", unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

    # --------------------------------------------------------------------------
    # TAB 4: ADVANCED ANALYTICS
    # --------------------------------------------------------------------------
    with tab_ana:
        st.markdown("### 📈 FLEET PERFORMANCE DATA")
        if st.session_state.v_manifest:
            an_df = pd.DataFrame(st.session_state.v_manifest)
            c1, c2 = st.columns(2)
            with c1:
                fig_pie = px.pie(an_df, names='name', title="Weight Share per SKU", hole=0.5, color_discrete_sequence=px.colors.sequential.copper)
                st.plotly_chart(fig_pie, use_container_width=True)
            with c2:
                fig_bar = px.bar(an_df, x='name', y='weight', title="Mass Contribution (KG)", color='weight', color_continuous_scale='copper')
                st.plotly_chart(fig_bar, use_container_width=True)
        else:
            st.info("No data in manifest for analysis.")

if __name__ == "__main__":
    main()
