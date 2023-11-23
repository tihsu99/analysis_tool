# 0. Cheat sheet 
## 0.1 Cheating tablet for commands (temporary, inputdir will change time by time, **only to test code in current version**):
To initialization and rebin:
```
python Init.py --year 2017 --channel all -b muPt btag
python ReBin.py -y 2017  --inputdir [--YOUR DIRECTORY]  --unblind --POI bh_HT
```
To produce datacard:
```
python prepareCards.py --combined --year 2017
```
To run limits:
```
python runlimits.py -c C -r C -y 2017 --Masses 200 350 800 1000
python runlimits.py -c C -r C -y 2017 --Masses 200 350 800 1000 --plot_only #plot
```
To run impacts:
```
python ./SignalExtraction_Estimation.py -y 2017 -c C -r C --mode datacard2workspace --mass_point 800
python ./SignalExtraction_Estimation.py -y 2017 -c C -r C --mode FitDiagnostics --mass_point 800
python ./SignalExtraction_Estimation.py -y 2017 -c C -r C --mode FinalYieldComputation --mass_point 800
python ./SignalExtraction_Estimation.py -y 2017 -c C -r C --mode PlotShape --mass_point 800 --shape_type preFit --plotRatio
python ./SignalExtraction_Estimation.py -y 2017 -c C -r C --mode PlotShape --mass_point 800 --shape_type postFit --plotRatio
python ./SignalExtraction_Estimation.py -y 2017 -c C -r C --mode diffNuisances --mass_point 800
python ./SignalExtraction_Estimation.py -y 2017 -c C -r C --mode PlotPulls --mass_point 800 
python ./SignalExtraction_Estimation.py -y 2017 -c C -r C --mode Impact_doInitFit --mass_point 800 
python ./SignalExtraction_Estimation.py -y 2017 -c C -r C --mode Impact_doFits --mass_point 800
python ./SignalExtraction_Estimation.py -y 2017 -c C -r C --mode SubmitGOF --mass_point 800 
```
After condor finishes the job.
```
python ./SignalExtraction_Estimation.py -y 2017 -c C -r C --mode Plot_Impacts --mass_point 800
python ./SignalExtraction_Estimation.py -y 2017 -c C -r C --mode GoFPlot --mass_point 800  
```
# 1. Initialization

## 1.1 Commands for Input files preparing for datacard production
Note: the initialization is to be done only once. You can block certain nuisances via `-b`.
```
python Init.py --year 2017 --channel all
python Init.py --year 2018 --channel all
python Init.py --year 2016apv --channel all
python Init.py --year 2016postapv --channel all
```
After this step, a folder, data_info, is created. And under this folder, you can find three main different files under data_info:

- data_info/Sample_Names/process_name_{year}.json # Contain the sample names sorting with certain physics process category
- data_info/NuisanceList/nuisance_list_{year}_{channel}.json # Contain the nuisances list for each channel
- data_info/Datacard_Input/{year}/Datacard_Input_{channel}.json # Contain the necessary information for datacard production later.

## 1.2 Breakdown uncertainties

