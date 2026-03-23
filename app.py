import streamlit as st
import json
import plotly.graph_objects as go
import math
import pandas as pd

# --- 1. KONFIGURACJA I STYLIZACJA ULTRA-PRO ---
st.set_page_config(
    page_title="SQM Logistics Terminal | Ultra-Pro v4", 
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
            {"name": "Paleta EPAL", "width": 80, "length": 120, "height": 140, "weight": 400, "canStack": True},
            {"name": "Case Mix 120x60", "width": 60, "length": 120, "height": 90, "weight": 110, "canStack": True},
            {"name": "Skrzynia LED", "width": 120, "length": 100, "height": 115, "weight": 380, "canStack": False}
        ]

# --- 4. NAPRAWIONY SILNIK PAKOWANIA (ELIMINACJA WYCIEKU POZA OBRYS) ---
@st.cache_data(show_spinner=False)
def get_packed_fleet(cargo_list, vehicle):
    """Precyzyjny algorytm Shelf-Packing z blokadą granic pojazdu."""
    remaining_items = [dict(i) for i in cargo_list]
    fleet = []
    
    while remaining_items:
        placed_stacks = []
        not_placed = []
        current_weight = 0
        max_reached_l = 0
        
        # Sortowanie: największa podstawa i wysokość najpierw
        items_to_pack = sorted(remaining_items, key=lambda x: (x['length'] * x['width'], x['height']), reverse=True)
        
        shelf_x = 0      # Postęp wzdłuż naczepy (Oś X)
        shelf_y = 0      # Postęp wzdłuż szerokości (Oś Y)
        shelf_max_x = 0  # Szerokość najszerszego elementu w obecnym rzędzie

        for item in items_to_pack:
            # 1. Limit DMC
            if current_weight + item['weight'] > vehicle['maxWeight']:
                not_placed.append(item)
                continue
                
            added = False
            
            # 2. Próba piętrowania (Stacking)
            if item.get('canStack', True):
                for s in placed_stacks:
                    # Dopasowanie podstawy 1:1 dla stabilności
                    match = (item['width'] == s['width'] and item['length'] == s['length'])
                    if s['canStackBase'] and match and (s['currentH'] + item['height']) <= vehicle['H']:
                        it_copy = item.copy()
                        it_copy['z_pos'] = s['currentH']
                        # Dziedziczenie orientacji rzędu
                        it_copy['w_active'], it_copy['l_active'] = s['width'], s['length']
                        s['items'].append(it_copy)
                        s['currentH'] += item['height']
                        current_weight += item['weight']
                        added = True
                        break
            
            if added: continue

            # 3. Szukanie miejsca na podłodze (Shelf Packing z rotacją)
            best_fit = None
            # Sprawdzamy obie orientacje (szerokość x długość)
            for w, l in [(item['width'], item['length']), (item['length'], item['width'])]:
                # Czy mieści się w obecnym rzędzie (Y)?
                if shelf_y + l <= vehicle['W'] and shelf_x + w <= vehicle['L']:
                    best_fit = (w, l, shelf_x, shelf_y)
                    break
                # Jeśli nie, czy mieści się w NOWYM rzędzie (X)?
                elif shelf_x + shelf_max_x + w <= vehicle['L'] and l <= vehicle['W']:
                    best_fit = (w, l, shelf_x + shelf_max_x, 0)
                    break

            if best_fit:
                fit_w, fit_l, pos_x, pos_y = best_fit
                
                # Jeśli przeskoczyliśmy do nowego rzędu (pos_y == 0), aktualizujemy bazę rzędu
                if pos_y == 0 and pos_x > shelf_x:
                    shelf_x = pos_x
                    shelf_y = 0
                    shelf_max_x = 0 # Resetowanie szerokości rzędu dla nowej linii
                
                it_copy = item.copy()
                it_copy['z_pos'] = 0
                it_copy['w_active'], it_copy['l_active'] = fit_w, fit_l
                
                placed_stacks.append({
                    'x': pos_x, 'y': pos_y, 'width': fit_w, 'length': fit_l, 
                    'currentH': item['height'], 'canStackBase': item.get('canStack', True), 'items': [it_copy]
                })
                
                shelf_y = pos_y + fit_l
                shelf_max_x = max(shelf_max_x, fit_w)
                current_weight += item['weight']
                max_reached_l = max(max_reached_l, pos_x + fit_w)
                added = True
            else:
                not_placed.append(item)
        
        if not placed_stacks: break
        fleet.append({"stacks": placed_stacks, "weight": current_weight, "ldm": max_reached_l/100})
        remaining_items = not_placed
                
    return fleet

