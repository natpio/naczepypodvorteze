# -*- coding: utf-8 -*-
"""
================================================================================
SYSTEM: VORTEZA STACK 
VERSION: 24.0 | APEX ULTIMATE PLUS
FIRM: VORTEZA SYSTEMS
STATUS: ENTERPRISE PRODUCTION READY | FULL MONOLITH SOURCE
================================================================================
"""

import streamlit as st
import json
import plotly.graph_objects as go
import pandas as pd
import math
import random
import base64
from datetime import datetime
import os

# ==============================================================================
# 0. MULTILINGUAL ENGINE (V-LANG)
# ==============================================================================
LANGUAGES = {
    "PL": {
        "title": "VORTEZA STACK", "fleet": "KONSOLA FLOTY", "unit": "JEDNOSTKA TRANSPORTOWA",
        "offset": "OFFSET OD ŚCIANY (cm)", "cargo": "WEJŚCIE ŁADUNKU", "sku_sel": "WYBÓR SKU",
        "qty": "ILOŚĆ (SZTUKI)", "add": "DODAJ DO MANIFESTU", "purge": "WYCZYŚĆ DANE",
        "manifest": "MANIFEST ZAŁADUNKOWY", "edit_m": "EDYCJA MANIFESTU", "cases": "OPAKOWANIA",
        "pcs": "SZTUKI ŁĄCZNIE", "weight": "WAGA BRUTTO", "util": "WYKORZYSTANIE",
        "cog": "ANALIZA ŚRODKA CIĘŻKOŚCI", "mission": "JEDNOSTKA MISJI", "l_auth": "OBRÓT: AUTORYZOWANY",
        "l_lock": "OBRÓT: ZABLOKOWANY", "no_data": "STATUS: OCZEKIWANIE NA DANE",
        "update": "AKTUALIZUJ MANIFEST", "terminate": "WYLOGUJ", "inventory": "BAZA SKU",
        "logs": "LOGI SYSTEMOWE", "kpi": "WSKAŹNIKI KPI"
    },
    "ENG": {
        "title": "VORTEZA STACK", "fleet": "FLEET CONSOLE", "unit": "TRANSPORT UNIT",
        "offset": "WALL OFFSET (cm)", "cargo": "CARGO ENTRY", "sku_sel": "SKU SELECTOR",
        "qty": "QUANTITY (TOTAL PCS)", "add": "APPEND TO MANIFEST", "purge": "PURGE ALL DATA",
        "manifest": "LOAD MANIFEST", "edit_m": "EDIT MANIFEST", "cases": "CASES",
        "pcs": "TOTAL PCS", "weight": "GROSS WEIGHT", "util": "UTILIZATION",
        "cog": "CENTER OF GRAVITY ANALYSIS", "mission": "MISSION UNIT", "l_auth": "ROTATION: AUTHORIZED",
        "l_lock": "ROTATION: LOCKED", "no_data": "STATUS: WAITING FOR MISSION DATA",
        "update": "UPDATE MANIFEST", "terminate": "TERMINATE", "inventory": "MASTER INVENTORY",
        "logs": "SYSTEM LOGS", "kpi": "OPERATIONAL KPI"
    },
    "ES": {
        "title": "VORTEZA STACK", "fleet": "CONSOLA DE FLOTA", "unit": "UNIDAD DE TRANSPORTE",
        "offset": "DESPLAZAMIENTO (cm)", "cargo": "ENTRADA DE CARGA", "sku_sel": "SELECTOR DE SKU",
        "qty": "CANTIDAD (PIEZAS)", "add": "AÑADIR AL MANIFIESTO", "purge": "LIMPIAR DATOS",
        "manifest": "MANIFIESTO DE CARGA", "edit_m": "EDITAR MANIFIESTO", "cases": "CAJAS",
        "pcs": "PIEZAS TOTALES", "weight": "PESO BRUTO", "util": "UTILIZACIÓN",
        "cog": "ANÁLISIS DEL CENTRO DE GRAVEDAD", "mission": "UNIDAD DE MISIÓN", "l_auth": "GIRO: AUTORIZADO",
        "l_lock": "GIRO: BLOQUEADO", "no_data": "ESTADO: ESPERANDO DATOS",
        "update": "ACTUALIZAR MANIFIESTO", "terminate": "SALIR", "inventory": "INVENTARIO",
        "logs": "REGISTROS", "kpi": "KPI OPERATIVO"
    },
    "DE": {
        "title": "VORTEZA STACK", "fleet": "FLOTTENKONSOLE", "unit": "TRANSPORTEINHEIT",
        "offset": "WANDABSTAND (cm)", "cargo": "LADUNGSEINGABE", "sku_sel": "SKU-AUSWAHL",
        "qty": "MENGE (STÜCK)", "add": "ZUM MANIFEST HINZUFÜGEN", "purge": "DATEN LÖSCHEN",
        "manifest": "LADEMANIFEST", "edit_m": "MANIFEST BEARBEITEN", "cases": "KARTONS",
        "pcs": "STÜCK GESAMT", "weight": "BRUTTOGEWICHT", "util": "AUSLASTUNG",
        "cog": "SCHWERPUNKTSANALYSE", "mission": "MISSIONSEINHEIT", "l_auth": "ROTATION: ERLAUBT",
        "l_lock": "ROTATION: GESPERRT", "no_data": "STATUS: WARTE AUF DATEN",
        "update": "MANIFEST AKTUALISIEREN", "terminate": "BEENDEN", "inventory": "INVENTAR",
        "logs": "SYSTEMPROTOKOLLE", "kpi": "BETRIEBS-KPI"
    }
}

