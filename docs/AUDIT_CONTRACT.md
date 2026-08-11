# Contrato de Auditoría

Este documento define las condiciones mínimas que debe cumplir cualquier implementación del auditor antes de ejecutarse sobre el banco real de imágenes.

## 1. Invariantes no negociables

1. Las fuentes son de solo lectura.
2. Ningún archivo fuente puede borrarse, moverse, renombrarse, editarse ni sobrescribirse.
3. Cada resultado debe conservar trazabilidad hasta la ruta y nombre original.
4. Los errores deben registrarse; nunca ocultarse ni resolverse destruyendo evidencia.
5. La salida debe escribirse fuera del árbol de imágenes fuente.
6. El auditor debe poder reejecutarse con la misma configuración.
7. La auditoría diagnostica; no produce todavía las cuatro imágenes maestras finales.

## 2. Entradas

### Banco de imágenes

Una o más rutas locales que contienen imágenes agrupadas por producto cuando sea posible.

### Catálogo maestro

Fuente estructurada con, idealmente:

- SKU / ID oficial
- nombre
- marca
- categoría / familia
- referencia
- material
- color
- medida / capacidad
- presentación
- EAN / UPC cuando exista

La identidad oficial del producto debe provenir del catálogo cuando esté disponible; no se debe inferir un atributo crítico desde una fotografía si existe una fuente maestra más confiable.

## 3. Salidas mínimas

El auditor deberá poder generar:

- `inventory.csv`
- `products_summary.csv`
- `duplicates_exact.csv`
- `duplicates_visual.csv`
- `quality_flags.csv`
- `coverage_by_product.csv`
- `audit_summary.md`
- `audit_config.json`
- `audit_errors.log`

Los resultados reales no se subirán automáticamente a GitHub.

## 4. Pruebas obligatorias antes del banco real

Antes de apuntar el auditor al banco completo debe demostrarse, con un fixture pequeño y controlado, que:

- no modifica timestamps ni bytes de las fuentes;
- no crea archivos dentro de las carpetas fuente;
- tolera archivos corruptos sin detener todo el proceso;
- reporta extensiones no soportadas;
- produce hashes reproducibles;
- puede reanudarse o repetirse sin duplicar/dañar resultados;
- registra configuración y errores.

## 5. Separación por capas

### Capa A — Determinista

Inventario, metadatos, integridad, hashes y agrupación conocida. Debe ser la primera en ejecutarse.

### Capa B — Heurística visual

Calidad, similitud, fondo, diversidad de vistas y señales de mezcla de SKU. Toda clasificación debe incluir confianza o quedar marcada como incierta.

### Capa C — Diagnóstico

Resume cada producto por cobertura y dificultad. No ejecuta todavía eliminación de fondo, reconstrucción, generación ni búsqueda externa.

## 6. Criterio para declarar la auditoría lista

La auditoría solo estará lista para ejecución masiva cuando:

- las rutas de entrada y salida estén claramente separadas;
- exista prueba no destructiva sobre fixtures;
- el catálogo maestro pueda cruzarse de forma trazable;
- los outputs mínimos estén definidos;
- los errores no interrumpan el lote completo;
- la configuración utilizada quede registrada;
- exista un comando de ejecución reproducible.

## 7. Lo que queda fuera de este contrato

La estrategia final de producción, eliminación masiva de fondos, reconstrucción multivista, generación asistida, fotografía nueva, búsqueda externa y carga al DAM se decidirán después de la auditoría y del piloto correspondiente.
