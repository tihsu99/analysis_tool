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
from Util.aux import *


#from Util.OverlappingPlots import *
def CheckAndExec(MODE,datacards,mode='',settings=dict()):
    
    #Check And Create Folder: SignalExtraction
    start = time.time()
    date = os.popen("date").read()
    print("\033[1;37m{date}\033[0;m".format(date=date))
    
    Fit_type =''
    if settings['expectSignal']:
        Fit_type+='s_plus_b'
        settings['expectSignal']= 1
    else:
        Fit_type+='b_only'
        settings['expectSignal']= 0
    
        
    CheckDir("SignalExtraction/{year}/{channel}/{coupling_values}/{higgs}/{mass}/".format(year=settings['year'],channel=settings['channel'],coupling_values=settings['coupling_value'],mass=settings['mass'],higgs=settings['higgs']),False)
    
    
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
    settings['workspace_root'] = os.path.join(settings['outputdir'],workspace_root)
    settings['datacards'] = os.path.join(settings['WorkDir'],datacards)
    settings['FitDiagnostics_file'] = os.path.join(settings['outputdir'],FitDiagnostics_file)
    settings['diffNuisances_File'] = diffNuisances_File
    settings['impacts_json'] = impacts_json
    settings['postFitPlot'] = 'results/postFit_{}'.format(settings['channel'])
    settings['preFitPlot'] = 'results/preFit_{}'.format(settings['channel'])
    if mode == 'postFitPlot' or mode == "preFitPlot" or mode == "PlotPulls" or mode=="Plot_Impacts" or mode =="ResultsCopy":
        MODE(settings=settings)
        if mode == "PlotPulls" or mode =="Plot_Impacts" or mode=="ResultsCopy": 
            pass
        else:
            print("\033[1;33m* You can use [--text_y] arguments to modify the y position of [channel mass year] in the plots.\033[0;m")
    else:
        CheckFile(settings['Log_Path'],True)
        MODE(settings=settings)
        print("\033[1;33m* Please see \033[4m{}\033[0;m \033[1;33mfor the output information. \033[0;m".format(settings['Log_Path']))
    
    print("\nRun time for \033[1;33m {mode} \033[0;m: \033[0;33m {runtime} \033[0;m sec".format(mode=mode,runtime=time.time()-start))

    

def datacard2workspace(settings=dict()):
    
    CheckFile(settings['workspace_root'],True,True)
    command = 'text2workspace.py {datacards}  -o {workspace_root}'.format(datacards=settings['datacards'],workspace_root=settings['workspace_root'])
    # print("\033[0;35m "+command+" \033[0;m\n")
    print(ts+command+ns)
    
    command+=' >& {Log_Path} '.format(Log_Path=settings['Log_Path'])
    os.system(command)

    print("\nNext mode: [\033[0;32m FitDiagnostics \033[0;m]")
    print("\n* A new Workspace root file: \033[0;32m\033[4m{}\033[0;m is created!".format(os.path.join(settings['outputdir'],settings['workspace_root'])))

def FitDiagnostics(settings=dict()):
    
    CheckFile(settings['FitDiagnostics_file'],True) 
    os.system('cd {outputdir}'.format(outputdir=settings['outputdir'])) 
    os.chdir("{outputdir}".format(outputdir=settings['outputdir']))
    workspace_root = os.path.basename(settings['workspace_root'])
    Log_Path = os.path.basename(settings['Log_Path'])

    command = "combine -M FitDiagnostics {workspace_root} --saveShapes -m {mass} --saveWithUncertainties -t -1 --expectSignal {expectSignal} -n _{year}_{channel}_{higgs}_{mass}_{coupling_value} --cminDefaultMinimizerStrategy 0 --rMin {rMin} --rMax {rMax}".format(workspace_root = workspace_root, year=settings['year'],channel=settings['channel'],higgs=settings['higgs'],mass=settings['mass'],coupling_value=settings['coupling_value'],expectSignal=settings['expectSignal'],rMin=settings['rMin'],rMax=settings['rMax'])

    print("\033[0;35m "+command+"\033[0;m\n")
    command = command + ' >& {Log_Path}'.format(Log_Path=Log_Path)
    os.system(command)
    #Status : MINIMIZE=0 HESSE=0

    #os.system('mv {FitDiagnostics_file} {outputdir}'.format(FitDiagnostics_file=FitDiagnostics_file,outputdir=settings['outputdir']))
    
    FitDiagnostics_file = settings['FitDiagnostics_file']
    
    print("A new FitDiagnostics file: \033[0;32m\033[4m{}\033[0;m is created! \n".format(FitDiagnostics_file))
    
    print("* Use the following commands to check whether the Status: \033[0;31m MINIMIZE=0 HESSE=0\033[0;m:\n")
    print("(1) \033[0;33m root -l \033[4m{FitDiagnostics_file}\033[0;m\n".format(FitDiagnostics_file=FitDiagnostics_file))
    print("(2) \033[0;33m fit_s->Print()\033[0;m\n")
    print("For more detailed information about FitDiagnostics : \033[0;34m\033[4mhttps://cms-analysis.github.io/HiggsAnalysis-CombinedLimit/part5/longexercise/#c-using-fitdiagnostics \033[0;m") 
    print("Before entering into the next mode, please check the log file.")
    
    print("\nNext mode: [\033[0;32m preFitPlot\033[0;m]")

