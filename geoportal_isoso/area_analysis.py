# Script integrado para cálculo de áreas por clase de cobertura de suelo
# Proyecto: Geoportal TCO Isoso - Dashboard REDD+/Verra
# Integrado con reclasificación consistente del proyecto

import ee
import pandas as pd

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

def calcular_areas_por_clase(year):
    """Calcula áreas por clase para un año específico usando reclasificación"""
    print(f"📊 Calculando áreas para el año {year}...")
    
    # Cargar territorio
    table = ee.FeatureCollection(TCO_ISOSO_ASSET)
    
    # Cargar y reclasificar imagen
    landCover = ee.Image(MAPBIOMAS_ASSET).select(f'classification_{year}').clip(table)
    landCover_rec = reclasificar_imagen(landCover)
    
    # Calcular área en hectáreas
    areaImage = ee.Image.pixelArea().divide(10000).addBands(landCover_rec)
    
    # Reducir para obtener áreas por clase
    areasByClass = areaImage.reduceRegion(
        reducer=ee.Reducer.sum().group(groupField=1, groupName='class'),
        geometry=table,
        scale=30,
        maxPixels=1e13,
        tileScale=4
    )
    
    # Convertir a lista
    areas_list = ee.List(areasByClass.get('groups')).getInfo()
    
    # Convertir a DataFrame
    df_temp = pd.DataFrame(areas_list)
    df_temp.columns = ['Class ID', f'Area (ha) {year}']
    df_temp[f'Area (ha) {year}'] = df_temp[f'Area (ha) {year}'].round(2)
    
    # Agregar nombres de clase
    df_temp['Class Name'] = df_temp['Class ID'].map(CLASE_NOMBRES)
    
    return df_temp

def calcular_areas_comparativo():
    """Calcula áreas para múltiples años y crea tabla comparativa"""
    print("🔄 Calculando áreas comparativas...")
    
    df_final = pd.DataFrame()
    
    for year in YEARS:
        df_temp = calcular_areas_por_clase(year)
        
        if df_final.empty:
            df_final = df_temp
        else:
            df_final = pd.merge(df_final, df_temp[['Class ID', f'Area (ha) {year}']], 
                              on='Class ID', how='outer')
    
    # Ordenar por ID de clase
    df_final = df_final.sort_values(by='Class ID').reset_index(drop=True)
    
    # Calcular cambios
    if len(YEARS) >= 2:
        year1, year2 = YEARS[0], YEARS[1]
        df_final[f'Cambio ({year1}-{year2})'] = (
            df_final[f'Area (ha) {year2}'] - df_final[f'Area (ha) {year1}']
        ).round(2)
        
        df_final[f'Cambio % ({year1}-{year2})'] = (
            (df_final[f'Cambio ({year1}-{year2})'] / df_final[f'Area (ha) {year1}'] * 100)
            .round(2)
        )
    
    return df_final

def mostrar_resultados(df):
    """Muestra los resultados en formato legible"""
    print("\n" + "="*80)
    print("📋 ÁREAS POR CLASE DE COBERTURA DE SUELO")
    print("="*80)
    print(df.to_string(index=False))
    print("="*80)
    
    # Resumen
    for year in YEARS:
        total = df[f'Area (ha) {year}'].sum()
        print(f"Total {year}: {total:,.2f} ha")
    
    if len(YEARS) >= 2:
        year1, year2 = YEARS[0], YEARS[1]
        cambio_total = df[f'Cambio ({year1}-{year2})'].sum()
        print(f"Cambio total ({year1}-{year2}): {cambio_total:+,.2f} ha")
        
        area_inicial = df[f'Area (ha) {year1}'].sum()
        pct_cambio = (cambio_total / area_inicial * 100)
        print(f"Porcentaje de cambio: {pct_cambio:+.2f}%")

# ============================================================================
# EJECUCIÓN PRINCIPAL
# ============================================================================

if __name__ == "__main__":
    print("🌍 Geoportal TCO Isoso - Análisis de Áreas Integrado")
    print("=" * 50)
    
    # Autenticar
    autenticar_gee()
    
    # Calcular áreas
    df_resultados = calcular_areas_comparativo()
    
    # Mostrar resultados
    mostrar_resultados(df_resultados)
    
    # Guardar a CSV (opcional)
    output_file = "areas_reclasificadas.csv"
    df_resultados.to_csv(output_file, index=False)
    print(f"\n💾 Resultados guardados en: {output_file}")
    
    print("✅ Análisis de áreas completado exitosamente")