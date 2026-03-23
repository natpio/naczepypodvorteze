# -*- coding: utf-8 -*-
"""
================================================================================
SYSTEM: VORTEZA STACK 
VERSION: 30.0 | OMNI SUPREME ARCHITECT
FIRM: VORTEZA SYSTEMS
STATUS: ENTERPRISE PRODUCTION READY | FULL MONOLITH SOURCE
================================================================================
"""

import streamlit as st
import json
import plotly.graph_objects as go
import plotly.express as px
import math
import pandas as pd
import random
import base64
from datetime import datetime
import io
import os
from PIL import Image

# ==============================================================================
# 1. SYSTEM TŁUMACZEŃ (i18n ENGINE)
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
        "standard": "STANDARD", "pcs_unit": "SZT/JEDN", "authorized": "ZAUTORYZOWANO", "locked": "ZABLOKOWANA",
        "oversize": "BŁĄD: TOWAR ZA DUŻY NA POJAZD", "sync_success": "SYNCHRONIZACJA ZAKOŃCZONA SUKCESEM",
        "length": "DŁUGOŚĆ", "width": "SZEROKOŚĆ", "height": "WYSOKOŚĆ", "stacking": "PIĘTROWANIE",
        "add_success": "WÓZKI DODANE DO MANIFESTU"
    },
    "ENG": {
        "fleet": "FLEET CONSOLE", "cargo": "CARGO ENTRY", "planner": "TACTICAL PLANNER",
        "inventory": "MASTER INVENTORY", "logs": "SYSTEM LOGS", "unit": "UNIT", "offset": "WALL OFFSET (cm)",
        "truss_calc": "TRUSS CALCULATOR", "add_truss": "CALC & ADD CARTS", "sku_sel": "SKU SELECTOR",
        "qty": "QUANTITY", "append": "APPEND TO MANIFEST", "purge": "PURGE ALL DATA", "cases": "CASES",
        "pcs": "TOTAL PIECES", "weight": "GROSS WEIGHT", "util": "UTILIZATION", "kpi": "OPERATIONAL KPI",
        "ldm": "LDM OCCUPIED", "cog": "CENTER OF GRAVITY (CoG)", "axle_f": "FRONT AXLES", 
        "axle_r": "REAR AXLES", "rotation": "ROTATION", "auth_req": "AUTHORIZATION REQUIRED",
        "truss_2m": "TRUSS 2M (PCS)", "truss_3m": "TRUSS 3M (PCS)", "manifest": "CARGO MANIFEST",
        "terminate": "TERMINATE SESSION", "sync": "SYNC DATABASE", "new_sku": "REGISTER NEW SKU",
        "standard": "STANDARD", "pcs_unit": "PCS/UNIT", "authorized": "AUTHORIZED", "locked": "LOCKED",
        "oversize": "ERROR: UNIT OVERSIZE FOR FLEET", "sync_success": "DATABASE SYNC SUCCESSFUL",
        "length": "LENGTH", "width": "WIDTH", "height": "HEIGHT", "stacking": "STACKING",
        "add_success": "CARTS ADDED TO MANIFEST"
    },
    "DE": {
        "fleet": "FLOTTENKONSOLE", "cargo": "LADUNGSEINGABE", "planner": "TAKTIK-PLANER",
        "inventory": "PRODUKTDATENBANK", "logs": "SYSTEMPROTOKOLLE", "unit": "FAHRZEUG", "offset": "WANDABSTAND (cm)",
        "truss_calc": "TRUSS-RECHNER", "add_truss": "BERECHNEN & HINZUFÜGEN", "sku_sel": "SKU AUSWAHL",
        "qty": "MENGE", "append": "ZUM MANIFEST HINZUFÜGEN", "purge": "ALLE LÖSCHEN", "cases": "PAKETE",
        "pcs": "STÜCK GESAMT", "weight": "BRUTTOGEWICHT", "util": "AUSLASTUNG", "kpi": "BETRIEBS-KPI",
        "ldm": "LDM BELEGT", "cog": "SCHWERPUNKTANALYSE", "axle_f": "VORDERACHSEN", 
        "axle_r": "HINTERACHSEN", "rotation": "ROTATION", "auth_req": "AUTORISIERUNG ERFORDERLICH",
        "truss_2m": "TRAVERSEN 2M", "truss_3m": "TRAVERSEN 3M", "manifest": "LADUNGSMANIFEST",
        "terminate": "SITZUNG BEENDEN", "sync": "SYNC DATENBANK", "new_sku": "NEUES SKU",
        "standard": "STANDARD", "pcs_unit": "STK/UNIT", "authorized": "AUTORISIERT", "locked": "GESPERRT",
        "oversize": "FEHLER: EINHEIT ZU GROSS", "sync_success": "DATENBANK SYNC ERFOLGREICH",
        "length": "LÄNGE", "width": "BREITE", "height": "HÖHE", "stacking": "STAPELUNG",
        "add_success": "WAGEN ZUM MANIFEST HINZUGEFÜGT"
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
        "terminate": "TERMINAR SESIÓN", "sync": "SINCRONIZAR BASE", "new_sku": "REGISTRAR SKU",
        "standard": "ESTÁNDAR", "pcs_unit": "PZAS/UNID", "authorized": "AUTORIZADO", "locked": "BLOQUEADO",
        "oversize": "ERROR: UNIDAD SOBREDIMENSIONADA", "sync_success": "SYNC DE BASE EXITOSA",
        "length": "LONGITUD", "width": "ANCHO", "height": "ALTURA", "stacking": "APILAMIENTO",
        "add_success": "CARROS AÑADIDOS AL MANIFIESTO"
    }
}

