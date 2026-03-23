import streamlit as st
import json
import plotly.graph_objects as go
import math
import pandas as pd
import random

# --- 1. KONFIGURACJA I PREMIUM UI ---
st.set_page_config(page_title="SQM Logistics Planner PRO", layout="wide", initial_sidebar_state="expanded")

def apply_custom_style():
    st.markdown("""
        <style>
        [data-testid="stMetricValue"] { font-size: 1.8rem; color: #007bff; }
        .stPlotlyChart { border-radius: 15px; overflow: hidden; box-shadow: 0 4px 12px rgba(0,0,0,0.1); }
        .vehicle-card { 
            padding: 20px; border-radius: 15px; background: white; 
            border-left: 5px solid #007bff; margin-bottom: 20px; 
        }
        </style>
    """, unsafe_allow_html=True)

apply_custom_style()

# --- 2. LOGIKA BIZNESOWA I DANE ---
VEHICLES = {
    "BUS (3.5t)": {"maxWeight": 1100, "L": 450, "W": 170, "H": 210, "color": "#A0A0A0"},
    "Solo 6m": {"maxWeight": 3500, "L": 600, "W": 245, "H": 250, "color": "#505050"},
    "Solo 7m": {"maxWeight": 7000, "L": 720, "W": 245, "H": 270, "color": "#303030"},
    "TIR FTL": {"maxWeight": 24000, "L": 1360, "W": 248, "H": 270, "color": "#101010"}
}

