# -*- coding: utf-8 -*-
"""
================================================================================
SYSTEM: VORTEZA STACK 
VERSION: 32.0 | INFINITY ARCHITECT
FIRM: VORTEZA SYSTEMS
STATUS: ENTERPRISE PRODUCTION READY | NO SHORTCUTS | FULL SOURCE CODE
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
import io
import os
from PIL import Image

# ==============================================================================
# 1. SYSTEM TŁUMACZEŃ (VERIFIED i18n ENGINE)
# ==============================================================================
TRANSLATIONS = {
    "PL": {
        "fleet": "KONSOLA FLOTY", "cargo": "WPISYWANIE ŁADUNKU", "planner": "PLANISTA TAKTYCZNY",
        "inventory": "BAZA PRODUKTÓW", "logs": "LOGI SYSTEMOWE", "unit": "POJAZD", "offset": "OFFSET OD ŚCIANY (cm)",
        "truss_calc": "KALKULATOR KRATOWNIC", "add_truss": "PRZELICZ I DODAJ WÓZKI", "sku_sel": "WYBÓR SKU",
        "qty": "SZTUKI", "append": "DODAJ DO MANIFESTU", "purge": "WYCZYŚĆ WSZYSTKO", "cases": "OPAKOWANIA",
        "pcs": "SZTUKI ŁĄCZNIE", "weight": "MASA BRUTTO", "util": "WYKORZYSTANIE", "kpi": "PARAMETRY OPERACYJNE",
        "ldm": "ZAJĘTE LDM", "cog": "ANALIZA ŚRODKA CIĘŻKOŚCI (CoG)", "axle_f": "OSIE PRZÓD (CAB)", 
        "axle_r": "OSIE TYŁ (REAR)", "rotation": "ROTACJA", "auth_req": "WYMAGANA AUTORYZACJA",
        "truss_2m": "KRATY 2M (SZT)", "truss_3m": "KRATY 3M (SZT)", "manifest": "MANIFEST ZAŁADUNKOWY",
        "terminate": "ZAKOŃCZ SESJĘ", "sync": "SYNCHRONIZUJ BAZĘ", "new_sku": "REJESTRACJA NOWEGO SKU",
        "length": "DŁUGOŚĆ (cm)", "width": "SZEROKOŚĆ (cm)", "height": "WYSOKOŚĆ (cm)", 
        "can_stack": "PIĘTROWANIE OK", "can_rotate": "OBRÓT OK", "mass_kg": "MASA (kg)", 
        "ipu": "SZTUK W CASE", "standard": "STANDARD", "pcs_unit": "SZT/JEDN",
        "oversize": "ALARM: JEDNOSTKA ZA DUŻA DLA FLOTY", "sync_ok": "BAZA ZSYNCHRONIZOWANA"
    },
    "ENG": {
        "fleet": "FLEET CONSOLE", "cargo": "CARGO ENTRY", "planner": "TACTICAL PLANNER",
        "inventory": "MASTER INVENTORY", "logs": "SYSTEM LOGS", "unit": "TRANSPORT UNIT", "offset": "WALL OFFSET (cm)",
        "truss_calc": "TRUSS CALCULATOR", "add_truss": "CALC & ADD CARTS", "sku_sel": "SKU SELECTOR",
        "qty": "QUANTITY", "append": "APPEND TO MANIFEST", "purge": "PURGE ALL DATA", "cases": "CASES",
        "pcs": "TOTAL PIECES", "weight": "GROSS WEIGHT", "util": "UTILIZATION", "kpi": "OPERATIONAL KPI",
        "ldm": "LDM OCCUPIED", "cog": "CENTER OF GRAVITY (CoG)", "axle_f": "FRONT AXLES", 
        "axle_r": "REAR AXLES", "rotation": "ROTATION", "auth_req": "AUTHORIZATION REQUIRED",
        "truss_2m": "TRUSS 2M (PCS)", "truss_3m": "TRUSS 3M (PCS)", "manifest": "CARGO MANIFEST",
        "terminate": "TERMINATE SESSION", "sync": "SYNC DATABASE", "new_sku": "REGISTER NEW SKU",
        "length": "LENGTH (cm)", "width": "WIDTH (cm)", "height": "HEIGHT (cm)", 
        "can_stack": "STACKING OK", "can_rotate": "ROTATION OK", "mass_kg": "MASS (kg)", 
        "ipu": "PCS PER UNIT", "standard": "STANDARD", "pcs_unit": "PCS/UNIT",
        "oversize": "ALARM: UNIT OVERSIZE FOR FLEET", "sync_ok": "DATABASE SYNCHRONIZED"
    },
    "DE": {
        "fleet": "FLOTTENKONSOLE", "cargo": "LADUNGSEINGABE", "planner": "TAKTIK-PLANER",
        "inventory": "PRODUKTDATENBANK", "logs": "SYSTEMLOGS", "unit": "FAHRZEUG", "offset": "WANDABSTAND (cm)",
        "truss_calc": "TRAVERSEN-RECHNER", "add_truss": "BERECHNEN & HINZUFÜGEN", "sku_sel": "SKU AUSWAHL",
        "qty": "MENGE", "append": "ZUM MANIFEST HINZUFÜGEN", "purge": "ALLE LÖSCHEN", "cases": "PAKETE",
        "pcs": "STÜCK GESAMT", "weight": "BRUTTOGEWICHT", "util": "AUSLASTUNG", "kpi": "BETRIEBS-KPI",
        "ldm": "LDM BELEGT", "cog": "SCHWERPUNKTANALYSE", "axle_f": "VORDERACHSEN", 
        "axle_r": "HINTERACHSEN", "rotation": "ROTATION", "auth_req": "AUTORISIERUNG ERFORDERLICH",
        "truss_2m": "TRAVERSEN 2M", "truss_3m": "TRAVERSEN 3M", "manifest": "LADUNGSMANIFEST",
        "terminate": "BEENDEN", "sync": "SYNC DATENBANK", "new_sku": "NEUES SKU",
        "length": "LÄNGE", "width": "BREITE", "height": "HÖHE", 
        "can_stack": "STAPELBAR", "can_rotate": "DREHBAR", "mass_kg": "GEWICHT (kg)", 
        "ipu": "STK/EINHEIT", "standard": "STANDARD", "pcs_unit": "STK/UNIT",
        "oversize": "ALARM: EINHEIT ZU GROSS", "sync_ok": "SYNC ERFOLGREICH"
    },
    "ES": {
        "fleet": "CONSOLA DE FLOTA", "cargo": "ENTRADA DE CARGA", "planner": "PLANIFICADOR",
        "inventory": "INVENTARIO MAESTRO", "logs": "LOGS DEL SISTEMA", "unit": "VEHÍCULO", "offset": "OFFSET DE PARED (cm)",
        "truss_calc": "CALCULADORA TRUSS", "add_truss": "CALCULAR Y AÑADIR", "sku_sel": "SELECTOR SKU",
        "qty": "CANTIDAD", "append": "AÑADIR AL MANIFIESTO", "purge": "BORRAR TODO", "cases": "BULTOS",
        "pcs": "PIEZAS TOTALES", "weight": "PESO BRUTO", "util": "UTILIZACIÓN", "kpi": "KPI OPERATIVO",
        "ldm": "LDM OCUPADO", "cog": "CENTRO DE GRAVEDAD", "axle_f": "EJES DELANTEROS", 
        "axle_r": "EJES TRASEROS", "rotation": "ROTACIÓN", "auth_req": "AUTORIZACIÓN REQUERIDA",
        "truss_2m": "TRUSS 2M", "truss_3m": "TRUSS 3M", "manifest": "MANIFIESTO DE CARGA",
        "terminate": "TERMINAR", "sync": "SINCRONIZAR BASE", "new_sku": "REGISTRAR SKU",
        "length": "LONGITUD", "width": "ANCHO", "height": "ALTURA", 
        "can_stack": "APILABLE", "can_rotate": "ROTACIÓN OK", "mass_kg": "PESO (kg)", 
        "ipu": "PZAS/UNID", "standard": "ESTÁNDAR", "pcs_unit": "PZAS/UNID",
        "oversize": "ALARM: UNIDAD DEMASIADO GRANDE", "sync_ok": "SYNC COMPLETADO"
    }
}

# ==============================================================================
# 2. DEFINICJE TECHNICZNE FLOTY
# ==============================================================================
FLEET_REGISTRY = {
    "TIR FTL Mega 13.6m": {"max_w": 24000, "L": 1360, "W": 248, "H": 300, "ax": 3, "cab": 240, "tare": 14500},
    "TIR FTL Standard 13.6m": {"max_w": 24000, "L": 1360, "W": 248, "H": 275, "ax": 3, "cab": 240, "tare": 13800},
    "Solo 9m Heavy Duty": {"max_w": 9500, "L": 920, "W": 245, "H": 270, "ax": 2, "cab": 200, "tare": 8500},
    "Solo 7m Medium": {"max_w": 7000, "L": 720, "W": 245, "H": 260, "ax": 2, "cab": 180, "tare": 6200},
    "BUS XL Express": {"max_w": 1300, "L": 485, "W": 175, "H": 220, "ax": 2, "cab": 140, "tare": 2250}
}

# ==============================================================================
# 3. BRANDING & SUPREME CSS ENGINE
# ==============================================================================
st.set_page_config(
    page_title="VORTEZA STACK v32.0",
    layout="wide",
    initial_sidebar_state="expanded",
    page_icon="🕋"
)

def get_b64_asset(path):
    try:
        if os.path.exists(path):
            with open(path, 'rb') as f: return base64.b64encode(f.read()).decode()
        return ""
    except: return ""

def inject_vorteza_supreme_ui():
    bg_b64 = get_b64_asset('bg_vorteza.png')
    st.markdown(f"""
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;600;700&family=JetBrains+Mono:wght@400;500&display=swap');
            
            :root {{
                --v-copper: #B58863;
                --v-glow: rgba(181, 136, 99, 0.6);
            }}

            .stApp {{
                background-image: url("data:image/png;base64,{bg_b64}");
                background-size: cover;
                background-attachment: fixed;
                color: #FFFFFF;
                font-family: 'Montserrat', sans-serif;
            }}

            /* APEX GLASS PANELS - Maksymalna czytelność na tle carbon */
            .v-tile-pro {{
                background: rgba(4, 4, 4, 0.97);
                padding: 2.8rem;
                border: 1px solid rgba(181, 136, 99, 0.3);
                border-left: 12px solid var(--v-copper);
                box-shadow: 0 60px 150px #000;
                margin-bottom: 3.5rem;
                backdrop-filter: blur(50px);
            }}

            section[data-testid="stSidebar"] {{
                background-color: rgba(2, 2, 2, 0.99) !important;
                border-right: 1px solid var(--v-copper);
                width: 500px !important;
                backdrop-filter: blur(40px);
            }}

            h1, h2, h3 {{ 
                color: var(--v-copper) !important; 
                text-transform: uppercase; 
                letter-spacing: 12px !important; 
                font-weight: 700 !important; 
                text-shadow: 4px 4px 25px #000;
            }}

            [data-testid="stMetricValue"] {{ 
                color: var(--v-copper) !important; 
                font-family: 'JetBrains Mono', monospace !important; 
                font-size: 3.8rem !important;
                text-shadow: 0 0 20px rgba(181, 136, 99, 0.4);
            }}

            .stButton > button {{
                background: linear-gradient(180deg, #0a0a0a, #1a1a1a);
                color: var(--v-copper);
                border: 2px solid var(--v-copper);
                padding: 1.8rem;
                text-transform: uppercase;
                letter-spacing: 10px;
                font-weight: 700;
                width: 100%;
                transition: 0.6s all cubic-bezier(0.19, 1, 0.22, 1);
                border-radius: 0;
            }}
            .stButton > button:hover {{
                background: var(--v-copper);
                color: #000;
                box-shadow: 0 0 100px var(--v-glow);
                transform: translateY(-5px);
            }}

            .v-rail-track {{
                width: 100%; height: 35px; background: #000; border-radius: 17px; position: relative; border: 2px solid #222; margin: 60px 0;
                box-shadow: inset 0 0 30px #000;
            }}
            .v-cog-indicator {{
                position: absolute; width: 14px; height: 75px; top: -20px; background: #00FF41; 
                box-shadow: 0 0 50px #00FF41; border-radius: 7px;
                transition: left 1.5s cubic-bezier(0.19, 1, 0.22, 1);
            }}

            .v-table-tactical {{ 
                width: 100%; border-collapse: collapse; margin-top: 45px; border: 1px solid #1a1a1a; 
            }}
            .v-table-tactical th {{ 
                background: #000; color: var(--v-copper); text-align: left; font-size: 0.9rem; 
                text-transform: uppercase; border-bottom: 3px solid #333; padding: 25px; letter-spacing: 3px;
            }}
            .v-table-tactical td {{ 
                padding: 22px 25px; border-bottom: 1px solid #111; color: #CCC; font-size: 1.1rem; 
            }}
            .v-table-tactical tr:hover {{ background: rgba(181, 136, 99, 0.08); }}

            .v-status-box {{
                background: rgba(181, 136, 99, 0.1); border: 1px solid var(--v-copper); padding: 20px; margin-bottom: 25px; font-family: 'JetBrains Mono'; font-size: 0.85rem;
            }}
        </style>
    """, unsafe_allow_html=True)

# ==============================================================================
# 4. SILNIK RENDERINGU 3D (EXPLICIT VERTEX ENGINE)
# ==============================================================================
def get_chromatic_color(name):
    palette = ["#B58863", "#D4AF37", "#8E6A4D", "#5E4633", "#A67C52", "#2C3E50", "#34495E", "#1A252F", "#16A085", "#27AE60", "#7F8C8D", "#95A5A6", "#BDC3C7", "#C0392B", "#F1C40F", "#E67E22"]
    random.seed(sum(ord(c) for c in name))
    return random.choice(palette)

def build_pro_box(x, y, z, dx, dy, dz, color, name):
    """Generuje matematycznie precyzyjną siatkę Mesh3d (12 trójkątów)."""
    vx = [x, x+dx, x+dx, x, x, x+dx, x+dx, x]
    vy = [y, y, y+dy, y+dy, y, y, y+dy, y+dy]
    vz = [z, z, z, z, z+dz, z+dz, z+dz, z+dz]
    # Indeksy ścian (6 ścian * 2 trójkąty)
    i = [7, 0, 0, 0, 4, 4, 6, 6, 4, 0, 3, 2]
    j = [3, 4, 1, 2, 5, 6, 5, 2, 0, 1, 6, 3]
    k = [0, 7, 2, 3, 6, 7, 1, 1, 5, 5, 7, 6]
    
    mesh = go.Mesh3d(x=vx, y=vy, z=vz, i=i, j=j, k=k, color=color, opacity=0.98, name=name, flatshading=True, lighting=dict(ambient=0.4, diffuse=0.8, specular=1))
    # Grubsze krawędzie dla czytelności
    lx = [x,x+dx,x+dx,x,x,x,x+dx,x+dx,x,x,x+dx,x+dx,x+dx,x+dx,x,x]
    ly = [y,y,y+dy,y+dy,y,y,y,y+dy,y+dy,y+dy,y+dy,y,y,y+dy,y+dy,y]
    lz = [z,z,z,z,z,z+dz,z+dz,z,z,z+dz,z+dz,z+dz,z,z,z+dz,z+dz]
    lines = go.Scatter3d(x=lx, y=ly, z=lz, mode='lines', line=dict(color='black', width=4), hoverinfo='skip')
    return [mesh, lines]

def render_vorteza_3d_engine(veh, stacks):
    fig = go.Figure()
    L, W, H = veh['L'], veh['W'], veh['H']
    
    # Podwozie
    fig.add_trace(go.Mesh3d(x=[0,L,L,0], y=[0,0,W,W], z=[-15,-15,-15,-15], color='#111', opacity=1, hoverinfo='skip'))
    
    # Koła CAD
    for a in range(veh['ax']):
        px = (L-450) + (a*145) if L > 800 else (L-180) + (a*145)
        if px < L:
            for side in [-42, W+26]:
                fig.add_trace(go.Mesh3d(x=[px-60, px+60, px+60, px-60], y=[side, side, side+18, side+18], z=[-85, -85, -15, -15], color='#000', opacity=1, hoverinfo='skip'))
                fig.add_trace(go.Mesh3d(x=[px-25, px+25, px+25, px-25], y=[side-2, side-2, side, side], z=[-60, -60, -35, -35], color='#B58863', opacity=0.9, hoverinfo='skip'))

    # Kabina Commander
    fig.add_trace(go.Mesh3d(x=[-veh['cab'], 0, 0, -veh['cab'], -veh['cab'], 0, 0, -veh['cab']], y=[-45,-45,W+45,W+45,-45,-45,W+45,W+45], z=[0,0,0,0,H*1.05,H*1.05,H*1.05,H*1.05], i=[7,0,0,0,4,4,6,6,4,0,3,2], j=[3,4,1,2,5,6,5,2,0,1,6,3], k=[0,7,2,3,6,7,1,1,5,5,7,6], color='#020202', opacity=1))

    # Klatka miedziana
    skel = [([0,L],[0,0],[0,0]), ([0,L],[W,W],[0,0]), ([0,0],[0,W],[0,0]), ([L,L],[0,W],[0,0]), ([0,0],[0,0],[0,H]), ([0,0],[W,W],[0,H]), ([0,L],[0,0],[H,H]), ([0,L],[W,W],[H,H]), ([L,L],[0,0],[0,H]), ([L,L],[W,W],[0,H])]
    for lx, ly, lz in skel: fig.add_trace(go.Scatter3d(x=lx, y=ly, z=lz, mode='lines', line=dict(color='#B58863', width=12), hoverinfo='skip'))

    # Towar
    for s in stacks:
        for u in s['items']:
            parts = build_pro_box(s['x'], s['y'], u['z'], u['w_fit'], u['l_fit'], u['height'], get_chromatic_color(u['name']), u['name'])
            for p in parts: fig.add_trace(p)

    fig.update_layout(scene=dict(aspectmode='data', xaxis_visible=False, yaxis_visible=False, zaxis_visible=False, camera=dict(eye=dict(x=2.5, y=2.5, z=2.0))), paper_bgcolor='rgba(0,0,0,0)', margin=dict(l=0,r=0,b=0,t=0), showlegend=False)
    return fig

# ==============================================================================
# 5. SUPREME PACKING ENGINE (V-ENGINE 32.0)
# ==============================================================================
class V32Engine:
    @staticmethod
    def pack(cargo, veh, offset=0):
        # Priorytet pakowania: No-Stack > No-Rotation > Powierzchnia
        items = sorted(cargo, key=lambda x: (not x.get('canStack', True), not x.get('allowRotation', True), x['width']*x['length']), reverse=True)
        stacks, failed, weight_accumulator = [], [], 0
        cx, cy, r_max_w = offset, 0, 0
        for u in items:
            if weight_accumulator + u['weight'] > veh['max_w']: failed.append(u); continue
            integrated = False
            if u.get('canStack', True):
                for s in stacks:
                    rot = u.get('allowRotation', True)
                    fit = (u['width'] <= s['w'] and u['length'] <= s['l']) or (u['length'] <= s['w'] and u['width'] <= s['l']) if rot else (u['width'] <= s['w'] and u['length'] <= s['l'])
                    if fit and (s['curH'] + u['height'] <= veh['H']):
                        uc = u.copy(); uc['z'] = s['curH']; uc['w_fit'], uc['l_fit'] = s['w'], s['l']
                        s['items'].append(uc); s['curH'] += u['height']; weight_accumulator += u['weight']; integrated = True; break
            if integrated: continue
            placed = False
            rots = [(u['width'], u['length']), (u['length'], u['width'])] if u.get('allowRotation', True) else [(u['width'], u['length'])]
            for fw, fl in rots:
                if cy + fl <= veh['W'] and cx + fw <= veh['L']:
                    uc = u.copy(); uc['z'] = 0; uc['w_fit'], uc['l_fit'] = fw, fl
                    stacks.append({'x':cx, 'y':cy, 'w':fw, 'l':fl, 'curH':u['height'], 'items':[uc]})
                    cy += fl; r_max_w = max(r_max_w, fw); weight_accumulator += u['weight']; placed = True; break
                elif cx + r_max_w + fw <= veh['L'] and fl <= veh['W']:
                    cx += r_max_w; cy = 0; r_max_w = fw
                    uc = u.copy(); uc['z'] = 0; uc['w_fit'], uc['l_fit'] = fw, fl
                    stacks.append({'x':cx, 'y':cy, 'w':fw, 'l':fl, 'curH':u['height'], 'items':[uc]})
                    cy += fl; weight_accumulator += u['weight']; placed = True; break
            if not placed: failed.append(u)
        ldm = (max([s['x'] + s['w'] for s in stacks]) / 100) if stacks else 0
        return stacks, weight_accumulator, failed, ldm

# ==============================================================================
# 6. GŁÓWNA APLIKACJA
# ==============================================================================
def main():
    inject_vorteza_supreme_ui()
    if 'authorized' not in st.session_state: st.session_state.authorized = False
    if not st.session_state.authorized:
        sys_key = str(st.secrets.get("password", "vorteza2026"))
        _, c, _ = st.columns([1, 1.8, 1])
        with c:
            with st.form("Login"):
                st.markdown("<h2 style='text-align:center;'>VORTEZA STACK</h2>", unsafe_allow_html=True)
                pwd = st.text_input("GOLIATH MASTER AUTHENTICATION", type="password")
                if st.form_submit_button("UNLOCK SYSTEM"):
                    if pwd == sys_key: st.session_state.authorized = True; st.rerun()
                    else: st.error("INVALID KEY")
        return

    if 'v_manifest' not in st.session_state: st.session_state.v_manifest = []
    if 'lang' not in st.session_state: st.session_state.lang = "PL"
    T = TRANSLATIONS[st.session_state.lang]
    
    # Baza SKU
    if os.path.exists('products.json'):
        with open('products.json', 'r', encoding='utf-8') as f: inventory = json.load(f)
    else: inventory = []

    # --- SIDEBAR KONTROLA ---
    with st.sidebar:
        st.session_state.lang = st.radio("INTERFACE LANGUAGE", ["PL", "ENG", "DE", "ES"], horizontal=True)
        st.markdown(f"### 📡 {T['fleet']}")
        v_sel = st.selectbox(T['unit'], list(FLEET_REGISTRY.keys()))
        veh = FLEET_REGISTRY[v_sel]
        x_off = st.slider(T['offset'], 0, veh['L']-200, 0)
        
        st.divider()
        st.markdown(f"### 📐 {T['truss_calc']}")
        cl1, cl2 = st.columns(2)
        t2m = cl1.number_input(T['truss_2m'], 0, 500, 0)
        t3m = cl2.number_input(T['truss_3m'], 0, 500, 0)
        if st.button(T['add_truss'], type="secondary"):
            # Urealnione wymiary: H=240, canStack=False
            p2 = {"name": "truss cart 14x2", "length": 200, "width": 60, "height": 240, "weight": 420, "canStack": False, "allowRotation": True, "itemsPerCase": 1}
            p3 = {"name": "truss cart 14x3", "length": 300, "width": 60, "height": 240, "weight": 630, "canStack": False, "allowRotation": True, "itemsPerCase": 1}
            for _ in range(math.ceil(t2m/14)): st.session_state.v_manifest.append(p2.copy())
            for _ in range(math.ceil(t3m/14)): st.session_state.v_manifest.append(p3.copy())
            st.rerun()

        st.divider()
        st.markdown(f"### 📥 {T['cargo']}")
        sku_list = [p['name'] for p in inventory]
        sel_sku = st.selectbox(T['sku_sel'], sku_list, index=None)
        if sel_sku:
            p_ref = next(i for i in inventory if i['name'] == sel_sku)
            ipc = p_ref.get('itemsPerCase', 1)
            st.markdown(f"<div class='v-status-box'><b>{T['standard']}:</b> {ipc} {T['pcs_unit']}<br><b>{T['rotation']}:</b> {'OK' if p_ref.get('allowRotation') else 'LOCKED'}</div>", unsafe_allow_html=True)
            qty_in = st.number_input(T['qty'], 1, 1000, ipc)
            if st.button(T['append'], type="primary"):
                for _ in range(math.ceil(qty_in/ipc)): st.session_state.v_manifest.append(p_ref.copy())
                st.rerun()
        if st.button(T['purge']): st.session_state.v_manifest = []; st.rerun()

    # --- MAIN DASHBOARD ---
    h_col1, h_col2 = st.columns([5, 1])
    with h_col1:
        l_data = get_b64_asset('logo_vorteza.png')
        if l_data: st.markdown(f'<img src="data:image/png;base64,{l_data}" width="200">', unsafe_allow_html=True)
        else: st.markdown("<h1>VORTEZA STACK</h1>", unsafe_allow_html=True)
    with h_col2:
        if st.button(T['terminate']): st.session_state.authorized = False; st.rerun()

    tab_p, tab_i = st.tabs([f"📊 {T['planner']}", f"📦 {T['inventory']}"])

    with tab_p:
        if st.session_state.v_manifest:
            # DASH KPI
            k1, k2, k3, k4 = st.columns(4)
            t_m = sum(float(u['weight']) for u in st.session_state.v_manifest)
            k1.metric(T['cases'], len(st.session_state.v_manifest))
            k2.metric(T['pcs'], sum(int(u.get('itemsPerCase', 1)) for u in st.session_state.v_manifest))
            k3.metric(T['weight'], f"{t_m} KG")
            k4.metric(T['util'], f"{(t_m/veh['max_w'])*100:.1f}%")

            rem = [dict(u) for u in st.session_state.v_manifest]
            assigned_fleet = []
            while rem:
                s, w, n, l = V32Engine.pack(rem, veh, offset=x_off)
                if not s: break
                assigned_fleet.append({"s": s, "w": w, "l": l})
                rem = n

            for idx, unit in enumerate(assigned_fleet):
                st.markdown(f'<div class="v-tile-pro">', unsafe_allow_html=True)
                st.markdown(f"### MISSION UNIT #{idx+1} | {v_sel}")
                
                v_col, d_col = st.columns([2.8, 1])
                with v_col:
                    st.plotly_chart(render_vorteza_3d_engine(veh, unit['s']), use_container_width=True)
                    # Load Balancer UI
                    tm, tw = 0, 0
                    for s_clust in unit['s']:
                        for i_unit in s_clust['items']: 
                            tm += (s_clust['x']+i_unit['w_fit']/2)*i_unit['weight']
                            tw += i_unit['weight']
                    cog_p = (tm/tw/veh['L'])*100 if tw > 0 else 0
                    st.markdown(f"#### ⚖️ {T['cog']}")
                    st.markdown(f'<div class="v-rail-track"><div class="v-cog-indicator" style="left:{cog_p}%;"></div><div style="position:absolute;left:15px;top:45px;font-size:0.7rem;color:#666;">{T["axle_f"]}</div><div style="position:absolute;right:15px;top:45px;font-size:0.7rem;color:#666;">{T["axle_r"]}</div></div><br>', unsafe_allow_html=True)
                with d_col:
                    st.markdown(f"**{T['kpi']}**")
                    st.write(f"{T['ldm']}: **{unit['l']:.2f} m**")
                    st.write(f"{T['weight']}: **{unit['w']} kg**")
                    st.divider()
                    st.markdown(f"**{T['manifest']}**")
                    # FIX: Ujednolicone klucze aggregacji Pandas
                    agg = pd.Series([it['name'] for s_box in unit['s'] for it in s_box['items']]).value_counts().reset_index()
                    agg.columns = ['SKU', 'QTY']
                    h_table = f'<table class="v-table-tactical"><tr><th>SKU</th><th>{T["qty"]}</th></tr>'
                    for _, row in agg.iterrows():
                        c_hex = get_chromatic_color(row["SKU"])
                        h_table += f'<tr><td><span style="color:{c_hex}">■</span> {row["SKU"]}</td><td>{row["QTY"]}</td></tr>'
                    st.markdown(h_table + '</table>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
        else: st.info("VORTEZA STACK: WAITING FOR MISSION DATA.")

    with tab_i:
        st.markdown(f"### 📦 {T['inventory']}")
        df_inv = pd.DataFrame(inventory)
        if not df_inv.empty:
            edt = st.data_editor(df_inv, use_container_width=True, num_rows="dynamic", key="v32_editor")
            if st.button(T['sync'], type="primary"):
                with open('products.json', 'w', encoding='utf-8') as f: 
                    json.dump(edt.to_dict('records'), f, indent=4, ensure_ascii=False)
                st.success(T['sync_ok'])
        
        st.divider()
        with st.expander(f"➕ {T['new_sku']}"):
            with st.form("AddAsset"):
                fn = st.text_input("SKU Name")
                ci1, ci2, ci3 = st.columns(3)
                fl, fw, fh = ci1.number_input(T['length'], 120), ci2.number_input(T['width'], 80), ci3.number_input(T['height'], 100)
                fm, fi = st.number_input(T['mass_kg'], 50), st.number_input(T['ipu'], 1)
                stk, rot = st.checkbox(T['can_stack'], True), st.checkbox(T['can_rotate'], True)
                if st.form_submit_button("COMMIT"):
                    inventory.append({"name":fn,"length":fl,"width":fw,"height":fh,"weight":fm,"itemsPerCase":fi,"canStack":stk,"allowRotation":rot})
                    with open('products.json', 'w', encoding='utf-8') as f: json.dump(inventory, f, indent=4, ensure_ascii=False)
                    st.rerun()

if __name__ == "__main__": main()
