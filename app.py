import streamlit as st
import xgboost as xgb
import numpy as np
import streamlit.components.v1 as components

# 1. Configuración de la página a formato ANCHO
st.set_page_config(
    page_title="Dashboard Vaca Muerta | CRISP-DM",
    page_icon="🛢️",
    layout="wide", # Usamos layout wide para que tu HTML de 1200px entre perfecto
    initial_sidebar_state="expanded"
)

# 2. Cargar el modelo
@st.cache_resource
def cargar_modelo():
    model = xgb.XGBRegressor()
    model.load_model('modelo_fracking_xgb.json')
    return model

modelo = cargar_modelo()

# 3. Controles en la BARRA LATERAL (Inputs)
st.sidebar.title("🎛️ Panel de Control")
st.sidebar.markdown("Ajuste los parámetros para recalcular el dashboard en tiempo real.")

longitud = st.sidebar.slider("Longitud Rama (m):", 100, 4500, 2200, 50)
cant_fracturas = st.sidebar.slider("Etapas de Fractura:", 1, 100, 45, 1)
potencia = st.sidebar.slider("Potencia Superficie (HP):", 5000, 50000, 25000, 500)
agua = st.sidebar.slider("Agua Inyectada (m³):", 1000, 160000, 75000, 1000)
arena = st.sidebar.slider("Arena Total (Tn):", 100, 15000, 6000, 100)

# 4. Predicción del Modelo
datos_entrada = np.array([[longitud, cant_fracturas, agua, arena, potencia]])
prediccion_psi = modelo.predict(datos_entrada)[0]

# Calcular porcentajes lógicos para las barras del dashboard basados en la presión
prob_alta = min(max((prediccion_psi - 10000) / 4000 * 100, 2), 95) if prediccion_psi > 10000 else 5
prob_baja = min(max((10000 - prediccion_psi) / 5000 * 100, 2), 95) if prediccion_psi < 10000 else 5
prob_media = 100 - prob_alta - prob_baja

