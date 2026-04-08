# 🌍 Geoportal TCO Isoso - Dashboard REDD+/Verra

> Dashboard web interactivo para inversionistas en mercados de carbono y proyectos REDD+/Verra

## 🚀 Quick Start

### Ver el Dashboard

**Opción 1: Preview Local (Recomendado)**
```bash
cd /home/ubuntu/geoportal_isoso
python3 -m http.server 8080
# Abrir en navegador: http://localhost:8080
```

**Opción 2: Deployment en GitHub Pages**
```bash
# Ver guía completa en DEPLOYMENT.md
git init
git add .
git commit -m "Initial commit"
git push origin main
# Habilitar GitHub Pages en Settings > Pages
```

**Opción 3: Abrir directamente**
```bash
# Abrir index.html en navegador
firefox index.html  # o chrome, etc.
```

---

## 📋 Componentes del Proyecto

Este proyecto incluye:

1. **🎨 Dashboard Web** (`index.html`) - Visualización interactiva con:
   - 4 KPIs principales (área total, bosque 2024, deforestación %, área REDD+)
   - Mapa interactivo Leaflet con comparador 2019/2024
   - Diagrama Sankey de transiciones de cobertura
   - Gráfico de barras comparativo
   - Tabla de cambios netos
   - Card metodológico

2. **🛠️ Scripts de Análisis** - Procesamiento geoespacial automatizado:
   - `gee_analysis.py` - Análisis principal con Google Earth Engine
   - `validar_json.py` - Validación de datos
   - `ejemplo_leer_json.py` - Lector y generador de reportes

3. **📊 Datos de Ejemplo** (`output_json_ejemplo/`) - JSONs con:
   - Áreas por clase 2019 y 2024
   - Matriz de transición completa

---

## Análisis Geoespacial

Script de análisis geoespacial para calcular cambios de cobertura de suelo en el Territorio Comunitario de Origen (TCO) Isoso, Bolivia, usando Google Earth Engine y datos de MapBiomas Bolivia.

---

## 📋 Descripción

Este script automatiza el análisis de cobertura de suelo para los años **2019** y **2024**, generando:

1. **Áreas por clase de uso de suelo** para cada año (en hectáreas)
2. **Matriz de transición** entre años (qué clases cambiaron a qué)
3. **Archivos JSON** listos para ser usados en el dashboard web

### Datos Fuente

- **MapBiomas Bolivia Collection 3**: Mapeo de cobertura y uso de suelo
  - Asset GEE: `projects/mapbiomas-public/assets/bolivia/lulc/collection3/mapbiomas_bolivia_collection3_integration_v1`
  - Resolución: 30 metros
  - Años disponibles: 1985-2024

- **Territorio TCO Isoso**: Área protegida y territorio indígena
  - Asset GEE: `users/aealfonsom/PA_IsosoTituladaTCO`
  - Ubicación: Santa Cruz, Bolivia

### Reclasificación

Las clases originales de MapBiomas (15 clases) se reclasifican a **5 clases principales**:

| Clase | Nombre | Color | IDs MapBiomas Incluidos |
|-------|--------|-------|-------------------------|
| 0 | Bosque | 🟢 `#006400` | 3, 6 |
| 1 | Herbazal/Arbustal | 🟩 `#45C2A5` | 11, 12, 13 |
| 2 | Agropecuario | 🟨 `#F5B454` | 15, 18, 21, 39, 72 |
| 3 | Área sin vegetación | 🟥 `#D4271E` | 23, 24, 25, 68 |
| 4 | Cuerpos de agua | 🟦 `#0000FF` | 33 |

---

## 🚀 Instalación y Configuración

### Prerequisitos

- Python 3.7 o superior
- Cuenta de Google Earth Engine (gratis para uso académico/investigación)
- Acceso a los assets de GEE mencionados

### Paso 1: Instalar Dependencias

```bash
# Crear entorno virtual (recomendado)
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt
```

### Paso 2: Autenticación con Google Earth Engine

**Primera vez (solo una vez por máquina):**

Al ejecutar el script por primera vez, se abrirá un navegador para autenticar tu cuenta de Google:

```bash
python gee_analysis.py
```

Sigue las instrucciones:
1. Inicia sesión con tu cuenta de Google asociada a GEE
2. Autoriza el acceso
3. Copia el código de autorización si es necesario

Esta autenticación se guarda localmente y no necesitas repetirla.

---

## 💻 Uso

### Ejecución Local

```bash
python gee_analysis.py
```

### Ejecución en Google Colab

1. Sube el archivo `gee_analysis.py` a tu Google Drive o Colab

2. En un notebook de Colab:

```python
# Instalar earthengine-api
!pip install earthengine-api

# Autenticar (solo primera vez)
import ee
ee.Authenticate()

# Ejecutar el script
!python gee_analysis.py
```

3. Descarga los archivos JSON generados desde el directorio `output_json/`

---

## 📊 Archivos de Salida

El script genera 3 archivos JSON en el directorio `output_json/`:

### 1. `areas_2019.json`

Áreas por clase de uso de suelo para el año 2019.

```json
{
  "year": 2019,
  "total_area_ha": 123456.78,
  "clases": {
    "Bosque": {
      "clase_id": 0,
      "nombre": "Bosque",
      "area_ha": 85000.50,
      "color": "#006400"
    },
    ...
  }
}
```

