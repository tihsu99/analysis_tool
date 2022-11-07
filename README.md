# 0. Suit-up!

In this section, you can just copy and past the command.

## 0.1 Enviroment Setup

Move to your workspace first or
```
mkdir workspace
cd workspace
```
Then,
```
export SCRAM_ARCH=slc7_amd64_gcc700
cmsrel CMSSW_10_2_13
cd CMSSW_10_2_13/src
cmsenv
git clone https://github.com/cms-analysis/HiggsAnalysis-CombinedLimit.git HiggsAnalysis/CombinedLimit

cd $CMSSW_BASE/src/HiggsAnalysis/CombinedLimit
git fetch origin
git checkout v8.2.0
scramv1 b clean; scramv1 b # always make a clean build
```
## 0.2 Install the CombineHarvester Tool

```
bash <(curl -s https://raw.githubusercontent.com/cms-analysis/CombineHarvester/master/CombineTools/scripts/sparse-checkout-ssh.sh)
cd $CMSSW_BASE/src
cd CombineHarvester
scram b -j 8
```

## 0.3 Install the code 

The code is part of the repository ttcbar, to get it simply do git clone: 
```
cd $CMSSW_BASE/src/HiggsAnalysis
git clone git@github.com:ExtraYukawa/LimitModel.git
```

# 1. Initialization

## 1.1 Commands for Input files preparing for datacard production
Note: the initialization is to be done only once. 
```
cd $CMSSW_BASE/src/HiggsAnalysis/LimitModel/
python Init.py --year 2017 --channel all
python Init.py --year 2018 --channel all
python Init.py --year 2016apv --channel all
python Init.py --year 2016postapv --channel all
```
After this step, a folder, data_info, is created. And under this folder, you can find three main different files under data_info:

- data_info/Sample_Names/process_name_{year}.json # Contain the sample names sorting with certain physics process category
- data_info/NuisanceList/nuisance_list_{year}_{channel}.json # Contain the nuisances list for each channel
- data_info/Datacard_Input/{year}/Datacard_Input_{channel}.json # Contain the necessary information for datacard production later.

## 1.2 Block unwanted nuisances (You can skip this)

If you don't want _chargeflipYEAR nuisances for ee channel in year2017 for example, you can remove it through the argument --blacklist
```
cd $CMSSW_BASE/src/HiggsAnalysis/LimitModel/
python Init.py --year 2017 --channel ee --blacklist _chargefilpYEAR  
```


# 2. Rebin and merging of processes 

## 2.1 Commands for histograms rebinning for original BDT_output files

Use the ReBin.py macro to perform two main tasks: 
```
1. Merge the histograms for various processes and make a new histogram which is sum of others, this is to make sure we don't have huge stats fluctuations. histograms for same/similar physics Processes are added. 
2. Once merging of histograms are done, each of these histogram is then rebinned, (uniform or non-uniform) depending on the needs. 
```

Normally, you should use the following commands. (Note that we always use mA as our Mass input in interference case.)
```
python ReBin.py -c all --Couplings  [0p1/0p4/0p8/1p0] --Coupling_Name [rtc/rtu/rtt] --y [year: 2016apv/2016postapv/2017/2018] --Masses [Mass points you want to take into account] --inputdir [input/provided/by/Gouranga] [--interference]; 
```


## 2.2 Cheating tablet for commands (temporary, inputdir will change time by time):

```
python ReBin.py -c all --Couplings  0p4 --Coupling_Name rtc --y 2017 --Masses 200 300 350 400 500 600 700 800 900 1000 --inputdir /eos/cms/store/group/phys_top/ExtraYukawa/BDT_Oct2022/BDT_output/; 

python ReBin.py -c all --Couplings  0p4 --Coupling_Name rtc --y 2018 --Masses 200 300 350 400 500 600 700 800 900 1000 --inputdir /eos/cms/store/group/phys_top/ExtraYukawa/BDT_Oct2022/BDT_output/;

python ReBin.py -c all --Couplings  0p4 --Coupling_Name rtc --y 2016postapv --Masses 200 300 350 400 500 600 700 800 900 1000 --inputdir /eos/cms/store/group/phys_top/ExtraYukawa/BDT_Oct2022/BDT_output/;

python ReBin.py -c all --Couplings  0p4 --Coupling_Name rtc --y 2016apv --Masses 200 300 350 400 500 600 700 800 900 1000 --inputdir /eos/cms/store/group/phys_top/ExtraYukawa/BDT_Oct2022/BDT_output/;

#Interference
python ReBin.py -c all --Couplings  0p4 --Coupling_Name rtc --y 2016apv --Masses 250 300 350 400 550 700 --inputdir /eos/cms/store/group/phys_top/ExtraYukawa/BDT_Oct2022/BDT_output/ --interference;

python ReBin.py -c all --Couplings  0p4 --Coupling_Name rtc --y 2016postapv --Masses 250 300 350 400 550 700 --inputdir /eos/cms/store/group/phys_top/ExtraYukawa/BDT_Oct2022/BDT_output/ --interference;

python ReBin.py -c all --Couplings  0p4 --Coupling_Name rtc --y 2017 --Masses 250 300 350 400 550 700 --inputdir /eos/cms/store/group/phys_top/ExtraYukawa/BDT_Oct2022/BDT_output/ --interference;

python ReBin.py -c all --Couplings  0p4 --Coupling_Name rtc --y 2018 --Masses 250 300 350 400 550 700 --inputdir /eos/cms/store/group/phys_top/ExtraYukawa/BDT_Oct2022/BDT_output/ --interference;
```

