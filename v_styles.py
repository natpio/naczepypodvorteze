# v_styles.py
import streamlit as st
import base64
import os

def load_vorteza_asset_b64(path):
    try:
        if os.path.exists(path):
            with open(path, 'rb') as f: return base64.b64encode(f.read()).decode()
        return ""
    except: return ""

def apply_supreme_ui():
    bg = load_vorteza_asset_b64('bg_vorteza.png')
    st.markdown(f"""
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;600;700&family=JetBrains+Mono:wght@400;500&display=swap');
            :root {{
                --v-copper: #B58863;
                --v-glow: rgba(181, 136, 99, 0.6);
            }}
            .stApp {{ 
                background-image: url("data:image/png;base64,{bg}"); 
                background-size: cover; background-attachment: fixed; color: #FFF; font-family: 'Montserrat'; 
            }}
            .v-tile-pro {{
                background: rgba(5, 5, 5, 0.96);
                padding: 2.8rem; border-radius: 4px; border: 1px solid rgba(181, 136, 99, 0.3);
                border-left: 12px solid var(--v-copper); box-shadow: 0 60px 150px #000; margin-bottom: 3.5rem; backdrop-filter: blur(45px);
            }}
            section[data-testid="stSidebar"] {{ 
                background-color: rgba(2, 2, 2, 0.99) !important; border-right: 1px solid var(--v-copper); width: 500px !important; 
            }}
            h1, h2, h3 {{ color: var(--v-copper) !important; text-transform: uppercase; letter-spacing: 12px; font-weight: 700; text-shadow: 4px 4px 25px #000; }}
            [data-testid="stMetricValue"] {{ color: var(--v-copper) !important; font-family: 'JetBrains Mono'; font-size: 3.8rem !important; }}
            [data-testid="stMetricLabel"] {{ color: #999 !important; text-transform: uppercase; letter-spacing: 4px; font-weight: 700; }}
            .stButton > button {{
                background: linear-gradient(180deg, #0a0a0a, #151515); color: var(--v-copper); border: 2px solid var(--v-copper);
                padding: 1.8rem; text-transform: uppercase; letter-spacing: 10px; font-weight: 700; width: 100%; transition: 0.6s all; border-radius: 0;
            }}
            .stButton > button:hover {{ background: var(--v-copper); color: #000; box-shadow: 0 0 100px var(--v-glow); transform: translateY(-5px); }}
            .v-rail-track {{ width: 100%; height: 35px; background: #000; border-radius: 17px; position: relative; border: 2px solid #222; margin: 60px 0; box-shadow: inset 0 0 25px #000; }}
            .v-cog-indicator {{ position: absolute; width: 15px; height: 75px; top: -20px; background: #00FF41; box-shadow: 0 0 50px #00FF41; border-radius: 8px; transition: left 1.5s cubic-bezier(0.19, 1, 0.22, 1); }}
            .v-table-tactical {{ width: 100%; border-collapse: collapse; margin-top: 45px; border: 1px solid #1a1a1a; }}
            .v-table-tactical th {{ background: #000; color: var(--v-copper); text-align: left; font-size: 0.9rem; text-transform: uppercase; border-bottom: 3px solid #333; padding: 25px; letter-spacing: 3px; }}
            .v-table-tactical td {{ padding: 20px 25px; border-bottom: 1px solid #111; color: #CCC; font-size: 1.1rem; }}
        </style>
    """, unsafe_allow_html=True)
