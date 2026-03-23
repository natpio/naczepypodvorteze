import streamlit as st
import json
import plotly.graph_objects as go
import math
import pandas as pd

# --- 1. KONFIGURACJA I STYLIZACJA ---
st.set_page_config(page_title="SQM Logistics Planner PRO", layout="wide")

st.markdown("""
    <style>
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; border: 1px solid #e0e0e0; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    .unit-box { background-color: #e3f2fd; padding: 10px; border-radius: 5px; border-left: 5px solid #2196f3; margin: 10px 0; }
    footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# --- 2. DANE I PARAMETRY ---
VEHICLES = {
    "BUS (3.5t)": {"maxWeight": 1100, "L": 450, "W": 170, "H": 210},
    "Solo 6m": {"maxWeight": 3500, "L": 600, "W": 245, "H": 250},
    "Solo 7m": {"maxWeight": 7000, "L": 720, "W": 245, "H": 270},
    "TIR FTL": {"maxWeight": 24000, "L": 1360, "W": 248, "H": 270}
}

def load_products():
    try:
        with open('products.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            # Upewnienie się, że każdy produkt ma parametr itemsPerCase
            for p in data:
                if 'itemsPerCase' not in p or p['itemsPerCase'] < 1:
                    p['itemsPerCase'] = 1
            return sorted(data, key=lambda x: x.get('name', ''))
    except:
        return []

# --- 3. ALGORYTM PAKOWANIA (3D Bin Packing Logic) ---
def pack_items(cargo_list, vehicle):
    # Sortowanie: najpierw największa podstawa (L*W)
    sorted_items = sorted(cargo_list, key=lambda x: (x['length'] * x['width']), reverse=True)
    
    placed_stacks = []
    not_placed = []
    current_weight = 0
    
    # Prosty algorytm warstwowy (Shelf-based)
    curr_x, curr_y, row_max_width = 0, 0, 0
    
    for item in sorted_items:
        if current_weight + item['weight'] > vehicle['maxWeight']:
            not_placed.append(item)
            continue
            
        stacked = False
        # Próba piętrowania
        if item.get('canStack', True):
            for s in placed_stacks:
                # Sprawdź czy pasuje wymiarami (podstawa) i czy nie za wysoko
                if ((item['width'] <= s['w'] and item['length'] <= s['l']) or 
                    (item['length'] <= s['w'] and item['width'] <= s['l'])):
                    if s['curH'] + item['height'] <= vehicle['H']:
                        it_copy = item.copy()
                        it_copy['z'] = s['curH']
                        s['items'].append(it_copy)
                        s['curH'] += item['height']
                        current_weight += item['weight']
                        stacked = True
                        break
        
        if not stacked:
            # Próba postawienia na podłodze (z rotacją)
            w, l = item['width'], item['length']
            fit = False
            for fw, fl in [(w, l), (l, w)]:
                if curr_y + fl <= vehicle['W'] and curr_x + fw <= vehicle['L']:
                    it_copy = item.copy()
                    it_copy['z'] = 0
                    placed_stacks.append({'x': curr_x, 'y': curr_y, 'w': fw, 'l': fl, 'curH': item['height'], 'items': [it_copy]})
                    curr_y += fl
                    row_max_width = max(row_max_width, fw)
                    fit = True; break
                elif curr_x + row_max_width + fw <= vehicle['L'] and fl <= vehicle['W']:
                    curr_x += row_max_width
                    curr_y = 0
                    row_max_width = fw
                    it_copy = item.copy()
                    it_copy['z'] = 0
                    placed_stacks.append({'x': curr_x, 'y': curr_y, 'w': fw, 'l': fl, 'curH': item['height'], 'items': [it_copy]})
                    curr_y += fl
                    fit = True; break
            
            if fit:
                current_weight += item['weight']
            else:
                not_placed.append(item)
                
    ldm = (max([s['x'] + s['w'] for s in placed_stacks]) / 100) if placed_stacks else 0
    return placed_stacks, current_weight, not_placed, ldm

# --- 4. WIZUALIZACJA ---
def draw_3d(stacks, vehicle):
    fig = go.Figure()
    # Obrys auta
    fig.add_trace(go.Mesh3d(x=[0, vehicle['L'], vehicle['L'], 0], y=[0, 0, vehicle['W'], vehicle['W']], z=[0, 0, 0, 0], color='lightgray', opacity=0.2))
    
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b']
    
    for i, s in enumerate(stacks):
        color = colors[i % len(colors)]
        for it in s['items']:
            x, y, z = s['x'], s['y'], it['z']
            dx, dy, dz = (it['width'], it['length'], it['height']) if it['width'] == s['w'] else (it['length'], it['width'], it['height'])
            
            fig.add_trace(go.Mesh3d(
                x=[x, x+dx, x+dx, x, x, x+dx, x+dx, x],
                y=[y, y, y+dy, y+dy, y, y, y+dy, y+dy],
                z=[z, z, z, z, z+dz, z+dz, z+dz, z+dz],
                i=[7,0,0,0,4,4,6,6,4,0,3,2], j=[3,4,1,2,5,6,5,2,0,1,6,3], k=[0,7,2,3,6,7,1,1,5,5,7,6],
                color=color, opacity=0.7, name=it['name']
            ))
    fig.update_layout(scene=dict(aspectmode='data'), margin=dict(l=0,r=0,b=0,t=0))
    return fig

# --- 5. GŁÓWNY INTERFEJS ---
def main():
    st.header("🚛 SQM Logistics: Kalkulator Opakowań")
    
    if 'cargo' not in st.session_state: st.session_state.cargo = []
    all_prods = load_products()

    with st.sidebar:
        st.subheader("🛠️ Ustawienia transportu")
        v_type = st.selectbox("Pojazd:", list(VEHICLES.keys()))
        veh = VEHICLES[v_type]
        
        st.divider()
        st.subheader("📦 Dodaj produkt")
        p_name = st.selectbox("Wybierz z bazy:", [p['name'] for p in all_prods], index=None)
        
        if p_name:
            p_data = next(p for p in all_prods if p['name'] == p_name)
            ipc = p_data['itemsPerCase']
            
            st.markdown(f"""<div class="unit-box">
                <b>Standard pakowania:</b><br>
                1 opakowanie = {ipc} szt.
            </div>""", unsafe_allow_html=True)
            
            input_qty = st.number_input("Ile SZTUK chcesz wysłać?", min_value=1, value=ipc)
            
            # --- LOGIKA PRZELICZANIA ---
            num_cases = math.ceil(input_qty / ipc)
            st.info(f"To zajmie: **{num_cases}** opakowań")
            
            if st.button("Dodaj do listy załadunkowej", use_container_width=True, type="primary"):
                for i in range(num_cases):
                    case = p_data.copy()
                    # Ostatnie opakowanie może być niepełne, ale wymiary skrzyni są stałe
                    case['is_full'] = True if (i < num_cases - 1 or input_qty % ipc == 0) else False
                    case['contained_pieces'] = ipc if case['is_full'] else (input_qty % ipc)
                    st.session_state.cargo.append(case)
                st.rerun()

        if st.button("Wyczyść listę"):
            st.session_state.cargo = []; st.rerun()

    # --- WIDOK LISTY I WYNIKÓW ---
    if st.session_state.cargo:
        # Statystyki
        df = pd.DataFrame(st.session_state.cargo)
        total_pcs = df['contained_pieces'].sum()
        total_w = df['weight'].sum()
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Sztuk łącznie", f"{int(total_pcs)} szt.")
        col2.metric("Opakowań (Case)", len(st.session_state.cargo))
        col3.metric("Waga ładunku", f"{total_w} kg")

        # Pakowanie
        to_pack = [dict(i) for i in st.session_state.cargo]
        trucks = []
        while to_pack:
            stacks, w, remaining, ldm = pack_items(to_pack, veh)
            if not stacks: break
            trucks.append({"stacks": stacks, "weight": w, "ldm": ldm})
            to_pack = remaining

        st.subheader(f"📊 Wynik optymalizacji: {len(trucks)} pojazd(y)")
        
        for i, t in enumerate(trucks):
            with st.expander(f"🚛 Pojazd #{i+1} | Waga: {t['weight']}kg | LDM: {t['ldm']:.2f}", expanded=True):
                c_chart, c_list = st.columns([2, 1])
                with c_chart:
                    st.plotly_chart(draw_3d(t['stacks'], veh), use_container_width=True)
                with c_list:
                    st.write("**Lista pakunkowa:**")
                    # Zliczanie wystąpień dla tego konkretnego auta
                    items_in_truck = []
                    for s in t['stacks']:
                        for it in s['items']:
                            items_in_truck.append(it['name'])
                    st.dataframe(pd.Series(items_in_truck).value_counts(), column_config={"index": "Produkt", "0": "Opakowań"})
    else:
        st.info("Wybierz produkt i podaj liczbę sztuk w panelu bocznym, aby rozpocząć planowanie.")

if __name__ == "__main__":
    main()