def diffNuisances(settings=dict()):
    
    CheckFile(settings['diffNuisances_File'],True) 
    
    
    command = 'python diffNuisances.py {FitDiagnostics_file} --all -g {diffNuisances_File} --abs'.format(FitDiagnostics_file=settings['FitDiagnostics_file'],diffNuisances_File=settings['diffNuisances_File'])
    print("\033[0;35m "+command+"\033[0;m\n")
    
    command += ' >& {Log_Path}'.format(Log_Path=settings['Log_Path'])
    
    os.system(command)
    
    print("\033[0;34m* diffNuisances root file: \033[4m{}\033[0;m is created. ".format(settings['diffNuisances_File']))
    print("\nNext mode: [\033[0;32m PlotPulls \033[0;m]")


def PlotPulls(settings=dict()):
    if settings['year'] == 'run2':n_canvas = '100'
    elif settings['channel']  =='C':n_canvas ='20'
    else:n_canvas = '10'

    command = 'root -l -b -q '+"'PlotPulls.C"+'("{diffNuisances_File}","","_{year}_{channel}_{higgs}_{mass}_{coupling_value}",{n_canvas},"{year}")'.format(diffNuisances_File=settings['diffNuisances_File'],year=settings['year'],channel=settings['channel'],higgs=settings['higgs'],mass=settings['mass'],coupling_value=settings['coupling_value'],n_canvas=n_canvas)+"'"
    print("\033[0;35m"+command+"\033[0;m")

    command += ' >& {}'.format(settings['Log_Path'])
    os.system(command)
    os.system("mv {outputdir}/fitDiagnostics_* {outputdir}/results ".format(outputdir=settings['outputdir']))

    os.system("mv {outputdir}/diffNuisances_*_.* {outputdir}/results".format(outputdir=settings['outputdir']))
    print("\nNext mode: [\033[0;32m Impact_doInitFit \033[0;m]")
    print("\033[1;33m* Your pull plots and root files are moved under: \033[4m{}/results\033[0;m".format(settings['outputdir']))

def Impact_doInitFit(settings=dict()):
    
    print("cd {outputdir}".format(outputdir=settings['outputdir']))
    os.chdir(settings['outputdir'])
    CheckFile("higgsCombine_initialFit_Test.MultiDimFit.mH{mass}.root".format(mass= settings['mass']),True)
    CheckFile("combine_logger.out",True)
    workspace_root = os.path.basename(settings['workspace_root'])
    Log_Path = os.path.basename(settings['Log_Path'])

    command = 'combineTool.py -M Impacts -d {workspace_root} --doInitialFit --robustFit 1 -m {mass} -t -1 --expectSignal {expectSignal} --rMin {rMin} --rMax {rMax} '.format(workspace_root=workspace_root,mass=settings['mass'],expectSignal=settings['expectSignal'],rMin=settings['rMin'],rMax=settings['rMax'])
    print("\033[0;35m"+command+"\033[0;m")
    command += ' >& {}'.format(Log_Path)
    os.system(command) 
    print("\nNext mode: [\033[0;32m Impact_doFits \033[0;m]")
    print("\033[1;33m* Check the log file to find whether the [rMin, rMax] fall into specificied range, otherwise you need to reset --rMin/--rMax.\033[0;m") 



