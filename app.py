import streamlit as st
import json
import plotly.graph_objects as go
import math
import pandas as pd

# --- 1. KONFIGURACJA I STYLIZACJA PREMIUM ---
st.set_page_config(
    page_title="SQM Logistics Terminal | Ultra-Pro", 
    layout="wide", 
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    .main { background-color: #0f172a; color: #f1f5f9; }
    .stMetric { background-color: #1e293b; padding: 15px; border-radius: 12px; border: 1px solid #334155; }
    [data-testid="stMetricValue"] { color: #3b82f6 !important; font-weight: 700; }
    .stButton>button { border-radius: 8px; font-weight: 700; text-transform: uppercase; transition: 0.3s; }
    .stButton>button:hover { box-shadow: 0 0 15px rgba(59, 130, 246, 0.4); }
    section[data-testid="stSidebar"] { background-color: #020617; border-right: 1px solid #1e293b; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. LOGOWANIE ---
def check_password():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    if not st.session_state.authenticated:
        col1, col2, col3 = st.columns([1, 1.5, 1])
        with col2:
            st.title("🔐 SQM LOGISTICS")
            try:
                master_password = str(st.secrets["password"])
            except:
                st.error("Błąd: Skonfiguruj hasło w Secrets.")
                return False
            pwd = st.text_input("Hasło dostępu:", type="password")
            if st.button("Zaloguj do systemu", use_container_width=True):
                if pwd == master_password:
                    st.session_state.authenticated = True
                    st.rerun()
                else:
                    st.error("Nieprawidłowe hasło.")
        return False
    return True

# --- 3. DANE POJAZDÓW ---
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
            {"name": "Skrzynia LED (Duża)", "width": 120, "length": 100, "height": 115, "weight": 380, "canStack": False, "itemsPerCase": 1}
        ]

# --- 4. LOGIKA PAKOWANIA ---
def pack_one_vehicle(remaining_items, vehicle):
    placed_stacks = []
    not_placed = []
    current_weight = 0
    max_reached_l = 0
    
    items_to_pack = sorted(remaining_items, key=lambda x: (x['length'] * x['width']), reverse=True)
    shelf_x, shelf_y, shelf_max_w = 0, 0, 0

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
        for fit_w, fit_l in [(w, l), (l, w)]:
            if shelf_y + fit_l <= vehicle['W'] and shelf_x + fit_w <= vehicle['L']:
                it_copy = item.copy()
                it_copy['z_pos'] = 0
                it_copy['width'], it_copy['length'] = fit_w, fit_l
                placed_stacks.append({'x': shelf_x, 'y': shelf_y, 'width': fit_w, 'length': fit_l, 'currentH': item['height'], 'canStackBase': item.get('canStack', True), 'items': [it_copy]})
                shelf_y += fit_l
                shelf_max_w = max(shelf_max_w, fit_w)
                added = True; break
            elif shelf_x + shelf_max_w + fit_w <= vehicle['L'] and fit_l <= vehicle['W']:
                shelf_x += shelf_max_w
                shelf_y, shelf_max_w = 0, fit_w
                it_copy = item.copy()
                it_copy['z_pos'] = 0
                it_copy['width'], it_copy['length'] = fit_w, fit_l
                placed_stacks.append({'x': shelf_x, 'y': shelf_y, 'width': fit_w, 'length': fit_l, 'currentH': item['height'], 'canStackBase': item.get('canStack', True), 'items': [it_copy]})
                shelf_y += fit_l
                added = True; break

        if added:
            current_weight += item['weight']
            max_reached_l = max(max_reached_l, shelf_x + shelf_max_w)
        else:
            not_placed.append(item)
                
    return placed_stacks, current_weight, not_placed, max_reached_l

# --- 5. WIZUALIZACJA ULTRA-PRO ---
def draw_3d_pro(placed_stacks, vehicle, color_map):
    fig = go.Figure()
    v_l, v_w, v_h = vehicle['L'], vehicle['W'], vehicle['H']

    # 1. Podłoga z siatką (Grid)
    fig.add_trace(go.Mesh3d(
        x=[0, v_l, v_l, 0], y=[0, 0, v_w, v_w], z=[0, 0, 0, 0],
        color='#1e293b', opacity=1.0, hoverinfo='skip'
    ))
    
    # 2. Ściany naczepy (Ghost Mode)
    # Ściana przednia (od strony kabiny)
    fig.add_trace(go.Mesh3d(
        x=[0, 0, 0, 0], y=[0, v_w, v_w, 0], z=[0, 0, v_h, v_h],
        color='#334155', opacity=0.15, hoverinfo='skip'
    ))
    # Ściana boczna lewa
    fig.add_trace(go.Mesh3d(
        x=[0, v_l, v_l, 0], y=[0, 0, 0, 0], z=[0, 0, v_h, v_h],
        color='#334155', opacity=0.05, hoverinfo='skip'
    ))

    # 3. Rysowanie skrzyń z indywidualnymi krawędziami
    for s in placed_stacks:
        for it in s['items']:
            x, y, z = s['x'], s['y'], it['z_pos']
            dx, dy, dz = it['width'], it['length'], it['height']
            color = color_map.get(it['name'], "#64748b")
            
            # Bryła (Mesh)
            fig.add_trace(go.Mesh3d(
                x=[x, x+dx, x+dx, x, x, x+dx, x+dx, x],
                y=[y, y, y+dy, y+dy, y, y, y+dy, y+dy],
                z=[z, z, z, z, z+dz, z+dz, z+dz, z+dz],
                i=[7,0,0,0,4,4,6,6,4,0,3,2], j=[3,4,1,2,5,6,5,2,0,1,6,3], k=[0,7,2,3,6,7,1,1,5,5,7,6],
                opacity=0.9, color=color, flatshading=True, name=it['name'],
                hovertemplate=f"<b>{it['name']}</b><br>Pos (X,Y,Z): {x},{y},{z}<br>Wymiary: {dx}x{dy}x{dz} cm<extra></extra>"
            ))
            
            # Krawędzie (High-Contrast Outlines)
            lines = [
                ([x, x+dx, x+dx, x, x], [y, y, y+dy, y+dy, y], [z, z, z, z, z]), # dół
                ([x, x+dx, x+dx, x, x], [y, y, y+dy, y+dy, y], [z+dz, z+dz, z+dz, z+dz, z+dz]), # góra
                ([x, x], [y, y], [z, z+dz]), ([x+dx, x+dx], [y, y], [z, z+dz]), # piony 1-2
                ([x+dx, x+dx], [y+dy, y+dy], [z, z+dz]), ([x, x], [y+dy, y+dy], [z, z+dz]) # piony 3-4
            ]
            for lx, ly, lz in lines:
                fig.add_trace(go.Scatter3d(
                    x=lx, y=ly, z=lz, mode='lines', 
                    line=dict(color='rgba(0,0,0,0.6)', width=4), hoverinfo='skip', showlegend=False
                ))

    fig.update_layout(
        scene=dict(
            xaxis=dict(title='DL (cm)', range=[0, v_l], gridcolor='#334155', backgroundcolor="#0f172a"),
            yaxis=dict(title='SZER (cm)', range=[0, v_w], gridcolor='#334155', backgroundcolor="#0f172a"),
            zaxis=dict(title='WYS (cm)', range=[0, v_h], gridcolor='#334155', backgroundcolor="#0f172a"),
            aspectmode='manual', aspectratio=dict(x=v_l/v_w*0.8, y=1, z=v_h/v_w*0.8),
            camera=dict(eye=dict(x=1.5, y=1.5, z=1.2))
        ),
        margin=dict(l=0, r=0, b=0, t=0), 
        paper_bgcolor='rgba(0,0,0,0)', 
        plot_bgcolor='rgba(0,0,0,0)'
    )
    return fig

# --- 6. GŁÓWNY INTERFEJS ---
if check_password():
    if 'cargo' not in st.session_state: st.session_state.cargo = []
    prods = load_products()
    if 'color_map' not in st.session_state:
        st.session_state.color_map = {p['name']: COLOR_PALETTE[i % len(COLOR_PALETTE)] for i, p in enumerate(prods)}

    with st.sidebar:
        st.title("🚛 SQM LOGISTICS")
        v_name = st.selectbox("TYP POJAZDU:", list(VEHICLES.keys()))
        veh = VEHICLES[v_name]
        
        st.divider()
        st.subheader("📦 DODAJ ŁADUNEK")
        sel_p_name = st.selectbox("SPRZĘT:", [p['name'] for p in prods], index=None)
        qty = st.number_input("ILOŚĆ:", min_value=1, value=1)
        
        if st.button("DODAJ DO PLANU", use_container_width=True) and sel_p_name:
            p_ref = next(p for p in prods if p['name'] == sel_p_name)
            ipc = p_ref.get('itemsPerCase', 1)
            num_units = math.ceil(qty / ipc)
            for i in range(num_units):
                c = p_ref.copy()
                remainder = qty % ipc
                c['actual_items'] = remainder if (i == num_units - 1 and remainder != 0) else ipc
                st.session_state.cargo.append(c)
            st.rerun()
            
        if st.button("RESETUJ PLAN", use_container_width=True, type="secondary"):
            st.session_state.cargo = []
            st.rerun()

    if st.session_state.cargo:
        st.header("📋 LISTA OPERACYJNA")
        df_cargo = pd.DataFrame(st.session_state.cargo)
        sum_df = df_cargo.groupby('name').agg({'actual_items': 'sum'}).reset_index()
        
        edited_df = st.data_editor(
            sum_df, hide_index=True, use_container_width=True,
            column_config={"name": "Produkt", "actual_items": st.column_config.NumberColumn("Sztuk", min_value=0)},
            key="pro_editor"
        )

        if not edited_df.equals(sum_df):
            new_cargo = []
            for _, row in edited_df.iterrows():
                if row['actual_items'] > 0:
                    p_orig = next((p for p in prods if p['name'] == row['name']), None)
                    if p_orig:
                        ipc = p_orig.get('itemsPerCase', 1)
                        num_u = math.ceil(row['actual_items'] / ipc)
                        for i in range(num_u):
                            unit = p_orig.copy()
                            rem = row['actual_items'] % ipc
                            unit['actual_items'] = rem if (i == num_u - 1 and rem != 0) else ipc
                            new_cargo.append(unit)
            st.session_state.cargo = new_cargo; st.rerun()

        rem_cargo = [dict(i) for i in st.session_state.cargo]
        fleet_results = []
        while rem_cargo:
            stacks, weight, not_p, ldm = pack_one_vehicle(rem_cargo, veh)
            if not stacks: break
            fleet_results.append({"stacks": stacks, "weight": weight, "ldm": ldm})
            rem_cargo = not_p

        for idx, truck in enumerate(fleet_results):
            with st.container():
                st.subheader(f"🚛 POJAZD #{idx+1} | LDM: {truck['ldm']:.2f}")
                col_viz, col_tab = st.columns([2.5, 1])
                with col_viz:
                    st.plotly_chart(draw_3d_pro(truck['stacks'], veh, st.session_state.color_map), use_container_width=True, key=f"v_{idx}")
                with col_tab:
                    st.metric("WAGA CAŁKOWITA", f"{truck['weight']} kg")
                    st.progress(min(truck['weight']/veh['maxWeight'], 1.0))
                    st.caption(f"Dopuszczalna: {veh['maxWeight']} kg")
                    all_it = [it for s in truck['stacks'] for it in s['items']]
                    st.dataframe(pd.DataFrame(all_it).groupby('name').size().reset_index(name='Case'), use_container_width=True, hide_index=True)
                st.divider()
    else:
        st.info("System gotowy. Dodaj sprzęt, aby wygenerować model załadunku.")
