import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import make_interp_spline

# Configuración de la página
st.set_page_config(page_title="Calculadora de Riesgo DCI - Ecuador", page_icon="👶", layout="centered")

st.title("📊 Simulador de Riesgo de Desnutrición Crónica (DCI)")
st.write("Herramienta interactiva basada en los datos de la ENDI 2023.")

# --- ENTRADAS DEL USUARIO ---
st.sidebar.header("Datos del Infante")
edad_dias = st.sidebar.slider("Edad del niño (en días):", min_value=1, max_value=2000, value=400, step=10)
zona = st.sidebar.radio("Zona de residencia:", ["Urbana", "Rural"])

# --- DATOS REALES DE TU GRÁFICA (Para interpolar y dibujar) ---
edades_ref = np.array([0, 85, 250, 375, 500, 625, 750, 850, 1000, 1125, 1250, 1375, 1500, 1625, 1750, 1875, 2000])
casos_ref = np.array([0, 85, 121, 185, 177, 180, 180, 195, 145, 147, 133, 123, 123, 122, 120, 9, 0])

# Interpolar para suavizar la curva
X_smooth = np.linspace(edades_ref.min(), edades_ref.max(), 300)
spl = make_interp_spline(edades_ref, casos_ref, k=3)
Y_smooth = spl(X_smooth)
Y_smooth = np.clip(Y_smooth, 0, None)

# Obtener la cantidad de casos interpolados para la edad ingresada
caso_usuario = float(np.interp(edad_dias, edades_ref, casos_ref))

# --- CÁLCULO DEL RIESGO ---
riesgo_edad = (caso_usuario / 195.0) * 100
factor_zona = 1.15 if zona == "Rural" else 0.85
riesgo_final = np.clip(riesgo_edad * factor_zona, 5, 99)

# --- MOSTRAR RESULTADOS ---
st.subheader("🚨 Diagnóstico de Riesgo Estimado")

if riesgo_final < 40:
    st.success(f"Riesgo Bajo: {riesgo_final:.1f}%")
elif riesgo_final < 75:
    st.warning(f"Riesgo Moderado: {riesgo_final:.1f}%")
else:
    st.error(f"Riesgo Crítico: {riesgo_final:.1f}%")

st.info(
    f"A los **{edad_dias} días** en la zona **{zona}**, el niño se encuentra en una phase de "
    f"{'máxima vulnerabilidad epidemiológica' if riesgo_final > 70 else 'estabilización de riesgo'}."
)

# --- DIBUJAR LA GRÁFICA DINÁMICA ---
fig, ax = plt.subplots(figsize=(8, 4.5))
ax.plot(X_smooth, Y_smooth, color='#d3d3d3', linestyle='--', label='Curva de Referencia Nacional')
ax.fill_between(X_smooth, Y_smooth, color='#fde8e8', alpha=0.5)
ax.axvspan(0, 1000, color='#ffcccc', alpha=0.2, label='Zona Crítica (0-1000 días)')
ax.scatter(edad_dias, caso_usuario, color='red', s=150, zorder=5, label='Infante Evaluado', edgecolor='black')
ax.annotate(
    f"{riesgo_final:.0f}% Riesgo", 
    (edad_dias, caso_usuario), 
    textcoords="offset points", 
    xytext=(0,10), 
    ha='center', 
    weight='bold', 
    color='red'
)

ax.set_title("Ubicación del Infante en la Curva de Vulnerabilidad", fontsize=12, weight='bold')
ax.set_xlabel("Edad (días)")
ax.set_ylabel("Densidad de Casos Activos")
ax.legend()
ax.grid(True, linestyle=':', alpha=0.6)

st.pyplot(fig)
