import streamlit as st
import json
import plotly.graph_objects as go
import math
import pandas as pd

# --- 1. KONFIGURACJA PREMIUM & DARK UI ---
st.set_page_config(
    page_title="SQM LOGISTICS | ULTRA-PRO", 
    page_icon="🏗️", 
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&family=Inter:wght@400;600;800&display=swap');
    
    :root {
        --bg-color: #0f172a;
        --card-bg: #1e293b;
        --accent: #3b82f6;
        --text-main: #f1f5f9;
    }

    .main { background-color: var(--bg-color); color: var(--text-main); }
    
    /* Dashboard Cards */
    [data-testid="stMetricValue"] {
        font-family: 'JetBrains Mono', monospace;
        font-size: 28px !important;
        color: #60a5fa !important;
    }
    
    .st-emotion-cache-12w0u9p {
        background-color: var(--card-bg) !important;
        border: 1px solid #334155 !important;
        border-radius: 16px !important;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }

    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #020617;
        border-right: 1px solid #1e293b;
    }

    /* Buttons */
    .stButton>button {
        width: 100%;
        border-radius: 10px;
        background-color: var(--accent);
        color: white;
        border: none;
        font-weight: 700;
        padding: 0.5rem;
        transition: all 0.3s ease;
    }
    
    .stButton>button:hover {
        background-color: #2563eb;
        transform: translateY(-2px);
        box-shadow: 0 10px 15px -3px rgba(59, 130, 246, 0.4);
    }

    h1, h2, h3 { font-family: 'Inter', sans-serif; font-weight: 800; color: white; }
    
    .status-badge {
        padding: 6px 12px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 600;
        background: rgba(59, 130, 246, 0.1);
        border: 1px solid var(--accent);
        color: var(--accent);
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. ZABEZPIECZENIA ---
def check_password():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    if not st.session_state.authenticated:
        col1, col2, col3 = st.columns([1, 1.5, 1])
        with col2:
            st.markdown("<div style='text-align: center; margin-top: 100px;'>", unsafe_allow_html=True)
            st.image("https://img.icons8.com/fluency/96/shield.png", width=60)
            st.title("SQM TERMINAL")
            try:
                master_password = str(st.secrets["password"])
            except:
                st.error("Błąd systemu: Brak zdefiniowanego hasła (Secrets).")
                return False
            
            with st.form("Login"):
                pwd = st.text_input("KOD DOSTĘPU", type="password")
                if st.form_submit_button("AUTORYZUJ"):
                    if pwd == master_password:
                        st.session_state.authenticated = True
                        st.rerun()
                    else:
                        st.error("BŁĄD AUTORYZACJI")
            st.markdown("</div>", unsafe_allow_html=True)
            return False
    return True

# --- 3. DANE I FLOTA ---
VEHICLES = {
    "Naczepa Standard (FTL)": {"maxWeight": 24000, "L": 1360, "W": 248, "H": 275},
    "Mega Trailer": {"maxWeight": 24000, "L": 1360, "W": 248, "H": 300},
    "Solo 7.2m": {"maxWeight": 7500, "L": 720, "W": 245, "H": 265},
    "Bus 10EP": {"maxWeight": 1100, "L": 485, "W": 220, "H": 230}
}

COLOR_PALETTE = ["#3b82f6", "#ef4444", "#10b981", "#f59e0b", "#8b5cf6", "#ec4899", "#06b6d4"]

def load_products():
    try:
        with open('products.json', 'r', encoding='utf-8') as f:
            return sorted(json.load(f), key=lambda x: x.get('name', ''))
    except:
        return [
            {"name": "Paleta EPAL", "width": 80, "length": 120, "height": 145, "weight": 500, "canStack": True},
            {"name": "Flightcase 120x60", "width": 60, "length": 120, "height": 90, "weight": 120, "canStack": True},
            {"name": "Screen Case LED", "width": 110, "length": 115, "height": 130, "weight": 420, "canStack": False}
        ]

# --- 4. ENGINE: PACKING ALGORITHM ---
def pack_engine(cargo_list, vehicle):
    placed_stacks = []
    not_placed = []
    current_weight = 0
    max_l = 0
    
    # Heurystyka: Najpierw ciężkie i o największej podstawie
    items = sorted(cargo_list, key=lambda x: (x['length'] * x['width'], x['weight']), reverse=True)
    
    x_cursor, y_cursor, row_max_w = 0, 0, 0

    for item in items:
        if current_weight + item['weight'] > vehicle['maxWeight']:
            not_placed.append(item)
            continue
            
        is_stacked = False
        if item.get('canStack', True):
            for s in placed_stacks:
                fits_dim = (item['width'] == s['width'] and item['length'] == s['length']) or \
                           (item['width'] == s['length'] and item['length'] == s['width'])
                if fits_dim and s['canStackBase'] and (s['currentH'] + item['height'] <= vehicle['H']):
                    it_c = item.copy()
                    it_c['z_pos'] = s['currentH']
                    it_c['w_active'], it_c['l_active'] = s['width'], s['length']
                    s['items'].append(it_c)
                    s['currentH'] += item['height']
                    current_weight += item['weight']
                    is_stacked = True
                    break
        
        if is_stacked: continue

        # Orientacja 2D
        found = False
        for w, l in [(item['width'], item['length']), (item['length'], item['width'])]:
            if y_cursor + l <= vehicle['W'] and x_cursor + w <= vehicle['L']:
                it_c = item.copy()
                it_c['z_pos'] = 0
                it_c['w_active'], it_c['l_active'] = w, l
                placed_stacks.append({
                    'x': x_cursor, 'y': y_cursor, 'width': w, 'length': l,
                    'currentH': item['height'], 'canStackBase': item.get('canStack', True),
                    'items': [it_c]
                })
                y_cursor += l
                row_max_w = max(row_max_w, w)
                found = True
                break
            elif x_cursor + row_max_w + w <= vehicle['L'] and l <= vehicle['W']:
                x_cursor += row_max_w
                y_cursor = 0
                row_max_w = w
                it_c = item.copy()
                it_c['z_pos'] = 0
                it_c['w_active'], it_c['l_active'] = w, l
                placed_stacks.append({
                    'x': x_cursor, 'y': y_cursor, 'width': w, 'length': l,
                    'currentH': item['height'], 'canStackBase': item.get('canStack', True),
                    'items': [it_c]
                })
                y_cursor += l
                found = True
                break

        if found:
            current_weight += item['weight']
            max_l = max(max_l, x_cursor + row_max_w)
        else:
            not_placed.append(item)

    return placed_stacks, current_weight, not_placed, max_l/100

# --- 5. VISUALIZATION: ULTRA-PRO 3D ---
def draw_ultra_3d(stacks, vehicle, color_map):
    fig = go.Figure()
    L, W, H = vehicle['L'], vehicle['W'], vehicle['H']

    # 1. Obrys Naczepy (Półprzezroczyste ściany)
    # Podłoga
    fig.add_trace(go.Mesh3d(
        x=[0, L, L, 0], y=[0, 0, W, W], z=[0, 0, 0, 0],
        color='#1e293b', opacity=0.8, hoverinfo='skip'
    ))
    # Ściana przednia
    fig.add_trace(go.Mesh3d(
        x=[0, 0, 0, 0], y=[0, W, W, 0], z=[0, 0, H, H],
        color='#334155', opacity=0.1, hoverinfo='skip'
    ))

    # 2. Rysowanie Skrzyń
    for s in stacks:
        for it in s['items']:
            x, y, z = s['x'], s['y'], it['z_pos']
            dx, dy, dz = it['w_active'], it['l_active'], it['height']
            color = color_map.get(it['name'], "#475569")

            # Bryła (Mesh)
            fig.add_trace(go.Mesh3d(
                x=[x, x+dx, x+dx, x, x, x+dx, x+dx, x],
                y=[y, y, y+dy, y+dy, y, y, y+dy, y+dy],
                z=[z, z, z, z, z+dz, z+dz, z+dz, z+dz],
                i=[7,0,0,0,4,4,6,6,4,0,3,2], j=[3,4,1,2,5,6,5,2,0,1,6,3], k=[0,7,2,3,6,7,1,1,5,5,7,6],
                opacity=0.9, color=color, flatshading=True, name=it['name'],
                customdata=[[it['name'], it['weight'], dx, dy, dz]],
                hovertemplate="<b>%{customdata[0]}</b><br>Wymiary: %{customdata[2]}x%{customdata[3]}x%{customdata[4]} cm<br>Waga: %{customdata[1]} kg<extra></extra>"
            ))

            # Kontury (High-Contrast Outlines)
            # Dół, góra i piony
            edges = [
                ([x, x+dx, x+dx, x, x], [y, y, y+dy, y+dy, y], [z, z, z, z, z]),
                ([x, x+dx, x+dx, x, x], [y, y, y+dy, y+dy, y], [z+dz, z+dz, z+dz, z+dz, z+dz]),
                ([x, x], [y, y], [z, z+dz]), ([x+dx, x+dx], [y, y], [z, z+dz]),
                ([x+dx, x+dx], [y+dy, y+dy], [z, z+dz]), ([x, x], [y+dy, y+dy], [z, z+dz])
            ]
            for ex, ey, ez in edges:
                fig.add_trace(go.Scatter3d(
                    x=ex, y=ey, z=ez, mode='lines', 
                    line=dict(color='rgba(0,0,0,0.5)', width=4), hoverinfo='skip', showlegend=False
                ))

    fig.update_layout(
        scene=dict(
            xaxis=dict(title='DŁUGOŚĆ (cm)', gridcolor='#334155', range=[0, L], backgroundcolor="#0f172a"),
            yaxis=dict(title='SZEROKOŚĆ (cm)', gridcolor='#334155', range=[0, W], backgroundcolor="#0f172a"),
            zaxis=dict(title='WYSOKOŚĆ (cm)', gridcolor='#334155', range=[0, H], backgroundcolor="#0f172a"),
            aspectmode='manual', aspectratio=dict(x=L/W*0.6, y=1, z=H/W*0.8),
            camera=dict(eye=dict(x=1.2, y=1.2, z=0.8))
        ),
        margin=dict(l=0, r=0, b=0, t=0),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
    )
    return fig

# --- 6. MAIN INTERFACE ---
if check_password():
    if 'cargo' not in st.session_state: st.session_state.cargo = []
    prods = load_products()
    
    if 'color_map' not in st.session_state:
        st.session_state.color_map = {p['name']: COLOR_PALETTE[i % len(COLOR_PALETTE)] for i, p in enumerate(prods)}

    # --- SIDEBAR: KONTROLA ---
    with st.sidebar:
        st.markdown("<h2 style='color: #60a5fa;'>SQM LOGISTICS</h2>", unsafe_allow_html=True)
        v_type = st.selectbox("TYP POJAZDU", list(VEHICLES.keys()))
        veh = VEHICLES[v_type]
        
        st.divider()
        st.subheader("📦 DODAJ ŁADUNEK")
        p_name = st.selectbox("SPRZĘT / CASE", [p['name'] for p in prods], index=None)
        p_qty = st.number_input("ILOŚĆ", min_value=1, value=1)
        
        c1, c2 = st.columns(2)
        with c1:
            if st.button("DODAJ") and p_name:
                base = next(p for p in prods if p['name'] == p_name)
                for _ in range(p_qty):
                    st.session_state.cargo.append(base.copy())
                st.rerun()
        with c2:
            if st.button("CZYŚĆ"):
                st.session_state.cargo = []
                st.rerun()

    # --- MAIN: DASHBOARD ---
    if st.session_state.cargo:
        # Podsumowanie listy
        with st.expander("📝 MANIFEST ZAŁADUNKOWY (KLIKNIJ ABY EDYTOWAĆ)"):
            df = pd.DataFrame(st.session_state.cargo)
            sum_df = df.groupby('name').size().reset_index(name='Ilość')
            st.dataframe(sum_df, use_container_width=True, hide_index=True)

        # Obliczenia
        rem_items = [dict(i) for i in st.session_state.cargo]
        trucks = []
        while rem_items:
            s, w, np, ldm = pack_engine(rem_items, veh)
            if not s: break
            trucks.append({"stacks": s, "weight": w, "ldm": ldm, "items_count": len([i for st in s for i in st['items']])})
            rem_items = np

        # Renderowanie floty
        for i, t in enumerate(trucks):
            st.markdown(f"### <span class='status-badge'>POJAZD #{i+1}</span> {v_type}", unsafe_allow_html=True)
            
            col_metrics, col_viz = st.columns([1, 3])
            
            with col_metrics:
                st.metric("ŁADUNEK (LDM)", f"{t['ldm']:.2f} m")
                st.metric("WAGA", f"{t['weight']} kg", f"{veh['maxWeight']-t['weight']} kg zapasu")
                st.write("**Wykorzystanie DMC:**")
                st.progress(min(t['weight']/veh['maxWeight'], 1.0))
                st.metric("SZTUK", t['items_count'])
                
            with col_viz:
                st.plotly_chart(draw_ultra_3d(t['stacks'], veh, st.session_state.color_map), use_container_width=True, key=f"v_{i}")
            
            st.divider()
            
        if rem_items:
            st.warning(f"🚨 POZA LIMITEM: {len(rem_items)} elementów nie zmieściło się w tej konfiguracji.")
    else:
        st.info("System operacyjny gotowy. Wybierz pojazd i dodaj sprzęt w panelu bocznym.")
