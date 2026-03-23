import streamlit as st
import json
import plotly.graph_objects as go
import math
import pandas as pd
import random
import base64

# =========================================================
# 1. AUTORYZACJA I KONFIGURACJA SECRETS
# =========================================================
def check_vorteza_auth():
    """Zarządza dostępem na podstawie pojedynczego hasła w Secrets."""
    if "v_auth" not in st.session_state:
        st.session_state.v_auth = False

    if not st.session_state.v_auth:
        # Pobieranie hasła z różnych możliwych lokalizacji w Secrets
        try:
            # Próba odczytu 'password' bezpośrednio lub z sekcji 'credentials'
            master_pwd = str(st.secrets.get("password", st.secrets.get("credentials", {}).get("password", "vorteza2026")))
        except Exception:
            st.error("KRYTYCZNY BŁĄD: Brak klucza 'password' w konfiguracji Secrets.")
            return False

        c1, c2, c3 = st.columns([1, 1.5, 1])
        with c2:
            st.markdown("<br><br><br>", unsafe_allow_html=True)
            with st.form("VortezaSecureLogin"):
                st.markdown("<h2 style='text-align:center; color:#B58863;'>VORTEZA SYSTEMS</h2>", unsafe_allow_html=True)
                st.markdown("<p style='text-align:center; font-size:0.8rem; color:#666;'>SECURITY CLEARANCE REQUIRED</p>", unsafe_allow_html=True)
                
                # Tylko pole hasła, zgodnie z Twoją prośbą
                input_pwd = st.text_input("ACCESS KEY", type="password", placeholder="Wprowadź klucz systemowy")
                submit = st.form_submit_button("AUTORYZUJ DOSTĘP")
                
                if submit:
                    if input_pwd == master_pwd:
                        st.session_state.v_auth = True
                        st.rerun()
                    else:
                        st.error("ODMOWA DOSTĘPU: Nieprawidłowy klucz.")
        return False
    return True

# Specyfikacja floty (Parametry techniczne)
VEHICLES = {
    "TIR FTL (Standard)": {"maxWeight": 24000, "L": 1360, "W": 248, "H": 275, "ldm_max": 13.6},
    "Solo 7m (Heavy)": {"maxWeight": 7000, "L": 720, "W": 245, "H": 270, "ldm_max": 7.2},
    "Solo 6m (Medium)": {"maxWeight": 3500, "L": 600, "W": 245, "H": 250, "ldm_max": 6.0},
    "BUS (Express)": {"maxWeight": 1100, "L": 450, "W": 175, "H": 210, "ldm_max": 4.5}
}

# =========================================================
# 2. VORTEZA CORE STYLE (HIGH-END UI)
# =========================================================
def apply_vorteza_ui():
    st.markdown("""
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;700&family=JetBrains+Mono:wght@300&display=swap');
            
            :root {
                --v-copper: #B58863;
                --v-dark-bg: #0A0A0A;
                --v-panel: rgba(18, 18, 18, 0.98);
                --v-text-main: #E0E0E0;
            }

            .stApp { background-color: var(--v-dark-bg); color: var(--v-text-main); font-family: 'Montserrat', sans-serif; }
            
            /* Nagłówki */
            h1, h2, h3 { color: var(--v-copper) !important; text-transform: uppercase; letter-spacing: 4px !important; font-weight: 700 !important; }

            /* Karty VORTEZA */
            .vorteza-card {
                background: var(--v-panel); padding: 2.2rem; border-radius: 2px;
                border-left: 4px solid var(--v-copper); box-shadow: 25px 25px 70px rgba(0,0,0,0.6);
                margin-bottom: 1.8rem; backdrop-filter: blur(12px);
            }

            /* Metryki */
            [data-testid="stMetricValue"] { color: var(--v-copper) !important; font-family: 'JetBrains Mono', monospace !important; font-size: 2.3rem !important; }
            label[data-testid="stWidgetLabel"] { color: var(--v-copper) !important; text-transform: uppercase; font-size: 0.75rem !important; font-weight: 700 !important; letter-spacing: 1px; }

            /* Przyciski */
            .stButton > button {
                background: transparent; color: var(--v-copper); border: 1px solid var(--v-copper);
                border-radius: 0px; padding: 0.8rem 2rem; text-transform: uppercase; letter-spacing: 2px;
                transition: all 0.4s ease; width: 100%; font-weight: 700;
            }
            .stButton > button:hover { background: var(--v-copper); color: black; box-shadow: 0 0 25px rgba(181, 136, 99, 0.4); }

            /* Tabele Contentu */
            .v-table { width: 100%; border-collapse: collapse; margin: 15px 0; }
            .v-table th { color: var(--v-copper); text-align: left; font-size: 0.65rem; text-transform: uppercase; border-bottom: 1px solid #333; padding: 12px; letter-spacing: 1px; }
            .v-table td { padding: 14px 12px; border-bottom: 1px solid #151515; font-size: 0.85rem; color: #BBB; }
            
            /* Info Box */
            .unit-box { background: rgba(181, 136, 99, 0.05); border: 1px solid rgba(181, 136, 99, 0.3); padding: 15px; margin: 10px 0; border-radius: 2px; font-size: 0.8rem; color: #AAA; }
        </style>
    """, unsafe_allow_html=True)

