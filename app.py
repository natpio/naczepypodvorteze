import streamlit as st
import json
import plotly.graph_objects as go
import math
import pandas as pd
import random

# --- 1. KONFIGURACJA I STYLIZACJA ---
st.set_page_config(page_title="SQM Logistics Planner", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; border: 1px solid #e0e0e0; }
    footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# --- 2. LOGOWANIE ---
def check_password():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    if not st.session_state.authenticated:
        st.title("🔐 Logistics Terminal")
        try:
            master_password = str(st.secrets["password"])
        except:
            st.error("Brak klucza 'password' w systemie Secrets.")
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
    "FTL": {"maxWeight": 24000, "L": 1360, "W": 245, "H": 265}
}

# Funkcja generująca dużą paletę barw
def get_product_color(product_name, all_products):
    if 'color_map' not in st.session_state:
        random.seed(42) # Stałe kolory przy każdym odświeżeniu
        unique_prods = [p['name'] for p in all_products]
        colors = []
        for _ in range(len(unique_prods) + 50):
            colors.append(f'#{random.randint(50, 200):02x}{random.randint(50, 200):02x}{random.randint(50, 200):02x}')
        st.session_state.color_map = dict(zip(unique_prods, colors))
    return st.session_state.color_map.get(product_name, "#808080")

