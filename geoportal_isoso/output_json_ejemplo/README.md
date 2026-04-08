# 📊 Datos JSON de Ejemplo

## Descripción

Este directorio contiene **datos de ejemplo** para demostrar el formato y estructura de los archivos JSON generados por el análisis de Google Earth Engine.

⚠️ **IMPORTANTE**: Estos son datos ficticios con propósitos de prueba y desarrollo. Para el análisis real del territorio TCO Isoso, ejecuta el script `gee_analysis.py`.

---

## Archivos Incluidos

### `areas_2019.json`
Áreas por clase de uso de suelo para el año 2019.

**Datos de ejemplo:**
- Área total: 135,487.62 ha
- Bosque: 98,542.35 ha (72.7%)
- Herbazal/Arbustal: 28,734.18 ha (21.2%)
- Agropecuario: 7,245.89 ha (5.3%)
- Área sin vegetación: 853.42 ha (0.6%)
- Cuerpos de agua: 111.78 ha (0.1%)

### `areas_2024.json`
Áreas por clase de uso de suelo para el año 2024.

**Datos de ejemplo:**
- Área total: 135,487.62 ha
- Bosque: 93,128.74 ha (68.7%) ↓ -5.5%
- Herbazal/Arbustal: 31,245.63 ha (23.1%) ↑ +8.7%
- Agropecuario: 10,158.27 ha (7.5%) ↑ +40.2%
- Área sin vegetación: 841.36 ha (0.6%) ≈ -1.4%
- Cuerpos de agua: 113.62 ha (0.1%) ≈ +1.6%

### `matriz_transicion.json`
Matriz de transición que muestra cómo cambiaron las clases entre 2019 y 2024.

**Cambios significativos (>1000 ha):**
- Bosque → Herbazal/Arbustal: 4,523.68 ha (degradación)
- Bosque → Agropecuario: 3,089.45 ha (deforestación)
- Herbazal → Bosque: 2,283.42 ha (regeneración)
- Agropecuario → Herbazal: 2,381.48 ha (abandono)

**Resumen:**
- Total cambios: 13,204.75 ha (9.75%)
- Área estable: 122,282.87 ha (90.25%)

---

## Uso

### Para Testing del Dashboard

```javascript
// Cargar datos de ejemplo en lugar de los reales
const datosEjemplo = {
  areas2019: require('./output_json_ejemplo/areas_2019.json'),
  areas2024: require('./output_json_ejemplo/areas_2024.json'),
  matrizTransicion: require('./output_json_ejemplo/matriz_transicion.json')
};

// Usar en tu dashboard
inicializarDashboard(datosEjemplo);
```

### Para Validación del Script

```bash
# Validar estructura de los JSONs de ejemplo
python validar_json.py

# Generar reporte de ejemplo
python ejemplo_leer_json.py
```

### Para Desarrollo

Usa estos archivos para:
1. ✅ Desarrollar componentes del dashboard sin esperar el análisis de GEE
2. ✅ Probar funciones de visualización
3. ✅ Validar la integración con el frontend
4. ✅ Generar maquetas y prototipos

---

## Características de los Datos

### Realismo

Los datos de ejemplo están diseñados para ser **realistas** y reflejar:
- Patrones típicos de deforestación en Bolivia
- Expansión agropecuaria
- Degradación forestal a herbazal
- Regeneración natural moderada
- Estabilidad de cuerpos de agua y áreas sin vegetación

### Consistencia

Los archivos mantienen consistencia:
- ✅ Las áreas totales coinciden entre 2019 y 2024
- ✅ La suma de transiciones en la matriz = área total
- ✅ Los porcentajes de cambio/estable suman 100%
- ✅ Los IDs de clase son correctos (0-4)
- ✅ Los colores coinciden con la paleta del proyecto

---

## Diferencias con Datos Reales

Los datos reales del análisis de GEE pueden diferir en:

1. **Áreas exactas**: Los valores reales dependen de la resolución y procesamiento de MapBiomas
2. **Patrones de cambio**: Las transiciones reales pueden ser diferentes
3. **Precisión**: Los datos reales tienen hasta 0.01 ha de precisión
4. **Clases presentes**: Algunas clases pueden no estar presentes en el territorio

---

## 🚨 Descargo de Responsabilidad

Estos datos son **ficticios** y solo para:
- ✅ Pruebas de desarrollo
- ✅ Demostraciones
- ✅ Validación de formato
- ✅ Prototipos de interfaz

❌ **NO usar para:**
- Análisis científico
- Reportes oficiales
- Toma de decisiones
- Proyectos REDD+/Verra

Para datos reales, ejecuta `gee_analysis.py` con tu cuenta de Google Earth Engine.

---

## Generación de Nuevos Datos de Ejemplo

Si necesitas generar nuevos datos de ejemplo con diferentes parámetros:

```python
# Usa el script gee_analysis.py con un territorio más pequeño
# y copia los resultados a este directorio

# O genera datos sintéticos con un script personalizado
import json
import random

# ... código para generar datos aleatorios pero consistentes
```

---

**📊 Proyecto**: Geoportal TCO Isoso  
**🎯 Propósito**: Datos de ejemplo para desarrollo  
**⚠️ Estado**: Datos ficticios - NO usar para producción
