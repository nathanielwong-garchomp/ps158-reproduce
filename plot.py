"""First descriptive figure. Requires pandas, numpy, matplotlib.
Run get_data.py first. Weighted means and weighted medians are computed
separately in each of five implicates, then averaged. No confidence
intervals: replicate-weight sampling variance is outside this first figure.
"""
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent
GROUPS = ['Bachelor’s degree or higher', 'High school diploma / GED']


def weighted_median(values, weights):
    order = np.argsort(values)
    x, w = np.asarray(values)[order], np.asarray(weights)[order]
    return x[np.searchsorted(np.cumsum(w), w.sum() / 2)]


def main():
    data = pd.read_csv(ROOT / 'data/wealth_education.csv')
    rows = []
    for (year, group, imp), d in data[data.group.isin(GROUPS)].groupby(['year', 'group', 'implicate']):
        rows.append(dict(year=year, group=group, implicate=imp,
                         median=weighted_median(d.networth, d.wgt),
                         mean=np.average(d.networth, weights=d.wgt)))
    stats = pd.DataFrame(rows).groupby(['year', 'group'])[['median', 'mean']].mean().reset_index()
    out = ROOT / 'outputs'
    out.mkdir(exist_ok=True)
    stats.to_csv(out / 'wealth_summary.csv', index=False)
    fig, axes = plt.subplots(1, 2, figsize=(11, 5.7))
    for ax, measure in zip(axes, ['median', 'mean']):
        for group, color in zip(GROUPS, ['#176b87', '#c45d35']):
            d = stats[stats.group.eq(group)]
            ax.plot(d.year, d[measure] / 1000, 'o-', color=color, lw=2.3, label=group)
        ax.set_title(f'{measure.title()} family net worth', loc='left', fontsize=13)
        ax.set_ylabel('Thousands of 2025 dollars')
        ax.set_xticks([1989, 1995, 2001, 2007, 2013, 2019, 2025])
        ax.tick_params(axis='x', labelsize=9)
        ax.set_ylim(bottom=0)
        ax.grid(axis='y', alpha=.2)
        ax.spines[['top', 'right']].set_visible(False)
    fig.suptitle('U.S. family wealth by reference person’s education', x=.08, ha='left', fontsize=17)
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc='lower center', bbox_to_anchor=(.5, .135), ncol=2, frameon=False)
    fig.text(.08, .07, 'Inflation: all years expressed in 2025 dollars using the Fed’s CPI-U-RS–based adjustment (September prices).\nSource: Federal Reserve SCF, public summary extracts. Survey-weighted; five implicates averaged.\nHigh school = diploma/GED only. Less than HS and some college/associate excluded. All ages; no age adjustment.\nDescriptive point estimates; no confidence intervals. Education question changed in 2016; Fed EDCL categories used.', fontsize=8.5, va='center')
    fig.subplots_adjust(left=.08, right=.98, top=.83, bottom=.28, wspace=.28)
    fig.savefig(out / 'wealth_gap.png', dpi=180)
    fig.savefig(out / 'wealth_gap.svg')
    print(stats.to_string(index=False))
    for measure in ['median', 'mean']:
        p = stats.pivot(index='year', columns='group', values=measure)
        print(measure, '\n', pd.DataFrame({'gap': p[GROUPS[0]]-p[GROUPS[1]], 'ratio': p[GROUPS[0]]/p[GROUPS[1]]}).to_string())

if __name__ == '__main__':
    main()