# 5. Inyección Dinámica del HTML (Tu código, pero con variables de Python adentro)
# Nota: Usamos f"""...""" para poder meter variables entre llaves { }
html_dashboard = f"""
<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8"/>
<style>
@import url("https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap");

:root {{
  --bg:        #0d1117;
  --surface:  #161b22;
  --surface2: #1c2330;
  --border:   #30363d;
  --border2:  #21262d;
  --text:     #e6edf3;
  --muted:    #8b949e;
  --dim:      #484f58;
  --blue:     #388bfd;
  --blue-dim: #1f3a5f;
  --green:    #3fb950;
  --green-dim:#1a3a1a;
  --orange:   #f78166;
  --orange-dim:#3a1e1a;
}}

* {{ box-sizing: border-box; margin: 0; padding: 0; }}

body {{
  font-family: "Syne", sans-serif;
  background: transparent; /* Transparente para fundirse con Streamlit */
  color: var(--text);
}}

/* ... (Aquí iría todo el resto de tu bloque CSS tal cual está) ... */

/* ── LAYOUT ── */
.wrapper {{
  padding: 10px;
  display: grid;
  grid-template-columns: 1fr 1fr;
  grid-template-rows: auto auto;
  gap: 18px;
  max-width: 100%; margin: 0 auto;
}}

/* ── WINDOW ── */
.win {{
  background: var(--surface); border: 1px solid var(--border);
  border-radius: 12px; overflow: hidden; box-shadow: 0 4px 24px rgba(0,0,0,.4);
}}
.win-bar {{ background: var(--surface2); border-bottom: 1px solid var(--border2); padding: 10px 16px; display: flex; align-items: center; gap: 8px; }}
.win-title {{ flex: 1; text-align: center; font-size: 12.5px; font-weight: 700; color: var(--muted); }}
.win-body {{ padding: 18px; }}

.pred-layout {{ display: grid; grid-template-columns: 1fr 1fr; gap: 14px; }}
.param-box, .result-wrap {{ background: var(--surface2); border: 1px solid var(--border2); border-radius: 8px; padding: 14px; }}
.param-row {{ display: flex; justify-content: space-between; padding: 6px 0; border-bottom: 1px solid var(--border2); font-size: 12px; }}
.param-key {{ color: var(--muted); }}
.param-val {{ font-family: "JetBrains Mono", monospace; font-weight: 600; color: var(--text); }}
.result-card {{ background: linear-gradient(135deg, #0d2535, #0d1a2a); border: 1px solid var(--blue); border-radius: 8px; padding: 14px; display: flex; align-items: center; gap: 12px; }}
.result-value {{ font-family: "JetBrains Mono", monospace; font-size: 22px; font-weight: 700; color: var(--green); }}

.prob-row2 {{ display: flex; align-items: center; gap: 8px; margin-bottom: 7px; }}
.prob-name2 {{ font-size: 11.5px; color: #cdd9e5; width: 95px; }}
.prob-track2 {{ flex: 1; background: var(--border2); border-radius: 3px; height: 13px; overflow: hidden; }}
.prob-fill2 {{ height: 100%; }}
.prob-fill2.p1 {{ background: linear-gradient(90deg,#1d4ed8,#60a5fa); }}
.prob-fill2.p2 {{ background: linear-gradient(90deg,#92400e,#f97316); }}
.prob-fill2.p3 {{ background: linear-gradient(90deg,#166534,#4ade80); }}
.prob-pct2 {{ font-family: "JetBrains Mono", monospace; font-size: 11.5px; color: var(--muted); width: 40px; text-align: right; }}

</style>
</head>
<body>

<div class="wrapper">
  <div class="win" style="grid-column: 1 / -1;">
    <div class="win-bar">
      <div class="win-title">Estimación de Pozo Individual (EN TIEMPO REAL)</div>
    </div>
    <div class="win-body">
      <div class="pred-layout">
        
        <div class="param-box">
          <div style="font-size: 11px; font-weight: 700; color: #8b949e; margin-bottom: 10px;">PARÁMETROS INGRESADOS</div>
          <div class="param-row"><span class="param-key">Longitud rama</span><span class="param-val">{longitud:,.0f} m</span></div>
          <div class="param-row"><span class="param-key">Etapas fractura</span><span class="param-val">{cant_fracturas}</span></div>
          <div class="param-row"><span class="param-key">Arena Total</span><span class="param-val">{arena:,.0f} tn</span></div>
          <div class="param-row"><span class="param-key">Agua inyectada</span><span class="param-val">{agua:,.0f} m³</span></div>
          <div class="param-row"><span class="param-key">Potencia Eq.</span><span class="param-val">{potencia:,.0f} HP</span></div>
        </div>

        <div class="result-wrap">
          <div>
            <div style="font-size: 11px; font-weight: 700; color: #8b949e; margin-bottom: 10px;">RESULTADO DEL MODELO XGBOOST</div>
            <div class="result-card">
              <div style="width:38px;height:38px;border-radius:50%;background:#3fb950;display:flex;align-items:center;justify-content:center;color:#000;font-weight:bold;">✓</div>
              <div>
                <div style="font-size: 11px; color: #8b949e;">Presión máxima estimada:</div>
                <div class="result-value">{prediccion_psi:,.0f} PSI</div>
              </div>
            </div>
          </div>
          
          <div style="margin-top:10px;">
            <div style="font-size: 11px; font-weight: 700; color: #8b949e; margin-bottom: 8px;">DISTRIBUCIÓN DE PROBABILIDAD (DINÁMICA)</div>
            <div class="prob-row2">
              <span class="prob-name2">Alta presión (>10k)</span>
              <div class="prob-track2"><div class="prob-fill2 p1" style="width:{prob_alta}%"></div></div>
              <span class="prob-pct2">{prob_alta:.1f}%</span>
            </div>
            <div class="prob-row2">
              <span class="prob-name2">Presión media</span>
              <div class="prob-track2"><div class="prob-fill2 p2" style="width:{prob_media}%"></div></div>
              <span class="prob-pct2">{prob_media:.1f}%</span>
            </div>
            <div class="prob-row2">
              <span class="prob-name2">Baja presión</span>
              <div class="prob-track2"><div class="prob-fill2 p3" style="width:{prob_baja}%"></div></div>
              <span class="prob-pct2">{prob_baja:.1f}%</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</div>

</body>
</html>
"""

# 6. Dibuja el HTML dentro de Streamlit ocupando todo el ancho
components.html(html_dashboard, height=800, scrolling=True)
