import os 
import sys
import time
import ROOT
import json
CURRENT_WORKDIR = os.getcwd()
sys.path.append(CURRENT_WORKDIR)
ROOT.gROOT.SetBatch(ROOT.kTRUE)
from Util.General_Tool import CheckDir,CheckFile
from Util.General_Tool import CheckFile
from collections import OrderedDict
from operator import itemgetter
#from Util.OverlappingPlots import *
def CheckAndExec(MODE,datacards,mode='',settings=dict()):
    
    #Check And Create Folder: SignalExtraction
    start = time.time()
    os.system("date")
    
    Fit_type =''
    if settings['expectSignal']:
        Fit_type+='s_plus_b'
        settings['expectSignal']= 1
    else:
        Fit_type+='b_only'
        settings['expectSignal']= 0

    
    
    CheckDir("SignalExtraction",True)
    CheckDir("SignalExtraction/{year}".format(year=settings['year']),True)
    CheckDir("SignalExtraction/{year}/{channel}".format(year=settings['year'],channel=settings['channel']),True)
    CheckDir("SignalExtraction/{year}/{channel}/{coupling_values}".format(year=settings['year'],channel=settings['channel'],coupling_values=settings['coupling_value']),True)
    CheckDir("SignalExtraction/{year}/{channel}/{coupling_values}/{higgs}".format(year=settings['year'],channel=settings['channel'],coupling_values=settings['coupling_value'],higgs=settings['higgs']),True)
    CheckDir("SignalExtraction/{year}/{channel}/{coupling_values}/{higgs}/{mass}/".format(year=settings['year'],channel=settings['channel'],coupling_values=settings['coupling_value'],mass=settings['mass'],higgs=settings['higgs']),True)
    CheckDir("SignalExtraction/{year}/{channel}/{coupling_values}/{higgs}/{mass}/{Fit_type}".format(year=settings['year'],channel=settings['channel'],coupling_values=settings['coupling_value'],higgs=settings['higgs'],Fit_type=Fit_type,mass=settings['mass']),True)
    CheckDir("SignalExtraction/{year}/{channel}/{coupling_values}/{higgs}/{mass}/{Fit_type}/err".format(year=settings['year'],channel=settings['channel'],coupling_values=settings['coupling_value'],higgs=settings['higgs'],Fit_type=Fit_type,mass=settings['mass']),True)
    CheckDir("SignalExtraction/{year}/{channel}/{coupling_values}/{higgs}/{mass}/{Fit_type}/output".format(year=settings['year'],channel=settings['channel'],coupling_values=settings['coupling_value'],higgs=settings['higgs'],Fit_type=Fit_type,mass=settings['mass']),True)
    CheckDir("SignalExtraction/{year}/{channel}/{coupling_values}/{higgs}/{mass}/{Fit_type}/log_condor".format(year=settings['year'],channel=settings['channel'],coupling_values=settings['coupling_value'],higgs=settings['higgs'],Fit_type=Fit_type,mass=settings['mass']),True)
    CheckDir("SignalExtraction/{year}/{channel}/{coupling_values}/{higgs}/{mass}/{Fit_type}/results".format(year=settings['year'],channel=settings['channel'],coupling_values=settings['coupling_value'],higgs=settings['higgs'],Fit_type=Fit_type,mass=settings['mass']),True)
    CheckDir("SignalExtraction/{year}/{channel}/{coupling_values}/{higgs}/{mass}/{Fit_type}/root".format(year=settings['year'],channel=settings['channel'],coupling_values=settings['coupling_value'],higgs=settings['higgs'],Fit_type=Fit_type,mass=settings['mass']),True)


    Final_Output_Dir = "SignalExtraction/{year}/{channel}/{coupling_values}/{higgs}/{mass}/{Fit_type}".format(year=settings['year'],channel=settings['channel'],coupling_values=settings['coupling_value'],higgs=settings['higgs'],Fit_type=Fit_type,mass=settings['mass'])

    
    settings['outputdir'] = Final_Output_Dir
    settings['WorkDir'] = CURRENT_WORKDIR
    
    Log_Path = os.path.relpath(datacards,os.path.dirname(datacards)).replace(".txt","_{}.log".format(mode))
    workspace_root = os.path.relpath(datacards,os.path.dirname(datacards)).replace("txt","root")
    FitDiagnostics_file = 'fitDiagnostics_{year}_{channel}_{higgs}_{mass}_{coupling_value}.root'.format(year=settings['year'],channel=settings['channel'],higgs=settings['higgs'],mass=settings['mass'],coupling_value=settings['coupling_value'])
    diffNuisances_File = os.path.join(Final_Output_Dir,FitDiagnostics_file.replace("fitDiagnostics","diffNuisances"))
    impacts_json = 'results/impacts_t0_{year}_{channel}_M{higgs}{mass}_{coupling_value}.json'.format(year=settings['year'],channel=settings['channel'],higgs=settings['higgs'],mass=settings['mass'],coupling_value=settings['coupling_value']) 

    
    
    settings['Log_Path'] = os.path.join(settings['outputdir'],Log_Path)
    CheckFile(settings['Log_Path'],True)
    settings['workspace_root'] = os.path.join(settings['outputdir'],workspace_root)
    settings['datacards'] = os.path.join(settings['WorkDir'],datacards)
    settings['FitDiagnostics_file'] = os.path.join(settings['outputdir'],FitDiagnostics_file)
    settings['diffNuisances_File'] = diffNuisances_File
    settings['impacts_json'] = impacts_json
    settings['postFitPlot'] = 'results/postFit_{}'.format(settings['channel'])
    settings['preFitPlot'] = 'results/preFit_{}'.format(settings['channel'])
    CheckFile(settings['Log_Path'],True,True)
    MODE(settings=settings)
    if mode!='postFitPlot':
        print("* Please see {} for the output information.".format(settings['Log_Path']))
    print("\nRun time for {mode}: {runtime} sec".format(mode=mode,runtime=time.time()-start))



