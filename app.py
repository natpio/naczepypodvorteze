import streamlit as st
import json
import plotly.graph_objects as go
import math
import pandas as pd

# --- 1. KONFIGURACJA I STYLIZACJA PRO ---
st.set_page_config(
    page_title="SQM Logistics Planner Pro", 
    page_icon="🚛", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS dla wyglądu klasy Enterprise
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    .main { 
        background-color: #f8fafc; 
    }
    
    /* Stylizacja kart metryk */
    div[data-testid="stMetricValue"] {
        font-size: 24px;
        font-weight: 700;
        color: #1e293b;
    }
    
    /* Karty kontenerów */
    .st-emotion-cache-12w0u9p {
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 20px;
        background-color: white;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    
    /* Sidebar */
    .css-12pwv7q {
        background-color: #0f172a;
    }
    
    /* Przyciski */
    .stButton>button {
        border-radius: 8px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        transition: all 0.2s;
    }
    
    .stButton>button:hover {
        border-color: #3b82f6;
        color: #3b82f6;
    }
    
    /* Nagłówki */
    h1, h2, h3 {
        color: #0f172a;
        font-weight: 700;
    }
    
    /* Statusy */
    .status-card {
        padding: 10px;
        border-radius: 8px;
        border-left: 5px solid #3b82f6;
        background-color: #eff6ff;
        margin-bottom: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. LOGOWANIE (SECRETS) ---
def check_password():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    if not st.session_state.authenticated:
        st.container()
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown("<h1 style='text-align: center;'>🔐 SQM LOGISTICS</h1>", unsafe_allow_html=True)
            try:
                master_password = str(st.secrets["password"])
            except:
                st.error("Brak konfiguracji hasła (Secrets).")
                return False
            
            with st.form("Login"):
                pwd = st.text_input("Hasło dostępu:", type="password")
                if st.form_submit_button("Zaloguj do systemu", use_container_width=True):
                    if pwd == master_password:
                        st.session_state.authenticated = True
                        st.rerun()
                    else:
                        st.error("Nieautoryzowany dostęp.")
            return False
    return True

# --- 3. PARAMETRY POJAZDÓW ---
VEHICLES = {
    "BUS (Plandeka)": {"maxWeight": 1100, "L": 450, "W": 220, "H": 240, "color": "#f59e0b"},
    "Solo 6m": {"maxWeight": 3500, "L": 600, "W": 245, "H": 250, "color": "#3b82f6"},
    "Solo 7m": {"maxWeight": 7000, "L": 720, "W": 245, "H": 260, "color": "#10b981"},
    "Naczepa FTL": {"maxWeight": 24000, "L": 1360, "W": 248, "H": 275, "color": "#ef4444"}
}

COLOR_PALETTE = ["#6366f1", "#f43f5e", "#10b981", "#f59e0b", "#8b5cf6", "#06b6d4", "#ec4899"]

def load_products():
    try:
        with open('products.json', 'r', encoding='utf-8') as f:
            return sorted(json.load(f), key=lambda x: x.get('name', ''))
    except:
        return [
            {"name": "Paleta EPAL 1", "width": 80, "length": 120, "height": 140, "weight": 450, "canStack": True, "itemsPerCase": 1},
            {"name": "Flightcase Mix", "width": 60, "length": 80, "height": 85, "weight": 80, "canStack": True, "itemsPerCase": 1},
            {"name": "Skrzynia LED", "width": 120, "length": 100, "height": 110, "weight": 350, "canStack": False, "itemsPerCase": 1}
        ]

# --- 4. LOGIKA PAKOWANIA ---
def pack_one_vehicle(remaining_items, vehicle):
    placed_stacks = []
    not_placed = []
    current_weight = 0
    max_reached_l = 0
    
    items_to_pack = sorted(remaining_items, key=lambda x: (x['length'] * x['width']), reverse=True)

    shelf_x = 0      
    shelf_y = 0      
    shelf_max_w = 0  

    for item in items_to_pack:
        if current_weight + item['weight'] > vehicle['maxWeight']:
            not_placed.append(item)
            continue
            
        added = False
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

        w, l = item['width'], item['length']
        orientations = [(w, l), (l, w)]
        
        found_spot = False
        for fit_w, fit_l in orientations:
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

# --- 5. WIZUALIZACJA 3D PRO ---
def draw_3d(placed_stacks, vehicle, color_map):
    fig = go.Figure()
    v_l, v_w, v_h = vehicle['L'], vehicle['W'], vehicle['H']

    # Podłoga naczepy (ciemniejsza, bardziej techniczna)
    fig.add_trace(go.Mesh3d(
        x=[0, v_l, v_l, 0], y=[0, 0, v_w, v_w], z=[0, 0, 0, 0],
        color='#334155', opacity=0.8, name="Podłoga"
    ))
    
    # Obrys klatki (grubsze linie)
    edges = [
        ([0, v_l], [0, 0], [0, 0]), ([0, v_l], [v_w, v_w], [0, 0]), ([0, v_l], [0, 0], [v_h, v_h]), ([0, v_l], [v_w, v_w], [v_h, v_h]),
        ([0, 0], [0, v_w], [0, 0]), ([v_l, v_l], [0, v_w], [0, 0]), ([0, 0], [0, v_w], [v_h, v_h]), ([v_l, v_l], [0, v_w], [v_h, v_h]),
        ([0, 0], [0, 0], [0, v_h]), ([v_l, v_l], [0, 0], [0, v_h]), ([0, 0], [v_w, v_w], [0, v_h]), ([v_l, v_l], [v_w, v_w], [0, v_h])
    ]
    for ex, ey, ez in edges:
        fig.add_trace(go.Scatter3d(x=ex, y=ey, z=ez, mode='lines', line=dict(color='#94a3b8', width=2), hoverinfo='none'))

    # Ładunki
    for s in placed_stacks:
        for it in s['items']:
            x0, y0, z0 = s['x'], s['y'], it['z_pos']
            dx, dy, dz = it['width'], it['length'], it['height']
            
            fig.add_trace(go.Mesh3d(
                x=[x0, x0+dx, x0+dx, x0, x0, x0+dx, x0+dx, x0],
                y=[y0, y0, y0+dy, y0+dy, y0, y0, y0+dy, y0+dy],
                z=[z0, z0, z0, z0, z0+dz, z0+dz, z0+dz, z0+dz],
                i=[7,0,0,0,4,4,6,6,4,0,3,2], j=[3,4,1,2,5,6,5,2,0,1,6,3], k=[0,7,2,3,6,7,1,1,5,5,7,6],
                opacity=1.0, 
                color=color_map.get(it['name'], "#64748b"),
                flatshading=True,
                name=it['name']
            ))

    fig.update_layout(
        scene=dict(
            xaxis=dict(title='L (cm)', backgroundcolor="#f1f5f9", gridcolor="white"),
            yaxis=dict(title='W (cm)', backgroundcolor="#f1f5f9", gridcolor="white"),
            zaxis=dict(title='H (cm)', backgroundcolor="#f1f5f9", gridcolor="white"),
            aspectmode='manual', aspectratio=dict(x=v_l/v_w, y=1, z=v_h/v_w),
            camera=dict(eye=dict(x=1.5, y=1.5, z=1.2))
        ),
        margin=dict(l=0, r=0, b=0, t=0), 
        showlegend=False,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
    )
    return fig

# --- 6. APLIKACJA GŁÓWNA ---
if check_password():
    if 'cargo' not in st.session_state: st.session_state.cargo = []
    prods = load_products()
    
    if 'color_map' not in st.session_state:
        st.session_state.color_map = {p['name']: COLOR_PALETTE[i % len(COLOR_PALETTE)] for i, p in enumerate(prods)}

    with st.sidebar:
        st.image("https://img.icons8.com/fluency/96/truck.png", width=80)
        st.title("SQM Transport")
        
        with st.expander("🚚 Konfiguracja Pojazdu", expanded=True):
            v_name = st.selectbox("Typ taboru:", list(VEHICLES.keys()))
            veh = VEHICLES[v_name]
            st.caption(f"Max: {veh['maxWeight']}kg | {veh['L']}x{veh['W']}cm")

        st.subheader("📦 Dodaj jednostkę")
        sel_p_name = st.selectbox("Baza sprzętu:", [p['name'] for p in prods], index=None, placeholder="Wybierz produkt...")
        qty = st.number_input("Ilość (szt.):", min_value=1, value=1)
        
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            if st.button("➕ Dodaj", use_container_width=True) and sel_p_name:
                p_ref = next(p for p in prods if p['name'] == sel_p_name)
                ipc = p_ref.get('itemsPerCase', 1)
                num_units = math.ceil(qty / ipc)
                for i in range(num_units):
                    c = p_ref.copy()
                    remainder = qty % ipc
                    c['actual_items'] = remainder if (i == num_units - 1 and remainder != 0) else ipc
                    st.session_state.cargo.append(c)
                st.rerun()
        with col_btn2:
            if st.button("🗑️ Reset", use_container_width=True):
                st.session_state.cargo = []
                st.rerun()

    # WIDOK GŁÓWNY
    if st.session_state.cargo:
        st.subheader("📋 Manifest ładunkowy")
        
        df_cargo = pd.DataFrame(st.session_state.cargo)
        sum_df = df_cargo.groupby('name').agg({'actual_items': 'sum'}).reset_index()
        
        edited_df = st.data_editor(
            sum_df, 
            hide_index=True, 
            use_container_width=True,
            column_config={
                "name": st.column_config.Column("Produkt / Case", disabled=True),
                "actual_items": st.column_config.NumberColumn("Łączna ilość sztuk", min_value=0, step=1)
            },
            key="main_cargo_editor"
        )

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

        # SILNIK PAKOWANIA
        rem_cargo = [dict(i) for i in st.session_state.cargo]
        fleet_results = []
        
        while rem_cargo:
            stacks, weight, not_p, m_l = pack_one_vehicle(rem_cargo, veh)
            if not stacks: break
            fleet_results.append({"stacks": stacks, "weight": weight, "ldm": m_l/100})
            rem_cargo = not_p

        st.markdown(f"### 📊 Wynik planowania: **{len(fleet_results)} auto/a**")

        for idx, truck in enumerate(fleet_results):
            with st.container():
                st.markdown(f"""
                <div class='status-card'>
                    <strong>POJAZD #{idx+1}</strong> | {v_name} | LDM: {truck['ldm']:.2f}
                </div>
                """, unsafe_allow_html=True)
                
                all_items_in_truck = [it for s in truck['stacks'] for it in s['items']]
                vol_used = sum(it['width']*it['length']*it['height'] for it in all_items_in_truck) / 1000000
                vol_total = (veh['L']*veh['W']*veh['H']) / 1000000
                
                m1, m2, m3, m4 = st.columns(4)
                m1.metric("LDM", f"{truck['ldm']:.2f}")
                m2.metric("Waga", f"{truck['weight']} kg", f"{veh['maxWeight'] - truck['weight']} wolne", delta_color="normal")
                m3.metric("Objętość", f"{vol_used:.1f} m³")
                m4.metric("Wypełnienie", f"{int(vol_used/vol_total*100)}%")

                col_viz, col_tab = st.columns([2, 1])
                with col_viz:
                    st.plotly_chart(draw_3d(truck['stacks'], veh, st.session_state.color_map), use_container_width=True, key=f"plot_{idx}")
                
                with col_tab:
                    st.write("**Specyfikacja:**")
                    df_in = pd.DataFrame(all_items_in_truck)
                    res = df_in.groupby('name').agg({'actual_items': 'sum', 'name': 'count'}).rename(
                        columns={'actual_items':'Sztuk','name':'Case'}
                    )
                    st.dataframe(res.reset_index(), use_container_width=True, hide_index=True)
                    
                    st.caption("Obciążenie osi / DMC")
                    st.progress(min(truck['weight']/veh['maxWeight'], 1.0))
                st.divider()
        
        if rem_cargo:
            st.error(f"🚨 Uwaga: {len(rem_cargo)} elementów nie zmieściło się w zadanej flocie!")
    else:
        st.info("System gotowy. Dodaj produkty z bazy danych, aby rozpocząć planowanie załadunku.")