# =========================================================
# 3. SILNIK WIZUALIZACJI 3D (CAD-ENGINE)
# =========================================================
def render_vorteza_3d(vehicle_data, cargo_stacks):
    fig = go.Figure()
    L, W, H = vehicle_data['L'], vehicle_data['W'], vehicle_data['H']

    # --- INFRASTRUKTURA POJAZDU ---
    # Podłoga i Rama
    fig.add_trace(go.Mesh3d(x=[0, L, L, 0], y=[0, 0, W, W], z=[-2, -2, -2, -2], color='#1a1a1a', opacity=1, hoverinfo='skip'))
    
    # Kabina (Industrial Look)
    fig.add_trace(go.Mesh3d(
        x=[-130, 0, 0, -130, -130, 0, 0, -130], y=[0, 0, W, W, 0, 0, W, W],
        z=[0, 0, 0, 0, H*0.8, H*0.8, H*0.8, H*0.8],
        i=[7,0,0,0,4,4,6,6,4,0,3,2], j=[3,4,1,2,5,6,5,2,0,1,6,3], k=[0,7,2,3,6,7,1,1,5,5,7,6],
        color='#050505', opacity=1, name="UNIT_CAB"
    ))

    # Obrys Paki (Miedziane krawędzie)
    edges = [
        ([0, L], [0, 0], [0, 0]), ([0, L], [W, W], [0, 0]), ([0, 0], [0, W], [0, 0]), ([L, L], [0, W], [0, 0]),
        ([0, 0], [0, 0], [0, H]), ([0, 0], [W, W], [0, H]), ([0, L], [0, 0], [H, H]), ([0, L], [W, W], [H, H])
    ]
    for xe, ye, ze in edges:
        fig.add_trace(go.Scatter3d(x=xe, y=ye, z=ze, mode='lines', line=dict(color='#B58863', width=3), hoverinfo='skip'))

    # --- RENDER ŁADUNKU ---
    for s_idx, stack in enumerate(cargo_stacks):
        # Gradacja miedzi dla wizualnego rozróżnienia stosów
        shade = 181 - (s_idx % 5) * 15
        c_color = f'rgb({shade}, {int(shade*0.75)}, {int(shade*0.55)})'
        
        for item in stack['items']:
            x, y, z = stack['x'], stack['y'], item['z']
            dx, dy, dz = item['w_fit'], item['l_fit'], item['height']
            
            # Skrzynia
            fig.add_trace(go.Mesh3d(
                x=[x, x+dx, x+dx, x, x, x+dx, x+dx, x], y=[y, y, y+dy, y+dy, y, y, y+dy, y+dy],
                z=[z, z, z, z, z+dz, z+dz, z+dz, z+dz],
                i=[7,0,0,0,4,4,6,6,4,0,3,2], j=[3,4,1,2,5,6,5,2,0,1,6,3], k=[0,7,2,3,6,7,1,1,5,5,7,6],
                color=c_color, opacity=0.95, name=item['name']
            ))
            # Krawędzie skrzyni (dla separacji)
            fig.add_trace(go.Scatter3d(
                x=[x, x+dx, x+dx, x, x, x, x+dx, x+dx, x, x, x+dx, x+dx, x+dx, x+dx, x, x],
                y=[y, y, y+dy, y+dy, y, y, y, y+dy, y+dy, y+dy, y+dy, y, y, y+dy, y+dy, y],
                z=[z, z, z, z, z, z+dz, z+dz, z, z, z+dz, z+dz, z+dz, z, z, z+dz, z+dz],
                mode='lines', line=dict(color='black', width=1.5), hoverinfo='skip'
            ))

    fig.update_layout(
        scene=dict(aspectmode='data', xaxis_visible=False, yaxis_visible=False, zaxis_visible=False,
                   camera=dict(eye=dict(x=1.7, y=1.7, z=1.1))),
        paper_bgcolor='rgba(0,0,0,0)', margin=dict(l=0, r=0, b=0, t=0), showlegend=False
    )
    return fig

