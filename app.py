import streamlit as st
import json
import plotly.graph_objects as go
import math
import pandas as pd
import random
import base64
from datetime import datetime

# ==============================================================================
# 1. GLOBALNA KONFIGURACJA SYSTEMU
# ==============================================================================
st.set_page_config(
    page_title="VORTEZA FLOW | TITAN v5.0",
    layout="wide",
    initial_sidebar_state="expanded",
    page_icon="🚛"
)

# --- KONFIGURACJA FLOTY ---
# Dane techniczne naczep zgodne ze standardami EU
VEHICLE_CONFIG = {
    "TIR FTL (Standard)": {
        "max_w": 24000, "L": 1360, "W": 248, "H": 275, 
        "ldm_total": 13.6, "color": "#1a1a1a", "desc": "Naczepa standardowa kurtynowa"
    },
    "Solo 7m (Heavy)": {
        "max_w": 7000, "L": 720, "W": 245, "H": 270, 
        "ldm_total": 7.2, "color": "#2c3e50", "desc": "Podwozie ciężarowe ciężkie"
    },
    "Solo 6m (Medium)": {
        "max_w": 3500, "L": 600, "W": 245, "H": 250, 
        "ldm_total": 6.0, "color": "#34495e", "desc": "Dystrybucja miejska / średnia"
    },
    "BUS (Express)": {
        "max_w": 1100, "L": 450, "W": 175, "H": 210, 
        "ldm_total": 4.5, "color": "#000000", "desc": "Transport ekspresowy / kurierski"
    }
}

# ==============================================================================
# 2. VORTEZA PRESTIGE UI (CUSTOM CSS & THEMING)
# ==============================================================================
def apply_vorteza_styles():
    st.markdown("""
        <style>
            /* Import czcionek premium */
            @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;700&family=JetBrains+Mono:wght@300&display=swap');
            
            :root {
                --v-copper: #B58863;
                --v-gold: #D4AF37;
                --v-dark-base: #080808;
                --v-panel-bg: rgba(15, 15, 15, 0.98);
                --v-text-primary: #EAEAEA;
                --v-text-secondary: #888888;
            }

            /* Globalne ustawienia tła i czcionek */
            .stApp {
                background-color: var(--v-dark-base);
                color: var(--v-text-primary);
                font-family: 'Montserrat', sans-serif;
            }

            /* Nagłówki VORTEZA */
            h1, h2, h3 {
                color: var(--v-copper) !important;
                text-transform: uppercase;
                letter-spacing: 4px !important;
                font-weight: 700 !important;
                margin-bottom: 1rem !important;
            }

            /* Sidebar Design */
            section[data-testid="stSidebar"] {
                background-color: #0d0d0d !important;
                border-right: 1px solid #222;
                width: 350px !important;
            }

            /* Karty wynikowe (Glassmorphism) */
            .v-card {
                background: var(--v-panel-bg);
                padding: 2.5rem;
                border-radius: 4px;
                border-left: 5px solid var(--v-copper);
                box-shadow: 20px 20px 50px rgba(0,0,0,0.7);
                margin-bottom: 2rem;
                backdrop-filter: blur(15px);
            }

            /* Metryki / KPI */
            [data-testid="stMetricValue"] {
                color: var(--v-copper) !important;
                font-family: 'JetBrains Mono', monospace !important;
                font-size: 2.4rem !important;
                font-weight: 300 !important;
            }
            [data-testid="stMetricLabel"] {
                color: var(--v-text-secondary) !important;
                text-transform: uppercase;
                letter-spacing: 2px;
            }

            /* Przyciski operacyjne */
            .stButton > button {
                background: transparent;
                color: var(--v-copper);
                border: 1px solid var(--v-copper);
                border-radius: 0px;
                padding: 1rem 2rem;
                text-transform: uppercase;
                letter-spacing: 3px;
                font-weight: 700;
                transition: 0.4s all;
                width: 100%;
            }
            .stButton > button:hover {
                background: var(--v-copper);
                color: black;
                box-shadow: 0 0 30px rgba(181, 136, 99, 0.5);
                border: 1px solid var(--v-copper);
            }

            /* Tabele systemowe */
            .v-table {
                width: 100%;
                border-collapse: collapse;
                margin-top: 15px;
            }
            .v-table th {
                color: var(--v-copper);
                text-align: left;
                font-size: 0.7rem;
                text-transform: uppercase;
                border-bottom: 1px solid #333;
                padding: 12px;
            }
            .v-table td {
                padding: 12px;
                border-bottom: 1px solid #1a1a1a;
                font-size: 0.85rem;
                color: #ccc;
            }

            /* Pasek ładowania / Info box */
            .info-box {
                background: rgba(181, 136, 99, 0.05);
                border: 1px solid rgba(181, 136, 99, 0.2);
                padding: 15px;
                margin: 10px 0;
                font-size: 0.8rem;
                color: #999;
                border-radius: 3px;
            }
        </style>
    """, unsafe_allow_html=True)