If you want to breakdown the nuisance uncertainties:
```
python Init.py --year 2017 --channel all --breakdown
python Init.py --year 2018 --channel all --breakdown
python Init.py --year 2016apv --channel all --breakdown
python Init.py --year 2016postapv --channel all --breakdown
```
Currently, the groups of uncertainties are theory and experimental. If one want to customize the group, please go to [Init_Tool/Nuisance_Producer.py](https://github.com/ExtraYukawa/LimitModel/blob/ZhengGang_dev2/Init_Tool/Nuisance_Producer.py)

The additional json file name is like 
- data_info/NuisanceList/nuisance_group_{YEAR}_{CHANNEL}.json # contain the group element information, which will feed into datacards.

## 1.2 Block unwanted nuisances (You can skip this)

If you don't want _chargeflipYEAR nuisances for ee channel in year2017 for example, you can remove it through the argument --blacklist
```
cd $CMSSW_BASE/src/HiggsAnalysis/LimitModel/
python Init.py --year 2017 --channel ee --blacklist _chargefilpYEAR  
```


## 1.3 Calculate logN uncertainty for category (Option)
To get information about logN uncertainty for merged category. Please use following command. With BDT cut, different signal will affect BDT shape and thus background composition. The average uncertainty will be affected but it was found to have negligible affect. `You need to enter the number to the corresponding code by hand if you want to change category uncertainty` since we want to keep the category uncertainty fixed and maintained in github in current stage.
```
python study_bkg_composition.py 
```


# 2. Rebin and merging of processes 

## 2.1 Commands for histograms rebinning for original BDT_output files

Use the ReBin.py macro to perform two main tasks (Binning setting is stored in `Util/General_Tool.py`, please edit it if you want to change binning): 
```
1. Merge the histograms for various processes and make a new histogram which is sum of others, this is to make sure we don't have huge stats fluctuations. histograms for same/similar physics Processes are added. 
2. Once merging of histograms are done, each of these histogram is then rebinned, (uniform or non-uniform) depending on the needs. 
```

Normally, you should use the following commands. (By default, the code will wrong all the channels, regions, and signals contain in the `data/sample.json` and `data/cut.json`)
```
python ReBin.py --y [year: 2016apv/2016postapv/2017/2018] --inputdir [input/provided/by/Gouranga] [--unblind] [--POI] [--channel] [--region] [--signal] 
```

## 2.2 Quiet the thousands of warning message 

If you don't want your terminal filled with these messages, you can add [-q/--quiet] like:
```
python ReBin.py --y [year: 2016apv/2016postapv/2017/2018] --inputdir [input/provided/by/Gouranga] [--unblind] [--POI] [--channel] [--region] [--signal] [--quiet]
```
Note: But you should be care of using [-q/--quiet], because it will ignore some important information while there is any nuisances you do not set correctly, like typo. 

And once this step is done, there are several rebined root files under `FinalInputs`.

# 3. Datacard preparation

In this section is aimming to explain how to prepare the datacards by yourself. But for people who want to get datacard quickly can simply skip the things to section `3.3 Quick command-list for datacard productions`

## 3.1 Pre-requists for datacards template production 

The next step is to create the datacards. The input needed for making datacards are:
1. data_info/Datacard_Input/{Year}/Datacard_Input_{channel}.json
2. data_info/Sample_Names/process_name_{year}.json
3. data_info/NuisanceList/nuisance_list_{year}_{channel}.json

So make sure you already `have/update` them, otherwise the datacard would give the wrong references for combine tool.

## 3.2 Datacard production Explanation

### 3.2.1 Datacard production

If you already make sure the above steps are settle, then you can produce the template datacards for certain channel in certain year with:

``` 
python prepareCards.py --year {list of 2016apv/2016postapv/2017/2018} [--channel] [--region] [--combined] [--signal/--mass] [--outdir]
```
By default, the code will run through all the channels, regions, so no need to specify `--channel`, `--year`, `--region`. `--signal` can specify the wanted list of signals, and if it is not specified `--mass` can be used instead to specify the signal Higgs mass (the signal sample naming rule is hardcoded in the code). `--outdir` means the datacard output directory name. `--combined` triggers the combination of all the era, channel, and region for all the combination (i.e. accumulate the lists of years to `run2`, all the channels to `C`)

### 3.2.2 Uncertainties breakdown (TODO)

To have the categorized uncertainties, you should already have the corresponding json file. Please go to Section 1.2. 
Once you have it, then you just need to use [--breakdown] for template production: 
```
python prepareCards.py -y {year:2016apv/2016postapv/2017/2018} -c {channel:ee/em/mm} --For template --breakdown {1,2,3} -reg 'SR_{channel:ee/em/mm}'
```
Then you will have the uncertain category in the last line of template datacard.

* [--breakdown] only works for `template` with various combinations of 2016apv-2018 & ee/em/mm. [NB: run2 as year and C as channel will not work]

# 4. Limit Plots

N.B: if you want to compute unblinded results, then add ``--unblind`` while run the command.

Note!!!: The pre-requiest for this is the corresponding datacard.

You can try following commands to produce the limit plots, but you would find it will take a century to finish per command :). 
```
python runlimits.py [--channel] [--region] [--year] --rtt [0.6] --rtc [0.4] [--unblind] --Masses [Mass list] --datacarddir [datacard directory] 
```
#### Plot Limits 

