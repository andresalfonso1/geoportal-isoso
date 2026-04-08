# Script integrado para diagrama Sankey de transiciones de cobertura de suelo
# Proyecto: Geoportal TCO Isoso - Dashboard REDD+/Verra
# Integrado con reclasificación consistente del proyecto

import ee
import pandas as pd
import plotly.graph_objects as go

# ============================================================================
# CONFIGURACIÓN (Consistente con gee_analysis.py)
# ============================================================================

# Asset de MapBiomas Bolivia Collection 3
MAPBIOMAS_ASSET = "projects/mapbiomas-public/assets/bolivia/lulc/collection3/mapbiomas_bolivia_collection3_integration_v1"

# Territorio TCO Isoso
TCO_ISOSO_ASSET = "users/aealfonsom/PA_IsosoTituladaTCO"

# Años de análisis
YEAR_INICIO = 2019
YEAR_FIN = 2024

# Reclasificación: de clases originales MapBiomas a 5 clases del proyecto
RECLASIFICACION = {
    3: 0,   # Bosque
    6: 0,   # Bosque
    11: 1,  # Herbazal/Arbustal
    12: 1,  # Herbazal/Arbustal
    13: 1,  # Herbazal/Arbustal
    15: 2,  # Agropecuario
    18: 2,  # Agropecuario
    21: 2,  # Agropecuario
    39: 2,  # Agropecuario
    72: 2,  # Agropecuario
    23: 3,  # Área sin vegetación
    24: 3,  # Área sin vegetación
    25: 3,  # Área sin vegetación
    68: 3,  # Área sin vegetación
    33: 4   # Cuerpos de agua
}

# Nombres de las clases reclasificadas
CLASE_NOMBRES = {
    0: "Bosque",
    1: "Herbazal/Arbustal",
    2: "Agropecuario",
    3: "Área sin vegetación",
    4: "Cuerpos de agua"
}

# Colores para visualización
CLASE_COLORES = {
    0: "#006400",  # Bosque
    1: "#45C2A5",  # Herbazal/Arbustal
    2: "#F5B454",  # Agropecuario
    3: "#D4271E",  # Área sin vegetación
    4: "#0000FF"   # Cuerpos de agua
}

# ============================================================================
# FUNCIONES
# ============================================================================

def autenticar_gee():
    """Autentica con Google Earth Engine"""
    try:
        ee.Initialize()
        print("✅ Conectado a Google Earth Engine")
    except Exception as e:
        print(f"❌ Error de autenticación: {e}")
        ee.Authenticate()
        ee.Initialize()

def reclasificar_imagen(imagen):
    """Reclasifica imagen a 5 clases del proyecto"""
    valores_from = list(RECLASIFICACION.keys())
    valores_to = list(RECLASIFICACION.values())
    
    return imagen.remap(valores_from, valores_to, defaultValue=-1)

def calcular_transiciones():
    """Calcula matriz de transición usando reclasificación consistente"""
    print("🔄 Calculando transiciones de cobertura...")
    
    # Cargar datos
    asset = MAPBIOMAS_ASSET
    table = ee.FeatureCollection(TCO_ISOSO_ASSET)
    
    year_start, year_end = YEAR_INICIO, YEAR_FIN
    
    # Cargar imágenes originales
    img_start = ee.Image(asset).select(f'classification_{year_start}').clip(table)
    img_end = ee.Image(asset).select(f'classification_{year_end}').clip(table)
    
    # Reclasificar a 5 clases
    img_start_rec = reclasificar_imagen(img_start)
    img_end_rec = reclasificar_imagen(img_end)
    
    # Crear imagen de transición (consistente con gee_analysis.py: multiply(10).add)
    transition_img = img_start_rec.multiply(10).add(img_end_rec)
    
    # Calcular áreas
    area_img = ee.Image.pixelArea().divide(10000).addBands(transition_img)
    stats = area_img.reduceRegion(
        reducer=ee.Reducer.sum().group(groupField=1, groupName='trans_id'),
        geometry=table.geometry(),
        scale=30,
        maxPixels=1e13,
        tileScale=4
    ).get('groups').getInfo()
    
    # Procesar datos
    df = pd.DataFrame(stats)
    df['source_id'] = (df['trans_id'] // 10).astype(int)
    df['target_id'] = (df['trans_id'] % 10).astype(int)
    df['source'] = df['source_id'].map(CLASE_NOMBRES)
    df['target'] = df['target_id'].map(CLASE_NOMBRES)
    
    # Filtrar transiciones válidas
    df_sankey = df.dropna().groupby(['source', 'target'])['sum'].sum().reset_index()
    
    # Etiquetas para nodos
    df_sankey['source_label'] = df_sankey['source'] + f" ({year_start})"
    df_sankey['target_label'] = df_sankey['target'] + f" ({year_end})"
    
    return df_sankey

def crear_diagrama_sankey(df_sankey):
    """Crea diagrama Sankey con Plotly"""
    # Crear lista de etiquetas únicas
    label_list = list(pd.concat([df_sankey['source_label'], df_sankey['target_label']]).unique())
    node_indices = {label: i for i, label in enumerate(label_list)}
    
    # Colores de nodos
    node_colors = [CLASE_COLORES.get([k for k, v in CLASE_NOMBRES.items() if v == label.split(' (')[0]][0], "grey") 
                   for label in label_list]
    
    # Crear figura
    fig = go.Figure(data=[go.Sankey(
        node=dict(
            pad=20,
            thickness=30,
            line=dict(color="black", width=0.2),
            label=label_list,
            color=node_colors
        ),
        link=dict(
            source=df_sankey['source_label'].map(node_indices),
            target=df_sankey['target_label'].map(node_indices),
            value=df_sankey['sum'],
            color=[f"rgba{tuple(list(int(CLASE_COLORES[[k for k, v in CLASE_NOMBRES.items() if v == s][0]][i:i+2], 16) for i in (1, 3, 5)) + [0.4])}" 
                   for s in df_sankey['source']],
            hovertemplate='%{source.label} → %{target.label}<br>Área: %{value:,.2f} ha<extra></extra>'
        ))])
    
    fig.update_layout(
        title_text=f"Análisis de Transición Coberturas: {YEAR_INICIO} - {YEAR_FIN}",
        font_size=14,
        template="plotly_white",
        height=600
    )
    
    return fig

# ============================================================================
# EJECUCIÓN PRINCIPAL
# ============================================================================

if __name__ == "__main__":
    print("🌍 Geoportal TCO Isoso - Diagrama Sankey Integrado")
    print("=" * 50)
    
    # Autenticar
    autenticar_gee()
    
    # Calcular transiciones
    df_transiciones = calcular_transiciones()
    
    print(f"📊 Encontradas {len(df_transiciones)} transiciones significativas")
    
    # Crear y mostrar diagrama
    fig = crear_diagrama_sankey(df_transiciones)
    fig.show()
    
    print("✅ Diagrama Sankey generado exitosamente")