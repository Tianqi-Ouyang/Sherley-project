# Sherley Cohort — CysC / Creatinine Ratio – Platinum AE

Clinical-research analysis investigating whether the baseline creatinine / cystatin-C ratio (`cr_cys_7`) predicts adverse events in cancer patients receiving platinum-based chemotherapy.

This repository is the **Sherley sub-cohort** (N=169 EMPIs from `Data/Patient IDS_Tianqi_20May2026.xlsx`) of the parent Cystatin C / Sherley project: <https://github.com/Tianqi-Ouyang/Cys-C-project->. The pipeline, derived variables, and statistical models are identical; only the EMPI inclusion list differs.

## Render

```bash
quarto render
```

`qmd/sherley_data.qmd` runs first and produces `sherley_final_master.rds`; the three `sherley_*` analysis files consume that rds. Rendered website + Word tables land in `docs/`.

## Inputs (not committed)

| File | Source |
|---|---|
| `Data/Patient IDS_Tianqi_20May2026.xlsx` | EMPI inclusion list (Sheet3, N=169) |
| `Data/CystatinCInPatientsO_DATA_2026-05-26_1104.csv` | REDCap export |
| RPDR `mes98_03182614492143216_{Dia,Lab,Med}.txt` | Loaded by absolute path from Partners HealthCare Dropbox |

Data files contain PHI/EMPI and are excluded by `.gitignore` (`Data/`, `*.csv`, `*.xlsx`, `*.rds`, `*.pdf`).

See `CLAUDE.md` for the full pipeline architecture, clinical conventions, and model adjusters.