# ==============================================================================
# 3. ZABEZPIECZENIA I LOGIN (SINGLE PASSWORD ACCESS)
# ==============================================================================
def check_access():
    if "authorized" not in st.session_state:
        st.session_state.authorized = False

    if not st.session_state.authorized:
        # Pobieranie klucza z Secrets (fallback do domyślnego dla testów lokalnych)
        try:
            sys_pwd = str(st.secrets.get("password", "vorteza2026"))
        except:
            sys_pwd = "vorteza2026"

        c1, c2, c3 = st.columns([1, 1.5, 1])
        with c2:
            st.markdown("<br><br><br><br>", unsafe_allow_html=True)
            with st.form("VortezaAuth"):
                st.markdown("<h2 style='text-align:center;'>SYSTEM AUTHORIZATION</h2>", unsafe_allow_html=True)
                pwd_input = st.text_input("ENTER SYSTEM KEY", type="password")
                if st.form_submit_button("ACCESS INTERFACE"):
                    if pwd_input == sys_pwd:
                        st.session_state.authorized = True
                        st.rerun()
                    else:
                        st.error("ACCESS DENIED: INVALID KEY")
        return False
    return True

# ==============================================================================
# 4. SILNIK WIZUALIZACJI 3D CAD-PRO
# ==============================================================================
def render_3d_transport(vehicle, stacks):
    fig = go.Figure()
    L, W, H = vehicle['L'], vehicle['W'], vehicle['H']

    # --- KONSTRUKCJA NACZEPY ---
    # Podłoga (Rama główna)
    fig.add_trace(go.Mesh3d(
        x=[0, L, L, 0], y=[0, 0, W, W], z=[-3, -3, -3, -3],
        color='#111111', opacity=1, hoverinfo='skip'
    ))
    
    # Kabina kierowcy (Zgeometryzowana bryła)
    fig.add_trace(go.Mesh3d(
        x=[-140, 0, 0, -140, -140, 0, 0, -140],
        y=[0, 0, W, W, 0, 0, W, W],
        z=[0, 0, 0, 0, H*0.8, H*0.8, H*0.8, H*0.8],
        i=[7,0,0,0,4,4,6,6,4,0,3,2], j=[3,4,1,2,5,6,5,2,0,1,6,3], k=[0,7,2,3,6,7,1,1,5,5,7,6],
        color='#050505', opacity=1, name="KABINA"
    ))

    # Klatka naczepy (Miedziane krawędzie konstrukcyjne)
    cage_lines = [
        ([0, L], [0, 0], [0, 0]), ([0, L], [W, W], [0, 0]),
        ([0, 0], [0, W], [0, 0]), ([L, L], [0, W], [0, 0]),
        ([0, 0], [0, 0], [0, H]), ([0, 0], [W, W], [0, H]),
        ([0, L], [0, 0], [H, H]), ([0, L], [W, W], [H, H]),
        ([L, L], [0, 0], [0, H]), ([L, L], [W, W], [0, H])
    ]
    for xc, yc, zc in cage_lines:
        fig.add_trace(go.Scatter3d(
            x=xc, y=yc, z=zc, mode='lines', 
            line=dict(color='#B58863', width=4), hoverinfo='skip'
        ))

    # --- RENDER ŁADUNKU ---
    for s_idx, stack in enumerate(stacks):
        # Generowanie barw w palecie VORTEZA (odcienie miedzi i brązu)
        base_color = 181 - (s_idx % 6) * 12
        it_color = f'rgb({base_color}, {int(base_color*0.75)}, {int(base_color*0.55)})'
        
        for item in stack['items']:
            x0, y0, z0 = stack['x'], stack['y'], item['z']
            dx, dy, dz = item['w_fit'], item['l_fit'], item['height']
            
            # Główna bryła paczki
            fig.add_trace(go.Mesh3d(
                x=[x0, x0+dx, x0+dx, x0, x0, x0+dx, x0+dx, x0],
                y=[y0, y0, y0+dy, y0+dy, y0, y0, y0+dy, y0+dy],
                z=[z0, z0, z0, z0, z0+dz, z0+dz, z0+dz, z0+dz],
                i=[7,0,0,0,4,4,6,6,4,0,3,2], j=[3,4,1,2,5,6,5,2,0,1,6,3], k=[0,7,2,3,6,7,1,1,5,5,7,6],
                color=it_color, opacity=0.95, name=item['name']
            ))
            
            # Krawędzie paczki (dla separacji wizualnej)
            fig.add_trace(go.Scatter3d(
                x=[x0, x0+dx, x0+dx, x0, x0, x0, x0+dx, x0+dx, x0, x0, x0+dx, x0+dx, x0+dx, x0+dx, x0, x0],
                y=[y0, y0, y0+dy, y0+dy, y0, y0, y0, y0+dy, y0+dy, y0+dy, y0+dy, y0, y0, y0+dy, y0+dy, y0],
                z=[z0, z0, z0, z0, z0, z0+dz, z0+dz, z0, z0, z0+dz, z0+dz, z0+dz, z0, z0, z0+dz, z0+dz],
                mode='lines', line=dict(color='black', width=1.5), hoverinfo='skip'
            ))

    fig.update_layout(
        scene=dict(
            aspectmode='data',
            xaxis_visible=False, yaxis_visible=False, zaxis_visible=False,
            camera=dict(eye=dict(x=1.8, y=1.8, z=1.2))
        ),
        paper_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=0, r=0, b=0, t=0),
        showlegend=False
    )
    return fig