# ==============================================================================
# 2. DEFINICJE TECHNICZNE FLOTY
# ==============================================================================
FLEET_MASTER_REGISTRY = {
    "TIR FTL Mega 13.6m": {"max_w": 24000, "L": 1360, "W": 248, "H": 300, "ldm": 13.6, "ax": 3, "cab": 230},
    "TIR FTL Standard 13.6m": {"max_w": 24000, "L": 1360, "W": 248, "H": 275, "ldm": 13.6, "ax": 3, "cab": 230},
    "Solo 9m Heavy Duty": {"max_w": 9500, "L": 920, "W": 245, "H": 270, "ldm": 9.2, "ax": 2, "cab": 200},
    "Solo 7m Medium": {"max_w": 7000, "L": 720, "W": 245, "H": 260, "ldm": 7.2, "ax": 2, "cab": 180},
    "BUS XL Express": {"max_w": 1300, "L": 485, "W": 175, "H": 220, "ldm": 4.8, "ax": 2, "cab": 140}
}

# ==============================================================================
# 3. BRANDING & GLASS UI ENGINE
# ==============================================================================
def get_resource_b64(path):
    """Bezpieczne ładowanie zasobów binarnych."""
    try:
        if os.path.exists(path):
            with open(path, 'rb') as f: return base64.b64encode(f.read()).decode()
        return ""
    except: return ""

