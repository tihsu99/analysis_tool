## Plotting 
The color map is defined in `../../python/common.py` and basic plotting style used `../../python/plotstyle.py`. To make the plot:
```
python plot_histo.py [args]
```
The arguments:
1. `--indir`: The directory which stores the skimmed root files.
2. `--outdir`: Output directory to store the plots. Default is the same as `indir`.
3. `--era`: Target era
4. `--region`: Target region 
5. `--channels`: List of target channels
6. `--Labels`: Target group of histogram
7. `--Black_list`: Banned group of histogram
8. `--signals`: List of signals 
9. `--logy`
10. `--overflow`: add overflow bin into the first/last bin
11. `--only_signal`: Only plot signal
12. `--normalize`: Normalize the distributions to one. Recommend only used with `--only_signal`
