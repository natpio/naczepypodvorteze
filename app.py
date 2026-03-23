import streamlit as st
import json
import plotly.graph_objects as go
import math
import pandas as pd

# --- 1. KONFIGURACJA I STYLIZACJA ULTRA-PRO ---
st.set_page_config(
    page_title="SQM Logistics Terminal | Ultra-Pro", 
    page_icon="🚛",
    layout="wide", 
    initial_sidebar_state="expanded"
)

# Stylizacja High-Tech (Dark Mode z neonowymi akcentami)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&family=Inter:wght@400;700&display=swap');
    
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    .main { background-color: #020617; color: #f1f5f9; }
    
    /* Neonowe metryki */
    div[data-testid="stMetricValue"] {
        font-family: 'JetBrains Mono', monospace;
        color: #00f2ff !important;
        text-shadow: 0 0 10px rgba(0, 242, 255, 0.4);
    }
    
    /* Karty kontenerów */
    .st-emotion-cache-12w0u9p {
        background-color: #0f172a !important;
        border: 1px solid #1e293b !important;
        border-radius: 12px !important;
    }

    .stButton>button {
        border-radius: 8px;
        font-weight: 700;
        background: linear-gradient(90deg, #3b82f6, #06b6d4);
        border: none;
        color: white;
        transition: 0.3s;
    }
    .stButton>button:hover { box-shadow: 0 0 15px rgba(59, 130, 246, 0.5); transform: scale(1.02); }
    </style>
    """, unsafe_allow_html=True)

# --- 2. LOGOWANIE (SECRETS) ---
def check_password():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    if not st.session_state.authenticated:
        col1, col2, col3 = st.columns([1, 1.5, 1])
        with col2:
            st.markdown("<h1 style='text-align: center; color: #00f2ff;'>SQM LOGISTICS</h1>", unsafe_allow_html=True)
            try:
                master_password = str(st.secrets["password"])
            except:
                st.error("Błąd: Skonfiguruj klucz 'password' w Secrets.")
                return False
            pwd = st.text_input("Hasło dostępu:", type="password")
            if st.button("ZALOGUJ DO SYSTEMU", use_container_width=True):
                if pwd == master_password:
                    st.session_state.authenticated = True
                    st.rerun()
                else:
                    st.error("Nieprawidłowe hasło.")
        return False
    return True

# --- 3. DANE I POJAZDY ---
VEHICLES = {
    "Naczepa FTL Standard": {"maxWeight": 24000, "L": 1360, "W": 248, "H": 270},
    "Naczepa MEGA": {"maxWeight": 24000, "L": 1360, "W": 248, "H": 300},
    "Solo 7.2m": {"maxWeight": 7000, "L": 720, "W": 245, "H": 260},
    "Bus 10EP": {"maxWeight": 1100, "L": 485, "W": 220, "H": 235}
}

COLOR_PALETTE = ["#3b82f6", "#ef4444", "#10b981", "#f59e0b", "#8b5cf6", "#06b6d4", "#f43f5e"]

def load_products():
    try:
        with open('products.json', 'r', encoding='utf-8') as f:
            return sorted(json.load(f), key=lambda x: x.get('name', ''))
    except:
        return [
            {"name": "Paleta EPAL", "width": 80, "length": 120, "height": 140, "weight": 400, "canStack": True, "itemsPerCase": 1},
            {"name": "Case Mix 120x60", "width": 60, "length": 120, "height": 90, "weight": 110, "canStack": True, "itemsPerCase": 1},
            {"name": "Skrzynia LED", "width": 120, "length": 100, "height": 115, "weight": 380, "canStack": False, "itemsPerCase": 1}
        ]

# --- 4. ZOPTYMALIZOWANY SILNIK PAKOWANIA ---
@st.cache_data(show_spinner=False)
def get_packed_fleet(cargo_list, vehicle):
    """Przelicza plan tylko przy zmianie danych wejściowych."""
    remaining_items = [dict(i) for i in cargo_list]
    fleet = []
    
    while remaining_items:
        placed_stacks = []
        not_placed = []
        current_weight = 0
        max_reached_l = 0
        
        # Sortowanie: największa podstawa najpierw
        items_to_pack = sorted(remaining_items, key=lambda x: (x['length'] * x['width']), reverse=True)
        shelf_x, shelf_y, shelf_max_w = 0, 0, 0

        for item in items_to_pack:
            if current_weight + item['weight'] > vehicle['maxWeight']:
                not_placed.append(item); continue
                
            added = False
            # Próba piętrowania
            if item.get('canStack', True):
                for s in placed_stacks:
                    match = (item['width'] == s['width'] and item['length'] == s['length'])
                    if s['canStackBase'] and match and (s['currentH'] + item['height']) <= vehicle['H']:
                        it_copy = item.copy()
                        it_copy['z_pos'] = s['currentH']
                        s['items'].append(it_copy)
                        s['currentH'] += item['height']
                        current_weight += item['weight']
                        added = True; break
            
            if not added:
                # Nowy stos (Rotacja 90°)
                for w, l in [(item['width'], item['length']), (item['length'], item['width'])]:
                    if shelf_y + l <= vehicle['W'] and shelf_x + w <= vehicle['L']:
                        it_copy = item.copy(); it_copy['z_pos'] = 0
                        placed_stacks.append({
                            'x': shelf_x, 'y': shelf_y, 'width': w, 'length': l, 
                            'currentH': item['height'], 'canStackBase': item.get('canStack', True), 'items': [it_copy]
                        })
                        shelf_y += l; shelf_max_w = max(shelf_max_w, w)
                        added = True; break
                    elif shelf_x + shelf_max_w + w <= vehicle['L'] and l <= vehicle['W']:
                        shelf_x += shelf_max_w; shelf_y = 0; shelf_max_w = w
                        it_copy = item.copy(); it_copy['z_pos'] = 0
                        placed_stacks.append({
                            'x': shelf_x, 'y': shelf_y, 'width': w, 'length': l, 
                            'currentH': item['height'], 'canStackBase': item.get('canStack', True), 'items': [it_copy]
                        })
                        shelf_y += l; added = True; break

            if added:
                current_weight += item['weight']
                max_reached_l = max(max_reached_l, shelf_x + shelf_max_w)
            else:
                not_placed.append(item)
        
        if not placed_stacks: break
        fleet.append({"stacks": placed_stacks, "weight": current_weight, "ldm": max_reached_l/100})
        remaining_items = not_placed
                
    return fleet

# --- 5. WYDAJNA WIZUALIZACJA 3D (SINGLE-TRACE) ---
def draw_3d_pro(placed_stacks, vehicle, color_map):
    fig = go.Figure()
    v_l, v_w, v_h = vehicle['L'], vehicle['W'], vehicle['H']

    # Podłoga i obrys naczepy (Neon)
    fig.add_trace(go.Mesh3d(x=[0, v_l, v_l, 0], y=[0, 0, v_w, v_w], z=[0, 0, 0, 0], color='#1e293b', opacity=1.0, hoverinfo='skip'))
    
    # Krawędzie naczepy
    fig.add_trace(go.Scatter3d(
        x=[0, v_l, v_l, 0, 0, None, 0, v_l, v_l, 0, 0, None, 0, 0, None, v_l, v_l, None, v_l, v_l, None, 0, 0],
        y=[0, 0, v_w, v_w, 0, None, 0, 0, v_w, v_w, 0, None, 0, 0, None, 0, 0, None, v_w, v_w, None, v_w, v_w],
        z=[0, 0, 0, 0, 0, None, v_h, v_h, v_h, v_h, v_h, None, 0, v_h, None, 0, v_h, None, 0, v_h, None, 0, v_h],
        mode='lines', line=dict(color='#00f2ff', width=3), hoverinfo='skip'
    ))

    # Optymalizacja krawędzi skrzyń: jeden trace zamiast setek
    edge_x, edge_y, edge_z = [], [], []

    for s in placed_stacks:
        for it in s['items']:
            x, y, z = s['x'], s['y'], it['z_pos']
            dx, dy, dz = it.get('width', s['width']), it.get('length', s['length']), it['height']
            color = color_map.get(it['name'], "#3b82f6")
            
            # Bryła
            fig.add_trace(go.Mesh3d(
                x=[x, x+dx, x+dx, x, x, x+dx, x+dx, x],
                y=[y, y, y+dy, y+dy, y, y, y+dy, y+dy],
                z=[z, z, z, z, z+dz, z+dz, z+dz, z+dz],
                i=[7,0,0,0,4,4,6,6,4,0,3,2], j=[3,4,1,2,5,6,5,2,0,1,6,3], k=[0,7,2,3,6,7,1,1,5,5,7,6],
                opacity=0.85, color=color, flatshading=True, name=it['name']
            ))
            
            # Dodawanie krawędzi do zbiorczej listy
            ex = [x, x+dx, x+dx, x, x, None, x, x+dx, x+dx, x, x, None, x, x, None, x+dx, x+dx, None, x+dx, x+dx, None, x, x]
            ey = [y, y, y+dy, y+dy, y, None, y, y, y+dy, y+dy, y, None, y, y, None, y, y, None, y+dy, y+dy, None, y+dy, y+dy]
            ez = [z, z, z, z, z, None, z+dz, z+dz, z+dz, z+dz, z+dz, None, z, z+dz, None, z, z+dz, None, z, z+dz, None, z, z+dz]
            edge_x.extend(ex); edge_y.extend(ey); edge_z.extend(ez); edge_x.append(None); edge_y.append(None); edge_z.append(None)

    fig.add_trace(go.Scatter3d(x=edge_x, y=edge_y, z=edge_z, mode='lines', line=dict(color='black', width=2), hoverinfo='skip'))

    fig.update_layout(
        scene=dict(
            xaxis=dict(title='DL (cm)', backgroundcolor="#020617", gridcolor="#1e293b"),
            yaxis=dict(title='SZ (cm)', backgroundcolor="#020617", gridcolor="#1e293b"),
            zaxis=dict(title='WY (cm)', backgroundcolor="#020617", gridcolor="#1e293b"),
            aspectmode='manual', aspectratio=dict(x=v_l/v_w*0.7, y=1, z=v_h/v_w*0.7)
        ),
        margin=dict(l=0, r=0, b=0, t=0), paper_bgcolor='rgba(0,0,0,0)', showlegend=False
    )
    return fig

# --- 6. APLIKACJA GŁÓWNA ---
if check_password():
    if 'cargo' not in st.session_state: st.session_state.cargo = []
    prods = load_products()
    if 'color_map' not in st.session_state:
        st.session_state.color_map = {p['name']: COLOR_PALETTE[i % len(COLOR_PALETTE)] for i, p in enumerate(prods)}

    with st.sidebar:
        st.markdown("<h2 style='color: #00f2ff;'>🚛 STEROWANIE</h2>", unsafe_allow_html=True)
        v_name = st.selectbox("POJAZD:", list(VEHICLES.keys()))
        veh = VEHICLES[v_name]
        
        st.divider()
        st.subheader("📦 DODAJ SPRZĘT")
        sel_p = st.selectbox("SPRZĘT:", [p['name'] for p in prods], index=None)
        qty = st.number_input("ILOŚĆ:", min_value=1, value=1)
        
        if st.button("DODAJ DO PLANU", use_container_width=True) and sel_p:
            p_ref = next(p for p in prods if p['name'] == sel_p)
            for _ in range(qty): st.session_state.cargo.append(p_ref.copy())
            st.rerun()
            
        if st.button("RESETUJ WSZYSTKO", use_container_width=True, type="secondary"):
            st.session_state.cargo = []; st.rerun()

    if st.session_state.cargo:
        # Edytor listy
        st.markdown("<h3 style='color: #00f2ff;'>📋 MANIFEST OPERACYJNY</h3>", unsafe_allow_html=True)
        df_cargo = pd.DataFrame(st.session_state.cargo)
        sum_df = df_cargo.groupby('name').size().reset_index(name='ilość')
        
        edited = st.data_editor(sum_df, hide_index=True, use_container_width=True, key="cargo_editor")
        if not edited.equals(sum_df):
            new_c = []
            for _, r in edited.iterrows():
                if r['ilość'] > 0:
                    orig = next(p for p in prods if p['name'] == r['name'])
                    new_c.extend([orig.copy() for _ in range(r['ilość'])])
            st.session_state.cargo = new_c; st.rerun()

        # Obliczenia i wyniki
        fleet = get_packed_fleet(st.session_state.cargo, veh)
        
        for idx, truck in enumerate(fleet):
            st.markdown(f"<div style='border-left: 4px solid #00f2ff; padding-left: 15px;'><h4>AUTO #{idx+1} | {v_name}</h4></div>", unsafe_allow_html=True)
            col_viz, col_met = st.columns([2.5, 1])
            
            with col_viz:
                st.plotly_chart(draw_3d_pro(truck['stacks'], veh, st.session_state.color_map), use_container_width=True, key=f"p_{idx}")
            
            with col_met:
                st.metric("LDM", f"{truck['ldm']:.2f} m")
                st.metric("WAGA ŁADUNKU", f"{truck['weight']} kg")
                st.write("**OBCIĄŻENIE DMC:**")
                st.progress(min(truck['weight']/veh['maxWeight'], 1.0))
                st.dataframe(pd.DataFrame([it for s in truck['stacks'] for it in s['items']]).groupby('name').size().reset_index(name='Sztuk'), hide_index=True)
            st.divider()
    else:
        st.info("System gotowy. Dodaj sprzęt w panelu bocznym.")
