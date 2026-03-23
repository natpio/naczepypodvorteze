# -*- coding: utf-8 -*-
"""
================================================================================
SYSTEM: VORTEZA STACK 
VERSION: 41.0 | GOLIATH FINAL MONOLITH
FIRM: VORTEZA SYSTEMS
STATUS: VERIFIED i18n | FULL PRODUCTION | ONE FILE
================================================================================
"""

import streamlit as st
import json
import plotly.graph_objects as go
import math
import pandas as pd
import random
import base64
from datetime import datetime
import os

# ==============================================================================
# 1. SILNIK TŁUMACZEŃ (Rygorystycznie sprawdzony pod kątem kluczy)
# ==============================================================================
TRANSLATIONS = {
    "PL": {
        "lang_label": "JĘZYK INTERFEJSU", "fleet": "KONSOLA FLOTY", "cargo": "WPISYWANIE ŁADUNKU", 
        "planner": "PLANISTA TAKTYCZNY", "inventory": "MASTER INVENTORY", "unit": "POJAZD", 
        "offset": "OFFSET OD ŚCIANY (cm)", "sku_sel": "WYBÓR SKU", "qty": "SZTUKI", 
        "append": "DODAJ DO MANIFESTU", "purge": "WYCZYŚĆ WSZYSTKO", "cases": "OPAKOWANIA", 
        "pcs": "SZTUKI ŁĄCZNIE", "weight": "MASA BRUTTO", "util": "WYKORZYSTANIE", 
        "kpi": "PARAMETRY OPERACYJNE", "ldm": "ZAJĘTE LDM", "cog": "ANALIZA ŚRODKA CIĘŻKOŚCI (CoG)", 
        "axle_f": "OSIE PRZÓD (CAB)", "axle_r": "OSIE TYŁ (REAR)", "terminate": "ZAKOŃCZ SESJĘ", 
        "manifest": "LISTA ZAŁADUNKOWA", "standard": "STANDARD", "pcs_unit": "SZT/JEDN", 
        "sync": "SYNCHRONIZUJ BAZĘ", "register_new": "➕ REJESTRACJA PRODUKTU", "length": "L (cm)", 
        "width": "W (cm)", "height": "H (cm)", "mass": "MASA (kg)", "stack": "PIĘTROWANIE", 
        "rot": "ROTACJA", "placeholder": "Wybierz produkt z listy...", "commit": "ZAPISZ W BAZIE"
    },
    "ENG": {
        "lang_label": "INTERFACE LANGUAGE", "fleet": "FLEET CONSOLE", "cargo": "CARGO ENTRY", 
        "planner": "TACTICAL PLANNER", "inventory": "MASTER INVENTORY", "unit": "TRANSPORT UNIT", 
        "offset": "WALL OFFSET (cm)", "sku_sel": "SKU SELECTOR", "qty": "QUANTITY", 
        "append": "APPEND TO MANIFEST", "purge": "PURGE ALL DATA", "cases": "CASES", 
        "pcs": "TOTAL PIECES", "weight": "GROSS WEIGHT", "util": "UTILIZATION", 
        "kpi": "OPERATIONAL KPI", "ldm": "OCCUPIED LDM", "cog": "CENTER OF GRAVITY (CoG)", 
        "axle_f": "FRONT AXLES", "axle_r": "REAR AXLES", "terminate": "TERMINATE SESSION", 
        "manifest": "PACKING LIST", "standard": "STANDARD", "pcs_unit": "PCS/UNIT", 
        "sync": "SYNC DATABASE", "register_new": "➕ REGISTER NEW ASSET", "length": "L (cm)", 
        "width": "W (cm)", "height": "H (cm)", "mass": "MASS (kg)", "stack": "STACKING", 
        "rot": "ROTATION", "placeholder": "Choose a product...", "commit": "COMMIT TO DB"
    },
    "DE": {
        "lang_label": "SPRACHE", "fleet": "FLOTTENKONSOLE", "cargo": "LADUNGSEINGABE", 
        "planner": "TAKTIK-PLANER", "inventory": "PRODUKTDATENBANK", "unit": "FAHRZEUG", 
        "offset": "WANDABSTAND (cm)", "sku_sel": "SKU AUSWAHL", "qty": "MENGE", 
        "append": "ZUM MANIFEST HINZUFÜGEN", "purge": "ALLE LÖSCHEN", "cases": "PAKETE", 
        "pcs": "STÜCK GESAMT", "weight": "BRUTTOGEWICHT", "util": "AUSLASTUNG", 
        "kpi": "BETRIEBS-KPI", "ldm": "LDM BELEGT", "cog": "SCHWERPUNKTANALYSE", 
        "axle_f": "VORDERACHSEN", "axle_r": "HINTERACHSEN", "terminate": "BEENDEN", 
        "manifest": "LADUNGSMANIFEST", "standard": "STANDARD", "pcs_unit": "STK/UNIT", 
        "sync": "SYNC DATENBANK", "register_new": "➕ NEUES PRODUKT", "length": "L (cm)", 
        "width": "B (cm)", "height": "H (cm)", "mass": "GEWICHT (kg)", "stack": "STAPELBAR", 
        "rot": "DREHBAR", "placeholder": "Produkt auswählen...", "commit": "SPEICHERN"
    },
    "ES": {
        "lang_label": "IDIOMA DEL SISTEMA", "fleet": "CONSOLA DE FLOTA", "cargo": "ENTRADA DE CARGA", 
        "planner": "PLANIFICADOR", "inventory": "INVENTARIO MAESTRO", "unit": "VEHÍCULO", 
        "offset": "OFFSET DE PARED (cm)", "sku_sel": "SELECTOR SKU", "qty": "CANTIDAD", 
        "append": "AÑADIR AL MANIFIESTO", "purge": "BORRAR TODO", "cases": "BULTOS", 
        "pcs": "PIEZAS TOTALES", "weight": "PESO BRUTO", "util": "UTILIZACIÓN", 
        "kpi": "KPI OPERATIVO", "ldm": "LDM OCUPADO", "cog": "CENTRO DE GRAVEDAD (CoG)", 
        "axle_f": "EJES DELANTEROS", "axle_r": "EJES TRASEROS", "terminate": "TERMINAR", 
        "manifest": "MANIFIESTO", "standard": "ESTÁNDAR", "pcs_unit": "PZAS/UNID", 
        "sync": "SINCRONIZAR", "register_new": "➕ REGISTRAR PRODUCTO", "length": "L (cm)", 
        "width": "A (cm)", "height": "H (cm)", "mass": "PESO (kg)", "stack": "APILABLE", 
        "rot": "ROTACIÓN", "placeholder": "Elegir un producto...", "commit": "GUARDAR EN DB"
    }
}

