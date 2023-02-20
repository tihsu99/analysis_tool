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
from Util.General_Tool import MakeNuisance_Hist,MakePositive_Hist,CheckDir,CheckFile
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
parser.add_argument('--interference',action='store_true')
parser.add_argument('-q','--quiet',action='store_true')
parser.add_argument('--Coupling_Name',default = 'rtc',choices=['rtc','rtu','rtt'])
args = parser.parse_args()


signal_process_name = 'ttc' #Keep the name rule, instead of ttu/ttt. Suggested by Gouranga.

if not args.interference:
  name_fix = 'ttc_a_{}'.format(args.Coupling_Name)
  args.inputdir=args.inputdir+'/{}/'+name_fix+'{}_MA{}'

if args.interference:
  name_fix = 'ttc_a_{}_s_{}_' + args.Coupling_Name + '{}'
  args.inputdir = args.inputdir + '/{}/'+name_fix


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

if not args.interference:
  signal_="TAToTTQ_{}COUPLIING_MAMASS".format(args.Coupling_Name)
else:
  signal_="TAToTTQ_MAMASS_s_MSMASS_{}COUPLIING".format(args.Coupling_Name)

sample_names = dict()
nuisances = dict()

for iyear in years:
    with open('./data_info/Sample_Names/process_name_{}.json'.format(iyear),'r') as f:
        sample_names[iyear] = json.load(f)
    nuisances[iyear] = dict()
    for ichannel in regions:
        with open('./data_info/NuisanceList/nuisance_list_{}_{}.json'.format(iyear,ichannel),'r') as f:
            Nuisances_dict = json.load(f)
        nuisances[iyear][ichannel] =[]
        for key in Nuisances_dict.keys():
            nuisances[iyear][ichannel].append(str(Nuisances_dict[key]))

##### Correlated Nuisance List -> Manually#####
Correlated_Nuisance_List = ['_sigYEARscale','_sigYEARpdf','_sigYEARps' ,'_jesYEAR']


Process_Categories = sample_names[iyear].keys()

#First remove the output folder for the era to be processed
for iyear in years:
    for ir in regions:
        for imass in masses: 
            for ic in couplings:
                filename_ = filename.format(str(imass), ir)
                ic_ = ic.replace("p","")
                if not args.interference:
                  inputdir_ = inputdir.format(iyear, ic_, str(imass)) 
                else:
                  inputdir_ = inputdir.format(iyear, str(imass), str(int(imass)-50), ic_)
                print (" filename: ", inputdir_+"/"+filename_)
                # print (inputdir+iyear+"/rtc"+ic.replace("p","")+"/"+filename_)
                if not args.interference:
                  rootfiilename=signal_process_name+'_a_'+args.Coupling_Name+ic.replace("p","")+'_MA'+imass+'/'+filename_
                else:
                  rootfiilename=signal_process_name+'_a_'+imass+'_s_'+str(int(imass)-50)+'_'+args.Coupling_Name+ic.replace("p","")+'/'+filename_
                #./FinalInputs/2016apv/ttc_a_rtu04_MA600/TMVApp_600_ee.root
                print("rm -rf " + outputdir+"/"+iyear+'/'+rootfiilename.split("/")[-2])
                #os.system("rm -rf "+outputdir+"/"+iyear+'/'+rootfiilename.split("/")[-2])

