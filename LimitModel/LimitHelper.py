import os
import  sys
CURRENT_WORKDIR = os.getcwd()
sys.path.append(CURRENT_WORKDIR)
from array import  array
from ROOT import TGraph, TFile, TGraphAsymmErrors
import ROOT as rt
import argparse
import csv
import pandas as pd
from Util.General_Tool import CheckDir,CheckFile
from collections import OrderedDict
import numpy as np
sys.path.insert(0, '../python')
from common import read_json
from scipy.interpolate import griddata
from scipy.interpolate import LinearNDInterpolator
from scipy.optimize import root

class RunLimits:
    ''' class to perform all tasks related to the limits once datacards are prepared '''
    ''' this class exepcts that all the steps needed to prepare the datacards and prepration of its inputs are already performed '''
    ''' instantiation of the class is done here ''' 
    def __init__(self, year, analysis="bH", region="SR", channel="em", postfix="asimov", model="extYukawa",unblind=False, verbose=False, rMax=5, signal_param=OrderedDict(), outputdir = "./", all_signal = []):
        self.year_                 = year
        self.analysis_             = analysis
        self.region_               = region
        self.channel_              = channel
        self.postfix_              = postfix
        self.model_                = model
        self.rMax_                 = rMax
        self.signal_param_         = signal_param
        self.outputdir_            = outputdir
        self.limit_dir             = os.path.join(self.outputdir_, "bin", self.year_, self.region_, self.channel_)
        if CheckDir(self.limit_dir,MakeDir=True):pass
        else:pass

        param_string = []
        for key in self.signal_param_:
          param_string.append(str(key) + str(self.signal_param_[key]))
        param_string = '_'.join(param_string)
        self.signal_str_ = param_string
        self.limitlog = os.path.join(self.limit_dir,"limits_" + self.analysis_ + "_" + param_string + "_"+self.postfix_+"_"+self.model_+".txt")
        self.limit_pdf_file    = "limits_" + self.analysis_ + "_"+ param_string + "_" + self.postfix_+"_"+self.model_ + "_" + self.region_ + "_" + self.channel_ + ".pdf"
        self.limit_root_file   = self.limitlog.replace(".txt",".root")
        self.limitlog_tmp_node = self.limitlog.replace(".txt","_{}.txt")

        self.all_signal_limit_root_file = []
        self.all_signal_limitlog_tmp_node = []
        self.all_signal_limitlog = []
        for signal_ in all_signal:
            limitlog = os.path.join(self.limit_dir, "limits_" + self.analysis_ + "_" + signal_ + "_" + self.postfix_ + "_" + self.model_ + ".txt")           
            self.all_signal_limitlog.append(limitlog)
            self.all_signal_limit_root_file.append(limitlog.replace('.txt', '.root'))
            self.all_signal_limitlog_tmp_node.append(limitlog.replace('.txt', '_{}.txt'))


        self.__unblind = unblind
        self.__verbose = verbose
        #self.runmode = runmode
        print("class instantiation done")


    ''' convert a text file with just one columns into a list '''
    def TextFileToList(self, textfile):
        return [iline.rstrip() for iline in open (textfile)]

    def PrintSpacing(self, nLine=1):
        for iline in range(nLine):
            print("***************************************************************************************************************************************")

    def TimeFormat(self):
        from datetime import datetime
        now = datetime.now()
        date_str = ((str(now)).replace("-","_")).split(":")
        date_format = (date_str[0]).replace(" ","_") + "_" + str(date_str[1])
        return date_format


    def setupDirs(self, txtfile):
        for idir in open(txtfile):
            os.system('mkdir -p '+idir.rstrip())
            os.system('cp index.php '+idir.rstrip())
        return 0

    def datacard_to_mparameters(self, name_):
        analysis_ = self.analysis_
        print ("LimitHelper.py::datacard_to_mparameters: ",analysis_, self.model_, name_)

        if ("Yukawa" in self.model_) and (analysis_ == "ttc"):
            mparameters = name_.split()

        if ("2hdma" in self.model_) and (analysis_ == self.analysis_):
            mparameters_ = ((name_.split("Merged_")[1]).replace(".log","")).split("_")
            mparameters_ = [mp.replace("p",".") for mp in mparameters_]
            ## ma, mA, tb, st, mdm
            return ([mparameters_[9], mparameters_[7], mparameters_[3], mparameters_[1], mparameters_[5]])

        if ("dmsimp" in self.model_) and (analysis_ == self.analysis_):
            ## this needs to be changed
            mparameters_ = ((name_.split("Merged_")[1]).replace(".log","")).split("_")
            #mparameters_ = [mp.replace("p",".") for mp in mparameters_]
            ## mPhi, mChi
            return ([mparameters_[1], mparameters_[3] ])


    def getLimits(self, dc, asimov=True, mass_point='MA200', cminDefaultMinimizerStrategy=0, rAbsAcc=0.001, cminDefaultMinimizerTolerance=1.0, dc_dir=None, log_dir=None, logname = None, extraCommand=''):
        asimovstr =""
        if logname is None:
          logname = dc.replace(".txt",".log")
          logname = logname.replace(dc_dir, log_dir)
        else:
          logname = logname.replace(dc_dir, log_dir)
        CheckDir('/'.join(logname.split('/')[:-1]), True)
        print ("logname: ",logname)

        if self.__unblind:
            command_ = "combine -M AsymptoticLimits " + dc + " -n " + self.year_ + "_" + self.region_ + "_" + self.channel_ + "_" + mass_point + "_" + self.signal_str_+"_"+self.postfix_+"_"+self.model_+' --cminDefaultMinimizerStrategy ' + str(cminDefaultMinimizerStrategy) + ' --rAbsAcc '+ str(rAbsAcc) + ' --X-rtd FITTER_NEW_CROSSING_ALGO --X-rtd FITTER_NEVER_GIVE_UP --X-rtd FITTER_BOUND --cminDefaultMinimizerTolerance=' + str(cminDefaultMinimizerTolerance) + ' --rMax ' + str(self.rMax_) + ' ' + extraCommand + ' '
        else:
            command_ = "combine -M AsymptoticLimits " + dc + " -n " + self.year_ + "_" + self.region_ + "_" + self.channel_ + "_" + mass_point+"_"+ self.signal_str_ + "_" + self.postfix_ + "_" + self.model_ + ' --run blind --cminDefaultMinimizerStrategy ' + str(cminDefaultMinimizerStrategy) + ' --rAbsAcc '+ str(rAbsAcc) + ' --X-rtd FITTER_NEW_CROSSING_ALGO --X-rtd FITTER_NEVER_GIVE_UP --X-rtd FITTER_BOUND --cminDefaultMinimizerTolerance=' + str(cminDefaultMinimizerTolerance) + ' --rMax ' + str(self.rMax_)  + ' ' + extraCommand + ' ' #TODO check -t -1 is correct
        if asimov:
            command_ = command_ + asimovstr
        if self.__verbose:
            command_ = command_ + '-v 3'

        os.system(command_+" >& "+logname)
        output_rootfile = "higgsCombine"+self.year_+"_"+self.region_+"_" + self.channel_ + "_"+mass_point+"_" + self.signal_str_ + "_" + self.postfix_+"_"+self.model_+".AsymptoticLimits.mH120.root"
        print(command_+" >& "+logname)

        # delete the output combine root file (not to make dirty your home area!)
        os.system("rm "+output_rootfile)
        return logname

    ## category can be merged/resolved/combined
    def LogToLimitList(self, logfile, allparameters, mode="a", postfix = '', POI = 'r'):
        expected25_=""
        expected16_=""
        expected50_=""
        expected84_=""
        expected975_=""
        observed_=""
        for ilongline in open(logfile):
            if "Observed Limit: {} < ".format(POI) in ilongline:
                observed_ = ilongline.replace("Observed Limit: {} < ".format(POI),"").rstrip()
            if "Expected  2.5%: {} < ".format(POI) in ilongline:
                expected25_ = ilongline.replace("Expected  2.5%: {} < ".format(POI),"").rstrip()
            if "Expected 16.0%: {} < ".format(POI) in ilongline:
                expected16_ = ilongline.replace("Expected 16.0%: {} < ".format(POI),"").rstrip()
            if "Expected 50.0%: {} < ".format(POI) in ilongline:
                expected50_ = ilongline.replace("Expected 50.0%: {} < ".format(POI),"").rstrip()
            if "Expected 84.0%: {} < ".format(POI) in ilongline:
                expected84_ = ilongline.replace("Expected 84.0%: {} < ".format(POI),"").rstrip()
            if "Expected 97.5%: {} < ".format(POI) in ilongline:
                expected975_ = ilongline.replace("Expected 97.5%: {} < ".format(POI),"").rstrip()

        print("allparameters:", allparameters)
        towrite =  str(allparameters[2])+" "+str(allparameters[1])+" "+expected25_+" "+expected16_+" "+ expected50_+" "+ expected84_+" "+ expected975_+" "+ observed_+"\n"

        print(towrite)
        #os.system ("mkdir -p bin/"+self.postfix_)
        #os.system ("mkdir -p plots_limit/"+self.postfix_)
        limitlog_tmp_node = self.limitlog.replace('.txt','{}.txt'.format(postfix + "_{}"))
        outfile=limitlog_tmp_node.format(allparameters[0]+allparameters[1])



        fout = open(outfile,mode)
        fout.write(towrite)
        fout.close()
        return outfile



    def TextFileToRootGraphs(self,med_idx=0,Masses=[],Higgs="MA"):
        #limit_root_file = filename.replace(".txt",".root")


        input_limitlog_tmp_list = [self.limitlog_tmp_node] if (len(self.all_signal_limitlog_tmp_node) == 0) else self.all_signal_limitlog_tmp_node
        limit_log_list = [self.limitlog] if (len(self.all_signal_limitlog_tmp_node) == 0) else  self.all_signal_limitlog
        limit_log_root_list = [self.limit_root_file] if (len(self.all_signal_limitlog_tmp_node) == 0) else self.all_signal_limit_root_file

        for file_idx, limitlog_tmp_ in enumerate(input_limitlog_tmp_list):
            med=array('f')
            #mchi=array('c')
            expm2=array('f')
            expm1=array('f')
            expmed=array('f')
            expp1=array('f')
            expp2=array('f')
            obs=array('f')
            errx=array('f')

            counter = 0
            Merged_txt_file = open(limit_log_list[file_idx],'w')
         
        
            for imass in Masses:
                input_file = input_limitlog_tmp_list[file_idx].format(Higgs+str(imass))
                if CheckFile(input_file):pass
                else:
                    raise ValueError('Make sure you have this file: {}'.format(input_file))
            
                f = open(input_file,"r")
                for line in f:
                    if len(line.rsplit())<7: continue
                    med.append(float(line.rstrip().split()[1]))
                    #mchi.append(chr(line.rstrip().split()[0]))                
                    expm2.append(float(line.rstrip().split()[4]) - float(line.rstrip().split()[2]) )
                    expm1.append(float(line.rstrip().split()[4]) - float(line.rstrip().split()[3]) )
                    expmed.append(float(line.rstrip().split()[4]))
                    expp1.append(float(line.rstrip().split()[5]) - float(line.rstrip().split()[4]) )
                    expp2.append(float(line.rstrip().split()[6]) - float(line.rstrip().split()[4]) )

                    if self.__unblind:
                        obs.append(float(line.rstrip().split()[7]))
                    errx.append(0.0)
                    print('imass: {}->{} GeV'.format(Higgs,imass))
                    print ('expm2: ', expm2[counter])
                    print ('expm1: ', expm1[counter])
                    print ('expmed: ', expmed[counter])
                    print ('expp1: ', expp1[counter])
                    print ('expp2: ', expp2[counter])
                    print('')
                    Merged_txt_file.write(line)
                    counter +=1
            Merged_txt_file.close()
            print('-----------------------------------------------------------------------------------------------------------')
            print("Merged Information for Limit is written into {} .".format(limit_log_list[file_idx]))
            g_exp2  = TGraphAsymmErrors(int(len(med)), med, expmed, errx, errx, expm2, expp2 )   ;  g_exp2.SetName("exp2")
            g_exp1  = TGraphAsymmErrors(int(len(med)), med, expmed, errx, errx, expm1, expp1 )   ;  g_exp1.SetName("exp1")
            g_expmed = TGraphAsymmErrors(int(len(med)), med, expmed)   ;  g_expmed.SetName("expmed")
        
            if self.__unblind:
                g_obs    = TGraphAsymmErrors(int(len(med)), med, obs   )   ;  g_obs.SetName("obs")
    
            f1 = TFile(limit_log_root_list[file_idx],'RECREATE')
            g_exp2.Write()
            g_exp1.Write()
            g_expmed.Write()
            if self.__unblind:
                g_obs.Write()
            f1.Write()
            f1.Close()
        return self.limit_root_file

    def SaveLimitPdf1D(self,outputdir='./',y_max=1000,y_min=0.1, signal_xsec_TGraph=None, coupling_varied = None):
        rootfile = self.limit_root_file
        setlogX=0
        y_max=y_max # scale of y axis
        y_min=y_min # scale of y axis


        rt.gStyle.SetOptTitle(0)
        rt.gStyle.SetOptStat(0)
        rt.gROOT.SetBatch(1)
        c = rt.TCanvas("c","c",620, 600)
        c.SetGrid(0,0)
        c.SetLogy(1)
        c.SetLogx(setlogX)
        c.SetLeftMargin(0.15)
        #leg = rt.TLegend(.15, .65, .35, .890);
        f = rt.TFile(rootfile,"read")
        exp2s =  f.Get("exp2")
        exp2s.SetMarkerStyle(20)
        exp2s.SetMarkerSize(1.1)
        exp2s.SetLineWidth(2)
        exp2s.SetFillColor(rt.kOrange);
        exp2s.SetLineColor(rt.kOrange)
        exp2s.GetXaxis().SetTitle("m_{H^{\pm}} (GeV)");
        exp2s.GetYaxis().SetRangeUser(y_min,y_max)
        exp2s.GetXaxis().SetTitleOffset(1.1)
        if signal_xsec_TGraph is None:
          exp2s.GetYaxis().SetTitle("95% C.L. limit on #mu=#sigma/#sigma_{theory}");
        #exp2s.GetYaxis().SetTitle("95% C.L. #mu=#sigma/#sigma_{theory}");
        else:
          exp2s.GetYaxis().SetTitle("95% C.L. limit on #sigma(pp#rightarrow XH^{#pm}) #it{B}(H^{#pm}#rightarrow tb)[pb]")
        exp2s.GetYaxis().SetTitleOffset(1.6)
        exp2s.GetYaxis().SetNdivisions(20,5,0);
        #exp2s.GetXaxis().SetNdivisions(505);
        #exp2s.GetYaxis().SetMoreLogLabels()
        #exp2s.GetXaxis().SetMoreLogLabels()
        #exp2s.GetXaxis().SetRangeUser(10,750)
        exp2s.Draw("A 3")

        exp1s =  f.Get("exp1")
        exp1s.SetMarkerStyle(20)
        exp1s.SetMarkerSize(1.1)
        exp1s.SetLineWidth(2)
        exp1s.SetFillColor(rt.kGreen + 2);
        exp1s.SetLineColor(rt.kGreen + 2)
        exp1s.Draw("3 same")

        exp =  f.Get("expmed")
        exp.SetMarkerStyle(1)
        exp.SetMarkerSize(1.1)
        exp.SetLineStyle(2)
        exp.SetLineWidth(3)
        exp.Draw("L same")
        if self.__unblind:
            print ("***Unblinding BOX***")
            obs =  f.Get("obs")
            obs.SetMarkerStyle(20)
            obs.SetMarkerColor(1)
            obs.SetMarkerSize(1.1)
            obs.SetLineColor(1)
            obs.SetLineWidth(3)
            obs.Draw("LP same")

        leg = rt.TLegend(.52, .55, .80, .890);
        leg.SetBorderSize(0);
        leg.SetFillColor(0);
        leg.SetShadowColor(0);
        leg.SetTextFont(42);
        leg.SetTextSize(0.03);

        leg.Draw("same")
        c.Update()


        for limit_root_file_ in self.all_signal_limit_root_file:
            if (limit_root_file_ == rootfile): continue
            print(limit_root_file_)
            f_signal_limit = rt.TFile(limit_root_file_, "read")
            exp = f_signal_limit.Get("expmed")
            exp.SetMarkerStyle(5)
            exp.SetMarkerSize(1.1)
            exp.SetLineWidth(0)
            exp.SetLineStyle(0)
            exp.Draw("P same")
            c.Update()
            f_signal_limit.Close()


        #print (c.GetUxmin(),c.GetUxmax())
        if signal_xsec_TGraph is None:
          line = rt.TLine(c.GetUxmin(),1.0,c.GetUxmax(),1.0);
          line.SetLineColor(rt.kRed)
          line.SetLineWidth(2)
          line.Draw('same ')

        if signal_xsec_TGraph is None:
          pass
        else:
          color_idx = 0
          colors = [
            rt.TColor.GetColor(235, 52, 128),      # Bright Green
            rt.TColor.GetColor(162, 52, 235),      # Bright Blue
            rt.TColor.GetColor(255, 0, 0),    # Gold
            rt.TColor.GetColor(235, 162, 52),     # Indigo
          ]
          style_idx = 3
          for stuff_ in signal_xsec_TGraph:

            if stuff_ == 'color': continue
            signal_xsec_TGraph[stuff_].SetLineColor(2)
            signal_xsec_TGraph[stuff_].SetLineStyle(style_idx)
            signal_xsec_TGraph[stuff_].SetFillColorAlpha(2, 0.2)
            # signal_xsec_TGraph[stuff_].SetFillColorAlpha(signal_xsec_TGraph['color'][stuff_], 0.5)
            signal_xsec_TGraph[stuff_].SetLineWidth(3)
            signal_xsec_TGraph[stuff_].Draw('3 L same')
            leg.AddEntry(signal_xsec_TGraph[stuff_], "{}".format(stuff_), "L")
            color_idx += 1
            style_idx += 1

        leg.AddEntry(exp, "Median expected ", "LP");
        leg.AddEntry(exp1s, "68% expected", "LF");
        leg.AddEntry(exp2s, "95% expected", "LF");
        if self.__unblind:
            leg.AddEntry(obs, "Observed", "LP");
        latex =  rt.TLatex();
        latex.SetNDC();
        latex.SetTextFont(42);
        latex.SetTextSize(0.03);
        latex.SetTextAlign(31);
        latex.SetTextAlign(12);
        model_ = '2HDM+a'

        import CMS_lumi
        CMS_lumi.writeExtraText = 1
        CMS_lumi.extraText = "Preliminary"
        CMS_lumi.cmsTextSize = 0.55
        CMS_lumi.relPosX    = 0.15
        CMS_lumi.relPosY    = 0.05
        CMS_lumi.lumi_sqrtS = "13 TeV" # used with iPeriod = 0, e.g. for simulation-only plots (default is an empty string)
        iPos = 0
        # if( iPos==0 ): CMS_lumi.relPosX = 0.5
        iPeriod=self.year_

        param_string = ''
        for param_ in self.signal_param_:
          if type(self.signal_param_[param_]) == str:
            value = self.signal_param_[param_].replace("p",".")
          param_string += "{}={} ".format(param_, value)
        CMS_lumi.CMS_lumi(c, iPeriod, iPos, 0.1, 0.092)