And you will see thousands of message like `Warning: ttc2018_TTTo1L_dieleTrigger2018Down doesn't exist`, you could just ignore it.

## 2.3 Quiet the thousands of warning message 

If you don't want your terminal filled with these messages, you can add [-q/--quiet] like:
```
python ReBin.py -c all --Couplings  0p4 --y 2017 --Masses 200 300 350 400 500 600 700 800 900 1000 --inputdir /afs/cern.ch/user/g/gkole/work/public/forTTC/BDT_output_with_signalXS_correctNevents -q; 
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

### 3.2.1 Template Datacard production for certain year

If you already make sure the above steps are settle, then you can produce the template datacards for certain channel in certain year with:

``` 
python prepareCards.py -y {year:2016apv/2016postapv/2017/2018} -c {channel:ee/em/mm} -reg 'SR_{channel:ee/em/mm}' --For template
```
- Result: Datacard template for certain channel in certain year

And after you repeat this command for all the dilepton channels, you can manage to get the combined-channel datacards:
```
python prepareCards.py -y {year} -c C --For template
```

### 3.2.2 Datacard production for each mass point with certain coupling value for certain year

Once you have the datacard template for certain channel, you can use the following command to produce the datacard for certain mass points:
```
python prepareCards.py -y {year:2016apv/2016postapv/2017/2018} -c {channel: em/mm/ee} --For specific -reg 'SR_{channel:ee/em/mm}' --coupling_value [rtc0p4,rtu0p4,rtt0p4... etc] --Masses {List like: 200 300 350 400 500 600 700}; #prerequiest: corresponing datacard template for certain channel
```
- Result: Datacard for certain mass point of certain year in certain channel.

And for channel-combined one, the command is similar:
```
python prepareCards.py -y {year:2016apv/2016postapv/2017/2018} -c C --For specific --coupling_value [rtc0p4,rtu0p4,rtt0p4... etc] --Masses {List like: 200 300 350 400 500 600 700}; #prerequiest: corresponing datacard template for combined-channel
```
- Result: Datacard for certain mass point of certain year in combined-channel.

### 3.2.3 Template Datacard production for run2 for certain dilepton channel

So, to produce the template datacard for `full run2` in certain dilepton channels, you need the template datacard of all the years for this certain channel, and with the following command:
```
python prepareCards.py -y run2 -c {channel:ee/em/mm} -reg 'SR_{channel:ee/em/mm}' --For template
```

- Result: Datacard template for full run2 in certain channel.

### 3.2.4 Datacard production for each mass point with certain coupling value for run2

You should already have run2 datacard template for certain channel, and  
```
python prepareCards.py -y run2 -c {channel:ee/em/mm} -reg 'SR_{channel:ee/em/mm}' --For specific --coupling_value [rtc0p4,rtu0p4,rtt0p4... etc] --Masses {List like: 200 300 350 400 500 600 700};
```
- Result: Datacard for certain mass point with certain coupling value for run2.

### 3.2.5 Template Datacard production for full run2 in combined-channel

You should already have run2 datacard template for all dilepton channels, and
```
python prepareCards.py -y run2 -c C  --For template 

```
- Result: Datacard template for full run2 with channels combined.

### 3.2.6 Datacard production for each mass point for certain coupling value for full run2 in combined-channel

Once you have the datacard template for full run2 with channels combined, then you can obtain the datacard for each mass point for full run2 in combined-channel with
```
python prepareCards.py -y run2 -c C --For specific --coupling_value [rtc0p4,rtu0p4,rtt0p4... etc] --Masses {List like: 200 300 350 400 500 600 700} [--interference] [--scale];
```
- Result: Datacard template for each mass point for certain coupling value for full run2 in combined-channel.

## 3.3 Quick command-list for datacard productions

Example for rtc = 0.4 in low mass regime
```
python prepareCards.py -y 2016apv -c em -reg 'SR_em' --For template
python prepareCards.py -y 2016apv -c ee -reg 'SR_ee' --For template
python prepareCards.py -y 2016apv -c mm -reg 'SR_mm' --For template
python prepareCards.py -y 2016apv -c C  --For template 