After the programs is finished, you should use [--plot_only] and [--outputdir] to see the plots. Like:
```
python runlimits.py  [--channel] [--region] [--year] --rtt [0.6] --rtc [0.4] [--unblind] --Masses [Mass list] --datacarddir [datacard directory] --outputdir [your/favoured/output/folder] --plot_only;
```
Note: Generally, it would take > 1 day to finish the calculation for full run2 limit plots. In section `6`, we provide the steps to get script for condor, and take rtc0p4 full run2 limit plot for low regime (200-700GeV) for example.

# 5. For impacts and pulls and post/pre-fit distribution

Note: if you want to do this for interference samples, please add `--interference`. And mass_point is corresponding to higgs A.  
Note: Since it takes too much space to store all the information, we suggest to make the workspace under eos directory, simply adding `--outdir [path/to/workspace]` after each step, then the code will automatically create and operate in that directory automatically.

N.B: if you want to compute unblinded results, then add ``--unblind`` while run the command.
N.B: if you want to do some parameter optimization and wanted to same output to different directory other than "Unblind/s_plus_b/s_plus_b", you can add ``--prefix <string>`` this will add the given string in the ouput directory "Unblind/s_plus_b/s_plus_b".

Step1 -> convert datacard to workspace files distribution. O(time) ~ 10 sec. For fullrun2: O(time) ~ 3mins.
```
python ./SignalExtraction_Estimation.py -y 2017 -c [CHANNEL] -r [REGION] --mode datacard2workspace [--rtt] [--rtc] --mass_point 800 --outdir [path/to/workspace]
```

Step2 -> FitDiagnostics. O(time) ~ O(3mins~15mins) for single year. time  ~ O(2.5-3hr )  
```
python ./SignalExtraction_Estimation.py -y 2017 -c [CHANNEL] -r [REGION] --mode FitDiagnostics [--rtt] [--rtc] --mass_point 800 --outdir [path/to/workspace]
```

Step3 -> FinalYieldComputation.
After this, you will have latex table with yields value (and error values) for each background.
```
python ./SignalExtraction_Estimation.py -y 2017 -c [CHANNEL] -r [REGION] --mode FinalYieldComputation [--rtt] [--rtc] --mass_point 800 --outdir [path/to/workspace]
```

Step3 -> preFit distribution. O(time) ~ 1 sec 
```
python ./SignalExtraction_Estimation.py -y 2017 -c [CHANNEL] -r [REGION] --mode PlotShape [--rtt] [--rtc] --mass_point 800 --text_y 800 --outdir [path/to/workspace] [--logy] [--plotRatio] --shape_type preFit
```

Step4 -> postFit distribution.
```
python ./SignalExtraction_Estimation.py -y 2017 -c [CHANNEL] -r [REGION] --mode PlotShape [--rtt] [--rtc] --mass_point 800 --text_y 800 --outdir [path/to/workspace] [--logy] [--plotRatio] --shape_type postFit
```

Step5 -> Calculating Pulls for each nuisances and background.
```
python ./SignalExtraction_Estimation.py -y 2017 -c [CHANNEL] -r [REGION] --mode diffNuisances [--rtt] [--rtc] --mass_point 800 --outdir [path/to/workspace]
```

Step6 -> Plot the pulls.
```
python ./SignalExtraction_Estimation.py -y 2017 -c [CHANNEL] -r [REGION] --mode PlotPulls [--rtt] [--rtc] --mass_point 800 --outdir [path/to/workspace]
```