# ==============================================================================
# 1. ŚRODOWISKO I REJESTR INŻYNIERYJNY FLOTY
# ==============================================================================
st.set_page_config(
    page_title="VORTEZA STACK v24.0",
    layout="wide",
    initial_sidebar_state="expanded",
    page_icon="🕋"
)

FLEET_MASTER_DATA = {
    "TIR FTL Mega 13.6m": {
        "max_w": 24000, "L": 1360, "W": 248, "H": 300, 
        "ldm_max": 13.6, "axles": 3, "wheelbase": 850, "tare": 14500, "cab_l": 230
    },
    "TIR FTL Standard 13.6m": {
        "max_w": 24000, "L": 1360, "W": 248, "H": 275, 
        "ldm_max": 13.6, "axles": 3, "wheelbase": 850, "tare": 13800, "cab_l": 230
    },
    "Solo 9m Heavy Duty": {
        "max_w": 9500, "L": 920, "W": 245, "H": 270, 
        "ldm_max": 9.2, "axles": 2, "wheelbase": 550, "tare": 8500, "cab_l": 200
    },
    "Solo 7m Medium": {
        "max_w": 7000, "L": 720, "W": 245, "H": 260, 
        "ldm_max": 7.2, "axles": 2, "wheelbase": 480, "tare": 6200, "cab_l": 180
    },
    "BUS XL Express": {
        "max_w": 1300, "L": 485, "W": 175, "H": 220, 
        "ldm_max": 4.8, "axles": 2, "wheelbase": 320, "tare": 2250, "cab_l": 140
    }
}

# ==============================================================================
# 2. BRANDING VORTEZA & UI ENGINE
# ==============================================================================
def inject_vorteza_stack_ui():
    st.markdown(f"""
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;600;700&family=JetBrains+Mono:wght@300;400;500&display=swap');
            :root {{
                --v-copper: #B58863;
                --v-panel-bg: rgba(6, 6, 6, 0.98);
                --v-border: rgba(181, 136, 99, 0.2);
            }}
            .stApp {{ background-color: #050505; color: #FFFFFF; font-family: 'Montserrat', sans-serif; }}
            .v-tile-apex {{
                background: var(--v-panel-bg); padding: 2.5rem; border: 1px solid var(--v-border);
                border-left: 10px solid var(--v-copper); margin-bottom: 2rem;
            }}
            h1, h2, h3 {{ color: var(--v-copper) !important; text-transform: uppercase; letter-spacing: 6px !important; }}
            [data-testid="stMetricValue"] {{ color: var(--v-copper) !important; font-family: 'JetBrains Mono', monospace !important; }}
            .v-table-tactical {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
            .v-table-tactical th {{ color: var(--v-copper); text-align: left; padding: 10px; border-bottom: 2px solid #333; }}
            .v-table-tactical td {{ padding: 10px; border-bottom: 1px solid #111; color: #CCC; }}
            .v-rail-track {{ width: 100%; height: 20px; background: #111; border-radius: 10px; position: relative; margin: 30px 0; }}
            .v-cog-pointer {{ position: absolute; width: 6px; height: 40px; top: -10px; transition: left 1s ease; }}
        </style>
    """, unsafe_allow_html=True)

# ==============================================================================
# 3. KONTROLA DOSTĘPU
# ==============================================================================
def check_authorized_clearance():
    if "authorized" not in st.session_state: st.session_state.authorized = False
    if not st.session_state.authorized:
        _, col_auth, _ = st.columns([1, 2, 1])
        with col_auth:
            with st.form("Auth"):
                st.markdown("<h2 style='text-align:center;'>VORTEZA LOGIN</h2>", unsafe_allow_html=True)
                pwd = st.text_input("SECURITY KEY", type="password")
                if st.form_submit_button("VALIDATE"):
                    if pwd == "vorteza2026":
                        st.session_state.authorized = True
                        st.rerun()
        return False
    return True

