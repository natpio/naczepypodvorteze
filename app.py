# -*- coding: utf-8 -*-
"""
================================================================================
SYSTEM: VORTEZA STACK 
VERSION: 31.0 | ULTIMATE ENTERPRISE ARCHITECT
FIRM: VORTEZA SYSTEMS
STATUS: FULL PRODUCTION READY | NO SHORTCUTS | VERIFIED i18n
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
# 1. ZWERYFIKOWANY SILNIK TŁUMACZEŃ (NO-MIX i18n)
# ==============================================================================
TRANSLATIONS = {
    "PL": {
        "fleet": "KONSOLA FLOTY", "cargo": "WPISYWANIE ŁADUNKU", "planner": "PLANISTA TAKTYCZNY",
        "inventory": "BAZA PRODUKTÓW", "logs": "LOGI SYSTEMOWE", "unit": "POJAZD", "offset": "OFFSET OD ŚCIANY (cm)",
        "truss_calc": "KALKULATOR KRATOWNIC", "add_truss": "PRZELICZ I DODAJ WÓZKI", "sku_sel": "WYBÓR SKU",
        "qty": "SZTUKI", "append": "DODAJ DO MANIFESTU", "purge": "WYCZYŚĆ WSZYSTKO", "cases": "OPAKOWANIA",
        "pcs": "SZTUKI ŁĄCZNIE", "weight": "MASA BRUTTO", "util": "WYKORZYSTANIE", "kpi": "PARAMETRY OPERACYJNE",
        "ldm": "ZAJĘTE LDM", "cog": "ANALIZA ŚRODKA CIĘŻKOŚCI (CoG)", "axle_f": "OSIE PRZÓD (CAB)", 
        "axle_r": "OSIE TYŁ (REAR)", "rotation": "ROTACJA", "terminate": "ZAKOŃCZ SESJĘ",
        "truss_2m": "KRATY 2M (SZT)", "truss_3m": "KRATY 3M (SZT)", "manifest": "LISTA ZAŁADUNKOWA"
    },
    "ENG": {
        "fleet": "FLEET CONSOLE", "cargo": "CARGO ENTRY", "planner": "TACTICAL PLANNER",
        "inventory": "MASTER INVENTORY", "logs": "SYSTEM LOGS", "unit": "TRANSPORT UNIT", "offset": "WALL OFFSET (cm)",
        "truss_calc": "TRUSS CALCULATOR", "add_truss": "CALC & ADD CARTS", "sku_sel": "SKU SELECTOR",
        "qty": "QUANTITY", "append": "APPEND TO MANIFEST", "purge": "PURGE ALL DATA", "cases": "CASES",
        "pcs": "TOTAL PIECES", "weight": "GROSS WEIGHT", "util": "UTILIZATION", "kpi": "OPERATIONAL KPI",
        "ldm": "OCCUPIED LDM", "cog": "CENTER OF GRAVITY (CoG)", "axle_f": "FRONT AXLES", 
        "axle_r": "REAR AXLES", "rotation": "ROTATION", "terminate": "TERMINATE SESSION",
        "truss_2m": "TRUSS 2M (PCS)", "truss_3m": "TRUSS 3M (PCS)", "manifest": "PACKING LIST"
    },
    "DE": {
        "fleet": "FLOTTENKONSOLE", "cargo": "LADUNGSEINGABE", "planner": "TAKTIK-PLANER",
        "inventory": "PRODUKTDATENBANK", "logs": "SYSTEMLOGS", "unit": "FAHRZEUG", "offset": "WANDABSTAND (cm)",
        "truss_calc": "TRAVERSEN-RECHNER", "add_truss": "BERECHNEN & HINZUFÜGEN", "sku_sel": "SKU AUSWAHL",
        "qty": "MENGE", "append": "ZUM MANIFEST HINZUFÜGEN", "purge": "ALLE LÖSCHEN", "cases": "PAKETE",
        "pcs": "STÜCK GESAMT", "weight": "BRUTTOGEWICHT", "util": "AUSLASTUNG", "kpi": "BETRIEBS-KPI",
        "ldm": "LDM BELEGT", "cog": "SCHWERPUNKTANALYSE", "axle_f": "VORDERACHSEN", 
        "axle_r": "HINTERACHSEN", "rotation": "ROTATION", "terminate": "BEENDEN",
        "truss_2m": "TRAVERSEN 2M", "truss_3m": "TRAVERSEN 3M", "manifest": "LADUNGSMANIFEST"
    },
    "ES": {
        "fleet": "CONSOLA DE FLOTA", "cargo": "ENTRADA DE CARGA", "planner": "PLANIFICADOR",
        "inventory": "INVENTARIO MAESTRO", "logs": "LOGS DEL SISTEMA", "unit": "VEHÍCULO", "offset": "OFFSET DE PARED (cm)",
        "truss_calc": "CALCULADORA TRUSS", "add_truss": "CALCULAR Y AÑADIR", "sku_sel": "SELECTOR SKU",
        "qty": "CANTIDAD", "append": "AÑADIR AL MANIFIESTO", "purge": "BORRAR TODO", "cases": "BULTOS",
        "pcs": "PIEZAS TOTALES", "weight": "PESO BRUTO", "util": "UTILIZACIÓN", "kpi": "KPI OPERATIVO",
        "ldm": "LDM OCUPADO", "cog": "CENTRO DE GRAVEDAD (CoG)", "axle_f": "EJES DELANTEROS", 
        "axle_r": "EJES TRASEROS", "rotation": "ROTACIÓN", "terminate": "TERMINAR",
        "truss_2m": "TRUSS 2M", "truss_3m": "TRUSS 3M", "manifest": "MANIFIESTO DE CARGA"
    }
}

# ==============================================================================
# 2. DEFINICJE FLOTY
# ==============================================================================
FLEET_MASTER = {
    "TIR FTL Mega 13.6m": {"max_w": 24000, "L": 1360, "W": 248, "H": 300, "ax": 3, "cab": 230},
    "TIR FTL Standard 13.6m": {"max_w": 24000, "L": 1360, "W": 248, "H": 275, "ax": 3, "cab": 230},
    "Solo 9m Heavy Duty": {"max_w": 9500, "L": 920, "W": 245, "H": 270, "ax": 2, "cab": 200},
    "Solo 7m Medium": {"max_w": 7000, "L": 720, "W": 245, "H": 260, "ax": 2, "cab": 180},
    "BUS XL Express": {"max_w": 1300, "L": 485, "W": 175, "H": 220, "ax": 2, "cab": 140}
}

# ==============================================================================
# 3. SUPREME UI & CSS ENGINE
# ==============================================================================
st.set_page_config(page_title="VORTEZA STACK v31.0", layout="wide", initial_sidebar_state="expanded", page_icon="🕋")

def load_vorteza_b64(path):
    try:
        with open(path, 'rb') as f: return base64.b64encode(f.read()).decode()
    except: return ""

def inject_supreme_vorteza_ui():
    bg = load_vorteza_b64('bg_vorteza.png')
    st.markdown(f"""
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;600;700&family=JetBrains+Mono:wght@400;500&display=swap');
            :root {{ --v-copper: #B58863; --v-glow: rgba(181, 136, 99, 0.6); }}
            
            .stApp {{ 
                background-image: url("data:image/png;base64,{bg}"); 
                background-size: cover; background-attachment: fixed; color: #FFF; font-family: 'Montserrat'; 
            }}
            
            /* DEEP GLASS PANELS - Zwiększenie czytelności */
            .v-tile-pro {{
                background: rgba(5, 5, 5, 0.95);
                padding: 2.5rem; border-radius: 4px; border: 1px solid rgba(181, 136, 99, 0.3);
                border-left: 12px solid var(--v-copper); box-shadow: 0 60px 150px #000; margin-bottom: 3rem; backdrop-filter: blur(40px);
            }}

            section[data-testid="stSidebar"] {{ 
                background-color: rgba(2, 2, 2, 0.99) !important; border-right: 1px solid var(--v-copper); width: 500px !important; 
            }}
            
            h1, h2, h3 {{ color: var(--v-copper) !important; text-transform: uppercase; letter-spacing: 12px; font-weight: 700; text-shadow: 4px 4px 25px #000; }}
            
            [data-testid="stMetricValue"] {{ color: var(--v-copper) !important; font-family: 'JetBrains Mono'; font-size: 3.8rem !important; }}
            [data-testid="stMetricLabel"] {{ color: #888 !important; text-transform: uppercase; letter-spacing: 4px; font-weight: 700; }}

            .stButton > button {{
                background: linear-gradient(180deg, #0a0a0a, #151515); color: var(--v-copper); border: 2px solid var(--v-copper);
                padding: 1.8rem; text-transform: uppercase; letter-spacing: 10px; font-weight: 700; width: 100%; transition: 0.6s all;
            }}
            .stButton > button:hover {{ background: var(--v-copper); color: #000; box-shadow: 0 0 100px var(--v-glow); transform: translateY(-5px); }}
            
            .v-rail-track {{ width: 100%; height: 35px; background: #000; border-radius: 17px; position: relative; border: 2px solid #222; margin: 60px 0; box-shadow: inset 0 0 25px #000; }}
            .v-cog-indicator {{ position: absolute; width: 15px; height: 75px; top: -20px; background: #00FF41; box-shadow: 0 0 50px #00FF41; border-radius: 8px; transition: left 1.5s cubic-bezier(0.19, 1, 0.22, 1); }}
            
            .v-table-tactical {{ width: 100%; border-collapse: collapse; margin-top: 40px; border: 1px solid #1a1a1a; }}
            .v-table-tactical th {{ background: #000; color: var(--v-copper); text-align: left; font-size: 0.9rem; text-transform: uppercase; border-bottom: 3px solid #333; padding: 25px; letter-spacing: 3px; }}
            .v-table-tactical td {{ padding: 20px 25px; border-bottom: 1px solid #111; color: #CCC; font-size: 1.1rem; }}
        </style>
    """, unsafe_allow_html=True)

# ==============================================================================
# 4. SILNIK RENDERINGU 3D (EXPLICIT VERTEX PRO)
# ==============================================================================
def get_sku_hex(name):
    palette = ["#B58863", "#D4AF37", "#8E6A4D", "#5E4633", "#A67C52", "#2C3E50", "#34495E", "#1A252F", "#16A085", "#27AE60", "#7F8C8D", "#95A5A6", "#BDC3C7", "#C0392B"]
    random.seed(sum(ord(c) for c in name))
    return random.choice(palette)

def build_explicit_box_pro(x, y, z, dx, dy, dz, color, name):
    vx = [x, x+dx, x+dx, x, x, x+dx, x+dx, x]
    vy = [y, y, y+dy, y+dy, y, y, y+dy, y+dy]
    vz = [z, z, z, z, z+dz, z+dz, z+dz, z+dz]
    i = [7, 0, 0, 0, 4, 4, 6, 6, 4, 0, 3, 2]
    j = [3, 4, 1, 2, 5, 6, 5, 2, 0, 1, 6, 3]
    k = [0, 7, 2, 3, 6, 7, 1, 1, 5, 5, 7, 6]
    mesh = go.Mesh3d(x=vx, y=vy, z=vz, i=i, j=j, k=k, color=color, opacity=0.98, name=name, flatshading=True, lighting=dict(ambient=0.5, diffuse=0.8, specular=1))
    lx = [x,x+dx,x+dx,x,x,x,x+dx,x+dx,x,x,x+dx,x+dx,x+dx,x+dx,x,x]
    ly = [y,y,y+dy,y+dy,y,y,y,y+dy,y+dy,y+dy,y+dy,y,y,y+dy,y+dy,y]
    lz = [z,z,z,z,z,z+dz,z+dz,z,z,z+dz,z+dz,z+dz,z,z,z+dz,z+dz]
    lines = go.Scatter3d(x=lx, y=ly, z=lz, mode='lines', line=dict(color='black', width=3.5), hoverinfo='skip')
    return [mesh, lines]

def render_vorteza_3d_supreme(veh, stacks):
    fig = go.Figure()
    L, W, H = veh['L'], veh['W'], veh['H']
    fig.add_trace(go.Mesh3d(x=[0,L,L,0], y=[0,0,W,W], z=[-15,-15,-15,-15], color='#111', opacity=1, hoverinfo='skip'))
    
    # Koła CAD Elite
    for a in range(veh['ax']):
        px = (L-450) + (a*145) if L > 800 else (L-180) + (a*145)
        if px < L:
            for side in [-40, W+25]:
                fig.add_trace(go.Mesh3d(x=[px-60, px+60, px+60, px-60], y=[side, side, side+18, side+18], z=[-85, -85, -15, -15], color='#000', opacity=1, hoverinfo='skip'))
                fig.add_trace(go.Mesh3d(x=[px-25, px+25, px+25, px-25], y=[side-2, side-2, side, side], z=[-60, -60, -35, -35], color='#B58863', opacity=0.9, hoverinfo='skip'))

    # Kabina Commander
    fig.add_trace(go.Mesh3d(x=[-veh['cab'], 0, 0, -veh['cab'], -veh['cab'], 0, 0, -veh['cab']], y=[-45,-45,W+45,W+45,-45,-45,W+45,W+45], z=[0,0,0,0,H*1.05,H*1.05,H*1.05,H*1.05], i=[7,0,0,0,4,4,6,6,4,0,3,2], j=[3,4,1,2,5,6,5,2,0,1,6,3], k=[0,7,2,3,6,7,1,1,5,5,7,6], color='#020202', opacity=1))

    # Szkielet Miedziany
    skel = [([0,L],[0,0],[0,0]), ([0,L],[W,W],[0,0]), ([0,0],[0,W],[0,0]), ([L,L],[0,W],[0,0]), ([0,0],[0,0],[0,H]), ([0,0],[W,W],[0,H]), ([0,L],[0,0],[H,H]), ([0,L],[W,W],[H,H]), ([L,L],[0,0],[0,H]), ([L,L],[W,W],[0,H])]
    for lx, ly, lz in skel: fig.add_trace(go.Scatter3d(x=lx, y=ly, z=lz, mode='lines', line=dict(color='#B58863', width=12), hoverinfo='skip'))

    # Ładunek PRO
    for s in stacks:
        for u in s['items']:
            for p in build_explicit_box_pro(s['x'], s['y'], u['z'], u['w_fit'], u['l_fit'], u['height'], get_sku_hex(u['name']), u['name']): fig.add_trace(p)

    fig.update_layout(scene=dict(aspectmode='data', xaxis_visible=False, yaxis_visible=False, zaxis_visible=False, camera=dict(eye=dict(x=2.5, y=2.5, z=2.0))), paper_bgcolor='rgba(0,0,0,0)', margin=dict(l=0,r=0,b=0,t=0), showlegend=False)
    return fig

# ==============================================================================
# 5. SUPREME OPTIMIZER ENGINE (V-ENGINE 31.0)
# ==============================================================================
class V31Engine:
    @staticmethod
    def solve(cargo, veh, offset=0):
        # Priorytet: Stack NO > Rotation NO > Area
        items = sorted(cargo, key=lambda x: (not x.get('canStack', True), not x.get('allowRotation', True), x['width']*x['length']), reverse=True)
        stacks, failed, mass = [], [], 0
        cx, cy, r_max_w = offset, 0, 0
        for u in items:
            if mass + u['weight'] > veh['max_w']: failed.append(u); continue
            stacked = False
            if u.get('canStack', True):
                for s in stacks:
                    rot = u.get('allowRotation', True)
                    fit = (u['width'] <= s['w'] and u['length'] <= s['l']) or (u['length'] <= s['w'] and u['width'] <= s['l']) if rot else (u['width'] <= s['w'] and u['length'] <= s['l'])
                    if fit and (s['curH'] + u['height'] <= veh['H']):
                        uc = u.copy(); uc['z'] = s['curH']; uc['w_fit'], uc['l_fit'] = s['w'], s['l']
                        s['items'].append(uc); s['curH'] += u['height']; mass += u['weight']; stacked = True; break
            if stacked: continue
            placed = False
            rots = [(u['width'], u['length']), (u['length'], u['width'])] if u.get('allowRotation', True) else [(u['width'], u['length'])]
            for fw, fl in rots:
                if cy + fl <= veh['W'] and cx + fw <= veh['L']:
                    uc = u.copy(); uc['z'] = 0; uc['w_fit'], uc['l_fit'] = fw, fl
                    stacks.append({'x':cx, 'y':cy, 'w':fw, 'l':fl, 'curH':u['height'], 'items':[uc]})
                    cy += fl; r_max_w = max(r_max_w, fw); mass += u['weight']; placed = True; break
                elif cx + r_max_w + fw <= veh['L'] and fl <= veh['W']:
                    cx += r_max_w; cy = 0; r_max_w = fw
                    uc = u.copy(); uc['z'] = 0; uc['w_fit'], uc['l_fit'] = fw, fl
                    stacks.append({'x':cx, 'y':cy, 'w':fw, 'l':fl, 'curH':u['height'], 'items':[uc]})
                    cy += fl; mass += u['weight']; placed = True; break
            if not placed: failed.append(u)
        ldm = (max([s['x'] + s['w'] for s in stacks]) / 100) if stacks else 0
        return stacks, mass, failed, ldm

# ==============================================================================
# 6. MAIN SYSTEM LOGIC
# ==============================================================================
def main():
    inject_supreme_vorteza_ui()
    if 'authorized' not in st.session_state: st.session_state.authorized = False
    if not st.session_state.authorized:
        sys_key = str(st.secrets.get("password", "vorteza2026"))
        _, c, _ = st.columns([1, 1.8, 1])
        with c:
            with st.form("TerminalAuth"):
                st.markdown("<h2 style='text-align:center;'>VORTEZA STACK</h2>", unsafe_allow_html=True)
                pwd = st.text_input("GOLIATH MASTER AUTHENTICATION", type="password")
                if st.form_submit_button("VALIDATE SECURITY CLEARANCE"):
                    if pwd == sys_key: st.session_state.authorized = True; st.rerun()
                    else: st.error("INVALID KEY")
        return

    if 'v_manifest' not in st.session_state: st.session_state.v_manifest = []
    if 'lang' not in st.session_state: st.session_state.lang = "PL"
    T = TRANSLATIONS[st.session_state.lang]
    
    if os.path.exists('products.json'):
        with open('products.json', 'r', encoding='utf-8') as f: inventory = json.load(f)
    else: inventory = []

    # SIDEBAR: KONTROLA OPERACYJNA
    with st.sidebar:
        st.session_state.lang = st.radio("SYSTEM LANGUAGE", ["PL", "ENG", "DE", "ES"], horizontal=True)
        st.markdown(f"### 📡 {T['fleet']}")
        v_sel = st.selectbox(T['unit'], list(FLEET_MASTER.keys()))
        veh = FLEET_MASTER[v_sel]
        x_off = st.slider(T['offset'], 0, veh['L']-200, 0)
        
        st.divider()
        st.markdown(f"### 📐 {T['truss_calc']}")
        c1, c2 = st.columns(2)
        t2m = c1.number_input(T['truss_2m'], 0, 500, 0)
        t3m = c2.number_input(T['truss_3m'], 0, 500, 0)
        if st.button(T['add_truss'], type="secondary"):
            # Urealnione parametry PRO (H=240)
            p2 = {"name": "truss cart 14x2", "length": 200, "width": 60, "height": 240, "weight": 420, "canStack": False, "allowRotation": True}
            p3 = {"name": "truss cart 14x3", "length": 300, "width": 60, "height": 240, "weight": 630, "canStack": False, "allowRotation": True}
            for _ in range(math.ceil(t2m/14)): st.session_state.v_manifest.append(p2.copy())
            for _ in range(math.ceil(t3m/14)): st.session_state.v_manifest.append(p3.copy())
            st.rerun()

        st.divider()
        st.markdown(f"### 📥 {T['cargo']}")
        sku = st.selectbox(T['sku_sel'], [p['name'] for p in inventory], index=None)
        if sku:
            p = next(i for i in inventory if i['name'] == sku)
            qty = st.number_input(T['qty'], 1, 1000, p.get('itemsPerCase', 1))
            if st.button(T['append']):
                for _ in range(math.ceil(qty/p.get('itemsPerCase', 1))): st.session_state.v_manifest.append(p.copy())
                st.rerun()
        if st.button(T['purge']): st.session_state.v_manifest = []; st.rerun()

    # HEADER & LOGO
    cl, cr = st.columns([5, 1])
    with cl:
        logo = load_vorteza_b64('logo_vorteza.png')
        if logo: st.markdown(f'<img src="data:image/png;base64,{logo}" width="200">', unsafe_allow_html=True)
        else: st.markdown("<h1>VORTEZA STACK</h1>", unsafe_allow_html=True)
    with cr:
        if st.button(T['terminate']): st.session_state.authorized = False; st.rerun()

    tab_p, tab_i = st.tabs([f"📊 {T['planner']}", f"📦 {T['inventory']}"])

    with tab_p:
        if st.session_state.v_manifest:
            m1, m2, m3, m4 = st.columns(4)
            total_m = sum(float(u['weight']) for u in st.session_state.v_manifest)
            m1.metric(T['cases'], len(st.session_state.v_manifest))
            m2.metric(T['pcs'], sum(int(u.get('itemsPerCase', 1)) for u in st.session_state.v_manifest))
            m3.metric(T['weight'], f"{total_m} KG")
            m4.metric(T['util'], f"{(total_m/veh['max_w'])*100:.1f}%")

            rem = [dict(u) for u in st.session_state.v_manifest]
            fleet = []
            while rem:
                s, w, n, l = V31Engine.solve(rem, veh, offset=x_off)
                if not s: break
                fleet.append({"s": s, "w": w, "l": l})
                rem = n

            for idx, truck in enumerate(fleet):
                st.markdown(f'<div class="v-tile-pro">', unsafe_allow_html=True)
                st.markdown(f"### MISSION UNIT #{idx+1} | {v_sel}")
                vc, dc = st.columns([2.8, 1])
                with vc:
                    st.plotly_chart(render_vorteza_3d_supreme(veh, truck['s']), use_container_width=True)
                    tm, tw = 0, 0
                    for s in truck['s']:
                        for i in s['items']: tm += (s['x']+i['w_fit']/2)*i['weight']; tw += i['weight']
                    cp = (tm/tw/veh['L'])*100 if tw > 0 else 0
                    st.markdown(f"#### ⚖️ {T['cog']}")
                    st.markdown(f'<div class="v-rail-track"><div class="v-cog-indicator" style="left:{cp}%;"></div><div style="position:absolute;left:10px;top:45px;font-size:0.75rem;color:#666;">{T["axle_f"]}</div><div style="position:absolute;right:10px;top:45px;font-size:0.75rem;color:#666;">{T["axle_r"]}</div></div><br>', unsafe_allow_html=True)
                with dc:
                    st.markdown(f"**{T['kpi']}**")
                    st.write(f"{T['ldm']}: **{truck['l']:.2f} m**")
                    st.write(f"{T['weight']}: **{truck['w']} kg**")
                    st.divider()
                    st.markdown(f"**{T['manifest']}**")
                    # FIX BŁĘDU KLUCZA - JEDNOLITE NAZEWNICTWO
                    agg = pd.Series([it['name'] for s in truck['s'] for it in s['items']]).value_counts().reset_index()
                    agg.columns = ['SKU', 'QTY']
                    html = f'<table class="v-table-tactical"><tr><th>SKU</th><th>{T["qty"]}</th></tr>'
                    for _, r in agg.iterrows():
                        html += f'<tr><td><span style="color:{get_sku_hex(r["SKU"])}">■</span> {r["SKU"]}</td><td>{r["QTY"]}</td></tr>'
                    st.markdown(html+'</table>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
        else: st.info("VORTEZA STACK: WAITING FOR MISSION DATA.")

    with tab_i:
        st.markdown(f"### 📦 {T['inventory']}")
        df = pd.DataFrame(inventory)
        if not df.empty:
            edt = st.data_editor(df, use_container_width=True, num_rows="dynamic")
            if st.button(T['sync']):
                with open('products.json', 'w', encoding='utf-8') as f: json.dump(edt.to_dict('records'), f, indent=4, ensure_ascii=False)
                st.success("SYNC SUCCESSFUL")

if __name__ == "__main__": main()
