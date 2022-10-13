
# Enviroment Setup
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
# Install the CombineHarvester Tool
```
bash <(curl -s https://raw.githubusercontent.com/cms-analysis/CombineHarvester/master/CombineTools/scripts/sparse-checkout-ssh.sh)
cd $CMSSW_BASE/src
cd CombineHarvester
scram b -j 8
```

## Higgs Combination Tool Installation(Only For Raman) 
Follow the Higgs Combination Twiki to install the combine package and compile it, 
 (add the link to combine Twiki  here )
```
source envsetter.sh
```

### Install the code 
The code is part of the repository ttcbar, to get it simply do git clone: 
```
cd $CMSSW_BASE/src/HiggsAnalysis
git clone git@github.com:ExtraYukawa/LimitModel.git
```
### Initialization

Note: the initialization is to be done only once. 
```
cd $CMSSW_BASE/src/HiggsAnalysis/LimitModel/
python Init.py --year 2017 --channel all
python Init.py --year 2018 --channel all
python Init.py --year 2016apv --channel all
python Init.py --year 2016postapv --channel all

```
If you don't want _chargeflipYEAR nuisances for ee channel in year2017 for example, you can remove it through the argument --blacklist
```
cd $CMSSW_BASE/src/HiggsAnalysis/LimitModel/
python Init.py --year 2017 --channel ee --blacklist _chargefilpYEAR  
```


### Rebin and merging of processes 

```
cd $CMSSW_BASE/src/HiggsAnalysis/LimitModel/ 
cmsenv 
```

Use the ReBin.py macro to perform two main tasks: 

1. Merge the histograms for various processes and make a new histogram which is sum of others, this is to make sure we don't have huge stats fluctuations. histograms for same/similar physics Processes are added. 

2. Once merging of histograms are done, each of these histogram is then rebinned, (uniform or non-uniform) depending on the needs. 

Normally, you should use the following commands.
```
python ReBin.py -c all --Couplings  0p4 --Coupling_Name rtc --y 2017 --Masses 200 300 350 400 500 600 700 800 900 1000 --inputdir /afs/cern.ch/user/g/gkole/work/public/forTTC/BDT_output_with_signalXS_correctNevents; 

python ReBin.py -c all --Couplings  0p4 --Coupling_Name rtc --y 2018 --Masses 200 300 350 400 500 600 700 800 900 1000 --inputdir /afs/cern.ch/user/g/gkole/work/public/forTTC/BDT_output_with_signalXS_correctNevents;

python ReBin.py -c all --Couplings  0p4 --Coupling_Name rtc --y 2016postapv --Masses 200 300 350 400 500 600 700 800 900 1000 --inputdir /afs/cern.ch/user/g/gkole/work/public/forTTC/BDT_output_with_signalXS_correctNevents;

python ReBin.py -c all --Couplings  0p4 --Coupling_Name rtc --y 2016apv --Masses 200 300 350 400 500 600 700 800 900 1000 --inputdir /afs/cern.ch/user/g/gkole/work/public/forTTC/BDT_output_with_signalXS_correctNevents;`
```

And you will see thousands of message like `Warning: ttc2018_TTTo1L_dieleTrigger2018Down doesn't exist`, you could just ignore it.
If you don't want your terminal filled with these messages, you can add [-q/--quiet] like:
```
python ReBin.py -c all --Couplings  0p4 --y 2017 --Masses 200 300 350 400 500 600 700 800 900 1000 --inputdir /afs/cern.ch/user/g/gkole/work/public/forTTC/BDT_output_with_signalXS_correctNevents -q; 
```

And once this step is done, there are several rebined root files under FinalInputs or your favoured output directory.



#Before running the macro, some values needs to be set, specially the input and output paths. 


The new output files are then used for the limit extraction. 

### Create template card for one region  datacards 
The next step is to create the datacards. The input needed for making datacards are; 
1. data_info/Datacard_Input/{Year}/Datacard_Input_{channel}.json
2. data_info/Sample_Names/process_name_{year}.json
3. data_info/NuisanceList/nuisance_list_{year}_{channel}.json

The datacards for each decay mode, each year can be created using following syntax, just copy paste them to terminal and wait for it to be over. 