# ==============================================================================
# 4. SILNIK CAD-3D & PAKOWANIE
# ==============================================================================
def get_vorteza_sku_hex(sku_name):
    palette = ["#B58863", "#D4AF37", "#8E6A4D", "#16A085", "#27AE60", "#2980B9", "#E67E22", "#C0392B"]
    random.seed(sum(ord(c) for c in sku_name))
    return random.choice(palette)

def render_vorteza_cad_3d(vehicle_specs, cargo_stacks):
    fig = go.Figure()
    L, W, H = vehicle_specs['L'], vehicle_specs['W'], vehicle_specs['H']
    
    # Podłoga naczepy
    fig.add_trace(go.Mesh3d(x=[0, L, L, 0], y=[0, 0, W, W], z=[0, 0, 0, 0], color='#222', opacity=0.5))
    
    for cluster in cargo_stacks:
        for unit in cluster['items']:
            x, y, z = cluster['x'], cluster['y'], unit['z']
            dx, dy, dz = unit['w_fit'], unit['l_fit'], unit['height']
            p_color = get_vorteza_sku_hex(unit['name'])
            
            # Box Geometry
            fig.add_trace(go.Mesh3d(
                x=[x, x+dx, x+dx, x, x, x+dx, x+dx, x],
                y=[y, y, y+dy, y+dy, y, y, y+dy, y+dy],
                z=[z, z, z, z, z+dz, z+dz, z+dz, z+dz],
                i=[7,0,0,0,4,4,6,6,4,0,3,2], j=[3,4,1,2,5,6,5,2,0,1,6,3], k=[0,7,2,3,6,7,1,1,5,5,7,6],
                color=p_color, opacity=0.9, name=unit['name']
            ))

    fig.update_layout(scene=dict(aspectmode='data', bgcolor='black'), margin=dict(l=0, r=0, b=0, t=0))
    return fig

class V24SupremeEngine:
    @staticmethod
    def solve(cargo_list, vehicle, x_offset=0):
        items_sorted = sorted(cargo_list, key=lambda x: (not x.get('canStack', True), x['width']*x['length']), reverse=True)
        placed_stacks = []
        failed_units = []
        total_weight = 0
        cx, cy, current_row_max_w = x_offset, 0, 0

        for unit in items_sorted:
            if total_weight + unit['weight'] > vehicle['max_w']:
                failed_units.append(unit); continue
            
            is_stacked = False
            if unit.get('canStack', True):
                for s in placed_stacks:
                    if (unit['width'] <= s['w'] and unit['length'] <= s['l']) and (s['curH'] + unit['height'] <= vehicle['H']):
                        u_copy = unit.copy(); u_copy['z'] = s['curH']
                        u_copy['w_fit'], u_copy['l_fit'] = s['w'], s['l']
                        s['items'].append(u_copy); s['curH'] += unit['height']
                        total_weight += unit['weight']; is_stacked = True; break
            
            if is_stacked: continue

            if cy + unit['length'] <= vehicle['W'] and cx + unit['width'] <= vehicle['L']:
                u_c = unit.copy(); u_c['z'] = 0; u_c['w_fit'], u_c['l_fit'] = unit['width'], unit['length']
                placed_stacks.append({'x':cx, 'y':cy, 'w':unit['width'], 'l':unit['length'], 'curH':unit['height'], 'items':[u_c]})
                cy += unit['length']; current_row_max_w = max(current_row_max_w, unit['width'])
                total_weight += unit['weight']
            elif cx + current_row_max_w + unit['width'] <= vehicle['L']:
                cx += current_row_max_w; cy = 0; current_row_max_w = unit['width']
                u_c = unit.copy(); u_c['z'] = 0; u_c['w_fit'], u_c['l_fit'] = unit['width'], unit['length']
                placed_stacks.append({'x':cx, 'y':cy, 'w':unit['width'], 'l':unit['length'], 'curH':unit['height'], 'items':[u_c]})
                cy += unit['length']; total_weight += unit['weight']
            else: failed_units.append(unit)
        
        ldm = (max([s['x'] + s['w'] for s in placed_stacks]) / 100) if placed_stacks else 0
        return placed_stacks, total_weight, failed_units, ldm

# ==============================================================================
# 5. DATA I/O
# ==============================================================================
def db_core_load():
    if os.path.exists('products.json'):
        with open('products.json', 'r', encoding='utf-8') as f: return json.load(f)
    return []

def db_core_save(data):
    with open('products.json', 'w', encoding='utf-8') as f: json.dump(data, f, indent=4)