# ==============================================================================
# 2. SPECYFIKACJA FLOTY
# ==============================================================================
FLEET_DATA = {
    "TIR FTL Mega 13.6m": {"max_w": 24000, "L": 1360, "W": 248, "H": 300, "ax": 3, "cab": 230},
    "TIR FTL Standard 13.6m": {"max_w": 24000, "L": 1360, "W": 248, "H": 275, "ax": 3, "cab": 230},
    "Solo 9m Heavy Duty": {"max_w": 9500, "L": 920, "W": 245, "H": 270, "ax": 2, "cab": 200}
}

# ==============================================================================
# 3. SUPREME UI & STYLE ENGINE (High Contrast Fix)
# ==============================================================================
st.set_page_config(page_title="VORTEZA STACK v41.0", layout="wide", initial_sidebar_state="expanded")

def load_v_asset(path):
    try:
        with open(path, 'rb') as f: return base64.b64encode(f.read()).decode()
    except: return ""

def apply_supreme_ui():
    bg = load_v_asset('bg_vorteza.png')
    st.markdown(f"""
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;600;700&family=JetBrains+Mono:wght@400;500&display=swap');
            :root {{ --v-copper: #B58863; --v-glow: rgba(181, 136, 99, 0.6); }}
            
            .stApp {{ background-image: url("data:image/png;base64,{bg}"); background-size: cover; background-attachment: fixed; color: #FFF; font-family: 'Montserrat'; }}
            
            /* ULTRA CONTRAST GLASS TILES - Naprawa czytelności */
            .v-tile-pro {{
                background: rgba(0, 0, 0, 0.98) !important;
                padding: 2.8rem; border-radius: 4px; border: 2px solid var(--v-copper);
                box-shadow: 0 60px 150px #000; margin-bottom: 3.5rem; backdrop-filter: blur(50px);
            }}

            section[data-testid="stSidebar"] {{ background-color: rgba(0, 0, 0, 0.99) !important; border-right: 1px solid var(--v-copper); width: 450px !important; }}
            
            h1, h2, h3 {{ color: var(--v-copper) !important; text-transform: uppercase; letter-spacing: 10px; font-weight: 700; text-shadow: 4px 4px 20px #000; }}
            
            /* Wyraźne Metryki */
            [data-testid="stMetricValue"] {{ color: var(--v-copper) !important; font-family: 'JetBrains Mono'; font-size: 3.8rem !important; font-weight: 400 !important; }}
            [data-testid="stMetricLabel"] {{ color: #BBB !important; text-transform: uppercase; letter-spacing: 4px; font-weight: 700; }}

            .stButton > button {{
                background: linear-gradient(180deg, #0a0a0a, #151515); color: var(--v-copper); border: 2px solid var(--v-copper);
                padding: 1.6rem; text-transform: uppercase; letter-spacing: 8px; font-weight: 700; width: 100%; transition: 0.5s all; border-radius: 0;
            }}
            .stButton > button:hover {{ background: var(--v-copper); color: #000; box-shadow: 0 0 100px var(--v-glow); transform: translateY(-5px); }}
            
            .v-rail-track {{ width: 100%; height: 35px; background: #000; border-radius: 17px; position: relative; border: 2px solid #222; margin: 60px 0; box-shadow: inset 0 0 25px #000; }}
            .v-cog-indicator {{ position: absolute; width: 15px; height: 75px; top: -20px; background: #00FF41; box-shadow: 0 0 50px #00FF41; border-radius: 8px; transition: left 1.5s cubic-bezier(0.19, 1, 0.22, 1); }}
        </style>
    """, unsafe_allow_html=True)

