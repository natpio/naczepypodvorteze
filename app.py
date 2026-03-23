import streamlit as st
import json
import plotly.graph_objects as go
import math
import pandas as pd
import random
import base64
from PIL import Image
import io

# =========================================================
# 1. ARCHITEKTURA SYSTEMU I BEZPIECZEŃSTWO
# =========================================================
try:
    # Integracja z Twoim systemem Secrets
    GITHUB_TOKEN = st.secrets.get("G_TOKEN", "BRAK")
    USER_DB = st.secrets.get("credentials", {}).get("usernames", {"admin": "vorteza2026"})
except Exception:
    USER_DB = {"admin": "admin123"}

# Pełna specyfikacja floty VORTEZA
VEHICLES = {
    "TIR FTL (Standard)": {"maxWeight": 24000, "L": 1360, "W": 248, "H": 275, "axles": 3},
    "Solo 7m (Heavy)": {"maxWeight": 7000, "L": 720, "W": 245, "H": 270, "axles": 2},
    "Solo 6m (Medium)": {"maxWeight": 3500, "L": 600, "W": 245, "H": 250, "axles": 2},
    "BUS (Express)": {"maxWeight": 1100, "L": 450, "W": 175, "H": 210, "axles": 2}
}

# =========================================================
# 2. VORTEZA PREMIUM UI (DESIGN SYSTEM)
# =========================================================
def apply_vorteza_design():
    st.markdown("""
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;700&family=JetBrains+Mono:wght@300&display=swap');
            
            :root {
                --v-copper: #B58863;
                --v-dark-bg: #0A0A0A;
                --v-panel: rgba(18, 18, 18, 0.98);
                --v-text-main: #E0E0E0;
                --v-text-dim: #888888;
            }

            .stApp {
                background-color: var(--v-dark-bg);
                color: var(--v-text-main);
                font-family: 'Montserrat', sans-serif;
            }

            /* Karty VORTEZA */
            .vorteza-card {
                background: var(--v-panel);
                padding: 2rem;
                border-radius: 2px;
                border-left: 4px solid var(--v-copper);
                box-shadow: 20px 20px 60px rgba(0,0,0,0.5);
                margin-bottom: 1.5rem;
                backdrop-filter: blur(10px);
            }

            /* Nagłówki */
            h1, h2, h3 {
                color: var(--v-copper) !important;
                text-transform: uppercase;
                letter-spacing: 4px !important;
                font-weight: 700 !important;
                filter: drop-shadow(2px 2px 2px rgba(0,0,0,0.8));
            }

            /* Metryki */
            [data-testid="stMetricValue"] {
                color: var(--v-copper) !important;
                font-family: 'JetBrains Mono', monospace !important;
                font-size: 2.2rem !important;
            }

            /* Przyciski */
            .stButton > button {
                background: transparent;
                color: var(--v-copper);
                border: 1px solid var(--v-copper);
                border-radius: 0px;
                padding: 0.8rem 2rem;
                text-transform: uppercase;
                letter-spacing: 2px;
                transition: all 0.4s ease;
                width: 100%;
            }

            .stButton > button:hover {
                background: var(--v-copper);
                color: black;
                box-shadow: 0 0 20px rgba(181, 136, 99, 0.4);
            }

            /* Customowe tabele */
            .v-table {
                width: 100%;
                border-collapse: collapse;
                margin: 10px 0;
            }
            .v-table th {
                color: var(--v-copper);
                text-align: left;
                font-size: 0.7rem;
                text-transform: uppercase;
                border-bottom: 1px solid #333;
                padding: 10px;
            }
            .v-table td {
                padding: 12px 10px;
                border-bottom: 1px solid #1a1a1a;
                font-size: 0.85rem;
            }
        </style>
    """, unsafe_allow_html=True)