def datacard2workspace(settings=dict()):
    
    CheckFile(settings['workspace_root'],True,True)
    command = 'text2workspace.py {datacards}  -o {workspace_root}  --channel-mask >& {Log_Path}'.format(datacards=settings['datacards'],workspace_root=settings['workspace_root'],Log_Path=settings['Log_Path'])
    print(command)
    os.system(command)
    print("A new Workspace root file: {} is created! ".format(os.path.join(settings['outputdir'],settings['workspace_root'])))

    print("\nNext mode: [FitDiagnostics]")

def FitDiagnostics(settings=dict()):
    
    CheckFile(settings['FitDiagnostics_file'],True) 
    os.system('cd {outputdir}'.format(outputdir=settings['outputdir'])) 
    os.chdir("{outputdir}".format(outputdir=settings['outputdir']))
    workspace_root = os.path.basename(settings['workspace_root'])
    Log_Path = os.path.basename(settings['Log_Path'])

    command = "combine -M FitDiagnostics {workspace_root} --saveShapes -m {mass} --saveWithUncertainties -t -1 --expectSignal {expectSignal} -n _{year}_{channel}_{higgs}_{mass}_{coupling_value} --cminDefaultMinimizerStrategy 0 --rMin {rMin} --rMax {rMax}".format(workspace_root = workspace_root, year=settings['year'],channel=settings['channel'],higgs=settings['higgs'],mass=settings['mass'],coupling_value=settings['coupling_value'],expectSignal=settings['expectSignal'],rMin=settings['rMin'],rMax=settings['rMax'])

    #FitDiagnostics_file = 'fitDiagnostics_{year}_{channel}_{higgs}_{mass}_{coupling_value}.root'.format(year=settings['year'],channel=settings['channel'],higgs=settings['higgs'],mass=settings['mass'],coupling_value=settings['coupling_value'])
    print(command)
    command = command + ' >& {Log_Path}'.format(Log_Path=Log_Path)
    os.system(command)
    #Status : MINIMIZE=0 HESSE=0

    #os.system('mv {FitDiagnostics_file} {outputdir}'.format(FitDiagnostics_file=FitDiagnostics_file,outputdir=settings['outputdir']))
    
    FitDiagnostics_file = settings['FitDiagnostics_file']
    
    print("A new FitDiagnostics file: {} is created! \n".format(FitDiagnostics_file))
    print("* Use the following commands to check whether the Status: MINIMIZE=0 HESSE=0:\n")
    print("(1) root -l {FitDiagnostics_file}\n".format(FitDiagnostics_file=FitDiagnostics_file))
    print("(2) fit_s->Print()\n")
    print("For more detailed information about FitDiagnostics : https://cms-analysis.github.io/HiggsAnalysis-CombinedLimit/part5/longexercise/#c-using-fitdiagnostics") 
    print("\nNext mode: [preFitPlot]")