def load_products():
    try:
        with open('products.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            for p in data:
                if 'itemsPerCase' not in p: p['itemsPerCase'] = 1
            return sorted(data, key=lambda x: x.get('name', ''))
    except:
        return [{"name": "Błąd produktów", "width": 80, "length": 120, "height": 100, "weight": 10, "itemsPerCase": 1}]

# --- 4. LOGIKA PAKOWANIA ---
def pack_one_vehicle(remaining_items, vehicle):
    placed_stacks = []
    not_placed = []
    current_weight = 0
    max_l = 0
    
    # Sortowanie: najpierw największa podstawa
    items = sorted(remaining_items, key=lambda x: (x['length'] * x['width']), reverse=True)
    x, y, max_w_in_row = 0, 0, 0

    for it in items:
        if current_weight + it['weight'] > vehicle['maxWeight']:
            not_placed.append(it)
            continue
            
        stacked = False
        if it.get('canStack', True):
            for s in placed_stacks:
                match = (it['width'] == s['w'] and it['length'] == s['l']) or (it['width'] == s['l'] and it['length'] == s['w'])
                if match and (s['curH'] + it['height']) <= vehicle['H']:
                    copy_it = it.copy()
                    copy_it['z'] = s['curH']
                    copy_it['w_fit'], copy_it['l_fit'] = s['w'], s['l']
                    s['items'].append(copy_it)
                    s['curH'] += it['height']
                    current_weight += it['weight']
                    stacked = True
                    break
        
        if not stacked:
            # Próba postawienia na podłodze (w tym rotacja)
            w, l = it['width'], it['length']
            found = False
            for fit_w, fit_l in [(w, l), (l, w)]:
                if y + fit_l <= vehicle['W'] and x + fit_w <= vehicle['L']:
                    copy_it = it.copy()
                    copy_it['z'] = 0
                    copy_it['w_fit'], copy_it['l_fit'] = fit_w, fit_l
                    placed_stacks.append({'x': x, 'y': y, 'w': fit_w, 'l': fit_l, 'curH': it['height'], 'items': [copy_it]})
                    y += fit_l
                    max_w_in_row = max(max_w_in_row, fit_w)
                    found = True; break
                elif x + max_w_in_row + fit_w <= vehicle['L'] and fit_l <= vehicle['W']:
                    x += max_w_in_row
                    y, max_w_in_row = 0, fit_w
                    copy_it = it.copy()
                    copy_it['z'] = 0
                    copy_it['w_fit'], copy_it['l_fit'] = fit_w, fit_l
                    placed_stacks.append({'x': x, 'y': y, 'w': fit_w, 'l': fit_l, 'curH': it['height'], 'items': [copy_it]})
                    y += fit_l
                    found = True; break
            
            if found:
                current_weight += it['weight']
                max_l = max(max_l, x + max_w_in_row)
            else:
                not_placed.append(it)
                
    return placed_stacks, current_weight, not_placed, max_l / 100

# --- 5. WIZUALIZACJA 3D ---
def draw_3d(stacks, vehicle, prods):
    fig = go.Figure()
    v_l, v_w, v_h = vehicle['L'], vehicle['W'], vehicle['H']

    # Podłoga
    fig.add_trace(go.Mesh3d(x=[0, v_l, v_l, 0], y=[0, 0, v_w, v_w], z=[0, 0, 0, 0], color='gray', opacity=0.1, hoverinfo='skip'))
    
    for s in stacks:
        for it in s['items']:
            x0, y0, z0 = s['x'], s['y'], it['z']
            dx, dy, dz = it['w_fit'], it['l_fit'], it['height']
            
            label = f"<b>{it['name']}</b><br>Wymiary: {dx}x{dy}x{dz} cm<br>Waga: {it['weight']} kg"
            
            fig.add_trace(go.Mesh3d(
                x=[x0, x0+dx, x0+dx, x0, x0, x0+dx, x0+dx, x0],
                y=[y0, y0, y0+dy, y0+dy, y0, y0, y0+dy, y0+dy],
                z=[z0, z0, z0, z0, z0+dz, z0+dz, z0+dz, z0+dz],
                i=[7,0,0,0,4,4,6,6,4,0,3,2], j=[3,4,1,2,5,6,5,2,0,1,6,3], k=[0,7,2,3,6,7,1,1,5,5,7,6],
                color=get_product_color(it['name'], prods), opacity=0.9,
                hovertext=label, hoverinfo="text"
            ))

    fig.update_layout(scene=dict(xaxis_range=[0,v_l], yaxis_range=[0,v_w], zaxis_range=[0,v_h], aspectmode='data'),
                      margin=dict(l=0,r=0,b=0,t=0), showlegend=False)
    return fig

# --- 6. GŁÓWNA APLIKACJA ---
if check_password():
    if 'cargo' not in st.session_state: st.session_state.cargo = []
    all_p = load_products()

    with st.sidebar:
        st.header("🚛 Ustawienia")
        v_type = st.selectbox("Pojazd:", list(VEHICLES.keys()))
        veh = VEHICLES[v_type]
        
        st.divider()
        st.subheader("➕ Dodaj do listy")
        p_name = st.selectbox("Produkt:", [p['name'] for p in all_p], index=None)
        count = st.number_input("Sztuk:", min_value=1, value=1)
        
        if st.button("Dodaj", use_container_width=True) and p_name:
            ref = next(p for p in all_p if p['name'] == p_name)
            ipc = ref.get('itemsPerCase', 1)
            num_units = math.ceil(count / ipc)
            for i in range(num_units):
                c = ref.copy()
                rem = count % ipc
                c['actual_items'] = rem if (i == num_units-1 and rem != 0) else ipc
                st.session_state.cargo.append(c)
            st.rerun()

        if st.button("Wyczyść plan", type="secondary"):
            st.session_state.cargo = []; st.rerun()

    if st.session_state.cargo:
        st.header("📋 Edytowalna Lista Załadunkowa")
        
        # Agregacja danych do edytora
        df = pd.DataFrame(st.session_state.cargo)
        if 'actual_items' not in df.columns: df['actual_items'] = 1
        agg_df = df.groupby('name').agg({'actual_items': 'sum'}).reset_index()
        
        # --- EDYTOR LISTY ---
        edited = st.data_editor(
            agg_df, 
            use_container_width=True, 
            hide_index=True,
            column_config={"name": "Produkt (zablokowane)", "actual_items": "Sztuk Razem (Edytuj tutaj)"},
            disabled=["name"],
            key="list_editor"
        )

        # Synchronizacja edytora ze stanem sesji
        if not edited.equals(agg_df):
            new_cargo = []
            for _, row in edited.iterrows():
                if row['actual_items'] > 0:
                    orig = next(p for p in all_p if p['name'] == row['name'])
                    ipc = orig.get('itemsPerCase', 1)
                    units = math.ceil(row['actual_items'] / ipc)
                    for i in range(units):
                        u = orig.copy()
                        r = row['actual_items'] % ipc
                        u['actual_items'] = r if (i == units-1 and r != 0) else ipc
                        new_cargo.append(u)
            st.session_state.cargo = new_cargo
            st.rerun()

        # Pakowanie
        to_pack = [dict(i) for i in st.session_state.cargo]
        fleet = []
        while to_pack:
            res_stacks, res_w, not_p, ldm = pack_one_vehicle(to_pack, veh)
            if not res_stacks: break
            fleet.append({"stacks": res_stacks, "w": res_w, "ldm": ldm})
            to_pack = not_p

        st.divider()
        st.header(f"📊 Wynik: {len(fleet)} pojazd(y)")
        
        for idx, truck in enumerate(fleet):
            with st.expander(f"🚛 Pojazd #{idx+1} | Waga: {truck['w']}kg | LDM: {truck['ldm']:.2f}", expanded=True):
                st.plotly_chart(draw_3d(truck['stacks'], veh, all_p), use_container_width=True)
    else:
        st.info("Dodaj produkty z panelu bocznego, aby zobaczyć plan.")