Step7.1 -> Init Fit for Impact. O(time) ~ 30 sec. O(time) ~ 5hrs for Combined. 
```
python ./SignalExtraction_Estimation.py -y 2017 -c [CHANNEL] -r [REGION] --mode Impact_doInitFit [--rtt] [--rtc] --mass_point 800 --outdir [path/to/workspace]
```

Step7.2 -> Do Fits for Impacts. You need to wait all the jobs completed. O(time) ~ 20-40 mins for single year. --outdir [path/to/workspace]

```
python ./SignalExtraction_Estimation.py -y 2017 -c [CHANNEL] -r [REGION] --mode Impact_doFits [--rtt] [--rtc] --mass_point 800 --outdir [path/to/workspace]
```
Step7.3: Submit from EOS (Only when workspace is under eos) (**TODO:Check the code**)
```
python ./SignalExtraction_Estimation.py -y 2017 -c [CHANNEL] -r [REGION] --mode SubmitFromEOS [--rtt] [--rtc] --mass_point 800 --outdir [path/to/workspace]
```

Step8: Plot Impacts.  O(time) ~ 30 sec.
```
python ./SignalExtraction_Estimation.py -y 2017 -c [CHANNEL] -r [REGION] --mode Plot_Impacts [--rtt] [--rtc] --mass_point 800 --outdir [path/to/workspace]
```
Step9 : Goodness of Test 
Firstly, you need to submit the jobs to condor for 50 toys for GoF
```
python ./SignalExtraction_Estimation.py -y 2017 -c [CHANNEL] -r [REGION] --mode SubmitGOF [--rtt] [--rtc] --mass_point 800 --GoF_Algorithm [KS, AD, saturated:default] 
```
Then, after all the jobs are completed, you can plot it with
```
python ./SignalExtraction_Estimation.py -y 2017 -c [CHANNEL] -r [REGION] --mode GoFPlot [--rtt] [--rtc] --mass_point 800 --GoF_Algorithm [KS, AD, saturated:default]
```

Step 10: plotCorrelation (**TODO:Modify to `analysis_tool` structure**)
Currently, only the correlated uncertainties to JES are plotted (Under development)
Note: FitDiagnostics files and impact json are necessary in this step.
```
python ./SignalExtraction_Estimation.py -y 2017 -c [CHANNEL] -r [REGION] --mode plotCorrelationRanking [--rtt] [--rtc] --mass_point 800
```
Step 11: Profile Scan plot (**TODO: Modify to `analysis_tool` structure**)
```
python ./SignalExtraction_Estimation.py -y 2017 -c [CHANNEL] -r [REGION] --mode DrawNLL [--rtt] [--rtc] --mass_point 800 --unblind --rMin -2 --rMax 1.5 --group ${GROUP:1, 2, 3}
```

# Final Yield computation:

exmaple script is taken from combine central repo:

https://github.com/cms-analysis/HiggsAnalysis-CombinedLimit/blob/290b8260808891936aab06e5996f293a9f8954c3/test/mlfitNormsToText.py

https://cms-analysis.github.io/HiggsAnalysis-CombinedLimit/part3/nonstandard/#normalizations

For this we need fit_diagonatic root file
```
cd Util/
python mlfitNormsToText.py ../SignalExtraction/run2/C/rtc04/A/900/ratio_test_Unblind/fitDiagnostics_run2_C_A_900_rtc04_plot.root  -u
```

# 6. Condor Jobs (TODO: Rest sections are not yet compatible with `analysis_tool` structure)

## 6.1 Condor Jobs for limit plots
The first step is create a Job_bus file (just a text file) with

```
python ./Util/prepareJobs.py --mode write
```

And you will see something like 
```
You Job_bus file with name -> Job_bus/lqhAti.txt is created.
Use [--mode append] and [--Job_bus_Name filename] to append the following task.
```
In this example, Job_bus file name is `Job_bus/lqhAti.txt`

