import streamlit as st
import json
import plotly.graph_objects as go
import math
import pandas as pd
import random

# --- 1. KONFIGURACJA I STYLIZACJA ---
st.set_page_config(page_title="SQM Logistics Planner Pro", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; border: 1px solid #e0e0e0; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    .unit-box { background-color: #e3f2fd; padding: 12px; border-radius: 8px; border-left: 5px solid #1976d2; margin: 10px 0; font-size: 0.9rem; }
    footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# --- 2. DANE POJAZDÓW ---
VEHICLES = {
    "BUS (3.5t)": {"maxWeight": 1100, "L": 450, "W": 170, "H": 210, "color": "#34495e"},
    "Solo 6m": {"maxWeight": 3500, "L": 600, "W": 245, "H": 250, "color": "#2c3e50"},
    "Solo 7m": {"maxWeight": 7000, "L": 720, "W": 245, "H": 270, "color": "#1a252f"},
    "TIR FTL": {"maxWeight": 24000, "L": 1360, "W": 248, "H": 270, "color": "#000000"}
}

def load_products():
    try:
        with open('products.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            for p in data:
                p.setdefault('itemsPerCase', 1)
                p.setdefault('canStack', True)
            return sorted(data, key=lambda x: x.get('name', ''))
    except:
        return []

def get_product_color(name):
    random.seed(sum(ord(c) for c in name))
    return f'rgb({random.randint(50, 200)}, {random.randint(50, 200)}, {random.randint(50, 200)})'

# --- 3. ULEPSZONA WIZUALIZACJA 3D ---
def draw_truck_pro(vehicle, stacks):
    fig = go.Figure()
    v_l, v_w, v_h = vehicle['L'], vehicle['W'], vehicle['H']
    
    # Podłoga naczepy
    fig.add_trace(go.Mesh3d(
        x=[0, v_l, v_l, 0], y=[0, 0, v_w, v_w], z=[-2, -2, -2, -2],
        color='#2c3e50', opacity=1, hoverinfo='skip'
    ))

    # Przednia ściana
    fig.add_trace(go.Mesh3d(
        x=[0, 0, 0, 0], y=[0, v_w, v_w, 0], z=[0, 0, v_h, v_h],
        color='#34495e', opacity=0.2, hoverinfo='skip'
    ))
    
    # Szkielet naczepy (Krawędzie)
    lines = [
        ([0, v_l], [0, 0], [0, 0]), ([0, v_l], [v_w, v_w], [0, 0]),
        ([0, 0], [0, v_w], [0, 0]), ([v_l, v_l], [0, v_w], [0, 0]),
        ([0, 0], [0, 0], [0, v_h]), ([0, 0], [v_w, v_w], [0, v_h]),
        ([0, v_l], [0, 0], [v_h, v_h]), ([0, v_l], [v_w, v_w], [v_h, v_h])
    ]
    for x_c, y_c, z_c in lines:
        fig.add_trace(go.Scatter3d(x=x_c, y=y_c, z=z_c, mode='lines', line=dict(color='#7f8c8d', width=4), hoverinfo='skip'))

    # Kabina
    cab_size = 120
    fig.add_trace(go.Mesh3d(
        x=[-cab_size, 0, 0, -cab_size, -cab_size, 0, 0, -cab_size],
        y=[0, 0, v_w, v_w, 0, 0, v_w, v_w],
        z=[0, 0, 0, 0, v_h*0.8, v_h*0.8, v_h*0.8, v_h*0.8],
        color='#1a1a1a', opacity=1, hoverinfo='skip'
    ))

    # Ładunek
    for s in stacks:
        for it in s['items']:
            x, y, z = s['x'], s['y'], it['z']
            dx, dy, dz = (it['width'], it['length'], it['height']) if it['width'] == s['w'] else (it['length'], it['width'], it['height'])
            color = get_product_color(it['name'])
            
            fig.add_trace(go.Mesh3d(
                x=[x, x+dx, x+dx, x, x, x+dx, x+dx, x],
                y=[y, y, y+dy, y+dy, y, y, y+dy, y+dy],
                z=[z, z, z, z, z+dz, z+dz, z+dz, z+dz],
                i=[7,0,0,0,4,4,6,6,4,0,3,2], j=[3,4,1,2,5,6,5,2,0,1,6,3], k=[0,7,2,3,6,7,1,1,5,5,7,6],
                color=color, opacity=1, name=f"{it['name']} ({it.get('pcs_in_this_case', 1)}szt)"
            ))
            # Kontur paczki
            fig.add_trace(go.Scatter3d(
                x=[x, x+dx, x+dx, x, x, x, x+dx, x+dx, x, x, x+dx, x+dx, x+dx, x+dx, x, x],
                y=[y, y, y+dy, y+dy, y, y, y, y+dy, y+dy, y+dy, y+dy, y, y, y+dy, y+dy, y],
                z=[z, z, z, z, z, z+dz, z+dz, z, z, z+dz, z+dz, z+dz, z, z, z+dz, z+dz],
                mode='lines', line=dict(color='rgba(0,0,0,0.5)', width=2), hoverinfo='skip'
            ))

    fig.update_layout(
        scene=dict(aspectmode='data', xaxis_visible=False, yaxis_visible=False, zaxis_visible=False,
                   camera=dict(eye=dict(x=1.8, y=1.8, z=1.2))),
        margin=dict(l=0, r=0, b=0, t=0), showlegend=False
    )
    return fig

# --- 4. SILNIK PAKOWANIA ---
def pack_items(cargo, vehicle):
    items = sorted(cargo, key=lambda x: (not x.get('canStack', True), x['width'] * x['length']), reverse=True)
    placed_stacks, not_placed = [], []
    curr_w, curr_x, curr_y, row_max_w = 0, 0, 0, 0
    
    for it in items:
        if curr_w + it['weight'] > vehicle['maxWeight']:
            not_placed.append(it); continue
            
        stacked = False
        if it.get('canStack', True):
            for s in placed_stacks:
                if ((it['width'] <= s['w'] and it['length'] <= s['l']) or (it['length'] <= s['w'] and it['width'] <= s['l'])):
                    if s['curH'] + it['height'] <= vehicle['H']:
                        it_c = it.copy(); it_c['z'] = s['curH']
                        s['items'].append(it_c); s['curH'] += it['height']
                        curr_w += it['weight']; stacked = True; break
        
        if not stacked:
            for w, l in [(it['width'], it['length']), (it['length'], it['width'])]:
                if curr_y + l <= vehicle['W'] and curr_x + w <= vehicle['L']:
                    it_c = it.copy(); it_c['z'] = 0
                    placed_stacks.append({'x': curr_x, 'y': curr_y, 'w': w, 'l': l, 'curH': it['height'], 'items': [it_c]})
                    curr_y += l; row_max_w = max(row_max_w, w); curr_w += it['weight']; stacked = True; break
                elif curr_x + row_max_w + w <= vehicle['L'] and l <= vehicle['W']:
                    curr_x += row_max_w; curr_y = 0; row_max_w = w
                    it_c = it.copy(); it_c['z'] = 0
                    placed_stacks.append({'x': curr_x, 'y': curr_y, 'w': w, 'l': l, 'curH': it['height'], 'items': [it_c]})
                    curr_y += l; curr_w += it['weight']; stacked = True; break
            if not stacked: not_placed.append(it)
                
    ldm = (max([s['x'] + s['w'] for s in placed_stacks]) / 100) if placed_stacks else 0
    return placed_stacks, curr_w, not_placed, ldm

# --- 5. APLIKACJA ---
def main():
    st.title("🚛 SQM Logistics Planner Pro v2.1")
    if 'cargo' not in st.session_state: st.session_state.cargo = []
    all_p = load_products()

    with st.sidebar:
        st.header("⚙️ Ustawienia")
        v_name = st.selectbox("Pojazd:", list(VEHICLES.keys()))
        veh = VEHICLES[v_name]
        
        st.divider()
        p_name = st.selectbox("Produkt:", [p['name'] for p in all_p], index=None)
        if p_name:
            p_ref = next(p for p in all_p if p['name'] == p_name)
            ipc = p_ref.get('itemsPerCase', 1)
            st.markdown(f'<div class="unit-box">📦 <b>1 opakowanie = {ipc} szt.</b></div>', unsafe_allow_html=True)
            count = st.number_input("Ile SZTUK wysłać?", min_value=1, value=ipc)
            num_cases = math.ceil(count / ipc)
            if st.button("Dodaj do planu", use_container_width=True, type="primary"):
                for i in range(num_cases):
                    case = p_ref.copy()
                    case['pcs_in_this_case'] = ipc if (i < num_cases - 1 or count % ipc == 0) else (count % ipc)
                    st.session_state.cargo.append(case)
                st.rerun()
        if st.button("Wyczyść wszystko", use_container_width=True): st.session_state.cargo = []; st.rerun()

    if st.session_state.cargo:
        # Statystyki z poprawką KeyError
        total_pcs = sum(int(c.get('pcs_in_this_case', c.get('itemsPerCase', 1))) for c in st.session_state.cargo)
        total_w = sum(float(c.get('weight', 0)) for c in st.session_state.cargo)
        
        c1, c2, c3 = st.columns(3)
        c1.metric("Opakowania", len(st.session_state.cargo))
        c2.metric("Łącznie Sztuk", f"{total_pcs} szt.")
        c3.metric("Waga ładunku", f"{total_w} kg")

        to_pack = [dict(c) for c in st.session_state.cargo]
        fleet = []
        while to_pack:
            res_s, res_w, rem, ldm = pack_items(to_pack, veh)
            if not res_s: break
            fleet.append({"stacks": res_s, "weight": res_w, "ldm": ldm})
            to_pack = rem

        st.subheader(f"Zapotrzebowanie transportowe: {len(fleet)} pojazd(y)")
        for idx, truck in enumerate(fleet):
            with st.expander(f"🚛 Pojazd #{idx+1} | Waga: {truck['weight']}kg | LDM: {truck['ldm']:.2f}", expanded=True):
                cv, cl = st.columns([2, 1])
                with cv: st.plotly_chart(draw_truck_pro(veh, truck['stacks']), use_container_width=True)
                with cl:
                    st.write("**Lista ładunkowa:**")
                    items_in = [it['name'] for s in truck['stacks'] for it in s['items']]
                    st.table(pd.Series(items_in).value_counts().reset_index().rename(columns={"index":"Produkt", "count":"Opakowań"}))
    else:
        st.info("Dodaj produkty, aby rozpocząć planowanie.")

if __name__ == "__main__":
    main()