# =========================================================
# 3. SILNIK WIZUALIZACJI 3D (CAD-STYLE)
# =========================================================
def generate_3d_transport_view(vehicle_dims, cargo_stacks):
    fig = go.Figure()
    L, W, H = vehicle_dims['L'], vehicle_dims['W'], vehicle_dims['H']

    # --- KONSTRUKCJA POJAZDU ---
    # Podwozie ( Rama )
    fig.add_trace(go.Mesh3d(
        x=[-150, L, L, -150], y=[0, 0, W, W], z=[-5, -5, -5, -5],
        color='#111', opacity=1, hoverinfo='skip'
    ))
    
    # Kabina kierowcy (Bryła geometryczna)
    fig.add_trace(go.Mesh3d(
        x=[-140, 0, 0, -140, -140, 0, 0, -140],
        y=[0, 0, W, W, 0, 0, W, W],
        z=[0, 0, 0, 0, H*0.75, H*0.75, H*0.75, H*0.75],
        i=[7,0,0,0,4,4,6,6,4,0,3,2], j=[3,4,1,2,5,6,5,2,0,1,6,3], k=[0,7,2,3,6,7,1,1,5,5,7,6],
        color='#1a1a1a', opacity=1, name="KABINA"
    ))

    # Przestrzeń ładunkowa (Wireframe + Podłoga)
    fig.add_trace(go.Mesh3d(
        x=[0, L, L, 0], y=[0, 0, W, W], z=[0, 0, 0, 0],
        color='#B58863', opacity=0.1, hoverinfo='skip'
    ))

    # Linie krawędziowe naczepy
    edges = [
        ([0, L], [0, 0], [0, 0]), ([0, L], [W, W], [0, 0]),
        ([0, 0], [0, W], [0, 0]), ([L, L], [0, W], [0, 0]),
        ([0, 0], [0, 0], [0, H]), ([0, 0], [W, W], [0, H]),
        ([0, L], [0, 0], [H, H]), ([0, L], [W, W], [H, H]),
        ([L, L], [0, 0], [0, H]), ([L, L], [W, W], [0, H])
    ]
    for x_e, y_e, z_e in edges:
        fig.add_trace(go.Scatter3d(x=x_e, y=y_e, z=z_e, mode='lines', line=dict(color='#B58863', width=2), hoverinfo='skip'))

    # --- WIZUALIZACJA ŁADUNKU ---
    for s_idx, stack in enumerate(cargo_stacks):
        # Kolorystyka miedziano-złota dla towaru
        cargo_color = f'rgb({181-s_idx*2}, {136-s_idx*2}, {99-s_idx*2})'
        
        for item in stack['items']:
            x0, y0, z0 = stack['x'], stack['y'], item['z']
            dx, dy, dz = item['w_fit'], item['l_fit'], item['height']
            
            # Bryła paczki
            fig.add_trace(go.Mesh3d(
                x=[x0, x0+dx, x0+dx, x0, x0, x0+dx, x0+dx, x0],
                y=[y0, y0, y0+dy, y0+dy, y0, y0, y0+dy, y0+dy],
                z=[z0, z0, z0, z0, z0+dz, z0+dz, z0+dz, z0+dz],
                i=[7,0,0,0,4,4,6,6,4,0,3,2], j=[3,4,1,2,5,6,5,2,0,1,6,3], k=[0,7,2,3,6,7,1,1,5,5,7,6],
                color=cargo_color, opacity=0.9, name=item['name'],
                hovertemplate=f"<b>{item['name']}</b><br>Wymiary: {dx}x{dy}x{dz}cm<br>Waga: {item['weight']}kg<extra></extra>"
            ))
            
            # Krawędzie paczki (dla separacji wizualnej)
            fig.add_trace(go.Scatter3d(
                x=[x0, x0+dx, x0+dx, x0, x0, x0, x0+dx, x0+dx, x0, x0, x0+dx, x0+dx, x0+dx, x0+dx, x0, x0],
                y=[y0, y0, y0+dy, y0+dy, y0, y0, y0, y0+dy, y0+dy, y0+dy, y0+dy, y0, y0, y0+dy, y0+dy, y0],
                z=[z0, z0, z0, z0, z0, z0+dz, z0+dz, z0, z0, z0+dz, z0+dz, z0+dz, z0, z0, z0+dz, z0+dz],
                mode='lines', line=dict(color='black', width=1), hoverinfo='skip'
            ))

    fig.update_layout(
        scene=dict(
            aspectmode='data',
            xaxis=dict(visible=False), yaxis=dict(visible=False), zaxis=dict(visible=False),
            camera=dict(eye=dict(x=1.6, y=1.6, z=1.0))
        ),
        paper_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=0, r=0, b=0, t=0),
        showlegend=False
    )
    return fig