Then the next step is to add the job into the Job_bus file, so in our case, we want to calculate the limits value in low mass regime for higgs A for run2 channel-conbined, then
```
python Util/prepareJobs.py -i Job_bus/lqhAti.txt --mode append --task LimitPlot --mass_point 200 --channel C --coupling_value rtc04 --higgs A --year run2 
python Util/prepareJobs.py -i Job_bus/lqhAti.txt --mode append --task LimitPlot --mass_point 300 --channel C --coupling_value rtc04 --higgs A --year run2
python Util/prepareJobs.py -i Job_bus/lqhAti.txt --mode append --task LimitPlot --mass_point 350 --channel C --coupling_value rtc04 --higgs A --year run2
python Util/prepareJobs.py -i Job_bus/lqhAti.txt --mode append --task LimitPlot --mass_point 400 --channel C --coupling_value rtc04 --higgs A --year run2
python Util/prepareJobs.py -i Job_bus/lqhAti.txt --mode append --task LimitPlot --mass_point 500 --channel C --coupling_value rtc04 --higgs A --year run2
python Util/prepareJobs.py -i Job_bus/lqhAti.txt --mode append --task LimitPlot --mass_point 600 --channel C --coupling_value rtc04 --higgs A --year run2
python Util/prepareJobs.py -i Job_bus/lqhAti.txt --mode append --task LimitPlot --mass_point 200 --channel C --coupling_value rtc04 --higgs A --year run2
python Util/prepareJobs.py -i Job_bus/lqhAti.txt --mode append --task LimitPlot --mass_point 250 --channel C --coupling_value rtc04 --higgs A --year run2 --interference #if you want to use interference sample
```
And you can use 
```
python Util/prepareJobs.py --mode read -i Job_bus/lqhAti.txt
```
to read the content of Job_bus/lqhAti.txt.

Also, you can use 
```
python Util/prepareJobs.py --mode reset -i Job_bus/lqhAti.txt
```
to reset the content.

Now, you should produce the shell script for each job:

```
python Util/write_shell_for_condor.py --Job_bus_Name Job_bus/lqhAti.txt
```
Then you would see the output information on your terminal

Feed your Job_bus file again into  Util/write_condor_job.py
```
python Util/write_condor_job.py --Job_bus_Name Job_bus/lqhAti.txt
```
And a condor script named `scripts/condor.sub` is created.

Now, please submit it with condor_submit
```
condor_submit scripts/condor.sub
```



# 7. Multiple Limit Plots

Merged selected multiple plots together. You should make sure you already make every single limit plot already. With `interp` option, you can plot 2D exclusion plot. Please note that you should not do `cmsenv` in this specific part (To plot 2D limit plot).
```
source env.sh
python ./Merged_Plots.py --channel C --year run2 --coupling_values rtu0p1 rtu0p4 rtu0p8 rtu1p0 --plot_y_max 1000 --plot_y_min 0.01 --Masses 200 300 350 400 500 600 700 800 900 1000 --outputdir [your/favour/folder] [--interp] [--paper] [--unblind]
```

# 8. Integrating results

This section is mainly for saving the results in AN structure specifically.
Let's say if your original merged-limit folder was: /your/output/folder/for/merged/plots_limit:
```
source example/IntegrateResults.sh rtc /your/output/folder/for/ 
```
Then, please check created folders for:
- ttc_merged
- Impacts_Plots
- LimitsTables

## 8.1 small example for integrating limit table
To produce the results in with particular era/channel/coupling for limit table:
```
python Results_Integrate.py --mode LimitTables --year 2016postapv --channel ee --coupling_value rtc0p4
```
## 8.2 small example for integrating SignalExctraction
```
python Results_Integrate.py --mode SignalExtraction --year 2018 --channel ee --mass 350 --coupling_value rtu0p4
```
## 8.3 Small example for integrating limit plots (only merged ones)
Let's say if your original merged-limit folder was: /your/output/folder/for/merged/plots_limit:
Then: 
```
python Results_Integrate.py --mode LimitPlots --limit_original_dir /your/output/folder/for/ --coupling rtu
```
For interference one:
```
python Results_Integrate.py --mode LimitPlots --limit_original_dir /your/output/folder/for/ --coupling rtu --interference
```
## 8.4 Workflow Toolkits
### Step1. Initialize setting and rebin the BDT ntuple.
```
sh example/step1_InitAndRebin.sh [BDT ntuple input directory] [--unblind]
```
### Step2. Prepare datacard.
```
sh example/step2_prepare_datacard.sh [rtc/rtu]
```