def inject_vorteza_supreme_style():
    """Wstrzykuje zaawansowany arkusz stylów CSS VORTEZA STACK."""
    bg_b64 = get_resource_b64('bg_vorteza.png')
    
    st.markdown(f"""
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;600;700&family=JetBrains+Mono:wght@300;400;500&display=swap');
            
            :root {{
                --v-copper: #B58863;
                --v-copper-glow: rgba(181, 136, 99, 0.5);
                --v-dark-obsidian: #010101;
                --v-panel-bg: rgba(8, 8, 8, 0.94);
                --v-border: rgba(181, 136, 99, 0.25);
                --v-neon-green: #00FF41;
            }}

            /* Global Viewport */
            .stApp {{
                background-image: url("data:image/png;base64,{bg_b64}");
                background-size: cover;
                background-attachment: fixed;
                color: #FFFFFF;
                font-family: 'Montserrat', sans-serif;
            }}

            /* Glassmorphism Tile Architecture */
            .v-tile-apex {{
                background: var(--v-panel-bg);
                padding: 2.5rem;
                border: 1px solid var(--v-border);
                border-left: 10px solid var(--v-copper);
                box-shadow: 0 50px 100px #000;
                margin-bottom: 3rem;
                backdrop-filter: blur(30px);
            }}

            /* Sidebar Technical Panel */
            section[data-testid="stSidebar"] {{
                background-color: rgba(3, 3, 3, 0.99) !important;
                border-right: 1px solid var(--v-border);
                width: 500px !important;
                backdrop-filter: blur(40px);
            }}

            /* Headlines */
            h1, h2, h3 {{ 
                color: var(--v-copper) !important; 
                text-transform: uppercase; 
                letter-spacing: 12px !important; 
                font-weight: 700 !important; 
                text-shadow: 2px 2px 20px #000;
            }}

            /* Metric Pro Visualization */
            [data-testid="stMetricValue"] {{ 
                color: var(--v-copper) !important; 
                font-family: 'JetBrains Mono', monospace !important; 
                font-size: 3.6rem !important;
            }}
            [data-testid="stMetricLabel"] {{
                color: #888 !important;
                text-transform: uppercase;
                letter-spacing: 4px;
                font-weight: 700;
            }}

            /* Interactive Master Controls */
            .stButton > button {{
                background: linear-gradient(180deg, #0a0a0a, #1a1a1a);
                color: var(--v-copper);
                border: 2px solid var(--v-copper);
                padding: 1.6rem;
                text-transform: uppercase;
                letter-spacing: 8px;
                font-weight: 700;
                width: 100%;
                transition: 0.6s all cubic-bezier(0.19, 1, 0.22, 1);
                border-radius: 0;
            }}
            .stButton > button:hover {{
                background: var(--v-copper);
                color: #000;
                box-shadow: 0 0 100px var(--v-copper-glow);
                transform: translateY(-5px);
            }}

            /* Tactical Data Tables */
            .v-table-tactical {{ 
                width: 100%; 
                border-collapse: collapse; 
                margin-top: 40px; 
                border: 1px solid #111;
            }}
            .v-table-tactical th {{ 
                background: #000;
                color: var(--v-copper); 
                text-align: left; 
                font-size: 0.85rem; 
                text-transform: uppercase; 
                border-bottom: 3px solid #333; 
                padding: 25px; 
                letter-spacing: 3px;
            }}
            .v-table-tactical td {{ 
                padding: 20px 25px; 
                border-bottom: 1px solid #111; 
                color: #CCC; 
                font-size: 1rem; 
            }}
            .v-table-tactical tr:hover {{ background: rgba(181,136,99,0.06); }}

            /* Load Balancer Visualization */
            .v-rail-track {{
                width: 100%; height: 35px; background: #050505; border-radius: 17px; position: relative; border: 2px solid #222; margin: 60px 0;
                box-shadow: inset 0 0 30px #000;
            }}
            .v-cog-pointer {{
                position: absolute; width: 12px; height: 75px; top: -20px; background: var(--v-neon-green); 
                box-shadow: 0 0 45px var(--v-neon-green); border-radius: 6px;
                transition: left 1.2s cubic-bezier(0.19, 1, 0.22, 1);
            }}
            
            /* Status Badges */
            .v-badge-pro {{
                background: rgba(181,136,99,0.1);
                border: 1px solid var(--v-copper);
                padding: 18px;
                font-family: 'JetBrains Mono', monospace;
                font-size: 0.8rem;
                margin-bottom: 25px;
            }}

            /* Data Editor UI */
            div[data-testid="stDataEditor"] {{
                background: rgba(10,10,10,0.95) !important;
                border: 1px solid var(--v-border) !important;
            }}
        </style>
    """, unsafe_allow_html=True)

