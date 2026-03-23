import streamlit as st
import json
import plotly.graph_objects as go
import math
import pandas as pd
import random
import base64

# =========================================================
# 1. SYSTEMOWA KONFIGURACJA I ZABEZPIECZENIA
# =========================================================
# Wymuszenie otwartego sidebaru na mobile i szerokiego układu
st.set_page_config(
    page_title="VORTEZA FLOW PRO | ENTERPRISE",
    layout="wide",
    initial_sidebar_state="expanded"
)

def check_vorteza_auth():
    """Autoryzacja Single-Key na podstawie Secrets."""
    if "v_auth" not in st.session_state:
        st.session_state.v_auth = False

    if not st.session_state.v_auth:
        try:
            # Pobieranie hasła z Streamlit Secrets
            master_pwd = str(st.secrets.get("password", "vorteza2026"))
        except Exception:
            st.error("KRYTYCZNY BŁĄD: System nie może odnaleźć klucza w Secrets.")
            return False

        c1, c2, c3 = st.columns([0.1, 0.8, 0.1])
        with c2:
            st.markdown("<br><br><br>", unsafe_allow_html=True)
            with st.form("VortezaEnterpriseLogin"):
                st.markdown("<h2 style='text-align:center; color:#B58863;'>VORTEZA SYSTEMS</h2>", unsafe_allow_html=True)
                st.markdown("<p style='text-align:center; font-size:0.8rem; color:#666;'>SECURITY CLEARANCE REQUIRED</p>", unsafe_allow_html=True)
                input_pwd = st.text_input("ACCESS KEY", type="password", placeholder="Wprowadź klucz")
                if st.form_submit_button("AUTORYZUJ WEJŚCIE"):
                    if input_pwd == master_pwd:
                        st.session_state.v_auth = True
                        st.rerun()
                    else:
                        st.error("ODMOWA DOSTĘPU: Klucz nieprawidłowy.")
        return False
    return True

# Baza Floty
VEHICLES = {
    "TIR FTL (Standard)": {"maxW": 24000, "L": 1360, "W": 248, "H": 275, "ldm": 13.6},
    "Solo 7m (Heavy)": {"maxW": 7000, "L": 720, "W": 245, "H": 270, "ldm": 7.2},
    "Solo 6m (Medium)": {"maxW": 3500, "L": 600, "W": 245, "H": 250, "ldm": 6.0},
    "BUS (Express)": {"maxW": 1100, "L": 450, "W": 175, "H": 210, "ldm": 4.5}
}

# =========================================================
# 2. VORTEZA DESIGN SYSTEM (PREMIUM CSS)
# =========================================================
def apply_vorteza_theme():
    st.markdown("""
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;700&family=JetBrains+Mono:wght@300&display=swap');
            
            :root {
                --v-copper: #B58863;
                --v-dark: #0A0A0A;
                --v-panel: rgba(18, 18, 18, 0.98);
                --v-text: #E0E0E0;
            }

            .stApp { background-color: var(--v-dark); color: var(--v-text); font-family: 'Montserrat', sans-serif; }
            h1, h2, h3 { color: var(--v-copper) !important; text-transform: uppercase; letter-spacing: 3px !important; font-weight: 700 !important; }

            .vorteza-card {
                background: var(--v-panel); padding: 2rem; border-radius: 2px;
                border-left: 4px solid var(--v-copper); box-shadow: 20px 20px 60px rgba(0,0,0,0.6);
                margin-bottom: 1.5rem; backdrop-filter: blur(10px);
            }

            [data-testid="stMetricValue"] { color: var(--v-copper) !important; font-family: 'JetBrains Mono', monospace !important; font-size: 2.2rem !important; }
            
            [data-testid="stSidebar"] { background-color: #0F0F0F !important; border-right: 1px solid #222; }
            
            .stButton > button {
                background: transparent; color: var(--v-copper); border: 1px solid var(--v-copper);
                border-radius: 0px; padding: 0.8rem 2rem; text-transform: uppercase; letter-spacing: 2px;
                transition: 0.4s; width: 100%; font-weight: 700;
            }
            .stButton > button:hover { background: var(--v-copper); color: black; box-shadow: 0 0 20px rgba(181, 136, 99, 0.4); }

            .v-table { width: 100%; border-collapse: collapse; margin: 15px 0; }
            .v-table th { color: var(--v-copper); text-align: left; font-size: 0.65rem; text-transform: uppercase; border-bottom: 1px solid #333; padding: 12px; }
            .v-table td { padding: 12px; border-bottom: 1px solid #1a1a1a; font-size: 0.85rem; color: #BBB; }
        </style>
    """, unsafe_allow_html=True)

