import os 
import sys
import time
import ROOT
import json
CURRENT_WORKDIR = os.getcwd()
sys.path.append(CURRENT_WORKDIR)
ROOT.gROOT.SetBatch(ROOT.kTRUE)
from Util.General_Tool import CheckDir,CheckFile,CheckFile,binning
from collections import OrderedDict
from operator import itemgetter
from Util.aux import *


#from Util.OverlappingPlots import *
def CheckAndExec(MODE,datacards,mode='',settings=dict()):
    
    #Check And Create Folder: SignalExtraction
    start = time.time()
    date = os.popen("date").read()
    print("\033[1;37m{date}\033[0;m".format(date=date))

    Fit_type = ''
    if settings['prefix'] != None:
        Fit_type = settings['prefix']+"_"+Fit_type
    else:
        Fit_type =''

    if settings['unblind']:
        Fit_type += 'Unblind'
    else:
        if settings['expectSignal']:
            Fit_type+='s_plus_b'
            settings['expectSignal']= 1
        else:
            Fit_type+='b_only'
            settings['expectSignal']= 0
    
        
    CheckDir(os.path.join(settings['outdir'],"SignalExtraction/{year}/{channel}/{coupling_values}/{higgs}/{mass}/".format(year=settings['year'],channel=settings['channel'],coupling_values=settings['coupling_value'],mass=settings['mass'],higgs=settings['higgs'])),False)
    
    
    CheckDir(os.path.join(settings['outdir'],"SignalExtraction"),True)
    CheckDir(os.path.join(settings['outdir'],"SignalExtraction/{year}".format(year=settings['year'])),True)
    CheckDir(os.path.join(settings['outdir'],"SignalExtraction/{year}/{channel}".format(year=settings['year'],channel=settings['channel'])),True)
    CheckDir(os.path.join(settings['outdir'],"SignalExtraction/{year}/{channel}/{coupling_values}".format(year=settings['year'],channel=settings['channel'],coupling_values=settings['coupling_value'])),True)
    CheckDir(os.path.join(settings['outdir'],"SignalExtraction/{year}/{channel}/{coupling_values}/{higgs}".format(year=settings['year'],channel=settings['channel'],coupling_values=settings['coupling_value'],higgs=settings['higgs'])),True)
    CheckDir(os.path.join(settings['outdir'],"SignalExtraction/{year}/{channel}/{coupling_values}/{higgs}/{mass}/".format(year=settings['year'],channel=settings['channel'],coupling_values=settings['coupling_value'],mass=settings['mass'],higgs=settings['higgs'])),True)
    CheckDir(os.path.join(settings['outdir'],"SignalExtraction/{year}/{channel}/{coupling_values}/{higgs}/{mass}/{Fit_type}".format(year=settings['year'],channel=settings['channel'],coupling_values=settings['coupling_value'],higgs=settings['higgs'],Fit_type=Fit_type,mass=settings['mass'])),True)
    CheckDir(os.path.join(settings['outdir'],"SignalExtraction/{year}/{channel}/{coupling_values}/{higgs}/{mass}/{Fit_type}/err".format(year=settings['year'],channel=settings['channel'],coupling_values=settings['coupling_value'],higgs=settings['higgs'],Fit_type=Fit_type,mass=settings['mass'])),True)
    CheckDir(os.path.join(settings['outdir'],"SignalExtraction/{year}/{channel}/{coupling_values}/{higgs}/{mass}/{Fit_type}/output".format(year=settings['year'],channel=settings['channel'],coupling_values=settings['coupling_value'],higgs=settings['higgs'],Fit_type=Fit_type,mass=settings['mass'])),True)
    CheckDir(os.path.join(settings['outdir'],"SignalExtraction/{year}/{channel}/{coupling_values}/{higgs}/{mass}/{Fit_type}/log_condor".format(year=settings['year'],channel=settings['channel'],coupling_values=settings['coupling_value'],higgs=settings['higgs'],Fit_type=Fit_type,mass=settings['mass'])),True)
    CheckDir(os.path.join(settings['outdir'],"SignalExtraction/{year}/{channel}/{coupling_values}/{higgs}/{mass}/{Fit_type}/results".format(year=settings['year'],channel=settings['channel'],coupling_values=settings['coupling_value'],higgs=settings['higgs'],Fit_type=Fit_type,mass=settings['mass'])),True)
    CheckDir(os.path.join(settings['outdir'],"SignalExtraction/{year}/{channel}/{coupling_values}/{higgs}/{mass}/{Fit_type}/root".format(year=settings['year'],channel=settings['channel'],coupling_values=settings['coupling_value'],higgs=settings['higgs'],Fit_type=Fit_type,mass=settings['mass'])),True)


    Final_Output_Dir = os.path.join(settings['outdir'],"SignalExtraction/{year}/{channel}/{coupling_values}/{higgs}/{mass}/{Fit_type}".format(year=settings['year'],channel=settings['channel'],coupling_values=settings['coupling_value'],higgs=settings['higgs'],Fit_type=Fit_type,mass=settings['mass']))

    settings['outputdir'] = Final_Output_Dir
    settings['WorkDir'] = CURRENT_WORKDIR
    settings['condorDir'] = os.path.join(settings['WorkDir'],"SignalExtraction/{year}/{channel}/{coupling_values}/{higgs}/{mass}/{Fit_type}".format(year=settings['year'],channel=settings['channel'],coupling_values=settings['coupling_value'],higgs=settings['higgs'],Fit_type=Fit_type,mass=settings['mass']))
    
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
    settings['plotNLLcode'] = os.path.join(settings['WorkDir'],'../../CombineHarvester/CombineTools/scripts/plot1DScan.py')

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
    

    if settings['unblind']:
        command = "combine -M FitDiagnostics {workspace_root} --saveShapes -m {mass} --saveWithUncertainties  --saveOverallShapes  -n _{year}_{channel}_{higgs}_{mass}_{coupling_value} --cminDefaultMinimizerStrategy {cminDefaultMinimizerStrategy} --cminDefaultMinimizerTolerance={cminDefaultMinimizerTolerance} --rMin {rMin} --rMax {rMax}".format(workspace_root = workspace_root, year=settings['year'],channel=settings['channel'],higgs=settings['higgs'],mass=settings['mass'],coupling_value=settings['coupling_value'],rMin=settings['rMin'],rMax=settings['rMax'],  cminDefaultMinimizerStrategy=settings['cminDefaultMinimizerStrategy'], cminDefaultMinimizerTolerance=settings['cminDefaultMinimizerTolerance'])
    else: 
        command = "combine -M FitDiagnostics {workspace_root} --saveShapes -m {mass} --saveWithUncertainties --saveOverallShapes -t -1 --expectSignal {expectSignal} -n _{year}_{channel}_{higgs}_{mass}_{coupling_value} --cminDefaultMinimizerStrategy {cminDefaultMinimizerStrategy} --cminDefaultMinimizerTolerance={cminDefaultMinimizerTolerance} --rMin {rMin} --rMax {rMax}".format(workspace_root = workspace_root, year=settings['year'],channel=settings['channel'],higgs=settings['higgs'],mass=settings['mass'],coupling_value=settings['coupling_value'],expectSignal=settings['expectSignal'],rMin=settings['rMin'],rMax=settings['rMax'],  cminDefaultMinimizerStrategy=settings['cminDefaultMinimizerStrategy'], cminDefaultMinimizerTolerance=settings['cminDefaultMinimizerTolerance'])

    print(ts+command+ns)
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
    print(ts+command+ns)
    command += ' >& {Log_Path}'.format(Log_Path=settings['Log_Path'])
    
    os.system(command)
    
    print("\033[0;34m* diffNuisances root file: \033[4m{}\033[0;m is created. ".format(settings['diffNuisances_File']))
    print("\nNext mode: [\033[0;32m PlotPulls \033[0;m]")