python prepareCards.py -y 2016postapv -c em -reg 'SR_em' --For template
python prepareCards.py -y 2016postapv -c ee -reg 'SR_ee' --For template
python prepareCards.py -y 2016postapv -c mm -reg 'SR_mm' --For template
python prepareCards.py -y 2016postapv -c C  --For template 


python prepareCards.py -y 2017 -c em -reg 'SR_em' --For template
python prepareCards.py -y 2017 -c ee -reg 'SR_ee' --For template
python prepareCards.py -y 2017 -c mm -reg 'SR_mm' --For template
python prepareCards.py -y 2017 -c C  --For template 

python prepareCards.py -y 2018 -c em -reg 'SR_em' --For template
python prepareCards.py -y 2018 -c ee -reg 'SR_ee' --For template
python prepareCards.py -y 2018 -c mm -reg 'SR_mm' --For template
python prepareCards.py -y 2018 -c C  --For template 

python prepareCards.py -y run2 -c C --For template  
python prepareCards.py -y run2 -c em -reg 'SR_em' --For template 
python prepareCards.py -y run2 -c ee -reg 'SR_ee' --For template 
python prepareCards.py -y run2 -c mm -reg 'SR_mm' --For template 


python prepareCards.py -y 2016apv -c em -reg 'SR_em' --For specific --coupling_value rtc0p4 --Masses 200 300 350 400 500 600 700;
python prepareCards.py -y 2016apv -c ee -reg 'SR_ee' --For specific --coupling_value rtc0p4 --Masses 200 300 350 400 500 600 700;
python prepareCards.py -y 2016apv -c mm -reg 'SR_mm' --For specific --coupling_value rtc0p4 --Masses 200 300 350 400 500 600 700;
python prepareCards.py -y 2016apv -c C  --For specific --coupling_value rtc0p4 --Masses 200 300 350 400 500 600 700;

python prepareCards.py -y 2016postapv -c em -reg 'SR_em' --For specific --coupling_value rtc0p4 --Masses 200 300 350 400 500 600 700;
python prepareCards.py -y 2016postapv -c ee -reg 'SR_ee' --For specific --coupling_value rtc0p4 --Masses 200 300 350 400 500 600 700;
python prepareCards.py -y 2016postapv -c mm -reg 'SR_mm' --For specific --coupling_value rtc0p4 --Masses 200 300 350 400 500 600 700;
python prepareCards.py -y 2016postapv -c C  --For specific --coupling_value rtc0p4 --Masses 200 300 350 400 500 600 700;

python prepareCards.py -y 2017 -c em -reg 'SR_em' --For specific --coupling_value rtc0p4 --Masses 200 300 350 400 500 600 700;
python prepareCards.py -y 2017 -c ee -reg 'SR_ee' --For specific --coupling_value rtc0p4 --Masses 200 300 350 400 500 600 700;
python prepareCards.py -y 2017 -c mm -reg 'SR_mm' --For specific --coupling_value rtc0p4 --Masses 200 300 350 400 500 600 700;
python prepareCards.py -y 2017 -c C  --For specific --coupling_value rtc0p4 --Masses 200 300 350 400 500 600 700;

python prepareCards.py -y 2018 -c em -reg 'SR_em' --For specific --coupling_value rtc0p4 --Masses 200 300 350 400 500 600 700;
python prepareCards.py -y 2018 -c ee -reg 'SR_ee' --For specific --coupling_value rtc0p4 --Masses 200 300 350 400 500 600 700 ;
python prepareCards.py -y 2018 -c mm -reg 'SR_mm' --For specific --coupling_value rtc0p4 --Masses 200 300 350 400 500 600 700 ;
python prepareCards.py -y 2018 -c C  --For specific --coupling_value rtc0p4 --Masses 200 300 350 400 500 600 700 ;

python prepareCards.py -y run2 -c C  --For specific --coupling_value rtc0p4 --Masses 200 300 350 400 500 600 700;

