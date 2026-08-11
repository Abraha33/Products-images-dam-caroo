# Products Images DAM — CAROO / ENVAX

Repositorio de trabajo para llevar el banco visual del catálogo a un estado confiable para el Digital Asset Management (DAM).

## Objetivo

Completar una operación única sobre aproximadamente 1.600 productos para obtener, como mínimo, 4 imágenes base confiables por producto y conservar los activos adicionales útiles correctamente asociados.

La prioridad es **fidelidad al producto real**, no automatización a cualquier costo.

## Estado actual

**Fase actual: preparación de la auditoría.**

Todavía **NO existe una estrategia final de producción aprobada**. Primero se auditará el banco real de imágenes de forma no destructiva; después, con evidencia, se decidirá qué combinación de selección, limpieza, reconstrucción multivista, fuentes externas, IA o fotografía usar.

Plan vigente: [`docs/PLAN_AUDITORIA_IMAGENES_DAM.md`](docs/PLAN_AUDITORIA_IMAGENES_DAM.md)

Seguimiento: GitHub Issue **#1 — Seguimiento — Auditoría de imágenes DAM**.

## Regla de seguridad principal

El auditor debe ser **read-only respecto a las fuentes**:

- no borrar imágenes;
- no moverlas;
- no renombrarlas;
- no sobrescribirlas;
- no editar originales;
- no deduplicar destructivamente;
- todos los resultados deben escribirse en una ruta de salida independiente.

Además, `.gitignore` bloquea por defecto imágenes, datos privados, pesos de modelos y resultados masivos para evitar subir accidentalmente el banco real a GitHub.

## Estructura del proyecto

```text
config/                     Configuración de ejemplo del auditor
docs/                       Plan, contrato y decisiones
reports/                    Solo documentación de reportes; resultados reales quedan locales
scripts/                    Entradas CLI / utilidades futuras
src/                        Implementación futura del auditor
.github/                    Plantillas y controles de colaboración
```

Los archivos históricos del antiguo sitio web que ya existían en la raíz del repositorio **no forman parte del auditor**. Se mantienen intactos por ahora; no se eliminarán ni reorganizarán sin una decisión explícita.

## Orden de trabajo

1. Preparar repositorio y reglas.
2. Confirmar estructura real de las carpetas y catálogo maestro.
3. Implementar auditor técnico determinista.
4. Ejecutar auditoría sin modificar fuentes.
5. Añadir auditoría visual donde aporte evidencia.
6. Diagnosticar cobertura real por producto.
7. Definir estrategia de producción.
8. Validarla con un piloto.
9. Ejecutar producción masiva y cargar al DAM.

## Importante

No se debe entrenar un modelo propio, quitar fondos masivamente, fabricar vistas, buscar faltantes de forma masiva ni reorganizar las imágenes antes de terminar el diagnóstico de la auditoría.
