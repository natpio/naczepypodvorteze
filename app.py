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
# KONFIGURACJA I SEKRETY (ZGODNIE Z VORTEZA)
# =========================================================
try:
    USER_DB = st.secrets["credentials"]["usernames"]
except Exception:
    USER_DB = {"admin": "admin123"} # Fallback do testów

# Parametry pojazdów
VEHICLES = {
    "BUS (3.5t)": {"maxWeight": 1100, "L": 450, "W": 170, "H": 210},
    "Solo 6m": {"maxWeight": 3500, "L": 600, "W": 245, "H": 250},
    "Solo 7m": {"maxWeight": 7000, "L": 720, "W": 245, "H": 270},
    "TIR FTL": {"maxWeight": 24000, "L": 1360, "W": 248, "H": 270}
}

# =========================================================
# FUNKCJE POMOCNICZE
# =========================================================
def get_base64_of_bin_file(bin_file):
    try:
        with open(bin_file, 'rb') as f:
            data = f.read()
        return base64.b64encode(data).decode()
    except:
        return ""

def load_products():
    try:
        with open('products.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            return sorted(data, key=lambda x: x.get('name', ''))
    except:
        return []

# =========================================================
# SYSTEM LOGOWANIA VORTEZA
# =========================================================
def check_password():
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False

    if not st.session_state["authenticated"]:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown("<br><br><br>", unsafe_allow_html=True)
            with st.form("Login"):
                st.markdown("<h3 style='text-align: center;'>VORTEZA | SECURE ACCESS</h3>", unsafe_allow_html=True)
                user = st.text_input("Użytkownik", placeholder="User ID")
                password = st.text_input("Hasło", type="password", placeholder="Access Key")
                submit = st.form_submit_button("AUTORYZUJ")
                if submit:
                    if user in USER_DB and USER_DB[user] == password:
                        st.session_state["authenticated"] = True
                        st.session_state["username"] = user
                        st.rerun()
                    else:
                        st.error("Błąd autoryzacji.")
        return False
    return True

# =========================================================
# STYLIZACJA VORTEZA SYSTEMS
# =========================================================
def apply_vorteza_theme():
    bin_str = get_base64_of_bin_file('bg_vorteza.png')
    bg_css = f'background-image: url("data:image/png;base64,{bin_str}");' if bin_str else "background-color: #0E0E0E;"
    
    st.markdown(f"""
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;700&display=swap');
            :root {{
                --v-copper: #B58863;
                --v-dark: #0E0E0E;
                --v-panel: rgba(20, 20, 20, 0.95);
                --v-text: #E0E0E0;
            }}
            .stApp {{
                {bg_css}
                background-size: cover;
                background-attachment: fixed;
                color: var(--v-text);
                font-family: 'Montserrat', sans-serif;
            }}
            h1, h2, h3, .stSubheader, p {{ color: var(--v-text) !important; }}
            h1, h2, h3 {{ color: var(--v-copper) !important; text-transform: uppercase; letter-spacing: 2px; }}
            
            .vorteza-card {{
                background-color: var(--v-panel);
                padding: 25px;
                border-radius: 5px;
                border-left: 5px solid var(--v-copper);
                box-shadow: 0 10px 40px rgba(0,0,0,0.8);
                backdrop-filter: blur(15px);
                margin-bottom: 20px;
            }}
            [data-testid="stMetricValue"] {{
                color: var(--v-copper) !important;
                font-size: 1.8rem !important;
                font-weight: 700 !important;
            }}
            label[data-testid="stWidgetLabel"] {{
                color: var(--v-copper) !important;
                text-transform: uppercase;
                font-size: 0.8rem !important;
                font-weight: 700 !important;
            }}
            .stButton > button {{
                background-color: rgba(0, 0, 0, 0.7);
                color: var(--v-copper);
                border: 1px solid var(--v-copper);
                font-weight: 700;
                text-transform: uppercase;
                transition: 0.3s;
            }}
            .stButton > button:hover {{
                background-color: var(--v-copper);
                color: black;
            }}
            /* Stylizacja tabeli zawartości */
            .content-table {{ width: 100%; border-collapse: collapse; }}
            .content-table th {{ color: var(--v-copper); text-align: left; border-bottom: 1px solid #444; padding: 10px; text-transform: uppercase; font-size: 0.7rem; }}
            .content-table td {{ padding: 10px; border-bottom: 1px solid #222; font-size: 0.85rem; }}
        </style>
    """, unsafe_allow_html=True)

# =========================================================
# SILNIK OPTYMALIZACJI (PRZENIESIONY Z TWOJEGO KODU)
# =========================================================
def optimize_packing(items, vehicle):
    items = sorted(items, key=lambda x: (not x.get('canStack', True), x['length'] * x['width']), reverse=True)
    placed_stacks, not_placed = [], []
    total_weight, curr_x, curr_y, row_max_width = 0, 0, 0, 0
    
    for it in items:
        if total_weight + it['weight'] > vehicle['maxWeight']:
            not_placed.append(it)
            continue
        fit_found = False
        if it.get('canStack', True):
            for s in placed_stacks:
                can_fit = (it['width'] <= s['w'] and it['length'] <= s['l']) or (it['length'] <= s['w'] and it['width'] <= s['l'])
                if can_fit and (s['curH'] + it['height'] <= vehicle['H']):
                    it_copy = it.copy(); it_copy['z'] = s['curH']
                    s['items'].append(it_copy); s['curH'] += it['height']
                    total_weight += it['weight']; fit_found = True; break
        if fit_found: continue
        dims = [(it['width'], it['length']), (it['length'], it['width'])]
        for w, l in dims:
            if curr_y + l <= vehicle['W'] and curr_x + w <= vehicle['L']:
                it_copy = it.copy(); it_copy['z'] = 0
                placed_stacks.append({'x': curr_x, 'y': curr_y, 'w': w, 'l': l, 'curH': it['height'], 'items': [it_copy]})
                curr_y += l; row_max_width = max(row_max_width, w); total_weight += it['weight']; fit_found = True; break
            elif curr_x + row_max_width + w <= vehicle['L'] and l <= vehicle['W']:
                curr_x += row_max_width; curr_y = 0; row_max_width = w
                it_copy = it.copy(); it_copy['z'] = 0
                placed_stacks.append({'x': curr_x, 'y': curr_y, 'w': w, 'l': l, 'curH': it['height'], 'items': [it_copy]})
                curr_y += l; total_weight += it['weight']; fit_found = True; break
        if not fit_found: not_placed.append(it)
    ldm = max([s['x'] + s['w'] for s in placed_stacks]) / 100 if placed_stacks else 0
    return placed_stacks, total_weight, not_placed, ldm

def create_3d_view(stacks, vehicle):
    fig = go.Figure()
    # Obrys paki (Miedziany zamiast Cyan)
    fig.add_trace(go.Mesh3d(
        x=[0, vehicle['L'], vehicle['L'], 0, 0, vehicle['L'], vehicle['L'], 0],
        y=[0, 0, vehicle['W'], vehicle['W'], 0, 0, vehicle['W'], vehicle['W']],
        z=[0, 0, 0, 0, vehicle['H'], vehicle['H'], vehicle['H'], vehicle['H']],
        opacity=0.03, color='#B58863', hoverinfo='skip'
    ))
    # Paleta VORTEZA (Miedź, Złoto, Czerń, Szarość)
    v_colors = ["#B58863", "#8E6A4D", "#5E4633", "#D4AF37", "#4A4A4A", "#2F2F2F"]
    for i, s in enumerate(stacks):
        color = v_colors[i % len(v_colors)]
        for it in s['items']:
            x, y, z = s['x'], s['y'], it['z']
            dx, dy, dz = (it['width'], it['length'], it['height']) if it['width'] == s['w'] else (it['length'], it['width'], it['height'])
            fig.add_trace(go.Mesh3d(
                x=[x, x+dx, x+dx, x, x, x+dx, x+dx, x], y=[y, y, y+dy, y+dy, y, y, y+dy, y+dy],
                z=[z, z, z, z, z+dz, z+dz, z+dz, z+dz],
                i=[7,0,0,0,4,4,6,6,4,0,3,2], j=[3,4,1,2,5,6,5,2,0,1,6,3], k=[0,7,2,3,6,7,1,1,5,5,7,6],
                color=color, opacity=0.9, name=it['name']
            ))
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        scene=dict(bgcolor='rgba(0,0,0,0)', aspectmode='data',
                   xaxis=dict(gridcolor='#333', title_font=dict(color='#B58863')),
                   yaxis=dict(gridcolor='#333', title_font=dict(color='#B58863')),
                   zaxis=dict(gridcolor='#333', title_font=dict(color='#B58863'))),
        margin=dict(l=0, r=0, b=0, t=0), showlegend=False
    )
    return fig