# =========================================================
# 3. SILNIK WIZUALIZACJI 3D (CAD-STYLE)
# =========================================================
def render_3d_engine(veh, stacks):
    fig = go.Figure()
    L, W, H = veh['L'], veh['W'], veh['H']

    # Konstrukcja Pojazdu
    fig.add_trace(go.Mesh3d(x=[0, L, L, 0], y=[0, 0, W, W], z=[-2, -2, -2, -2], color='#111', opacity=1, hoverinfo='skip'))
    fig.add_trace(go.Mesh3d(x=[-130, 0, 0, -130, -130, 0, 0, -130], y=[0, 0, W, W, 0, 0, W, W], z=[0, 0, 0, 0, H*0.75, H*0.75, H*0.75, H*0.75], color='#050505', opacity=1))

    # Szkielet Paki
    edges = [([0, L], [0, 0], [0, 0]), ([0, L], [W, W], [0, 0]), ([0, 0], [0, W], [0, 0]), ([L, L], [0, W], [0, 0]),
             ([0, 0], [0, 0], [0, H]), ([0, 0], [W, W], [0, H]), ([0, L], [0, 0], [H, H]), ([0, L], [W, W], [H, H])]
    for xe, ye, ze in edges:
        fig.add_trace(go.Scatter3d(x=xe, y=ye, z=ze, mode='lines', line=dict(color='#B58863', width=3), hoverinfo='skip'))

    # Render Ładunku
    for s_idx, stack in enumerate(stacks):
        shade = max(50, 181 - (s_idx % 8) * 15)
        c_color = f'rgb({shade}, {int(shade*0.75)}, {int(shade*0.55)})'
        for it in stack['items']:
            x, y, z = stack['x'], stack['y'], it['z']
            dx, dy, dz = it['w_fit'], it['l_fit'], it['height']
            fig.add_trace(go.Mesh3d(x=[x,x+dx,x+dx,x,x,x+dx,x+dx,x], y=[y,y,y+dy,y+dy,y,y,y+dy,y+dy], z=[z,z,z,z,z+dz,z+dz,z+dz,z+dz],
                                   i=[7,0,0,0,4,4,6,6,4,0,3,2], j=[3,4,1,2,5,6,5,2,0,1,6,3], k=[0,7,2,3,6,7,1,1,5,5,7,6], color=c_color, opacity=0.95))
            fig.add_trace(go.Scatter3d(x=[x,x+dx,x+dx,x,x,x,x+dx,x+dx,x,x,x+dx,x+dx,x+dx,x+dx,x,x], y=[y,y,y+dy,y+dy,y,y,y,y+dy,y+dy,y+dy,y+dy,y,y,y+dy,y+dy,y],
                                     z=[z,z,z,z,z,z+dz,z+dz,z,z,z+dz,z+dz,z+dz,z,z,z+dz,z+dz], mode='lines', line=dict(color='black', width=1.5), hoverinfo='skip'))

    fig.update_layout(scene=dict(aspectmode='data', xaxis_visible=False, yaxis_visible=False, zaxis_visible=False, camera=dict(eye=dict(x=1.7, y=1.7, z=1.1))),
                      paper_bgcolor='rgba(0,0,0,0)', margin=dict(l=0,r=0,b=0,t=0), showlegend=False)
    return fig

# =========================================================
# 4. LOGIKA PAKOWANIA (V-ENGINE 4.0)
# =========================================================
def packing_engine(cargo, veh):
    sorted_it = sorted(cargo, key=lambda x: (not x.get('canStack', True), x['width']*x['length']), reverse=True)
    stacks, failed, w_sum, cx, cy, row_w = [], [], 0, 0, 0, 0
    for it in sorted_it:
        if w_sum + it['weight'] > veh['maxW']: failed.append(it); continue
        stacked = False
        if it.get('canStack', True):
            for s in stacks:
                if ((it['width']<=s['w'] and it['length']<=s['l']) or (it['length']<=s['w'] and it['width']<=s['l'])) and (s['curH']+it['height'] <= veh['H']):
                    it_c = it.copy(); it_c['z']=s['curH']; it_c['w_fit'], it_c['l_fit']=s['w'], s['l']; s['items'].append(it_c); s['curH']+=it['height']; w_sum+=it['weight']; stacked=True; break
        if not stacked:
            for fw, fl in [(it['width'], it['length']), (it['length'], it['width'])]:
                if cy+fl <= veh['W'] and cx+fw <= veh['L']:
                    it_c = it.copy(); it_c['z']=0; it_c['w_fit'], it_c['l_fit']=fw, fl; stacks.append({'x':cx, 'y':cy, 'w':fw, 'l':fl, 'curH':it['height'], 'items':[it_c]}); cy+=fl; row_w=max(row_w, fw); w_sum+=it['weight']; stacked=True; break
                elif cx+row_w+fw <= veh['L'] and fl <= veh['W']:
                    cx+=row_w; cy=0; row_w=fw; it_c = it.copy(); it_c['z']=0; it_c['w_fit'], it_c['l_fit']=fw, fl; stacks.append({'x':cx, 'y':cy, 'w':fw, 'l':fl, 'curH':it['height'], 'items':[it_c]}); cy+=fl; w_sum+=it['weight']; stacked=True; break
            if not stacked: failed.append(it)
    return stacks, w_sum, failed, (max([s['x']+s['w'] for s in stacks])/100 if stacks else 0)