# ==============================================================================
# 4. RENDERER CAD-3D SUPREME (Precyzyjne mapowanie trójkątów)
# ==============================================================================
def get_v_color(name):
    palette = ["#B58863", "#D4AF37", "#8E6A4D", "#5E4633", "#A67C52", "#2C3E50", "#34495E", "#16A085", "#27AE60", "#7F8C8D", "#BDC3C7"]
    random.seed(sum(ord(c) for c in name))
    return random.choice(palette)

def build_box(x, y, z, dx, dy, dz, color, name):
    vx = [x, x+dx, x+dx, x, x, x+dx, x+dx, x]
    vy = [y, y, y+dy, y+dy, y, y, y+dy, y+dy]
    vz = [z, z, z, z, z+dz, z+dz, z+dz, z+dz]
    i, j, k = [7,0,0,0,4,4,6,6,4,0,3,2], [3,4,1,2,5,6,5,2,0,1,6,3], [0,7,2,3,6,7,1,1,5,5,7,6]
    mesh = go.Mesh3d(x=vx, y=vy, z=vz, i=i, j=j, k=k, color=color, opacity=0.98, name=name, flatshading=True, lighting=dict(ambient=0.4, diffuse=0.8, specular=1))
    lx = [x,x+dx,x+dx,x,x,x,x+dx,x+dx,x,x,x+dx,x+dx,x+dx,x+dx,x,x]
    ly = [y,y,y+dy,y+dy,y,y,y,y+dy,y+dy,y+dy,y+dy,y,y,y+dy,y+dy,y]
    lz = [z,z,z,z,z,z+dz,z+dz,z,z,z+dz,z+dz,z+dz,z,z,z+dz,z+dz]
    lines = go.Scatter3d(x=lx, y=ly, z=lz, mode='lines', line=dict(color='black', width=3.5), hoverinfo='skip')
    return [mesh, lines]