# =========================================================
# 4. SILNIK OPTYMALIZACJI (FIRST-FIT DECREASING + STACKING)
# =========================================================
def vorteza_packing_engine(cargo_units, vehicle):
    # Sortowanie po objętości i wadze
    sorted_cargo = sorted(cargo_units, key=lambda x: (x['length']*x['width'], x['weight']), reverse=True)
    
    placed_stacks = []
    failed_to_pack = []
    total_weight = 0
    
    # Parametry robocze
    curr_x, curr_y, max_h_in_row = 0, 0, 0
    row_width = 0

    for item in sorted_cargo:
        if total_weight + item['weight'] > vehicle['maxWeight']:
            failed_to_pack.append(item); continue
            
        is_stacked = False
        # 1. Próba piętrowania (Stacking)
        if item.get('canStack', True):
            for stack in placed_stacks:
                # Sprawdzenie czy wymiary pasują (z tolerancją rotacji)
                dim_match = (item['width'] <= stack['w'] and item['length'] <= stack['l']) or \
                            (item['length'] <= stack['w'] and item['width'] <= stack['l'])
                
                if dim_match and (stack['curH'] + item['height'] <= vehicle['H']):
                    it_copy = item.copy()
                    it_copy['z'] = stack['curH']
                    it_copy['w_fit'], it_copy['l_fit'] = stack['w'], stack['l']
                    stack['items'].append(it_copy)
                    stack['curH'] += item['height']
                    total_weight += item['weight']
                    is_stacked = True; break
        
        if is_stacked: continue

        # 2. Próba postawienia na podłodze (Floor placement)
        placed = False
        orientations = [(item['width'], item['length']), (item['length'], item['width'])]
        for w, l in orientations:
            if curr_y + l <= vehicle['W'] and curr_x + w <= vehicle['L']:
                it_c = item.copy(); it_c['z'] = 0; it_c['w_fit'], it_c['l_fit'] = w, l
                placed_stacks.append({'x': curr_x, 'y': curr_y, 'w': w, 'l': l, 'curH': item['height'], 'items': [it_c]})
                curr_y += l; row_width = max(row_width, w); total_weight += item['weight']; placed = True; break
            elif curr_x + row_width + w <= vehicle['L'] and l <= vehicle['W']:
                curr_x += row_width; curr_y = 0; row_width = w
                it_c = item.copy(); it_c['z'] = 0; it_c['w_fit'], it_c['l_fit'] = w, l
                placed_stacks.append({'x': curr_x, 'y': curr_y, 'w': w, 'l': l, 'curH': item['height'], 'items': [it_c]})
                curr_y += l; total_weight += item['weight']; placed = True; break
        
        if not placed: failed_to_pack.append(item)

    # Obliczanie LDM (Loading Meters)
    # LDM = Max(X + Szerokość stosu) / 100
    ldm_val = max([s['x'] + s['w'] for s in placed_stacks]) / 100 if placed_stacks else 0
    return placed_stacks, total_weight, failed_to_pack, ldm_val

