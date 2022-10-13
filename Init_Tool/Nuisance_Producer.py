import json
from Util.General_Tool import CheckFile

def nui_producer(year,blacklist=[],whitelist=[],outputdir='./data_info',channel='all'):

    nuis_Init=[
            "_lumiYEAR", 
            "_pileup",
            "_muIDYEARsys", 
            "_muIDYEARstat",
            "_eleIDYEARsys",
            "_eleIDYEARstat",
            "_ctagYEARstat",
            "_ctagYEARExtrap",
            "_ctagYEARLHEmuF",
            "_ctagYEARLHEmuR",
            "_ctagYEARInterp",
            "_ctagYEARPSFSR",
            "_ctagYEARPSISR",
            "_ctagYEARPU",
            "_ctagDYXSbUP",
            "_ctagDYXScUP",
            "_ctagWJetsXscUP",
            "_ctagJER",
            "_ctagJES",
            "_chargeflipYEARstat",
            "_chargeflipYEARsyst",
            "_prefire"
            "_metYEARunclusterE", 
            "_sigYEARscale","_sigYEARpdf","_sigYEARps", #only for signal
            #"_prefireYEAR", 
            "_jesYEAR",
            "_jerYEAR", 
            "_elemuTriggerYEAR" ,
            "_dimuTriggerYEAR",
            "_dieleTriggerYEAR",
            "_fake",
            "_normTTTo2L","_normttWW","_normttZZ","_normttWZ","_normttZ","_normttW","_normtZq","_normtttX","_normVVV"]

    nuis_Final = {}
    nuis_Final_return = []
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
            if year=='2018':
                if 'prefireYEAR' in nui:continue
                else:pass

            nuis_Final[Index] = nui
            nuis_Final_return.append(nui)

            Index+=1
    
    CheckFile('{}/nuisance_list_{}_{}.json'.format(outputdir,year,channel),True)    
    with open('{}/nuisance_list_{}_{}.json'.format(outputdir,year,channel),'w') as f:
        json.dump(nuis_Final,f,indent=4)
        
    return nuis_Final_return