#        latex.DrawLatex(0.20, 0.76, '{} {} {}'.format('g2HDM', self.region_, self.channel_));
        latex.DrawLatex(0.20, 0.8, "g2HDM")
        if signal_xsec_TGraph is None:
          latex.DrawLatex(0.20, 0.64, str(param_string)); #sin#theta = 0.7, m_{\chi} = 1 GeV");


        OUT_DIR = os.path.join(outputdir,"plots_limit", self.year_)

        #if not os.path.isdir(OUT_DIR):os.system("mkdir -p {OUT_DIR}")

        #self.limit_pdf_file  = rootfile.replace(".root","_"+self.model_+".pdf").replace("bin","plot_limit")
        #c.SetLogx(1)
        c.Update()
        #c.SaveAs(name+".png")

        CheckDir(OUT_DIR,True)
        self.limit_pdf_file  = os.path.join(OUT_DIR,self.limit_pdf_file)

        if signal_xsec_TGraph is not None and coupling_varied is not None:
          self.limit_pdf_file = self.limit_pdf_file.replace(".pdf", "_{}_varied.pdf".format(coupling_varied))

        CheckFile(self.limit_pdf_file,True)

        c.SaveAs(self.limit_pdf_file)
        self.limit_png_file = self.limit_pdf_file.replace(".pdf",".png")

        CheckFile(self.limit_png_file,True)
        c.SaveAs(self.limit_png_file)

        c.SaveAs(self.limit_png_file.replace(".png", ".C"))
        c.Close()

        return "pdf file is saved"



    def getlimitScaled_1D(self, coupling_value=0.1, divisionfactor=10000000000):
        limit_file_in  = self.limitlog
        limit_file_out = self.limitlog_scaled

        df = pd.read_fwf("ttc_cross_sections.txt")

        print('xs_before\n{}'.format(df))

        if self.Coupling == 'rtc':
            xs = df[(df.rhotu==0) & (df.rhott==0) & (df.PID=="a0")]
        elif self.Coupling =='rtu':
            xs = df[(df.rhotc==0) & (df.rhott==0) & (df.PID=="a0")]
        else:
            xs = df[(df.rhotu==0) & (df.rhotc==0) & (df.PID=="a0")]

        print('xs_after\n'.format(xs))


        xs.drop(axis=1,labels=["PID","Err_cross_section"], inplace=True)
        Drop_index = []
        if self.Coupling =='rtc':
            index_name = 'rhotc'
            Drop_index.append('rhotu')
            Drop_index.append('rhott')
        elif self.Coupling =='rtu':
            index_name = 'rhotu'
            Drop_index.append('rhotc')
            Drop_index.append('rhott')
        elif self.Coupling =='rtt':
            index_name = 'rhott'
            Drop_index.append('rhotu')
            Drop_index.append('rhotc')
        else:raise ValueError("We haven't set this coupling :{}".format(self.Coupling))
        limits = pd.read_csv(limit_file_in, delimiter=" ", names=[index_name,"Mass","expm2", "expm1", "exp", "expp1", "expp2", "obs"])
        #limits[self.Coupling] = 0.4 ## this is dummy value
        print(limits)
        #print(limits['rhotc'])
        if self.Coupling =='rtc':
            xs_skim_ = xs[xs.rhotc==coupling_value]
            limits.rhotc = limits.rhotc * 0.1
        elif self.Coupling =='rtu':
            limits.rhotu = limits.rhotu * 0.1
            xs_skim_ = xs[xs.rhotu==coupling_value]
        elif self.Coupling =='rtt':
            limits.rhott = limits.rhott * 0.1
            xs_skim_ = xs[xs.rhott==coupling_value]
        else:raise ValueError('')
        xs_Mass_  = xs_skim_.set_index([index_name,"Mass"])
        print('xs_Mass_\n{}'.format(xs_Mass_))
        limits=limits.set_index([index_name,"Mass"])
        print('limits\n{}'.format(limits))
        limits_merged = limits.merge(xs_Mass_, left_index=True, right_index=True, how='outer')
        print('limits_merged\n{}'.format(limits_merged))

        limits_merged.drop(axis=1,
                           labels=[Drop_index[0],Drop_index[1],"cross_section"],
                           inplace=True)

        limits_scaled = limits_merged
        print(limits_scaled)

        limits_scaled.reset_index(inplace=True)
        print(limits_scaled)

        limits_scaled.dropna(axis=0,
                             inplace=True)
        print(limits_scaled)

        p0 = limits_scaled.to_string(justify='right',
                                     index=False,
                                     header=False)


        fout = open(limit_file_out,"w")
        fout.write(p0)
        fout.close()

        print (limits_scaled)
        return limits_scaled




    def RunImpacts(self, datacard, logfilename, runmode="data"):
        workspace=datacard.replace(".txt",".root")


        if runmode=="data":
            ''' First we perform an initial fit for the signal strength and its uncertainty'''
            os.system("combineTool.py -M Impacts -d "+workspace+" -m 200 --rMin -1 --rMax 2 --robustFit 1 --doInitialFit  -t -1 ")
            '''Then we run the impacts for all the nuisance parameters'''
            os.system("combineTool.py -M Impacts -d "+workspace+" -m 200 --rMin -1 --rMax 2 --robustFit 1 --doFits  -t -1 ")
            '''we collect all the output and convert it to a json file'''
            os.system("combineTool.py -M Impacts -d "+workspace+" -m 200 --rMin -1 --rMax 2 --robustFit 1 --output impacts.json")
            '''then make a plot showing the pulls and parameter impacts, sorted by the largest impact'''
            os.system("plotImpacts.py -i impacts.json -o impacts")


        ## run impact  asimov
        print("do nothing for now")
        ## run impact  data


    def SavePrePostComparison(self,run_mode, outdir, category, year):
        default_fit_root   = "fitDiagnostics.root"
        default_pull_root  = "pulls.root"

        ''' prepare the names of root file '''
        fit_Diagnostics = default_fit_root.replace(".root", "_"+category+"_"+year+"_"+run_mode+".root")
        pull_root       = default_pull_root.replace(".root",  "_"+category+"_"+year+"_"+run_mode+".root")

        print("run_mode, fit_Diagnostics, pull_root", run_mode, fit_Diagnostics, pull_root)
        ''' move the rootfile to avoid ambiguity '''

        postfix_ = "_"+category+"_"+year+"_"


        if run_mode == "cronly":
            self.PrintSpacing()
            dir_ = outdir["pulls"]
            os.system("mv "+default_fit_root+" " + fit_Diagnostics)
            os.system('root -l -b -q plotPostNuisance_combine.C\(\\"'+fit_Diagnostics+'\\",\\"'+dir_+'\\",\\"'+postfix_+'\\"\)')

            print("python PlotPreFitPostFit.py "+fit_Diagnostics+" "+dir_+" "+postfix_)
            os.system("python PlotPreFitPostFit.py "+fit_Diagnostics+" "+dir_+" "+postfix_)

        if run_mode != "cronly":
            os.system("mv "+default_fit_root+" " + fit_Diagnostics)
            ''' get the different of nuisances '''
            self.PrintSpacing()
            print("python diffNuisances.py "+fit_Diagnostics+" --abs --all -g "+pull_root)
            os.system("python diffNuisances.py "+fit_Diagnostics+" --abs --all -g "+pull_root)
            os.system("mv "+default_pull_root+" " + pull_root)
            self.PrintSpacing()
            dir_ = outdir["pulls"]

            print('root -l -b -q PlotPulls.C\(\\"'+pull_root+'\\",\\"'+dir_+'\\",\\"'+postfix_+'\\"\)')
            os.system('root -l -b -q PlotPulls.C\(\\"'+pull_root+'\\",\\"'+dir_+'\\",\\"'+postfix_+'\\"\)')
            dir_ = outdir["yr"]
            self.PrintSpacing()
            print("python yieldratio.py "+fit_Diagnostics+" "+dir_+" "+postfix_)
            os.system("python yieldratio.py "+fit_Diagnostics+" "+dir_+" "+postfix_)
            dir_ = outdir["pfitOverlay"]
            self.PrintSpacing()

            print("python PlotPreFitPostFit.py "+fit_Diagnostics+" "+dir_+" "+postfix_)
            os.system("python PlotPreFitPostFit.py "+fit_Diagnostics+" "+dir_+" "+postfix_)

            dir_ = outdir["stack"]
            print("call the stack file")
            dir_ = outdir["tf"]
            print("call the TF file")







    def RunPulls(self, datacard, run_mode, outdir, category, year):
        ## setup the dir structure
        #self.setupDirs("configs/pulls_dir.txt")
        ## data fit
        if run_mode == "data":
            self.PrintSpacing(2)
            print("performing the fit in run_mode ",run_mode)
            print("combine -M FitDiagnostics --saveShapes "+datacard+ " --saveWithUncertainties --saveNormalizations --X-rtd MINIMIZER_analytic ")
            os.system("combine -M FitDiagnostics --saveShapes "+datacard+ " --saveWithUncertainties --saveNormalizations --X-rtd MINIMIZER_analytic ")
            self.PrintSpacing(1)
            self.SavePrePostComparison("data",outdir,category, year)



        ## asimov fit
        if run_mode == "asimov":
            self.PrintSpacing(2)
            print("combine -M FitDiagnostics --saveShapes "+datacard + " --saveWithUncertainties --saveNormalizations --X-rtd MINIMIZER_analytic  --rMin -100 -t -1 --expectSignal 0")
            os.system("combine -M FitDiagnostics --saveShapes "+datacard + " --saveWithUncertainties --saveNormalizations --X-rtd MINIMIZER_analytic  --rMin -100 -t -1 --expectSignal 0")
            self.PrintSpacing(1)
            self.SavePrePostComparison("asimov",outdir,category,year)

        ## CR only fit
        if run_mode == "cronly":
            print("text2workspace.py "+datacard+" --channel-masks")
            os.system("text2workspace.py "+datacard+" --channel-masks")
            wsname = datacard.replace(".txt",".root")

            print("combine -M FitDiagnostics  "+wsname+" --saveShapes --saveWithUncertainties --setParameters mask_SR=1,mask_cat_1b_SR=1,mask_cat_2b_SR=1 --X-rtd MINIMIZER_analytic --cminFallbackAlgo Minuit2,0:1.0")
            os.system("combine -M FitDiagnostics  "+wsname+" --saveShapes --saveWithUncertainties --setParameters mask_SR=1,mask_cat_1b_SR=1,mask_cat_2b_SR=1 --X-rtd MINIMIZER_analytic --cminFallbackAlgo Minuit2,0:1.0")


            self.SavePrePostComparison("cronly",outdir, category,year)

    def SetLimitLog(self, name):
      self.limitlog = name
      self.limit_root_file   = self.limitlog.replace(".txt",".root")
      self.limitlog_tmp_node = self.limitlog.replace(".txt","_{}.txt")


    def Scan2DNLL(self, dc, POI_name = 'r_3b', asimov=True, mass_point='MA200', cminDefaultMinimizerStrategy=0, rAbsAcc=0.001, cminDefaultMinimizerTolerance=1.0, dc_dir=None, out_dir=None, extraCommand='', model_name = 'g2HDM_3Bbased'):
        asimovstr ="-t -1 "
        tag = self.year_ + "_" + self.region_ + "_" + self.channel_ + "_" + mass_point+"_"+ self.signal_str_ + "_" + self.postfix_ + "_" + self.model_

        imass = mass_point.replace('MA', '').replace('mH','')
        input_file = self.limitlog_tmp_node.format(mass_point)
        if CheckFile(input_file):pass
        else:
            raise ValueError('Make sure you have this file: {}'.format(input_file))

        f = open(input_file,"r")
        expmed = 1.0
        for line in f:
            if len(line.rsplit())<7: continue
            expmed = (float(line.rstrip().split()[4])) * 4.0

        if model_name == 'g2HDM_separate':
          command_ = "combine -M MultiDimFit " + dc + extraCommand + f' --setParameterRanges r_2b=0,{expmed}:r_3b=0,{expmed*2} --setParameters r_2b=0,r_3b=0 ' #TODO check -t -1 is correct
        else:
          command_ = "combine -M MultiDimFit " + dc + extraCommand + ' --setParameterRanges {POI}=0,2:Rb=0,2 --setParameters {POI}=1,Rb=1 '.format(POI=POI_name) #TODO check -t -1 is correct
        if asimov:
            command_ = command_ + asimovstr
        if self.__verbose:
            command_ = command_ + '-v 3'

        os.system(command_ + "--algo grid --points 800 -n {tag} --cminDefaultMinimizerStrategy 0 ".format(tag = tag + "_2DNLL" ))
        output_rootfile = "higgsCombine"+self.year_+"_"+self.region_+"_" + self.channel_ + "_"+mass_point+"_" + self.signal_str_ + "_" + self.postfix_+"_"+self.model_+"_2DNLL.MultiDimFit.mH120.root"
        print(command_  + "--algo grid --points 2000 & ")
        CheckDir(out_dir,MakeDir=True)
        # delete the output combine root file (not to make dirty your home area!)
        os.system("mv {out} {outdir}/.".format(out=output_rootfile, outdir=out_dir))

        #output_rootfile = "higgsCombine"+self.year_+"_"+self.region_+"_" + self.channel_ + "_"+mass_point+"_" + self.signal_str_ + "_" + self.postfix_+"_"+self.model_+"_2DContour68.MultiDimFit.mH120.root"
        #os.system("(" + command_ + "--algo contour2d --cl 0.68 -n {tag} --points 20 --fastScan && mv {out} {outdir}/.) &".format(tag = tag + "_2DContour68", out=output_rootfile, outdir=out_dir))

        #output_rootfile = "higgsCombine"+self.year_+"_"+self.region_+"_" + self.channel_ + "_"+mass_point+"_" + self.signal_str_ + "_" + self.postfix_+"_"+self.model_+"_2DContour95.MultiDimFit.mH120.root"
        #os.system(command_ + "--algo contour2d --cl 0.95 -n {tag} --points 20 --fastScan ; mv {out} {outdir}/.".format(tag = tag + "_2DContour95" , out=output_rootfile, outdir=out_dir))