def Impact_doFits(settings=dict()):
    
    print("\033[0;35mcd {outputdir}\n\033[0;m".format(outputdir=settings['outputdir']))
    os.chdir(settings['outputdir'])
    
    workspace_root = os.path.basename(settings['workspace_root'])
    Log_Path = os.path.basename(settings['Log_Path'])
    
    
    command = 'combineTool.py -M Impacts -d {workspace_root} --doFits --robustFit 1 -m {mass} -t -1 --expectSignal {expectSignal} --rMin {rMin} --rMax {rMax} --job-mode condor --task-name {year}-{channel}-{coupling_value}-M{higgs}{mass} '.format(workspace_root=workspace_root,year=settings['year'],channel=settings['channel'],higgs=settings['higgs'],mass=settings['mass'],coupling_value=settings['coupling_value'],expectSignal=settings['expectSignal'],rMin=settings['rMin'],rMax=settings['rMax'])+'--sub-opts='+"'+JobFlavour="+'"testmatch"'+"'"
    
    print("\033[0;35m"+command+"\033[0;m")
    command += ' >& {}'.format(Log_Path)
    os.system(command) 

    print("\nNext mode: [\033[0;32m Plot_Impacts \033[1;33m]")
    print("\033[1;33m* You need to wait for the condor job is done, then move to the next step [Plot_Impacts]. \033[0;m")

def Plot_Impacts(settings=dict()):

    print("\033[0;35mcd {outputdir}\033[0;m -> Your current work directory".format(outputdir=settings['outputdir']))
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
    print("\033[0;35m"+command+"\n\n"+"\033[0;m")
    command += ' > {Log_Path}'.format(Log_Path=Log_Path)
    os.system(command)
   
    os.chdir('../')
    command = 'plotImpacts.py -i  {impacts_json} -o {impacts_json_prefix}'.format(impacts_json=settings['impacts_json'],impacts_json_prefix=settings['impacts_json'].replace(".json",""))
    
    print("\033[0;35m"+command+"\n\n"+"\033[0;m")
    command += ' >> {Log_Path}'.format(Log_Path=Log_Path)
    os.system(command)
    
    print("\n\033[0;31mTransforming 'pdf' to 'pdg'...\033[0;m")
    command = 'pdftoppm {impacts_json_prefix}.pdf {impacts_json_prefix} -png -rx 300 -ry 300'.format(impacts_json_prefix= settings['impacts_json'].replace(".json",""))
    print("\n\033[0;35m"+command+"\n"+"\033[0;m")
    
    os.system(command)    
    
    print("\033[1;33m* Please check \033[4m{impacts_json_prefix}.pdf\033[0;m".format(impacts_json_prefix=os.path.join(settings['outputdir'],settings['impacts_json'].replace(".json",""))))
    print("\033[1;33m* Your impact json file is : \033[4m{impacts_json_prefix}\033[0;m".format(impacts_json_prefix=os.path.join(settings['outputdir'],settings['impacts_json']))) 