### Step2.1 Submit limit calculation to condor (See Section 6.)

### Step3. After all the limit computations are finished, use following command to plot it.
```
sh example/step3_plot_limit.sh [rtc/rtu] [outputdir] [--unblind]
```

### Step4. Merge and display the plots with different year/mass/coupling strength.
```
sh example/step4_merge_plot.sh [rtc/rtu] [outputdir] [--unblind]
```
Plot 2D limit (Probably need to reopen lxplus and run without `cmsenv`.
```
sh example/step4_2_merge_plot_2D.sh [outputdir] [--unblind] 
```

### Step5. Make limit table
```
sh example/step5_make_limit_tables.sh [rtc/rtu] [--unblind]
```
### Step6. Impact plot
Use tmux to run all the impact task in batch. (Please change the target you want to run in the shell file)
```
sh example/step6_1_batch_plot_impact.sh [rtc/rtu] [outputdir] [--unblind]
```
If you want to run individually (detail information is stored in shell file).
```
sh example/plot_Impact.sh [era] [channel] [mass] [coupling(rtc01 etc.)] [s_plus_b/b_only] [pure/interference] 0 1.0 [outdir] [--unblind]
```
You can use this command to check the status of each step.
```
sh example/check_Impact_log_file.sh [rtc/rtu] [storage_dir(previous outputdir)] [FitDiagnostics/diffNuisances/Impact_doInitFit/...]
```
Plot the to the pdf format.
```
sh example/step6_2_plot_Impact_pdf.sh [rtc04/rtu04] [storage_dir(previous outputdir)] [--unblind]
```
Integrate them into latex form.
```
sh example/step6_3_integrate_Impact.sh [storage_dir(previous outputdir)]
```
Move to Impact plots to AN
```
sh example/step6_4_move_Impact_plot_to_AN.sh [AN directory]
```

### Aux. Compare two expected limit
To compared two expected limit, please enter the comparison directories name like following. The directory should have all the root/txt files under it.
```
python example/compare_different_limit.py --ref_dir [dir_for_comparison] --new_dir [dir_for_comparison] --coupling_values rtc0p1 rtc0p4 rtc1p0 [--interference]
```

# 9. Trouble Shooting 

## 9.1 Possible bugs in ReBin.py

If you encounter the error message like
```
Traceback (most recent call last):
  File "./ReBin.py", line 142, in <module>
    h_ttV.Add( f_in.Get(prefix+"ttZtoQQ"+inuis) )
TypeError: none of the 3 overloaded methods succeeded. Full details:
  bool TH1::Add(TF1* h1, double c1 = 1, const char* option = "") =>
    could not convert argument 1
  bool TH1::Add(const TH1* h1, double c1 = 1) =>
    could not convert argument 1
  bool TH1::Add(const TH1* h, const TH1* h2, double c1 = 1, double c2 = 1) =>
    takes at least 2 arguments (1 given)
```

You should tune the name of histogram you want to "get" and "rebin", instead of "naming", to be consistent with the histograms names in input file.
For this case, ttZtoQQ->ttZToQQ in line 142 for year2016postapv.

## 9.2 Possible bugs in runlimit.py

If you encounter the error message like
```
Traceback (most recent call last):
  File "/afs/cern.ch/user/z/zhenggan/work_space/CMSSW_10_2_13/bin/slc7_amd64_gcc700/text2workspace.py", line 63, in <module>
    MB.doModel(justCheckPhysicsModel=options.justCheckPhysicsModel)
  File "/afs/cern.ch/user/z/zhenggan/work_space/CMSSW_10_2_13/python/HiggsAnalysis/CombinedLimit/ModelTools.py", line 110, in doModel
    if not justCheckPhysicsModel: self.doObservables()
  File "/afs/cern.ch/user/z/zhenggan/work_space/CMSSW_10_2_13/python/HiggsAnalysis/CombinedLimit/ShapeTools.py", line 61, in doObservables
    self.prepareAllShapes();
  File "/afs/cern.ch/user/z/zhenggan/work_space/CMSSW_10_2_13/python/HiggsAnalysis/CombinedLimit/ShapeTools.py", line 332, in prepareAllShapes
    shape = self.getShape(b,p); norm = 0;
  File "/afs/cern.ch/user/z/zhenggan/work_space/CMSSW_10_2_13/python/HiggsAnalysis/CombinedLimit/ShapeTools.py", line 573, in getShape
    raise RuntimeError, "Failed to find %s in file %s (from pattern %s, %s)" % (objname,finalNames[0],names[1],names[0])
RuntimeError: Failed to find ttc2016postapv_tzq in file FinalInputs/2016postapv/ttc_a_rtc04_MA500/TMVApp_500_em.root (from pattern ttc2016postapv_$PROCESS, FinalInputs/2016postapv/ttc_a_rtc04_MA500/TMVApp_500_em.root)
Error when running the combination:
	Failed to convert the input datacard from LandS to RooStats format. The lines above probably contain more information about the error.
combine -M AsymptoticLimits datacards_ttc_2016postapv/ttc_datacard_2016postapv_SR_em_em_MA500_rtc04.txt -t -1 > datacards_ttc_2016postapv/log/ttc_datacard_2016postapv_SR_em_em_MA500_rtc04.log
allparameters: ('500', '04')
04 500
```

You should tune the name of histogram you want to "get" and "rebin", instead of "naming",to be consistent with the histograms names in input file.

For this case, tzq -> tZq for year2016postapv while in processing ReBin.py.

## 9.3 Possible Common Fit Minimizer Options in combine:
```
--cminDefaultMinimizerStrategy 0 --cminDefaultMinimizerTolerance=1.0
```
Like the above option fix the Run-2 combined channel impact plot.
NB: they are added in the code but while run you have to apply from command line option
e.g
```
python ./SignalExtraction_Estimation.py -y run2 -c C --mode Impact_doInitFit  --coupling_value rtc04 --mass_point 350 --cminDefaultMinimizerStrategy 0 --cminDefaultMinimizerTolerance=1.0
```

### 10. Appendix from Raman

## For signal shape comparison 
python OverlappingPlots.py; cp -r plots_SignalShapeComparison/ /afs/cern.ch/work/k/khurana/public/AnalysisStuff/ttc


## for rescaling signal
sigscale rateParam * TAToTTQ_rtc01_MA350 0.01 [0.009999,0.01111]


## Stack plots 
python stackhist.py fitDiagnostics_C_20161718_asimov_t_0_SignalExtractionChecks2017.root ee asimov 20161718
python stackhist.py fitDiagnostics_C_20161718_asimov_t_0_SignalExtractionChecks2017.root em asimov 20161718
python stackhist.py fitDiagnostics_C_20161718_asimov_t_0_SignalExtractionChecks2017.root mm asimov 20161718

nuisance edit rename * * jes2016 jes2017
nuisance edit rename * * jes2018 jes2017
nuisance edit rename * * jes2016apv jes2017

page 124 of the AN for theory cross-section uncertainty 



## limit model for 1 year is done now. 
## nuisnace shapes used for the fitting 
## Signal shape comparison 
## post fit plots 
## combination for full Run 2 
## fit diagnostics test, mainly pulls, impacts and goodness of fit for the model. 
## add the interference samples to see the results. 
## perform 2d scans.  