# =========================================================
# GŁÓWNA APLIKACJA
# =========================================================
st.set_page_config(page_title="VORTEZA FLOW | LOGISTICS PLANNER", layout="wide")
apply_vorteza_theme()

if check_password():
    # Nagłówek VORTEZA
    col_logo, col_title, col_logout = st.columns([1, 4, 1])
    with col_logo:
        try:
            st.image('logo_vorteza.png', use_container_width=True)
        except:
            st.markdown("<h2 style='color:#B58863;'>VORTEZA</h2>", unsafe_allow_html=True)
    with col_title:
        st.markdown("<h1 style='margin-bottom:0;'>VORTEZA FLOW</h1>", unsafe_allow_html=True)
        st.markdown("<p style='letter-spacing:3px; color:#666;'>SYSTEMS | 3D LOGISTICS INTERFACE</p>", unsafe_allow_html=True)
    with col_logout:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("WYLOGUJ"):
            del st.session_state["authenticated"]; st.rerun()

    all_products = load_products()
    if 'cargo_list' not in st.session_state: st.session_state.cargo_list = []

    # --- SIDEBAR (ZGODNIE ZE STYLEM) ---
    with st.sidebar:
        st.markdown("<h3 style='color:#B58863;'>OPERACJE</h3>", unsafe_allow_html=True)
        v_name = st.selectbox("JEDNOSTKA FLOTY", list(VEHICLES.keys()))
        v_data = VEHICLES[v_name]
        
        st.markdown('<div class="route-preview">', unsafe_allow_html=True)
        st.markdown(f"Pojemność: {v_data['L']}x{v_data['W']} cm<br>Dopuszczalna masa: {v_data['maxWeight']} kg", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.divider()
        selected_p = st.selectbox("BAZA PRODUKTÓW", [p['name'] for p in all_products], index=None)
        qty = st.number_input("ILOŚĆ (JEDNOSTKI)", min_value=1, value=1)
        
        if st.button("DODAJ DO MANIFESTU"):
            if selected_p:
                p_info = next(p for p in all_products if p['name'] == selected_p)
                for _ in range(qty): st.session_state.cargo_list.append(p_info.copy())
                st.toast(f"Zaktualizowano manifest: {selected_p}")
            else: st.warning("Wybierz jednostkę ładunkową.")

        if st.button("RERESETUJ SYSTEM", type="secondary"):
            st.session_state.cargo_list = []; st.rerun()

    # --- WIDOK GŁÓWNY ---
    if st.session_state.cargo_list:
        # Statystyki w kartach VORTEZA
        m1, m2, m3, m4 = st.columns(4)
        total_qty = len(st.session_state.cargo_list)
        total_w = sum(i['weight'] for i in st.session_state.cargo_list)
        total_v = sum((i['width']*i['length']*i['height'])/1000000 for i in st.session_state.cargo_list)
        
        with m1: st.metric("TOTAL UNITS", total_qty)
        with m2: st.metric("TOTAL WEIGHT", f"{total_w} KG")
        with m3: st.metric("VOLUME", f"{total_v:.2f} M³")
        with m4: st.metric("ESTIMATED LDM", f"{(total_w/v_data['maxWeight'])*(v_data['L']/100):.2f}")

        # Proces pakowania
        remaining = [dict(i) for i in st.session_state.cargo_list]
        fleet_results = []
        while remaining:
            stacks, weight, not_p, ldm = optimize_packing(remaining, v_data)
            if not stacks and remaining:
                st.error("KRYTYCZNY BŁĄD: Jednostka zbyt duża dla wybranego pojazdu.")
                break
            fleet_results.append({"stacks": stacks, "weight": weight, "ldm": ldm})
            remaining = not_p

        st.subheader(f"ASYGNACJA FLOTY: {len(fleet_results)} JEDNOSTKI")
        
        for idx, truck in enumerate(fleet_results):
            st.markdown(f'<div class="vorteza-card">', unsafe_allow_html=True)
            st.markdown(f"### POJAZD #{idx+1} | {v_name}", unsafe_allow_html=True)
            
            c_plot, c_data = st.columns([1.5, 1])
            with c_plot:
                st.plotly_chart(create_3d_view(truck['stacks'], v_data), use_container_width=True)
            with c_data:
                st.markdown("<p style='color:#B58863; font-weight:bold;'>MANIFEST ZAŁADUNKOWY</p>", unsafe_allow_html=True)
                items = [it['name'] for s in truck['stacks'] for it in s['items']]
                summary = pd.Series(items).value_counts().reset_index()
                
                # Budowanie tabeli w stylu VORTEZA
                html_table = '<table class="content-table"><tr><th>Produkt</th><th>Sztuk</th></tr>'
                for _, row in summary.iterrows():
                    html_table += f'<tr><td>{row["index"]}</td><td>{row["count"]}</td></tr>'
                html_table += '</table>'
                st.markdown(html_table, unsafe_allow_html=True)
                
                st.markdown(f"<br><p style='font-size:0.8rem;'>WYKORZYSTANIE MASY: <b>{(truck['weight']/v_data['maxWeight'])*100:.1f}%</b></p>", unsafe_allow_html=True)
                st.markdown(f"<p style='font-size:0.8rem;'>WYKORZYSTANIE LDM: <b>{truck['ldm']:.2f}</b></p>", unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="vorteza-card" style="text-align:center;">SYSTEM GOTOWY. OCZEKIWANIE NA DANE MANIFESTU...</div>', unsafe_allow_html=True)