def load_products():
    try:
        with open('products.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            return sorted(data, key=lambda x: x.get('name', ''))
    except Exception as e:
        st.error(f"Błąd bazy danych: {e}")
        return []

# --- 3. SILNIK OPTYMALIZACJI (Packing Engine) ---
def optimize_packing(items, vehicle):
    """
    Ulepszony algorytm First-Fit Decreasing z rotacją i sprawdzaniem stosowalności.
    """
    # Sortowanie: najpierw te, których nie można piętrować, potem wg pola podstawy
    items = sorted(items, key=lambda x: (not x.get('canStack', True), x['length'] * x['width']), reverse=True)
    
    placed_stacks = []
    not_placed = []
    total_weight = 0
    
    # Grid-based packing (prosty, ale czytelny dla logistyka)
    curr_x, curr_y, row_max_width = 0, 0, 0
    
    for it in items:
        if total_weight + it['weight'] > vehicle['maxWeight']:
            not_placed.append(it)
            continue
            
        fit_found = False
        
        # 1. Próba piętrowania na istniejących stosach
        if it.get('canStack', True):
            for s in placed_stacks:
                # Sprawdź wymiary (z rotacją 90st)
                can_fit_dims = (it['width'] <= s['w'] and it['length'] <= s['l']) or \
                               (it['length'] <= s['w'] and it['width'] <= s['l'])
                if can_fit_dims and (s['curH'] + it['height'] <= vehicle['H']):
                    it_copy = it.copy()
                    it_copy['z'] = s['curH']
                    s['items'].append(it_copy)
                    s['curH'] += it['height']
                    total_weight += it['weight']
                    fit_found = True
                    break
        
        if fit_found: continue

        # 2. Próba postawienia na podłodze (z rotacją)
        dims_to_try = [(it['width'], it['length']), (it['length'], it['width'])]
        for w, l in dims_to_try:
            if curr_y + l <= vehicle['W'] and curr_x + w <= vehicle['L']:
                # Miejsce w obecnym rzędzie
                it_copy = it.copy()
                it_copy['z'] = 0
                placed_stacks.append({'x': curr_x, 'y': curr_y, 'w': w, 'l': l, 'curH': it['height'], 'items': [it_copy]})
                curr_y += l
                row_max_width = max(row_max_width, w)
                total_weight += it['weight']
                fit_found = True
                break
            elif curr_x + row_max_width + w <= vehicle['L'] and l <= vehicle['W']:
                # Nowy rząd
                curr_x += row_max_width
                curr_y = 0
                row_max_width = w
                it_copy = it.copy()
                it_copy['z'] = 0
                placed_stacks.append({'x': curr_x, 'y': curr_y, 'w': w, 'l': l, 'curH': it['height'], 'items': [it_copy]})
                curr_y += l
                total_weight += it['weight']
                fit_found = True
                break
        
        if not fit_found:
            not_placed.append(it)

    # Oblicz LDM (Longest X / 100)
    ldm = max([s['x'] + s['w'] for s in placed_stacks]) / 100 if placed_stacks else 0
    return placed_stacks, total_weight, not_placed, ldm

# --- 4. WIZUALIZACJA 3D PRO ---
def create_3d_view(stacks, vehicle):
    fig = go.Figure()
    
    # Rysowanie obrysu paki
    fig.add_trace(go.Mesh3d(
        x=[0, vehicle['L'], vehicle['L'], 0, 0, vehicle['L'], vehicle['L'], 0],
        y=[0, 0, vehicle['W'], vehicle['W'], 0, 0, vehicle['W'], vehicle['W']],
        z=[0, 0, 0, 0, vehicle['H'], vehicle['H'], vehicle['H'], vehicle['H']],
        opacity=0.05, color='cyan', hoverinfo='skip'
    ))

    colors = ["#636EFA", "#EF553B", "#00CC96", "#AB63FA", "#FFA15A", "#19D3F3", "#FF6692", "#B6E880"]

    for i, s in enumerate(stacks):
        color = colors[i % len(colors)]
        for it in s['items']:
            x, y, z = s['x'], s['y'], it['z']
            dx, dy, dz = (it['width'], it['length'], it['height']) if it['width'] == s['w'] else (it['length'], it['width'], it['height'])
            
            # Box
            fig.add_trace(go.Mesh3d(
                x=[x, x+dx, x+dx, x, x, x+dx, x+dx, x],
                y=[y, y, y+dy, y+dy, y, y, y+dy, y+dy],
                z=[z, z, z, z, z+dz, z+dz, z+dz, z+dz],
                i=[7,0,0,0,4,4,6,6,4,0,3,2], j=[3,4,1,2,5,6,5,2,0,1,6,3], k=[0,7,2,3,6,7,1,1,5,5,7,6],
                color=color, opacity=0.8, name=it['name'],
                hovertemplate=f"<b>{it['name']}</b><br>Waga: {it['weight']}kg<br>Z: {z}cm<extra></extra>"
            ))
            # Krawędzie dla czytelności
            fig.add_trace(go.Scatter3d(
                x=[x, x+dx, x+dx, x, x, x, x+dx, x+dx, x, x, x+dx, x+dx, x+dx, x+dx, x, x],
                y=[y, y, y+dy, y+dy, y, y, y, y+dy, y+dy, y+dy, y+dy, y, y, y+dy, y+dy, y],
                z=[z, z, z, z, z, z+dz, z+dz, z, z, z+dz, z+dz, z+dz, z, z, z+dz, z+dz],
                mode='lines', line=dict(color='black', width=2), hoverinfo='skip'
            ))

    fig.update_layout(
        scene=dict(
            aspectmode='data',
            xaxis_title="Długość (cm)", yaxis_title="Szerokość (cm)", zaxis_title="Wysokość (cm)",
            camera=dict(eye=dict(x=1.5, y=1.5, z=1.2))
        ),
        margin=dict(l=0, r=0, b=0, t=0),
        showlegend=False
    )
    return fig

# --- 5. GŁÓWNY INTERFEJS ---
def main():
    st.title("📦 SQM Logistics Planner Pro")
    
    if 'cargo_list' not in st.session_state:
        st.session_state.cargo_list = []

    all_products = load_products()

    with st.sidebar:
        st.header("⚙️ Konfiguracja")
        v_name = st.selectbox("Wybierz pojazd:", list(VEHICLES.keys()))
        v_data = VEHICLES[v_name]
        
        st.info(f"Parametry: {v_data['L']}x{v_data['W']}x{v_data['H']} cm | Max: {v_data['maxWeight']} kg")
        
        st.divider()
        st.subheader("🚀 Dodaj ładunek")
        selected_p = st.selectbox("Produkt z bazy:", [p['name'] for p in all_products], index=None)
        qty = st.number_input("Ilość (sztuk):", min_value=1, value=1)
        
        if st.button("Dodaj do planu", use_container_width=True, type="primary"):
            if selected_p:
                p_info = next(p for p in all_products if p['name'] == selected_p)
                for _ in range(qty):
                    st.session_state.cargo_list.append(p_info.copy())
                st.toast(f"Dodano {qty}x {selected_p}")
            else:
                st.warning("Wybierz produkt!")

        if st.button("Wyczyść wszystko", use_container_width=True):
            st.session_state.cargo_list = []
            st.rerun()

    # --- WIDOK GŁÓWNY ---
    if not st.session_state.cargo_list:
        st.placeholder().visual_content = st.info("Twoja lista załadunkowa jest pusta. Dodaj produkty z panelu bocznego.")
        return

    # Statystyki ogólne
    c1, c2, c3, c4 = st.columns(4)
    total_qty = len(st.session_state.cargo_list)
    total_w = sum(i['weight'] for i in st.session_state.cargo_list)
    total_v = sum((i['width']*i['length']*i['height'])/1000000 for i in st.session_state.cargo_list)
    
    c1.metric("Sztuk łącznie", total_qty)
    c2.metric("Waga całkowita", f"{total_w} kg")
    c3.metric("Objętość", f"{total_v:.2f} m³")
    c4.metric("LDM (Suma)", f"{(total_w/v_data['maxWeight'])* (v_data['L']/100):.2f}")

    # Proces pakowania
    remaining = [dict(i) for i in st.session_state.cargo_list]
    fleet_results = []
    
    while remaining:
        stacks, weight, not_p, ldm = optimize_packing(remaining, v_data)
        if not stacks and remaining: 
            st.error("Niektóre przedmioty są za duże dla tego pojazdu!")
            break
        fleet_results.append({"stacks": stacks, "weight": weight, "ldm": ldm})
        remaining = not_p

    # Wyniki
    st.header(f"🚛 Plan Transportu: {len(fleet_results)} pojazd(y)")
    
    for idx, truck in enumerate(fleet_results):
        with st.container():
            st.markdown(f"""<div class="vehicle-card">
                <h3>Pojazd #{idx+1} ({v_name})</h3>
                Wypełnienie wagowe: <b>{ (truck['weight']/v_data['maxWeight'])*100:.1f}%</b> | 
                Zajęte LDM: <b>{truck['ldm']:.2f}</b>
            </div>""", unsafe_allow_html=True)
            
            col_chart, col_data = st.columns([2, 1])
            
            with col_chart:
                st.plotly_chart(create_3d_view(truck['stacks'], v_data), use_container_width=True)
            
            with col_data:
                st.subheader("Zawartość")
                # Agregacja do tabeli
                truck_items = []
                for s in truck['stacks']:
                    for it in s['items']:
                        truck_items.append(it['name'])
                
                summary_df = pd.Series(truck_items).value_counts().reset_index()
                summary_df.columns = ['Produkt', 'Sztuk']
                st.table(summary_df)

    # Export
    if st.button("Generuj Raport PDF (Symulacja)"):
        st.snow()
        st.success("Raport gotowy do pobrania (funkcja demo)")

if __name__ == "__main__":
    main()