def postFitPlot(settings=dict()):
    figDiagnostics_File = settings['FitDiagnostics_file']
    if CheckFile(figDiagnostics_File,False,False):pass
    else:
        FitDiagnostics_file_1 = 'results/fitDiagnostics_{year}_{channel}_{higgs}_{mass}_{coupling_value}.root'.format(year=settings['year'],channel=settings['channel'],higgs=settings['higgs'],mass=settings['mass'],coupling_value=settings['coupling_value'])
        figDiagnostics_File = os.path.join(settings['outputdir'],FitDiagnostics_file_1)
        if CheckFile(figDiagnostics_File,False,False):pass
        else: raise ValueError('\033[0;31mCheck :{figDiagnostics_File} exists or not. Otherwise you should go back to [FigDiagnostics_File] stage.'.format(figDiagnostics_File=figDiagnostics_File))



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
        if not settings['interference']:
            Histogram_Names.append("TAToTTQ_{coupling_value}_M{higgs}{mass}".format(coupling_value=settings['coupling_value'],higgs=settings['higgs'],mass=settings['mass']))
        else:
            Histogram_Names.append('TAToTTQ_{mass}_s_{mass2}_{coupling_value}'.format(coupling_value=settings['coupling_value'],higgs=settings['higgs'],mass=settings['mass'],mass2=settings['mass2']))
    else:
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
        print("\n\033[1;32mEnter {}\033[0;m".format(first_dir+second_dir))
        for Histogram_Name in Histogram_Names:
            #Histogram[Histogram_Name] = fin.Get(first_dir+second_dir+Histogram_Name).Clone()
            #print(first_dir+second_dir+Histogram_Name)
            h = fin.Get(first_dir+second_dir+Histogram_Name).Clone()
            nbin = h.GetNbinsX()
            h_reset_x_scale = ROOT.TH1F(first_dir+second_dir+Histogram_Name,first_dir+second_dir+Histogram_Name,nbin,-1,1)

            if type(h) != ROOT.TH1F:
                raise ValueError("\033[0;31mNo such histogram, please check {SampleName_File} and {figDiagnostics_File}\033[0;m".format(SampleName_File=SampleName_File,figDiagnostics_File=figDiagnostics_File))
            else:
                print("\033[1;32mAccess: {}\033[0;m".format(Histogram_Name))
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
            "mass":settings["mass"],
            "text_y":settings["text_y"]
            }
    if settings["expectSignal"]:
        if not settings['interference']:    
            template_settings["Signal_Name"] = "TAToTTQ_{coupling_value}_M{higgs}{mass}".format(coupling_value=settings['coupling_value'],higgs=settings['higgs'],mass=settings['mass'])
        else:
            
            template_settings["Signal_Name"] = 'TAToTTQ_{mass}_s_{mass2}_{coupling_value}'.format(coupling_value=settings['coupling_value'],higgs=settings['higgs'],mass=settings['mass'],mass2=settings['mass2'])
    else:
        template_settings["Signal_Name"] = "DEFAULT"
    print("\n")
    Plot_Histogram(template_settings=template_settings,expectSignal=settings["expectSignal"]) 


    #a = h_stack.GetXaxis();
    #a.ChangeLabel(1,-1,-1,-1,-1,-1,"-1");
    #a.ChangeLabel(-1,-1,-1,-1,-1,-1,"1");
    
    print("\nNext mode: \033[0;32m [diffNuisances] \033[1;33m")
    print("\033[1;33m* Please check \033[4m{prefix}.pdf\033[0;m".format(prefix=os.path.join(CURRENT_WORKDIR,os.path.join(settings['outputdir'],settings['postFitPlot']))))
    print("\033[1;33m* Please check \033[4m{prefix}.png\033[0;m".format(prefix=os.path.join(CURRENT_WORKDIR,os.path.join(settings['outputdir'],settings['postFitPlot']))))
    



def preFitPlot(settings=dict()):
    figDiagnostics_File = settings['FitDiagnostics_file']
    if CheckFile(figDiagnostics_File,False,False):pass
    else:
        FitDiagnostics_file_1 = 'results/fitDiagnostics_{year}_{channel}_{higgs}_{mass}_{coupling_value}.root'.format(year=settings['year'],channel=settings['channel'],higgs=settings['higgs'],mass=settings['mass'],coupling_value=settings['coupling_value'])
        figDiagnostics_File = os.path.join(settings['outputdir'],FitDiagnostics_file_1)
        if CheckFile(figDiagnostics_File,False,False):pass
        else: raise ValueError('\033[0;31m Check :{figDiagnostics_File} exists or not. Otherwise you should go back to \033[1m[FitDiagnostics] \033[0;m'.format(figDiagnostics_File=figDiagnostics_File))

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
        first_dir = 'shapes_prefit'
        #TAToTTQ_300_s_250_rtc04 -> Inteference sample
        if not settings['interference']:
            Histogram_Names.append("TAToTTQ_{coupling_value}_M{higgs}{mass}".format(coupling_value=settings['coupling_value'],higgs=settings['higgs'],mass=settings['mass']))
        else:
            Histogram_Names.append('TAToTTQ_{mass}_s_{mass2}_{coupling_value}'.format(coupling_value=settings['coupling_value'],higgs=settings['higgs'],mass=settings['mass'],mass2=settings['mass2']))
    else:
        first_dir = 'shapes_prefit'

    
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
        print("\n\033[1;32mEnter {}\033[0;m".format(first_dir+second_dir))
        for Histogram_Name in Histogram_Names:
            #Histogram[Histogram_Name] = fin.Get(first_dir+second_dir+Histogram_Name).Clone()
            #print(first_dir+second_dir+Histogram_Name)
            h = fin.Get(first_dir+second_dir+Histogram_Name)
            if type(h) != ROOT.TH1F:
                raise ValueError("\033[0;31m No such histogram, please check {SampleName_File} and {figDiagnostics_File} \033[0;m".format(SampleName_File=SampleName_File,figDiagnostics_File=figDiagnostics_File))

            else:
                h = fin.Get(first_dir+second_dir+Histogram_Name).Clone()
                nbin = h.GetNbinsX()
                h_reset_x_scale = ROOT.TH1F(first_dir+second_dir+Histogram_Name,first_dir+second_dir+Histogram_Name,nbin,-1,1)
                print("\033[1;32mAccess: {} \033[0;m ".format(Histogram_Name))
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
            "mass":settings["mass"],
            "text_y":settings["text_y"]
            } 
    if settings["expectSignal"]:
        if not settings['interference']:    
            template_settings["Signal_Name"] = "TAToTTQ_{coupling_value}_M{higgs}{mass}".format(coupling_value=settings['coupling_value'],higgs=settings['higgs'],mass=settings['mass'])
        else:
            
            template_settings["Signal_Name"] = 'TAToTTQ_{mass}_s_{mass2}_{coupling_value}'.format(coupling_value=settings['coupling_value'],higgs=settings['higgs'],mass=settings['mass'],mass2=settings['mass2'])
    else:
        template_settings["Signal_Name"] = "DEFAULT"
    Plot_Histogram(template_settings=template_settings,expectSignal=settings["expectSignal"]) 


    print("\nNext mode: \033[0;32m[postFitPlot]\033[1;m")
    print("\033[1;33m* Please check \033[4m{prefix}.pdf\033[0;m".format(prefix=os.path.join(CURRENT_WORKDIR,os.path.join(settings['outputdir'],settings['preFitPlot']))))
    print("\033[1;33m* Please check \033[4m{prefix}.png\033[0;m".format(prefix=os.path.join(CURRENT_WORKDIR,os.path.join(settings['outputdir'],settings['preFitPlot']))))