def diffNuisances(settings=dict()):
    
    CheckFile(settings['diffNuisances_File'],True) 
    
    
    command = 'python diffNuisances.py {FitDiagnostics_file} --all -g {diffNuisances_File} --abs'.format(FitDiagnostics_file=settings['FitDiagnostics_file'],diffNuisances_File=settings['diffNuisances_File'])
    print(command)
    
    command += ' >& {Log_Path}'.format(Log_Path=settings['Log_Path'])
    
    os.system(command)
    
    print("*Please see {} for more information.".format(settings['Log_Path']))
    print("*diffNuisances root file: {} is created. ".format(settings['diffNuisances_File']))
    print("\nNext mode: [PlotPulls]")


def PlotPulls(settings=dict()):
    if settings['year'] == 'run2':n_canvas = '100'
    elif settings['channel']  =='C':n_canvas ='20'
    else:n_canvas = '10'

    command = 'root -l -b -q '+"'PlotPulls.C"+'("{diffNuisances_File}","","_{year}_{channel}_{higgs}_{mass}_{coupling_value}",{n_canvas},"{year}")'.format(diffNuisances_File=settings['diffNuisances_File'],year=settings['year'],channel=settings['channel'],higgs=settings['higgs'],mass=settings['mass'],coupling_value=settings['coupling_value'],n_canvas=n_canvas)+"'"
    print(command)

    command += ' >& {}'.format(settings['Log_Path'])
    os.system(command)
   # os.system("mv {outputdir}/fitDiagnostics_* {outputdir}/results ".format(outputdir=settings['outputdir']))

    os.system("mv {outputdir}/diffNuisances_*_.* {outputdir}/results".format(outputdir=settings['outputdir']))
    print("\n")
    print("*Please see {} for more information.".format(settings['Log_Path']))
    print("*Your pull plots and root files are moved under: [ {}/results ]".format(settings['outputdir']))
    print("\nNext mode: [Impact_doInitFit]")

def Impact_doInitFit(settings=dict()):
    
    print("cd {outputdir}".format(outputdir=settings['outputdir']))
    os.chdir(settings['outputdir'])
    CheckFile("higgsCombine_initialFit_Test.MultiDimFit.mH{mass}.root".format(mass= settings['mass']),True)
    CheckFile("combine_logger.out",True)
    workspace_root = os.path.basename(settings['workspace_root'])
    Log_Path = os.path.basename(settings['Log_Path'])

    command = 'combineTool.py -M Impacts -d {workspace_root} --doInitialFit --robustFit 1 -m {mass} -t -1 --expectSignal {expectSignal} --rMin {rMin} --rMax {rMax} '.format(workspace_root=workspace_root,mass=settings['mass'],expectSignal=settings['expectSignal'],rMin=settings['rMin'],rMax=settings['rMax'])
    print(command)
    command += ' >& {}'.format(Log_Path)
    os.system(command) 
    
    print("\n")
    print("*Please see {} for more information.".format(settings['Log_Path']))
    print("\nNext mode: [Impact_doFits]")



def Impact_doFits(settings=dict()):
    
    print("cd {outputdir}".format(outputdir=settings['outputdir']))
    os.chdir(settings['outputdir'])
    
    workspace_root = os.path.basename(settings['workspace_root'])
    Log_Path = os.path.basename(settings['Log_Path'])
    
    
    command = 'combineTool.py -M Impacts -d {workspace_root} --doFits --robustFit 1 -m {mass} -t -1 --expectSignal {expectSignal} --rMin {rMin} --rMax {rMax} --job-mode condor --task-name {year}-{channel}-{coupling_value}-M{higgs}{mass} '.format(workspace_root=workspace_root,year=settings['year'],channel=settings['channel'],higgs=settings['higgs'],mass=settings['mass'],coupling_value=settings['coupling_value'],expectSignal=settings['expectSignal'],rMin=settings['rMin'],rMax=settings['rMax'])+'--sub-opts='+"'+JobFlavour="+'"testmatch"'+"'"
    
    print(command)
    command += ' >& {}'.format(Log_Path)
    os.system(command) 

    print("\n")
    print("You need to wait for the condor job is done, then move to the next step [Plot_Impacts].")
    print("\nNext mode: [Plot_Impacts]")

