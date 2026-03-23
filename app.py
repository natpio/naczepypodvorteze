import streamlit as st
import json
import plotly.graph_objects as go
import math
import pandas as pd
import random

# --- 1. KONFIGURACJA I STYLIZACJA ---
st.set_page_config(page_title="SQM Logistics Planner v3.5", layout="wide")

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
            # Hasło pobierane z .streamlit/secrets.toml (klucz "password")
            master_password = str(st.secrets["password"])
        except:
            st.error("Błąd: Brak hasła w konfiguracji systemowej.")
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
    "BUS": {"maxWeight": 1100, "L": 450, "W": 150, "H": 245},
    "6m": {"maxWeight": 3500, "L": 600, "W": 245, "H": 245},
    "7m": {"maxWeight": 7000, "L": 700, "W": 245, "H": 245},
    "FTL (Standard)": {"maxWeight": 24000, "L": 1360, "W": 245, "H": 265},
    "Mega": {"maxWeight": 24000, "L": 1360, "W": 245, "H": 300}
}

def generate_color_palette(n):
    """Generuje listę n unikalnych kolorów HEX."""
    colors = []
    for i in range(n):
        # Generowanie kolorów z pominięciem bardzo ciemnych i bardzo jasnych
        r = random.randint(60, 210)
        g = random.randint(60, 210)
        b = random.randint(60, 210)
        colors.append(f'#{r:02x}{g:02x}{b:02x}')
    return colors