# ==============================================================================
# 4. KONTROLA DOSTĘPU (SECURITY GATEWAY)
# ==============================================================================
def check_authorized_access():
    """Weryfikuje poświadczenia operatora systemu VORTEZA STACK."""
    if "authorized" not in st.session_state:
        st.session_state.authorized = False

    if not st.session_state.authorized:
        try:
            sys_key = str(st.secrets.get("password", "vorteza2026"))
        except:
            sys_key = "vorteza2026"

        st.markdown("<br><br><br><br><br><br><br>", unsafe_allow_html=True)
        _, col_auth, _ = st.columns([1, 2.5, 1])
        with col_auth:
            with st.form("VortezaAuthGate"):
                st.markdown("<h2 style='text-align:center;'>VORTEZA STACK</h2>", unsafe_allow_html=True)
                st.markdown("<p style='text-align:center; color:#333; font-size:0.75rem; letter-spacing:6px;'>ENCRYPTED COMMAND TERMINAL</p>", unsafe_allow_html=True)
                pwd_in = st.text_input("GOLIATH CORE AUTHENTICATION", type="password")
                if st.form_submit_button("VALIDATE SECURITY CLEARANCE"):
                    if pwd_in == sys_key:
                        st.session_state.authorized = True
                        st.rerun()
                    else:
                        st.error("ACCESS DENIED: INVALID KEY DETECTED")
        return False
    return True

# ==============================================================================
# 5. RENDERER CAD-3D STACK (EXPLICIT VERTEX ENGINE v30.0)
# ==============================================================================
def get_chromatic_sku_color(sku_name):
    """Zwraca unikalny kolor metaliczny dla każdego SKU."""
    palette = ["#B58863", "#D4AF37", "#8E6A4D", "#5E4633", "#A67C52", "#2C3E50", "#34495E", "#1A252F", "#16A085", "#27AE60", "#7F8C8D", "#95A5A6", "#BDC3C7", "#C0392B"]
    random.seed(sum(ord(c) for c in sku_name))
    return random.choice(palette)

def build_explicit_cube_mesh(x, y, z, dx, dy, dz, color, name):
    """Generuje matematycznie precyzyjną siatkę wierzchołków bryły dla Plotly."""
    # 8 Wierzchołków bryły
    vx = [x, x+dx, x+dx, x, x, x+dx, x+dx, x]
    vy = [y, y, y+dy, y+dy, y, y, y+dy, y+dy]
    vz = [z, z, z, z, z+dz, z+dz, z+dz, z+dz]
    
    # 12 Trójkątów tworzących 6 ścian
    i = [7, 0, 0, 0, 4, 4, 6, 6, 4, 0, 3, 2]
    j = [3, 4, 1, 2, 5, 6, 5, 2, 0, 1, 6, 3]
    k = [0, 7, 2, 3, 6, 7, 1, 1, 5, 5, 7, 6]
    
    mesh = go.Mesh3d(
        x=vx, y=vy, z=vz, i=i, j=j, k=k,
        color=color, opacity=0.98, name=name,
        flatshading=True, lighting=dict(ambient=0.5, diffuse=0.8, specular=1),
        hovertemplate=f"<b>{name}</b><br>D: {dx}cm W: {dy}cm H: {dz}cm<extra></extra>"
    )
    
    # Krawędzie (Edge detection outline)
    lx = [x,x+dx,x+dx,x,x,x,x+dx,x+dx,x,x,x+dx,x+dx,x+dx,x+dx,x,x]
    ly = [y,y,y+dy,y+dy,y,y,y,y+dy,y+dy,y+dy,y+dy,y,y,y+dy,y+dy,y]
    lz = [z,z,z,z,z,z+dz,z+dz,z,z,z+dz,z+dz,z+dz,z,z,z+dz,z+dz]
    
    lines = go.Scatter3d(x=lx, y=ly, z=lz, mode='lines', line=dict(color='black', width=3.5), hoverinfo='skip')
    return [mesh, lines]