def PlotPulls(settings=dict()):
    if settings['year'] == 'run2':n_canvas = '100'
    elif settings['channel']  =='C':n_canvas ='20'
    else:n_canvas = '10'

    command = 'root -l -b -q '+"'PlotPulls.C"+'("{diffNuisances_File}","","_{year}_{channel}_{higgs}_{mass}_{coupling_value}",{n_canvas},"{year}")'.format(diffNuisances_File=settings['diffNuisances_File'],year=settings['year'],channel=settings['channel'],higgs=settings['higgs'],mass=settings['mass'],coupling_value=settings['coupling_value'],n_canvas=n_canvas)+"'"
    print(ts+command+ns)

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

    if settings['unblind']:
        print (hs + "**Unbliding IMPACT command**"+ ns)
        command = 'combineTool.py -M Impacts -d {workspace_root} --doInitialFit --robustFit 1 -m {mass}  --rMin {rMin} --rMax {rMax} --cminDefaultMinimizerStrategy {cminDefaultMinimizerStrategy} --cminDefaultMinimizerTolerance={cminDefaultMinimizerTolerance}'.format(workspace_root=workspace_root,mass=settings['mass'],rMin=settings['rMin'],rMax=settings['rMax'], cminDefaultMinimizerStrategy=settings['cminDefaultMinimizerStrategy'], cminDefaultMinimizerTolerance=settings['cminDefaultMinimizerTolerance'])
    else:
        command = 'combineTool.py -M Impacts -d {workspace_root} --doInitialFit --robustFit 1 -m {mass} -t -1 --expectSignal {expectSignal} --rMin {rMin} --rMax {rMax} --cminDefaultMinimizerStrategy {cminDefaultMinimizerStrategy} --cminDefaultMinimizerTolerance={cminDefaultMinimizerTolerance}'.format(workspace_root=workspace_root,mass=settings['mass'],expectSignal=settings['expectSignal'],rMin=settings['rMin'],rMax=settings['rMax'], cminDefaultMinimizerStrategy=settings['cminDefaultMinimizerStrategy'], cminDefaultMinimizerTolerance=settings['cminDefaultMinimizerTolerance'])

    print(ts+command+ns)
    command += ' >& {}'.format(Log_Path)
    os.system(command) 
    print("\nNext mode: [\033[0;32m Impact_doFits \033[0;m]")
    print("\033[1;33m* Check the log file to find whether the [rMin, rMax] fall into specificied range, otherwise you need to reset --rMin/--rMax.\033[0;m") 