def load_products():
    try:
        with open('products.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            # Standaryzacja pól
            for p in data:
                if 'itemsPerCase' not in p: p['itemsPerCase'] = 1
                if 'weight' not in p: p['weight'] = 5
            return sorted(data, key=lambda x: x.get('name', ''))
    except Exception as e:
        st.error(f"Nie można załadować bazy produktów: {e}")
        return [{"name": "Standardowa Paleta", "width": 80, "length": 120, "height": 140, "weight": 400, "canStack": True, "itemsPerCase": 1}]

# --- 4. LOGIKA PAKOWANIA (FIRST-FIT DECREASING) ---
def pack_one_vehicle(remaining_items, vehicle):
    placed_stacks = []
    not_placed = []
    current_weight = 0
    max_reached_l = 0
    
    # Sortowanie po powierzchni podstawy (większe najpierw)
    items_to_pack = sorted(remaining_items, key=lambda x: (x['length'] * x['width']), reverse=True)
    shelf_x, shelf_y, shelf_max_w = 0, 0, 0

    for item in items_to_pack:
        if current_weight + item['weight'] > vehicle['maxWeight']:
            not_placed.append(item)
            continue
            
        added = False
        # Próba sztaplowania (stacking)
        if item.get('canStack', True):
            for s in placed_stacks:
                match = (item['width'] == s['width'] and item['length'] == s['length']) or \
                        (item['width'] == s['length'] and item['length'] == s['width'])
                if s['canStackBase'] and match and (s['currentH'] + item['height']) <= vehicle['H']:
                    it_copy = item.copy()
                    it_copy['z_pos'] = s['currentH']
                    it_copy['width'], it_copy['length'] = s['width'], s['length']
                    s['items'].append(it_copy)
                    s['currentH'] += item['height']
                    current_weight += item['weight']
                    added = True
                    break
        
        if added: continue

        # Próba postawienia na podłodze (rotacja 90 st.)
        w, l = item['width'], item['length']
        for fit_w, fit_l in [(w, l), (l, w)]:
            if shelf_y + fit_l <= vehicle['W'] and shelf_x + fit_w <= vehicle['L']:
                it_copy = item.copy()
                it_copy['z_pos'] = 0
                it_copy['width'], it_copy['length'] = fit_w, fit_l
                placed_stacks.append({
                    'x': shelf_x, 'y': shelf_y, 'width': fit_w, 'length': fit_l, 
                    'currentH': item['height'], 'canStackBase': item.get('canStack', True), 'items': [it_copy]
                })
                shelf_y += fit_l
                shelf_max_w = max(shelf_max_w, fit_w)
                current_weight += item['weight']
                max_reached_l = max(max_reached_l, shelf_x + shelf_max_w)
                added = True
                break
            elif shelf_x + shelf_max_w + fit_w <= vehicle['L'] and fit_l <= vehicle['W']:
                shelf_x += shelf_max_w
                shelf_y, shelf_max_w = 0, fit_w
                it_copy = item.copy()
                it_copy['z_pos'] = 0
                it_copy['width'], it_copy['length'] = fit_w, fit_l
                placed_stacks.append({
                    'x': shelf_x, 'y': shelf_y, 'width': fit_w, 'length': fit_l,
                    'currentH': item['height'], 'canStackBase': item.get('canStack', True), 'items': [it_copy]
                })
                shelf_y += fit_l
                current_weight += item['weight']
                max_reached_l = max(max_reached_l, shelf_x + shelf_max_w)
                added = True
                break
        
        if not added: 
            not_placed.append(item)
                
    return placed_stacks, current_weight, not_placed, max_reached_l

# --- 5. WIZUALIZACJA 3D ---
def draw_3d(placed_stacks, vehicle, color_map):
    fig = go.Figure()
    v_l, v_w, v_h = vehicle['L'], vehicle['W'], vehicle['H']

    # Wizualizacja konturów naczepy
    fig.add_trace(go.Mesh3d(x=[0, v_l, v_l, 0], y=[0, 0, v_w, v_w], z=[0, 0, 0, 0], color='lightgrey', opacity=0.1, hoverinfo='skip'))
    
    for s in placed_stacks:
        for it in s['items']:
            x0, y0, z0 = s['x'], s['y'], it['z_pos']
            dx, dy, dz = it['width'], it['length'], it['height']
            
            # Etykieta Hover - informacja po najechaniu myszką
            hover_text = (f"<b>{it['name']}</b><br>"
                          f"Wymiary: {dx} x {dy} x {dz} cm<br>"
                          f"Waga: {it['weight']} kg")
            
            fig.add_trace(go.Mesh3d(
                x=[x0, x0+dx, x0+dx, x0, x0, x0+dx, x0+dx, x0],
                y=[y0, y0, y0+dy, y0+dy, y0, y0, y0+dy, y0+dy],
                z=[z0, z0, z0, z0, z0+dz, z0+dz, z0+dz, z0+dz],
                i=[7,0,0,0,4,4,6,6,4,0,3,2], j=[3,4,1,2,5,6,5,2,0,1,6,3], k=[0,7,2,3,6,7,1,1,5,5,7,6],
                opacity=0.9, 
                color=color_map.get(it['name'], "#808080"),
                hovertext=hover_text, 
                hoverinfo="text",
                name=it['name']
            ))

    fig.update_layout(
        scene=dict(
            xaxis=dict(title='Długość (cm)', range=[0, v_l]),
            yaxis=dict(title='Szerokość (cm)', range=[0, v_w]),
            zaxis=dict(title='Wysokość (cm)', range=[0, v_h]),
            aspectmode='manual', aspectratio=dict(x=v_l/v_w, y=1, z=v_h/v_w)
        ),
        margin=dict(l=0, r=0, b=0, t=0), 
        showlegend=False
    )
    return fig

# --- 6. GŁÓWNA LOGIKA APLIKACJI ---
if check_password():
    if 'cargo' not in st.session_state: st.session_state.cargo = []
    prods = load_products()
    
    # Przypisanie unikalnego koloru do każdego produktu z bazy
    if 'color_map' not in st.session_state:
        palette = generate_color_palette(len(prods))
        st.session_state.color_map = {p['name']: palette[i] for i, p in enumerate(prods)}

    with st.sidebar:
        st.image("https://sqm.eu/wp-content/uploads/2021/04/logo-sqm-white.png", width=150) # Opcjonalne logo
        st.title("Logistics Planner")
        v_name = st.selectbox("Wybierz środek transportu:", list(VEHICLES.keys()))
        veh = VEHICLES[v_name]
        
        st.divider()
        st.subheader("📦 Dodawanie towaru")
        sel_p_name = st.selectbox("Szukaj w bazie produktów:", [p['name'] for p in prods], index=None)
        qty = st.number_input("Liczba sztuk:", min_value=1, value=1)
        
        if st.button("Dodaj do listy", use_container_width=True) and sel_p_name:
            p_ref = next(p for p in prods if p['name'] == sel_p_name)
            ipc = p_ref.get('itemsPerCase', 1)
            num_units = math.ceil(qty / ipc)
            for i in range(num_units):
                c = p_ref.copy()
                # Obliczanie faktycznej zawartości w ostatniej jednostce
                remainder = qty % ipc
                c['actual_items'] = remainder if (i == num_units - 1 and remainder != 0) else ipc
                st.session_state.cargo.append(c)
            st.rerun()
            
        if st.button("Wyczyść wszystko", type="secondary", use_container_width=True):
            st.session_state.cargo = []
            st.rerun()

    # Ekran główny
    if st.session_state.cargo:
        st.header("📋 Zarządzanie wysyłką")
        
        # Przygotowanie danych do edytora (Agregacja)
        df_cargo = pd.DataFrame(st.session_state.cargo)
        if 'actual_items' not in df_cargo.columns:
            df_cargo['actual_items'] = 1
            
        sum_df = df_cargo.groupby('name').agg({'actual_items': 'sum'}).reset_index()
        
        edited_df = st.data_editor(
            sum_df, 
            hide_index=True, 
            use_container_width=True,
            column_config={
                "name": st.column_config.Column("Nazwa produktu", disabled=True),
                "actual_items": st.column_config.NumberColumn("Sztuk całkowicie", min_value=0)
            },
            key="main_editor"
        )

        # Reakcja na zmiany w edytorze
        if not edited_df.equals(sum_df):
            new_cargo = []
            for _, row in edited_df.iterrows():
                if row['actual_items'] > 0:
                    p_orig = next(p for p in prods if p['name'] == row['name'])
                    ipc = p_orig.get('itemsPerCase', 1)
                    num_u = math.ceil(row['actual_items'] / ipc)
                    for i in range(num_u):
                        u = p_orig.copy()
                        rem = row['actual_items'] % ipc
                        u['actual_items'] = rem if (i == num_u - 1 and rem != 0) else ipc
                        new_cargo.append(u)
            st.session_state.cargo = new_cargo
            st.rerun()

        # Obliczanie rozmieszczenia (Fleet Planning)
        rem_cargo = [dict(i) for i in st.session_state.cargo]
        fleet = []
        while rem_cargo:
            stacks, weight, not_p, m_l = pack_one_vehicle(rem_cargo, veh)
            if not stacks: break
            fleet.append({"stacks": stacks, "weight": weight, "ldm": m_l/100})
            rem_cargo = not_p

        st.divider()
        st.header(f"🚛 Plan transportu: {len(fleet)} pojazd(y)")

        for idx, truck in enumerate(fleet):
            with st.expander(f"Pojazd #{idx+1} ({v_name}) - Analiza", expanded=True):
                col_met, col_viz = st.columns([1, 3])
                
                with col_met:
                    st.metric("LDM (Metry bieżące)", f"{truck['ldm']:.2f}")
                    st.metric("Waga ładunku", f"{truck['weight']} kg")
                    floor_area = sum(s['width']*s['length'] for s in truck['stacks'])
                    st.metric("Zajęcie podłogi", f"{int(floor_area/(veh['L']*veh['W'])*100)}%")
                    
                    st.write("**Lista na tym aucie:**")
                    all_truck_items = [it for s in truck['stacks'] for it in s['items']]
                    truck_df = pd.DataFrame(all_truck_items)
                    if not truck_df.empty:
                        res_truck = truck_df.groupby('name').size().reset_index(name='Szt.')
                        st.table(res_truck)

                with col_viz:
                    st.plotly_chart(draw_3d(truck['stacks'], veh, st.session_state.color_map), use_container_width=True, key=f"v_{idx}")
    else:
        st.info("Lista towarów jest pusta. Użyj panelu bocznego, aby dodać przedmioty do planu.")
