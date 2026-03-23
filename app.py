import streamlit as st
import json
import plotly.graph_objects as go
import math
import pandas as pd

# --- 1. KONFIGURACJA I STYLIZACJA ---
st.set_page_config(page_title="PRO Logistics Planner v3.2", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; border: 1px solid #e0e0e0; }
    .stExpander { border: 1px solid #d1d1d1; border-radius: 10px; background-color: white !important; }
    footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# --- 2. LOGOWANIE (SECRETS) ---
def check_password():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    if not st.session_state.authenticated:
        st.title("🔐 Logistics Terminal")
        try:
            # Hasło musi być zdefiniowane w .streamlit/secrets.toml lub w panelu Cloud
            master_password = str(st.secrets["password"])
        except:
            st.error("Brak hasła w systemie Secrets (klucz 'password').")
            return False
        pwd = st.text_input("Hasło dostępu:", type="password")
        if st.button("Zaloguj"):
            if pwd == master_password:
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("Błędne hasło.")
        return False
    return True

# --- 3. PARAMETRY POJAZDÓW ---
VEHICLES = {
    "BUS": {"maxWeight": 1100, "L": 450, "W": 150, "H": 245, "color": "#ffca28"},
    "6m": {"maxWeight": 3500, "L": 600, "W": 245, "H": 245, "color": "#42a5f5"},
    "7m": {"maxWeight": 7000, "L": 700, "W": 245, "H": 245, "color": "#66bb6a"},
    "FTL": {"maxWeight": 24000, "L": 1360, "W": 245, "H": 265, "color": "#ef5350"}
}

COLOR_PALETTE = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd", "#8c564b", "#e377c2", "#bcbd22", "#17becf"]

def load_products():
    try:
        with open('products.json', 'r', encoding='utf-8') as f:
            return sorted(json.load(f), key=lambda x: x.get('name', ''))
    except:
        # Fallback danych demonstracyjnych
        return [
            {"name": "Paleta EPAL 1", "width": 80, "length": 120, "height": 140, "weight": 450, "canStack": True, "itemsPerCase": 1},
            {"name": "Skrzynia Drewniana", "width": 100, "length": 100, "height": 100, "weight": 200, "canStack": True, "itemsPerCase": 1},
            {"name": "Karton Zbiorczy", "width": 60, "length": 40, "height": 40, "weight": 20, "canStack": True, "itemsPerCase": 10}
        ]

# --- 4. LOGIKA PAKOWANIA (PUNKT 1: ROTACJA + SHELF-PACKING) ---
def pack_one_vehicle(remaining_items, vehicle):
    placed_stacks = []
    not_placed = []
    current_weight = 0
    max_reached_l = 0
    
    # Sortowanie dla stabilności: największa powierzchnia podstawy na dół
    items_to_pack = sorted(remaining_items, key=lambda x: (x['length'] * x['width']), reverse=True)

    # Parametry Shelf-Packing
    shelf_x = 0      # Postęp wzdłuż długości (L)
    shelf_y = 0      # Postęp wzdłuż szerokości (W)
    shelf_max_w = 0  # Maksymalna szerokość aktualnego rzędu (oś X)

    for item in items_to_pack:
        # Limit wagowy
        if current_weight + item['weight'] > vehicle['maxWeight']:
            not_placed.append(item)
            continue
            
        added = False

        # PRÓBA PIĘTROWANIA (Stacking)
        if item.get('canStack', True):
            for s in placed_stacks:
                # Sprawdź dopasowanie wymiarów (z uwzględnieniem rotacji stosu)
                match = (item['width'] == s['width'] and item['length'] == s['length']) or \
                        (item['width'] == s['length'] and item['length'] == s['width'])
                
                if s['canStackBase'] and match and (s['currentH'] + item['height']) <= vehicle['H']:
                    it_copy = item.copy()
                    it_copy['z_pos'] = s['currentH']
                    # Wizualne wyrównanie do podstawy stosu
                    it_copy['width'], it_copy['length'] = s['width'], s['length']
                    
                    s['items'].append(it_copy)
                    s['currentH'] += item['height']
                    current_weight += item['weight']
                    added = True
                    break
        
        if added: continue

        # NOWY STOS (Shelf Packing + Rotacja 90°)
        w, l = item['width'], item['length']
        orientations = [(w, l), (l, w)]
        
        found_spot = False
        for fit_w, fit_l in orientations:
            # 1. Sprawdź miejsce w obecnym rzędzie (Y)
            if shelf_y + fit_l <= vehicle['W'] and shelf_x + fit_w <= vehicle['L']:
                it_copy = item.copy()
                it_copy['z_pos'] = 0
                it_copy['width'], it_copy['length'] = fit_w, fit_l
                
                placed_stacks.append({
                    'x': shelf_x, 'y': shelf_y, 'width': fit_w, 'length': fit_l,
                    'currentH': item['height'], 'canStackBase': item.get('canStack', True),
                    'items': [it_copy]
                })
                
                shelf_y += fit_l
                shelf_max_w = max(shelf_max_w, fit_w)
                found_spot = True
                break
            
            # 2. Próbuj otworzyć nowy rząd (X)
            elif shelf_x + shelf_max_w + fit_w <= vehicle['L'] and fit_l <= vehicle['W']:
                shelf_x += shelf_max_w
                shelf_y = 0
                shelf_max_w = fit_w
                
                it_copy = item.copy()
                it_copy['z_pos'] = 0
                it_copy['width'], it_copy['length'] = fit_w, fit_l
                
                placed_stacks.append({
                    'x': shelf_x, 'y': shelf_y, 'width': fit_w, 'length': fit_l,
                    'currentH': item['height'], 'canStackBase': item.get('canStack', True),
                    'items': [it_copy]
                })
                
                shelf_y += fit_l
                found_spot = True
                break

        if found_spot:
            current_weight += item['weight']
            max_reached_l = max(max_reached_l, shelf_x + shelf_max_w)
        else:
            not_placed.append(item)
                
    return placed_stacks, current_weight, not_placed, max_reached_l

# --- 5. WIZUALIZACJA 3D ---
def draw_3d(placed_stacks, vehicle, color_map):
    fig = go.Figure()
    v_l, v_w, v_h = vehicle['L'], vehicle['W'], vehicle['H']

    # Podłoga pojazdu
    fig.add_trace(go.Mesh3d(
        x=[0, v_l, v_l, 0], y=[0, 0, v_w, v_w], z=[0, 0, 0, 0],
        color='lightgrey', opacity=0.4, name="Podłoga"
    ))
    
    # Obrys klatki naczepy
    edges = [
        ([0, v_l], [0, 0], [0, 0]), ([0, v_l], [v_w, v_w], [0, 0]), ([0, v_l], [0, 0], [v_h, v_h]), ([0, v_l], [v_w, v_w], [v_h, v_h]),
        ([0, 0], [0, v_w], [0, 0]), ([v_l, v_l], [0, v_w], [0, 0]), ([0, 0], [0, v_w], [v_h, v_h]), ([v_l, v_l], [0, v_w], [v_h, v_h]),
        ([0, 0], [0, 0], [0, v_h]), ([v_l, v_l], [0, 0], [0, v_h]), ([0, 0], [v_w, v_w], [0, v_h]), ([v_l, v_l], [v_w, v_w], [0, v_h])
    ]
    for ex, ey, ez in edges:
        fig.add_trace(go.Scatter3d(x=ex, y=ey, z=ez, mode='lines', line=dict(color='black', width=1), hoverinfo='none'))

    # Rysowanie ładunków
    for s in placed_stacks:
        for it in s['items']:
            x0, y0, z0 = s['x'], s['y'], it['z_pos']
            dx, dy, dz = it['width'], it['length'], it['height']
            
            # Wierzchołki prostopadłościanu
            fig.add_trace(go.Mesh3d(
                x=[x0, x0+dx, x0+dx, x0, x0, x0+dx, x0+dx, x0],
                y=[y0, y0, y0+dy, y0+dy, y0, y0, y0+dy, y0+dy],
                z=[z0, z0, z0, z0, z0+dz, z0+dz, z0+dz, z0+dz],
                i=[7,0,0,0,4,4,6,6,4,0,3,2], j=[3,4,1,2,5,6,5,2,0,1,6,3], k=[0,7,2,3,6,7,1,1,5,5,7,6],
                opacity=0.9, color=color_map.get(it['name'], "#808080"), name=it['name']
            ))

    fig.update_layout(
        scene=dict(
            xaxis=dict(title='Długość (cm)', range=[0, v_l]),
            yaxis=dict(title='Szerokość (cm)', range=[0, v_w]),
            zaxis=dict(title='Wysokość (cm)', range=[0, v_h]),
            aspectmode='manual', aspectratio=dict(x=v_l/v_w, y=1, z=v_h/v_w)
        ),
        margin=dict(l=0, r=0, b=0, t=0), showlegend=False
    )
    return fig

# --- 6. APLIKACJA GŁÓWNA ---
if check_password():
    if 'cargo' not in st.session_state: st.session_state.cargo = []
    prods = load_products()
    
    if 'color_map' not in st.session_state:
        st.session_state.color_map = {p['name']: COLOR_PALETTE[i % len(COLOR_PALETTE)] for i, p in enumerate(prods)}

    # PANEL BOCZNY
    with st.sidebar:
        st.title("🚛 Panel Sterowania")
        v_name = st.selectbox("Typ Pojazdu:", list(VEHICLES.keys()))
        veh = VEHICLES[v_name]
        
        st.divider()
        st.subheader("📦 Dodaj Towar")
        sel_p_name = st.selectbox("Produkt z bazy:", [p['name'] for p in prods], index=None)
        qty = st.number_input("Ilość sztuk:", min_value=1, value=1)
        
        if st.button("Dodaj do planu", use_container_width=True) and sel_p_name:
            p_ref = next(p for p in prods if p['name'] == sel_p_name)
            ipc = p_ref.get('itemsPerCase', 1)
            # Dzielenie sztuk na jednostki transportowe (skrzynie/palety)
            num_units = math.ceil(qty / ipc)
            for i in range(num_units):
                c = p_ref.copy()
                remainder = qty % ipc
                c['actual_items'] = remainder if (i == num_units - 1 and remainder != 0) else ipc
                st.session_state.cargo.append(c)
            st.rerun()
            
        if st.button("Usuń wszystko", use_container_width=True, type="secondary"):
            st.session_state.cargo = []
            st.rerun()

    # WIDOK GŁÓWNY
    if st.session_state.cargo:
        st.header("📋 Lista Wysyłkowa")
        
        # Przygotowanie danych do edytora
        df_cargo = pd.DataFrame(st.session_state.cargo)
        # Sumujemy sztuki, aby użytkownik edytował łączną ilość
        sum_df = df_cargo.groupby('name').agg({'actual_items': 'sum'}).reset_index()
        
        st.info("Zmień wartość w kolumnie **actual_items** i naciśnij Enter. Wpisanie **0** usunie produkt.")
        
        # EDYTOR LISTY (PUNKT 2: Edycja i kasowanie przy 0)
        edited_df = st.data_editor(
            sum_df, 
            hide_index=True, 
            use_container_width=True,
            column_config={
                "name": st.column_config.Column("Produkt", disabled=True),
                "actual_items": st.column_config.NumberColumn("Sztuk Razem", min_value=0, step=1)
            },
            key="main_cargo_editor"
        )

        # Synchronizacja po edycji
        if not edited_df.equals(sum_df):
            new_cargo = []
            for _, row in edited_df.iterrows():
                if row['actual_items'] > 0:
                    p_orig = next((p for p in prods if p['name'] == row['name']), None)
                    if p_orig:
                        ipc = p_orig.get('itemsPerCase', 1)
                        total_q = row['actual_items']
                        num_u = math.ceil(total_q / ipc)
                        for i in range(num_u):
                            unit = p_orig.copy()
                            rem = total_q % ipc
                            unit['actual_items'] = rem if (i == num_u - 1 and rem != 0) else ipc
                            new_cargo.append(unit)
            st.session_state.cargo = new_cargo
            st.rerun()

        # SILNIK PAKOWANIA (Wiele pojazdów jeśli potrzeba)
        rem_cargo = [dict(i) for i in st.session_state.cargo]
        fleet_results = []
        
        while rem_cargo:
            stacks, weight, not_p, m_l = pack_one_vehicle(rem_cargo, veh)
            if not stacks: # Jeśli nic nie weszło do pustego auta, przerwij by uniknąć pętli
                break
            fleet_results.append({"stacks": stacks, "weight": weight, "ldm": m_l/100})
            rem_cargo = not_p

        # WYŚWIETLANIE WYNIKÓW
        st.divider()
        st.header(f"📊 Plan Załadunku: {len(fleet_results)} auto/a")

        if rem_cargo:
            st.warning(f"⚠️ Nie udało się zapakować {len(rem_cargo)} jednostek! Zmień typ pojazdu.")

        for idx, truck in enumerate(fleet_results):
            with st.container():
                st.subheader(f"🚛 Pojazd #{idx+1} ({v_name})")
                
                # Obliczenia metryk
                all_items_in_truck = [it for s in truck['stacks'] for it in s['items']]
                vol_used = sum(it['width']*it['length']*it['height'] for it in all_items_in_truck) / 1000000
                vol_total = (veh['L']*veh['W']*veh['H']) / 1000000
                floor_area_used = sum(s['width']*s['length'] for s in truck['stacks'])
                floor_total = veh['L']*veh['W']
                
                m1, m2, m3, m4 = st.columns(4)
                m1.metric("LDM", f"{truck['ldm']:.2f} m")
                m2.metric("Zajęcie Podłogi", f"{int(floor_area_used/floor_total*100)}%")
                m3.metric("Waga", f"{truck['weight']} / {veh['maxWeight']} kg")
                m4.metric("Objętość", f"{vol_used:.1f} m³")

                col_viz, col_tab = st.columns([3, 2])
                with col_viz:
                    st.plotly_chart(draw_3d(truck['stacks'], veh, st.session_state.color_map), use_container_width=True, key=f"plot_{idx}")
                with col_tab:
                    st.write("**📍 Specyfikacja załadunku:**")
                    df_in = pd.DataFrame(all_items_in_truck)
                    res = df_in.groupby('name').agg({'actual_items': 'sum', 'name': 'count', 'weight': 'sum'}).rename(
                        columns={'actual_items':'Sztuk','name':'Jednostek','weight':'Waga (kg)'}
                    )
                    st.dataframe(res.reset_index(), use_container_width=True, hide_index=True)
                    
                    st.write("**Wykorzystanie DMC:**")
                    st.progress(min(truck['weight']/veh['maxWeight'], 1.0))
                st.divider()
    else:
        st.info("Brak towarów. Wybierz produkty z panelu bocznego, aby wygenerować plan.")