```
python prepareCards.py -y 2016apv -c em -reg 'SR_em'
python prepareCards.py -y 2016apv -c ee -reg 'SR_ee'
python prepareCards.py -y 2016apv -c mm -reg 'SR_mm'


python prepareCards.py -y 2016postapv -c em -reg 'SR_em'
python prepareCards.py -y 2016postapv -c ee -reg 'SR_ee'
python prepareCards.py -y 2016postapv -c mm -reg 'SR_mm'

python prepareCards.py -y 2017 -c em -reg 'SR_em'
python prepareCards.py -y 2017 -c ee -reg 'SR_ee'
python prepareCards.py -y 2017 -c mm -reg 'SR_mm'


python prepareCards.py -y 2018 -c em -reg 'SR_em'
python prepareCards.py -y 2018 -c ee -reg 'SR_ee'
python prepareCards.py -y 2018 -c mm -reg 'SR_mm'
```
Note: If you want to prepare the template datacard again, you can add as following
```
python prepareCards.py -y 2018 -c em -reg 'SR_em' --reset
```

### Combine the cards for all regions to make a jumbo card 
```
cd datacards_ttc_2016postapv; combineCards.py em=ttc_datacard_2016postapv_SR_em_em_template.txt ee=ttc_datacard_2016postapv_SR_ee_ee_template.txt mm=ttc_datacard_2016postapv_SR_mm_mm_template.txt > ttc_datacard_2016postapv_SR_C_C_template.txt ; cd -

cd datacards_ttc_2016apv; combineCards.py em=ttc_datacard_2016apv_SR_em_em_template.txt ee=ttc_datacard_2016apv_SR_ee_ee_template.txt mm=ttc_datacard_2016apv_SR_mm_mm_template.txt > ttc_datacard_2016apv_SR_C_C_template.txt ; cd -

cd datacards_ttc_2017; combineCards.py em=ttc_datacard_2017_SR_em_em_template.txt ee=ttc_datacard_2017_SR_ee_ee_template.txt mm=ttc_datacard_2017_SR_mm_mm_template.txt > ttc_datacard_2017_SR_C_C_template.txt ; cd -

cd datacards_ttc_2018; combineCards.py em=ttc_datacard_2018_SR_em_em_template.txt ee=ttc_datacard_2018_SR_ee_ee_template.txt mm=ttc_datacard_2018_SR_mm_mm_template.txt > ttc_datacard_2018_SR_C_C_template.txt ; cd -

rm -rf datacards_ttc_run2
mkdir datacards_ttc_run2 
cp datacards_ttc_2016apv/ttc_datacard_2016apv_SR_C_C_template.txt datacards_ttc_run2
cp datacards_ttc_2016postapv/ttc_datacard_2016postapv_SR_C_C_template.txt datacards_ttc_run2
cp datacards_ttc_2017/ttc_datacard_2017_SR_C_C_template.txt datacards_ttc_run2
cp datacards_ttc_2018/ttc_datacard_2018_SR_C_C_template.txt datacards_ttc_run2
cd datacards_ttc_run2
combineCards.py year2016apv=ttc_datacard_2016apv_SR_C_C_template.txt year2016postapv=ttc_datacard_2016postapv_SR_C_C_template.txt year2017=ttc_datacard_2017_SR_C_C_template.txt year2018=ttc_datacard_2018_SR_C_C_template.txt > ttc_datacard_run2_SR_C_C_template.txt; cd -;
```

### Run the cards 

#### 2016postapv
```
python runlimits.py -c em --Couplings rtc04 -y 2016postapv --Masses 200 300 350 400 500 600 700  --outputdir [your/favoured/output/folder]
python runlimits.py -c mm --Couplings rtc04 -y 2016postapv --Masses 200 300 350 400 500 600 700  --outputdir [your/favoured/output/folder]
python runlimits.py -c ee --Couplings rtc04 -y 2016postapv --Masses 200 300 350 400 500 600 700  --outputdir [your/favoured/output/folder]
python runlimits.py -c C --Couplings rtc04 -y 2016postapv --Masses 200 300 350 400 500 600 700  --outputdir [your/favoured/output/folder]
```

