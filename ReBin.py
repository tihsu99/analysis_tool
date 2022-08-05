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


#processes=["TTTo1L","ttWW", "ttWZ", "ttWtoLNu", "ttZ", "ttZtoQQ", "tttW", "tttt", "tzq", "WWW", "DY", "WWZ", "WWdps", "WZ", "WZZ", "ZZZ", "osWW", "tW", "tbarW", "ttH", "ttWH", "ttWtoQQ", 
#           "ttZH", "tttJ", "zz2l", "TAToTTQ_rtcCOUPLIING_MAMASS"]

nuisnaces=["_lumiYEAR", "_prefireYEAR", "_fakeYEAR", "_jesYEAR", "_jerYEAR", "_elemuTriggerYEAR", "_muIDYEAR", "_eleIDYEAR", "_dieleTriggerYEAR", "_dimuTriggerYEAR"]

variations=["Up", "Down"]

allvariations= [inuis+iv for iv in variations for inuis in nuisnaces]
allvariations.append("")

print ("allvariations: ", allvariations)
regions=["ee"]#,"mm","em"]
couplings=["0p4"]
masses=[400,200, 300, 350, 400, 500, 600, 700] 
years=["2018"]#"2016", "2016apv", "2017", "2018"]
inputdir="/eos/cms/store/group/phys_top/ExtraYukawa/BDT/BDT_output/{}/ttc_a_rtc{}_MA{}" ## YEAR, coupling, mass needs to be provided

outputdir="/eos/cms/store/group/phys_top/ExtraYukawa/FinalInputs"

filename="TMVApp_{}_{}.root"

##filename_ = filename.format("400","ee")
##print (filename_)


