# v_visuals.py
import plotly.graph_objects as go
import random

def get_pro_color(name):
    palette = ["#B58863", "#D4AF37", "#8E6A4D", "#5E4633", "#A67C52", "#2C3E50", "#34495E", "#16A085", "#27AE60"]
    random.seed(sum(ord(c) for c in name))
    return random.choice(palette)

def build_explicit_box(x, y, z, dx, dy, dz, color, name):
    vx = [x, x+dx, x+dx, x, x, x+dx, x+dx, x]
    vy = [y, y, y+dy, y+dy, y, y, y+dy, y+dy]
    vz = [z, z, z, z, z+dz, z+dz, z+dz, z+dz]
    i, j, k = [7,0,0,0,4,4,6,6,4,0,3,2], [3,4,1,2,5,6,5,2,0,1,6,3], [0,7,2,3,6,7,1,1,5,5,7,6]
    mesh = go.Mesh3d(x=vx, y=vy, z=vz, i=i, j=j, k=k, color=color, opacity=0.98, name=name, flatshading=True, lighting=dict(ambient=0.5, diffuse=0.8))
    lx = [x,x+dx,x+dx,x,x,x,x+dx,x+dx,x,x,x+dx,x+dx,x+dx,x+dx,x,x]
    ly = [y,y,y+dy,y+dy,y,y,y,y+dy,y+dy,y+dy,y+dy,y,y,y+dy,y+dy,y]
    lz = [z,z,z,z,z,z+dz,z+dz,z,z,z+dz,z+dz,z+dz,z,z,z+dz,z+dz]
    lines = go.Scatter3d(x=lx, y=ly, z=lz, mode='lines', line=dict(color='black', width=3.5), hoverinfo='skip')
    return [mesh, lines]

def render_3d_pro(veh, stacks):
    fig = go.Figure()
    L, W, H = veh['L'], veh['W'], veh['H']
    fig.add_trace(go.Mesh3d(x=[0,L,L,0], y=[0,0,W,W], z=[-15,-15,-15,-15], color='#111', opacity=1, hoverinfo='skip'))
    # Kabina
    fig.add_trace(go.Mesh3d(x=[-veh['cab'], 0, 0, -veh['cab'], -veh['cab'], 0, 0, -veh['cab']], y=[-45,-45,W+45,W+45,-45,-45,W+45,W+45], z=[0,0,0,0,H*1.05,H*1.05,H*1.05,H*1.05], i=[7,0,0,0,4,4,6,6,4,0,3,2], j=[3,4,1,2,5,6,5,2,0,1,6,3], k=[0,7,2,3,6,7,1,1,5,5,7,6], color='#020202', opacity=1))
    for s in stacks:
        for u in s['items']:
            for p in build_explicit_box(s['x'], s['y'], u['z'], u['w_fit'], u['l_fit'], u['height'], get_pro_color(u['name']), u['name']): fig.add_trace(p)
    fig.update_layout(scene=dict(aspectmode='data', xaxis_visible=False, yaxis_visible=False, zaxis_visible=False, camera=dict(eye=dict(x=2.5, y=2.5, z=2.0))), paper_bgcolor='rgba(0,0,0,0)', margin=dict(l=0,r=0,b=0,t=0), showlegend=False)
    return fig
