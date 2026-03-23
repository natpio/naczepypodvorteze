import streamlit as st
import json
import plotly.graph_objects as go
import math
import pandas as pd
import random

# --- KONFIGURACJA I STYLIZACJA ---
st.set_page_config(page_title="SQM Logistics Planner PRO", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #f1f3f6; }
    .stMetric { background-color: #ffffff; padding: 20px; border-radius: 12px; border: 1px solid #d1d9e6; box-shadow: 3px 3px 6px #c8d0e7, -3px -3px 6px #ffffff; }
    .unit-info { background: linear-gradient(135.deg, #1e3a8a, #3b82f6); color: white; padding: 15px; border-radius: 10px; margin: 10px 0; }
    .footer-note { font-size: 0.8rem; color: #64748b; margin-top: 50px; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

# --- KONFIGURACJA POJAZDÓW ---
VEHICLES = {
    "BUS (3.5t)": {"maxWeight": 1100, "L": 450, "W": 170, "H": 210, "color": "#475569"},
    "Solo 6m": {"maxWeight": 3500, "L": 600, "W": 245, "H": 250, "color": "#1e293b"},
    "Solo 7m": {"maxWeight": 7000, "L": 720, "W": 245, "H": 270, "color": "#0f172a"},
    "TIR FTL": {"maxWeight": 24000, "L": 1360, "W": 248, "H": 275, "color": "#000000"}
}

# --- FUNKCJE POMOCNICZE ---
def load_products():
    try:
        with open('products.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            for p in data:
                p.setdefault('itemsPerCase', 1)
                p.setdefault('canStack', True)
            return sorted(data, key=lambda x: x['name'])
    except Exception as e:
        st.error(f"Błąd bazy danych: {e}")
        return []

def get_product_color(name):
    random.seed(sum(ord(c) for c in name))
    return f'rgb({random.randint(50, 200)}, {random.randint(50, 200)}, {random.randint(50, 200)})'

# --- WIZUALIZACJA 3D (TRUCK MODEL) ---
def draw_truck_pro(fig, vehicle, stacks):
    v_l, v_w, v_h = vehicle['L'], vehicle['W'], vehicle['H']
    
    # 1. KABINA I RAMA (Stylizacja PRO)
    fig.add_trace(go.Mesh3d(
        x=[-90, 0, 0, -90, -90, 0, 0, -90],
        y=[0, 0, v_w, v_w, 0, 0, v_w, v_w],
        z=[0, 0, 0, 0, v_h*0.7, v_h*0.7, v_h*0.7, v_h*0.7],
        color=vehicle['color'], opacity=1, hoverinfo='skip'
    ))
    
    # 2. PAKA (Wireframe / Glass Box)
    fig.add_trace(go.Mesh3d(
        x=[0, v_l, v_l, 0, 0, v_l, v_l, 0],
        y=[0, 0, v_w, v_w, 0, 0, v_w, v_w],
        z=[0, 0, 0, 0, v_h, v_h, v_h, v_h],
        color='lightblue', opacity=0.05, hoverinfo='skip'
    ))

    # 3. ŁADUNEK
    for s in stacks:
        for it in s['items']:
            x, y, z = s['x'], s['y'], it['z']
            dx, dy, dz = (it['width'], it['length'], it['height']) if it['width'] == s['w'] else (it['length'], it['width'], it['height'])
            
            # Skrzynia
            fig.add_trace(go.Mesh3d(
                x=[x, x+dx, x+dx, x, x, x+dx, x+dx, x],
                y=[y, y, y+dy, y+dy, y, y, y+dy, y+dy],
                z=[z, z, z, z, z+dz, z+dz, z+dz, z+dz],
                i=[7,0,0,0,4,4,6,6,4,0,3,2], j=[3,4,1,2,5,6,5,2,0,1,6,3], k=[0,7,2,3,6,7,1,1,5,5,7,6],
                color=get_product_color(it['name']), opacity=0.9, name=it['name']
            ))
            # Krawędzie
            fig.add_trace(go.Scatter3d(
                x=[x, x+dx, x+dx, x, x, x, x+dx, x+dx, x, x, x+dx, x+dx, x+dx, x+dx, x, x],
                y=[y, y, y+dy, y+dy, y, y, y, y+dy, y+dy, y+dy, y+dy, y, y, y+dy, y+dy, y],
                z=[z, z, z, z, z, z+dz, z+dz, z, z, z+dz, z+dz, z+dz, z, z, z+dz, z+dz],
                mode='lines', line=dict(color='white', width=1.5), hoverinfo='skip'
            ))

    fig.update_layout(scene=dict(aspectmode='data', xaxis_visible=False, yaxis_visible=False, zaxis_visible=False),
                      margin=dict(l=0, r=0, b=0, t=0), showlegend=False)
    return fig

# --- LOGIKA PAKOWANIA ---
def pack_engine(cargo_list, vehicle):
    items = sorted(cargo_list, key=lambda x: (not x['canStack'], x['width']*x['length']), reverse=True)
    placed_stacks, not_placed = [], []
    curr_w, curr_x, curr_y, row_max_w = 0, 0, 0, 0
    
    for it in items:
        if curr_w + it['weight'] > vehicle['maxWeight']:
            not_placed.append(it)
            continue
            
        stacked = False
        if it['canStack']:
            for s in placed_stacks:
                if ((it['width'] <= s['w'] and it['length'] <= s['l']) or (it['length'] <= s['w'] and it['width'] <= s['l'])) and (s['curH'] + it['height'] <= vehicle['H']):
                    it_copy = it.copy(); it_copy['z'] = s['curH']
                    s['items'].append(it_copy); s['curH'] += it['height']
                    curr_w += it['weight']; stacked = True; break
        
        if not stacked:
            for w, l in [(it['width'], it['length']), (it['length'], it['width'])]:
                if curr_y + l <= vehicle['W'] and curr_x + w <= vehicle['L']:
                    it_copy = it.copy(); it_copy['z'] = 0
                    placed_stacks.append({'x': curr_x, 'y': curr_y, 'w': w, 'l': l, 'curH': it['height'], 'items': [it_copy]})
                    curr_y += l; row_max_w = max(row_max_w, w); curr_w += it['weight']; stacked = True; break
                elif curr_x + row_max_w + w <= vehicle['L'] and l <= vehicle['W']:
                    curr_x += row_max_w; curr_y = 0; row_max_w = w
                    it_copy = it.copy(); it_copy['z'] = 0
                    placed_stacks.append({'x': curr_x, 'y': curr_y, 'w': w, 'l': l, 'curH': it['height'], 'items': [it_copy]})
                    curr_y += l; curr_w += it['weight']; stacked = True; break
            if not stacked: not_placed.append(it)
                
    ldm = (max([s['x'] + s['w'] for s in placed_stacks]) / 100) if placed_stacks else 0
    return placed_stacks, curr_w, not_placed, ldm

# --- APLIKACJA ---
def main():
    st.title("🚛 SQM Logistics Planner Pro v2.0")
    
    if 'cargo' not in st.session_state: st.session_state.cargo = []
    all_p = load_products()

    # --- SIDEBAR ---
    with st.sidebar:
        st.header("⚙️ Ustawienia")
        v_name = st.selectbox("Typ pojazdu:", list(VEHICLES.keys()))
        veh = VEHICLES[v_name]
        
        st.divider()
        st.header("📦 Dodaj Towar")
        p_name = st.selectbox("Produkt:", [p['name'] for p in all_p], index=None)
        
        if p_name:
            p_ref = next(p for p in all_p if p['name'] == p_name)
            ipc = p_ref['itemsPerCase']
            st.markdown(f'<div class="unit-info"><b>Standard pakowania:</b><br>{ipc} szt. / opakowanie</div>', unsafe_allow_html=True)
            
            count = st.number_input("Ile SZTUK wysłać?", min_value=1, value=ipc)
            num_cases = math.ceil(count / ipc)
            
            if st.button("Dodaj do planu", use_container_width=True, type="primary"):
                for i in range(num_cases):
                    case = p_ref.copy()
                    case['pcs_in_this_case'] = ipc if (i < num_cases - 1 or count % ipc == 0) else (count % ipc)
                    st.session_state.cargo.append(case)
                st.rerun()

        if st.button("Wyczyść wszystko", use_container_width=True):
            st.session_state.cargo = []; st.rerun()

    # --- WIDOK GŁÓWNY ---
    if st.session_state.cargo:
        # Metryki zbiorcze
        total_pcs = sum(c['pcs_in_this_case'] for c in st.session_state.cargo)
        total_w = sum(c['weight'] for c in st.session_state.cargo)
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Opakowania", len(st.session_state.cargo))
        col2.metric("Łącznie Sztuk", f"{total_pcs} szt.")
        col3.metric("Waga ładunku", f"{total_w} kg")

        # Algorytm pakowania (wiele aut)
        to_pack = [dict(c) for c in st.session_state.cargo]
        fleet = []
        while to_pack:
            res_s, res_w, rem, ldm = pack_engine(to_pack, veh)
            if not res_s: break
            fleet.append({"stacks": res_s, "weight": res_w, "ldm": ldm})
            to_pack = rem

        st.subheader(f"Zapotrzebowanie transportowe: {len(fleet)} pojazd(y)")
        
        for i, truck in enumerate(fleet):
            with st.expander(f"🚛 Pojazd #{i+1} | Waga: {truck['weight']}kg | LDM: {truck['ldm']:.2f}", expanded=True):
                cv, cl = st.columns([2, 1])
                with cv:
                    st.plotly_chart(draw_truck_pro(go.Figure(), veh, truck['stacks']), use_container_width=True)
                with cl:
                    st.write("**Lista ładunkowa:**")
                    items_in = [it['name'] for s in truck['stacks'] for it in s['items']]
                    st.table(pd.Series(items_in).value_counts().reset_index().rename(columns={"index":"Produkt", "count":"Opakowań"}))
        
        st.markdown('<p class="footer-note">System SQM Logistics Planner | 2026 Pro Edition</p>', unsafe_allow_html=True)
    else:
        st.info("Twoja lista jest pusta. Wybierz produkt z panelu bocznego i podaj liczbę sztuk.")

if __name__ == "__main__":
    main()
