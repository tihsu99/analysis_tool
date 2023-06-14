import os 
import sys
import time
import ROOT
import json
import math
import matplotlib.pyplot as plt
CURRENT_WORKDIR = os.getcwd()
sys.path.append(CURRENT_WORKDIR)
ROOT.gROOT.SetBatch(ROOT.kTRUE)
from Util.General_Tool import CheckDir,CheckFile,CheckFile,binning
from collections import OrderedDict
from operator import itemgetter
from Util.aux import *
import numpy as np
import ctypes
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
    settings['FitDiagnostics_file'] = os.path.join(settings['outputdir'],'results/'+FitDiagnostics_file)
    settings['diffNuisances_File'] = diffNuisances_File 
    settings['impacts_json'] = impacts_json
    settings['shapePlot'] = 'results/{}_{}'.format(settings['shape_type'],settings['channel'])
    settings['plotNLLcode'] = os.path.join(settings['WorkDir'],'../../CombineHarvester/CombineTools/scripts/plot1DScan.py')

    if mode == 'PlotShape' or mode == "PlotPulls" or mode=="Plot_Impacts" or mode =="ResultsCopy":
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
    
    if settings['correlation']:
        command += ' --plots '
        print('Correlation Matrix will be saved in the FitDiagnostics root file...')
    
    if settings['saveNormalizations']:
        command += ' --saveNormalizations '
        print('[saveNormalizations] is applied in the FigDiagnostics stage ')
    print(ts+command+ns)
    command = command + ' >& {Log_Path}'.format(Log_Path=Log_Path)
    os.system(command)
    #Status : MINIMIZE=0 HESSE=0

    #os.system('mv {FitDiagnostics_file} {outputdir}'.format(FitDiagnostics_file=FitDiagnostics_file,outputdir=settings['outputdir']))
    
    os.system('mv ./fitDiagnostics* ./results')
    FitDiagnostics_file = settings['FitDiagnostics_file']
    
    print("A new FitDiagnostics file: \033[0;32m\033[4m{}\033[0;m is created! \n".format(FitDiagnostics_file))
    
    print("* Use the following commands to check whether the Status: \033[0;31m MINIMIZE=0 HESSE=0\033[0;m:\n")
    print("(1) \033[0;33m root -l \033[4m{FitDiagnostics_file}\033[0;m\n".format(FitDiagnostics_file=FitDiagnostics_file))
    print("(2) \033[0;33m fit_s->Print()\033[0;m\n")
    print("For more detailed information about FitDiagnostics : \033[0;34m\033[4mhttps://cms-analysis.github.io/HiggsAnalysis-CombinedLimit/part5/longexercise/#c-using-fitdiagnostics \033[0;m") 
    print("Before entering into the next mode, please check the log file.")
    
    print("\nNext mode: [\033[0;32m FinalYieldComputation\033[0;m]")

def diffNuisances(settings=dict()):
    
    CheckFile(settings['diffNuisances_File'],True) 
    
    
    command = 'python diffNuisances.py {FitDiagnostics_file} --all -g {diffNuisances_File} --abs'.format(FitDiagnostics_file=settings['FitDiagnostics_file'],diffNuisances_File=settings['diffNuisances_File'])
    print(ts+command+ns)
    command += ' >& {Log_Path}'.format(Log_Path=settings['Log_Path'])
    
    os.system(command)
    
    print("\033[0;34m* diffNuisances root file: \033[4m{}\033[0;m is created. ".format(settings['diffNuisances_File']))
    print("\nNext mode: [\033[0;32m PlotPulls \033[0;m]")


def PlotPulls(settings=dict()):
    if settings['year'] == 'run2':n_canvas = '15'
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
    # safety check:
    if not os.path.isfile(workspace_root):
      raise Exception("First run: --mode datacard2workspace step")
    
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
    
    print("\n\033[0;31mTransforming 'pdf' to 'png'...\033[0;m")
    command = 'pdftoppm {impacts_json_prefix}.pdf {impacts_json_prefix} -png -rx 300 -ry 300'.format(impacts_json_prefix= settings['impacts_json'].replace(".json",""))
    print("\n\033[0;35m"+command+"\n"+"\033[0;m")
    
    os.system(command)    
    
    print("\033[1;33m* Please check \033[4m{impacts_json_prefix}.pdf\033[0;m".format(impacts_json_prefix=os.path.join(settings['outputdir'],settings['impacts_json'].replace(".json",""))))
    print("\033[1;33m* Your impact json file is : \033[4m{impacts_json_prefix}\033[0;m".format(impacts_json_prefix=os.path.join(settings['outputdir'],settings['impacts_json']))) 

