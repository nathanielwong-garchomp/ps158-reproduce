"""Download official SCF data and build wealth-by-reference-person-education data.
Run: python get_data.py (requires pandas). Dollars are 2025 dollars in
this release. EDCL uses the Fed’s harmonized education categories for 1989–2025.
Group 2 is high school/GED only; group 4 is bachelor’s degree or higher.
"""
from pathlib import Path
from urllib.parse import urljoin
import hashlib
import json
import re
import subprocess
import zipfile
import pandas as pd

ROOT = Path(__file__).resolve().parent
RAW = ROOT / 'data' / 'raw'
BASE = 'https://www.federalreserve.gov'
YEARS = range(1989, 2026, 3)


def download(url, path):
    if not path.exists():
        tmp = path.with_suffix(path.suffix + '.part')
        subprocess.run(['curl', '--fail', '--location', '--silent', '--show-error',
                        '--retry', '3', url, '-o', str(tmp)], check=True)
        tmp.replace(path)
    return path


def main():
    RAW.mkdir(parents=True, exist_ok=True)
    manifest, frames, availability = [], [], []
    for year in YEARS:
        page_url = f'{BASE}/econres/' + ('scfindex.htm' if year == 2025 else f'scf_{year}.htm')
        page = download(page_url, RAW / f'page{year}.html').read_text()
        links = [urljoin(BASE, h) for h in re.findall(r'href=[\"\x27]([^\"\x27]+)', page)]
        extract_url = next(h for h in links if h.endswith(f'scfp{year}excel.zip'))
        path = download(extract_url, RAW / f'extract{year}.zip')
        manifest.append({'year': year, 'url': extract_url,
                         'sha256': hashlib.sha256(path.read_bytes()).hexdigest()})
        with zipfile.ZipFile(path) as z:
            name = next(n for n in z.namelist() if n.lower().endswith('.csv'))
            extract = pd.read_csv(z.open(name))
        extract.columns = extract.columns.str.lower()
        id_col = 'y1' if 'y1' in extract else 'x1'
        merged = extract[[id_col, 'networth', 'wgt', 'edcl']].copy()
        if not merged.edcl.isin([1, 2, 3, 4]).all():
            raise ValueError(f'{year}: unexpected education codes')
        merged['group'] = merged.edcl.map({1: 'Less than high school',
            2: 'High school diploma / GED', 3: 'Some college / associate',
            4: 'Bachelor’s degree or higher'})
        merged['year'] = year
        merged['implicate'] = merged[id_col].astype(int) % 10
        assert set(merged.implicate) == {1, 2, 3, 4, 5}
        assert merged.wgt.gt(0).all() and merged.networth.notna().all()
        assert not merged[id_col].duplicated().any()
        frames.append(merged)
        print(f'{year}: {len(merged)} implicate records', flush=True)
    pd.concat(frames, ignore_index=True).to_csv(ROOT / 'data' / 'wealth_education.csv', index=False)
    (ROOT / 'data' / 'sources.json').write_text(json.dumps({'dollar_year': 2025, 'sources': manifest}, indent=2))

if __name__ == '__main__':
    main()
