import json
from Util.General_Tool import CheckFile

def nui_producer(year,blacklist=[],whitelist=[],outputdir='./data_info',channel='all'):
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
            "_muIDYEARsys", 
            "_muIDYEARstat",
            "_eleIDYEARsys",
            "_eleIDYEARstat",
            "_ctagYEARstat",
            "_ctagYEARExtrap",
            "_ctagYEARInterp",
            "_ctagDYXSb",
            "_ctagDYXSc",
            "_ctagWJetsXSc",
            "_chargeflipYEARstat",
            "_chargeflipYEARsyst",
            "_prefire",
            "_metYEARunclusterE", 
            "_sigYEARscale","_sigYEARpdf","_sigYEARps", #only for signal
            "_jesYEAR",
            "_jerYEAR", 
            "_elemuTriggerYEAR" ,
            "_dimuTriggerYEAR",
            "_dieleTriggerYEAR",
            "_fake",
            "_muonYEARptCorrection",
            "_normTTTo2L","_normSingleTop","_normDY","_normVV","_normVBS","_normttVV","_normttVH","_normttZ","_normttW","_normtZq","_normtttX","_normVVV"]
            #"_normTTTo2L","_normttWW","_normttZZ","_normttWZ","_normttZ","_normttW","_normtZq","_normtttX","_normVVV"]
    if year=='2017' or year=='2018': 
        nuis_Init.append("_lumiCorr1718")


    nuis_Final = dict()
        
    if year=='2016apv' or year=='2016postapv':
        nuis_Init = [nui.replace("_lumiYEAR","_lumi2016") for nui in nuis_Init]
        
    nuis_Final_return = []
    
    corr_nuis_Final =dict()
    corr_nuis_Final_return =[]
    
    Index = 0
    for nui in nuis_Init:
        if nui in blacklist and nui not in whitelist:pass
        else:
            if channel=='ee':
                if 'elemuTriggerYEAR' in nui or 'dimuTriggerYEAR' in nui or 'muIDYEARsys' in nui or 'muIDYEARstat' in nui:continue
                else:pass 
            elif channel =='mm':
                if "dieleTriggerYEAR" in nui or 'elemuTriggerYEAR' in nui or 'eleIDYEARstat' in nui or 'eleIDYEARsys' in nui or "chargeflipYEAR" in nui:continue
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
    
    CheckFile('{}/nuisance_list_{}_{}.json'.format(outputdir,year,channel),True)    
    with open('{}/nuisance_list_{}_{}.json'.format(outputdir,year,channel),'w') as f:
        json.dump(nuis_Final,f,indent=4)
    CheckFile('{}/corrected_nuisance_list_{}_{}.json'.format(outputdir,year,channel),True)    
    with open('{}/corrected_nuisance_list_{}_{}.json'.format(outputdir,year,channel),'w') as f:
        json.dump(corr_nuis_Final,f,indent=4)
        
    return corr_nuis_Final_return
