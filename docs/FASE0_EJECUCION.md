# Fase 0 — Ingesta y triage técnico READ-ONLY

## Propósito

Convertir el desorden actual de archivos en un inventario técnico reproducible **sin organizar manualmente y sin modificar los originales**.

Esta fase NO identifica todavía cuál es la vista frontal, lateral, superior o hero; tampoco decide la estrategia final de producción. Su única función es saber con precisión qué existe, dónde está y cuánta redundancia técnica hay.

## Política de seguridad

El auditor:

- NO mueve archivos fuente.
- NO renombra archivos fuente.
- NO borra archivos fuente.
- NO edita imágenes fuente.
- NO sobrescribe archivos fuente.
- Solo abre los archivos en modo lectura y escribe resultados en una carpeta de salida separada.

Incluso los duplicados exactos o visuales se reportan; **no se eliminan automáticamente**.

## Qué produce

- `inventory.csv`: una fila por archivo con ruta original, tamaño, extensión, hash SHA-256 y, cuando sea imagen legible, dimensiones, formato, modo, transparencia, EXIF orientation y pHash.
- `folder_summary.csv`: resumen de la estructura actual por carpeta superior.
- `duplicates_exact.csv`: grupos de archivos byte-a-byte idénticos.
- `duplicates_visual.csv`: candidatos visualmente similares mediante pHash. Es una señal conservadora, no una orden de borrado.
- `audit_config.json`: parámetros de ejecución y trazabilidad.
- `audit_errors.log`: archivos que no pudieron leerse o analizarse correctamente.
- `audit_summary.md`: resumen humano de la corrida.

## Ejecución en Windows

Desde PowerShell, estando en la raíz del repositorio:

```powershell
powershell -ExecutionPolicy Bypass -File ".\scripts\run_phase0.ps1" `
  -InputPath "D:\RUTA\A\TODAS\LAS\IMAGENES"
```

Si no se indica `-OutputPath`, el lanzador crea una carpeta hermana llamada aproximadamente `ENVAX_AUDIT_YYYYMMDD-HHMMSS`.

Para fijar la salida explícitamente:

```powershell
powershell -ExecutionPolicy Bypass -File ".\scripts\run_phase0.ps1" `
  -InputPath "D:\RUTA\A\TODAS\LAS\IMAGENES" `
  -OutputPath "D:\Caroo\audits\imagenes-fase0"
```

El lanzador crea un entorno Python aislado bajo `%LOCALAPPDATA%\envax-phase0-audit-venv` e instala solamente las dependencias indicadas en `requirements-phase0.txt`.

## Formatos

Se intentan analizar como imagen: JPG/JPEG, PNG, WEBP, BMP, TIFF, GIF, AVIF, HEIC y HEIF. Si un archivo no puede ser decodificado, **no se detiene toda la corrida**: queda inventariado y el error se registra.

## Duplicados visuales: limitación deliberada

La primera versión utiliza pHash y agrupación conservadora para evitar comparaciones exhaustivas de costo cuadrático sobre bancos muy grandes. Puede omitir algunos casi-duplicados; esto es preferible en Fase 0 a producir falsos criterios de eliminación.

La detección visual más fuerte se puede ejecutar después, sobre el universo ya medido y reducido.

## Qué compartir después de ejecutarlo

Idealmente, compartir la carpeta completa de salida. Como mínimo:

1. `audit_summary.md`
2. `folder_summary.csv`
3. `inventory.csv`
4. `duplicates_exact.csv`
5. `duplicates_visual.csv`
6. `audit_errors.log`

Con esos resultados se cierra la estructura real del banco y se decide qué debe entrar a la auditoría visual de Fase 2.

## Criterio de éxito de Fase 0

No es “tener las imágenes organizadas”. Es poder responder con evidencia:

- cuántos archivos existen realmente;
- cuántos son imágenes legibles;
- cuánto espacio ocupan;
- dónde están;
- cuánta duplicación exacta existe;
- qué redundancia visual probable existe;
- qué formatos o archivos presentan problemas;
- cuál es la estructura real que heredamos.

Solo después de eso se diseña la organización lógica por producto/SKU.
