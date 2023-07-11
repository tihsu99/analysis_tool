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
#import yaml
#f = open('systematicsDict.yaml') 
#doc = yaml.safe_load(f)


class RunLimits:
    ''' class to perform all tasks related to the limits once datacards are prepared '''
    ''' this class exepcts that all the steps needed to prepare the datacards and prepration of its inputs are already performed '''
    
    ''' instantiation of the class is done here ''' 
    def __init__(self, year, analysis="ttc", analysisbin="em", postfix="asimov", coupling='rtc',coupling_value=0.1, model="extYukawa",unblind=False, interference=False, verbose=False, rMax=5):
        self.year_                 = year
        self.analysis_             = analysis 
        self.analysisbin_          = analysisbin 
        self.postfix_              = postfix
        self.model_                = model
        self.coupling_             = coupling_value
        self.coupling_str_         = str(self.coupling_).replace(".","p")
        self.interference_         = interference
        self.rMax_                 = rMax
        
        #self.limitlog              = "bin/limits_ttc"+self.year_+"_"+self.analysisbin_+"_"+coupling+self.coupling_str_+"_"+self.postfix_+"_"+self.model_+".txt"
        #self.limitlog_scaled       = self.limitlog.replace(".txt","_scaled.txt")
        #self.limit_root_file       = self.limitlog.replace(".txt",".root")
        
        self.limit_dir = "bin/"+self.year_+"/"+analysisbin
        if CheckDir(self.limit_dir,MakeDir=True):pass
        else:pass

        self.limitlog = os.path.join(self.limit_dir,"limits_ttc_"+coupling+self.coupling_str_+"_"+self.postfix_+"_"+self.model_+".txt")
        self.limit_pdf_file = "limits_ttc_"+coupling+self.coupling_str_+"_"+self.postfix_+"_"+self.model_+"_"+analysisbin+".pdf"
        if interference: 
          self.limitlog = self.limitlog.replace(".txt","_interference.txt")
          self.limit_pdf_file = self.limit_pdf_file.replace(".pdf","_interference.pdf")
        self.limit_root_file = self.limitlog.replace(".txt",".root")
        self.limitlog_tmp_node = self.limitlog.replace(".txt","_{}.txt")
        self.Coupling = coupling
        self.__unblind = unblind
        self.__verbose = verbose
        #self.runmode = runmode
        print "class instantiation done"
        
        
    ''' convert a text file with just one columns into a list '''
    def TextFileToList(self, textfile):
        return [iline.rstrip() for iline in open (textfile)]
        
        
    def PrintSpacing(self, nLine=1):
        for iline in range(nLine):
            print "***************************************************************************************************************************************"
            
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
            

    def getLimits(self, dc, asimov=True,mass_point='MA200',cminDefaultMinimizerStrategy=0, rAbsAcc=0.001, cminDefaultMinimizerTolerance=1.0):
        asimovstr =""
        logname = dc.replace(".txt",".log")
        logname = logname.replace( logname.split("/")[-1], os.path.join("log",logname.split("/")[-1] ) )
        print ("logname: ",logname)
        
        if self.__unblind:
            command_ = "combine -M AsymptoticLimits "+dc+" "+"-n "+self.year_+"_"+self.analysisbin_+"_"+mass_point+"_"+self.Coupling+self.coupling_str_+"_"+self.postfix_+"_"+self.model_+' --cminDefaultMinimizerStrategy ' + str(cminDefaultMinimizerStrategy) + ' --rAbsAcc '+ str(rAbsAcc) + ' --X-rtd FITTER_NEW_CROSSING_ALGO --X-rtd FITTER_NEVER_GIVE_UP --X-rtd FITTER_BOUND --cminDefaultMinimizerTolerance=' + str(cminDefaultMinimizerTolerance) + ' --rMax ' + str(self.rMax_) + ' '
        else:
            command_ = "combine -M AsymptoticLimits "+dc+" "+"-n "+self.year_+"_"+self.analysisbin_+"_"+mass_point+"_"+self.Coupling+self.coupling_str_+"_"+self.postfix_+"_"+self.model_+' --run blind --cminDefaultMinimizerStrategy ' + str(cminDefaultMinimizerStrategy) + ' --rAbsAcc '+ str(rAbsAcc) + ' --X-rtd FITTER_NEW_CROSSING_ALGO --X-rtd FITTER_NEVER_GIVE_UP --X-rtd FITTER_BOUND --cminDefaultMinimizerTolerance=' + str(cminDefaultMinimizerTolerance) + ' --rMax ' + str(self.rMax_) + ' '
        if asimov:
            command_ = command_ + asimovstr
        if self.__verbose:
            command_ = command_ + '-v 3'

        os.system(command_+" >& "+logname)
        output_rootfile = "higgsCombine"+self.year_+"_"+self.analysisbin_+"_"+mass_point+"_"+self.Coupling+self.coupling_str_+"_"+self.postfix_+"_"+self.model_+".AsymptoticLimits.mH120.root"
        print(command_+" >& "+logname)

        # delete the output combine root file (not to make dirty your home area!)
        os.system("rm "+output_rootfile)

        return logname
        
    ## category can be merged/resolved/combined
    def LogToLimitList(self, logfile, allparameters, mode="a"):
        expected25_="" 
        expected16_="" 
        expected50_="" 
        expected84_="" 
        expected975_=""
        observed_=""
        for ilongline in open(logfile):
            if "Observed Limit: r < " in ilongline:
                observed_ = ilongline.replace("Observed Limit: r < ","").rstrip()
            if "Expected  2.5%: r < " in ilongline:
                expected25_ = ilongline.replace("Expected  2.5%: r < ","").rstrip()
            if "Expected 16.0%: r < " in ilongline:
                expected16_ = ilongline.replace("Expected 16.0%: r < ","").rstrip()
            if "Expected 50.0%: r < " in ilongline:
                expected50_ = ilongline.replace("Expected 50.0%: r < ","").rstrip()
            if "Expected 84.0%: r < " in ilongline:
                expected84_ = ilongline.replace("Expected 84.0%: r < ","").rstrip()
            if "Expected 97.5%: r < " in ilongline:
                expected975_ = ilongline.replace("Expected 97.5%: r < ","").rstrip()
        
        #allparameters  = self.datacard_to_mparameters(logfile)
        print "allparameters:", allparameters
        towrite =  str(allparameters[2])+" "+str(allparameters[1])+" "+expected25_+" "+expected16_+" "+ expected50_+" "+ expected84_+" "+ expected975_+" "+ observed_+"\n"
        
        print towrite
        #os.system ("mkdir -p bin/"+self.postfix_)
        #os.system ("mkdir -p plots_limit/"+self.postfix_)
        outfile=self.limitlog_tmp_node.format(allparameters[0]+allparameters[1]) 


        
        fout = open(outfile,mode)
        fout.write(towrite)
        fout.close()
        return outfile
    


    def TextFileToRootGraphs(self,med_idx=0,Masses=[],Higgs="MA"):
        #limit_root_file = filename.replace(".txt",".root")
        
        med=array('f')
        mchi=array('f')
        expm2=array('f')
        expm1=array('f')
        expmed=array('f')
        expp1=array('f')
        expp2=array('f')
        obs=array('f')
        errx=array('f')

        counter = 0
        Merged_txt_file = open(self.limitlog,'w')
        
        
        
        for imass in Masses:
            input_file = self.limitlog_tmp_node.format(Higgs+str(imass))
            if CheckFile(input_file):pass
            else:
                raise ValueError('Make sure you have this file: {}'.format(input_file))
            
            f = open(input_file,"r")
            for line in f:
                if len(line.rsplit())<7: continue
                med.append(float(line.rstrip().split()[1]))
                mchi.append(float(line.rstrip().split()[0]))
                
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
        print("Merged Information for Limit is written into {} .".format(self.limitlog))
        g_exp2  = TGraphAsymmErrors(int(len(med)), med, expmed, errx, errx, expm2, expp2 )   ;  g_exp2.SetName("exp2")
        g_exp1  = TGraphAsymmErrors(int(len(med)), med, expmed, errx, errx, expm1, expp1 )   ;  g_exp1.SetName("exp1")
        g_expmed = TGraphAsymmErrors(int(len(med)), med, expmed)   ;  g_expmed.SetName("expmed")
        
        if self.__unblind:
            g_obs    = TGraphAsymmErrors(int(len(med)), med, obs   )   ;  g_obs.SetName("obs")
    
        f1 = TFile(self.limit_root_file,'RECREATE')
        g_exp2.Write()
        g_exp1.Write()
        g_expmed.Write()
        if self.__unblind:
            g_obs.Write()
        f1.Write()
        f1.Close()
        return self.limit_root_file

    def SaveLimitPdf1D(self,outputdir='./',y_max=1000,y_min=0.1):
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
        c.SetLeftMargin(0.12)
        #leg = rt.TLegend(.15, .65, .35, .890);
        f = rt.TFile(rootfile,"read")
        exp2s =  f.Get("exp2")
        exp2s.SetMarkerStyle(20)
        exp2s.SetMarkerSize(1.1)
        exp2s.SetLineWidth(2)
        exp2s.SetFillColor(rt.kYellow);
        exp2s.SetLineColor(rt.kYellow)
        exp2s.GetXaxis().SetTitle("m_{A} (GeV)");
        exp2s.GetYaxis().SetRangeUser(y_min,y_max)
        exp2s.GetXaxis().SetTitleOffset(1.1)
        #exp2s.GetYaxis().SetTitle("95% C.L. asymptotic limit on #mu=#sigma/#sigma_{theory}");
        exp2s.GetYaxis().SetTitle("95% C.L. #mu=#sigma/#sigma_{theory}");
        exp2s.GetYaxis().SetTitleOffset(1.7)
        exp2s.GetYaxis().SetNdivisions(20,5,0);
        #exp2s.GetXaxis().SetNdivisions(505);
        exp2s.GetYaxis().SetMoreLogLabels()
        #exp2s.GetXaxis().SetMoreLogLabels()
        #exp2s.GetXaxis().SetRangeUser(10,750)
        exp2s.Draw("A 3")

        exp1s =  f.Get("exp1")
        exp1s.SetMarkerStyle(20)
        exp1s.SetMarkerSize(1.1)
        exp1s.SetLineWidth(2)
        exp1s.SetFillColor(rt.kGreen);
        exp1s.SetLineColor(rt.kGreen)
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
            obs.Draw("L same")
    
        leg = rt.TLegend(.6, .65, .88, .890);
        leg.SetBorderSize(0);
        leg.SetFillColor(0);
        leg.SetShadowColor(0);
        leg.SetTextFont(42);
        leg.SetTextSize(0.03);
        leg.AddEntry(exp, " CL_{S}  Expected ", "LP");
        leg.AddEntry(exp1s, "CL_{S}  Expected #pm 1#sigma", "LF");
        leg.AddEntry(exp2s, " CL_{S}  Expected #pm 2#sigma", "LF");
        if self.__unblind:
            leg.AddEntry(obs, "Observed", "LP");
    
        leg.Draw("same")
        c.Update()
        #print (c.GetUxmin(),c.GetUxmax())
        line = rt.TLine(c.GetUxmin(),1.0,c.GetUxmax(),1.0);
        line.SetLineColor(rt.kRed)
        line.SetLineWidth(2)
        line.Draw('same ')
    
        latex =  rt.TLatex();
        latex.SetNDC();
        latex.SetTextFont(42);
        latex.SetTextSize(0.03);
        latex.SetTextAlign(31);
        latex.SetTextAlign(12);
        model_ = '2HDM+a'
        
        import CMS_lumi
        CMS_lumi.writeExtraText = 1
        CMS_lumi.extraText = "Internal"
        CMS_lumi.lumi_sqrtS = "13 TeV" # used with iPeriod = 0, e.g. for simulation-only plots (default is an empty string)
        iPos = 11
        if( iPos==0 ): CMS_lumi.relPosX = 0.12
        iPeriod=self.year_

        CMS_lumi.CMS_lumi(c, iPeriod, iPos)

        if self.Coupling =='rtc':
            sig_process_name = 'tt#bar{c}  '
        elif self.Coupling =='rtu':
            sig_process_name = 'tt#bar{u}  '
        elif self.Coupling =='rtt':
            sig_process_name = 'tt#bar{t}  '

        if self.interference_:
          latex.DrawLatex(0.20, 0.76, "m_{A}-m_{H} = 50 GeV");
        latex.DrawLatex(0.20, 0.7, sig_process_name+self.analysisbin_);
        latex.DrawLatex(0.20, 0.64, "Extra Yukawa");
        latex.DrawLatex(0.15, 0.58, "{} =".format(self.Coupling)+str(self.coupling_)); #sin#theta = 0.7, m_{\chi} = 1 GeV");
        #latex.DrawLatex(0.15, 0.52, "sin#theta = 0.7, m_{\chi} = 1 GeV");
        
                
        OUT_DIR = os.path.join(outputdir,"plots_limit")
        
        #if not os.path.isdir(OUT_DIR):os.system("mkdir -p {OUT_DIR}")

        #self.limit_pdf_file  = rootfile.replace(".root","_"+self.model_+".pdf").replace("bin","plot_limit")
        #c.SetLogx(1)
        c.Update()
        #c.SaveAs(name+".png")
        
        CheckDir(OUT_DIR,True)
        self.limit_pdf_file  = os.path.join(OUT_DIR,self.limit_pdf_file)
        
        CheckFile(self.limit_pdf_file,True)
        
        c.SaveAs(self.limit_pdf_file)
        self.limit_png_file = self.limit_pdf_file.replace(".pdf",".png")

        CheckFile(self.limit_png_file,True)
        c.SaveAs(self.limit_png_file)
        
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
        print "do nothing for now"
        ## run impact  data 
        
        
    def SavePrePostComparison(self,run_mode, outdir, category, year):
        default_fit_root   = "fitDiagnostics.root"
        default_pull_root  = "pulls.root"
        
        ''' prepare the names of root file '''
        fit_Diagnostics = default_fit_root.replace(".root", "_"+category+"_"+year+"_"+run_mode+".root")
        pull_root       = default_pull_root.replace(".root",  "_"+category+"_"+year+"_"+run_mode+".root")
        
        print "run_mode, fit_Diagnostics, pull_root", run_mode, fit_Diagnostics, pull_root
        ''' move the rootfile to avoid ambiguity '''         

        postfix_ = "_"+category+"_"+year+"_"
        
        
        if run_mode == "cronly":
            self.PrintSpacing()
            dir_ = outdir["pulls"]
            os.system("mv "+default_fit_root+" " + fit_Diagnostics)
            os.system('root -l -b -q plotPostNuisance_combine.C\(\\"'+fit_Diagnostics+'\\",\\"'+dir_+'\\",\\"'+postfix_+'\\"\)')
            
            print ("python PlotPreFitPostFit.py "+fit_Diagnostics+" "+dir_+" "+postfix_)
            os.system("python PlotPreFitPostFit.py "+fit_Diagnostics+" "+dir_+" "+postfix_)
        
        if run_mode != "cronly":
            os.system("mv "+default_fit_root+" " + fit_Diagnostics)
            ''' get the different of nuisances ''' 
            self.PrintSpacing()
            print ("python diffNuisances.py "+fit_Diagnostics+" --abs --all -g "+pull_root)
            os.system("python diffNuisances.py "+fit_Diagnostics+" --abs --all -g "+pull_root)
            os.system("mv "+default_pull_root+" " + pull_root)
            self.PrintSpacing()
            dir_ = outdir["pulls"]
            
            print ('root -l -b -q PlotPulls.C\(\\"'+pull_root+'\\",\\"'+dir_+'\\",\\"'+postfix_+'\\"\)')
            os.system('root -l -b -q PlotPulls.C\(\\"'+pull_root+'\\",\\"'+dir_+'\\",\\"'+postfix_+'\\"\)')
            dir_ = outdir["yr"]
            self.PrintSpacing()
            print ("python yieldratio.py "+fit_Diagnostics+" "+dir_+" "+postfix_)
            os.system("python yieldratio.py "+fit_Diagnostics+" "+dir_+" "+postfix_)
            dir_ = outdir["pfitOverlay"]
            self.PrintSpacing()
            
            print ("python PlotPreFitPostFit.py "+fit_Diagnostics+" "+dir_+" "+postfix_)
            os.system("python PlotPreFitPostFit.py "+fit_Diagnostics+" "+dir_+" "+postfix_)
            
            dir_ = outdir["stack"]
            print "call the stack file"
            dir_ = outdir["tf"]
            print "call the TF file"
            

                        

    
            

    def RunPulls(self, datacard, run_mode, outdir, category, year):
        ## setup the dir structure 
        #self.setupDirs("configs/pulls_dir.txt")
        ## data fit 
        if run_mode == "data":
            self.PrintSpacing(2)
            print "performing the fit in run_mode ",run_mode
            print ("combine -M FitDiagnostics --saveShapes "+datacard+ " --saveWithUncertainties --saveNormalizations --X-rtd MINIMIZER_analytic ")
            os.system("combine -M FitDiagnostics --saveShapes "+datacard+ " --saveWithUncertainties --saveNormalizations --X-rtd MINIMIZER_analytic ")
            self.PrintSpacing(1)
            self.SavePrePostComparison("data",outdir,category, year)
        
            

        ## asimov fit 
        if run_mode == "asimov":
            self.PrintSpacing(2)
            print ("combine -M FitDiagnostics --saveShapes "+datacard + " --saveWithUncertainties --saveNormalizations --X-rtd MINIMIZER_analytic  --rMin -100 -t -1 --expectSignal 0")
            os.system("combine -M FitDiagnostics --saveShapes "+datacard + " --saveWithUncertainties --saveNormalizations --X-rtd MINIMIZER_analytic  --rMin -100 -t -1 --expectSignal 0")
            self.PrintSpacing(1)
            self.SavePrePostComparison("asimov",outdir,category,year)
        
        ## CR only fit 
        if run_mode == "cronly":
            print ("text2workspace.py "+datacard+" --channel-masks")
            os.system("text2workspace.py "+datacard+" --channel-masks")
            wsname = datacard.replace(".txt",".root")

            print("combine -M FitDiagnostics  "+wsname+" --saveShapes --saveWithUncertainties --setParameters mask_SR=1,mask_cat_1b_SR=1,mask_cat_2b_SR=1 --X-rtd MINIMIZER_analytic --cminFallbackAlgo Minuit2,0:1.0")
            os.system("combine -M FitDiagnostics  "+wsname+" --saveShapes --saveWithUncertainties --setParameters mask_SR=1,mask_cat_1b_SR=1,mask_cat_2b_SR=1 --X-rtd MINIMIZER_analytic --cminFallbackAlgo Minuit2,0:1.0")
            
            
            self.SavePrePostComparison("cronly",outdir, category,year)
        
        
