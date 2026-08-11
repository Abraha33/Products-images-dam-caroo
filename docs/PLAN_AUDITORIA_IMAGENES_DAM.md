# Plan de Auditoría de Imágenes para DAM

Estado: **ACTIVO — estrategia final aún no definida**  
Repositorio: `Abraha33/Products-images-dam-caroo`  
Última actualización: 2026-08-11

## 1. Objetivo fijo

El objetivo del proyecto no es construir un sistema permanente de procesamiento de imágenes, sino completar una operación única para dejar el DAM con activos base confiables para el catálogo.

Meta mínima:

- Aproximadamente 1.600 productos.
- Al menos 4 imágenes base por producto.
- Las imágenes base deben ser reutilizables para ecommerce, catálogos, blogs, publicaciones, diseño y otros canales.
- Los activos adicionales útiles deben conservarse y quedar correctamente asociados al producto.
- La fidelidad al producto real tiene prioridad sobre la automatización.

## 2. Decisión actual

**No existe todavía una estrategia final de producción aprobada.**

Primero se realizará una auditoría profunda, no destructiva y reproducible del banco real de imágenes. La estrategia se definirá después usando los resultados de esa auditoría, en lugar de imponer una técnica única basada en supuestos.

## 3. Principios de la auditoría

1. **Read-only:** no borrar, mover, renombrar, editar ni sobrescribir imágenes fuente.
2. **Trazabilidad:** cada resultado debe poder rastrearse hasta el archivo original.
3. **Producto primero:** el análisis debe poder resumirse por SKU/ID/producto.
4. **No confundir diagnóstico con producción:** durante la auditoría no se generan aún las cuatro imágenes finales.
5. **Medición antes de decidir:** las herramientas de limpieza, selección, reconstrucción, IA, fuentes externas o fotografía se escogerán después de medir el banco real.
6. **Detección de fallos:** la auditoría debe identificar explícitamente los casos que no son resolubles de forma automática.

## 4. Entradas esperadas

### 4.1 Catálogo maestro

Por producto, idealmente:

- SKU / ID oficial
- nombre del producto
- marca
- categoría / familia
- referencia
- material
- color
- medida / capacidad
- presentación
- EAN / UPC, cuando exista

Los atributos críticos no deben inferirse desde las imágenes si pueden cruzarse contra el catálogo maestro.

### 4.2 Banco de imágenes

Las imágenes deberían llegar agrupadas por producto siempre que sea posible, conservando el nombre original de cada archivo.

La auditoría debe tolerar:

- JPG / JPEG
- PNG
- WEBP y otros formatos habituales
- fotos tomadas por teléfono
- imágenes obtenidas de internet o fabricantes
- miniaturas
- derivados
- duplicados
- imágenes con fondo
- productos transparentes, translúcidos, blancos o brillantes
- imágenes de calidad desigual

## 5. Qué debe medir la auditoría

### 5.1 Inventario técnico

Por archivo:

- ruta
- nombre original
- extensión
- tamaño en bytes
- dimensiones en píxeles
- relación de aspecto
- orientación
- canal alfa / transparencia
- EXIF cuando exista
- capacidad de lectura / archivo corrupto

### 5.2 Duplicados

Detectar por separado:

- duplicados exactos mediante hash criptográfico
- duplicados visuales o casi duplicados mediante hash perceptual / similitud
- posibles derivados de una misma imagen

No borrar nada durante la auditoría.

### 5.3 Calidad visual

Estimar, sin modificar el original:

- resolución útil
- desenfoque
- ruido
- sobreexposición / subexposición
- compresión severa
- recorte del producto
- producto parcialmente fuera del cuadro
- cantidad aproximada del encuadre ocupada por el producto

### 5.4 Fondo y dificultad de aislamiento

Clasificar aproximadamente:

- fondo simple
- fondo complejo
- fondo ya transparente
- producto blanco sobre fondo claro
- producto transparente / translúcido
- producto reflectivo / brillante
- bordes difíciles

Esto permitirá predecir qué tan viable será una futura eliminación masiva de fondos.

### 5.5 Cobertura visual y vistas

Por producto, estimar qué evidencia visual existe para:

- vista principal / hero 3/4
- frontal
- lateral / posterior
- superior / interior / detalle funcional
- otras vistas adicionales

La clasificación inicial puede ser probabilística; no debe declararse una vista como definitiva si la confianza es baja.

### 5.6 Diversidad visual

Medir por producto:

- número de imágenes totales
- número de imágenes únicas
- número de grupos visuales distintos
- similitud entre imágenes
- diversidad probable de ángulos
- si existen suficientes vistas compatibles para estudiar reconstrucción multivista

### 5.7 Riesgos de identidad

Detectar señales de:

- múltiples productos distintos dentro de una misma carpeta
- diferencias de color, medida, referencia o presentación
- imágenes de empaque que podrían no corresponder exactamente al SKU
- archivos posiblemente asociados al producto equivocado

La auditoría debe marcar estos casos para revisión; no corregirlos automáticamente sin evidencia suficiente.

## 6. Resultado esperado por producto

Cada producto debe terminar la auditoría con un registro que permita clasificarlo, provisionalmente, en una o más rutas:

### A. Cobertura suficiente existente
Ya existen cuatro o más vistas potencialmente utilizables.

### B. Cobertura suficiente tras limpieza
El material parece suficiente, pero requiere aislamiento de fondo, recorte, orientación u otras correcciones básicas.

### C. Candidato a reconstrucción multivista
Hay múltiples imágenes del mismo producto y suficiente diversidad de ángulos como para evaluar herramientas como VGGT / COLMAP / técnicas relacionadas.

### D. Cobertura parcial
Hay imágenes útiles, pero faltan una o más vistas.

### E. Fuente externa probablemente necesaria
El banco interno no contiene suficiente evidencia.

### F. Fotografía nueva probablemente necesaria
No existe material fiable suficiente o la identidad no puede garantizarse mediante otras fuentes.

### G. Caso ambiguo / riesgo de SKU incorrecto
Debe resolverse la identidad antes de producir activos maestros.

Estas categorías son diagnóstico, no estrategia final.

## 7. Entregables de la auditoría

La primera versión deberá generar, como mínimo:

1. `inventory.csv` — inventario completo de archivos.
2. `products_summary.csv` — resumen por producto/SKU.
3. `duplicates_exact.csv` — grupos de duplicados exactos.
4. `duplicates_visual.csv` — posibles duplicados/casi duplicados visuales.
5. `quality_flags.csv` — problemas técnicos o visuales detectados.
6. `coverage_by_product.csv` — cobertura probable de vistas.
7. `audit_summary.md` — diagnóstico global legible por humanos.
8. `audit_config.json` — parámetros utilizados para que la auditoría sea reproducible.
9. `audit_errors.log` — archivos que no pudieron analizarse y motivo.

Los nombres pueden evolucionar, pero la información anterior debe conservarse.

## 8. Fases

### Fase 0 — Preparación

- [ ] Confirmar estructura real de carpetas de imágenes.
- [ ] Confirmar formato y ubicación del catálogo maestro.
- [ ] Definir una carpeta separada de salida para la auditoría.
- [ ] Registrar número aproximado de productos y archivos.

**Criterio de salida:** las fuentes están identificadas y el auditor puede ejecutarse sin tocar originales.

### Fase 1 — Auditor técnico determinista

- [ ] Inventario de archivos.
- [ ] Metadatos técnicos.
- [ ] Integridad / corrupción.
- [ ] Hash exacto.
- [ ] Hash perceptual.
- [ ] Agrupación por producto según estructura disponible.

**Criterio de salida:** sabemos qué archivos existen realmente y cuánta redundancia contienen.

### Fase 2 — Auditor visual

- [ ] Calidad básica.
- [ ] Complejidad de fondo.
- [ ] transparencia / translucidez / reflejos.
- [ ] similitud visual.
- [ ] diversidad probable de ángulos.
- [ ] cobertura probable de las cuatro vistas objetivo.
- [ ] señales de mezcla de productos.

**Criterio de salida:** cada producto posee un diagnóstico de cobertura y dificultad.

### Fase 3 — Diagnóstico global

- [ ] Distribución de productos por ruta A–G.
- [ ] Porcentaje con 4 vistas potenciales ya presentes.
- [ ] Porcentaje resoluble aparentemente con limpieza básica.
- [ ] Porcentaje candidato a reconstrucción multivista.
- [ ] Porcentaje con faltantes reales.
- [ ] Incidencia de transparentes/translúcidos/brillantes.
- [ ] Incidencia de posibles errores de identidad.

**Criterio de salida:** existe evidencia suficiente para diseñar la estrategia de producción.

### Fase 4 — Definición de estrategia

**NO EJECUTAR antes de cerrar Fase 3.**

Con los resultados reales se decidirá qué combinación utilizar de:

- selección de imágenes existentes
- eliminación de fondo
- normalización
- corrección ligera
- herramientas multivista / reconstrucción
- fuentes oficiales externas
- proveedores / distribuidores
- generación asistida, únicamente cuando pueda validarse fidelidad
- fotografía nueva

La estrategia puede ser diferente por familia de productos o por tipo de caso.

### Fase 5 — Piloto

- [ ] Seleccionar una muestra representativa de productos fáciles, medianos y difíciles.
- [ ] Ejecutar la estrategia propuesta.
- [ ] Medir cobertura, fidelidad, fallos, costo computacional e intervención humana.
- [ ] Ajustar reglas.

**Criterio de salida:** una estrategia validada empíricamente y no solo teóricamente.

### Fase 6 — Producción masiva

Pendiente de definir después del piloto.

### Fase 7 — Control de calidad y DAM

Pendiente de definir después del piloto.

## 9. Estándar maestro provisional de imagen

Este estándar es una hipótesis de trabajo y deberá validarse antes de producción masiva:

- PNG con transparencia alfa
- 3000 × 3000 px
- relación 1:1
- sRGB
- producto aproximadamente 80–90 % del encuadre
- sin fondo incorporado
- sin textos añadidos
- sin marca de agua
- sin bordes
- sin sombra artificial incorporada como parte obligatoria

Las cuatro posiciones objetivo provisionales son:

1. HERO / 3/4
2. FRONT / frontal
3. SIDE-BACK / lateral o posterior según el producto
4. TOP-DETAIL / superior, interior o detalle funcional

No se debe forzar el mismo ángulo exacto a categorías cuya función visual requiera otra vista.

## 10. Herramientas candidatas — no aprobadas todavía como pipeline

### Auditoría determinista

- Python
- Pillow
- OpenCV
- hashes criptográficos
- pHash / dHash u otro hash perceptual

### Segmentación / eliminación futura de fondos

Candidatas:

- `rembg`
- SAM / SAM 2 u otros modelos de segmentación

Advertencia: no asumir automatización perfecta en plástico transparente, translúcido, blanco o reflectivo.

### Reconstrucción / multivista

Candidatas a evaluar cuando la auditoría confirme suficiente evidencia:

- VGGT / variantes compatibles
- COLMAP
- Meshroom / AliceVision
- técnicas de reconstrucción / representación 3D relacionadas

Advertencia: no asumir que reconstrucción multivista produce una representación comercial fiel en todos los productos, especialmente objetos transparentes, reflectivos o con poca textura.

## 11. Qué NO se hará todavía

- No borrar duplicados.
- No editar masivamente originales.
- No remover fondos del banco completo.
- No fabricar automáticamente las cuatro vistas.
- No entrenar un modelo propio.
- No buscar faltantes en internet de manera masiva.
- No reorganizar destructivamente las carpetas.
- No cargar derivados al DAM.
- No declarar una herramienta como solución universal.

## 12. Métricas para decidir la estrategia después

Como mínimo se medirá:

- cobertura actual de 4 vistas por producto
- cobertura potencial después de limpieza
- porcentaje de duplicación
- porcentaje de archivos inutilizables
- porcentaje de productos con suficiente diversidad multivista
- porcentaje de productos con dificultad alta de segmentación
- porcentaje de productos que requieren fuentes externas
- porcentaje que probablemente requiere fotografía nueva
- tasa de ambigüedad de identidad/SKU

Durante el piloto se añadirán:

- fidelidad visual
- tasa de aprobación automática
- tasa de revisión humana
- tasa de error
- tiempo/costo por producto

## 13. Registro de decisiones

| ID | Decisión | Estado |
|---|---|---|
| IMG-001 | Meta mínima de 4 imágenes base por producto | Aprobada |
| IMG-002 | Conservar activos adicionales útiles | Aprobada |
| IMG-003 | Auditar antes de definir estrategia final | Aprobada |
| IMG-004 | Auditoría inicial 100 % no destructiva | Aprobada |
| IMG-005 | No entrenar un modelo propio antes de tener evidencia | Vigente |
| IMG-006 | No asumir una única técnica para todos los SKU | Vigente |
| IMG-007 | Estándar PNG 3000×3000 transparente | Provisional; validar antes de producción |
| IMG-008 | Estrategia final de producción | Pendiente de auditoría |

## 14. Estado actual

**Etapa actual: diseño y construcción de la auditoría.**

La próxima acción técnica es construir el auditor read-only y ejecutarlo sobre el banco real de imágenes. El resultado de esa ejecución será la entrada formal para definir la estrategia de producción de las cuatro imágenes maestras por producto.
