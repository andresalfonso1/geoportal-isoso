# Script integrado para visualización de mapas de cobertura de suelo
# Proyecto: Geoportal TCO Isoso - Dashboard REDD+/Verra
# Integrado con reclasificación consistente del proyecto

import ee
import geemap

# ============================================================================
# CONFIGURACIÓN (Consistente con gee_analysis.py)
# ============================================================================

# Asset de MapBiomas Bolivia Collection 3
MAPBIOMAS_ASSET = "projects/mapbiomas-public/assets/bolivia/lulc/collection3/mapbiomas_bolivia_collection3_integration_v1"

# Territorio TCO Isoso
TCO_ISOSO_ASSET = "users/aealfonsom/PA_IsosoTituladaTCO"

# Años de análisis
YEARS = [2019, 2024]

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

# Paleta de colores (consistente con el dashboard)
PALETTE = [
    "#006400",  # 0: Bosque
    "#45C2A5",  # 1: Herbazal/Arbustal
    "#F5B454",  # 2: Agropecuario
    "#D4271E",  # 3: Área sin vegetación
    "#0000FF"   # 4: Cuerpos de agua
]

VIS_PARAMS = {'min': 0, 'max': 4, 'palette': PALETTE}

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

def cargar_datos():
    """Carga y procesa las imágenes de cobertura de suelo"""
    print("📦 Cargando datos de cobertura...")
    
    # Cargar territorio
    table = ee.FeatureCollection(TCO_ISOSO_ASSET)
    
    # Cargar y reclasificar imágenes
    img_2019 = ee.Image(MAPBIOMAS_ASSET).select('classification_2019').clip(table)
    img_2024 = ee.Image(MAPBIOMAS_ASSET).select('classification_2024').clip(table)
    
    img_2019_rec = reclasificar_imagen(img_2019)
    img_2024_rec = reclasificar_imagen(img_2024)
    
    print("✅ Datos cargados y reclasificados")
    
    return img_2019_rec, img_2024_rec, table

def crear_mapa_comparativo(img_2019, img_2024, table):
    """Crea mapa interactivo comparativo usando geemap"""
    print("🗺️ Creando mapa comparativo...")
    
    # Crear mapa
    m = geemap.Map()
    m.centerObject(table, 10)
    
    # Configurar capas para comparación dividida
    left_layer = geemap.ee_tile_layer(img_2019, VIS_PARAMS, 'Cobertura 2019')
    right_layer = geemap.ee_tile_layer(img_2024, VIS_PARAMS, 'Cobertura 2024')
    
    # Aplicar mapa dividido
    m.split_map(left_layer, right_layer)
    
    # Agregar leyenda
    legend_dict = {
        "Bosque": "#006400",
        "Herbazal/Arbustal": "#45C2A5",
        "Agropecuario": "#F5B454",
        "Área sin vegetación": "#D4271E",
        "Cuerpos de agua": "#0000FF"
    }
    
    m.add_legend(title="Leyenda de Cobertura", legend_dict=legend_dict)
    
    # Agregar capa del territorio
    m.addLayer(table.style(**{'color': 'red', 'fillColor': '00000000', 'width': 2}), 
               {}, 'TCO Isoso')
    
    return m

def calcular_estadisticas_basicas(img_2019, img_2024, table):
    """Calcula estadísticas básicas de cambio"""
    print("📊 Calculando estadísticas básicas...")
    
    # Área total del territorio
    area_total = table.geometry().area().divide(10000).getInfo()  # en ha
    print(f"Área total del territorio: {area_total:,.2f} ha")
    
    # Crear imagen de cambio (1 = cambió, 0 = igual)
    cambio = img_2019.neq(img_2024)
    
    # Calcular área de cambio
    area_cambio_img = ee.Image.pixelArea().divide(10000).multiply(cambio)
    area_cambio = area_cambio_img.reduceRegion(
        reducer=ee.Reducer.sum(),
        geometry=table.geometry(),
        scale=30,
        maxPixels=1e13
    ).get('area').getInfo()
    
    pct_cambio = (area_cambio / area_total) * 100
    
    print(f"Área con cambios: {area_cambio:,.2f} ha ({pct_cambio:.2f}%)")
    print(f"Área estable: {area_total - area_cambio:,.2f} ha ({100 - pct_cambio:.2f}%)")
    
    return {
        'area_total_ha': area_total,
        'area_cambio_ha': area_cambio,
        'porcentaje_cambio': pct_cambio
    }

# ============================================================================
# EJECUCIÓN PRINCIPAL
# ============================================================================

if __name__ == "__main__":
    print("🌍 Geoportal TCO Isoso - Visualización de Mapas Integrada")
    print("=" * 60)
    
    # Autenticar
    autenticar_gee()
    
    # Cargar datos
    img_2019, img_2024, table = cargar_datos()
    
    # Calcular estadísticas
    stats = calcular_estadisticas_basicas(img_2019, img_2024, table)
    
    # Crear mapa
    mapa = crear_mapa_comparativo(img_2019, img_2024, table)
    
    print("\n" + "="*60)
    print("🗺️ MAPA COMPARATIVO CREADO")
    print("="*60)
    print("• Capa izquierda: Cobertura 2019")
    print("• Capa derecha: Cobertura 2024")
    print("• Leyenda: Clasificación de cobertura")
    print("• Borde rojo: Límites del TCO Isoso")
    print("="*60)
    
    # Mostrar mapa (en Jupyter/notebook)
    # mapa
    
    print("✅ Mapa comparativo listo para visualización")
    print("💡 Para usar en Jupyter: ejecutar 'mapa' en una celda")
    
    # Nota: En un script independiente, el mapa se mostraría en el navegador
    # Para uso en script, podríamos exportar a HTML
    # mapa.to_html('mapa_comparativo.html')