signal_="TAToTTQ_rtcCOUPLIING_MAMASS"

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

                prefix="ttc2018_"
                
                rebin_=5
                ## create the output file in EOS 
                print (rootfiilename.split("/")[-2], rootfiilename.split("/")[-1])
                os.system("mkdir "+outputdir+"/"+iyear+"/"+rootfiilename.split("/")[-2])
                outputfilename=outputdir+"/"+iyear+"/"+rootfiilename.split("/")[-2]+"/"+rootfiilename.split("/")[-1]
                print (outputfilename)
                fout = TFile(outputfilename,"RECREATE")

                
                ## This list needs to be altered for each year, 
                allvariations = [iv.replace("YEAR",iyear) for iv in allvariations]
                print ("systematic variations: ", allvariations)
                for inuis in allvariations:
                    
                    print (prefix+"TTTo1L"+inuis)
                    if (type( f_in.Get(prefix+"TTTo1L"+inuis) ) is TH1F) :
                        h_TTTo1L      = copy.deepcopy ( f_in.Get(prefix+"TTTo1L"+inuis) ) 
                        h_TTTo1L.Rebin(rebin_); h_TTTo1L.SetNameTitle("h_TTTo1L"+inuis,"h_TTTo1L"+inuis)
                        fout.cd()
                        h_TTTo1L.Write()
                        print (prefix+"TTTo1L"+inuis,"hisstogram written")
                            
                    
                    f_in.cd()
                    print (prefix+"ttWtoLNu"+inuis)
                    if type(f_in.Get(prefix+"ttWtoLNu"+inuis)) is TH1F:
                        h_ttWtoLNu    = copy.deepcopy ( f_in.Get(prefix+"ttWtoLNu"+inuis) )
                        h_ttWtoLNu.Rebin(rebin_);  h_ttWtoLNu.SetNameTitle("h_ttWtoLNu"+inuis,"h_ttWtoLNu"+inuis)
                        fout.cd()
                        h_ttWtoLNu.Write()
                        print (prefix+"ttWtoLNu"+inuis, "hisstogram written")
                    
                    f_in.cd()
                    if type(f_in.Get(prefix+"ttWW"+inuis)) is TH1F:
                        h_ttVV        = copy.deepcopy (f_in.Get(prefix+"ttWW"+inuis) )
                        h_ttVV.Add (f_in.Get(prefix+"ttWZ"+inuis) )
                        h_ttVV.Rebin(rebin_);  h_ttVV.SetNameTitle("h_ttVV"+inuis,"h_ttVV"+inuis)
                        fout.cd()
                        h_ttVV.Write()
                        
                    f_in.cd()
                    if type(f_in.Get(prefix+"ttZ"+inuis)) is TH1F:
                        h_ttV      = copy.deepcopy(f_in.Get(prefix+"ttZ"+inuis))
                        h_ttV.Add( f_in.Get(prefix+"ttZtoQQ"+inuis) )
                        h_ttV.Add( f_in.Get(prefix+"ttWtoQQ"+inuis) )
                        h_ttV.Rebin(rebin_);  h_ttV.SetNameTitle("h_ttV"+inuis,"h_ttV"+inuis)
                        fout.cd()
                        h_ttV.Write()
                    
                    f_in.cd()
                    if (type(f_in.Get(prefix+"tttW"+inuis))) is TH1F:
                        h_tttX     = copy.deepcopy ( f_in.Get(prefix+"tttW"+inuis) )
                        h_tttX.Add (  f_in.Get(prefix+"tttt"+inuis) )
                        h_tttX.Rebin(rebin_);  h_tttX.SetNameTitle("h_tttX"+inuis,"h_tttX"+inuis)
                        fout.cd()
                        h_tttX.Write()   
                    
                    f_in.cd()
                    if (type(f_in.Get(prefix+"WWW"+inuis))) is TH1F:
                        h_VVV      = copy.deepcopy ( f_in.Get(prefix+"WWW"+inuis) )
                        h_VVV.Add( f_in.Get(prefix+"WWZ"+inuis))
                        h_VVV.Add( f_in.Get(prefix+"WZZ"+inuis))
                        h_VVV.Rebin(rebin_);  h_VVV.SetNameTitle("h_VVV"+inuis,"h_VVV"+inuis)
                        fout.cd()   
                        h_VVV.Write()
                        
                    
                    f_in.cd()
                    if (type(f_in.Get(prefix+"tW"+inuis))) is TH1F:
                        h_t_tbar_W = copy.deepcopy ( f_in.Get(prefix+"tW"+inuis) )
                        h_t_tbar_W.Add(  f_in.Get(prefix+"tbarW"+inuis) ) 
                        h_t_tbar_W.Rebin(rebin_);  h_t_tbar_W.SetNameTitle("h_t_tbar_W"+inuis,"h_t_tbar_W"+inuis)
                        fout.cd()
                        h_t_tbar_W.Write()
                        
                    f_in.cd()
                    if (type(f_in.Get(prefix+"ttH"+inuis))) is TH1F:
                        h_tt_V_H   = copy.deepcopy ( f_in.Get(prefix+"ttH"+inuis) )
                        h_tt_V_H.Add ( f_in.Get(prefix+"ttWH"+inuis))
                        h_tt_V_H.Add ( f_in.Get(prefix+"ttZH"+inuis))
                        h_tt_V_H.Rebin(rebin_);  h_tt_V_H.SetNameTitle("h_tt_V_H"+inuis,"h_tt_V_H"+inuis)
                        fout.cd()
                        h_tt_V_H.Write()
                    
                    f_in.cd()
                    if (type(f_in.Get(prefix+"DY"+inuis))) is TH1F:
                        h_DY       = copy.deepcopy (f_in.Get(prefix+"DY"+inuis))
                        h_DY.Rebin(rebin_);  h_DY.SetNameTitle("h_DY"+inuis,"h_DY"+inuis)
                        fout.cd()
                        h_DY.Write()
                    
                    f_in.cd()
                    if (type(f_in.Get(prefix+"tzq"+inuis))) is TH1F:
                        h_tzq      = copy.deepcopy ( f_in.Get(prefix+"tzq"+inuis)) 
                        h_tzq.Rebin(rebin_);  h_tzq.SetNameTitle("h_tzq"+inuis,"h_tzq"+inuis)
                        fout.cd()
                        h_tzq.Write()
                        
                    f_in.cd()
                    if (type(f_in.Get(prefix+"WWdps"+inuis))) is TH1F:
                        h_VV       = copy.deepcopy (f_in.Get(prefix+"WWdps"+inuis))
                        h_VV.Add( f_in.Get(prefix+"WZ"+inuis))
                        h_VV.Add( f_in.Get(prefix+"osWW"+inuis))
                        h_VV.Rebin(rebin_);  h_VV.SetNameTitle("h_VV"+inuis,"h_VV"+inuis)
                        fout.cd()
                        h_VV.Write
                        
                    
                    sig_name_ = prefix+(signal_.replace("MASS","400")).replace("COUPLIING","01")
                    f_in.cd()
                    if (type(f_in.Get(sig_name_+inuis))) is TH1F:
                        h_signal_ = copy.deepcopy( f_in.Get(sig_name_+inuis)); h_signal_.Rebin(rebin_); h_signal_.SetNameTitle(sig_name_+inuis, sig_name_+inuis)
                        fout.cd()
                        h_signal_.Write()


                    
                                        

