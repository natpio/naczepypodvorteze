import streamlit as st
import json
import plotly.graph_objects as go
import math
import pandas as pd

# --- 1. KONFIGURACJA I STYLIZACJA ---
st.set_page_config(
    page_title="SQM Logistics Terminal | Full Integration", 
    page_icon="🚛",
    layout="wide", 
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&family=Inter:wght@400;700&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    .main { background-color: #020617; color: #f1f5f9; }
    div[data-testid="stMetricValue"] {
        font-family: 'JetBrains Mono', monospace;
        color: #00f2ff !important;
        text-shadow: 0 0 10px rgba(0, 242, 255, 0.4);
    }
    .stButton>button {
        border-radius: 8px; font-weight: 700;
        background: linear-gradient(90deg, #3b82f6, #06b6d4);
        border: none; color: white; transition: 0.3s;
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
                else: st.error("Nieprawidłowe hasło.")
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
            for p in data:
                if 'itemsPerCase' not in p or p['itemsPerCase'] < 1:
                    p['itemsPerCase'] = 1
            return sorted(data, key=lambda x: x['name'])
    except Exception as e:
        st.error(f"Nie znaleziono pliku products.json: {e}")
        return []

# --- 4. KONWERSJA SZTUK NA JEDNOSTKI TRANSPORTOWE ---
def get_transport_units(manifest_list, all_prods):
    units = []
    for item in manifest_list:
        prod = next((p for p in all_prods if p['name'] == item['name']), None)
        if not prod: continue
        
        # Obliczamy ile jednostek (case/palet) potrzeba na tę liczbę sztuk
        num_units = math.ceil(item['qty'] / prod['itemsPerCase'])
        
        for _ in range(num_units):
            unit_copy = prod.copy()
            # Zachowujemy info o tym, z czego powstała jednostka
            units.append(unit_copy)
    return units

# --- 5. SILNIK PAKOWANIA (V4 - FIX BOUNDARIES) ---
@st.cache_data(show_spinner=False)
def get_packed_fleet(transport_units, vehicle):
    remaining = [dict(u) for u in transport_units]
    fleet = []
    
    while remaining:
        placed_stacks = []
        not_placed = []
        curr_weight = 0
        max_l = 0
        
        # Sortowanie: największa powierzchnia podłogi najpierw
        to_pack = sorted(remaining, key=lambda x: (x['length'] * x['width']), reverse=True)
        
        shelf_x, shelf_y, shelf_max_x = 0, 0, 0

        for unit in to_pack:
            if curr_weight + unit['weight'] > vehicle['maxWeight']:
                not_placed.append(unit); continue
                
            added = False
            # Próba piętrowania
            if unit.get('canStack', True):
                for s in placed_stacks:
                    if s['canStackBase'] and (unit['width'] == s['width'] and unit['length'] == s['length']) and (s['currentH'] + unit['height'] <= vehicle['H']):
                        u_c = unit.copy()
                        u_c['z_pos'] = s['currentH']
                        u_c['w_act'], u_c['l_act'] = s['width'], s['length']
                        s['items'].append(u_c)
                        s['currentH'] += unit['height']
                        curr_weight += unit['weight']; added = True; break
            
            if added: continue

            # Nowy stos na podłodze (z rotacją)
            best_fit = None
            for w, l in [(unit['width'], unit['length']), (unit['length'], unit['width'])]:
                if shelf_y + l <= vehicle['W'] and shelf_x + w <= vehicle['L']:
                    best_fit = (w, l, shelf_x, shelf_y); break
                elif shelf_x + shelf_max_x + w <= vehicle['L'] and l <= vehicle['W']:
                    best_fit = (w, l, shelf_x + shelf_max_x, 0); break

            if best_fit:
                fw, fl, px, py = best_fit
                if py == 0 and px > shelf_x: # Nowy rząd
                    shelf_x, shelf_y, shelf_max_x = px, 0, 0
                
                u_c = unit.copy()
                u_c['z_pos'] = 0
                u_c['w_act'], u_c['l_act'] = fw, fl
                
                placed_stacks.append({
                    'x': px, 'y': py, 'width': fw, 'length': fl, 
                    'currentH': unit['height'], 'canStackBase': unit.get('canStack', True), 'items': [u_c]
                })
                shelf_y = py + fl
                shelf_max_x = max(shelf_max_x, fw)
                curr_weight += unit['weight']
                max_l = max(max_l, px + fw)
                added = True
            else:
                not_placed.append(unit)
        
        if not placed_stacks: break
        fleet.append({"stacks": placed_stacks, "weight": curr_weight, "ldm": max_l/100})
        remaining = not_placed
                
    return fleet

# --- 6. WIZUALIZACJA 3D ---
def draw_3d_pro(stacks, vehicle, color_map):
    fig = go.Figure()
    L, W, H = vehicle['L'], vehicle['W'], vehicle['H']

    # Obrys naczepy
    fig.add_trace(go.Scatter3d(
        x=[0, L, L, 0, 0, None, 0, L, L, 0, 0, None, 0, 0, None, L, L, None, L, L, None, 0, 0],
        y=[0, 0, W, W, 0, None, 0, 0, W, W, 0, None, 0, 0, None, 0, 0, None, W, W, None, W, W],
        z=[0, 0, 0, 0, 0, None, H, H, H, H, H, None, 0, H, None, 0, H, None, 0, H, None, 0, H],
        mode='lines', line=dict(color='#00f2ff', width=2), hoverinfo='skip'
    ))

    edge_x, edge_y, edge_z = [], [], []
    for s in stacks:
        for it in s['items']:
            x, y, z = s['x'], s['y'], it['z_pos']
            dx, dy, dz = it.get('w_act', s['width']), it.get('l_act', s['length']), it['height']
            
            fig.add_trace(go.Mesh3d(
                x=[x, x+dx, x+dx, x, x, x+dx, x+dx, x], y=[y, y, y+dy, y+dy, y, y, y+dy, y+dy], z=[z, z, z, z, z+dz, z+dz, z+dz, z+dz],
                i=[7,0,0,0,4,4,6,6,4,0,3,2], j=[3,4,1,2,5,6,5,2,0,1,6,3], k=[0,7,2,3,6,7,1,1,5,5,7,6],
                opacity=0.8, color=color_map.get(it['name'], "#3b82f6"), flatshading=True, name=it['name']
            ))
            
            ex = [x, x+dx, x+dx, x, x, None, x, x+dx, x+dx, x, x, None, x, x, None, x+dx, x+dx, None, x+dx, x+dx, None, x, x]
            ey = [y, y, y+dy, y+dy, y, None, y, y, y+dy, y+dy, y, None, y, y, None, y, y, None, y+dy, y+dy, None, y+dy, y+dy]
            ez = [z, z, z, z, z, None, z+dz, z+dz, z+dz, z+dz, z+dz, None, z, z+dz, None, z, z+dz, None, z, z+dz, None, z, z+dz]
            edge_x.extend(ex); edge_y.extend(ey); edge_z.extend(ez); edge_x.append(None); edge_y.append(None); edge_z.append(None)

    fig.add_trace(go.Scatter3d(x=edge_x, y=edge_y, z=edge_z, mode='lines', line=dict(color='black', width=1.5), hoverinfo='skip'))
    fig.update_layout(scene=dict(aspectmode='manual', aspectratio=dict(x=L/W*0.6, y=1, z=H/W*0.6)), margin=dict(l=0, r=0, b=0, t=0), paper_bgcolor='rgba(0,0,0,0)', showlegend=False)
    return fig

# --- 7. INTERFEJS GŁÓWNY ---
if check_password():
    if 'manifest' not in st.session_state: st.session_state.manifest = []
    prods = load_products()
    
    if 'color_map' not in st.session_state:
        st.session_state.color_map = {p['name']: COLOR_PALETTE[i % len(COLOR_PALETTE)] for i, p in enumerate(prods)}

    with st.sidebar:
        st.markdown("<h2 style='color: #00f2ff;'>SQM LOGISTICS</h2>", unsafe_allow_html=True)
        v_type = st.selectbox("POJAZD:", list(VEHICLES.keys()))
        veh = VEHICLES[v_type]
        st.divider()
        
        sel_p = st.selectbox("SPRZĘT (Z BAZY):", [p['name'] for p in prods], index=None)
        p_qty = st.number_input("LICZBA SZTUK SPRZĘTU:", min_value=1, value=1)
        
        if st.button("DODAJ DO LISTY", use_container_width=True) and sel_p:
            existing = next((m for m in st.session_state.manifest if m['name'] == sel_p), None)
            if existing: existing['qty'] += p_qty
            else: st.session_state.manifest.append({'name': sel_p, 'qty': p_qty})
            st.rerun()
            
        if st.button("RESETUJ PLAN", use_container_width=True, type="secondary"):
            st.session_state.manifest = []; st.rerun()

    if st.session_state.manifest:
        st.markdown("<h3 style='color: #00f2ff;'>📋 MANIFEST I PRZELICZENIE JEDNOSTEK</h3>", unsafe_allow_html=True)
        
        # Tabela podsumowująca przeliczenie sztuk na case'y
        calc_list = []
        for m in st.session_state.manifest:
            p_ref = next(p for p in prods if p['name'] == m['name'])
            num_c = math.ceil(m['qty'] / p_ref['itemsPerCase'])
            calc_list.append({
                "Produkt": m['name'],
                "Sztuk sprzętu": m['qty'],
                "Pojemność case": p_ref['itemsPerCase'],
                "Jednostek (Case/Palet)": num_c
            })
        st.table(pd.DataFrame(calc_list))

        # Generowanie fizycznych jednostek i pakowanie
        transport_units = get_transport_units(st.session_state.manifest, prods)
        fleet = get_packed_fleet(transport_units, veh)
        
        for idx, truck in enumerate(fleet):
            st.markdown(f"#### AUTO #{idx+1} | {v_type}")
            c1, c2 = st.columns([2.5, 1])
            with c1:
                st.plotly_chart(draw_3d_pro(truck['stacks'], veh, st.session_state.color_map), use_container_width=True, key=f"f_{idx}")
            with c2:
                st.metric("LDM", f"{truck['ldm']:.2f} m")
                st.metric("WAGA", f"{truck['weight']} kg")
                st.progress(min(truck['weight']/veh['maxWeight'], 1.0))
                
                # Podsumowanie jednostek w tym konkretnym aucie
                units_in_truck = [it for s in truck['stacks'] for it in s['items']]
                sum_truck = pd.DataFrame(units_in_truck).groupby('name').size().reset_index(name='Liczba Case')
                st.dataframe(sum_truck, hide_index=True, use_container_width=True)
            st.divider()
    else:
        st.info("System gotowy. Wybierz sprzęt z bazy w panelu bocznym.")
