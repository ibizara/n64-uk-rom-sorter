# N64 UK ROM Sorter

An **N64 ROM sorter** that organises ROMs using a **UK / Europe-first** region priority, with **USA** as the second choice and **Japan** as the final fallback when building out a more complete set.

It is aimed at anyone who wants an **N64 collection focused on UK / Europe releases** without leaving gaps where a game only exists in another region.

The included spreadsheet and Python script can also be adjusted if you want to change the sorting logic or use a different region order.

## What this repo does

- converts supported N64 ROM formats to `.n64`
- sorts N64 ROMs using the included game list spreadsheet
- places matched ROMs into region folders
- sends unknown or unmatched ROMs to an `INVALID` folder
- creates CSV reports for the sort results and missing titles

## Region priority

The intended region preference for this set is:

1. **UK / Europe**
2. **USA**
3. **Japan**

## Included files

- `sort_n64_roms.py` – main Python sorter
- `convert_to_n64.sh` – conversion script for `.v64` / `.z64` to `.n64`
- `N64 UK Complete Game List.xlsx` – main spreadsheet used by the sorter
- `DD64 Game List.xlsx` – additional spreadsheet
- `n64romconvert` – converter binary
- `n64romtype` – helper binary used by the converter
- `extras/wallpaper.png` – SummerCart64 wallpaper
- `extras/labels.db` – SummerCart64 label asset for Analogue 3D
- `reports/` – generated sort reports

## Extras

This repo also includes SummerCart64 extras:

- label assets
- wallpaper

## Requirements

You will need:

- **Python 3**
- **openpyxl**
- a Unix-like shell to run `convert_to_n64.sh`
- your source **N64 ROM files**

## Install

On Debian/Ubuntu, install Python 3 and the required package with:

```bash
sudo apt install python3 python3-openpyxl
```

If needed, make the converter binary and shell script executable:

```bash
chmod +x n64romconvert
chmod +x convert_to_n64.sh
```

## Folder layout

The scripts are expected to be run from the repository root.

### Input folders

- `IN_RAW/` – source ROMs in `.v64`, `.z64`, or `.n64`
- `IN_N64/` – normalised `.n64` ROMs ready for sorting

### Output folders

- `OUT/Europe/`
- `OUT/USA/`
- `OUT/Japan/`
- `OUT/INVALID/`
- `reports/`

## How to use

### 1. Add ROMs

Put your ROM files into `IN_RAW/`.

Supported input formats for conversion:

- `.v64`
- `.z64`
- `.n64`

### 2. Convert ROMs to `.n64`

Run:

```bash
./convert_to_n64.sh
```

This will:

- convert `.v64` and `.z64` files to `.n64`
- move existing `.n64` files into `IN_N64/`
- skip unsupported files

### 3. Run the sorter

Run:

```bash
python3 sort_n64_roms.py
```

This will:

- read `N64 UK Complete Game List.xlsx`
- calculate CRC32 and SHA1 values for ROMs in `IN_N64/`
- match ROMs against the spreadsheet
- move matched ROMs into:
  - `OUT/Europe/`
  - `OUT/USA/`
  - `OUT/Japan/`
- move unmatched or invalid files into:
  - `OUT/INVALID/`
- write reports to `reports/`

### 4. Check the reports

After sorting, review:

- `reports/sort_log.csv`
- `reports/missing_from_collection.csv`

## Notes

- duplicate ROMs are deleted by default in `sort_n64_roms.py`
- the main workbook used by the sorter is `N64 UK Complete Game List.xlsx`
- the sorter currently reads from `Sheet1`
- if a ROM does not match the spreadsheet by CRC, it is moved to `OUT/INVALID/`
- the sorting logic can be edited in the Python script if you want a different region preference

## Converter source

The included converter binary was generated from source from:

- [`ezntek/n64romconvert`](https://github.com/ezntek/n64romconvert)

This repository uses that converter as part of the ROM preparation workflow.

## Summary

This repo is an **N64 ROM sorter** for building a **UK / Europe-first collection**, with support for conversion, spreadsheet-based matching, region sorting, and report generation.