def PlotShape(settings=dict()):
    
    if settings['shape_type'].lower() == 'postfit':
        outputFile = os.path.join(settings['outputdir'], 'results/PostFitShapesFromWorkspace_output_.root')
    else:
        outputFile = settings['FitDiagnostics_file']
    
    if CheckFile(outputFile,False,False):pass
    else:
        raise ValueError('\033[0;31mCheck :{outputFile} exists or not.'.format(outputFile = outputFile))




    FileIn = ROOT.TFile(outputFile,"READ")
    Histogram_Names = []
    RootLevel = FileIn
    if settings['shape_type'].lower() == 'prefit':
        RootLevel = FileIn.Get('shapes_prefit')
        #RootLevel.cd()
    ## This part is only for creating the keys which corresponds to category defintion 
    for first_level in RootLevel.GetListOfKeys():
        first_level_name = first_level.GetName()
        if type(RootLevel.Get(first_level_name)) !=  ROOT.TDirectoryFile: continue

        for second_level in RootLevel.Get(first_level_name).GetListOfKeys():
            category = second_level.GetName() 
            if category == 'data_obs' or category == 'data': category = 'Data'
            Histogram_Names.append(category)
        break
    
    Histogram = dict()
    Integral= dict()

    for category in Histogram_Names:
        if ('TotalSig' in category) or  ('TotalProcs' in category):continue #In PostFitWorkspace
        if ('total_overall' in category) or ('total_signal' in category) or ('total' == category) or ('overall_total_covar' in category) or ('total_covar' in category): continue #In Fitdiagnostics
        if category == 'data_obs': category = 'Data' # In PostFitWorkspace, for postFit
        
        if category == 'data': #For preFit 
            category = 'Data' # In FitDiagnostics
        elif category == 'total_background':
            category = 'TotalBkg' 
        Histogram[category] = ROOT.TH1F(category, '', len(binning) - 1, binning) 
        Integral[category] = 0
    
    Maximum = -1
    Histogram_Registered = False 
    for first_level in RootLevel.GetListOfKeys():
        first_level_name = first_level.GetName()
        if not(settings['shape_type'].lower() in first_level_name) and settings['shape_type'].lower() == 'postfit': 
            continue
        if type(RootLevel.Get(first_level_name)) !=  ROOT.TDirectoryFile: continue
        
        for second_level in RootLevel.Get(first_level_name).GetListOfKeys():
            category = second_level.GetName()
            
            if settings['shape_type'].lower()  == 'postfit' and 'TAToTTQ' in category:
                first_level_name = first_level_name.replace('postfit', 'prefit') # preFit make the signal looks significant
            if (category =='TotalSig') or  (category == 'TotalProcs'):continue # In PostfitWorkspace
            if ('total_overall' in category) or ('total_signal' in category) or ('total' == category) or ('overall_total_covar' in category) or ('total_covar' in category): continue #In Fitdiagnostics
            fpath = first_level_name + '/' + category
            
            h = RootLevel.Get(fpath).Clone()
            if type(h) != ROOT.TH1F and type(h) != ROOT.TGraphAsymmErrors: raise TypeError('No such Histogram in file: {}'.format(fpath))

            h_postfix = ROOT.TH1F(fpath, '', len(binning) - 1, binning)
                    
                    
                
            nbin = h_postfix.GetNbinsX()
            
            for ibin in range(nbin):
                
                if category == 'data_obs' or category == 'data':
                    if settings['shape_type'].lower()  == 'prefit':
                        # h is TGraphAsymmetryError in prefit case. See FitDiagnostics file.
                        error = h.GetErrorY(ibin + 1)
                        bincontent = h.Eval(ibin + 0.5) #Graph
                    else:
                        error   = h.GetBinError(ibin+1) # just symmetrical error
                        bincontent = h.GetBinContent(ibin+1) 
                    h_postfix.SetBinError(ibin+1, error)
                else:
                    bincontent = h.GetBinContent(ibin+1) 
                h_postfix.SetBinContent(ibin+1, bincontent) # Modify the x-axis value
            
            if category == 'data_obs' or category == 'data':
                category = 'Data'
            elif category == 'total_background':
                category = 'TotalBkg' 
            Integral[category] += h_postfix.Integral()
            Histogram[category].Add(h_postfix)
            
            print('Access Histogram {fpath}'.format(fpath = fpath))
    for category in Histogram_Names:
        if ('TotalSig' in category) or  ('TotalProcs' in category):continue
        if ('total_overall' in category) or ('total_signal' in category) or ('total' == category) or ('overall_total_covar' in category) or ('total_covar' in category): continue #In Fitdiagnostics
        if category == 'total_background':
            category = 'TotalBkg' 
        elif category == 'data_obs' or category == 'data': category = 'Data'
        if Maximum < Histogram[category].GetMaximum():
            Maximum = Histogram[category].GetMaximum()

    if settings['shape_type'].lower() == 'prefit':
        Title = 'Pre-Fit Distribution'
    else:
        Title = 'Post-Fit Distribution'

    template_settings= {
            "Maximum":Maximum,
            "Integral":Integral,
            "Histogram":Histogram,
            "outputfilename":os.path.join(CURRENT_WORKDIR,os.path.join(settings['outputdir'],settings['shapePlot'])),
            "year":settings['year'],      
            "Title":Title,
            "xaxisTitle":'BDT score',
            "yaxisTitle":'Events / bin',
            "channel":settings['channel'],
            "coupling_value":settings['coupling_value'],
            "mass":settings["mass"],
            "text_y":settings["text_y"],
            "logy":settings["logy"],
            "unblind":settings['unblind'],
            "expectSignal":settings['expectSignal'],
            "plotRatio":settings['plotRatio'],
            "interference":settings['interference'],
            "paper":settings['paper']
            }
    if settings["unblind"] or settings["expectSignal"]:
        if not settings['interference']:    
            template_settings["Signal_Name"] = "TAToTTQ_{coupling_value}_M{higgs}{mass}".format(coupling_value=settings['coupling_value'],higgs=settings['higgs'],mass=settings['mass'])
        else:
                
            template_settings["Signal_Name"] = 'TAToTTQ_{mass}_s_{mass2}_{coupling_value}'.format(coupling_value=settings['coupling_value'],higgs=settings['higgs'],mass=settings['mass'],mass2=settings['mass2'])
    else:
            template_settings["Signal_Name"] = "DEFAULT"
    print("\n")
    template_settings["Signal_Name"] = template_settings["Signal_Name"].replace("01","04").replace("10","04")

    Plot_Histogram(template_settings=template_settings) 

    FileIn.Close()
    #a = h_stack.GetXaxis();
    #a.ChangeLabel(1,-1,-1,-1,-1,-1,"-1");
    #a.ChangeLabel(-1,-1,-1,-1,-1,-1,"1");

    if settings["logy"]:
      log_tag = "_log"
    else:
      log_tag = ""

    print("\nNext mode: \033[0;32m [diffNuisances] \033[1;33m")
    print("\033[1;33m* Please check \033[4m{plot}{log}.pdf\033[0;m".format(plot =os.path.join(CURRENT_WORKDIR,os.path.join(settings['outputdir'],settings['shapePlot'])),log=log_tag))
    print("\033[1;33m* Please check \033[4m{plot}{log}.png\033[0;m".format(plot=os.path.join(CURRENT_WORKDIR,os.path.join(settings['outputdir'],settings['shapePlot'])),log=log_tag))



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
        Color_Dict['Data'] = ROOT.kBlack
    if template_settings["unblind"] or template_settings["expectSignal"]:
        Color_Dict[template_settings["Signal_Name"]] = ROOT.kRed

    #### Canvas ####
    ROOT.gStyle.SetOptTitle(0)
    ROOT.gStyle.SetOptStat(0)
    ROOT.gROOT.SetBatch(1)
    
    canvas = ROOT.TCanvas("","",620,600)
    

    Set_Logy = template_settings['logy']

    if template_settings['plotRatio']:
      pad1 = ROOT.TPad('pad1','',0.00, 0.22, 0.99, 0.99)
      pad2 = ROOT.TPad('pad2','',0.00, 0.00, 0.99, 0.22)
      pad1.SetBottomMargin(0.01);
      pad1.SetTicks(1,1)
      pad2.SetTopMargin(0.035);
      pad2.SetBottomMargin(0.45);
      pad2.SetTicks(1,1)
      pad1.Draw()
      pad2.Draw()
      pad1.cd()
    else:
      pad1 = ROOT.TPad('pad1','',0.00, 0.00, 0.99, 0.99)
      pad1.SetTicks(1,1)
      pad1.SetBottomMargin(0.1);
      pad1.Draw()
      pad1.cd()

    if Set_Logy:
        pad1.SetLogy(1)
        Histogram_MaximumScale = 1000
    else:
        Histogram_MaximumScale = 2.0

    canvas.SetGrid(1,1)
    canvas.SetLeftMargin(0.12)
    canvas.SetRightMargin(0.08)
    ###############

    #### Legend ####
    legend_NCol = int(len(Color_Dict.keys())/5)
    legend = ROOT.TLegend(.15, .62, .15+0.37*(legend_NCol-1), .86);
    legend.SetNColumns(legend_NCol)
    legend.SetBorderSize(0);
    legend.SetFillColor(0);
    legend.SetShadowColor(0);
    legend.SetTextFont(42);
    legend.SetTextSize(0.038);
    #### Ordered_Integral ####
    Ordered_Integral = OrderedDict(sorted(template_settings['Integral'].items(), key=itemgetter(1)))
    ##########################
   
    if template_settings['unblind']:
      nDigits = int(np.log10(template_settings['Integral']["Data"]))+1
      for idx, Histogram_Name in enumerate(Ordered_Integral):
        if Histogram_Name == "Data": continue
        Yield = template_settings['Integral'][Histogram_Name]
        if int(np.log10(Yield))+1 >= nDigits:
          template_settings['Integral'][Histogram_Name] = (str(Yield)[:nDigits])
        else:
          template_settings['Integral'][Histogram_Name] = (str(Yield)[:nDigits+1])

    #### Histogram Settings ####
    h_stack = ROOT.THStack()
    hh_total = None
    hh_total = template_settings['Histogram']['TotalBkg'].Clone()
    h_sig =None
    for idx, Histogram_Name in enumerate(Ordered_Integral):

        if Histogram_Name == template_settings["Signal_Name"] and template_settings["Signal_Name"] != "DEFAULT":
            h_sig = template_settings['Histogram'][Histogram_Name]
            h_sig.SetLineColor(Color_Dict[Histogram_Name]) 
            h_sig.SetLineWidth(4)
    #        h_sig.SetLineStyle(9)
        else:    
            if Histogram_Name == 'Data':
                if template_settings['unblind']:
                    legend.AddEntry(template_settings['Histogram'][Histogram_Name],Histogram_Name+' [{:.0f}]'.format(template_settings['Integral'][Histogram_Name]) , 'PE')
                    template_settings['Histogram'][Histogram_Name].SetMarkerStyle(8)
                    template_settings['Histogram'][Histogram_Name].SetMarkerColor(1)
                    template_settings['Histogram'][Histogram_Name].SetLineWidth(2)
                    template_settings['Histogram'][Histogram_Name].SetLineColor(1)
            else:
                if Histogram_Name == 'TotalBkg': continue
                template_settings['Histogram'][Histogram_Name].SetFillColorAlpha(Color_Dict[Histogram_Name],0.65)
                h_stack.Add(template_settings['Histogram'][Histogram_Name])
                legend.AddEntry(template_settings['Histogram'][Histogram_Name],Histogram_Name.replace("TTTo2L","t#bar{t}").replace("ttW","t#bar{t}W").replace("ttH","t#bar{t}H") + ' [' + str(template_settings['Integral'][Histogram_Name]) + ']', 'F')

    h_stack.SetTitle("{};BDT score;Events / bin ".format(template_settings['Title']))
    h_stack.SetMaximum(h_stack.GetStack().Last().GetMaximum() * Histogram_MaximumScale)
    if Set_Logy:
      h_stack.SetMinimum(3.2)
    else:
      h_stack.SetMinimum(0.1)
    h_stack.Draw()
    h_stack.GetYaxis().SetTitle("Events / bin")
    h_stack.GetYaxis().SetTitleSize(0.042) # THStack should first be drawn and then can do this step
    h_stack.GetYaxis().SetTitleOffset(1.0)
