# Produce ROOT file
This section is mainly focus on producing slim root file. The input directory is kept in `../../pyhon/common.py`.  
```
python runcondor.py [args]
```
The arguments are:
1. `--outdir`: Target stored directory. It can be in `\eos`.
2. `--era`: Target era. Default is `all`, which runs all four eras
3. `--region`: List of regions
4. `--channels`: List of channels
5. `--Labels`: Target label/group of `variables`
6. `--Black_list`: Banned label/group of `variables`
7. `--POIs`: List of `variables` that will perform nuisance varition.
8. `--JobFlavour`: condor JobFlavour
9. `--universe`: condor universe
10. `--blocksize`: Events processed in each condor job` 
11. `--test`: Do not trigger condor submission
12. `--check`: Check all files are produced successfully and merged them.
13. `--sample_json`: Json file that contains sample information.
14. `--cut_json`: Json file that contains cut / region information.
15. `--variable_json`: Json file that contains variable definition.
16. `--histogram_json`: Json file that contains histogram information.
17. `--nuisance_json`: Json file that contains nuisacne information.
18. `--trigger_json`: Json file that contains trigger information.
19. `--MET_filter_json`: Json file that contains MET filter information.

As an example, you produce the 2017 skimmed ntuple with following command (most of the arguments can just follow default value):
```
python runcondor.py --outdir [YOUR DIRECTORY] --era 2017 --POIs bh_HT
```

After running `runcondor.py`, the code will produce `check.sh` and `clear.sh`, which are cheat sheets to do the checking(merging) and clear all the unneeded files after merging.. Feel free to modify the `JobFlavour` in it etc. (TODO: it is normal to have failed job and need to resubmit again, need to fix it)
**It is important to check and merge the files, it may take one or two more trials to make all files correct**
```
sh check.sh
``` 
```
sh clear.sh # Once all files merge successfully
```

 
