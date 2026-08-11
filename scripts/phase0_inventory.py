#!/usr/bin/env python3
"""ENVAX DAM - Fase 0.

Auditor tecnico READ-ONLY del banco de archivos. Nunca mueve, renombra,
borra ni modifica archivos fuente. Solo escribe reportes en --output.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import sys
import time
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import asdict, dataclass, fields
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from PIL import Image, ImageOps
import imagehash

try:
    from pillow_heif import register_heif_opener
    register_heif_opener()
except Exception:
    pass

IMAGE_EXTENSIONS = {
    ".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tif", ".tiff",
    ".gif", ".avif", ".heic", ".heif"
}


def utc_iso(ts: Optional[float] = None) -> str:
    dt = datetime.now(timezone.utc) if ts is None else datetime.fromtimestamp(ts, timezone.utc)
    return dt.isoformat()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def has_real_alpha(img: Image.Image) -> bool:
    if "A" in img.getbands():
        return img.getchannel("A").getextrema() != (255, 255)
    return img.mode == "P" and "transparency" in img.info


@dataclass
class Record:
    relative_path: str
    absolute_path: str
    filename: str
    extension: str
    parent_folder: str
    top_level_folder: str
    size_bytes: Optional[int]
    modified_utc: str
    image_candidate: bool
    readable_image: Optional[bool]
    width_px: Optional[int]
    height_px: Optional[int]
    aspect_ratio: Optional[float]
    image_format: str
    image_mode: str
    has_transparency: Optional[bool]
    exif_orientation: Optional[int]
    sha256: str
    phash: str
    error: str


def inspect_file(path: Path, root: Path) -> Record:
    rel = path.relative_to(root)
    ext = path.suffix.lower()
    candidate = ext in IMAGE_EXTENSIONS
    errors = []
    size = None
    modified = ""
    sha = ""
    readable = None
    width = height = None
    ratio = None
    fmt = mode = ph = ""
    alpha = None
    orientation = None

    try:
        stat = path.stat()
        size = stat.st_size
        modified = utc_iso(stat.st_mtime)
    except Exception as exc:
        errors.append(f"stat:{type(exc).__name__}:{exc}")

    try:
        sha = sha256_file(path)
    except Exception as exc:
        errors.append(f"sha256:{type(exc).__name__}:{exc}")

    if candidate:
        try:
            with Image.open(path) as img:
                fmt = img.format or ""
                mode = img.mode
                width, height = img.size
                ratio = round(width / height, 6) if height else None
                alpha = has_real_alpha(img)
                try:
                    value = img.getexif().get(274)
                    orientation = int(value) if value is not None else None
                except Exception:
                    orientation = None
                normalized = ImageOps.exif_transpose(img).convert("RGB")
                ph = str(imagehash.phash(normalized))
                readable = True
        except Exception as exc:
            readable = False
            errors.append(f"image:{type(exc).__name__}:{exc}")

    parts = rel.parts
    return Record(
        relative_path=str(rel),
        absolute_path=str(path.resolve()),
        filename=path.name,
        extension=ext,
        parent_folder=path.parent.name,
        top_level_folder=parts[0] if len(parts) > 1 else "",
        size_bytes=size,
        modified_utc=modified,
        image_candidate=candidate,
        readable_image=readable,
        width_px=width,
        height_px=height,
        aspect_ratio=ratio,
        image_format=fmt,
        image_mode=mode,
        has_transparency=alpha,
        exif_orientation=orientation,
        sha256=sha,
        phash=ph,
        error=" | ".join(errors),
    )


def write_csv(path: Path, rows: list[dict], columns: list[str]) -> None:
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)


def exact_duplicates(records: list[Record]) -> list[dict]:
    groups = defaultdict(list)
    for r in records:
        if r.sha256:
            groups[r.sha256].append(r)
    rows = []
    n = 0
    for sha, members in groups.items():
        if len(members) < 2:
            continue
        n += 1
        for r in members:
            rows.append({"group_id": f"EXACT-{n:06d}", "sha256": sha,
                         "relative_path": r.relative_path, "size_bytes": r.size_bytes})
    return rows


def visual_duplicates(records: list[Record], max_distance: int) -> list[dict]:
    """Agrupa candidatos por pHash. O(n^2) solo dentro de buckets de 12 bits.

    Es deliberadamente conservador: puede omitir algun casi-duplicado que cruce
    buckets, pero evita explotar en costo con bancos grandes. No se usa para borrar.
    """
    buckets = defaultdict(list)
    for r in records:
        if r.phash:
            buckets[r.phash[:3]].append(r)

    rows = []
    group_n = 0
    visited = set()
    for members in buckets.values():
        for i, a in enumerate(members):
            if a.relative_path in visited:
                continue
            cluster = [a]
            ha = int(a.phash, 16)
            for b in members[i + 1:]:
                if b.sha256 == a.sha256:
                    continue
                distance = (ha ^ int(b.phash, 16)).bit_count()
                if distance <= max_distance:
                    cluster.append(b)
            if len(cluster) < 2:
                continue
            group_n += 1
            for r in cluster:
                visited.add(r.relative_path)
                rows.append({
                    "group_id": f"VISUAL-{group_n:06d}",
                    "relative_path": r.relative_path,
                    "phash": r.phash,
                    "distance_to_seed": (ha ^ int(r.phash, 16)).bit_count(),
                    "sha256": r.sha256,
                    "width_px": r.width_px,
                    "height_px": r.height_px,
                })
    return rows


def folder_summary(records: list[Record]) -> list[dict]:
    out = {}
    for r in records:
        key = r.top_level_folder or "(ROOT)"
        s = out.setdefault(key, {"top_level_folder": key, "files_total": 0,
            "image_candidates": 0, "readable_images": 0, "unreadable_images": 0,
            "bytes_total": 0})
        s["files_total"] += 1
        s["bytes_total"] += r.size_bytes or 0
        if r.image_candidate:
            s["image_candidates"] += 1
            if r.readable_image is True:
                s["readable_images"] += 1
            elif r.readable_image is False:
                s["unreadable_images"] += 1
    return sorted(out.values(), key=lambda x: (-x["files_total"], x["top_level_folder"].lower()))


def main() -> int:
    ap = argparse.ArgumentParser(description="ENVAX DAM Fase 0 - auditor READ-ONLY")
    ap.add_argument("--input", required=True, help="Raiz del banco de archivos")
    ap.add_argument("--output", required=True, help="Carpeta separada para reportes")
    ap.add_argument("--workers", type=int, default=max(2, min(8, os.cpu_count() or 4)))
    ap.add_argument("--phash-distance", type=int, default=5)
    args = ap.parse_args()

    root = Path(args.input).expanduser().resolve()
    output = Path(args.output).expanduser().resolve()
    if not root.is_dir():
        print(f"ERROR: no existe la carpeta fuente: {root}", file=sys.stderr)
        return 2
    if root == output:
        print("ERROR: --output debe ser distinto de --input", file=sys.stderr)
        return 2
    if not 0 <= args.phash_distance <= 16:
        print("ERROR: --phash-distance debe estar entre 0 y 16", file=sys.stderr)
        return 2

    output.mkdir(parents=True, exist_ok=True)
    start = time.time()

    def inside_output(p: Path) -> bool:
        try:
            resolved = p.resolve()
            return resolved == output or output in resolved.parents
        except Exception:
            return False

    paths = []
    for dirpath, dirnames, filenames in os.walk(root):
        current = Path(dirpath)
        dirnames[:] = [d for d in dirnames if not inside_output(current / d)]
        paths.extend(current / name for name in filenames if not inside_output(current / name))

    print(f"Archivos encontrados: {len(paths):,}")
    records = []
    unhandled = []
    with ThreadPoolExecutor(max_workers=max(1, args.workers)) as pool:
        futures = {pool.submit(inspect_file, p, root): p for p in paths}
        done = 0
        for future in as_completed(futures):
            p = futures[future]
            try:
                records.append(future.result())
            except Exception as exc:
                unhandled.append(f"{p}\t{type(exc).__name__}: {exc}")
            done += 1
            if done % 1000 == 0 or done == len(paths):
                print(f"Analizados: {done:,}/{len(paths):,}")

    records.sort(key=lambda r: r.relative_path.lower())
    inventory_cols = [f.name for f in fields(Record)]
    write_csv(output / "inventory.csv", [asdict(r) for r in records], inventory_cols)

    exact = exact_duplicates(records)
    write_csv(output / "duplicates_exact.csv", exact,
              ["group_id", "sha256", "relative_path", "size_bytes"])
    visual = visual_duplicates(records, args.phash_distance)
    write_csv(output / "duplicates_visual.csv", visual,
              ["group_id", "relative_path", "phash", "distance_to_seed", "sha256", "width_px", "height_px"])
    folders = folder_summary(records)
    write_csv(output / "folder_summary.csv", folders,
              ["top_level_folder", "files_total", "image_candidates", "readable_images", "unreadable_images", "bytes_total"])

    errors = unhandled + [f"{r.relative_path}\t{r.error}" for r in records if r.error]
    (output / "audit_errors.log").write_text("\n".join(errors) + ("\n" if errors else ""), encoding="utf-8")

    config = {
        "generated_utc": utc_iso(), "input_root": str(root), "output_dir": str(output),
        "workers": args.workers, "phash_distance": args.phash_distance,
        "read_only_source_policy": True, "script_version": "0.1.0",
        "image_extensions": sorted(IMAGE_EXTENSIONS), "python": sys.version,
    }
    (output / "audit_config.json").write_text(json.dumps(config, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    exact_groups = len({x["group_id"] for x in exact})
    visual_groups = len({x["group_id"] for x in visual})
    images = sum(r.image_candidate for r in records)
    readable = sum(r.readable_image is True for r in records)
    unreadable = sum(r.readable_image is False for r in records)
    gib = sum(r.size_bytes or 0 for r in records) / (1024 ** 3)
    elapsed = time.time() - start
    summary = f"""# Fase 0 - resultado tecnico\n\n- Fuente: `{root}`\n- Archivos: **{len(records):,}**\n- Candidatos a imagen: **{images:,}**\n- Imagenes legibles: **{readable:,}**\n- Imagenes no legibles: **{unreadable:,}**\n- Volumen inventariado: **{gib:.2f} GiB**\n- Grupos duplicados exactos: **{exact_groups:,}**\n- Grupos visuales candidatos: **{visual_groups:,}**\n- Duracion: **{elapsed:.1f} s**\n\n## Regla\nEste barrido no mueve, renombra, borra ni edita archivos fuente. Los duplicados visuales son candidatos para revision, nunca una orden de borrado.\n"""
    (output / "audit_summary.md").write_text(summary, encoding="utf-8")

    print(f"Listo: {output}")
    print("Fuente intacta: no se movio, renombro, borro ni edito ningun archivo.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