def render_3d_pro(veh, stacks):
    fig = go.Figure()
    L, W, H = veh['L'], veh['W'], veh['H']
    fig.add_trace(go.Mesh3d(x=[0,L,L,0], y=[0,0,W,W], z=[-15,-15,-15,-15], color='#111', opacity=1, hoverinfo='skip'))
    
    # Koła CAD i Osie
    for a in range(veh['ax']):
        px = (L-450) + (a*145) if L > 800 else (L-180) + (a*145)
        if px < L:
            for side in [-40, W+22]:
                fig.add_trace(go.Mesh3d(x=[px-55, px+55, px+55, px-55], y=[side, side, side+18, side+18], z=[-80, -80, -15, -15], color='#000', opacity=1))
                fig.add_trace(go.Mesh3d(x=[px-22, px+22, px+22, px-22], y=[side-2, side-2, side, side], z=[-55, -55, -35, -35], color='#B58863', opacity=0.9))

    # Kabina
    fig.add_trace(go.Mesh3d(x=[-veh['cab'], 0, 0, -veh['cab'], -veh['cab'], 0, 0, -veh['cab']], y=[-45,-45,W+45,W+45], z=[0,0,0,0,H*1.05,H*1.05,H*1.05,H*1.05], i=[7,0,0,0,4,4,6,6,4,0,3,2], j=[3,4,1,2,5,6,5,2,0,1,6,3], k=[0,7,2,3,6,7,1,1,5,5,7,6], color='#050505', opacity=1))

    # Szkielet miedziany
    skel = [([0,L],[0,0],[0,0]), ([0,L],[W,W],[0,0]), ([0,0],[0,W],[0,0]), ([L,L],[0,W],[0,0]), ([0,0],[0,0],[0,H]), ([0,0],[W,W],[0,H]), ([0,L],[0,0],[H,H]), ([0,L],[W,W],[H,H]), ([L,L],[0,0],[0,H]), ([L,L],[W,W],[0,H])]
    for lx, ly, lz in skel: fig.add_trace(go.Scatter3d(x=lx, y=ly, z=lz, mode='lines', line=dict(color='#B58863', width=12), hoverinfo='skip'))

    for s in stacks:
        for u in s['items']:
            parts = build_box(s['x'], s['y'], u['z'], u['w_fit'], u['l_fit'], u['height'], get_v_color(u['name']), u['name'])
            for p in parts: fig.add_trace(p)
    
    fig.update_layout(scene=dict(aspectmode='data', xaxis_visible=False, yaxis_visible=False, zaxis_visible=False, camera=dict(eye=dict(x=2.5, y=2.5, z=2.0))), paper_bgcolor='rgba(0,0,0,0)', margin=dict(l=0,r=0,b=0,t=0), showlegend=False)
    return fig