# --- 5. WYDAJNA WIZUALIZACJA 3D (SINGLE-TRACE EDGES) ---
def draw_3d_pro(stacks, vehicle, color_map):
    fig = go.Figure()
    L, W, H = vehicle['L'], vehicle['W'], vehicle['H']

    # 1. Podłoga i neonowy obrys naczepy
    fig.add_trace(go.Mesh3d(x=[0, L, L, 0], y=[0, 0, W, W], z=[0, 0, 0, 0], color='#1e293b', opacity=1.0, hoverinfo='skip'))
    
    fig.add_trace(go.Scatter3d(
        x=[0, L, L, 0, 0, None, 0, L, L, 0, 0, None, 0, 0, None, L, L, None, L, L, None, 0, 0],
        y=[0, 0, W, W, 0, None, 0, 0, W, W, 0, None, 0, 0, None, 0, 0, None, W, W, None, W, W],
        z=[0, 0, 0, 0, 0, None, H, H, H, H, H, None, 0, H, None, 0, H, None, 0, H, None, 0, H],
        mode='lines', line=dict(color='#00f2ff', width=2), hoverinfo='skip'
    ))

    # Zbiory dla krawędzi skrzyń (optymalizacja prędkości)
    edge_x, edge_y, edge_z = [], [], []

    for s in stacks:
        for it in s['items']:
            x, y, z = s['x'], s['y'], it['z_pos']
            # Pobieramy wymiary po rotacji przeliczone przez silnik
            dx, dy, dz = it.get('w_active', s['width']), it.get('l_active', s['length']), it['height']
            color = color_map.get(it['name'], "#3b82f6")
            
            # Bryła 3D
            fig.add_trace(go.Mesh3d(
                x=[x, x+dx, x+dx, x, x, x+dx, x+dx, x],
                y=[y, y, y+dy, y+dy, y, y, y+dy, y+dy],
                z=[z, z, z, z, z+dz, z+dz, z+dz, z+dz],
                i=[7,0,0,0,4,4,6,6,4,0,3,2], j=[3,4,1,2,5,6,5,2,0,1,6,3], k=[0,7,2,3,6,7,1,1,5,5,7,6],
                opacity=0.8, color=color, flatshading=True, name=it['name']
            ))
            
            # Dodawanie krawędzi do wspólnego trace'a
            ex = [x, x+dx, x+dx, x, x, None, x, x+dx, x+dx, x, x, None, x, x, None, x+dx, x+dx, None, x+dx, x+dx, None, x, x]
            ey = [y, y, y+dy, y+dy, y, None, y, y, y+dy, y+dy, y, None, y, y, None, y, y, None, y+dy, y+dy, None, y+dy, y+dy]
            ez = [z, z, z, z, z, None, z+dz, z+dz, z+dz, z+dz, z+dz, None, z, z+dz, None, z, z+dz, None, z, z+dz, None, z, z+dz]
            edge_x.extend(ex); edge_y.extend(ey); edge_z.extend(ez); edge_x.append(None); edge_y.append(None); edge_z.append(None)

    fig.add_trace(go.Scatter3d(x=edge_x, y=edge_y, z=edge_z, mode='lines', line=dict(color='black', width=1.5), hoverinfo='skip'))

    fig.update_layout(
        scene=dict(
            xaxis=dict(range=[0, L], title="DL (cm)", backgroundcolor="#020617"),
            yaxis=dict(range=[0, W], title="SZ (cm)", backgroundcolor="#020617"),
            zaxis=dict(range=[0, H], title="WY (cm)", backgroundcolor="#020617"),
            aspectmode='manual', aspectratio=dict(x=L/W*0.6, y=1, z=H/W*0.6)
        ),
        margin=dict(l=0, r=0, b=0, t=0), paper_bgcolor='rgba(0,0,0,0)', showlegend=False
    )
    return fig