def render_vorteza_cad_3d(vehicle_specs, cargo_stacks):
    """Generuje kompletny inżynieryjny model 3D naczepy wraz z ładunkiem."""
    fig = go.Figure()
    L, W, H = vehicle_specs['L'], vehicle_specs['W'], vehicle_specs['H']

    # Podłoga naczepy
    fig.add_trace(go.Mesh3d(x=[0, L, L, 0], y=[0, 0, W, W], z=[-15, -15, -15, -15], color='#111111', opacity=1, hoverinfo='skip'))
    
    # Koła i Osie CAD
    ax_count = vehicle_specs.get('ax', 3)
    rear_base_x = L - 450 if L > 800 else L - 180
    for a in range(ax_count):
        px = rear_base_x + (a * 145)
        if px < L:
            for side in [-40, W+25]:
                fig.add_trace(go.Mesh3d(x=[px-60, px+60, px+60, px-60], y=[side, side, side+18, side+18], z=[-85, -85, -15, -15], color='#000', opacity=1, hoverinfo='skip'))
                fig.add_trace(go.Mesh3d(x=[px-25, px+25, px+25, px-25], y=[side-2, side-2, side, side], z=[-60, -60, -35, -35], color='#B58863', opacity=0.9, hoverinfo='skip'))

    # Kabina Commander
    cab_l = vehicle_specs.get('cab', 230)
    fig.add_trace(go.Mesh3d(x=[-cab_l, 0, 0, -cab_l, -cab_l, 0, 0, -cab_l], y=[-45, -45, W+45, W+45], z=[0, 0, 0, 0, H*1.05, H*1.05, H*1.05, H*1.05], i=[7,0,0,0,4,4,6,6,4,0,3,2], j=[3,4,1,2,5,6,5,2,0,1,6,3], k=[0,7,2,3,6,7,1,1,5,5,7,6], color='#050505', opacity=1))

    # Klatka Miedziana
    skel = [([0, L], [0, 0], [0, 0]), ([0, L], [W, W], [0, 0]), ([0, 0], [0, W], [0, 0]), ([L, L], [0, W], [0, 0]),
            ([0, 0], [0, 0], [0, H]), ([0, 0], [W, W], [0, H]), ([0, L], [0, 0], [H, H]), ([0, L], [W, W], [H, H])]
    for lx, ly, lz in skel:
        fig.add_trace(go.Scatter3d(x=lx, y=ly, z=lz, mode='lines', line=dict(color='#B58863', width=12), hoverinfo='skip'))

    # Render Ładunku
    for cluster in cargo_stacks:
        for unit in cluster['items']:
            clr = get_chromatic_sku_color(unit['name'])
            box_parts = build_explicit_cube_mesh(cluster['x'], cluster['y'], unit['z'], unit['w_fit'], unit['l_fit'], unit['height'], clr, unit['name'])
            for part in box_parts: fig.add_trace(part)

    fig.update_layout(scene=dict(aspectmode='data', xaxis_visible=False, yaxis_visible=False, zaxis_visible=False, camera=dict(eye=dict(x=2.5, y=2.5, z=2.0))), paper_bgcolor='rgba(0,0,0,0)', margin=dict(l=0, r=0, b=0, t=0), showlegend=False)
    return fig

