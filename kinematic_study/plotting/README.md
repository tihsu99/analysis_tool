## Plotting 
The color map is defined in `../../python/common.py` and basic plotting style used `../../python/plotstyle.py`. To make the plot:
```
python plot_histo.py [args]
```
The arguments:
1. `--indir`: The directory which stores the skimmed root files.
2. `--outdir`: Output directory to store the plots. Default is the same as `indir`.
3. `--era`: Target era
4. `--region`: Target region (Default follows `../../data/cut.json` region definition) 
5. `--channels`: List of target channels (Default follows `../../data/cut.json` region definition)
6. `--Labels`: Target group of histogram
7. `--Black_list`: Banned group of histogram
8. `--signals`: List of signals 
9. `--logy` : Default is `False`
10. `--overflow`: add overflow bin into the first/last bin
11. `--only_signal`: Only plot signal
12. `--normalize`: Normalize the distributions to one. Recommend only used with `--only_signal`
13. `--unblind`: Unblind or not (Default is blind)
14. `--block_sample`: List of samples that should be blocked
15. `--Yield`: Add yield in legend or not.
16. `--ratio_min`: ratio y axis lower bound.
17. `--ratio_max`: ratio y axis higher bound.
18. `--ratio_Ndiv`: ratio y axis Ndivisions.
For example, you can plot it with following command
```
python plot_histo.py --indir [YOUR DIRECTORY] --era 2017 [--unblind] [--Yield]
```
Or for signal only plot
```
python plot_histo.py --indir [YOUR DIRECTORY] --era 2017 --only_signal --signals [LIST of SIGNALS] --normalize
```

Complete example (do not forget to change the path to the folder to yours):
```
python plot_histo.py --indir /eos/user/g/gkole/database/bHplus/CR_1b4j --era 2017 --sample_json ../../data/sample.json --region CR_1b4j --channel mu_resolved --Labels Normal Control_plot --outdir test1_CR_1b4j
```
### Signal Gen plot
Utilizing the `coffea` to perform signal genlevel study make the code much more simpler. In `signal_gen_plot.py`, the decay dictionary defined the wanted decay mode and the code will automatically selected all the events that have this decay and reconstruct the kinematic of every `genPartons` in this decay mode. Arguments are not yet done for this code, but users can easily modify the dictionary and the code to perform the genlevel study.
```
source ../../script/env.sh
python signal_gen_plot.py
```