#    pad1.Modified()
#    pad1.Update()
    h_stack.Draw("HIST")
    # For uncert.
    hh_total.SetFillStyle(3005)
    hh_total.SetFillColor(12) #ROOT.kGray + 2)
    hh_total.SetMarkerSize(0)
    hh_total.SetMarkerStyle(0)
    hh_total.SetMarkerColor(12) #ROOT.kGray + 2)
    hh_total.SetLineWidth(0)
    legend.AddEntry(hh_total,'Total-Unc','F')
    hh_total.Draw("SAME E2")

    if template_settings['unblind']:
        template_settings['Histogram']["Data"].Draw("SAME P*")
    if type(h_sig )== ROOT.TH1F:
        h_sig.Scale(2.5)
        h_sig.Draw("HIST;SAME")
        legend.AddEntry(h_sig,'g2HDM Signal(x2.5)', 'L')
    if template_settings['plotRatio']:
        pad2.cd()
        hMC     = h_stack.GetStack().Last()
        h_ratio = (template_settings['Histogram']["Data"].Clone())
        # h_ratio.Sumw2()
        h_ratio.Divide(hh_total)
        h_ratio.SetMarkerStyle(20)
        h_ratio.SetMarkerSize(0.85)
        h_ratio.SetMarkerColor(1)
        h_ratio.SetLineWidth(1)
          
        h_ratio.GetYaxis().SetTitle("Obs / Exp")
        h_ratio.GetXaxis().SetTitle(h_stack.GetXaxis().GetTitle())
        h_ratio.GetYaxis().CenterTitle()
        h_ratio.SetMaximum(1.2)
        h_ratio.SetMinimum(0.85)
        h_ratio.GetYaxis().SetNdivisions(4)
        h_ratio.GetYaxis().SetTitleOffset(0.3)
        h_ratio.GetYaxis().SetTitleSize(0.14)
        h_ratio.GetYaxis().SetLabelSize(0.1)
        h_ratio.GetXaxis().SetTitleSize(0.14)
        h_ratio.GetXaxis().SetLabelSize(0.1)
        h_ratio.Draw("E 2")

        x = [];
        y = [];
        xerror_l = [];
        xerror_r = [];
        yerror_u = [];
        yerror_d = [];
        
        
        
        for i in range(0,h_ratio.GetNbinsX()):
          x.append(h_ratio.GetBinCenter(i+1))
          y.append(1.0)
          xerror_l.append(0.5*h_ratio.GetBinWidth(i+1))
          xerror_r.append(0.5*h_ratio.GetBinWidth(i+1))
          # print (h_ratio.GetBinContent(i+1)*math.pow(math.pow(template_settings['Histogram']["Data"].GetBinError(i+1) / template_settings['Histogram']["Data"].GetBinContent(i+1), 2)+math.pow(hh_total.GetBinError(i+1)/hMC.GetBinContent(i+1),2),0.5))
          # print ("black point error: ",h_ratio.GetBinError(i+1))
          # print ("old band", hh_total.GetBinError(i+1)/hMC.GetBinContent(i+1))
          yerror_u.append(hh_total.GetBinError(i+1)/hMC.GetBinContent(i+1))
          yerror_d.append(hh_total.GetBinError(i+1)/hMC.GetBinContent(i+1))
        ru = ROOT.TGraphAsymmErrors(len(x), np.array(x), np.array(y),np.array(xerror_l),np.array(xerror_r), np.array(yerror_d), np.array(yerror_u))
        ru.SetFillColor(1);
        ru.SetFillStyle(3005);
        ru.Draw("SAME 2");


        pad1.cd()


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

    latex = ROOT.TLatex()
    latex.SetTextSize(0.038)
    latex.SetTextAlign(12)
    latex.SetNDC()
    latex.SetTextFont(42);
    latex.DrawLatex(0.21, 0.59, "#rho_{t%s} = %.1f,  m_{A} = %s GeV"%(quark, value,template_settings['mass']))
    if template_settings["interference"]:
      latex.DrawLatex(0.21, 0.54, "m_{A} - m_{H} = 50 GeV");

    ### CMS Pad #####
    
    import CMS_lumi
    CMS_lumi.writeExtraText = 1
    if template_settings['paper']:
      CMS_lumi.extraText = ""
      CMS_lumi.relPosX = 0.06
      CMS_lumi.relPosY = 0.03
    else:
      CMS_lumi.extraText = "Preliminary"
    CMS_lumi.lumi_sqrtS = "13 TeV" # used with iPeriod = 0, e.g. for simulation-only plots (default is an empty string)
    iPos = 11
    if( iPos==0 ): CMS_lumi.relPosX = 0.12
    iPeriod=template_settings['year']

    CMS_lumi.CMS_lumi(pad1, iPeriod, iPos)

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
    if settings['group'] == 0:pass 
    else:
        with open('./data_info/NuisanceList/group_set{group}.json'.format(group = int(settings['group']))) as f:
            Group = json.load(f)
    
    
    os.system('cd {outputdir}'.format(outputdir=settings['outputdir'])) 
    os.chdir(settings['outputdir'])
    workspace_root = os.path.basename(settings['workspace_root'])
    plot1Dscan = os.path.join(CURRENT_WORKDIR, 'plot1DScan.py')
     
    # safety check:
    if not os.path.isfile(workspace_root):
          raise Exception("First run: --mode datacard2workspace step")

    Log_Path = os.path.basename(settings['Log_Path'])
    commands = []
    rMin = settings['rMin']
    rMax = settings['rMax']
    points = 20
    
    if not settings['unblind']:
        print('Do not support blind option')
        return
    
    commands.append('echo datacard_workspace File: {workspace_root}'.format(workspace_root = workspace_root ))
    commands.append('echo Start to do likelihood Scan')
    commands.append('echo single scan ...')
    
    common_pattern = '.{year}.{channel}.{coupling}.unblind.Set{group}'.format(year = settings['year'], channel = settings['channel'], coupling = settings['coupling_value'], group = settings['group'])
    
    
    if settings['interference']:
        common_pattern += '.interference'
    else:
        common_pattern += '.pure'
        
    SingleScan_pattern = '.singlescan' + common_pattern 
    Snapshot_pattern = '.snap' + common_pattern 
         
    SingleScan_root = 'higgsCombine' + SingleScan_pattern + '.MultiDimFit.mH{mass}.root'.format(mass = settings['mass'])
    ### Single Fit ####
    Snapshot_root = 'higgsCombine' + Snapshot_pattern + '.MultiDimFit.mH{mass}.root'.format(mass = settings['mass'])
     
    commands.append('combine -M MultiDimFit {workspace_root} -n {SingleScan_pattern} -m {mass} --rMin {rMin} --rMax {rMax} --algo grid --points {points}'.format(workspace_root = workspace_root, SingleScan_pattern = SingleScan_pattern, mass = settings['mass'], rMin = settings['rMin'], rMax = settings['rMax'], points = points))
    
    commands.append('{plot1Dscan}  {SingleScan_root} -o Likelihood{SingleScan_pattern}'.format(plot1Dscan = plot1Dscan, SingleScan_root = SingleScan_root, SingleScan_pattern = SingleScan_pattern)) 
    ####################
    ####  SnapShot #####
    commands.append('combine -M MultiDimFit {workspace_root} -n {Snapshot_pattern} -m {mass} --rMin {rMin} --rMax {rMax} --saveWorkspace'.format(workspace_root = workspace_root, Snapshot_pattern = Snapshot_pattern, mass = settings['mass'], rMin = settings['rMin'], rMax = settings['rMax']))
    #####################
    #### Profile Scan ###
    
    commands.append('echo Start to do breakdown')
    commands.append('combine -M MultiDimFit {Snapshot_root} -n {common_pattern} -m {mass} --rMin {rMin} --rMax {rMax} --algo grid --points {points} --snapshotName MultiDimFit'.format(Snapshot_root = Snapshot_root, common_pattern = common_pattern, mass = settings['mass'], rMin = settings['rMin'], rMax = settings['rMax'], points = points))
    
    FreezeGroup_root = []
    FreezeGroup_pattern = []
    FreezeGroup_names = []
    chain_name = ''
    
    for Idx, group in enumerate(Group):
        if Idx == len(Group) - 1:break
        FileName = 'higgsCombine.freeze'
        chain_name += '.' + group
        FreezeGroup_names.append(' + '.join(Group[:Idx+1]) )
        FileName = FileName + chain_name + common_pattern + '.MultiDimFit.mH{mass}.root'.format(mass = settings['mass']) 
        freeze_pattern = '.freeze' + chain_name + common_pattern  
        FreezeGroup_root.append(FileName)
        FreezeGroup_pattern.append(freeze_pattern)
    FREEZE = '' 
    
    for Idx, group in enumerate(Group):
        if Idx == len(Group) - 1: break
        FREEZE += group if Idx == 0 else ',' + group
        commands.append('combine -M MultiDimFit {workspace_root}  -n {pattern} -m {mass} --rMin {rMin} --rMax {rMax} --algo grid --points {points} --freezeNuisanceGroups {FREEZE} --snapshotName MultiDimFit'.format(workspace_root = Snapshot_root, pattern = FreezeGroup_pattern[Idx], mass = settings['mass'], rMin = settings['rMin'], rMax = settings['rMax'], points = points, FREEZE = FREEZE))
    
    freeze_pattern = '.freeze.All' + common_pattern  
    
    FileName = 'higgsCombine' + freeze_pattern + '.MultiDimFit.mH{mass}.root'.format(mass = settings['mass']) 
    FreezeGroup_root.append(FileName)
    FreezeGroup_pattern.append(freeze_pattern) 
    
    
    
    commands.append('combine -M MultiDimFit {workspace_root}  -n {pattern} -m {mass} --rMin {rMin} --rMax {rMax} --algo grid --points {points}  --snapshotName MultiDimFit --freezeParameters allConstrainedNuisances'.format(workspace_root = Snapshot_root, pattern = freeze_pattern, mass = settings['mass'], rMin = settings['rMin'], rMax = settings['rMax'], points = points))
     
    ## Plot ##
    Queue = ''
    
    for Idx, File in enumerate(FreezeGroup_root):
        if Idx != len(FreezeGroup_root) - 1:
            Queue += '{File}:"Freeze {FreezeGroup_name}":{Idx} '.format(File = File, FreezeGroup_name = FreezeGroup_names[Idx], Idx = Idx+1) 
        else:
            Queue += '{File}:"Stat. Only":{Idx} '.format(File = File, Idx = Idx + 1) 

    BREAKDOWN_LIST = ','.join(Group)        
    
    if settings['interference']:
        POSTFIX = '--interference'
    else:
        POSTFIX = '' 
    commands.append('{plot1DScan} {SingleScan_root} --main-label "Total Uncert." -o Likelihood.breakdown.mH{mass}{common_pattern} --others {Queue} --breakdown "{BREAKDOWN_LIST}"'.format(mass = settings['mass'], plot1DScan = plot1Dscan, SingleScan_root = SingleScan_root,common_pattern = common_pattern, Queue = Queue, BREAKDOWN_LIST = BREAKDOWN_LIST + ', Stat.') + ' --year {year} --channel {channel} --mass {mass} --postfixname Set{group} {POSTFIX}'.format(year = settings['year'], channel = settings['channel'], mass = settings['mass'], group = settings['group'], POSTFIX = POSTFIX) ) 
    
    ### Scan NLL under each nuisance variation
    #commands.append('combineTool.py -M FastScan -w {workspace_root}:w'.format(workspace_root = workspace_root)) 
     
    for i in range(len(commands)):
        print(ts+commands[i]+ns)
        if i == 0:
            commands[i] = commands[i] + ' &> {Log_Path}'.format(Log_Path=Log_Path)
        else:
            commands[i] = commands[i] + ' &>> {Log_Path}'.format(Log_Path=Log_Path)
    command = ';'.join(commands)
    os.system(command)