# ==============================================================================
# 6. SILNIK PAKOWANIA V-ENGINE 30.0 (OMNI OPTIMIZER)
# ==============================================================================
class V30SupremeEngine:
    """Zaawansowany algorytm bin-packingu 3D z kontrolą V-PERMIT i balansem X."""
    
    @staticmethod
    def execute_solve(cargo, vehicle, x_offset=0):
        # Priorytetyzacja FFD: 1. No-Stack, 2. No-Rotation, 3. Pole Powierzchni
        items_sorted = sorted(cargo, key=lambda x: (not x.get('canStack', True), not x.get('allowRotation', True), x['width']*x['length']), reverse=True)
        placed_stacks, failed, mass_acc = [], [], 0
        cx, cy, current_row_max_w = x_offset, 0, 0

        for unit in items_sorted:
            if mass_acc + unit['weight'] > vehicle['max_w']:
                failed.append(unit); continue
            
            # Protokół Stacking
            integrated = False
            if unit.get('canStack', True):
                for s in placed_stacks:
                    rot_p = unit.get('allowRotation', True)
                    fit = (unit['width'] <= s['w'] and unit['length'] <= s['l']) or (unit['length'] <= s['w'] and unit['width'] <= s['l']) if rot_p else (unit['width'] <= s['w'] and unit['length'] <= s['l'])
                    if fit and (s['curH'] + unit['height'] <= vehicle['H']):
                        uc = unit.copy(); uc['z'] = s['curH']; uc['w_fit'], uc['l_fit'] = s['w'], s['l']
                        s['items'].append(uc); s['curH'] += unit['height']; mass_acc += unit['weight']; integrated = True; break
            
            if integrated: continue

            # Protokół Podłoga
            placed_on_floor = False
            orientations = [(unit['width'], unit['length']), (unit['length'], unit['width'])] if unit.get('allowRotation', True) else [(unit['width'], unit['length'])]
            for fw, fl in orientations:
                if cy + fl <= vehicle['W'] and cx + fw <= vehicle['L']:
                    uc = unit.copy(); uc['z'] = 0; uc['w_fit'], uc['l_fit'] = fw, fl
                    placed_stacks.append({'x':cx, 'y':cy, 'w':fw, 'l':fl, 'curH':unit['height'], 'items':[uc]})
                    cy += fl; current_row_max_w = max(current_row_max_w, fw); mass_acc += unit['weight']; placed_on_floor = True; break
                elif cx + current_row_max_w + fw <= vehicle['L'] and fl <= vehicle['W']:
                    cx += current_row_max_w; cy = 0; current_row_max_w = fw
                    uc = unit.copy(); uc['z'] = 0; uc['w_fit'], uc['l_fit'] = fw, fl
                    placed_stacks.append({'x':cx, 'y':cy, 'w':fw, 'l':fl, 'curH':unit['height'], 'items':[uc]})
                    cy += fl; mass_acc += unit['weight']; placed_on_floor = True; break
            
            if not placed_on_floor: failed.append(unit)
        
        ldm_real = (max([s['x'] + s['w'] for s in placed_stacks]) / 100) if placed_stacks else 0
        return placed_stacks, mass_acc, failed, ldm_real

# ==============================================================================
# 7. ANALITYKA INŻYNIERYJNA (CoG)
# ==============================================================================
def render_load_balancer_analysis(veh, stacks, T):
    if not stacks: return
    t_mom, t_w = 0, 0
    for s in stacks:
        for it in s['items']:
            t_mom += (s['x'] + it['w_fit']/2) * it['weight']
            t_w += it['weight']
    cog_p = (t_mom / t_w / veh['L']) * 100 if t_w > 0 else 0
    st.markdown(f"### ⚖️ {T['cog']}")
    clr = "#00FF41" if 35 < cog_p < 65 else "#FF3131"
    st.markdown(f"""
        <div class="v-rail-track">
            <div class="v-cog-pointer" style="left:{cog_p}%; background:{clr}; box-shadow:0 0 45px {clr};"></div>
            <div style="position:absolute;left:20px;top:45px;font-size:0.7rem;color:#666;">{T['axle_f']}</div>
            <div style="position:absolute;right:20px;top:45px;font-size:0.7rem;color:#666;">{T['axle_r']}</div>
        </div>
        <br>
    """, unsafe_allow_html=True)

# ==============================================================================
# 8. DATA PERSISTENCE
# ==============================================================================
def db_load_vorteza():
    if os.path.exists('products.json'):
        try:
            with open('products.json', 'r', encoding='utf-8') as f: return json.load(f)
        except: return []
    return []

