# v_engine.py
import math

class VEngine:
    @staticmethod
    def solve(cargo, veh, offset=0):
        # Priorytet: No-Stack > No-Rotation > Powierzchnia
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
