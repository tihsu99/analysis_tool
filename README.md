# Analysis Tool
This tool is made for plotting distribution, skim the root files (`kinematic_study`), and further proceed to limit extraction. The main input is controled by the `json` files in `data` and main functions are defined in the `h` files in `script`. Since it utilize the novel function in RDataFrame, it **requires ROOT v6.26** and thus **do not run cmsenv**(except for **limit study**) , otherwise it will conflict with each other.

To run on lxplus9:
```
cmssw-el7
```
# Installation
To install combine tools, we follow combine v9 recommodation
```
cmsrel CMSSW_11_3_4
cd CMSSW_11_3_4/src
cmsenv
git clone https://github.com/cms-analysis/HiggsAnalysis-CombinedLimit.git HiggsAnalysis/CombinedLimit
cd HiggsAnalysis/CombinedLimit
```
Update to a recommended tag - currently the recommended tag is v9.1.0.
```
cd $CMSSW_BASE/src/HiggsAnalysis/CombinedLimit
git fetch origin
git checkout v9.1.0
scramv1 b clean; scramv1 b # always make a clean build
```
Install CombineHarvester package
```
cd $CMSSW_BASE/src
git clone https://github.com/cms-analysis/CombineHarvester.git CombineHarvester
cd CombineHarvester
git checkout v2.0.0
scram b
```
Install this package
```
cd $CMSSW_BASE/src
git clone git@github.com:ExtraYukawa/bHplusAnalysis.git
cd analysis_tool
```
Please note that `LimitModel` needs to be run under `cmssw-el7` while other parts do not. Please make sure to run `cmssw-el7` when performing limit study.
# Structure
## Input - sample
The sample information should be keep in `data/sample.json`. It contains following information:
1. **xsec**:  cross section for MC samples.
2. **xsec_err**: ratio of cross section error (Percentage).
3. **Label**: Indicate whether this sample is MC or data or data drivien, background or signal.
4. **Category**: The group/process this sample belongs to.
## Input - cut
The region definition is kept in `data/cut.json`. It supports multiple regions and channels definition. It follows the structure below:
- Region name
  - channel\_cut
    - Channel name
      - cut name: Channel cut definition
  - general\_cut
    - cut name: cut definition
## Input - variable
The variable definition is kept in `data/variable.json`. **All the new variables and variables used to vary nuisance (even it is already defined in NanoAOD)** should be in this file. Note that the variables are defined following the order in this file, so **order matters**. It contains following information:
1. **Def**: Definition of this variable. If it is defined, just type "Defined".
2. **Labels**: Labels of this variable. In later stage, we can utilize it to control which group of variables to use. Please note that if this variable is **MC only**, please type "MC".
3. **Save**: This is highly related to Labels, it means when certain group is called, the variable will be saved in the skim root file.
There is a special treatment that first pump the single value to `RVec` and then restore it with `RVec[0]`. This is meant to make it possible to vary together with other variables that are `RVec` when performing nuisance study.
## Input - histogram
The registered histograms are kept in `data/histogram.json`. Note that `nbin` is defined the plotting `nbin`. When generating the histogram, we actually use 600 times `nbin` in order to provide flexibility for future rebin purpose. It contains following information:
1. **Title**
2. **xlow**
3. **xhigh**
4. **nbin**
5. **Labels**: Same function as `Labels` in variable part.
## Input - nuisance
The nuisance information is stored in `data/nuisance.json`. It follows the structure below:
- Name of varition
  - Nominal: List of variables that change
  - Def: RVec of variated varialbe definition 
  - Label: affect which type of data [MC/data\_driven]
## Input - trigger
The trigger information is stored in `data/trigger.json`. It follows the structure below:
- Name of trigger
 - Channel: List of channels that use this trigger
 - Dataset: Only for data, this define the dataset that uses this trigger
 - Trigger: Era: Triggers for that era, that are combined with `or` (you can define the whole logic sentence instead, so arbitary trigger should be possible)
## Input - MET_filter
The list of MET filters is stored in `data/MET_filter.json`. Some files that might not have certain MET filters, it is solved by code automatically.