def db_save_vorteza(data):
    with open('products.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

# ==============================================================================
# 9. GŁÓWNA ARCHITEKTURA INTERFEJSU (VORTEZA STACK)
# ==============================================================================
def main():
    inject_vorteza_supreme_style()
    if not check_authorized_access(): return

    if 'v_manifest' not in st.session_state: st.session_state.v_manifest = []
    if 'lang' not in st.session_state: st.session_state.lang = "PL"
    T = TRANSLATIONS[st.session_state.lang]
    inventory = db_load_vorteza()

    # TOP CONTROL NAVBAR
    hc1, hc2, hc3 = st.columns([1, 4, 1])
    with hc1:
        logo_data = get_resource_b64('logo_vorteza.png')
        if logo_data: st.markdown(f'<img src="data:image/png;base64,{logo_data}" width="180">', unsafe_allow_html=True)
        else: st.markdown("### VORTEZA")
    with hc2:
        st.markdown(f"<h1>VORTEZA STACK</h1>")
        st.markdown(f"<p style='color:#444; font-size:0.75rem; letter-spacing:8px;'>v30.0 OMNI SUPREME ARCHITECT | STATUS: ACTIVE</p>", unsafe_allow_html=True)
    with hc3:
        if st.button(T['terminate']): st.session_state.authorized = False; st.rerun()

    # SIDEBAR MISSION CONTROL
    with st.sidebar:
        st.session_state.lang = st.radio("INTERFACE LANGUAGE", ["PL", "ENG", "DE", "ES"], horizontal=True)
        st.markdown(f"### 📡 {T['fleet']}")
        v_key = st.selectbox(T['unit'], list(FLEET_MASTER_REGISTRY.keys()))
        veh = FLEET_MASTER_REGISTRY[v_key]
        x_off_val = st.slider(T['offset'], 0, veh['L']-200, 0)
        
        st.divider()
        st.markdown(f"### 📐 {T['truss_calc']}")
        c_t1, c_t2 = st.columns(2)
        t2m = c_t1.number_input(T['truss_2m'], 0, 400, 0)
        t3m = c_t2.number_input(T['truss_3m'], 0, 400, 0)
        if st.button(T['add_truss'], type="secondary"):
            # Urealnione wymiary: H=240, canStack=False
            p51 = {"name": "truss cart 14x2", "length": 200, "width": 60, "height": 240, "weight": 420, "canStack": False, "allowRotation": True}
            p52 = {"name": "truss cart 14x3", "length": 300, "width": 60, "height": 240, "weight": 630, "canStack": False, "allowRotation": True}
            for _ in range(math.ceil(t2m/14)): st.session_state.v_manifest.append(p51.copy())
            for _ in range(math.ceil(t3m/14)): st.session_state.v_manifest.append(p52.copy())
            st.toast(T['add_success'])

        st.divider()
        st.markdown(f"### 📥 {T['cargo']}")
        sku_list = [p['name'] for p in inventory]
        sel_sku = st.selectbox(T['sku_sel'], sku_list, index=None)
        if sel_sku:
            p_ref = next(p for p in inventory if p['name'] == sel_sku)
            ipc = p_ref.get('itemsPerCase', 1)
            st.markdown(f"<div class='v-badge-pro'><b>{T['standard']}:</b> {ipc} {T['pcs_unit']}<br><b>{T['rotation']}:</b> {'AUTHORIZED' if p_ref.get('allowRotation') else 'LOCKED'}</div>", unsafe_allow_html=True)
            qty_in = st.number_input(T['qty'], min_value=1, value=ipc)
            if st.button(T['append'], type="primary"):
                for i in range(math.ceil(qty_in / ipc)): st.session_state.v_manifest.append(p_ref.copy())
                st.rerun()
        if st.button(T['purge']): st.session_state.v_manifest = []; st.rerun()

    # WORKSPACE TABS
    tab_p, tab_i, tab_l = st.tabs([f"📊 {T['planner']}", f"📦 {T['inventory']}", f"⚙️ {T['logs']}"])

    with tab_p:
        if st.session_state.v_manifest:
            # Global Metrics Header
            k1, k2, k3, k4 = st.columns(4)
            total_mass = sum(float(u['weight']) for u in st.session_state.v_manifest)
            k1.metric(T['cases'], len(st.session_state.v_manifest))
            k2.metric(T['pcs'], sum(int(u.get('itemsPerCase', 1)) for u in st.session_state.v_manifest))
            k3.metric(T['weight'], f"{total_mass} KG")
            k4.metric(T['util'], f"{(total_mass/veh['max_w'])*100:.1f}%")

            # Packing Engine Run
            rem_units = [dict(u) for u in st.session_state.v_manifest]
            fleet_allocation = []
            while rem_units:
                res_s, res_w, n_p, ldm_r = V30SupremeEngine.execute_solve(rem_units, veh, x_offset=x_off_val)
                if not res_s: st.error(T['oversize']); break
                fleet_allocation.append({"s": res_s, "w": res_w, "l": ldm_r})
                rem_units = n_p

            # Rendering Results
            for idx, truck in enumerate(fleet_allocation):
                st.markdown(f'<div class="v-tile-apex">', unsafe_allow_html=True)
                st.markdown(f"### MISSION UNIT #{idx+1} | {v_key}")
                v_col, d_col = st.columns([2.8, 1])
                with v_col:
                    st.plotly_chart(render_vorteza_cad_3d(veh, truck['s']), use_container_width=True)
                    render_load_balancer_analysis(veh, truck['s'], T)
                with d_col:
                    st.markdown(f"**{T['kpi']}**")
                    st.write(f"{T['ldm']}: **{truck['l']:.2f} m**")
                    st.write(f"{T['weight']}: **{truck['w']} kg**")
                    st.divider()
                    st.markdown(f"**{T['manifest']}**")
                    sku_agg = pd.Series([it['name'] for s in truck['s'] for it in s['items']]).value_counts().reset_index()
                    sku_agg.columns = ['SKU', 'QTY']
                    h_table = f'<table class="v-table-tactical"><tr><th>SKU</th><th>{T["qty"]}</th></tr>'
                    for _, r in sku_agg.iterrows():
                        h_table += f'<tr><td><span style="color:{get_chromatic_sku_color(r["SKU"])}">■</span> {r["SKU"]}</td><td>{r["QTY"]}</td></tr>'
                    st.markdown(h_table + '</table>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
        else: st.info("VORTEZA STACK: WAITING FOR MISSION DATA.")

    with tab_i:
        st.markdown(f"### 📦 {T['inventory']}")
        df_inv = pd.DataFrame(inventory)
        if not df_inv.empty:
            edt_db = st.data_editor(df_inv, use_container_width=True, num_rows="dynamic", key="v30_editor")
            if st.button(T['sync'], type="primary"):
                db_save_vorteza(edt_db.to_dict('records')); st.success(T['sync_success'])
        
        st.divider()
        with st.expander(f"➕ {T['new_sku']}"):
            with st.form("AddAssetSupreme"):
                fn = st.text_input("SKU Name")
                ci1, ci2, ci3 = st.columns(3)
                fl, fw, fh = ci1.number_input(T['length'], 120), ci2.number_input(T['width'], 80), ci3.number_input(T['height'], 100)
                fm, fi = st.number_input(T['weight'], 50), st.number_input(T['pcs_unit'], 1)
                ca1, ca2 = st.columns(2)
                fs, fr = ca1.checkbox(T['stacking'], True), ca2.checkbox(T['rotation'], True)
                if st.form_submit_button("COMMIT TO MASTER DB"):
                    inventory.append({"name":fn,"length":fl,"width":fw,"height":fh,"weight":fm,"itemsPerCase":fi,"canStack":fs,"allowRotation":fr})
                    db_save_vorteza(inventory); st.rerun()

    with tab_l:
        st.code(f"SYSTEM: VORTEZA STACK v30.0\nCORE: APEX-SUPREME-OPTIMIZER\nSESSION: {datetime.now()}\nSTATUS: Nominal", language="bash")

if __name__ == "__main__": main()