def plotCorrelationRanking(settings=dict()):

    outputdir = os.path.join(settings['outputdir'], 'results')
    impacts_json = os.path.join(settings['outputdir'], settings['impacts_json'])
    

    inFile = ROOT.TFile.Open(settings['FitDiagnostics_file'] ,"READ")

    Impact_Rank = 30
    Corr_Rank= 15
    CorrelationMatrix = inFile.Get('covariance_fit_s')

    with open(impacts_json) as f:
        data = json.load(f)

    POIs = [ele['name'] for ele in data['POIs']]
    POI = POIs[0]


    Params = data['params']
    print('Start to ranking impacts')
    Params.sort(key = lambda x: abs(x['impact_%s' % POI]), reverse = True)


    Impact_Rank_Top_param = dict()
    for idx, param in enumerate(Params):
        #if idx > Impact_Rank: break
        paramInfo = dict()
        paramInfo['Name'] = param['name']
        paramInfo['bin'] = -1
        paramInfo['Rk'] = idx+1
        Impact_Rank_Top_param[param['name']] = paramInfo
    print('Start to retrieve correlation information for nuisance')
    Impact_Rank_Top_param_List = sorted(Impact_Rank_Top_param.items(), key = lambda x: x[1]['Rk'], reverse = True)
    for idx, param in enumerate(Impact_Rank_Top_param_List):
        for ibin in range(CorrelationMatrix.GetNbinsX() + 1):
            if CorrelationMatrix.GetXaxis().GetBinLabel(ibin+1) == param[1]['Name']:
                Impact_Rank_Top_param_List[idx][1]['bin'] = ibin+1
                
    print('Plotting')
    for idx,param in enumerate(Impact_Rank_Top_param_List):
        if param[1]['Name']  != 'jes' :continue
        Correlation = []

        for ibin in range(CorrelationMatrix.GetNbinsY()):
            Info = {}
            Info['name'] = CorrelationMatrix.GetYaxis().GetBinLabel(ibin+1) 
            Info['correlation'] = CorrelationMatrix.GetBinContent(param[1]['bin'], ibin+1)
            Correlation.append(Info)



        Correlation.sort(key = lambda x: abs(x['correlation']), reverse = True)
        #Correlation = Correlation[:Corr_Rank]
        correlation_array = []
        name_array = []
        barh_color = []
        counter = 0
        for jdx, corr in enumerate(Correlation):
            if counter < Corr_Rank:
                if corr['name'] == param[1]['Name']:
                    continue
                correlation_array.append(corr['correlation'])
                counter += 1
                if corr['correlation'] > 0:
                    barh_color.append('cornflowerblue')
                else:
                    barh_color.append('lightcoral')
                if corr['name'] == 'r':
                    name_array.append(corr['name'])
                else:
                    name_array.append(corr['name'] + ':Rk(%s)' % Impact_Rank_Top_param[corr['name']]['Rk'])
            else:break

        ypos = np.arange(len(name_array))
        plt.rcdefaults()
        fig, ax = plt.subplots()
        plt.gcf().set_size_inches(8,6)
        ax.barh(ypos, np.array(correlation_array), align = 'center', color = barh_color)
        ax.set_yticks(ypos)
        ax.set_xlim([-1, 1]) 
        ax.set_yticklabels(name_array)
        
        ax.yaxis.grid(True, linestyle='--', which='major',
                                   color='grey', alpha=.65)
        ax.axvline(0, color='red', alpha=0.65)
        for tick in ax.yaxis.get_major_ticks():
            tick.label.set_fontsize(10) 
        ax.invert_yaxis()
        ax.set_xlabel('Correlation')
        ax.set_title('Correlation Ranking for %s (rank: %d)' %(param[1]['Name'], param[1]['Rk']))
        
        output = os.path.join(outputdir, 'ImpactRank%s_CorrelationFor-%s.png'%(param[1]['Rk'], param[1]['Name']))
        plt.tight_layout()  
        fig.savefig(output, dpi=100)
        fig.savefig(output.replace('.png','.pdf'), dpi=100)
        print('\033[1;33m* Please check plot: \033[4m{}\033[0;m'.format(output))
    