def Plot_Impacts(settings=dict()):

    print("cd {outputdir}".format(outputdir=settings['outputdir']))
    os.chdir(settings['outputdir'])
    Log_Path = os.path.basename(settings['Log_Path'])
    
    os.system("mv *{year}-{channel}-{coupling_value}-M{higgs}{mass}*.err err".format(year=settings['year'],channel=settings['channel'],coupling_value=settings['coupling_value'],higgs=settings['higgs'],mass=settings['mass']))
    os.system("mv *{year}-{channel}-{coupling_value}-M{higgs}{mass}*.log log_condor".format(year=settings['year'],channel=settings['channel'],coupling_value=settings['coupling_value'],higgs=settings['higgs'],mass=settings['mass']))
    os.system("mv *{year}-{channel}-{coupling_value}-M{higgs}{mass}*.out output".format(year=settings['year'],channel=settings['channel'],coupling_value=settings['coupling_value'],higgs=settings['higgs'],mass=settings['mass']))
    os.system("mv higgsCombine_paramFit*.root root/")
    os.system("mv higgsCombine_initialFit*.root root/")
    
    os.chdir("root")

    workspace_root = os.path.basename(settings['workspace_root'])
    Log_Path = os.path.basename(settings['Log_Path'])
    command = 'combineTool.py -M Impacts -d ../{workspace_root} -o ../{impacts_json} -m {mass}'.format(workspace_root=workspace_root,impacts_json=settings['impacts_json'],mass=settings['mass'])
    print(command+"\n\n")
    command += ' > {Log_Path}'.format(Log_Path=Log_Path)
    os.system(command)
   
    os.chdir('../')
    command = 'plotImpacts.py -i  {impacts_json} -o {impacts_json_prefix}'.format(impacts_json=settings['impacts_json'],impacts_json_prefix=settings['impacts_json'].replace(".json",""))
    
    print(command+"\n\n")
    command += ' >> {Log_Path}'.format(Log_Path=Log_Path)
    os.system(command)
    
    command = 'pdftoppm {impacts_json_prefix}.pdf {impacts_json_prefix} -png -rx 300 -ry 300'.format(impacts_json_prefix= settings['impacts_json'].replace(".json",""))
    print(command+"\n\n")
    
    os.system(command)    
    
    print("Please check {impacts_json_prefix}.pdf".format(impacts_json_prefix=os.path.join(settings['outputdir'],settings['impacts_json'].replace(".json",""))))
    #print("Please check {impacts_json_prefix}.png".format(impacts_json_prefix=os.path.join(settings['outputdir'],settings['impacts_json'].replace(".json",""))))
    
    #print("mv higgsCombine_paramFit*.root root/")
    #os.system("mv higgsCombine_paramFit*.root root/")

