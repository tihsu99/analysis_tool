import json
from Util.General_Tool import CheckFile

def nui_producer(year,blacklist=[],whitelist=[],outputdir='./data_info'):

    nuis_Init=["_lumiYEAR", "_pileup", "_muIDYEARsys", "_muIDYEARstat",
    "_eleIDYEARsys", "_eleIDYEARstat", "_elemuTriggerYEAR", 
    "_ctagYEARstat", "_ctagYEAREleID", "_ctagYEARLHEmuF", 
    "_ctagYEARLHEmuR", "_ctagYEARmuID", "_ctagYEARPSFSR",
    "_ctagYEARPU", "_ctagDYXS", "_ctagSTXS", "_ctagVVXS",
    "_ctagWJetXS", "_ctagTTXS", "_ctagJER", "_ctagJES",
    "_chargeflipYEAR",
    "_metYEARunclusterE", 
    "_sigYEARscale","_sigYEARpdf","_sigYEARps", #only for signal
    #"_prefireYEAR", 
    "_jesYEAR",
    "_jerYEAR", "_elemuTriggerYEAR" ,"_dimuTriggerYEAR","_dieleTriggerYEAR","_fake",
    "_normTTTo2L"#,"_normTTTo1L"
    ,"_normttWW","_normttZZ","_normttWZ","_normttZ","_normttW","_normtZq","_normtttX","_normVVV"]

    nuis_Final = {}
    nuis_Final_return = []
    for idx,nui in enumerate(nuis_Init):
        if nui in blacklist and nui not in whitelist:pass
        else:
            nuis_Final[idx] = nui
            nuis_Final_return.append(nui)
    
    CheckFile('{}/nuisance_list_{}.json'.format(outputdir,year),True)    
    with open('{}/nuisance_list_{}.json'.format(outputdir,year),'w') as f:
        json.dump(nuis_Final,f,indent=4)
        
    return nuis_Final_return