# =========================================================
# 5. GŁÓWNA APLIKACJA (MASTER CONTROL)
# =========================================================
def main():
    apply_vorteza_theme()
    if not check_vorteza_auth(): return

    # Header
    h1, h2 = st.columns([4, 1])
    with h1:
        st.markdown("<h1>VORTEZA FLOW</h1><p style='color:#555; font-size:0.75rem; letter-spacing:2px;'>LOGISTICS MASTER v4.0 | ENTERPRISE CONTROL</p>", unsafe_allow_html=True)
    with h2:
        if st.button("LOGOUT SYSTEM"): st.session_state.v_auth = False; st.rerun()

    if 'v_cargo' not in st.session_state: st.session_state.v_cargo = []

    # Sidebar
    with st.sidebar:
        st.markdown("### KONFIGURACJA ZASOBÓW")
        v_sel = st.selectbox("WYBIERZ POJAZD", list(VEHICLES.keys()))
        veh = VEHICLES[v_sel]
        st.divider()
        try:
            with open('products.json', 'r', encoding='utf-8') as f: db = json.load(f)
        except: db = []
        
        p_name = st.selectbox("PRODUKT", [p['name'] for p in db], index=None)
        if p_name:
            p_ref = next(p for p in db if p['name'] == p_name)
            ipc = p_ref.get('itemsPerCase', 1)
            st.markdown(f"<div style='font-size:0.75rem; color:#B58863;'>STANDARD PAKOWANIA: {ipc} szt.</div>", unsafe_allow_html=True)
            p_qty = st.number_input("LICZBA SZTUK", min_value=1, value=ipc)
            n_c = math.ceil(p_qty / ipc)
            if st.button("DODAJ DO MANIFESTU"):
                for i in range(n_c):
                    case = p_ref.copy()
                    case['p_act'] = ipc if (i < n_c - 1 or p_qty % ipc == 0) else (p_qty % ipc)
                    st.session_state.v_cargo.append(case)
                st.rerun()
        if st.button("RESTART SYSTEMU"): st.session_state.v_cargo = []; st.rerun()

    # Dashboard
    if st.session_state.v_cargo:
        # Metryki
        total_kg = sum(float(c.get('weight', 0)) for c in st.session_state.v_cargo)
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("OPAKOWANIA", len(st.session_state.v_cargo))
        m2.metric("SZTUKI", sum(int(c.get('p_act', 1)) for c in st.session_state.v_cargo))
        m3.metric("WAGA", f"{total_kg} KG")
        m4.metric("LDM (EST.)", f"{(total_kg/veh['maxW'])*(veh['L']/100):.2f}")

        # Pakowanie
        rem = [dict(c) for c in st.session_state.v_cargo]
        fleet = []
        while rem:
            s, w, n, l = packing_engine(rem, veh)
            if not s: break
            fleet.append({"stacks":s, "weight":w, "ldm":l})
            rem = n

        st.markdown(f"### ASYGNACJA FLOTY: {len(fleet)} JEDNOSTKI")
        for idx, truck in enumerate(fleet):
            st.markdown('<div class="vorteza-card">', unsafe_allow_html=True)
            c3d, cde = st.columns([2, 1])
            with c3d: st.plotly_chart(render_3d_engine(veh, truck['stacks']), use_container_width=True)
            with cde:
                st.markdown(f"**POJAZD #{idx+1} | {v_sel}**")
                st.markdown(f"WYKORZYSTANIE LDM: <span style='color:#B58863;'>{truck['ldm']:.2f}</span> / {veh['ldm']}", unsafe_allow_html=True)
                st.markdown(f"MASA CAŁKOWITA: <span style='color:#B58863;'>{truck['weight']} KG</span>", unsafe_allow_html=True)
                st.divider()
                st.markdown("**MANIFEST ZAŁADUNKOWY:**")
                sum_df = pd.Series([it['name'] for s in truck['stacks'] for it in s['items']]).value_counts().reset_index()
                sum_df.columns = ['Produkt', 'Opakowań']
                html_t = '<table class="v-table"><tr><th>Produkt</th><th>Ilość</th></tr>'
                for _, r in sum_df.iterrows(): html_t += f'<tr><td>{r["Produkt"]}</td><td>{r["Opakowań"]}</td></tr>'
                st.markdown(html_t+'</table>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Eksport danych
        st.download_button("POBIERZ MANIFEST (CSV)", pd.DataFrame(st.session_state.v_cargo).to_csv(index=False), "manifest_vorteza.csv", "text/csv")
    else:
        st.markdown('<div class="vorteza-card" style="text-align:center;">SYSTEM GOTOWY. OCZEKIWANIE NA DANE...</div>', unsafe_allow_html=True)

if __name__ == "__main__": main()
