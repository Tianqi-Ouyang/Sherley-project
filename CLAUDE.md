# CLAUDE.md

@~/.claude/hospital-privacy.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a clinical research analysis project investigating whether the baseline creatinine-to-cystatin C ratio predicts adverse events in cancer patients receiving platinum-based chemotherapy (cisplatin/carboplatin). The primary exposure is `cr_cys_7` (creatinine/cystatin C ratio < 0.7).

This is the **Sherley cohort** — an N=169 EMPI sub-cohort filtered from the same REDCap export and RPDR pull used by the parent Cystatin C / Jiaxuan project (https://github.com/Tianqi-Ouyang/Cys-C-project-). The pipeline, variables, models, and outputs are identical; only the EMPI inclusion list changes.

## Running the Analysis

This project uses Quarto. Render the website from the project root:

```bash
quarto render
```

`qmd/jiaxuan_data.qmd` runs first and writes `jiaxuan_final_master.rds`; the three downstream `jiaxuan_*` analysis files consume that rds. Output lands in `docs/`.

## Files

- **`Data/Patient IDS_Tianqi_20May2026.xlsx`** — Sherley EMPI inclusion list (Sheet3, N=169).
- **`Data/CystatinCInPatientsO_DATA_2026-04-27_0819.csv`** — REDCap export (reused from parent project).
- RPDR diagnoses / labs / medications are loaded by absolute path from the Partners HealthCare Dropbox (see `qmd/jiaxuan_data.qmd` lines 675/680/686).

### Jiaxuan Project Files (in `qmd/`)

- **`jiaxuan_data.qmd`** — Data management pipeline. Produces `jiaxuan_final_master.rds`. Must be rendered first.
- **`jiaxuan_whole.qmd`** — Whole cohort analysis (all platinum patients).
- **`jiaxuan_carbo.qmd`** — Carboplatin cohort analysis.
- **`jiaxuan_carbo_auc3.qmd`** — Carboplatin AUC ≥ 3 subgroup (N=463).

All three analysis files read from `jiaxuan_final_master.rds`. The Quarto website nav has a "Jiaxuan Project" dropdown with all four files.

The primary `.Rmd` also loads external data files (RPDR exports: diagnoses, labs, medications, demographics as `.txt`/`.xlsx` files) that are expected to exist in paths hardcoded in the script.

## Architecture / Data Pipeline

The analysis follows a linear pipeline within the `.Rmd` file:

1. **Data loading** — Merges REDCap CSV with RPDR clinical data (diagnoses, labs, medications, demographics) and supplementary Excel files.
2. **Data cleaning** — Standardizes column names, handles missing values, processes date fields.
3. **Variable creation** — Constructs clinical variables:
   - Kidney function: eGFR from creatinine (CKD-EPI), eGFR from cystatin C, CKD stage
   - Exposure: `cr_cys_7` (creatinine/cystatin C ratio, binary threshold < 0.7)
   - Comorbidity: Charlson score, 15+ drug indicators
   - Treatment: platinum type, dose category (low/high)
4. **Outcome definition** — Events within 90-day follow-up:
   - Grade 2/3 adverse events: anemia, thrombocytopenia, AKI
   - Hospitalizations (11 categories), ED visits (7 categories)
   - Electrolyte abnormalities: hypokalemia (K < 3), hypomagnesemia (Mg < 0.9), hyponatremia (Na < 125)
   - 90-day mortality
5. **Statistical analysis** — Descriptive tables (gtsummary/tableone), competing risk regression (tidycmprsk), cumulative incidence plots (ggcuminc).

## Key R Packages

| Purpose | Packages |
|---|---|
| Data manipulation | tidyverse, dplyr, readxl, openxlsx |
| Descriptive stats | tableone, gtsummary |
| Competing risks | tidycmprsk, cmprsk |
| Survival analysis | survival, survminer, ggsurvfit, finalfit |
| Visualization | ggplot2, ggpubr |
| Comorbidity scoring | comorbidity (Charlson index) |
| Missing data | mice |

## Key Clinical Concepts

- **cr_cys_7**: The main exposure — binary indicator for creatinine/cystatin C ratio < 0.7. Low ratio suggests muscle wasting (sarcopenia) independent of GFR.
- **Competing risks framework**: Death is treated as a competing event for non-fatal outcomes; `tidycmprsk::crr()` is used instead of standard Cox regression.
- **Platinum dosing**: Cisplatin ≥ 70 mg/m² and carboplatin AUC ≥ 5 are categorized as "high dose."
- **CKD staging**: Based on Cockcroft-Gault eGFR from pre-baseline creatinine values from RPDR labs.
- **eGFR capping rules**: Only `ckd_epi_gfr_cre_cys_unindex` is capped at 125 mL/min (unindexing by BSA can produce implausible values). The indexed `ckd_epi_gfr_cre_cys` and `cockcroft` are NOT capped. Use **uncapped** versions for eGFR ratio; use **capped** versions (`ckd_epi_gfr_cre_cys_unindex_cap125`, `cockcroft_cap125`) for dose discrepancy calculations.
- **dose_discrep_per25increase**: Dose discrepancy (actual − predicted carboplatin dose in mg) divided by 25, so HRs represent per 25 mg increase. Used as an alternative predictor alongside `egfr_ratio_per10`. Only in carbo/AUC3 files.

## Jiaxuan Project — Analysis Structure

### Reference categories
- **sex**: Female is reference
- **ecog_score_cat2**: "0" is reference (explicit factor)

### Key variables
- **egfr_ratio_per10**: Negated (`-egfr_ratio * 10`), so HRs represent per 0.1-unit **decrease** in CKD-EPI Cr-Cys / CG ratio
- **egfr_discrepancy**: `ckd_epi_gfr_cre_cys_unindex - cockcroft` (mL/min)
- **dose_discrep_per25increase**: `dose_discrepancy / 25` (carbo/AUC3 only)
- **abs_dose_discrep_cat**: Absolute dose discrepancy binned: <25, 25–49.99, 50–74.99, 75–99.99, ≥100 mg (carbo/AUC3 only)

### Section structure (whole cohort: `jiaxuan_whole.qmd`)
1. Setup
2. Table 1
3. Fine-Gray Models — eGFR Ratio (adjusted for Cockcroft-Gault)
4. Cause-Specific Hazard Models — eGFR Ratio (adjusted for CG)
5. Linear subHR Curves — eGFR Ratio (raw scale, xlim 0.65–1.45)
6. Linear subHR Curves — eGFR Discrepancy (auto-scale x)
7. Linear subHR Curves — Hospitalization by Reason (1–8)
8. Scatter Plots — eGFR Discrepancy

### Section structure (carbo/AUC3 cohorts add):
- Section 2: Dose Discrepancy Distribution histogram
- Sections 6–7: Fine-Gray + CSH models with `dose_discrep_per25increase`
- Section 10: Linear subHR — Dose Discrepancy (auto-scale x)
- Section 12: Scatter Plots — Dose Discrepancy vs eGFR

### Model adjusters (Cockcroft-adjusted)
Base: age, sex, score, ecog_score_cat2, cancer_type_cat_7, tumor_stage, high_dose, Paclitaxel, Pemetrexed, Gemcitabine, bmi, smoking, steroids, thyroid + cockcroft. Whole cohort adds platin_group (auto-dropped for dose discrepancy models). Anemia models add pre_HGB_45days; thrombocytopenia adds pre_PLT_45days.

### 90-Day Death
Modeled with Cox PH (not competing risks). Section headers labeled "(Cox PH)".

### Plot trimming
Linear subHR plots trim at 2.5/97.5 percentile. eGFR ratio plots use xlim = (0.65, 1.45). Discrepancy/dose plots auto-scale x-axis.