# ==============================================================================
# 5. PACKING ENGINE V-ENGINE 41.0
# ==============================================================================
class V41Engine:
    @staticmethod
    def pack(cargo, veh, offset=0):
        # Priorytet: Stack NO > Area
        items = sorted(cargo, key=lambda x: (not x.get('canStack', True), x['width']*x['length']), reverse=True)
        stacks, failed, mass = [], [], 0
        cx, cy, r_max_w = offset, 0, 0
        for u in items:
            if mass + u['weight'] > veh['max_w']: failed.append(u); continue
            stacked = False
            if u.get('canStack', True):
                for s in stacks:
                    if (u['width'] <= s['w'] and u['length'] <= s['l']) and (s['curH'] + u['height'] <= veh['H']):
                        uc = u.copy(); uc['z'] = s['curH']; uc['w_fit'], uc['l_fit'] = s['w'], s['l']
                        s['items'].append(uc); s['curH'] += u['height']; mass += u['weight']; stacked = True; break
            if stacked: continue
            if cy + u['length'] <= veh['W'] and cx + u['width'] <= veh['L']:
                uc = u.copy(); uc['z'] = 0; uc['w_fit'], uc['l_fit'] = u['width'], u['length']
                stacks.append({'x':cx, 'y':cy, 'w':u['width'], 'l':u['length'], 'curH':u['height'], 'items':[uc]})
                cy += u['length']; r_max_w = max(r_max_w, u['width']); mass += u['weight']
            elif cx + r_max_w + u['width'] <= veh['L'] and u['length'] <= veh['W']:
                cx += r_max_w; cy = 0; r_max_w = u['width']
                uc = u.copy(); uc['z'] = 0; uc['w_fit'], uc['l_fit'] = u['width'], u['length']
                stacks.append({'x':cx, 'y':cy, 'w':u['width'], 'l':u['length'], 'curH':u['height'], 'items':[uc]})
                cy += u['length']; mass += u['weight']
            else: failed.append(u)
        ldm = (max([s['x'] + s['w'] for s in stacks]) / 100) if stacks else 0
        return stacks, mass, failed, ldm

