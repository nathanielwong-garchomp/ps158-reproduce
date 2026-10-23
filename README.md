# U.S. family wealth by education, 1989–2025

## Figure

`outputs/wealth_gap.png` (also available as SVG) shows median and mean family net worth in two panels, comparing families whose SCF reference person has a bachelor’s degree or higher with those whose reference person has a high-school diploma/GED only. The figure includes all ages and families with or without children. Less-than-high-school and some-college/associate groups are excluded.

## Data and method

`get_data.py` downloads the Federal Reserve’s [Survey of Consumer Finances public summary extracts](https://www.federalreserve.gov/econres/scfindex.htm): `scfp1989excel.zip` through `scfp2025excel.zip`, covering 13 triennial surveys. The endpoint is the 2025 survey, released October 9, 2026. Raw downloads are cached in `data/raw/`; source URLs and SHA-256 hashes are recorded in `data/sources.json`.

The analysis uses `NETWORTH` (assets minus debts), `EDCL` (reference person’s education), and `WGT` (survey weight). The Fed’s extracts already express wealth in 2025 dollars using its CPI-U-RS–based adjustment; the scripts do not adjust it again. `plot.py` calculates weighted means and medians separately for each of five imputations, then averages them. Results are saved in `outputs/wealth_summary.csv`.

These are descriptive comparisons, without age adjustment or confidence intervals in the figure. They do not measure the causal effect of college. The education question changed in 2016; the analysis uses the Fed’s harmonized categories.

## Validation

The 2025 college mean is approximately **$2.24 million**. The Fed’s [published public-data table](https://www.federalreserve.gov/econres/files/scf2025_tables_public_real_historical.xlsx), Table 4, cell AA36, reports $2,240,460, versus our $2,240,358. Pooling the five imputations instead of averaging separately calculated means reproduces that table after rounding. The [main report](https://www.federalreserve.gov/publications/files/scf26.pdf), Table 2, reports about $2.26 million using internal data; confidentiality modifications and analysis-weight adjustments can produce differences. Avoid interpreting dollar-level precision as certainty.

## Rerun

Requires Python 3, `curl`, and internet access for downloads. From the project directory:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install pandas numpy matplotlib
.venv/bin/python get_data.py
.venv/bin/python plot.py
```

If the environment already exists, run only the last two commands. To force fresh downloads, first rename `data/raw/` as a backup, then rerun both scripts. Existing generated data and outputs will be overwritten. To check reproducibility, save a copy of `outputs/wealth_summary.csv` beforehand and compare it with the regenerated file using `diff`.
