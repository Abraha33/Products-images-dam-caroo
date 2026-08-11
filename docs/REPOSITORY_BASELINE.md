# Baseline del Repositorio

Fecha: 2026-08-11

## Situación encontrada

El repositorio `Abraha33/Products-images-dam-caroo` ya contenía antes de este proyecto código de un antiguo template/storefront web basado en "Fruitables".

Ese código **no se considera parte del auditor de imágenes** y no se ha borrado, movido ni refactorizado durante la preparación.

## Decisión de aislamiento

El trabajo de auditoría se prepara en la rama:

`plan/auditoria-imagenes-dam`

Esto evita mezclar cambios de gobernanza y auditoría con una limpieza destructiva del legado.

## Regla

No retirar, archivar ni reemplazar el contenido legado de `main` sin una decisión explícita posterior.

## Estructura nueva añadida

- `README.md`
- `.gitignore`
- `config/audit.example.yaml`
- `docs/PLAN_AUDITORIA_IMAGENES_DAM.md`
- `docs/AUDIT_CONTRACT.md`
- `docs/REPOSITORY_BASELINE.md`
- `requirements-audit.txt`
- `src/README.md`
- `scripts/README.md`
- `reports/README.md`
- `.github/pull_request_template.md`

## Estado

El repositorio está preparado para comenzar la **implementación del auditor read-only**, pero todavía no se ha ejecutado ninguna auditoría ni se ha definido la estrategia final de producción de imágenes.