# ==============================================================================
# 6. GŁÓWNA ARCHITEKTURA
# ==============================================================================
def main():
    apply_supreme_ui()
    
    if 'authorized' not in st.session_state: st.session_state.authorized = False
    if not st.session_state.authorized:
        sys_key = "vorteza2026"
        _, col, _ = st.columns([1, 1.8, 1])
        with col:
            with st.form("VAuthFinal"):
                st.markdown("<h2 style='text-align:center;'>VORTEZA STACK</h2>", unsafe_allow_html=True)
                pwd_in = st.text_input("GOLIATH MASTER CORE KEY", type="password")
                if st.form_submit_button("UNLOCK"):
                    if pwd_in == sys_key: st.session_state.authorized = True; st.rerun()
                    else: st.error("INVALID KEY")
        st.stop()

    if 'v_manifest' not in st.session_state: st.session_state.v_manifest = []
    
    # Naprawa wyboru języka - Zapewnienie poprawności etykiet
    lang_code = st.sidebar.radio("LANGUAGE / JĘZYK", ["PL", "ENG", "DE", "ES"], horizontal=True)
    T = TRANSLATIONS[lang_code]

    if os.path.exists('products.json'):
        with open('products.json', 'r', encoding='utf-8') as f: inventory = json.load(f)
    else: inventory = []

    # SIDEBAR MISSION COMMAND
    with st.sidebar:
        st.markdown(f"### 📡 {T['fleet']}")
        v_sel = st.selectbox(T['unit'], list(FLEET_DATA.keys()))
        veh = FLEET_DATA[v_sel]
        x_off = st.slider(T['offset'], 0, veh['L']-200, 0)
        
        st.divider()
        st.markdown(f"### 📥 {T['cargo']}")
        sku_list = [p['name'] for p in inventory]
        sku = st.selectbox(T['sku_sel'], sku_list, index=None, placeholder=T['placeholder'])
        if sku:
            p_ref = next(i for i in inventory if i['name'] == sku)
            ipc = p_ref.get('itemsPerCase', 1)
            st.markdown(f"<div style='color:#B58863; font-size:0.8rem;'>{T['standard']}: {ipc} {T['pcs_unit']}</div>", unsafe_allow_html=True)
            qty = st.number_input(T['qty'], 1, 1000, ipc)
            if st.button(T['append']):
                for _ in range(math.ceil(qty/ipc)): st.session_state.v_manifest.append(p_ref.copy())
                st.rerun()
        if st.button(T['purge']): st.session_state.v_manifest = []; st.rerun()

    # DASHBOARD
    st.markdown(f"<h1>VORTEZA STACK</h1>", unsafe_allow_html=True)
    tab_p, tab_i = st.tabs([f"📊 {T['planner']}", f"📦 {T['inventory']}"])

    with tab_p:
        if st.session_state.v_manifest:
            k1, k2, k3, k4 = st.columns(4)
            tm_tot = sum(float(u['weight']) for u in st.session_state.v_manifest)
            k1.metric(T['cases'], len(st.session_state.v_manifest))
            k2.metric(T['pcs'], sum(int(u.get('itemsPerCase', 1)) for u in st.session_state.v_manifest))
            k3.metric(T['weight'], f"{tm_tot} KG")
            k4.metric(T['util'], f"{(tm_tot/veh['max_w'])*100:.1f}%")
            
            rem = [dict(u) for u in st.session_state.v_manifest]
            fleet_res = []
            while rem:
                s, w, n, l = V41Engine.pack(rem, veh, offset=x_off)
                if not s: break
                fleet_res.append({"s": s, "w": w, "l": l}); rem = n
                
            for idx, unit in enumerate(fleet_res):
                st.markdown(f'<div class="v-tile-pro">', unsafe_allow_html=True)
                st.markdown(f"### MISSION UNIT #{idx+1} | {v_sel}")
                vc, dc = st.columns([2.8, 1])
                with vc:
                    st.plotly_chart(render_3d_pro(veh, unit['s']), use_container_width=True)
                    # Balans CoG
                    tm, tw = 0, 0
                    for s_clust in unit['s']:
                        for i_unit in s_clust['items']: tm += (s_clust['x']+i_unit['w_fit']/2)*i_unit['weight']; tw += i_unit['weight']
                    cp = (tm/tw/veh['L'])*100 if tw > 0 else 0
                    st.markdown(f"#### ⚖️ {T['cog']}")
                    st.markdown(f'<div class="v-rail-track"><div class="v-cog-indicator" style="left:{cp}%;"></div></div><br>', unsafe_allow_html=True)
                with dc:
                    st.markdown(f"**{T['kpi']}**")
                    st.write(f"{T['ldm']}: **{unit['l']:.2f} m**")
                    st.write(f"{T['weight']}: **{unit['w']} kg**")
                    st.divider()
                    st.markdown(f"**{T['manifest']}**")
                    agg = pd.Series([u['name'] for s_box in unit['s'] for u in s_box['items']]).value_counts().reset_index()
                    agg.columns = ['SKU', 'QTY']
                    h_table = f'<table class="v-table-tactical"><tr><th>SKU</th><th>{T["qty"]}</th></tr>'
                    for _, r in agg.iterrows():
                        h_table += f'<tr><td><span style="color:{get_v_color(r["SKU"])}">■</span> {r["SKU"]}</td><td>{r["QTY"]}</td></tr>'
                    st.markdown(h_table + '</table>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
        else: st.info(T['placeholder'])

    with tab_i:
        st.markdown(f"### 📦 {T['inventory']}")
        if inventory:
            df_inv = pd.DataFrame(inventory)
            edt = st.data_editor(df_inv, use_container_width=True, num_rows="dynamic")
            if st.button(T['sync']):
                with open('products.json', 'w', encoding='utf-8') as f: json.dump(edt.to_dict('records'), f, indent=4, ensure_ascii=False)
                st.success("SYNC OK")
        
        with st.expander(f"{T['register_new']}"):
            with st.form("NewAssetFormFinal"):
                fn = st.text_input("Name / SKU")
                c1, c2, c3 = st.columns(3)
                fl, fw, fh = c1.number_input(T['length'], 120), c2.number_input(T['width'], 80), c3.number_input(T['height'], 100)
                fm, fi = st.number_input(T['mass'], 50), st.number_input(T['pcs_unit'], 1)
                ca1, ca2 = st.columns(2)
                fs, fr = ca1.checkbox(T['stack'], True), ca2.checkbox(T['rot'], True)
                if st.form_submit_button(T['commit']):
                    inventory.append({"name":fn,"length":fl,"width":fw,"height":fh,"weight":fm,"itemsPerCase":fi,"canStack":fs,"allowRotation":fr})
                    with open('products.json', 'w', encoding='utf-8') as f: json.dump(inventory, f, indent=4, ensure_ascii=False)
                    st.rerun()

if __name__ == "__main__": main()
