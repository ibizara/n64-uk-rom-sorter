#!/usr/bin/env python3
"""
scan_crc_inventory.py

Recursively scans a directory, computes:
- CRC32 for every file
- a deterministic aggregate CRC32 for every directory

Outputs a CSV inventory with:
type,path,name,size_bytes,file_count,crc32

Notes:
- File CRC32 is the standard CRC32 of file contents.
- Directory CRC32 is a computed signature based on the sorted list of all files
  contained within that directory tree. It is useful for inventory/comparison,
  but it is not a native filesystem property.
"""

from __future__ import annotations

import argparse
import csv
import os
import zlib
from pathlib import Path
from typing import Dict, List, Tuple


def crc32_file(path: Path, chunk_size: int = 1024 * 1024) -> str:
    """Return uppercase 8-char CRC32 for a file."""
    crc = 0
    with path.open("rb") as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            crc = zlib.crc32(chunk, crc)
    return f"{crc & 0xFFFFFFFF:08X}"


def build_directory_signature(file_entries: List[Tuple[str, int, str]]) -> str:
    """
    Build a deterministic CRC32 for a directory from its descendant files.

    Each file contributes:
      relative_path|size_bytes|file_crc32
    Entries are sorted by relative path before hashing.
    """
    crc = 0
    for rel_path, size_bytes, file_crc in sorted(file_entries, key=lambda x: x[0].lower()):
        line = f"{rel_path}|{size_bytes}|{file_crc}\n".encode("utf-8", errors="replace")
        crc = zlib.crc32(line, crc)
    return f"{crc & 0xFFFFFFFF:08X}"


def scan(root: Path) -> List[Dict[str, object]]:
    root = root.resolve()

    files: List[Dict[str, object]] = []
    all_dirs = set()

    for dirpath, dirnames, filenames in os.walk(root):
        current_dir = Path(dirpath)
        all_dirs.add(current_dir)
        for dirname in dirnames:
            all_dirs.add(current_dir / dirname)

        for filename in filenames:
            file_path = current_dir / filename
            rel_path = file_path.relative_to(root).as_posix()
            size = file_path.stat().st_size
            crc = crc32_file(file_path)

            files.append(
                {
                    "type": "file",
                    "path": rel_path,
                    "name": file_path.name,
                    "size_bytes": size,
                    "file_count": "",
                    "crc32": crc,
                    "_abs_path": file_path,
                }
            )

    rows: List[Dict[str, object]] = []

    # Add directory rows
    for directory in sorted(all_dirs, key=lambda p: (len(p.relative_to(root).parts), p.as_posix())):
        rel_dir = "." if directory == root else directory.relative_to(root).as_posix()

        descendant_files: List[Tuple[str, int, str]] = []
        for f in files:
            abs_path = f["_abs_path"]
            try:
                rel_to_dir = abs_path.relative_to(directory)
                descendant_files.append((rel_to_dir.as_posix(), int(f["size_bytes"]), str(f["crc32"])))
            except ValueError:
                continue

        dir_crc = build_directory_signature(descendant_files)
        rows.append(
            {
                "type": "directory",
                "path": rel_dir,
                "name": directory.name if directory != root else root.name,
                "size_bytes": "",
                "file_count": len(descendant_files),
                "crc32": dir_crc,
            }
        )

    # Add file rows
    for f in sorted(files, key=lambda x: str(x["path"]).lower()):
        rows.append(
            {
                "type": "file",
                "path": f["path"],
                "name": f["name"],
                "size_bytes": f["size_bytes"],
                "file_count": "",
                "crc32": f["crc32"],
            }
        )

    return rows


def write_csv(rows: List[Dict[str, object]], output_path: Path) -> None:
    with output_path.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["type", "path", "name", "size_bytes", "file_count", "crc32"],
        )
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Scan a directory recursively and output file/folder CRC32 inventory to CSV."
    )
    parser.add_argument(
        "--directory",
        required=True,
        help="Root directory to scan.",
    )
    parser.add_argument(
        "--output",
        required=True,
        help="Output CSV path.",
    )
    args = parser.parse_args()

    root = Path(args.directory)
    if not root.exists():
        raise SystemExit(f"Directory does not exist: {root}")
    if not root.is_dir():
        raise SystemExit(f"Not a directory: {root}")

    rows = scan(root)
    output_path = Path(args.output)
    write_csv(rows, output_path)

    print(f"Wrote {len(rows)} rows to {output_path}")


if __name__ == "__main__":
    main()