# ==============================================================================
# 5. ZAAWANSOWANY SILNIK PAKOWANIA (V-ENGINE 5.0)
# ==============================================================================
def v_engine_core(cargo_units, vehicle):
    """
    Optymalizacja 3D Bin Packing z obsługą rotacji, piętrowania i limitów masy.
    """
    # Sortowanie: najpierw te, których nie można piętrować, potem pole podstawy (FFD)
    sorted_cargo = sorted(cargo_units, key=lambda x: (not x.get('canStack', True), x['width']*x['length']), reverse=True)
    
    placed_stacks = []
    failed_items = []
    current_weight = 0
    
    # Parametry rozmieszczenia
    cx, cy, current_row_width = 0, 0, 0

    for item in sorted_cargo:
        if current_weight + item['weight'] > vehicle['max_w']:
            failed_items.append(item); continue
            
        stacked = False
        # 1. PRÓBA PIĘTROWANIA (Stacking)
        if item.get('canStack', True):
            for s in placed_stacks:
                # Sprawdzanie czy wymiary pasują (tolerancja rotacji 90 stopni)
                can_fit = (item['width'] <= s['w'] and item['length'] <= s['l']) or \
                          (item['length'] <= s['w'] and item['width'] <= s['l'])
                
                if can_fit and (s['curH'] + item['height'] <= vehicle['H']):
                    it_copy = item.copy()
                    it_copy['z'] = s['curH']
                    it_copy['w_fit'], it_copy['l_fit'] = s['w'], s['l']
                    s['items'].append(it_copy)
                    s['curH'] += item['height']
                    current_weight += item['weight']
                    stacked = True; break
        
        if stacked: continue

        # 2. PRÓBA POŁOŻENIA NA PODŁODZE (Floor placement + Rotation)
        placed = False
        orientations = [(item['width'], item['length']), (item['length'], item['width'])]
        
        for fw, fl in orientations:
            # Sprawdzenie w aktualnym rzędzie (Y)
            if cy + fl <= vehicle['W'] and cx + fw <= vehicle['L']:
                it_c = item.copy(); it_c['z'] = 0; it_c['w_fit'], it_c['l_fit'] = fw, fl
                placed_stacks.append({'x': cx, 'y': cy, 'w': fw, 'l': fl, 'curH': item['height'], 'items': [it_c]})
                cy += fl; current_row_width = max(current_row_width, fw)
                current_weight += item['weight']; placed = True; break
            # Sprawdzenie w nowym rzędzie (X)
            elif cx + current_row_width + fw <= vehicle['L'] and fl <= vehicle['W']:
                cx += current_row_width; cy = 0; current_row_width = fw
                it_c = item.copy(); it_c['z'] = 0; it_c['w_fit'], it_c['l_fit'] = fw, fl
                placed_stacks.append({'x': cx, 'y': cy, 'w': fw, 'l': fl, 'curH': item['height'], 'items': [it_c]})
                cy += fl; current_weight += item['weight']; placed = True; break
        
        if not placed: failed_items.append(item)

    # Obliczanie realnego LDM (Longest X + Width of that stack)
    ldm_real = (max([s['x'] + s['w'] for s in placed_stacks]) / 100) if placed_stacks else 0
    return placed_stacks, current_weight, failed_items, ldm_real

