import json
from Util.General_Tool import CheckFile
from Init_Tool.Nuisance_Group import DefineGroup

def nui_producer(year,blacklist=[],whitelist=[],outputdir='./data_info',channel='all', breakdown = False):
    """

    Uncorrelated sources (they need to be kept in the datacard):
    ------------------------------------------------------------
    ExtrapDown,
    ExtrapUp, 
    InterpDown ,
    InterpUp , 
    StatDown, 
    StatUp, 
    XSec_BRUnc_DYJets_bDown,
    XSec_BRUnc_DYJets_bUp, 
    XSec_BRUnc_DYJets_cDown, 
    XSec_BRUnc_DYJets_cUp, 
    XSec_BRUnc_WJets_cDown ,
    XSec_BRUnc_WJets_cUp,

    Correlated sources (they should not appear in the datacard but will be in the inputs already):
    ----------------------------------------------------------------------------------------------
    The following ones should be correlated to sig201Xscale:
        LHEScaleWeight_muFDown, 
        LHEScaleWeight_muFUp,
        LHEScaleWeight_muRDown, 
        LHEScaleWeight_muRUp, 

    The following ones should be correlated to sig201Xps:
        PSWeightFSRDown, 
        PSWeightFSRUp, 
        PSWeightISRDown,
        PSWeightISRUp, 

    The following should be correlated to pileup:
        PUWeightDown, 
        PUWeightUp, 

    The following should be correlated to jer201X:
        jerUp, 
        jerDown, 

    The following should be correlated to jes201X:
        jesTotalUp, 
        jesTotalDown

    """
    Corr_nuis_list = ["_sigYEARscale","_sigYEARpdf","_sigYEARps","_jesYEAR"]


    nuis_Init=[
            "_lumiYEAR",
            "_lumiCorrFullRun2",
            "_pileup",
            "_prefire",
            "_muonYEARptCorrection",
            "_muIDYEARsys", 
            "_muIDYEARstat",
            "_eleIDYEARsys",
            "_eleIDYEARstat",
            "_elemuTriggerYEAR" ,
            "_dimuTriggerYEAR",
            "_dieleTriggerYEAR",
            "_ctagYEARstat",
            "_ctagYEARExtrap",
            "_ctagYEARInterp",
            "_ctagLHEmuF",
            "_ctagLHEmuR",
            "_ctagPSFSR",
            "_ctagPSISR",
            "_ctagDYXSb",
            "_ctagDYXSc",
            "_ctagWJetsXSc",
            "_chargeflipYEARstat",
            "_chargeflipYEARsyst",
            "_metYEARunclusterE", 
            "_jesYEAR",
            "_jerYEAR", 
            "_fakeYEAR",
            "_fakeYEAReleStat",
            "_fakeYEARmuStat",
#            "_normTTTo2L","_normSingleTop","_normDY","_normVV","_normVBS","_normttVV","_normttVH","_normttZ","_normttW","_normtZq","_normtttX","_normVVV",
            "_normTTTo2L","_normOthers","_normVV","_normVBS","_normttH","_normttW",
            "_sigYEARscale","_sigYEARpdf","_sigYEARps"] #only for signal
            #"_normTTTo2L","_normttWW","_normttZZ","_normttWZ","_normttZ","_normttW","_normtZq","_normtttX","_normVVV"]
    
    if year=='2017' or year=='2018': 
        nuis_Init.insert(1,"_lumiCorr1718")


    # remove _prefire for 2018:
    if year=='2018':
        nuis_Init.remove("_prefire")

        
    if year=='2016apv' or year=='2016postapv':
        nuis_Init = [nui.replace("_lumiYEAR","_lumi2016") for nui in nuis_Init]

        
    nuis_Final = dict()
    nuis_Final_return = []
    
    corr_nuis_Final =dict()
    corr_nuis_Final_return =[]
    
    Index = 0

    if breakdown:
        ## Three different sets for uncertainty groups defintions
        Set1 = dict() 
        Set1['Total_Experimental'] = []
        Set1['Total_SignalModeling'] = []
        Set1['Total_BackgroundModeling'] = []

        Set2 = dict()
        Set2['Flavour_Tagger'] = []
        Set2['Nonprompt_Lepton'] = []
        Set2['NormttW'] = []
        Set2['Experimental_Rest'] = []
        Set2['Modeling_Rest'] = []
        
    for nui in nuis_Init:
        if nui in blacklist and nui not in whitelist:pass
        else:
            if channel=='ee':
                if 'elemuTriggerYEAR' in nui or 'dimuTriggerYEAR' in nui or 'muIDYEARsys' in nui or 'muIDYEARstat' in nui or '_muonYEARptCorrection' in nui or 'fakeYEARmuStat' in nui:continue
                else:pass 
            elif channel =='mm':
                if "dieleTriggerYEAR" in nui or 'elemuTriggerYEAR' in nui or 'eleIDYEARstat' in nui or 'eleIDYEARsys' in nui or "chargeflipYEAR" in nui or 'fakeYEAReleStat' in nui:continue
                else:pass
            else:
                if "dieleTriggerYEAR" in nui or 'dimuTriggerYEAR' in nui or "chargeflipYEAR" in nui:continue
                else:pass
            #if year=='2018':
            #    if 'prefireYEAR' in nui:continue
            #    else:pass
            nuis_Final[Index] = nui
            nuis_Final_return.append(nui)
            if nui in  Corr_nuis_list:
                nui=nui.replace("YEAR","")

            else:pass
            corr_nuis_Final[Index] = nui
            corr_nuis_Final_return.append(nui)

            Index+=1
            if breakdown:
                nui = nui.replace("_", "")
                nui = nui.replace("YEAR", year)
        
                if "normttW" in nui:
                    Set1['Total_BackgroundModeling'].append(nui)
                    Set2['NormttW'].append(nui)
                elif "sig" in nui:
                    Set1['Total_SignalModeling'].append(nui)
                    Set2['Modeling_Rest'].append(nui)
                elif "fake" in nui:
                    Set1['Total_Experimental'].append(nui)   
                    Set2['Nonprompt_Lepton'].append(nui) 
                elif "ctag" in nui:
                    Set1['Total_Experimental'].append(nui)   
                    Set2['Flavour_Tagger'].append(nui)
                elif "norm" in nui:
                    Set1['Total_BackgroundModeling'].append(nui)
                    Set2['Modeling_Rest'].append(nui)
                else:
                    Set1['Total_Experimental'].append(nui)   
                    Set2['Experimental_Rest'].append(nui) 
    
    CheckFile('{}/nuisance_list_{}_{}.json'.format(outputdir,year,channel),True)    
    with open('{}/nuisance_list_{}_{}.json'.format(outputdir,year,channel),'w') as f:
        json.dump(nuis_Final,f,indent=4)
    CheckFile('{}/corrected_nuisance_list_{}_{}.json'.format(outputdir,year,channel),True)    
    with open('{}/corrected_nuisance_list_{}_{}.json'.format(outputdir,year,channel),'w') as f:
        json.dump(corr_nuis_Final,f,indent=4)
    
    if breakdown:
        File = '{}/nuisance_group_{}_{}_set1.json'.format(outputdir,year,channel)
        CheckFile(File, True) 
        with open(File, 'w') as f:
            json.dump(Set1, f, indent =4 )
        File = '{}/nuisance_group_{}_{}_set2.json'.format(outputdir,year,channel)
        CheckFile(File, True) 
        with open(File, 'w') as f:
            json.dump(Set2, f, indent =4 )

        DefineGroup(outputdir = outputdir) 
    return corr_nuis_Final_return