def postFitPlot(settings=dict()):
    figDiagnostics_File = settings['FitDiagnostics_file']
    if CheckFile(figDiagnostics_File,False,False):pass
    else:
        FitDiagnostics_file_1 = 'results/fitDiagnostics_{year}_{channel}_{higgs}_{mass}_{coupling_value}.root'.format(year=settings['year'],channel=settings['channel'],higgs=settings['higgs'],mass=settings['mass'],coupling_value=settings['coupling_value'])
        figDiagnostics_File = os.path.join(settings['outputdir'],FitDiagnostics_file_1)
        if CheckFile(figDiagnostics_File,False,False):pass
        else: raise ValueError('Check :{figDiagnostics_File} exists or not. Otherwise you should go back to [FigDiagnostics_File] stage.'.format(figDiagnostics_File=figDiagnostics_File))



    SampleName_File = "./data_info/Sample_Names/process_name_2018.json"
    with open(SampleName_File,'r') as f:
        Sample_Names = json.load(f).keys()
    Histogram = dict()
    Histogram_Names = []
    for Sample_Name in Sample_Names:
        Histogram_Names.append(str(Sample_Name))

    fin = ROOT.TFile(figDiagnostics_File,"READ")

    if settings['expectSignal']:
        first_dir = 'shapes_fit_s'
    else:
        first_dir = 'shapes_fit_b'

    first_dir = 'shapes_fit_b'
    
    second_dirs = []
    if settings['channel'] != 'C' and settings['year'] !='run2':
        second_dirs = ['/SR_{channel}/'.format(channel=settings['channel'])]
    elif settings['channel'] =='C' and settings['year'] != 'run2':
        second_dirs = ['/ee/','/em/','/mm/']
    elif settings['year'] == 'run2' and settings['channel'] != 'C':
        for year in ['/year2016apv/','/year2016postapv/','/year2017/','/year2018/']:
            second_dirs.append(year)
    elif settings['year'] =='run2' and settings['channel'] =='C':
        for year in ['/year2016apv','/year2016postapv','/year2017','/year2018']:
            for channel in ['ee/','em/','mm/']:
                second_dirs.append(year+'_'+channel)
    
    Histogram = dict()
    Integral= dict()
    Maximum = -1
    Histogram_Registered = False 
    
    for second_dir in second_dirs: 

        for Histogram_Name in Histogram_Names:
            #Histogram[Histogram_Name] = fin.Get(first_dir+second_dir+Histogram_Name).Clone()
            print(first_dir+second_dir+Histogram_Name)
            h = fin.Get(first_dir+second_dir+Histogram_Name).Clone()
            nbin = h.GetNbinsX()
            h_reset_x_scale = ROOT.TH1F(Histogram_Name+'_',Histogram_Name+'_',nbin,-1,1)

            if type(h) != ROOT.TH1F:
                raise ValueError("No such histogram, please check {SampleName_File} and {figDiagnostics_File}".format(SampleName_File=SampleName_File,figDiagnostics_File=figDiagnostics_File))
            else:
                print("Access: {}".format(Histogram_Name))
                if Histogram_Registered:
                    Integral[Histogram_Name] += h.Integral()
                else:
                    Integral[Histogram_Name] = h.Integral()
                ### Set Bin Content
                
                for ibin in range(nbin+2):
                    h_reset_x_scale.SetBinContent(ibin+1,h.GetBinContent(ibin+1))
                if Histogram_Registered:
                    Histogram[Histogram_Name].Add(h_reset_x_scale)
                else:
                    Histogram[Histogram_Name] = h_reset_x_scale
        Histogram_Registered=True
    
    for Histogram_Name in Histogram_Names:
        if Maximum < Histogram[Histogram_Name].GetMaximum():
            Maximum = Histogram[Histogram_Name].GetMaximum()


    
    template_settings= {
            "Maximum":Maximum,
            "Integral":Integral,
            "Histogram":Histogram,
            "outputfilename":os.path.join(CURRENT_WORKDIR,os.path.join(settings['outputdir'],settings['postFitPlot'])),
            "year":settings['year'],      
            "Title":'Post-Fit Distribution',
            "xaxisTitle":'BDT score',
            "yaxisTitle":'Events/(1)',
            "channel":settings['channel'],
            "coupling_value":settings['coupling_value'],
            "mass":settings["mass"]
            } 
    Plot_Histogram(template_settings=template_settings) 


    #a = h_stack.GetXaxis();
    #a.ChangeLabel(1,-1,-1,-1,-1,-1,"-1");
    #a.ChangeLabel(-1,-1,-1,-1,-1,-1,"1");
    print("Please check {prefix}.pdf".format(prefix=os.path.join(CURRENT_WORKDIR,os.path.join(settings['outputdir'],settings['postFitPlot']))))
    print("Please check {prefix}.png".format(prefix=os.path.join(CURRENT_WORKDIR,os.path.join(settings['outputdir'],settings['postFitPlot']))))
    
    print("\nNext mode: [diffNuisances]")
    