for iyear in years:
    Correlated_Nuisance_List_YEAR =[]
    for nui in Correlated_Nuisance_List:
        for U_or_D in ["Up","Down"]:
            correlated_nui = nui+U_or_D
            Correlated_Nuisance_List_YEAR.append(correlated_nui.replace("YEAR",iyear))
            #print(correlated_nui)
    for ir in regions:
        #print(nuisances[iyear][ir])
        variations=["Up", "Down"]
        allvariations= [inuis+iv for iv in variations for inuis in nuisances[iyear][ir]]
        allvariations.append("")
        for imass in masses: 
            for ic in couplings:
                filename_ = filename.format(str(imass), ir)
                ic_ = ic.replace("p","")
                if not args.interference:
                  inputdir_ = inputdir.format(iyear, ic_, str(imass))
                else:
                  inputdir_ = inputdir.format(iyear, str(imass), str(int(imass)-50), ic_)
                print (" fiilename: ", inputdir_+"/"+filename_)
                # print (inputdir+iyear+"/rtc"+ic.replace("p","")+"/"+filename_)
                print (inputdir_+"/"+filename_)
                rootfiilename_IN=inputdir_+"/"+filename_
                f_in = TFile(rootfiilename_IN,"R")
                
                f_in.cd()
                #f_in.ls()
                prefix="ttc"+iyear+"_"
                
                rebin_=5
                if not args.interference:
                  rootfiilename_OUT=signal_process_name+'_a_'+args.Coupling_Name+ic.replace("p","")+'_MA'+imass+'/'+filename_
                else:
                  rootfiilename_OUT=signal_process_name+'_a_'+imass+'_s_'+str(int(imass)-50)+'_'+args.Coupling_Name+ic.replace("p","")+'/'+filename_

                print(rootfiilename_OUT.split("/")[-2])

                print("mkdir -p "+outputdir+"/"+iyear+"/"+rootfiilename_OUT.split("/")[-2])
                CheckDir(outputdir+"/"+iyear+"/"+rootfiilename_OUT.split("/")[-2],True,True)
                outputfilename=outputdir+"/"+iyear+"/"+rootfiilename_OUT
                CheckFile(outputfilename,True)
                
                fout = TFile(outputfilename,"RECREATE")
                print ("Output file is created. -> : {}\n\n".format(outputfilename))

                
                ## This list needs to be altered for each year, 
                allvariations = [iv.replace("YEAR",iyear) for iv in allvariations]
                #print(allvariations)
                #print ("systematic variations: ", allvariations)
                for inuis in allvariations:
                    Hist = dict()
                    
                    ### Correlate Nuisance###
                    correct_nuisance_name=''
                    if inuis in Correlated_Nuisance_List_YEAR:
                        correct_nuisance_name = inuis.replace(iyear,"")
                        #print(iyear,ir,ic,imass,inuis,correct_nuisance_name)
                    else:
                        correct_nuisance_name = inuis
                        #print(iyear,ir,ic,imass,inuis,correct_nuisance_name)
                    #print(correct_nuisance_name) 
                    #########################
                    
                    for Category in Process_Categories:
                        
                        Category = str(Category)
                        f_in.cd()
                        Hist[Category] = MakeNuisance_Hist(prefix=prefix,samples_list=sample_names[iyear][Category],nuis=inuis,f=f_in,process_category=Category,rebin=rebin_,year=iyear,q=args.quiet,correct_nuisance_name=correct_nuisance_name)
                        if Hist[Category] is None:pass
                        else:
                            fout.cd()
                            Hist[Category] = MakePositive_Hist(Hist[Category])
                            Hist[Category].Write()
                         
                    

                    ### data_obs ###
                    if (type(f_in.Get(prefix+"data_obs"+inuis))) is TH1F:
                        h_data_obs = copy.deepcopy(f_in.Get(prefix+"data_obs"+inuis))
                        h_data_obs.Rebin(rebin_);  h_data_obs.SetNameTitle("ttc"+iyear+"_data_obs"+inuis,"ttc"+iyear+"_data_obs"+inuis)
                        fout.cd()
                        h_data_obs.Write()
                    ### Signal Sample ####
                    if not args.interference:
                      sig_name_ = prefix+(signal_.replace("MASS",str(imass))).replace("COUPLIING",ic_)
                    else:
                      sig_name_ = prefix+(signal_.replace("MAMASS",str(imass))).replace("MSMASS",str(int(imass)-50)).replace("COUPLIING",ic_)
                    f_in.cd()
                    if (type(f_in.Get(str(sig_name_+inuis)))) is TH1F:
                        h_signal_ = copy.deepcopy( f_in.Get(str(sig_name_+inuis))); h_signal_.Rebin(rebin_); h_signal_.SetNameTitle(str(sig_name_+correct_nuisance_name), str(sig_name_+correct_nuisance_name))
                        fout.cd()
                        h_signal_.Write()

                    
                                        