```

### 3.3.1 Quick command-list for datacard productions with scaling and interference sample

Take 2018 for example, just add `--scale` in the command line. Code automatically take coupling value 0p4 as scaling reference.
```
python prepareCards.py -y 2018 -c C  --For specific --coupling_value rtc0p1 --Masses 200 300 350 400 500 600 700 800 900 1000 --scale;
python prepareCards.py -y 2018 -c C  --For specific --coupling_value rtc0p4 --Masses 200 300 350 400 500 600 700 800 900 1000 --scale;
python prepareCards.py -y 2018 -c C  --For specific --coupling_value rtc0p8 --Masses 200 300 350 400 500 600 700 800 900 1000 --scale;
python prepareCards.py -y 2018 -c C  --For specific --coupling_value rtc1p0 --Masses 200 300 350 400 500 600 700 800 900 1000 --scale;

```
Similar to interference samples. (Note that we always use mA as our Mass input in interference case.)
```
python prepareCards.py -y 2018 -c C  --For specific --coupling_value rtc0p1 --Masses 250 300 350 400 550 700 --scale --interference;
python prepareCards.py -y 2018 -c C  --For specific --coupling_value rtc0p4 --Masses 250 300 350 400 550 700 --scale --interference;
python prepareCards.py -y 2018 -c C  --For specific --coupling_value rtc0p8 --Masses 250 300 350 400 550 700 --scale --interference;
python prepareCards.py -y 2018 -c C  --For specific --coupling_value rtc1p0 --Masses 250 300 350 400 550 700 --scale --interference;
```


# 4. Limit Plots

Note!!!: The pre-requiest for this is the corresponding datacard.

You can try following commands to produce the limit plots, but you would find it will take a century to finish per command :). 
#### 2016postapv
```
python runlimits.py -c em --coupling_value rtc04 -y 2016postapv --Masses 200 300 350 400 500 600 700   
python runlimits.py -c mm --coupling_value rtc04 -y 2016postapv --Masses 200 300 350 400 500 600 700  
python runlimits.py -c ee --coupling_value rtc04 -y 2016postapv --Masses 200 300 350 400 500 600 700  
python runlimits.py -c C --coupling_value rtc04 -y 2016postapv --Masses 200 300 350 400 500 600 700   
```

#### 2016 apv 
```
python runlimits.py -c em --coupling_value rtc04 -y 2016apv --Masses 200 300 350 400 500 600 700  
python runlimits.py -c mm --coupling_value rtc04 -y 2016apv --Masses 200 300 350 400 500 600 700   
python runlimits.py -c ee --coupling_value rtc04 -y 2016apv --Masses 200 300 350 400 500 600 700   
python runlimits.py -c C --coupling_value rtc04 -y 2016apv --Masses 200 300 350 400 500 600 700   
```
#### 2017
```
python runlimits.py -c em --coupling_value rtc04 -y 2017 --Masses 200 300 350 400 500 600 700 800 900 1000  
python runlimits.py -c mm --coupling_value rtc04 -y 2017 --Masses 200 300 350 400 500 600 700 800 900 1000  
python runlimits.py -c ee --coupling_value rtc04 -y 2017 --Masses 200 300 350 400 500 600 700 800 900 1000  
python runlimits.py -c C --coupling_value rtc04 -y 2017 --Masses 200 300 350 400 500 600 700 800 900 1000  
```
#### 2018
```
python runlimits.py -c em --coupling_value rtc04 -y 2018 --Masses 200 300 350 400 500 600 700 800 900 1000 
python runlimits.py -c mm --coupling_value rtc04 -y 2018 --Masses 200 300 350 400 500 600 700 800 900 1000 
python runlimits.py -c ee --coupling_value rtc04 -y 2018 --Masses 200 300 350 400 500 600 700 800 900 1000 
python runlimits.py -c C  --coupling_value rtc04 -y 2018 --Masses 200 300 350 400 500 600 700 800 900 1000 
```
### Run2
```
python runlimits.py -c C --coupling_value rtc01 -y run2  --Masses 200 300 350 400 500 600 700 800 900 1000 
python runlimits.py -c C --coupling_value rtc04 -y run2  --Masses 200 300 350 400 500 600 700 800 900 1000 
python runlimits.py -c C --coupling_value rtc08 -y run2  --Masses 200 300 350 400 500 600 700 800 900 1000 
python runlimits.py -c C --coupling_value rtc10 -y run2  --Masses 200 300 350 400 500 600 700 800 900 1000 
```
### Run2(Interference)
```
python runlimits.py -c C --coupling_value rtc01 -y run2  --Masses 250 300 350 400 550 700 --interference
python runlimits.py -c C --coupling_value rtc04 -y run2  --Masses 250 300 350 400 550 700 --interference
python runlimits.py -c C --coupling_value rtc08 -y run2  --Masses 250 300 350 400 550 700 --interference
python runlimits.py -c C --coupling_value rtc10 -y run2  --Masses 250 300 350 400 550 700 --interference
```
#### Plot Limits 

After the programs is finished, you should use [--plot_only] and [--outputdir] to see the plots. Like:
```
python runlimits.py -c [C,ee,em,ee] --coupling_value [rtc04,rtu04 etc] -y [2016apv,2016postapv,2017,2018] --Masses [Mass list] --outputdir [your/favoured/output/folder] --plot_only [--interference];
```


Note: Generally, it would take > 1 day to finish the calculation for full run2 limit plots. In section `6`, we provide the steps to get script for condor, and take rtc0p4 full run2 limit plot for low regime (200-700GeV) for example.

# 5. For impacts and pulls and post/pre-fit distribution


Step1 -> convert datacard to workspace files distribution. O(time) ~ 10 sec. For fullrun2: O(time) ~ 3mins.
```
python ./SignalExtraction_Estimation.py -y 2018 -c ee --mode datacard2workspace --coupling_value rtu04 --mass_point 800
```

Step2 -> FitDiagnostics. O(time) ~ O(3mins~15mins) for single year. time  ~ O(2.5-3hr )  
```
python ./SignalExtraction_Estimation.py -y 2018 -c ee --mode FitDiagnostics --coupling_value rtu04 --mass_point 800
```

Step3 -> preFit distribution. O(time) ~ 1 sec
```
python ./SignalExtraction_Estimation.py -y 2018 -c ee --mode preFitPlot --coupling_value rtu04 --mass_point 800 --text_y 800
```

Step4 -> postFit distribution.
```
python ./SignalExtraction_Estimation.py -y 2018 -c ee --mode postFitPlot --coupling_value rtu04 --mass_point 800 --text_y 800
```

Step5 -> Calculating Pulls for each nuisances and background.
```
python ./SignalExtraction_Estimation.py -y 2018 -c ee --mode diffNuisances --coupling_value rtu04 --mass_point 800
```

Step6 -> Plot the pulls.
```
python ./SignalExtraction_Estimation.py -y 2018 -c ee --mode PlotPulls --coupling_value rtu04 --mass_point 800
```

Step6 -> Init Fit for Impact. O(time) ~ 30 sec. O(time) ~ 5hrs for Combined. 
```
python ./SignalExtraction_Estimation.py -y 2018 -c ee --mode Impact_doInitFit --coupling_value rtu04 --mass_point 800
```

Step7 -> Do Fits for Impacts. You need to wait all the jobs completed. O(time) ~ 20-40 mins for single year. 

```
python ./SignalExtraction_Estimation.py -y 2018 -c ee --mode Impact_doFits --coupling_value rtu04 --mass_point 800
```
Step8: Plot Impacts.  O(time) ~ 30 sec.
```
python ./SignalExtraction_Estimation.py -y 2018 -c ee --mode Plot_Impacts --coupling_value rtu04 --mass_point 800
```

Step9: Copy results to your given folder.  O(time) ~ 30 sec.
```
python ./SignalExtraction_Estimation.py -y 2018 -c ee --mode ResultsCopy --coupling_value rtu04 --mass_point 800 --dest [Your/Given/OutputFolder]
```
Under this command, take this command for example, it will copy the local folder: SignalExtraction/2018/ee/rtu04/A/800/b_only/ as Your/Given/OutputFolder/`SignalExtraction/2018/ee/rtu04/A/800/b_only/`

# 6. Condor Jobs

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

## 6.2 Condor Jobs for limit plots

The steps are very simple. The pre-requiest for this is the corresponding datacard.
For channel-combined in run2 with rtc04, MA=300GeV
```
python ./Util/write_shell_for_condor.py --channel C --year run2 --coupling_value rtc04 --mass_point 300 --higgs A --mode Impact --outputdir [Your/output/folder/ForImpacts]
python ./Util/write_condor_job.py --shell_script ./scripts/shell_script_Impact_for_C_run2.sh
condor_submit scripts/condor.sub
```
Note: After you collect result, you need to plot them! Please see the corresponding command in section 4.

# 7. Multiple Limit Plots

Merged selected multiple plots together. You should make sure you already make every single limit plot already. 
```
python ./Merged_Plots.py --channel C --year run2 --coupling_values rtu0p1 rtu0p4 --plot_y_max 1000 --plot_y_min 0.01 --outputdir [your/favour/folder]
```


# 8. Trouble Shooting 

## 8.1 Possible bugs in ReBin.py

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

## 8.2 Possible bugs in runlimit.py

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


### 9. Appendix from Raman

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