def Impact_doFits(settings=dict()):
    
    print("\033[0;35mcd {outputdir}\n\033[0;m".format(outputdir=settings['outputdir']))
    os.chdir(settings['outputdir'])
    
    workspace_root = os.path.basename(settings['workspace_root'])
    Log_Path = os.path.basename(settings['Log_Path'])
    
    if settings['unblind']:
        print (hs + "**Unbliding IMPACT command**"+ ns)
        command = 'combineTool.py -M Impacts -d {workspace_root} --doFits --robustFit 1 -m {mass} --rMin {rMin} --rMax {rMax} --cminDefaultMinimizerStrategy {cminDefaultMinimizerStrategy} --cminDefaultMinimizerTolerance={cminDefaultMinimizerTolerance} --job-mode condor --task-name {year}-{channel}-{coupling_value}-M{higgs}{mass} '.format(workspace_root=workspace_root,year=settings['year'],channel=settings['channel'],higgs=settings['higgs'],mass=settings['mass'],coupling_value=settings['coupling_value'],rMin=settings['rMin'],rMax=settings['rMax'], cminDefaultMinimizerStrategy=settings['cminDefaultMinimizerStrategy'], cminDefaultMinimizerTolerance=settings['cminDefaultMinimizerTolerance'])+'--sub-opts='+"'+JobFlavour="+'"tomorrow"'+"'"
    else:
        command = 'combineTool.py -M Impacts -d {workspace_root} --doFits --robustFit 1 -m {mass} -t -1 --expectSignal {expectSignal} --rMin {rMin} --rMax {rMax} --cminDefaultMinimizerStrategy {cminDefaultMinimizerStrategy} --cminDefaultMinimizerTolerance={cminDefaultMinimizerTolerance} --job-mode condor --task-name {year}-{channel}-{coupling_value}-M{higgs}{mass} '.format(workspace_root=workspace_root,year=settings['year'],channel=settings['channel'],higgs=settings['higgs'],mass=settings['mass'],coupling_value=settings['coupling_value'],expectSignal=settings['expectSignal'],rMin=settings['rMin'],rMax=settings['rMax'], cminDefaultMinimizerStrategy=settings['cminDefaultMinimizerStrategy'], cminDefaultMinimizerTolerance=settings['cminDefaultMinimizerTolerance'])+'--sub-opts='+"'+JobFlavour="+'"tomorrow"'+"'"

    print(ts+command+ns)
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
    print(ts+command+ns)
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
    if settings['unblind']:
        Histogram_Names.append('data')

    fin = ROOT.TFile(figDiagnostics_File,"READ")
    
    if settings['expectSignal'] or settings['unblind']:
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

            if type(h) != ROOT.TH1F:
                if settings['unblind'] and Histogram_Name =='data':
                    data_higComb = h
                    data = ROOT.TH1F('data', '', len(binning)-1,binning)
                    
                    for bini in range(data.GetSize()):
                        tgraph_content = data_higComb.Eval(bini+0.5) # must fit the center of the bin in tgraph
                        tgraph_error   = data_higComb.GetErrorY(bini+1) # just symmetrical error
                        data.SetBinContent (bini+1, tgraph_content)
                        data.SetBinError   (bini+1, tgraph_error)

                    if Histogram_Registered:
                      Integral[Histogram_Name]+= int(data.Integral())
                    else:
                      Integral[Histogram_Name] = int(data.Integral())
                    if Histogram_Registered:
                      Histogram[Histogram_Name].Add(data)
                    else:
                      Histogram[Histogram_Name] = data
                else:
                    print(first_dir+second_dir+Histogram_Name)
                    raise ValueError("\033[0;31mNo such histogram, please check {SampleName_File} and {figDiagnostics_File}\033[0;m".format(SampleName_File=SampleName_File,figDiagnostics_File=figDiagnostics_File))
            else:
                print("\033[1;32mAccess: {}\033[0;m".format(Histogram_Name))
                nbin = h.GetNbinsX()
                h_reset_x_scale = ROOT.TH1F(first_dir+second_dir+Histogram_Name,first_dir+second_dir+Histogram_Name,len(binning)-1,binning)
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
            "text_y":settings["text_y"],
            "logy":settings["logy"],
            "unblind":settings['unblind'],
            "expectSignal":settings['expectSignal']
            }
    if settings["unblind"] or settings["expectSignal"]:
        if not settings['interference']:    
            template_settings["Signal_Name"] = "TAToTTQ_{coupling_value}_M{higgs}{mass}".format(coupling_value=settings['coupling_value'],higgs=settings['higgs'],mass=settings['mass'])
        else:
                
            template_settings["Signal_Name"] = 'TAToTTQ_{mass}_s_{mass2}_{coupling_value}'.format(coupling_value=settings['coupling_value'],higgs=settings['higgs'],mass=settings['mass'],mass2=settings['mass2'])
    else:
            template_settings["Signal_Name"] = "DEFAULT"
    print("\n")
    Plot_Histogram(template_settings=template_settings) 


    #a = h_stack.GetXaxis();
    #a.ChangeLabel(1,-1,-1,-1,-1,-1,"-1");
    #a.ChangeLabel(-1,-1,-1,-1,-1,-1,"1");

    if settings["logy"]:
      log_tag = "_log"
    else:
      log_tag = ""

    print("\nNext mode: \033[0;32m [diffNuisances] \033[1;33m")
    print("\033[1;33m* Please check \033[4m{prefix}{log}.pdf\033[0;m".format(prefix=os.path.join(CURRENT_WORKDIR,os.path.join(settings['outputdir'],settings['postFitPlot'])),log=log_tag))
    print("\033[1;33m* Please check \033[4m{prefix}{log}.png\033[0;m".format(prefix=os.path.join(CURRENT_WORKDIR,os.path.join(settings['outputdir'],settings['postFitPlot'])),log=log_tag))

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
    if settings['unblind']:
        Histogram_Names.append('data')

    Histogram = dict()
    Integral= dict()
    Maximum = -1
    fin = ROOT.TFile(figDiagnostics_File,"READ")

    Histogram = dict()
    if settings['unblind']:
        first_dir = 'shapes_prefit'
        if not settings['interference']:
            Histogram_Names.append("TAToTTQ_{coupling_value}_M{higgs}{mass}".format(coupling_value=settings['coupling_value'],higgs=settings['higgs'],mass=settings['mass']))
        else:
            Histogram_Names.append('TAToTTQ_{mass}_s_{mass2}_{coupling_value}'.format(coupling_value=settings['coupling_value'],higgs=settings['higgs'],mass=settings['mass'],mass2=settings['mass2']))

    else:
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
                if settings['unblind'] and Histogram_Name =='data':
                    data_higComb = h
                    data = ROOT.TH1F('data', '', len(binning)-1, binning)
                    
                    for bini in range(data.GetNbinsX()):
                        tgraph_content = data_higComb.Eval(bini+0.5) # must fit the center of the bin in tgraph
                        tgraph_error   = data_higComb.GetErrorY(bini+1) # just symmetrical error
                        data.SetBinContent (bini+1, tgraph_content)
                        data.SetBinError   (bini+1, tgraph_error)

                    if Histogram_Registered:
                      Integral[Histogram_Name]+= int(data.Integral())
                    else:
                      Integral[Histogram_Name] = int(data.Integral())
                    if Histogram_Registered:
                      Histogram[Histogram_Name].Add(data)
                    else:
                      Histogram[Histogram_Name] = data

                else:
                    print(first_dir+second_dir+Histogram_Name)
                    raise ValueError("\033[0;31m No such histogram, please check {SampleName_File} and {figDiagnostics_File} \033[0;m".format(SampleName_File=SampleName_File,figDiagnostics_File=figDiagnostics_File))

            else:
                h = fin.Get(first_dir+second_dir+Histogram_Name).Clone()
                nbin = h.GetNbinsX()
                if not (nbin == len(binning)-1):
                  raise ValueError("\033[0;31m Input binning is not consistent with local binning setting. Please check binning in Util/General_Tool.py \033[0;m")
                h_reset_x_scale = ROOT.TH1F(first_dir+second_dir+Histogram_Name,first_dir+second_dir+Histogram_Name,len(binning)-1, binning)
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
            "text_y":settings["text_y"],
            "logy":settings["logy"],
            "unblind":settings["unblind"],
            "expectSignal":settings["expectSignal"]
            } 
    if settings["expectSignal"] or settings["unblind"]:
        if not settings['interference']:    
            template_settings["Signal_Name"] = "TAToTTQ_{coupling_value}_M{higgs}{mass}".format(coupling_value=settings['coupling_value'],higgs=settings['higgs'],mass=settings['mass'])
        else:                
            template_settings["Signal_Name"] = 'TAToTTQ_{mass}_s_{mass2}_{coupling_value}'.format(coupling_value=settings['coupling_value'],higgs=settings['higgs'],mass=settings['mass'],mass2=settings['mass2'])
    else:
            template_settings["Signal_Name"] = "DEFAULT"
    Plot_Histogram(template_settings=template_settings) 
    
    if settings["logy"]:
      log_tag = "_log"
    else:
      log_tag = ""

    print("\nNext mode: \033[0;32m[postFitPlot]\033[1;m")
    print("\033[1;33m* Please check \033[4m{prefix}{log}.pdf\033[0;m".format(prefix=os.path.join(CURRENT_WORKDIR,os.path.join(settings['outputdir'],settings['preFitPlot'])),log=log_tag))
    print("\033[1;33m* Please check \033[4m{prefix}{log}.png\033[0;m".format(prefix=os.path.join(CURRENT_WORKDIR,os.path.join(settings['outputdir'],settings['preFitPlot'])),log=log_tag))




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
            'ttH':ROOT.kRed-9,
            'ttVV':ROOT.kOrange+3,
            'SingleTop':ROOT.kGray,
            'Others': ROOT.kYellow-4,
            }
    if template_settings["unblind"]:
        Color_Dict['data'] = ROOT.kBlack
    if template_settings["unblind"] or template_settings["expectSignal"]:
        Color_Dict[template_settings["Signal_Name"]] = ROOT.kOrange
    for Histogram_Name in template_settings['Histogram'].keys():
        if Histogram_Name not in Color_Dict.keys():
            raise ValueError("Make sure {} in Color_Dict.keys()".format(Histogram_Name)) 

    #### Canvas ####
    ROOT.gStyle.SetOptTitle(0)
    ROOT.gStyle.SetOptStat(0)
    ROOT.gROOT.SetBatch(1)
    canvas = ROOT.TCanvas("","",620,600)

    Set_Logy = template_settings['logy']

    if Set_Logy:
        canvas.SetLogy(1)
        Histogram_MaximumScale = 1000
    else:
        Histogram_MaximumScale = 1.5
    canvas.SetGrid(1,1)
    canvas.SetLeftMargin(0.12)
    canvas.SetRightMargin(0.08)
    ###############

    #### Legend ####
    legend_NCol = int(len(Color_Dict.keys())/5)
    legend = ROOT.TLegend(.15, .65, .15+0.37*(legend_NCol-1), .890);
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
            if Histogram_Name == 'data':
                if template_settings['unblind']:
                    legend.AddEntry(template_settings['Histogram'][Histogram_Name],Histogram_Name+' [{:02d}]'.format(template_settings['Integral'][Histogram_Name]) , 'PE')
                    template_settings['Histogram'][Histogram_Name].SetMarkerStyle(8)
                    template_settings['Histogram'][Histogram_Name].SetMarkerColor(1)
                    template_settings['Histogram'][Histogram_Name].SetLineWidth(2)
            else:
                template_settings['Histogram'][Histogram_Name].SetFillColorAlpha(Color_Dict[Histogram_Name],0.65)
                h_stack.Add(template_settings['Histogram'][Histogram_Name])
                legend.AddEntry(template_settings['Histogram'][Histogram_Name],Histogram_Name+' [{:.1f}]'.format(template_settings['Integral'][Histogram_Name]) , 'F')
    h_stack.SetTitle("Post-Fit Distribution;BDT score;Events/(1) ")
    h_stack.SetMaximum(template_settings['Maximum'] * Histogram_MaximumScale)
    h_stack.SetMinimum(0.1)
    h_stack.Draw("HIST")
    if template_settings['unblind']:
        template_settings['Histogram']["data"].Draw("SAME P*")
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
    #latex.DrawLatex(.10,template_settings["text_y"],"#rho_{t%s} = %s"%(quark,value))
    #latex.DrawLatex(.5,template_settings["text_y"],"M_{A} = %s "%(template_settings['mass']))
    #latex.DrawLatex(-.4,template_settings["text_y"],"Channel: {}".format(template_settings['channel']))
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
    if Set_Logy:
      log_tag = "_log"
    else:
      log_tag = ""
    canvas.Update()
    canvas.SaveAs('{prefix}{log}.pdf'.format(prefix=template_settings['outputfilename'],log=log_tag))
    canvas.SaveAs('{prefix}{log}.png'.format(prefix=template_settings['outputfilename'],log=log_tag))


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