# =========================================================
# 5. GŁÓWNA LOGIKA APLIKACJI
# =========================================================
def main():
    apply_vorteza_design()

    # --- SYSTEM AUTORYZACJI ---
    if "auth" not in st.session_state: st.session_state.auth = False

    if not st.session_state.auth:
        c1, c2, c3 = st.columns([1, 1.5, 1])
        with c2:
            st.markdown("<br><br>", unsafe_allow_html=True)
            with st.form("VortezaLogin"):
                st.markdown("<h3 style='text-align:center;'>VORTEZA SYSTEMS | ACCESS</h3>", unsafe_allow_html=True)
                usr = st.text_input("ID OPERATORA")
                pwd = st.text_input("KLUCZ DOSTĘPU", type="password")
                if st.form_submit_button("AUTORYZUJ"):
                    if usr in USER_DB and USER_DB[usr] == pwd:
                        st.session_state.auth = True; st.rerun()
                    else: st.error("Odmowa dostępu.")
        return

    # --- INTERFEJS OPERACYJNY ---
    # Header
    h_col1, h_col2 = st.columns([4, 1])
    with h_col1:
        st.markdown("<h1>VORTEZA FLOW</h1>", unsafe_allow_html=True)
        st.markdown("<p style='letter-spacing:2px; font-size:0.7rem; color:#666;'>INTERFACE VERSION 3.0 | 2026 LOGISTICS CORE</p>", unsafe_allow_html=True)
    with h_col2:
        if st.button("LOGOUT"): st.session_state.auth = False; st.rerun()

    # Inicjalizacja listy towarowej
    if 'v_cargo' not in st.session_state: st.session_state.v_cargo = []

    # Sidebar: Konfiguracja
    with st.sidebar:
        st.markdown("### KONFIGURACJA FLOTY")
        v_selected = st.selectbox("JEDNOSTKA TRANSPORTOWA", list(VEHICLES.keys()))
        v_specs = VEHICLES[v_selected]
        
        st.markdown(f"""
            <div style='font-size:0.8rem; color:#888; border:1px solid #333; padding:10px;'>
                POJEMNOŚĆ: {v_specs['L']}x{v_specs['W']}x{v_specs['H']} cm<br>
                MAX ŁADUNEK: {v_specs['maxWeight']} kg
            </div>
        """, unsafe_allow_html=True)
        
        st.divider()
        st.markdown("### DODAJ ŁADUNEK")
        try:
            with open('products.json', 'r', encoding='utf-8') as f: products_db = json.load(f)
        except: products_db = []
        
        p_name = st.selectbox("PRODUKT Z BAZY", [p['name'] for p in products_db], index=None)
        p_qty = st.number_input("LICZBA SZTUK", min_value=1, value=1)
        
        if st.button("DODAJ DO MANIFESTU"):
            if p_name:
                p_ref = next(p for p in products_db if p['name'] == p_name)
                # Logika przeliczania sztuk na opakowania zbiorcze
                items_per_case = p_ref.get('itemsPerCase', 1)
                num_cases = math.ceil(p_qty / items_per_case)
                
                for i in range(num_cases):
                    case_unit = p_ref.copy()
                    # Ostatni case może nie być pełny (opcjonalnie do statystyk)
                    case_unit['actual_pcs'] = items_per_case if (i < num_cases - 1 or p_qty % items_per_case == 0) else (p_qty % items_per_case)
                    st.session_state.v_cargo.append(case_unit)
                st.toast(f"Zaktualizowano manifest: {num_cases} opakowań.")
            else: st.warning("Wybierz jednostkę z bazy.")

        if st.button("RESETUJ MANIFEST", type="secondary"):
            st.session_state.v_cargo = []; st.rerun()

    # --- PANEL ANALITYCZNY ---
    if st.session_state.v_cargo:
        # Statystyki Manifestu
        m1, m2, m3, m4 = st.columns(4)
        total_cases = len(st.session_state.v_cargo)
        total_pcs = sum(int(c.get('actual_pcs', 1)) for c in st.session_state.v_cargo)
        total_kg = sum(float(c.get('weight', 0)) for c in st.session_state.v_cargo)
        
        m1.metric("OPAKOWANIA", total_cases)
        m2.metric("SZTUKI (SUMA)", total_pcs)
        m3.metric("WAGA CAŁKOWITA", f"{total_kg} KG")
        
        # Wyliczenie orientacyjnego LDM na podstawie wagi (bezpiecznik)
        ldm_estimate = (total_kg / v_specs['maxWeight']) * (v_specs['L'] / 100)
        m4.metric("LDM (EST.)", f"{ldm_estimate:.2f}")

        # PRZETWARZANIE ZAŁADUNKU (MULTIPLE VEHICLES SUPPORT)
        remaining_units = [dict(u) for u in st.session_state.v_cargo]
        fleet_manifest = []
        
        while remaining_units:
            res_stacks, res_weight, not_p, ldm_real = vorteza_packing_engine(remaining_units, v_specs)
            if not res_stacks:
                st.error("KRYTYCZNY BŁĄD: Jednostka zbyt duża dla wybranej naczepy.")
                break
            fleet_manifest.append({"stacks": res_stacks, "weight": res_weight, "ldm": ldm_real})
            remaining_units = not_p

        st.markdown(f"### ASYGNACJA FLOTY: {len(fleet_manifest)} POJAZD(Y)")
        
        for idx, truck in enumerate(fleet_manifest):
            st.markdown(f'<div class="vorteza-card">', unsafe_allow_html=True)
            st.markdown(f"### JEDNOSTKA #{idx+1} | {v_selected}", unsafe_allow_html=True)
            
            c_3d, c_info = st.columns([2, 1])
            
            with c_3d:
                st.plotly_chart(generate_3d_view(v_specs, truck['stacks']), use_container_width=True)
            
            with c_info:
                st.markdown("**PARAMETRY OPERACYJNE:**")
                st.markdown(f"LDM WYKORZYSTANE: <b style='color:#B58863;'>{truck['ldm']:.2f}</b>", unsafe_allow_html=True)
                st.markdown(f"WAGA ŁADUNKU: <b style='color:#B58863;'>{truck['weight']} KG</b>", unsafe_allow_html=True)
                st.markdown(f"WYPEŁNIENIE MASY: <b style='color:#B58863;'>{(truck['weight']/v_specs['maxWeight'])*100:.1f}%</b>", unsafe_allow_html=True)
                
                st.divider()
                st.markdown("**LISTA ZAŁADUNKOWA:**")
                # Agregacja zawartości pojazdu
                truck_items = [it['name'] for stack in truck['stacks'] for it in stack['items']]
                if truck_items:
                    summary = pd.Series(truck_items).value_counts().reset_index()
                    summary.columns = ['Produkt', 'Opakowań']
                    
                    # Generowanie tabeli HTML w stylu VORTEZA
                    table_html = '<table class="v-table"><tr><th>Produkt</th><th>Ilość</th></tr>'
                    for _, row in summary.iterrows():
                        table_html += f'<tr><td>{row["Produkt"]}</td><td>{row["Opakowań"]}</td></tr>'
                    table_html += '</table>'
                    st.markdown(table_html, unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="vorteza-card" style="text-align:center; color:#666;">POCZEKALNIA: OCZEKIWANIE NA DANE MANIFESTU ŁADUNKOWEGO...</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