#### 2016 apv 
```
python runlimits.py -c em --Couplings rtc04 -y 2016apv --Masses 200 300 350 400 500 600 700  --outputdir [your/favoured/output/folder]
python runlimits.py -c mm --Couplings rtc04 -y 2016apv --Masses 200 300 350 400 500 600 700  --outputdir [your/favoured/output/folder]
python runlimits.py -c ee --Couplings rtc04 -y 2016apv --Masses 200 300 350 400 500 600 700  --outputdir [your/favoured/output/folder]
python runlimits.py -c C --Couplings rtc04 -y 2016apv --Masses 200 300 350 400 500 600 700  --outputdir [your/favoured/output/folder]
```
#### 2017
```
python runlimits.py -c em --Couplings rtc04 -y 2017 --Masses 200 300 350 400 500 600 700 800 900 1000 --outputdir [your/favoured/output/folder]
python runlimits.py -c mm --Couplings rtc04 -y 2017 --Masses 200 300 350 400 500 600 700 800 900 1000 --outputdir [your/favoured/output/folder]
python runlimits.py -c ee --Couplings rtc04 -y 2017 --Masses 200 300 350 400 500 600 700 800 900 1000 --outputdir [your/favoured/output/folder]
python runlimits.py -c C --Couplings rtc04 -y 2017 --Masses 200 300 350 400 500 600 700 800 900 1000 --outputdir [your/favoured/output/folder]
```
#### 2018
```
python runlimits.py -c em --Couplings rtc04 -y 2018 --Masses 200 300 350 400 500 600 700 800 900 1000 --outputdir [your/favoured/output/folder]
python runlimits.py -c mm --Couplings rtc04 -y 2018 --Masses 200 300 350 400 500 600 700 800 900 1000 --outputdir [your/favoured/output/folder]
python runlimits.py -c ee --Couplings rtc04 -y 2018 --Masses 200 300 350 400 500 600 700 800 900 1000 --outputdir [your/favoured/output/folder] 
python runlimits.py -c C  --Couplings rtc04 -y 2018 --Masses 200 300 350 400 500 600 700 800 900 1000 --outputdir [your/favoured/output/folder]
```
### Run2
```
python runlimits.py -c C --Couplings rtc01 -y run2  --Masses 200 300 350 400 500 600 700 800 900 1000 --outputdir [your/favoured/output/folder]	
python runlimits.py -c C --Couplings rtc04 -y run2  --Masses 200 300 350 400 500 600 700 800 900 1000 --outputdir [your/favoured/output/folder]	
python runlimits.py -c C --Couplings rtc08 -y run2  --Masses 200 300 350 400 500 600 700 800 900 1000 --outputdir [your/favoured/output/folder]	
python runlimits.py -c C --Couplings rtc10 -y run2  --Masses 200 300 350 400 500 600 700 800 900 1000 --outputdir [your/favoured/output/folder]	
```
But, generally, it would take about 8 hrs to finish the calculation for full run2 limit plots, thus, it would be good to run it on condor, and here we provide the steps to get script for condor, and take rtc0p4 full run2 limit plot for example:

```
python ./Util/write_shell_for_condor.py --channel C --year run2 --coupling_value rtc04 --Masses 200 300 350 400 500 600 700 --higgs A --mode LimitPlot --outputdir [your/favoured/output/folder]
python ./Util/write_condor_job.py --shell_script ./scripts/shell_script_LimitPlot_for_C_run2.sh 
condor_submit ./scripts/condor.sub 
```
####


## For impacts and pulls 
source runallchecks.sh SignalExtractionChecks2017 20161718 C datacards_ttc_run2/ttc_datacard_run2_SR_C_C_MA200_rtc04.txt 

source runallchecks.sh SignalExtractionChecks2017 2017 C datacards_ttc_2017/ttc_datacard_2017_SR_C_C_MA200_rtc04.txt
* autoMCStats 10 0 1

Same as the case for combined one in limit plot calculation ,condor job is strongly suggested. And here, we take rtc0p4 full run2 limit plot for example as well:
```
python ./Util/write_shell_for_condor.py --channel C --year run2 --coupling_value rtc04 --mass_point 300 --higgs A --mode Impact --outputdir /eos/user/z/zhenggan/www/run2/Impacts/
python ./Util/write_condor_job.py --shell_script ./scripts/shell_script_Impact_for_C_run2.sh
condor_submit ./scripts/condor.sub
```

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

## Trouble Shooting 

### For ReBin.py

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

### For runlimits.py

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



## limit model for 1 year is done now. 
## nuisnace shapes used for the fitting 
## Signal shape comparison 
## post fit plots 
## combination for full Run 2 
## fit diagnostics test, mainly pulls, impacts and goodness of fit for the model. 
## add the interference samples to see the results. 
## perform 2d scans.  