def SubmitGOF(settings = dict()):

    command = "./SubmitGOF.sh {algo} {year} {channel} {coupling} {mass} ".format(algo = settings['GoF_Algorithm'], year = settings['year'], channel = settings['channel'], coupling = settings['coupling_value'], mass = settings['mass'])

    if settings['unblind']:
        command += ' unblind'
    else:
        if settings['expectSignal']:
            command += ' sig_bkg'
        else:
            command += ' bkg'

    if settings['interference']:
        
        command += ' interference'

    else:
        command += ' pure'
    

    print(ts+command+ns)
    
    os.system(command)

    
def GoFPlot(settings = dict()):
    ROOT.gStyle.SetOptTitle(0)
    ROOT.gStyle.SetOptStat(0)
    ROOT.gROOT.SetBatch(1)
    algo = settings['GoF_Algorithm']

    os.chdir("{outputdir}/results".format(outputdir=settings['outputdir']))
    print('Processing {algo} algorithm...'.format(algo = algo))

    analysis = "ExtraYukawa"
    OutputFile = 'GoF_{algo}_{coupling_value}_{year}_{channel}_mH{mass}.root'.format(year = settings['year'], channel = settings['channel'], mass = settings['mass'], coupling_value = settings['coupling_value'], algo = algo)
    rootToysFiles = 'higgsCombinetoys*.{coupling_value}.{year}.{channel}.{mass}.{algo}.GoodnessOfFit.mH{mass}.*.root'.format(year = settings['year'], channel = settings['channel'], mass = settings['mass'], coupling_value = settings['coupling_value'],  algo = algo)
    rootDataFiles = 'higgsCombineData.{coupling_value}.{year}.{channel}.{mass}.{algo}.GoodnessOfFit.mH{mass}.root'.format(year = settings['year'], channel = settings['channel'], mass = settings['mass'], coupling_value = settings['coupling_value'],  algo = algo)
    CheckFile(OutputFile, True, True) 
    if len(rootToysFiles) > 0:
        print('Merging \"{rootToysFiles}\" ROOT files into\"{OutputFile}\"'.format(OutputFile = OutputFile, rootToysFiles = rootToysFiles))
        os.system('hadd -k {OutputFile} {rootFiles} > mergeROOT.txt'.format(OutputFile = OutputFile, rootFiles = rootToysFiles))
    else:
        print('Found {nrootFiles} toy ROOT files to merge'.format(nrootFiles = len(rootToysFiles)))
        raise Exception('')

    if CheckFile(OutputFile, False, True):
        print('Opening merged ROOT file \"{OutputFile}\"'.format(OutputFile = OutputFile))
    else:
        print('The output ROOT file  \"{OutputFile}\" does not exist.'.format(OutputFile = OutputFile))
    if CheckFile(rootDataFiles, False, True):pass
    else:
        print('Please check whether {rootDataFiles} {outputdir}/results'.format(rootDataFiles = rootDataFiles, outputdir=settings['outputdir']))
    
    fToys = ROOT.TFile(OutputFile)
    if settings['unblind']:
        fData = ROOT.TFile(rootDataFiles)
    else:
        fData = ROOT.TFile(OutputFile)
    tToys = fToys.Get("limit")
    tData = fData.Get("limit")
    nToys = tToys.GetEntries()

    print('NData = {:.1f}, NToys = {:.1f}'.format(tData.GetEntries(), tToys.GetEntries()))
    tData.GetEntry(0)
    GoF_DATA = tData.limit

    print(GoF_DATA)

    ### Setting(Toys) ###
    GoF_TOYS_TOT = 0
    pval_cum = 0
    toys     = []
    minToy   = +99999999
    maxToy   = -99999999
    settings['Log_Path'] = 'ttc_{algo}_{coupling_value}_{year}_SR_{channel}_{channel}_MA{mass}_doGoFPlot.log'.format(year = settings['year'], channel = settings['channel'], mass = settings['mass'], coupling_value = settings['coupling_value'], algo = algo)
    with open(settings['Log_Path'], 'w') as f:
        for i in range(0, tToys.GetEntries()):
            tToys.GetEntry(i)
            GoF_TOYS_TOT += tToys.limit
            toys.append(tToys.limit)
            
            # Accumulate p-Value if GoF_toy > GoF_data
            if tToys.limit > GoF_DATA:
                f.write("GoF (toy) = {:.3f}, GoF (data) = {:.3f}, p-Value += {} ({})\n".format(tToys.limit, GoF_DATA, tToys.limit, pval_cum))
                pval_cum += tToys.limit 
    settings['Log_Path'] = os.path.join('{outputdir}/results'.format(outputdir = settings['outputdir']), settings['Log_Path'])
    
    pval = pval_cum/GoF_TOYS_TOT
    msg = "p-Value = {:.3f} (= {:.2f}/{:.2f})".format(pval, pval_cum, GoF_TOYS_TOT)

    nBins = 100
    xMax = {}
    xMax["saturated"] = 2000
    xMax["KS"] = 2000.0
    xMax["AD"] = 200.0
    xMin = dict()
    xMin["saturated"] = 0
    xMin["KS"] = 0.0
    xMin["AD"] = 0.0
    binWidth = dict()
    binWidth['saturated'] = 5
    binWidth['KS'] = 0.002
    binWidth['AD'] = 0.2
    nBins = (xMax[algo]-xMin[algo])/binWidth[algo]

    hist = ROOT.TH1D("GoF-{}".format(algo), "", int(nBins), xMin[algo], xMax[algo])

    for k in toys:
        hist.Fill(k)
    xMin  = hist.GetBinLowEdge(hist.FindFirstBinAbove(0.0))*0.25
    xMax  = hist.GetBinLowEdge(hist.FindLastBinAbove(0.0))*1.75 
    yMin  = 0.0
    yMax  = hist.GetMaximum()*1.05

    c = ROOT.TCanvas('c', 'c')
    
    binW = hist.GetBinWidth(0)
    if binW >= 5.0:
        yTitle = "Entries / {:.1f}".format(binW)
    elif binW >= 0.1:
        yTitle = "Entries / {:.2f}".format(binW)
    elif binW >= 0.01:
        yTitle = "Entries / {:.3f}".format(binW)
    else:
        yTitle = "Entries / {:.4f}".format(binW)
    
    hist.GetYaxis().SetTitle(yTitle) # bin width does not change
    hist.GetXaxis().SetTitle("test-statistic t")
    hist.GetXaxis().SetTitle("test-statistic t")
    hist.SetLineColorAlpha(ROOT.kRed, 0.4)
    hist.SetLineWidth(3)

    
    hist.GetXaxis().SetRangeUser(xMin, xMax)
    hist.GetYaxis().SetRangeUser(yMin, yMax)

    hist.GetYaxis().SetTitleOffset(1.30)


    hist.Draw()
    # Duplicate histogram for filling only part which is above GoF_DATA    
    hCum = hist.Clone("Cumulative")
    for b in range(0, hCum.GetNbinsX()):
        if b < hCum.FindBin(GoF_DATA):
            hCum.SetBinContent(b + 1 , 0)
    hCum.SetLineWidth(0)
    hCum.SetFillColorAlpha(ROOT.kBlue - 6, 0.35) #kLightRed)
    hCum.SetFillStyle(1001)
    hCum.Draw("same")
    hist.Draw("same") # re-draw to get line

    # Customise arrow indicating data-observed
    tZeroX = hist.GetBinLowEdge(hist.FindBin(GoF_DATA)) # GoF_DATA
    if hist.GetBinContent(hist.FindBin(GoF_DATA)) > 0.0:
        tZeroY = hist.GetBinContent(hist.FindBin(GoF_DATA))*0.25
    else:
        tZeroY = hist.GetMaximum()/5

    
    
    
    arr = ROOT.TArrow(GoF_DATA, 0.0001, GoF_DATA, hist.GetMaximum()/8, 0.02, "<|")
    arr.SetLineColor(ROOT.kBlue + 3)
    arr.SetFillColor(ROOT.kBlue + 3)
    arr.SetFillStyle(1001)
    arr.SetLineWidth(3)
    arr.SetLineStyle(1)
    arr.SetAngle(60)
    arr.Draw("<|same")

    # Add data observed value
    left = ROOT.TLatex()
    #left.SetNDC()
    left.SetTextFont(43)
    left.SetTextSize(22)
    left.SetTextAlign(11)
    if GoF_DATA < 1.0:
        left.DrawLatex(tZeroX, tZeroY*1.1, "#color[4]{t_{0}= %.2f}" % (GoF_DATA))
    elif GoF_DATA < 10.0:
        left.DrawLatex(tZeroX, tZeroY*1.1, "#color[4]{t_{0}= %.1f}" % (GoF_DATA))
    else:
        left.DrawLatex(tZeroX, tZeroY*1.1, "#color[4]{t_{0}= %.0f}" % (GoF_DATA))


    anaText = ROOT.TLatex()
    anaText.SetNDC()
    anaText.SetTextFont(43)
    anaText.SetTextSize(22)
    anaText.SetTextAlign(31) 
    anaText.DrawLatex(0.92, 0.86, analysis)

    # p-value
    pvalText = ROOT.TLatex()
    pvalText.SetNDC()
    pvalText.SetTextFont(43)
    pvalText.SetTextSize(22)
    pvalText.SetTextAlign(31) #11
    pvalText.DrawLatex(0.92, 0.80, "# toys: %d" % nToys)
    pvalText.DrawLatex(0.92, 0.74, "p-value: %.2f" % pval)
    
    import CMS_lumi
    CMS_lumi.writeExtraText = 1
    CMS_lumi.extraText = "Internal"
    CMS_lumi.lumi_sqrtS = "13 TeV" # used with iPeriod = 0, e.g. for simulation-only plots (default is an empty string)
    iPos = 11
    if( iPos==0 ): CMS_lumi.relPosX = 0.12
    iPeriod = settings['year']

    CMS_lumi.CMS_lumi(c, iPeriod, iPos)



    plotname = 'GoF_{algo}.{coupling_value}.{year}.{channel}.{mass}.mH{mass}.pdf'.format(year = settings['year'], channel = settings['channel'], mass = settings['mass'], coupling_value = settings['coupling_value'], algo = algo)

    c.Update()
    c.SaveAs(plotname)
    c.SaveAs(plotname.replace('.pdf', '.png'))
    plotname = os.path.join(settings['outputdir']+'/results', plotname) 
    print('\033[1;33m* Please check plot: \033[4m{}\033[0;m'.format(plotname))
    print('\033[1;33m* Please check plot: \033[4m{}\033[0;m'.format(plotname.replace('.pdf', '.png')))