def preFitPlot(settings=dict()):
    figDiagnostics_File = settings['FitDiagnostics_file']
    if CheckFile(figDiagnostics_File,False,False):pass
    else:
        FitDiagnostics_file_1 = 'results/fitDiagnostics_{year}_{channel}_{higgs}_{mass}_{coupling_value}.root'.format(year=settings['year'],channel=settings['channel'],higgs=settings['higgs'],mass=settings['mass'],coupling_value=settings['coupling_value'])
        figDiagnostics_File = os.path.join(settings['outputdir'],FitDiagnostics_file_1)
        if CheckFile(figDiagnostics_File,False,False):pass
        else: raise ValueError('Check :{figDiagnostics_File} exists or not. Otherwise you should go back to [FigDiagnostics_File] stage.'.format(figDiagnostics_File=figDiagnostics_File))

    #### Define Category Names for Samples ####
    SampleName_File = "./data_info/Sample_Names/process_name_2018.json"
    with open(SampleName_File,'r') as f:
        Sample_Names = json.load(f).keys()
    Histogram_Names = []
    for Sample_Name in Sample_Names:
        Histogram_Names.append(str(Sample_Name))
    ########################################## 
    
    Histogram = dict()
    Integral= dict()
    Maximum = -1
    fin = ROOT.TFile(figDiagnostics_File,"READ")

    Histogram = dict()
    if settings['expectSignal']:
        first_dir = 'shapes_fit_s'
        #TAToTTQ_300_s_250_rtc04 -> Inteference sample
        Histogram_Names.append("TAToTTQ_{coupling_value}_M{higgs}{mass}".format(coupling_value=settings['coupling_value'],higgs=settings['higgs'],mass=settings['mass']))
    else:
        first_dir = 'shapes_fit_b'

    first_dir = 'shapes_fit_b'
    
    second_dirs = []
    if settings['channel'] != 'C' and settings['year'] !='run2':
        second_dirs = ['/SR_{channel}/'.format(channel=settings['channel'])]
    elif settings['channel'] =='C' and settings['year'] != 'run2':
        second_dirs = ['/ee/','/em/','/mm/']
    elif settings['year'] == 'run2' and settings['channel'] != 'C':
        for year in ['/year2016apv/','/year2016postapv/','/year2017/','/year2018/']:
            second_dirs.append(year)
    elif settings['year'] =='run2' and settings['channel'] =='C':
        for year in ['/year2016apv','/year2016postapv','/year2017','/year2018']:
            for channel in ['ee/','em/','mm/']:
                second_dirs.append(year+'_'+channel)
    
    Integral= dict()
    Maximum = -1
    Histogram_Registered = False 
    
    for second_dir in second_dirs: 

        for Histogram_Name in Histogram_Names:
            #Histogram[Histogram_Name] = fin.Get(first_dir+second_dir+Histogram_Name).Clone()
            print(first_dir+second_dir+Histogram_Name)
            h = fin.Get(first_dir+second_dir+Histogram_Name).Clone()
            nbin = h.GetNbinsX()
            h_reset_x_scale = ROOT.TH1F(Histogram_Name+'_',Histogram_Name+'_',nbin,-1,1)

            if type(h) != ROOT.TH1F:
                raise ValueError("No such histogram, please check {SampleName_File} and {figDiagnostics_File}".format(SampleName_File=SampleName_File,figDiagnostics_File=figDiagnostics_File))
            else:
                print("Access: {}".format(Histogram_Name))
                if Histogram_Registered:
                    Integral[Histogram_Name] += h.Integral()
                else:
                    Integral[Histogram_Name] = h.Integral()
                ### Set Bin Content
                
                for ibin in range(nbin+2):
                    h_reset_x_scale.SetBinContent(ibin+1,h.GetBinContent(ibin+1))
                if Histogram_Registered:
                    Histogram[Histogram_Name].Add(h_reset_x_scale)
                else:
                    Histogram[Histogram_Name] = h_reset_x_scale
        Histogram_Registered=True
    
    for Histogram_Name in Histogram_Names:
        if Maximum < Histogram[Histogram_Name].GetMaximum():
            Maximum = Histogram[Histogram_Name].GetMaximum()
    

    template_settings= {
            "Maximum":Maximum,
            "Integral":Integral,
            "Histogram":Histogram,
            "outputfilename":os.path.join(CURRENT_WORKDIR,os.path.join(settings['outputdir'],settings['preFitPlot'])),
            "year":settings['year'],      
            "Title":'Pre-Fit Distribution',
            "xaxisTitle":'BDT score',
            "yaxisTitle":'Events/(1)',
            "channel":settings['channel'],
            "coupling_value":settings['coupling_value'],
            "mass":settings["mass"]
            } 
    Plot_Histogram(template_settings=template_settings) 


    print("Please check {prefix}.pdf".format(prefix=os.path.join(CURRENT_WORKDIR,os.path.join(settings['outputdir'],settings['preFitPlot']))))
    print("Please check {prefix}.png".format(prefix=os.path.join(CURRENT_WORKDIR,os.path.join(settings['outputdir'],settings['preFitPlot']))))
    print("\nNext mode: [postFitPlot]")




