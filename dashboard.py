import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Configuración de la página
st.set_page_config(page_title="Dashboard Dificultades Cognitivas", layout="wide", page_icon="📊")

# Título
st.title("Dificultad de concentración y memoria entre dos géneros")

# Cargar datos desde el archivo local
try:
    df = pd.read_csv("CopiaAnalisis.csv")
except Exception as e:
    st.error(f"Error al cargar el archivo CSV: {e}")
    st.stop()

# Asegurar nombres de columnas correctos y filtrar las necesarias
df = df[['Genero', 'Dificultadrecordando', 'Dificultadconcetracion']]
df.columns = ['Genero', 'Dificultadrecordando', 'Dificultadconcetracion']  # Estandarizar nombres

# Mapeo de valores para mejor legibilidad
genero_map = {1: 'Hombre', 2: 'Mujer'}
dificultad_map = {0: 'Ausencia', 1: 'Presencia'}
df['Genero'] = df['Genero'].map(genero_map)
df['Dificultadrecordando'] = df['Dificultadrecordando'].map(dificultad_map)
df['Dificultadconcetracion'] = df['Dificultadconcetracion'].map(dificultad_map)

# Colores personalizados
colores = {'Ausencia': '#dffd6e', 'Presencia': '#ffad61'}  # Verde y Naranja
fondo = '#ffffff'  # Blanco
texto = '#000000'  # Negro

# Layout de la primera fila: botones y métricas
col1, col2 = st.columns([1, 2])

# Botones para filtrar por género
with col1:
    st.subheader("Filtrar por Género")
    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        if st.button("Mujeres"):
            genero_filtro = "Mujer"
        else:
            genero_filtro = None
    with col_btn2:
        if st.button("Hombres"):
            genero_filtro = "Hombre"
        else:
            genero_filtro = genero_filtro if 'genero_filtro' in locals() else None

# Filtrar datos según el botón presionado
if genero_filtro:
    df_filtrado = df[df['Genero'] == genero_filtro]
else:
    df_filtrado = df

# Métricas
with col2:
    st.subheader("Estadísticas de Participantes")
    total_participantes = len(df)
    porcentaje_mujeres = (len(df[df['Genero'] == 'Mujer']) / total_participantes * 100) if total_participantes > 0 else 0
    porcentaje_hombres = (len(df[df['Genero'] == 'Hombre']) / total_participantes * 100) if total_participantes > 0 else 0
    col_m1, col_m2, col_m3 = st.columns(3)
    col_m1.metric("Total Participantes", total_participantes)
    col_m2.metric("% Mujeres", f"{porcentaje_mujeres:.1f}%")
    col_m3.metric("% Hombres", f"{porcentaje_hombres:.1f}%")

# Layout de la segunda fila: gráficas
col3, col4 = st.columns(2)

# Gráfica de barras: Dificultad de concentración
with col3:
    st.subheader("Dificultad de Concentración por Género")
    # Calcular porcentajes para hombres y mujeres
    conc_data = df.groupby(['Genero', 'Dificultadconcetracion']).size().unstack(fill_value=0)
    conc_data = conc_data.div(conc_data.sum(axis=1), axis=0) * 100  # Convertir a porcentajes
    conc_data = conc_data.reset_index()
    
    # Crear gráfica de barras
    fig_bar = go.Figure()
    for dificultad in ['Ausencia', 'Presencia']:
        fig_bar.add_trace(go.Bar(
            x=conc_data['Genero'],
            y=conc_data[dificultad],
            name=dificultad,
            text=[f"{val:.1f}%" for val in conc_data[dificultad]],
            textposition='auto',
            marker_color=colores[dificultad]
        ))
    fig_bar.update_layout(
        barmode='group',
        title="Porcentaje de Dificultad de Concentración",
        xaxis_title="Género",
        yaxis_title="Porcentaje",
        yaxis=dict(ticksuffix="%"),
        plot_bgcolor=fondo,
        paper_bgcolor=fondo,
        font=dict(color=texto)
    )
    st.plotly_chart(fig_bar, use_container_width=True)

# Gráficas de pastel: Dificultad de recordar
with col4:
    st.subheader("Dificultad de Recordar por Género")
    # Preparar datos para mujeres y hombres
    mujeres_data = df[df['Genero'] == 'Mujer']['Dificultadrecordando'].value_counts()
    hombres_data = df[df['Genero'] == 'Hombre']['Dificultadrecordando'].value_counts()
    
    # Crear subplots para gráficas de pastel
    fig_pie = make_subplots(rows=1, cols=2, specs=[[{'type': 'pie'}, {'type': 'pie'}]],
                            subplot_titles=["Mujeres", "Hombres"])
    
    # Pastel para mujeres
    fig_pie.add_trace(
        go.Pie(
            labels=mujeres_data.index,
            values=mujeres_data.values,
            name="Mujeres",
            textinfo='percent+label',
            textposition='inside',
            marker=dict(colors=[colores.get(idx, '#dffd6e') for idx in mujeres_data.index])
        ),
        row=1, col=1
    )
    
    # Pastel para hombres
    fig_pie.add_trace(
        go.Pie(
            labels=hombres_data.index,
            values=hombres_data.values,
            name="Hombres",
            textinfo='percent+label',
            textposition='inside',
            marker=dict(colors=[colores.get(idx, '#ffad61') for idx in hombres_data.index])
        ),
        row=1, col=2
    )
    
    fig_pie.update_layout(
        title="Porcentaje de Dificultad de Recordar",
        plot_bgcolor=fondo,
        paper_bgcolor=fondo,
        font=dict(color=texto)
    )
    st.plotly_chart(fig_pie, use_container_width=True)

# Mostrar datos filtrados
if genero_filtro:
    st.subheader(f"Datos de {genero_filtro}")
    st.dataframe(df_filtrado, use_container_width=True)

# Nota al pie
st.write("Dashboard generado con Streamlit y datos de CopiaAnalisis.csv.")