def FinalYieldComputation(settings=dict()):

    # add a safety loop whether "FitDiagnostics_root" and "workspace_root" files are there or not! gkole fix me
    workspace_root = settings['workspace_root']
    FitDiagnostics_root = settings['FitDiagnostics_file']
    if os.path.isfile(workspace_root) and os.path.isfile(FitDiagnostics_root):
        print ("FitDiagnostics_root and workspace_root files are there!")
    else:
      raise Exception("First run: --mode datacard2workspace and --mode FitDiagnostics steps")

    outputFile = os.path.join(settings['outputdir'], 'results/PostFitShapesFromWorkspace_output_.root')
    command = "PostFitShapesFromWorkspace -w {workspace_root} -o {outputFile} -m 350 -f {FitDiagnostics_root}:fit_s --postfit --sampling --print".format(workspace_root = settings['workspace_root'], FitDiagnostics_root = settings['FitDiagnostics_file'], outputFile = outputFile)
    command+=' >& {Log_Path} '.format(Log_Path=settings['Log_Path'])
    
    os.system(command) 
    FileIn = ROOT.TFile.Open(outputFile, 'READ')
    

    Yield = dict()

    if settings['channel'] == 'C':
        channels = ['ee', 'em', 'mm']
    else:
        channels = [settings['channel']]
    if settings['year'] == 'run2':
        years = ['2016apv', '2016postapv', '2017', '2018']
    
    process_name_list = []
    for first_level in FileIn.GetListOfKeys():
        first_level_name = first_level.GetName()
        for second_level in FileIn.Get(first_level_name).GetListOfKeys():
            process_name_list.append(second_level.GetName())
        break

    for process in process_name_list:
        Yield[process] = dict()
        for Type in ['postfit', 'prefit']:
            Yield[process][Type] = dict()
            for channel in channels:
                Yield[process][Type][channel] = dict()
                Yield[process][Type][channel]['Central'] = 0
                Yield[process][Type][channel]['Error'] = 0

    
    
    for first_level in FileIn.GetListOfKeys():
        first_level_name = first_level.GetName()
        print('In Dir: {}'.format(first_level_name))
        if settings['year'] == "run2":
            year,channel,Type = first_level_name.split('_')
        else:
            channel,Type = first_level_name.split('_')
        for second_level in FileIn.Get(first_level_name).GetListOfKeys():
            process_name = second_level.GetName()
            
            unc = ctypes.c_double(0)
            H = FileIn.Get('{}/{}'.format(first_level_name, process_name))
            Integral = H.IntegralAndError(1, H.GetNbinsX(), unc)
            print('Process: {}, Integral: {}, Error: {}'.format(process_name, Integral, unc.value))
            Yield[process_name][Type][channel]['Central'] += Integral
            Yield[process_name][Type][channel]['Error'] += unc.value *  unc.value
    
    for process in process_name_list:
        for Type in ['prefit', 'postfit']:
            for channel in channels:
                Yield[process][Type][channel]['Error'] = math.sqrt(Yield[process][Type][channel]['Error'])

    FinalYield_json = os.path.join(settings['outputdir'], 'results/finalyield.json')
    with open(FinalYield_json, 'w') as f:
        json.dump(Yield, f, indent = 4)

    PostFixstr = ''
    if settings['unblind']:
        PostFixstr +='-unblind'
    else:
        PostFixstr += 'blind'
    PostFixstr += "-" + settings['year']
    PostFixstr += "-" + settings['channel']
    PostFixstr += "-" + settings['coupling_value']
    PostFixstr += "-mA" + settings['mass']
    if settings['interference']:
        PostFixstr +='-interference'
    else:
        PostFixstr += '-pure'


    with open('finalyield{PostFixstr}.tex'.format(PostFixstr = PostFixstr), 'w') as f:
        End = '\n'
        f.write(r'\begin{table}[!htpb]'+End)
        f.write(r'\begin{center}'+End)
        f.write(r'\begin{tabular}{|l|l|l|l|}'+End)
        f.write(r'\hline'+End)
        f.write(r'process     &    Yield   (\Pe{}\Pe)     & Yield (\PGm{}\PGm)  &  Yield (\Pe{}\PGm) \\'+End)
        f.write(r'\hline'+End)
        
        for category in ['data_obs', 'TotalBkg','Nonprompt', 'TTTo2L', 'VBS', 'ttW', 'ttH', 'VV', 'Others']:
            if ('TAToTTQ'  in category) or ('TotalSig' in category)  or ('TotalProcs' in category):continue
            
            if 'data' in category:
                f.write(r'{}'.format('Data'))
            else:
                f.write(r'{}'.format(category))
        
            for channel in channels:
                
                f.write(r'& {:.1f} $\pm$ {:.1f} '.format(Yield[category]['postfit'][channel]['Central'], Yield[category]['postfit'][channel]['Error']))
            f.write(r'\\'+End)
            if 'TotalBkg' in category:
                f.write(r'\hline\hline'+End)

        f.write(r'\hline'+End)
        f.write(r'\end{tabular}'+End)
        
        if settings['year'] == 'run2':
            YEAR = 'full Run 2'
        else:
            YEAR = settings['year']
        if settings['channel'] == 'C':
            CHANNEL = r'\Pe{}\Pe, \PGm{}\PGm and \Pe{}\PGm'
        elif settings['channel'] == 'ee':
            CHANNEL = r'\Pe{}\Pe'
        elif settings['channel'] == 'em':
            CHANNEL = r'\Pe{}\Pm'
        elif settings['channel'] == 'mm':
            CHANNEL = r'\Pm{}\Pm'

        CHANNEL+= " decay channel"
        if settings['interference']:
            INTERFERENCE = 'with H-A interference(\mA - \mH = 50 \GeV)'
        else:
            INTERFERENCE = '(pure)'
        if settings['coupling_value']:
            if 'rtu' in settings['coupling_value']:
                cp = 'rtu'
                COUPLING = r'$\rho_{tu}'
            elif 'rtc' in settings['coupling_value']:
                cp = 'rtc'
                COUPLING = r'$\rho_{tc}'

            COUPLING += ' = ' + str(float(settings['coupling_value'].split(cp)[1]) * 0.1) + ' $ '
            
        f.write(r'\caption{Yield table for '+CHANNEL + ' for ' + YEAR + ' with '+ COUPLING+ ' for ' + r' \mA = ' + settings['mass'] + ' \GeV {INTERFERENCE} }}'.format(INTERFERENCE = INTERFERENCE) + End)
        if settings['interference']:
            f.write(r'\label{tab:yields_'+settings['coupling_value']+r'_interference}'+End)
        else:
            f.write(r'\label{tab:yields_'+settings['coupling_value']+r'_pure}'+End)
        f.write(r'\end{center}'+End)
        f.write(r'\end{table}'+End)
    FileIn.Close()
    print('\033[1;33m* Please check txt file: \033[4m{}\033[0;m'.format('finalyield{PostFixstr}.tex'.format(PostFixstr = PostFixstr)))
    print('\033[1;33m* Please check txt file: \033[4m{}\033[0;m'.format(FinalYield_json))
