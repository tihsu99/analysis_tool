'''
Algorithm: 
- get the file name
- get the histograms 
- create a new histogram, bkg_sum 
- use the fine binned histogram for this purpose, however during development, it is not availale, 
- loop over all the bins (from top to bottom). 
- if the event content is <7, sum its content with the neighbour (on left of the histogram), and increase the bin width by 1 unit
- check if the new integral is <7 or not, if <7 add the neighbouring bin on the left and increase the bin width by 1 unit
- keep repeating until the bin content is >=7 and save this bin width. 
- Use this new content and bin width to make the new shape and write it to a new file. 
- use them to get the limits, 
- repeat the whole process with 6, 7, 8, 9, 10 events and see what givess the best limits. 
'''

from ROOT import TH1F, TFile 
import copy
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__))))
#print(sys.path)
import json
from Util.General_Tool import MakeNuisance_Hist,MakePositive_Hist
#processes=["TTTo1L","ttWW", "ttWZ", "ttWtoLNu", "ttZ", "ttZtoQQ", "tttW", "tttt", "tzq", "WWW", "DY", "WWZ", "WWdps", "WZ", "WZZ", "ZZZ", "osWW", "tW", "tbarW", "ttH", "ttWH", "ttWtoQQ", 
#           "ttZH", "tttJ", "zz2l", "TAToTTQ_rtcCOUPLIING_MAMASS"]

import argparse


parser = argparse.ArgumentParser()

parser.add_argument('-y','--year',help='List of Years of data. Default value=["2016postapv"].',default=['2016postapv'],nargs='*')
parser.add_argument('--Couplings',help='List of various couplings you want to consider. The format must be like: 0.4 -> 0p4, 1.0 -> 1p0. Default value=["0p4"]',default=["0p4"],nargs='*')
parser.add_argument('--Masses',help='List of masses point. Default list=[200,300,350,400,500,600,700]',default=[200, 300, 350, 400, 500, 600, 700],nargs='+')
parser.add_argument('-c','--category',help='List of dilepton channels. Default value=["all"]. *In general, you do not need to tune this value',default=["all"],nargs='+')
parser.add_argument('--outputdir',help="Output directory, normally, you do not need to modfiy this value.",default='./FinalInputs')
parser.add_argument('--inputdir',help="Input directory, normally, you don't need to modfiy this value.",default='/eos/cms/store/group/phys_top/ExtraYukawa/BDT/BDT_output')
parser.add_argument('--unblind',action='store_true')

args = parser.parse_args()

if args.year=='2017':
    args.inputdir=args.inputdir+'/{}/ttc_a_rtc{}_MA{}'
else:
    args.inputdir=args.inputdir+'/{}/ttc_a_rtc{}_MA{}'

with open('./data_info/nuisance_list.json'.format(args.year),'r') as f:
    nuisances = json.load(f)

print(nuisances)


variations=["Up", "Down"]

allvariations= [inuis+iv for iv in variations for inuis in nuisances]
allvariations.append("")
#print ("allvariations: ", allvariations)
if 'all' in args.category:
    regions = ["ee","mm","em"]
else:
    regions=args.category
couplings=args.Couplings
masses=args.Masses
years=args.year
inputdir=args.inputdir ## YEAR, coupling, mass needs to be provided
#inputdir="/afs/cern.ch/work/k/khurana/NTU/ttc/CMSSW_10_6_29/src/ttcbar/LimitModel/BDT_output/{}/ttc_a_rtc{}_MA{}" ## YEAR, coupling, mass needs to be provided

outputdir=args.outputdir
#outputdir="/afs/cern.ch/work/k/khurana/NTU/ttc/CMSSW_10_6_29/src/ttcbar/LimitModel/FinalInputs"

filename="TMVApp_{}_{}.root"

##filename_ = filename.format("400","ee")
##print (filename_)


signal_="TAToTTQ_rtcCOUPLIING_MAMASS"

sample_names = dict()

for iyear in years:
    with open('./data_info/process_name_{}.json'.format(iyear),'r') as f:
        sample_names[iyear] = json.load(f)


Process_Categories = sample_names[iyear].keys()

for imass in masses: 
    for ir in regions:
        for iyear in years:
            for ic in couplings:
                filename_ = filename.format(str(imass), ir)
                ic_ = ic.replace("p","")
                inputdir_ = inputdir.format(iyear, ic_, str(imass)) 
                print (" fiilename: ", inputdir_+"/"+filename_)
                # print (inputdir+iyear+"/rtc"+ic.replace("p","")+"/"+filename_)
                print (inputdir_+"/"+filename_)
                rootfiilename=inputdir_+"/"+filename_
                f_in = TFile(rootfiilename,"R")
                
                f_in.cd()
                #f_in.ls()

                prefix="ttc"+iyear+"_"
                
                rebin_=5
                ## create the output file in EOS 
                print (rootfiilename.split("/")[-2], rootfiilename.split("/")[-1])
                os.system("mkdir -p "+outputdir+"/"+iyear+"/"+rootfiilename.split("/")[-2])
                outputfilename=outputdir+"/"+iyear+"/"+rootfiilename.split("/")[-2]+"/"+rootfiilename.split("/")[-1]
                print (outputfilename)
                fout = TFile(outputfilename,"RECREATE")

                
                ## This list needs to be altered for each year, 
                allvariations = [iv.replace("YEAR",iyear) for iv in allvariations]
                #print ("systematic variations: ", allvariations)
                for inuis in allvariations:
                    
                    Hist = dict()

                    
                    for Category in Process_Categories:
                        
                        Category = str(Category)
                        f_in.cd()
                        Hist[Category] = MakeNuisance_Hist(prefix=prefix,samples_list=sample_names[iyear][Category],nuis=inuis,f=f_in,process_category=Category,rebin=rebin_,year=iyear)
                        if Hist[Category] is None:pass
                        else:
                            fout.cd()
                            Hist[Category] = MakePositive_Hist(Hist[Category])
                            Hist[Category].Write()
                         
                    

                    ### data_obs ###
                    ''' 
                    if args.unblind:
                        f_in.cd()
                        if (type(f_in.Get(prefix+"data_obs"+inuis))) is TH1F:
                            h_data_obs = copy.deepcopy(f_in.Get(prefix+"data_obs"+inuis))
                            h_data_obs.Rebin(rebin_);  h_data_obs.SetNameTitle("ttc"+iyear+"_data_obs"+inuis,"ttc"+iyear+"_data_obs"+inuis)
                            fout.cd()
                            h_data_obs.Write()
                    else:pass 
                    '''
                    f_in.cd()
                    if (type(f_in.Get(prefix+"data_obs"+inuis))) is TH1F:
                        h_data_obs = copy.deepcopy(f_in.Get(prefix+"data_obs"+inuis))
                        h_data_obs.Rebin(rebin_);  h_data_obs.SetNameTitle("ttc"+iyear+"_data_obs"+inuis,"ttc"+iyear+"_data_obs"+inuis)
                        fout.cd()
                        h_data_obs.Write()
                    ### Signal Sample ####
                    sig_name_ = prefix+(signal_.replace("MASS",str(imass))).replace("COUPLIING",ic_)
                    f_in.cd()
                    if (type(f_in.Get(str(sig_name_+inuis)))) is TH1F:
                        h_signal_ = copy.deepcopy( f_in.Get(str(sig_name_+inuis))); h_signal_.Rebin(rebin_); h_signal_.SetNameTitle(str(sig_name_+inuis), str(sig_name_+inuis))
                        fout.cd()
                        h_signal_.Write()


                    
                                        
