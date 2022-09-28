import json

def nui_producer(year,blacklist=[],whitelist=[]):

    nuis_Init=["_lumiYEAR", "_pileup", "_muIDYEARsys", "_muIDYEARstat",
    "_eleIDYEARsys", "_eleIDYEARstat", "_elemuTriggerYEAR", 
    "_ctagYEARstat", "_ctagYEAREleID", "_ctagYEARLHEmuF", 
    "_ctagYEARLHEmuR", "_ctagYEARmuID", "_ctagYEARPSFSR", 
    "_ctagYEARPU", "_ctagDYXS", "_ctagSTXS", "_ctagVVXS",
    "_ctagWJetXS", "_ctagTTXS", "_ctagJER", "_ctagJES",
    "_chargeflipYEAR",
    "_sigYEARpdf",  ## only signal 
    "_metYEARunclusterE", 
    "_prefireYEAR", "_jesYEAR",
    "_jerYEAR", "_elemuTriggerYEAR" ,"_dimuTriggerYEAR","_dieleTriggerYEAR","fakeYEAR"]

    nuis_Final = []
    for nui in nuis_Init:
        if nui in blacklist:pass
        else:nuis_Final.append(nui)
    
    with open('./data_info/nuisance_list.json','w') as f:
        json.dump(nuis_Final,f,indent=4)
        

