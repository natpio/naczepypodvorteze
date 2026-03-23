import streamlit as st
import json
import plotly.graph_objects as go
import math
import pandas as pd

# --- 1. KONFIGURACJA I STYLIZACJA ---
st.set_page_config(page_title="SQM Logistics Planner PRO", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; border: 1px solid #e0e0e0; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    .unit-box { background-color: #e3f2fd; padding: 12px; border-radius: 8px; border-left: 5px solid #1976d2; margin: 10px 0; font-size: 0.9rem; }
    footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# --- 2. PARAMETRY POJAZDÓW ---
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
                if 'itemsPerCase' not in p or p['itemsPerCase'] < 1: p['itemsPerCase'] = 1
            return sorted(data, key=lambda x: x.get('name', ''))
    except:
        return []

def get_pro_color(product_name):
    name = product_name.upper()
    if "LED" in name: return "#3498db" # Blue
    if "TRUSS" in name: return "#95a5a6" # Silver
    if "CASE" in name: return "#e67e22" # Orange
    if "SPEAKER" in name: return "#9b59b6" # Purple
    return "#2ecc71" # Green

# --- 3. WIZUALIZACJA PRO ---
def draw_truck_structure(fig, v_l, v_w, v_h, color):
    # KABINA
    cab_l = 80
    fig.add_trace(go.Mesh3d(
        x=[-cab_l, 0, 0, -cab_l, -cab_l, 0, 0, -cab_l],
        y=[0, 0, v_w, v_w, 0, 0, v_w, v_w],
        z=[0, 0, 0, 0, v_h*0.65, v_h*0.65, v_h*0.65, v_h*0.65],
        i=[7,0,0,0,4,4,6,6,4,0,3,2], j=[3,4,1,2,5,6,5,2,0,1,6,3], k=[0,7,2,3,6,7,1,1,5,5,7,6],
        color=color, opacity=1, hoverinfo='skip'
    ))
    # RAMA
    fig.add_trace(go.Mesh3d(
        x=[-cab_l, v_l, v_l, -cab_l], y=[0, 0, v_w, v_w], z=[-5, -5, -5, -5],
        color="#1a1a1a", opacity=1, hoverinfo='skip'
    ))
    # OBRYS PAKI (Wireframe)
    lx = [0, v_l, v_l, 0, 0, 0, v_l, v_l, v_l, v_l, 0, 0, 0, 0, v_l, v_l]
    ly = [0, 0, v_w, v_w, 0, 0, 0, 0, v_w, v_w, v_w, v_w, 0, v_w, v_w, 0]
    lz = [0, 0, 0, 0, 0, v_h, v_h, 0, 0, v_h, v_h, 0, v_h, v_h, v_h, v_h]
    fig.add_trace(go.Scatter3d(x=lx, y=ly, z=lz, mode='lines', line=dict(color='black', width=2), hoverinfo='skip'))

# --- 4. SILNIK PAKOWANIA ---
def pack_items(cargo, vehicle):
    items = sorted(cargo, key=lambda x: (x['length'] * x['width']), reverse=True)
    placed_stacks, not_placed = [], []
    curr_weight, curr_x, curr_y, row_max_w = 0, 0, 0, 0
    
    for it in items:
        if curr_weight + it['weight'] > vehicle['maxWeight']:
            not_placed.append(it)
            continue
            
        stacked = False
        if it.get('canStack', True):
            for s in placed_stacks:
                if ((it['width'] <= s['w'] and it['length'] <= s['l']) or 
                    (it['length'] <= s['w'] and it['width'] <= s['l'])):
                    if s['curH'] + it['height'] <= vehicle['H']:
                        it_c = it.copy(); it_c['z'] = s['curH']
                        s['items'].append(it_c); s['curH'] += it['height']
                        curr_weight += it['weight']; stacked = True; break
        
        if not stacked:
            for w, l in [(it['width'], it['length']), (it['length'], it['width'])]:
                if curr_y + l <= vehicle['W'] and curr_x + w <= vehicle['L']:
                    it_c = it.copy(); it_c['z'] = 0
                    placed_stacks.append({'x': curr_x, 'y': curr_y, 'w': w, 'l': l, 'curH': it['height'], 'items': [it_c]})
                    curr_y += l; row_max_w = max(row_max_w, w); curr_weight += it['weight']; stacked = True; break
                elif curr_x + row_max_w + w <= vehicle['L'] and l <= vehicle['W']:
                    curr_x += row_max_w; curr_y = 0; row_max_w = w
                    it_c = it.copy(); it_c['z'] = 0
                    placed_stacks.append({'x': curr_x, 'y': curr_y, 'w': w, 'l': l, 'curH': it['height'], 'items': [it_c]})
                    curr_y += l; curr_weight += it['weight']; stacked = True; break
            if not stacked: not_placed.append(it)
                
    ldm = (max([s['x'] + s['w'] for s in placed_stacks]) / 100) if placed_stacks else 0
    return placed_stacks, curr_weight, not_placed, ldm

# --- 5. MAIN APP ---
def main():
    st.title("📦 SQM Logistics Planner Pro")
    if 'cargo' not in st.session_state: st.session_state.cargo = []
    all_prods = load_products()

    with st.sidebar:
        st.header("🚛 Transport")
        v_name = st.selectbox("Pojazd:", list(VEHICLES.keys()))
        veh = VEHICLES[v_name]
        
        st.divider()
        st.header("📥 Ładunek")
        p_name = st.selectbox("Produkt:", [p['name'] for p in all_prods], index=None)
        
        if p_name:
            p_data = next(p for p in all_prods if p['name'] == p_name)
            ipc = p_data['itemsPerCase']
            st.markdown(f'<div class="unit-box">📦 <b>1 opakowanie = {ipc} szt.</b></div>', unsafe_allow_html=True)
            input_pcs = st.number_input("Liczba SZTUK:", min_value=1, value=ipc)
            num_cases = math.ceil(input_pcs / ipc)
            st.caption(f"Wygeneruje to {num_cases} opakowań zbiorczych.")
            
            if st.button("Dodaj do planu", use_container_width=True, type="primary"):
                for i in range(num_cases):
                    case = p_data.copy()
                    case['pcs'] = ipc if (i < num_cases-1 or input_pcs % ipc == 0) else (input_pcs % ipc)
                    st.session_state.cargo.append(case)
                st.rerun()

        if st.button("Wyczyść plan"): st.session_state.cargo = []; st.rerun()

    if st.session_state.cargo:
        # Statystyki
        total_w = sum(c['weight'] for c in st.session_state.cargo)
        c1, c2, c3 = st.columns(3)
        c1.metric("Opakowań", len(st.session_state.cargo))
        c2.metric("Sztuk Razem", sum(c['pcs'] for c in st.session_state.cargo))
        c3.metric("Waga Całkowita", f"{total_w} kg")

        # Pakowanie w pętlę (obsługa wielu aut)
        to_pack = [dict(c) for c in st.session_state.cargo]
        fleet = []
        while to_pack:
            res_s, res_w, rem, ldm = pack_items(to_pack, veh)
            if not res_s: break
            fleet.append({"stacks": res_s, "weight": res_w, "ldm": ldm})
            to_pack = rem

        st.subheader(f"Wynik: {len(fleet)} pojazd(y)")
        for idx, truck in enumerate(fleet):
            with st.expander(f"🚛 Pojazd #{idx+1} | Waga: {truck['weight']}kg | LDM: {truck['ldm']:.2f}", expanded=True):
                col_viz, col_list = st.columns([2, 1])
                with col_viz:
                    fig = go.Figure()
                    draw_truck_structure(fig, veh['L'], veh['W'], veh['H'], veh['color'])
                    for s in truck['stacks']:
                        for it in s['items']:
                            x, y, z = s['x'], s['y'], it['z']
                            dx, dy, dz = (it['width'], it['length'], it['height']) if it['width'] == s['w'] else (it['length'], it['width'], it['height'])
                            fig.add_trace(go.Mesh3d(
                                x=[x, x+dx, x+dx, x, x, x+dx, x+dx, x],
                                y=[y, y, y+dy, y+dy, y, y, y+dy, y+dy],
                                z=[z, z, z, z, z+dz, z+dz, z+dz, z+dz],
                                i=[7,0,0,0,4,4,6,6,4,0,3,2], j=[3,4,1,2,5,6,5,2,0,1,6,3], k=[0,7,2,3,6,7,1,1,5,5,7,6],
                                color=get_pro_color(it['name']), opacity=0.85, name=f"{it['name']} ({it['pcs']}szt)"
                            ))
                    fig.update_layout(scene=dict(aspectmode='data', xaxis_visible=False, yaxis_visible=False, zaxis_visible=False), margin=dict(l=0,r=0,b=0,t=0))
                    st.plotly_chart(fig, use_container_width=True)
                with col_list:
                    st.write("**Lista załadunkowa:**")
                    items_in = []
                    for s in truck['stacks']: 
                        for it in s['items']: items_in.append(it['name'])
                    st.table(pd.Series(items_in).value_counts().reset_index().rename(columns={"index":"Produkt", "count":"Opakowań"}))
    else:
        st.info("Dodaj produkty, aby zobaczyć wizualizację.")

if __name__ == "__main__":
    main()
