import streamlit as st
import json
import plotly.graph_objects as go
import math
import pandas as pd

# --- 1. KONFIGURACJA I STYLIZACJA ULTRA-PRO ---
st.set_page_config(
    page_title="SQM Logistics Terminal | Ultra-Pro v5", 
    page_icon="🚛",
    layout="wide", 
    initial_sidebar_state="expanded"
)

# Stylizacja High-Tech (Dark Mode z neonowymi akcentami) - Twoja ustalona stylistyka
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
    
    /* Karty kontenerów i edytora */
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
    .stButton>button:hover { 
        box-shadow: 0 0 15px rgba(59, 130, 246, 0.5); 
        transform: scale(1.02); 
    }
    
    /* Ukrycie domyślnych elementów Streamlit */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# --- 2. LOGOWANIE (SECRETS) ---
def check_password():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    if not st.session_state.authenticated:
        col1, col2, col3 = st.columns([1, 1.5, 1])
        with col2:
            st.markdown("<h1 style='text-align: center; color: #00f2ff; margin-top: 50px;'>SQM LOGISTICS</h1>", unsafe_allow_html=True)
            st.markdown("<p style='text-align: center; color: #64748b;'>SYSTEM ZARZĄDZANIA TERMINALEM</p>", unsafe_allow_html=True)
            try:
                master_password = str(st.secrets["password"])
            except:
                st.error("Błąd: Skonfiguruj klucz 'password' w Secrets.")
                return False
            
            pwd = st.text_input("Klucz dostępu:", type="password")
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

