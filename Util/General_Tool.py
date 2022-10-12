import ROOT
from ROOT import TFile,TH1F
import copy
import os 
import sys
CURRENT_WORKDIR = os.getcwd()
def MakeNuisance_Hist(prefix='',samples_list=[],nuis='',f=TFile,process_category='',rebin=5,year='2017',q=False):
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
        if q:pass
        else:print("Warning: {} doesn't exist".format(sample_nuis_name))
    return h

def MakePositive_Hist(Hist,value=0.0001):

    H = copy.deepcopy(Hist) 

    for ibin in range(Hist.GetNbinsX()):
        if Hist.GetBinContent(ibin+1) < 0:
            H.SetBinContent(ibin+1,value) #this is up to user
        else:pass
    return H
def CheckDir(Dir_to_check="",MakeDir=True):
    '''
    Just check whether a folder is existed or not. If it is not, then create a new one.
    '''
    
    if os.path.isdir(Dir_to_check): return True
    else:
        print("Warning: You don't have directory: `{}` under {}\n".format(Dir_to_check, CURRENT_WORKDIR))
        if MakeDir:
            os.system('mkdir -p {}'.format(os.path.join(CURRENT_WORKDIR,Dir_to_check)))
            print("Warning: Dir-> ./{} is made now.\n".format(Dir_to_check))
        else:pass
        print("")
        return False

def CheckFile(File_to_check='',RemoveFile=False):

    '''
    Just check if file is existed or not. Here the function provides a further option
    to let users decide whether this existed file should be deleted or not.
    '''
    
    if os.path.isfile(File_to_check): 
        print('Warning: File-> {} exists'.format(File_to_check))
        if RemoveFile:
            print('Warning: Remove File-> {}\n'.format(File_to_check))
            os.system('rm -f {}'.format(File_to_check))
        return True
    else:

        print('Warning: File-> {} does not exist\n'.format(File_to_check))

        return False