def Plot_Histogram(template_settings=dict()):

    Color_Dict ={
            'DY':ROOT.kRed,
            'VV':ROOT.kCyan-9,
            'VVV':ROOT.kSpring - 9,
            'tttX':ROOT.kPink-3,
            'Nonprompt':ROOT.kViolet-4,
            'tZq':ROOT.kYellow-4,
            'TTTo2L':ROOT.kBlue,
            'ttW':ROOT.kGreen-2,
            'ttZ':ROOT.kCyan-2,
            'VBS':ROOT.kBlue-6,
            'ttVH':ROOT.kRed-9,
            'ttVV':ROOT.kOrange+3,
            'SingleTop':ROOT.kGray,
            }
    for Histogram_Name in template_settings['Histogram'].keys():
        if Histogram_Name not in Color_Dict.keys():
            raise ValueError("Make sure {} in Color_Dict.keys()".format(Histogram_Name)) 

    #### Canvas ####
    ROOT.gStyle.SetOptTitle(0)
    ROOT.gStyle.SetOptStat(0)
    ROOT.gROOT.SetBatch(1)
    canvas = ROOT.TCanvas("","",620,600)

    Set_Logy =True

    if Set_Logy:
        canvas.SetLogy(1)
        Histogram_MaximumScale = 100
    else:
        Histogram_MaximumScale = 1.5
    canvas.SetGrid(1,1)
    canvas.SetLeftMargin(0.12)
    canvas.SetRightMargin(0.08)
    ###############

    #### Legend ####
    legend_NCol = int(len(Color_Dict.keys())/5)
    legend = ROOT.TLegend(.15, .65, .65+0.25*(legend_NCol-1), .890);
    legend.SetNColumns(legend_NCol)
    legend.SetBorderSize(0);
    legend.SetFillColor(0);
    legend.SetShadowColor(0);
    legend.SetTextFont(42);
    legend.SetTextSize(0.03);
    #### Ordered_Integral ####
    Ordered_Integral = OrderedDict(sorted(template_settings['Integral'].items(), key=itemgetter(1)))
    ##########################
    
    #### Histogram Settings ####
    h_stack = ROOT.THStack()
    for idx, Histogram_Name in enumerate(Ordered_Integral):
        template_settings['Histogram'][Histogram_Name].SetFillColor(Color_Dict[Histogram_Name])
        #Histogram[Histogram_Name].Draw('HIST SAME')
        h_stack.Add(template_settings['Histogram'][Histogram_Name])
        legend.AddEntry(template_settings['Histogram'][Histogram_Name],Histogram_Name+' [{:.1f}]'.format(template_settings['Integral'][Histogram_Name]) , 'F')
    h_stack.SetTitle("Post-Fit Distribution;BDT score;Events/(1) ")
    h_stack.SetMaximum(template_settings['Maximum'] * Histogram_MaximumScale)
    h_stack.SetMinimum(1)
    h_stack.Draw("HIST")
    latex = ROOT.TLatex()
    latex.SetTextSize(0.035)
    latex.SetTextAlign(12)  

    ###########################
    if "rtc" in template_settings['coupling_value']:
        quark = "c"
        coupling ="rtc"
    elif "rtu" in template_settings['coupling_value']:
        quark = "u"
        coupling ="rtu"
    else:
        raise ValueError("Check the bugs: {coupling_value}".format(coupling_value = template_settings['coupling_value']))
    value = int(template_settings['coupling_value'].split(coupling)[-1]) * 0.1
    legend.Draw("SAME")
    latex.DrawLatex(.10,200,"#rho_{t%s} = %s"%(quark,value))
    latex.DrawLatex(.5,200,"M_{A} = %s "%(template_settings['mass']))
    latex.DrawLatex(-.4,200,"Channel: {}".format(template_settings['channel']))
    ### CMS Pad #####
    import CMS_lumi
    CMS_lumi.writeExtraText = 1
    CMS_lumi.extraText = "Internal"
    CMS_lumi.lumi_sqrtS = "13 TeV" # used with iPeriod = 0, e.g. for simulation-only plots (default is an empty string)
    iPos = 11
    if( iPos==0 ): CMS_lumi.relPosX = 0.12
    iPeriod=template_settings['year']

    CMS_lumi.CMS_lumi(canvas, iPeriod, iPos)

    ######


    canvas.Update()
    canvas.SaveAs('{prefix}.pdf'.format(prefix=template_settings['outputfilename']))
    canvas.SaveAs('{prefix}.png'.format(prefix=template_settings['outputfilename']))