### 2. `areas_2024.json`

Áreas por clase de uso de suelo para el año 2024 (misma estructura que 2019).

### 3. `matriz_transicion.json`

Matriz de transición mostrando cambios de cobertura entre 2019 y 2024.

```json
{
  "year_inicio": 2019,
  "year_fin": 2024,
  "matriz": {
    "Bosque": {
      "Bosque": { "area_ha": 80000.00, "from_id": 0, "to_id": 0 },
      "Agropecuario": { "area_ha": 5000.50, "from_id": 0, "to_id": 2 }
    },
    ...
  },
  "resumen": {
    "area_total_ha": 123456.78,
    "area_cambio_ha": 15000.00,
    "area_estable_ha": 108456.78,
    "porcentaje_cambio": 12.15,
    "porcentaje_estable": 87.85
  }
}
```

---

## 🔧 Configuración Avanzada

Puedes modificar las constantes en `gee_analysis.py` para personalizar el análisis:

```python
# Cambiar años de análisis
YEAR_INICIO = 2015
YEAR_FIN = 2023

# Usar diferente territorio
TCO_ISOSO_ASSET = "users/tu_usuario/tu_territorio"

# Modificar reclasificación
RECLASIFICACION = {
    3: 0,   # Bosque
    # ... agregar o modificar clases
}
```

---

## 📈 Interpretación de Resultados

### Áreas por Clase

- **area_ha**: Área en hectáreas (1 ha = 10,000 m²)
- **total_area_ha**: Suma de todas las áreas clasificadas

### Matriz de Transición

- **Diagonal principal** (ej: Bosque → Bosque): Áreas que permanecieron estables
- **Fuera de la diagonal**: Áreas que cambiaron de clase
- **area_cambio_ha**: Total de hectáreas que cambiaron de clase
- **porcentaje_cambio**: Porcentaje del territorio que experimentó cambios

### Ejemplo de Análisis

Si la matriz muestra:
- `Bosque → Agropecuario: 5000 ha`
  
Significa que **5,000 hectáreas de bosque** fueron convertidas a **uso agropecuario** entre 2019 y 2024.

Esto es relevante para:
- **Cálculo de emisiones de CO₂** (deforestación)
- **Proyectos REDD+** (Reducción de Emisiones por Deforestación y Degradación)
- **Certificación Verra** para créditos de carbono

---

## 🐛 Solución de Problemas

### Error: "User memory limit exceeded"

**Solución**: El territorio es muy grande. El script ya incluye `tileScale=4` para optimizar. Si persiste:

```python
# En la función calcular_areas_por_clase, aumenta tileScale
stats = area_class.reduceRegion(
    reducer=reducer,
    geometry=territorio.geometry(),
    scale=30,
    maxPixels=1e13,
    tileScale=8  # Aumentar de 4 a 8 o 16
)
```

### Error: "Asset not found"

**Causa**: No tienes acceso al asset de GEE.

**Solución**: 
1. Verifica que tu cuenta de GEE esté registrada
2. Para el territorio TCO Isoso, el propietario (`aealfonsom`) debe compartir el asset contigo
3. En la consola de GEE, verifica que puedas ver: `users/aealfonsom/PA_IsosoTituladaTCO`

### El script es muy lento

**Normal**: Los cálculos en GEE pueden tardar 5-15 minutos dependiendo del tamaño del territorio y la carga del servidor.

**Optimizaciones ya incluidas**:
- `tileScale=4`: Procesa en tiles más pequeños
- `scale=30`: Usa la resolución nativa de MapBiomas (30m)
- `.getInfo()`: Solo obtiene datos necesarios

---

## 📚 Referencias

- [MapBiomas Bolivia](https://bolivia.mapbiomas.org/)
- [Google Earth Engine](https://earthengine.google.com/)
- [Documentación GEE Python API](https://developers.google.com/earth-engine/guides/python_install)
- [Estándar Verra VCS](https://verra.org/programs/verified-carbon-standard/)
- [REDD+ Framework](https://redd.unfccc.int/)

---

## 📝 Notas Técnicas

### Resolución Espacial

- **30 metros**: Cada píxel representa 900 m² (0.09 ha)
- Para un territorio de ~100,000 ha, se procesan ~1.1 millones de píxeles

### Precisión

- **Áreas**: Precisión de 0.01 ha (100 m²)
- **Porcentajes**: Precisión de 0.01%
- **Clase -1**: Píxeles no clasificados (raros en MapBiomas)

### Limitaciones

1. **Datos históricos**: MapBiomas Bolivia Collection 3 puede tener lagunas de datos en años específicos
2. **Cobertura de nubes**: Imágenes satelitales pueden tener interferencia de nubes (ya procesadas por MapBiomas)
3. **Resolución temporal**: Análisis anual, no captura cambios intra-anuales

---

## 🤝 Contribuciones

Para reportar errores o sugerir mejoras:
1. Documenta el error con mensaje completo
2. Indica la versión de Python y earthengine-api
3. Comparte el traceback si está disponible

---

## 📄 Licencia

Proyecto desarrollado para análisis de conservación y mercados de carbono en Bolivia.

---

## ✨ Autor

Sistema de análisis geoespacial - Proyecto TCO Isoso  
Fecha: Abril 2026

---

**🌳 ¡Gracias por contribuir a la conservación de los bosques bolivianos!**