# ==============================================================================
# 6. MAIN APPLICATION
# ==============================================================================
def main():
    inject_vorteza_stack_ui()
    if not check_authorized_clearance(): return

    if 'v_manifest' not in st.session_state: st.session_state.v_manifest = []
    if 'lang' not in st.session_state: st.session_state.lang = "PL"
    
    L = LANGUAGES[st.session_state.lang]
    inventory = db_core_load()

    # SIDEBAR MISSION CONTROL
    with st.sidebar:
        st.session_state.lang = st.selectbox("🌐 LANGUAGE", ["PL", "ENG", "ES", "DE"], 
                                             index=["PL", "ENG", "ES", "DE"].index(st.session_state.lang))
        L = LANGUAGES[st.session_state.lang]
        
        st.markdown(f"### 📡 {L['fleet']}")
        v_key = st.selectbox(L['unit'], list(FLEET_MASTER_DATA.keys()))
        veh = FLEET_MASTER_DATA[v_key]
        x_shift = st.slider(L['offset'], 0, veh['L']-200, 0)
        
        st.divider()
        st.markdown(f"### 📥 {L['cargo']}")
        sel_sku_name = st.selectbox(L['sku_sel'], [p['name'] for p in inventory], index=None)
        
        if sel_sku_name:
            p_ref = next(p for p in inventory if p['name'] == sel_sku_name)
            p_qty = st.number_input(L['qty'], min_value=1, value=p_ref.get('itemsPerCase', 1))
            if st.button(L['add']):
                # Dodajemy jako wpis zbiorczy (linia manifestu)
                new_entry = p_ref.copy()
                new_entry['p_act'] = p_qty
                st.session_state.v_manifest.append(new_entry)
                st.rerun()

        # EDYTOR MANIFESTU (EDYCJA ILOŚCI)
        if st.session_state.v_manifest:
            st.divider()
            st.markdown(f"### 📝 {L['edit_m']}")
            df_m = pd.DataFrame(st.session_state.v_manifest)
            edited_m = st.data_editor(df_m[['name', 'p_act']], 
                                     column_config={"name": "SKU", "p_act": st.column_config.NumberColumn(L['qty'], min_value=0)},
                                     num_rows="dynamic", use_container_width=True)
            if st.button(L['update']):
                updated_list = []
                for _, row in edited_m.iterrows():
                    if row['p_act'] > 0:
                        original = next((p for p in inventory if p['name'] == row['name']), None)
                        if original:
                            u_entry = original.copy()
                            u_entry['p_act'] = row['p_act']
                            updated_list.append(u_entry)
                st.session_state.v_manifest = updated_list
                st.rerun()

        if st.button(L['purge']): st.session_state.v_manifest = []; st.rerun()

    # TABS
    t_plan, t_inv, t_log = st.tabs([f"📊 {L['title']}", f"📦 {L['inventory']}", f"⚙️ {L['logs']}"])

    with t_plan:
        if st.session_state.v_manifest:
            # Przygotowanie fizycznej listy pudełek dla silnika
            engine_input = []
            for entry in st.session_state.v_manifest:
                num_cases = math.ceil(entry['p_act'] / entry.get('itemsPerCase', 1))
                for _ in range(num_cases): engine_input.append(entry.copy())
            
            stacks, weight, failed, ldm = V24SupremeEngine.solve(engine_input, veh, x_shift)
            
            c1, c2, c3 = st.columns(3)
            c1.metric(L['pcs'], sum(it['p_act'] for it in st.session_state.v_manifest))
            c2.metric(L['weight'], f"{weight} KG")
            c3.metric(L['util'], f"{(weight/veh['max_w'])*100:.1f}%")

            st.markdown('<div class="v-tile-apex">', unsafe_allow_html=True)
            st.plotly_chart(render_vorteza_cad_3d(veh, stacks), use_container_width=True)
            
            # Balans CoG
            cog_p = (ldm*100 / (veh['L']/100)) / 2 
            marker_clr = "#00FF41" if 35 < cog_p < 65 else "#FF3131"
            st.markdown(f'**{L["cog"]}**')
            st.markdown(f'<div class="v-rail-track"><div class="v-cog-pointer" style="left:{cog_p}%; background:{marker_clr}; box-shadow:0 0 15px {marker_clr}"></div></div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.info(L['no_data'])

    with t_inv:
        st.markdown(f"### {L['inventory']}")
        df_inv = pd.DataFrame(inventory)
        new_inv = st.data_editor(df_inv, num_rows="dynamic", use_container_width=True)
        if st.button("SAVE DATABASE"):
            db_core_save(new_inv.to_dict('records'))
            st.success("SYNC OK")

    with t_log:
        st.code(f"SYSTEM: VORTEZA STACK v24.0\nSTATUS: NOMINAL\nLANG: {st.session_state.lang}\nTIME: {datetime.now()}")

if __name__ == "__main__":
    main()