# --- 6. INTERFEJS ---
if check_password():
    if 'cargo' not in st.session_state: st.session_state.cargo = []
    prods = load_products()
    if 'color_map' not in st.session_state:
        st.session_state.color_map = {p['name']: COLOR_PALETTE[i % len(COLOR_PALETTE)] for i, p in enumerate(prods)}

    with st.sidebar:
        st.markdown("<h2 style='color: #00f2ff;'>SQM PANEL</h2>", unsafe_allow_html=True)
        v_name = st.selectbox("TYP POJAZDU:", list(VEHICLES.keys()))
        veh = VEHICLES[v_name]
        
        st.divider()
        st.subheader("📦 DODAJ ELEMENTY")
        sel_p = st.selectbox("PRODUKT:", [p['name'] for p in prods], index=None)
        qty = st.number_input("ILOŚĆ SZTUK:", min_value=1, value=1)
        
        if st.button("DODAJ DO PLANU", use_container_width=True) and sel_p:
            p_ref = next(p for p in prods if p['name'] == sel_p)
            for _ in range(qty): 
                st.session_state.cargo.append(p_ref.copy())
            st.rerun()
            
        if st.button("WYCZYŚĆ LISTĘ", use_container_width=True, type="secondary"):
            st.session_state.cargo = []; st.rerun()

    if st.session_state.cargo:
        st.markdown("<h3 style='color: #00f2ff;'>📋 MANIFEST ZAŁADUNKOWY</h3>", unsafe_allow_html=True)
        # Agregacja do edycji
        df_cargo = pd.DataFrame(st.session_state.cargo)
        sum_df = df_cargo.groupby('name').size().reset_index(name='ilość')
        
        edited = st.data_editor(sum_df, hide_index=True, use_container_width=True, key="v4_editor")
        
        if not edited.equals(sum_df):
            new_c = []
            for _, r in edited.iterrows():
                if r['ilość'] > 0:
                    orig = next(p for p in prods if p['name'] == r['name'])
                    new_c.extend([orig.copy() for _ in range(r['ilość'])])
            st.session_state.cargo = new_c; st.rerun()

        # Obliczenia
        fleet = get_packed_fleet(st.session_state.cargo, veh)
        
        for idx, truck in enumerate(fleet):
            st.markdown(f"<div style='border-left: 4px solid #00f2ff; padding-left: 15px;'><h4>AUTO #{idx+1} | {v_name}</h4></div>", unsafe_allow_html=True)
            col_viz, col_met = st.columns([2.5, 1])
            
            with col_viz:
                st.plotly_chart(draw_3d_pro(truck['stacks'], veh, st.session_state.color_map), use_container_width=True, key=f"v4_p_{idx}")
            
            with col_met:
                st.metric("LDM", f"{truck['ldm']:.2f} m")
                st.metric("WAGA CAŁKOWITA", f"{truck['weight']} kg")
                st.write("**OBCIĄŻENIE DMC:**")
                st.progress(min(truck['weight']/veh['maxWeight'], 1.0))
                
                # Zestawienie towarów w tym konkretnym aucie
                items_in_truck = [it for s in truck['stacks'] for it in s['items']]
                st.dataframe(pd.DataFrame(items_in_truck).groupby('name').size().reset_index(name='Sztuk'), hide_index=True, use_container_width=True)
            st.divider()
    else:
        st.info("Brak danych do wyświetlenia. Wybierz sprzęt w panelu bocznym.")