#        os.system(command_ + "--algo contour2d --cl 0.99 -n {tag} --points 20 --fastScan".format(tag = tag + "_2DContour99" ))
#        output_rootfile = "higgsCombine"+self.year_+"_"+self.region_+"_" + self.channel_ + "_"+mass_point+"_" + self.signal_str_ + "_" + self.postfix_+"_"+self.model_+"_2DContour99.MultiDimFit.mH120.root"
#        os.system("mv {out} {outdir}/.".format(out=output_rootfile, outdir=out_dir))

    def bestFit(self, fin_name, x, y, xsec_2b = 1.0, xsec_3b = 1.0):
        x_values = array('d', [])
        y_values = array('d', [])
        fin = rt.TFile.Open(fin_name, "READ")
        t = fin.Get("limit")
        for entry in t:
          if entry.quantileExpected == -1:
            x_values.append(getattr(entry, x) * xsec_2b)
            y_values.append(getattr(entry, y) * xsec_3b)
            # Assuming x_values and y_values are lists or arrays containing your data points
        graph = rt.TGraph(len(x_values), x_values, y_values)  # Create the TGraph with your data
        graph.SetName("MyGraph")  # Set the name of the graph to "MyGraph"
        graph.Draw("P SAME")  # Draw the graph on the same canvas as existing plots
        gr0 = graph.Clone()  # Clone the graph to gr0

        #t.Draw(y+":"+x+">>Graph", "quantileExpected == 1", "P SAME")
        #gr0 = rt.gROOT.FindObject("Graph").Clone()
        #rt.gROOT.FindObject("Graph").SetName("aa")
        #rt.gROOT.Remove(rt.gROOT.FindObject("Graph"))
        gr0.SetMarkerStyle(34)
        gr0.SetMarkerSize(2.0)
        fin.Close()
        return gr0

    def drawPoint(self, x, y, style = 34, color = rt.kRed, size = 4.0):
      x_values = array('d', [x])
      y_values = array('d', [y])
      graph = rt.TGraph(len(x_values), x_values, y_values)  # Create the TGraph with your data
      graph.SetName("MyGraph")  # Set the name of the graph to "MyGraph"
      gr0 = graph.Clone()  # Clone the graph to gr0
      gr0.SetMarkerStyle(style)
      gr0.SetMarkerSize(size)
      gr0.SetMarkerColor(color)
      return gr0


    def draw_2DNLL(self, fin_name, x, y, xsec_2b_limit = 1.0, xsec_3b_limit = 1.0, xsec_2b = 1.0, xsec_3b = 1.0):
        fin = rt.TFile.Open(fin_name, "READ")
        t = fin.Get("limit")
        # Compute boundaries dynamically
        xsec_2b_boundary = t.GetMaximum("{x}*{xsec_2b}".format(x=x, xsec_2b=xsec_2b))
        xsec_3b_boundary = t.GetMaximum("{y}*{xsec_3b}".format(y=y, xsec_3b=xsec_3b))

        print(xsec_3b_limit, xsec_3b)