# =========================================================
# 4. LOGIKA PAKOWANIA (V-ENGINE 3.1)
# =========================================================
def vorteza_engine(cargo_list, vehicle):
    # Sortowanie: Stackowalne na dół, potem największa podstawa
    sorted_items = sorted(cargo_list, key=lambda x: (not x.get('canStack', True), x['width']*x['length']), reverse=True)
    
    stacks, failed, weight_sum = [], [], 0
    cx, cy, row_w = 0, 0, 0

    for it in sorted_items:
        if weight_sum + it['weight'] > vehicle['maxWeight']:
            failed.append(it); continue
            
        stacked = False
        if it.get('canStack', True):
            for s in stacks:
                if ((it['width']<=s['w'] and it['length']<=s['l']) or (it['length']<=s['w'] and it['width']<=s['l'])) and (s['curH']+it['height'] <= vehicle['H']):
                    it_c = it.copy(); it_c['z'] = s['curH']; it_c['w_fit'], it_c['l_fit'] = s['w'], s['l']
                    s['items'].append(it_c); s['curH']+=it['height']; weight_sum+=it['weight']; stacked=True; break
        
        if not stacked:
            for fw, fl in [(it['width'], it['length']), (it['length'], it['width'])]:
                if cy + fl <= vehicle['W'] and cx + fw <= vehicle['L']:
                    it_c = it.copy(); it_c['z'] = 0; it_c['w_fit'], it_c['l_fit'] = fw, fl
                    stacks.append({'x':cx, 'y':cy, 'w':fw, 'l':fl, 'curH':it['height'], 'items':[it_c]})
                    cy+=fl; row_w=max(row_w, fw); weight_sum+=it['weight']; stacked=True; break
                elif cx + row_w + fw <= vehicle['L'] and fl <= vehicle['W']:
                    cx+=row_w; cy=0; row_w=fw; it_c = it.copy(); it_c['z'] = 0; it_c['w_fit'], it_c['l_fit'] = fw, fl
                    stacks.append({'x':cx, 'y':cy, 'w':fw, 'l':fl, 'curH':it['height'], 'items':[it_c]})
                    cy+=fl; weight_sum+=it['weight']; stacked=True; break
            if not stacked: failed.append(it)

    ldm = max([s['x'] + s['w'] for s in stacks]) / 100 if stacks else 0
    return stacks, weight_sum, failed, ldm