def Plot_Histogram(template_settings=dict(),expectSignal=False):

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
    if expectSignal:
        Color_Dict[template_settings["Signal_Name"]] = ROOT.kOrange
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
    h_sig =None
    for idx, Histogram_Name in enumerate(Ordered_Integral):
        if Histogram_Name == template_settings["Signal_Name"] and template_settings["Signal_Name"] != "DEFAULT":
            h_sig = template_settings['Histogram'][Histogram_Name]
            h_sig.SetLineColor(Color_Dict[Histogram_Name]) 
            h_sig.SetLineWidth(4)
            h_sig.SetLineStyle(9)
        else:    
            template_settings['Histogram'][Histogram_Name].SetFillColorAlpha(Color_Dict[Histogram_Name],0.65)
            #Histogram[Histogram_Name].Draw('HIST SAME')
            
            h_stack.Add(template_settings['Histogram'][Histogram_Name])
            legend.AddEntry(template_settings['Histogram'][Histogram_Name],Histogram_Name+' [{:.1f}]'.format(template_settings['Integral'][Histogram_Name]) , 'F')
    h_stack.SetTitle("Post-Fit Distribution;BDT score;Events/(1) ")
    h_stack.SetMaximum(template_settings['Maximum'] * Histogram_MaximumScale)
    h_stack.SetMinimum(1)
    h_stack.Draw("HIST")
    if type(h_sig )== ROOT.TH1F:
        h_sig.Scale(10)
        h_sig.Draw("HIST;SAME")
        legend.AddEntry(h_sig,'Signal(X 10)', 'L')
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
    latex.DrawLatex(.10,template_settings["text_y"],"#rho_{t%s} = %s"%(quark,value))
    latex.DrawLatex(.5,template_settings["text_y"],"M_{A} = %s "%(template_settings['mass']))
    latex.DrawLatex(-.4,template_settings["text_y"],"Channel: {}".format(template_settings['channel']))
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


def ResultsCopy(settings=dict()):
    
    
    CheckDir(settings['outputdir']) # Check your current output directory exists or not 
    
    ### Check your ongoing output directory exists or not ###
    if not CheckDir(settings['dest'],False):
        raise ValueError("Please check \033[0;31m{dest}\033[0;m exists".format(dest=settings['dest']))
    else:
        pass
    
    #########################################################
    Dest = os.path.join(settings['dest'],settings['outputdir'])
    CheckDir(Dest,True)

    print("Start to copy the folder: \033[0;32m\033[4m{origin}\033[0;m to destination: \033[1;33m\033[4m{dest}\033[0;m".format(origin=settings['outputdir'],dest=Dest))
    
    print("\ncp -r \033[1;32m{origin}/* \033[1;33m{dest}\033[0;m/\033[1;32m{origin}\033[0;m".format(origin = settings['outputdir'],dest=settings['dest']))
    
    command = "cp -r {origin}/* {dest}/{origin}".format(origin= settings['outputdir'],dest= settings['dest'])
    os.system(command) 