#        h = rt.TH2F('2DNLL', '2*deltaNLL:{x}:{y}'.format(x=x,y=y),44,0,2,44,0,2)
        t.Draw("2*deltaNLL:{y}*{xsec_3b}:{x}*{xsec_2b}>>2DNLL(28, 0, {xsec_2b_boundary}, 28, 0, {xsec_3b_boundary})".format(x=x, y=y, xsec_2b_boundary = xsec_2b * xsec_2b_limit, xsec_3b_boundary = xsec_3b * xsec_3b_limit, xsec_2b = xsec_2b, xsec_3b = xsec_3b),"","PROF COLZ")
        h = rt.gROOT.FindObject("2DNLL").Clone()
#        for entry in range(t.GetEntries()):
#          t.GetEntry(entry)
#          h.Fill(eval("t.{x}".format(x=x)), eval("t.{y}".format(y=y)), 2*t.deltaNLL)
        h.SetDirectory(0)
        fin.Close()
        return h




    def draw_contour2D(self, fin_name, x, y, xsec_2b_limit = 1.0, xsec_3b_limit = 1.0, xsec_2b = 1.0, xsec_3b = 1.0):

        # Ref: https://cms-analysis.github.io/HiggsAnalysis-CombinedLimit/tutorial2023/parametric_exercise/?h=contour#two-dimensional-likelihood-scan

        fin = rt.TFile.Open(fin_name, "READ")
        t = fin.Get("limit")

        # Number of points in interpolation
        n_points = 200
        x_range = [0, xsec_2b_limit * xsec_2b]
        y_range = [0, xsec_3b_limit * xsec_3b]

        n_bins = 40

        x_array, y_array, deltaNLL = [], [], []
        for ev in t:
            x_array.append(getattr(ev, x) * xsec_2b)
            y_array.append(getattr(ev, y) * xsec_3b)
            deltaNLL.append(getattr(ev, "deltaNLL"))

        dnll = np.asarray(deltaNLL)
        points = np.array([x_array, y_array]).transpose()
        # Set up grid
        grid_x, grid_y = np.mgrid[x_range[0] : x_range[1] : n_points * 1j, y_range[0] : y_range[1] : n_points * 1j]
        grid_vals = griddata(points, dnll, (grid_x, grid_y), "cubic")



        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

        # Remove NANS
        grid_x = grid_x[grid_vals == grid_vals]
        grid_y = grid_y[grid_vals == grid_vals]
        grid_vals = grid_vals[grid_vals == grid_vals]
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


        # Define Profile2D histogram
        h2D = rt.TProfile2D("h", "h", n_bins, x_range[0], x_range[1], n_bins, y_range[0], y_range[1])
        h2D.SetDirectory(0)


        for i in range(len(grid_vals)):
           # Factor of 2 comes from 2*NLL
           h2D.Fill(grid_x[i], grid_y[i], 2 * grid_vals[i])

        # Loop over bins: if content = 0 then set 999
        for ibin in range(1, h2D.GetNbinsX() + 1):
          for jbin in range(1, h2D.GetNbinsY() + 1):
              if h2D.GetBinContent(ibin, jbin) == 0:
                  xc = h2D.GetXaxis().GetBinCenter(ibin)
                  yc = h2D.GetYaxis().GetBinCenter(jbin)
                  h2D.Fill(xc, yc, 999)
        h2D.SetContour(999)

        c68, c95 = h2D.Clone(), h2D.Clone()
        c68.SetContour(2)
        c68.SetContourLevel(1, 2.3)
        c68.SetContourLevel(0, 1e10)
        c68.SetLineWidth(3)
        c68.SetLineColor(rt.kBlue)
        c95.SetContour(2)
        c95.SetContourLevel(0, 1e10)
        c95.SetContourLevel(1, 5.99)
        c95.SetLineWidth(3)
        c95.SetLineStyle(2)
        c95.SetLineColor(rt.kRed)
        c68.SetDirectory(0)
        c95.SetDirectory(0)
        fin.Close()

        return h2D, c68, c95

    def draw_contour(self, fin_name, x, y, pmin, pmax, bestFit, xsec_2b = 1.0, xsec_3b = 1.0):
      fin = rt.TFile.Open(fin_name, "READ")
      t = fin.Get("limit")
      t.Draw("{y}*{xsec_3b}:{x}*{xsec_2b}".format(x=x, y=y, xsec_2b = xsec_2b, xsec_3b = xsec_3b), "%f <= quantileExpected && quantileExpected <= %f && quantileExpected != 1"%(pmin,pmax), "SAME p");
      gr = rt.gROOT.FindObject("Graph").Clone();
      rt.gROOT.FindObject("Graph").SetName("aa")
      x0 = bestFit.GetX()[0] * xsec_2b
      y0 = bestFit.GetY()[0] * xsec_3b;
      xi = gr.GetX()
      yi = gr.GetY();
      n  = gr.GetN();
      for i in range(n):
        xi[i] -= x0
        yi[i] -= y0

      gr.Sort(rt.TGraph.CompareArg)
      for i in range(n):
        xi[i] += x0
        yi[i] += y0
      fin.Close()
      return gr

    def Save2DNLL(self,outputdir='./', mass_point='MA200', POI_name='r_3b', model_name = 'g2HDM_3Bbased', ratio_file = None, df_sig_xsec = None):
        rt.gStyle.Reset()
        rt.gStyle.SetOptTitle(0)
        rt.gStyle.SetOptStat(0)
        rt.gROOT.SetBatch(1)
        rt.gStyle.SetCanvasColor(0)
        rt.gStyle.SetPalette(rt.kLightTemperature)
        rt.TColor.InvertPalette();
        c = rt.TCanvas("c","c",700, 600)
        c.SetTopMargin(0.085)
        c.SetRightMargin(0.14)
        c.SetLeftMargin(0.14)
        c.SetLogz(1)
        c.SetGrid(0,0)
        c.SetTicks(1,1)


        imass = mass_point.replace('MA', '').replace('mH','')
        input_file = self.limitlog_tmp_node.format(mass_point)
        if CheckFile(input_file):pass
        else:
            raise ValueError('Make sure you have this file: {}'.format(input_file))

        f = open(input_file,"r")
        expmed = 1.0
        for line in f:
            if len(line.rsplit())<7: continue
            expmed = (float(line.rstrip().split()[4])) * 4.0
            print("expmed", expmed)
        xsec_2b_limit = expmed
        xsec_3b_limit = expmed * 2.0

        tag = self.year_ + "_" + self.region_ + "_" + self.channel_ + "_" + mass_point+"_"+ self.signal_str_ + "_" + self.postfix_ + "_" + self.model_
        MultiFit_root_file = os.path.join(outputdir, '2DNLL', 'higgsCombine{tag}_2DNLL.MultiDimFit.mH120.root'.format(tag=tag))


        xsec_2b_ratio = 1.0
        xsec_3b_ratio = 1.0
        signal_points = OrderedDict()
        if model_name == 'g2HDM_separate':
          POI_name = 'r_2b'
          second_POI_name = 'r_3b'
          if ratio_file is not None:
            ratios = read_json(ratio_file)
            ratio_ = ratios[str(mass_point).replace('MH', '')]
            xsec_2b_ratio = ratio_ / (1.0 + ratio_)
            xsec_3b_ratio = 1.0 / (1.0 + ratio_)
            mass = mass_point.replace('MH','')

            if int(mass) < 600:
              couplings = [(0.1, 0.1), (0.1, 0.4), (0.1, 0.6), (0.1, 1.0)]
            if int(mass) >= 600:
              couplings = [(0.1, 0.1), (0.1, 0.4), (0.4, 0.6), (0.6, 0.4)]
            for coupling_ in couplings:
              rtc = coupling_[0]
              rtt = coupling_[1]
              xsec = df_sig_xsec[(df_sig_xsec['Mass'] == int(mass)) & (abs(df_sig_xsec['rtt'] - rtt) < 1e-5) & (abs(df_sig_xsec['rtc'] - rtc) < 1e-5)]['xsec'].iloc[0]
              xsec_2b = xsec * xsec_2b_ratio
              xsec_3b = xsec * xsec_3b_ratio
              signal_points["#rho_{tc}=%.1f, #rho_{tt}=%.1f"%(rtc, rtt)] = self.drawPoint(xsec_2b, xsec_3b, 47, rt.kRed + len(signal_points), size = 2.0)
        else:
          second_POI_name = 'Rb'


        h = self.draw_2DNLL(MultiFit_root_file, POI_name, second_POI_name, xsec_2b = xsec_2b_ratio, xsec_3b = xsec_3b_ratio, xsec_2b_limit = xsec_2b_limit, xsec_3b_limit = xsec_3b_limit)
        h, CL68, CL95 = self.draw_contour2D(MultiFit_root_file, POI_name, second_POI_name, xsec_2b = xsec_2b_ratio, xsec_3b = xsec_3b_ratio, xsec_2b_limit = xsec_2b_limit, xsec_3b_limit = xsec_3b_limit)

        h.SetTitle("2 #Delta NLL;;;")
        if model_name == 'g2HDM_separate':
          h.GetXaxis().SetTitle('#sigma(pp#rightarrow H^{#pm})Br(H^{#pm}#rightarrow tb)[pb]' if POI_name == 'r_2b' else '#sigma(pp#rightarrow bH^{#pm})Br(H^{#pm}#rightarrow tb)[pb]')
          h.GetYaxis().SetTitle('#sigma(pp#rightarrow H^{#pm})Br(H^{#pm}#rightarrow tb)[pb]' if second_POI_name == 'r_2b' else '#sigma(pp#rightarrow bH^{#pm})Br(H^{#pm}#rightarrow tb)[pb]')
        else:
          h.GetXaxis().SetTitle(POI_name)
          h.GetYaxis().SetTitle(second_POI_name)
        h.GetZaxis().SetTitle("2 #Delta NLL")
        h.GetZaxis().SetMaxDigits(2)
        best_fit = self.bestFit(MultiFit_root_file, POI_name, second_POI_name, xsec_2b = xsec_2b_ratio, xsec_3b = xsec_3b_ratio)

        #CL68_root_file = os.path.join(outputdir, '2DNLL', 'higgsCombine{tag}_2DContour68.MultiDimFit.mH120.root'.format(tag=tag))
        #CL68 = self.draw_contour(CL68_root_file, POI_name, second_POI_name, 0.31, 1.0, best_fit, xsec_2b = xsec_2b_ratio, xsec_3b = xsec_3b_ratio)
        #CL68.SetLineWidth(2); CL68.SetLineStyle(1); CL68.SetLineColor(1); CL68.SetFillStyle(1001); CL68.SetFillColorAlpha(17,0.35); CL68.SetMarkerSize(3)
        #CL95_root_file = os.path.join(outputdir, '2DNLL', 'higgsCombine{tag}_2DContour95.MultiDimFit.mH120.root'.format(tag=tag))
        #CL95 = self.draw_contour(CL95_root_file, POI_name, second_POI_name, 0.049, 1.0, best_fit, xsec_2b = xsec_2b_ratio, xsec_3b = xsec_3b_ratio)
        #CL95.SetLineWidth(2); CL95.SetLineStyle(7); CL95.SetLineColor(1); CL95.SetFillStyle(1001); CL95.SetFillColorAlpha(43, 0.5); CL95.SetMarkerSize(3)
        h.Draw("COLZ")
        CL68.Draw("cont3same")
        CL95.Draw("cont3same")

        SM = self.drawPoint(0, 0, 29, rt.kBlue)
        SM.Draw("P SAME")
        for signal_point in signal_points:
          signal_points[signal_point].Draw("P SAME")

        best_fit.Draw("P SAME")

        legend = rt.TLegend(0.55, 0.45, 0.80, 0.9)
        legend.AddEntry(CL68, "1 #sigma band")
        legend.AddEntry(CL95, "2 #sigma band")
        legend.AddEntry(best_fit, "Best Fit(mH^{#pm} = %s GeV)"%(mass_point.replace('MH', '')))
        legend.AddEntry(SM, "SM")
        for signal_point in signal_points:
          legend.AddEntry(signal_points[signal_point], signal_point)
        legend.Draw("SAME")
        plotdir = os.path.join(outputdir, '2DNLL', 'plot')
        CheckDir(plotdir)


        # CMS style

        import CMS_lumi

        CMS_lumi.writeExtraText = 1
        CMS_lumi.relPosX = 0.15
        CMS_lumi.extraText = "Preliminary"
        CMS_lumi.lumi_sqrtS = "13 TeV" # used with iPeriod = 0, e.g. for simulation-only plots (default is an empty string)
        iPos = 0
        iPeriod="run2"
        CMS_lumi.CMS_lumi(c, iPeriod, iPos, 0.135)
        c.Update()

        c.SaveAs(os.path.join(plotdir, '{tag}.png'.format(tag=tag)))
        c.SaveAs(os.path.join(plotdir, '{tag}.pdf'.format(tag=tag)))
        c.SaveAs(os.path.join(plotdir, '{tag}.C'.format(tag=tag)))