# ==============================================================================
# 6. GŁÓWNA ARCHITEKTURA APLIKACJI
# ==============================================================================
def main():
    apply_vorteza_styles()
    
    if not check_access():
        return

    # --- NAGŁÓWEK SYSTEMOWY ---
    col_h1, col_h2 = st.columns([4, 1])
    with col_h1:
        st.markdown("<h1>VORTEZA FLOW</h1>", unsafe_allow_html=True)
        st.markdown(f"<p style='color:#666; letter-spacing:2px; font-size:0.75rem;'>LOGISTICS MANAGEMENT INTERFACE | v5.0 TITAN | {datetime.now().strftime('%d.%m.%Y')}</p>", unsafe_allow_html=True)
    with col_h2:
        if st.button("TERMINATE SESSION"):
            st.session_state.authorized = False; st.rerun()

    # Inicjalizacja Manifestu
    if 'v_manifest' not in st.session_state:
        st.session_state.v_manifest = []

    # --- SIDEBAR: KONTROLA OPERACJI ---
    with st.sidebar:
        st.markdown("### 🛠️ KONFIGURACJA")
        sel_veh_name = st.selectbox("POJAZD DOCELOWY", list(VEHICLE_CONFIG.keys()))
        veh = VEHICLE_CONFIG[sel_veh_name]
        
        st.markdown(f"""
            <div class="info-box">
                TYP: {veh['desc']}<br>
                WYMIARY: {veh['L']}x{veh['W']}x{veh['H']} cm<br>
                LIMIT MASY: {veh['max_w']} kg
            </div>
        """, unsafe_allow_html=True)
        
        st.divider()
        st.markdown("### 📥 DODAJ DO MANIFESTU")
        
        # Próba załadowania bazy produktów
        try:
            with open('products.json', 'r', encoding='utf-8') as f:
                p_db = json.load(f)
        except:
            p_db = []
            st.warning("Baza produktów niedostępna.")
        
        p_sel_name = st.selectbox("PRODUKT", [p['name'] for p in p_db], index=None)
        
        if p_sel_name:
            p_ref = next(p for p in p_db if p['name'] == p_sel_name)
            ipc = p_ref.get('itemsPerCase', 1)
            
            st.markdown(f"<div style='color:var(--v-copper); font-size:0.75rem;'>OPAKOWANIE: {ipc} sztuk</div>", unsafe_allow_html=True)
            p_count = st.number_input("LICZBA SZTUK", min_value=1, value=ipc)
            
            # Przeliczanie na opakowania
            num_cases = math.ceil(p_count / ipc)
            st.caption(f"Generuje {num_cases} opakowań zbiorczych.")
            
            if st.button("AKTUALIZUJ MANIFEST", type="primary"):
                for i in range(num_cases):
                    new_unit = p_ref.copy()
                    # Logika pozostałych sztuk w ostatnim case
                    new_unit['pcs_in_unit'] = ipc if (i < num_cases - 1 or p_count % ipc == 0) else (p_count % ipc)
                    st.session_state.v_manifest.append(new_unit)
                st.rerun()

        if st.button("WYCZYŚĆ WSZYSTKO"):
            st.session_state.v_manifest = []; st.rerun()

    # --- DASHBOARD GŁÓWNY ---
    tab1, tab2 = st.tabs(["📊 PLANNER ZAŁADUNKU", "📦 BAZA PRODUKTÓW"])

    with tab1:
        if st.session_state.v_manifest:
            # 1. Podsumowanie Manifestu (KPI)
            kpi1, kpi2, kpi3, kpi4 = st.columns(4)
            total_u = len(st.session_state.v_manifest)
            total_p = sum(int(u.get('pcs_in_unit', 1)) for u in st.session_state.v_manifest)
            total_kg = sum(float(u.get('weight', 0)) for u in st.session_state.v_manifest)
            
            kpi1.metric("OPAKOWANIA", total_u)
            kpi2.metric("SZTUKI", total_p)
            kpi3.metric("WAGA", f"{total_kg} KG")
            kpi4.metric("LDM (TEOR.)", f"{(total_kg/veh['max_w'])*(veh['L']/100):.2f}")

            # 2. PROCES PAKOWANIA (V-ENGINE RUN)
            remaining_cargo = [dict(u) for u in st.session_state.v_manifest]
            fleet_plan = []
            
            while remaining_cargo:
                res_stacks, res_w, not_packed, ldm_r = v_engine_core(remaining_cargo, veh)
                if not res_stacks:
                    st.error("KRYTYCZNY BŁĄD: Jednostka zbyt duża dla naczepy.")
                    break
                fleet_plan.append({"stacks": res_stacks, "weight": res_w, "ldm": ldm_r})
                remaining_cargo = not_packed

            # 3. WYNIKI ASYGNACJI
            st.markdown(f"### ASYGNACJA FLOTY: {len(fleet_plan)} POJAZD(Y)")
            
            for i, truck in enumerate(fleet_plan):
                with st.container():
                    st.markdown(f'<div class="v-card">', unsafe_allow_html=True)
                    st.markdown(f"### JEDNOSTKA TRANSPORTOWA #{i+1} | {sel_veh_name}", unsafe_allow_html=True)
                    
                    c_viz, c_inf = st.columns([2, 1])
                    with c_viz:
                        st.plotly_chart(render_3d_transport(veh, truck['stacks']), use_container_width=True)
                    with c_inf:
                        st.markdown("**ANALIZA WYKORZYSTANIA:**")
                        st.markdown(f"REALNE LDM: <b style='color:var(--v-copper);'>{truck['ldm']:.2f}</b>", unsafe_allow_html=True)
                        st.markdown(f"MASA CAŁKOWITA: <b style='color:var(--v-copper);'>{truck['weight']} KG</b>", unsafe_allow_html=True)
                        st.markdown(f"UTYLIZACJA MASY: <b>{(truck['weight']/veh['max_w'])*100:.1f}%</b>", unsafe_allow_html=True)
                        
                        st.divider()
                        st.markdown("**LISTA ZAŁADUNKOWA (PACKING LIST):**")
                        t_items = [it['name'] for s in truck['stacks'] for it in s['items']]
                        if t_items:
                            agg = pd.Series(t_items).value_counts().reset_index()
                            agg.columns = ['PRODUKT', 'ILOŚĆ CASE']
                            
                            t_html = '<table class="v-table"><tr><th>Produkt</th><th>Case</th></tr>'
                            for _, r in agg.iterrows():
                                t_html += f'<tr><td>{r["PRODUKT"]}</td><td>{r["ILOŚĆ CASE"]}</td></tr>'
                            t_html += '</table>'
                            st.markdown(t_html, unsafe_allow_html=True)
                    
                    st.markdown('</div>', unsafe_allow_html=True)

            # Export
            st.markdown("### EKSPORT DANYCH")
            csv = pd.DataFrame(st.session_state.v_manifest).to_csv(index=False).encode('utf-8')
            st.download_button("POBIERZ MANIFEST CSV", data=csv, file_name=f"VORTEZA_MANIFEST_{datetime.now().strftime('%Y%m%d')}.csv", mime="text/csv")
        else:
            st.markdown('<div class="v-card" style="text-align:center; color:#555;">VORTEZA FLOW READY. OCZEKIWANIE NA DANE MANIFESTU...</div>', unsafe_allow_html=True)

    with tab2:
        st.markdown("### ZARZĄDZANIE INWENTARZEM")
        if p_db:
            df_db = pd.DataFrame(p_db)
            st.dataframe(df_db, use_container_width=True)
        else:
            st.info("Baza produktów jest pusta lub nie została wczytana.")

if __name__ == "__main__":
    main()
