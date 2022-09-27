import ROOT
from ROOT import TFile,TH1F
import copy
def MakeNuisance_Hist(prefix='',samples_list=[],nuis='',f=TFile,process_category='',rebin=5,year='2017'):
    Init = True
    
    Nui_Exist = False
    h = None
    for sample in samples_list:
        
        sample_nuis_name = str(prefix+sample+nuis)

        if(type(f.Get(sample_nuis_name)) is TH1F):
            if Init:
                h  = copy.deepcopy ( f.Get(sample_nuis_name) )
                Init = False
                Nui_Exist=True
            else:
                h.Add(f.Get(sample_nuis_name))
    if Nui_Exist:
        h.Rebin(rebin)
        h.SetNameTitle("ttc"+year+"_"+process_category+nuis,"ttc"+year+"_"+process_category+nuis)
    else:
        print("Warning: {} doesn't exist".format(sample_nuis_name))
    return h