# =========================================================
# 5. GŁÓWNA APLIKACJA
# =========================================================
def main():
    apply_vorteza_ui()

    if not check_vorteza_auth():
        return

    # --- Nagłówek ---
    h1, h2 = st.columns([4, 1])
    with h1:
        st.markdown("<h1>VORTEZA FLOW</h1>", unsafe_allow_html=True)
        st.markdown("<p style='color:#555; font-size:0.7rem; letter-spacing:2px;'>LOGISTICS CORE v3.1 | PRO EDITION 2026</p>", unsafe_allow_html=True)
    with h2:
        if st.button("LOGOUT"): st.session_state.v_auth = False; st.rerun()

    if 'v_cargo' not in st.session_state: st.session_state.v_cargo = []

    # --- Sidebar Operacyjny ---
    with st.sidebar:
        st.markdown("### KONFIGURACJA JEDNOSTKI")
        v_sel = st.selectbox("FLOTA", list(VEHICLES.keys()))
        v_specs = VEHICLES[v_sel]
        
        st.markdown(f"""<div class='unit-box'>POJEMNOŚĆ: {v_specs['L']}x{v_specs['W']}x{v_specs['H']} cm<br>ŁADOWNOŚĆ: {v_specs['maxWeight']} kg</div>""", unsafe_allow_html=True)
        
        st.divider()
        st.markdown("### MANIFEST ŁADUNKOWY")
        try:
            with open('products.json', 'r', encoding='utf-8') as f: db = json.load(f)
        except: db = []
        
        p_name = st.selectbox("PRODUKT", [p['name'] for p in db], index=None)
        if p_name:
            p_ref = next(p for p in db if p['name'] == p_name)
            ipc = p_ref.get('itemsPerCase', 1)
            st.markdown(f"<div style='font-size:0.7rem; color:#B58863;'>STANDARD: {ipc} szt. / opak.</div>", unsafe_allow_html=True)
            p_qty = st.number_input("SZTUKI", min_value=1, value=ipc)
            n_cases = math.ceil(p_qty / ipc)
            
            if st.button("DODAJ DO MANIFESTU"):
                for i in range(n_cases):
                    case = p_ref.copy()
                    case['p_actual'] = ipc if (i < n_cases - 1 or p_qty % ipc == 0) else (p_qty % ipc)
                    st.session_state.v_cargo.append(case)
                st.toast(f"Dodano {n_cases} opakowań.")

        if st.button("WYCZYŚĆ SYSTEM"): st.session_state.v_cargo = []; st.rerun()

    # --- Panel Wyników ---
    if st.session_state.v_cargo:
        # Statystyki Manifestu
        m1, m2, m3, m4 = st.columns(4)
        total_kg = sum(float(c.get('weight', 0)) for c in st.session_state.v_cargo)
        total_pcs = sum(int(c.get('p_actual', 1)) for c in st.session_state.v_cargo)
        
        m1.metric("OPAKOWANIA", len(st.session_state.v_cargo))
        m2.metric("SZTUKI", total_pcs)
        m3.metric("WAGA", f"{total_kg} KG")
        # Wyliczenie orientacyjne (safety buffer)
        m4.metric("LDM (EST.)", f"{(total_kg/v_specs['maxWeight'])*(v_specs['L']/100):.2f}")

        # Proces Pakowania (Obsługa wielu aut)
        rem_cargo = [dict(c) for c in st.session_state.v_cargo]
        fleet = []
        
        while rem_cargo:
            res_st, res_w, not_p, ldm_r = vorteza_engine(rem_cargo, v_specs)
            if not res_st: 
                st.error("JEDNOSTKA ZBYT DUŻA DLA TEJ FLOTY")
                break
            fleet.append({"stacks": res_st, "weight": res_w, "ldm": ldm_r})
            rem_cargo = not_p

        st.markdown(f"### ASYGNACJA FLOTY: {len(fleet)} POJAZD(Y)")
        
        for idx, truck in enumerate(fleet):
            st.markdown('<div class="vorteza-card">', unsafe_allow_html=True)
            c_3d, c_det = st.columns([2, 1])
            
            with c_3d:
                st.plotly_chart(render_vorteza_3d(v_specs, truck['stacks']), use_container_width=True)
            
            with c_det:
                st.markdown(f"**JEDNOSTKA #{idx+1} | {v_sel}**")
                st.markdown(f"LDM: <span style='color:#B58863;'>{truck['ldm']:.2f}</span> / {v_specs['ldm_max']}", unsafe_allow_html=True)
                st.markdown(f"WAGA: <span style='color:#B58863;'>{truck['weight']} KG</span>", unsafe_allow_html=True)
                
                st.divider()
                st.markdown("**ZAWARTOŚĆ POJAZDU:**")
                t_items = [it['name'] for s in truck['stacks'] for it in s['items']]
                if t_items:
                    sum_df = pd.Series(t_items).value_counts().reset_index()
                    sum_df.columns = ['Produkt', 'Opakowań']
                    
                    html_t = '<table class="v-table"><tr><th>Produkt</th><th>Ilość</th></tr>'
                    for _, r in sum_df.iterrows():
                        html_t += f'<tr><td>{r["Produkt"]}</td><td>{r["Opakowań"]}</td></tr>'
                    html_t += '</table>'
                    st.markdown(html_t, unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="vorteza-card" style="text-align:center; color:#444;">VORTEZA FLOW: READY FOR MANIFEST DATA...</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