@st.cache_data
def load_products():
    try:
        with open('products.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            # Walidacja pola itemsPerCase
            for p in data:
                if 'itemsPerCase' not in p or p['itemsPerCase'] < 1:
                    p['itemsPerCase'] = 1
            return sorted(data, key=lambda x: x.get('name', ''))
    except Exception as e:
        st.error(f"Nie znaleziono pliku products.json: {e}")
        return []

# --- 4. LOGIKA PRZELICZANIA I SILNIK PAKOWANIA ---

def convert_items_to_units(manifest, all_prods):
    """Przelicza sztuki sprzętu na konkretne case'y do ułożenia."""
    transport_units = []
    for item in manifest:
        prod_ref = next((p for p in all_prods if p['name'] == item['name']), None)
        if not prod_ref: continue
        
        # Obliczamy ile pełnych i niepełnych opakowań potrzeba
        num_cases = math.ceil(item['qty'] / prod_ref['itemsPerCase'])
        
        for _ in range(num_cases):
            unit = prod_ref.copy()
            transport_units.append(unit)
    return transport_units

@st.cache_data(show_spinner=False)
def get_packed_fleet(transport_units, vehicle):
    """
    Zaawansowany algorytm Shelf-Packing z rygorystycznym resetem rzędów (v5.1).
    Eliminuje błąd wychodzenia poza obrys naczepy.
    """
    remaining_items = [dict(i) for i in transport_units]
    fleet = []
    
    while remaining_items:
        placed_stacks = []
        not_placed = []
        current_weight = 0
        max_reached_l = 0
        
        # Sortowanie: największa podstawa najpierw
        items_to_pack = sorted(remaining_items, key=lambda x: (x['length'] * x['width']), reverse=True)
        
        shelf_x = 0      # Postęp wzdłuż naczepy (X)
        shelf_y = 0      # Postęp wzdłuż szerokości (Y)
        shelf_max_x = 0  # Maksymalna długość elementu w obecnym rzędzie

        for item in items_to_pack:
            # 1. Limit DMC
            if current_weight + item['weight'] > vehicle['maxWeight']:
                not_placed.append(item)
                continue
                
            added = False
            
            # 2. Próba piętrowania (Stacking)
            if item.get('canStack', True):
                for s in placed_stacks:
                    # Dopasowanie podstawy musi być idealne (lub w granicach stabilności)
                    if s['canStackBase'] and (item['width'] == s['width'] and item['length'] == s['length']) and (s['currentH'] + item['height']) <= vehicle['H']:
                        it_copy = item.copy()
                        it_copy['z_pos'] = s['currentH']
                        it_copy['w_active'], it_copy['l_active'] = s['width'], s['length']
                        s['items'].append(it_copy)
                        s['currentH'] += item['height']
                        current_weight += item['weight']
                        added = True
                        break
            
            if added: continue

            # 3. Szukanie miejsca na podłodze (Shelf Packing z rotacją)
            best_fit = None
            # Sprawdzamy obie orientacje: normalną i obróconą o 90 stopni
            for w, l in [(item['width'], item['length']), (item['length'], item['width'])]:
                # Czy mieści się w obecnym rzędzie (szerokość Y)?
                if shelf_y + l <= vehicle['W'] and shelf_x + w <= vehicle['L']:
                    best_fit = (w, l, shelf_x, shelf_y)
                    break
                # Jeśli nie, czy mieści się w NOWYM rzędzie (następna sekcja X)?
                elif shelf_x + shelf_max_x + w <= vehicle['L'] and l <= vehicle['W']:
                    best_fit = (w, l, shelf_x + shelf_max_x, 0)
                    break

            if best_fit:
                fit_w, fit_l, pos_x, pos_y = best_fit
                
                # Jeśli przeskoczyliśmy do nowego rzędu (pos_y == 0), aktualizujemy bazę rzędu
                if pos_y == 0 and pos_x > shelf_x:
                    shelf_x = pos_x
                    shelf_y = 0
                    shelf_max_x = 0 
                
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

# --- 5. WIZUALIZACJA 3D (ULTRA-CLEAN RENDERER) ---
def draw_3d_pro(stacks, vehicle, color_map):
    fig = go.Figure()
    L, W, H = vehicle['L'], vehicle['W'], vehicle['H']

    # 1. Podłoga i neonowa rama naczepy
    fig.add_trace(go.Scatter3d(
        x=[0, L, L, 0, 0, None, 0, L, L, 0, 0, None, 0, 0, None, L, L, None, L, L, None, 0, 0],
        y=[0, 0, W, W, 0, None, 0, 0, W, W, 0, None, 0, 0, None, 0, 0, None, W, W, None, W, W],
        z=[0, 0, 0, 0, 0, None, H, H, H, H, H, None, 0, H, None, 0, H, None, 0, H, None, 0, H],
        mode='lines', line=dict(color='#00f2ff', width=3), hoverinfo='skip'
    ))

    # Trace dla krawędzi skrzyń (jeden ślad dla wydajności)
    edge_x, edge_y, edge_z = [], [], []

    for s in stacks:
        for it in s['items']:
            x, y, z = s['x'], s['y'], it['z_pos']
            dx, dy, dz = it.get('w_active', s['width']), it.get('l_active', s['length']), it['height']
            color = color_map.get(it['name'], "#3b82f6")
            
            # Główna bryła (Mesh)
            fig.add_trace(go.Mesh3d(
                x=[x, x+dx, x+dx, x, x, x+dx, x+dx, x],
                y=[y, y, y+dy, y+dy, y, y, y+dy, y+dy],
                z=[z, z, z, z, z+dz, z+dz, z+dz, z+dz],
                i=[7,0,0,0,4,4,6,6,4,0,3,2], j=[3,4,1,2,5,6,5,2,0,1,6,3], k=[0,7,2,3,6,7,1,1,5,5,7,6],
                opacity=0.85, color=color, flatshading=True, name=it['name']
            ))
            
            # Obliczanie krawędzi (czarne kontury)
            ex = [x, x+dx, x+dx, x, x, None, x, x+dx, x+dx, x, x, None, x, x, None, x+dx, x+dx, None, x+dx, x+dx, None, x, x]
            ey = [y, y, y+dy, y+dy, y, None, y, y, y+dy, y+dy, y, None, y, y, None, y, y, None, y+dy, y+dy, None, y+dy, y+dy]
            ez = [z, z, z, z, z, None, z+dz, z+dz, z+dz, z+dz, z+dz, None, z, z+dz, None, z, z+dz, None, z, z+dz, None, z, z+dz]
            edge_x.extend(ex); edge_y.extend(ey); edge_z.extend(ez); edge_x.append(None); edge_y.append(None); edge_z.append(None)

    fig.add_trace(go.Scatter3d(x=edge_x, y=edge_y, z=edge_z, mode='lines', line=dict(color='black', width=1.5), hoverinfo='skip'))

    fig.update_layout(
        scene=dict(
            xaxis=dict(title="DŁ (cm)", backgroundcolor="#020617", color="white", showgrid=False),
            yaxis=dict(title="SZ (cm)", backgroundcolor="#020617", color="white", showgrid=False),
            zaxis=dict(title="WY (cm)", backgroundcolor="#020617", color="white", showgrid=False),
            aspectmode='manual', aspectratio=dict(x=L/W*0.6, y=1, z=H/W*0.6)
        ),
        margin=dict(l=0, r=0, b=0, t=0), paper_bgcolor='rgba(0,0,0,0)', showlegend=False
    )
    return fig

# --- 6. INTERFEJS UŻYTKOWNIKA ---

if check_password():
    # Inicjalizacja sesji
    if 'manifest' not in st.session_state: st.session_state.manifest = []
    all_prods = load_products()
    
    if 'color_map' not in st.session_state:
        st.session_state.color_map = {p['name']: COLOR_PALETTE[i % len(COLOR_PALETTE)] for i, p in enumerate(all_prods)}

    # --- SIDEBAR: KONTROLA ---
    with st.sidebar:
        st.markdown("<h2 style='color: #00f2ff;'>SQM LOGISTICS</h2>", unsafe_allow_html=True)
        v_name = st.selectbox("TYP NACZEPY / AUTA:", list(VEHICLES.keys()))
        veh = VEHICLES[v_name]
        
        st.divider()
        st.subheader("📦 DODAJ SPRZĘT")
        sel_p_name = st.selectbox("PRODUKT Z BAZY:", [p['name'] for p in all_prods], index=None)
        p_qty = st.number_input("LICZBA SZTUK (ITEM QTY):", min_value=1, value=1)
        
        if st.button("DODAJ DO PLANU", use_container_width=True) and sel_p_name:
            # Sprawdź czy już jest na liście (jeśli tak, zsumuj)
            idx = next((i for i, m in enumerate(st.session_state.manifest) if m['name'] == sel_p_name), None)
            if idx is not None:
                st.session_state.manifest[idx]['qty'] += p_qty
            else:
                st.session_state.manifest.append({'name': sel_p_name, 'qty': p_qty})
            st.rerun()
            
        if st.button("WYCZYŚĆ LISTĘ", use_container_width=True, type="secondary"):
            st.session_state.manifest = []; st.rerun()

    # --- MAIN PANEL: WYNIKI ---
    if st.session_state.manifest:
        st.markdown("<h2 style='color: #00f2ff;'>📋 PLANOWANIE ZAŁADUNKU</h2>", unsafe_allow_html=True)
        
        # Tabela zbiorcza: Sztuki vs Opakowania
        st.subheader("Manifest i przeliczenie na jednostki")
        summary_list = []
        for m in st.session_state.manifest:
            p_ref = next(p for p in all_prods if p['name'] == m['name'])
            num_units = math.ceil(m['qty'] / p_ref['itemsPerCase'])
            summary_list.append({
                "Produkt": m['name'],
                "Sztuk sprzętu": m['qty'],
                "W jednym case": p_ref['itemsPerCase'],
                "Jednostek transportowych": num_units
            })
        st.table(pd.DataFrame(summary_list))

        # Konwersja manifestu na listę fizycznych jednostek
        transport_units = convert_items_to_units(st.session_state.manifest, all_prods)
        
        # Obliczenie floty (podział na auta)
        fleet = get_packed_fleet(transport_units, veh)
        
        # Wyświetlanie każdego auta
        for i, truck in enumerate(fleet):
            st.markdown(f"<div style='border-left: 5px solid #00f2ff; padding-left: 20px; margin-top: 40px;'><h3>AUTO #{i+1} | {v_name}</h3></div>", unsafe_allow_html=True)
            
            col_viz, col_data = st.columns([2.5, 1])
            
            with col_viz:
                st.plotly_chart(draw_3d_pro(truck['stacks'], veh, st.session_state.color_map), use_container_width=True, key=f"truck_viz_{i}")
            
            with col_data:
                st.metric("LDM (Metry bieżące)", f"{truck['ldm']:.2f} m")
                st.metric("WAGA ŁADUNKU", f"{truck['weight']} kg")
                
                # Obciążenie DMC
                load_pct = min(truck['weight'] / veh['maxWeight'], 1.0)
                st.write(f"**Wypełnienie DMC ({int(load_pct*100)}%):**")
                st.progress(load_pct)
                
                # Co dokładnie jest w tym aucie?
                items_in_truck = [it for s in truck['stacks'] for it in s['items']]
                truck_spec = pd.DataFrame(items_in_truck).groupby('name').size().reset_index(name='Liczba Case')
                st.dataframe(truck_spec, hide_index=True, use_container_width=True)
            st.divider()
    else:
        # Stan pusty (ekran startowy)
        st.info("Terminal gotowy. Wybierz sprzęt z bazy danych po lewej stronie, aby rozpocząć planowanie transportu.")
        st.markdown("""
            **Instrukcja:**
            1. Wybierz typ naczepy w panelu bocznym.
            2. Wybierz produkt z listy (pobieranej z `products.json`).
            3. Wpisz liczbę **sztuk sprzętu** (system sam przeliczy to na odpowiednią ilość case'ów).
            4. Kliknij 'Dodaj do planu' - algorytm automatycznie ułoży towar w 3D i wyliczy LDM.
        """)