def SubmitFromEOS(settings=dict()):

  CheckDir(settings['condorDir'])
  command = "cp {origin}/*.s* {dest}/.".format(origin = settings['outputdir'], dest = settings['condorDir'])
  os.system(command)
  for f in os.listdir(settings['condorDir']):
    if 'sub' in f:
      os.chdir("{dest}".format(dest = settings['condorDir']))
      os.system("condor_submit {submit_file}".format(submit_file = f))
      os.chdir("{dest}".format(dest = settings['WorkDir']))

def DrawNLL(settings=dict()):
  os.system('cd {outputdir}'.format(outputdir=settings['outputdir'])) 
  os.chdir(settings['outputdir'])
  workspace_root = os.path.basename(settings['workspace_root'])
  Log_Path = os.path.basename(settings['Log_Path'])
  commands = []
  rMin = -4
  rMax = 4
  points = 80
  if settings['unblind']:
    commands.append("combine -M MultiDimFit {workspace_root} -m {mass} -n _{year}_{channel}_{higgs}_{mass}_{coupling_value}.DrawNLL --rMin {rMin} --rMax {rMax} --cminDefaultMinimizerStrategy {cminDefaultMinimizerStrategy} --cminDefaultMinimizerTolerance={cminDefaultMinimizerTolerance} --algo grid --points {points}".format(workspace_root=workspace_root,year=settings['year'],channel=settings['channel'],higgs=settings['higgs'],mass=settings['mass'],coupling_value=settings['coupling_value'],rMin=rMin,rMax=rMax,points=points, cminDefaultMinimizerStrategy=settings['cminDefaultMinimizerStrategy'], cminDefaultMinimizerTolerance=settings['cminDefaultMinimizerTolerance']))
    commands.append("combine -M MultiDimFit {workspace_root} -m {mass} -n _{year}_{channel}_{higgs}_{mass}_{coupling_value}.snapshot --rMin {rMin} --rMax {rMax} --cminDefaultMinimizerStrategy {cminDefaultMinimizerStrategy} --cminDefaultMinimizerTolerance={cminDefaultMinimizerTolerance} --saveWorkspace".format(workspace_root=workspace_root,year=settings['year'],channel=settings['channel'],higgs=settings['higgs'],mass=settings['mass'],coupling_value=settings['coupling_value'],rMin=rMin,rMax=rMax,cminDefaultMinimizerStrategy=settings['cminDefaultMinimizerStrategy'], cminDefaultMinimizerTolerance=settings['cminDefaultMinimizerTolerance']))
    commands.append("combine -M MultiDimFit higgsCombine_{year}_{channel}_{higgs}_{mass}_{coupling_value}.snapshot.MultiDimFit.mH{mass}.root -m {mass} -n _{year}_{channel}_{higgs}_{mass}_{coupling_value}.freezeAll --rMin {rMin} --rMax {rMax} --cminDefaultMinimizerStrategy {cminDefaultMinimizerStrategy} --cminDefaultMinimizerTolerance={cminDefaultMinimizerTolerance} --algo grid --points {points} --freezeParameters allConstrainedNuisances --snapshotName MultiDimFit".format(year=settings['year'],channel=settings['channel'],higgs=settings['higgs'],mass=settings['mass'],coupling_value=settings['coupling_value'],rMin=rMin,rMax=rMax,points=points,cminDefaultMinimizerStrategy=settings['cminDefaultMinimizerStrategy'], cminDefaultMinimizerTolerance=settings['cminDefaultMinimizerTolerance']))
    commands.append("python {plotNLLcode} higgsCombine_{year}_{channel}_{higgs}_{mass}_{coupling_value}.DrawNLL.MultiDimFit.mH{mass}.root --others 'higgsCombine_{year}_{channel}_{higgs}_{mass}_{coupling_value}.freezeAll.MultiDimFit.mH{mass}.root:FreezeAll:2' -o results/POI_NLL --breakdown Syst,Stat".format(year=settings['year'],channel=settings['channel'],higgs=settings['higgs'],mass=settings['mass'],coupling_value=settings['coupling_value'],plotNLLcode=settings['plotNLLcode']))
    commands.append("combineTool.py -M FastScan -w {workspace_root}:w".format(workspace_root=workspace_root))
    commands.append("mv nll.pdf results/Nuisance_NLL.pdf")
    for i in range(len(commands)):
      print(ts+commands[i]+ns)
      if i == 0:
        commands[i] = commands[i] + ' &> {Log_Path}'.format(Log_Path=Log_Path)
      else:
        commands[i] = commands[i] + ' &>> {Log_Path}'.format(Log_Path=Log_Path)
    command = ';'.join(commands)
    os.system(command)
  else:
    print("Do not have blind option now")

