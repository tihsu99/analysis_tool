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

def CheckAndExec(MODE,datacards,mode='',settings=dict()):
    
    #Check And Create Folder: SignalExtraction
    start = time.time()
    CheckDir("./SignalExtraction",True)
    CheckDir("./SignalExtraction/{year}".format(year=settings['year']),True)
    CheckDir("./SignalExtraction/{year}/{channel}".format(year=settings['year'],channel=settings['channel']),True)
    CheckDir("./SignalExtraction/{year}/{channel}/{coupling_values}".format(year=settings['year'],channel=settings['channel'],coupling_values=settings['coupling_value']),True)
    CheckDir("./SignalExtraction/{year}/{channel}/{coupling_values}/{higgs}".format(year=settings['year'],channel=settings['channel'],coupling_values=settings['coupling_value'],higgs=settings['higgs']),True)
    CheckDir("./SignalExtraction/{year}/{channel}/{coupling_values}/{higgs}/err".format(year=settings['year'],channel=settings['channel'],coupling_values=settings['coupling_value'],higgs=settings['higgs']),True)
    CheckDir("./SignalExtraction/{year}/{channel}/{coupling_values}/{higgs}/output".format(year=settings['year'],channel=settings['channel'],coupling_values=settings['coupling_value'],higgs=settings['higgs']),True)
    CheckDir("./SignalExtraction/{year}/{channel}/{coupling_values}/{higgs}/log_condor".format(year=settings['year'],channel=settings['channel'],coupling_values=settings['coupling_value'],higgs=settings['higgs']),True)
    CheckDir("./SignalExtraction/{year}/{channel}/{coupling_values}/{higgs}/results".format(year=settings['year'],channel=settings['channel'],coupling_values=settings['coupling_value'],higgs=settings['higgs']),True)

    Final_Output_Dir = "SignalExtraction/{year}/{channel}/{coupling_values}/{higgs}".format(year=settings['year'],channel=settings['channel'],coupling_values=settings['coupling_value'],higgs=settings['higgs'])


    
    Log_Path = os.path.join(Final_Output_Dir,os.path.relpath(datacards,os.path.dirname(datacards)).replace(".txt","_{}.log".format(mode)))
    workspace_root = os.path.join(Final_Output_Dir,os.path.relpath(datacards,os.path.dirname(datacards)).replace("txt","root"))
    FitDiagnostics_file = 'fitDiagnostics_{year}_{channel}_{higgs}_{mass}_{coupling_value}.root'.format(year=settings['year'],channel=settings['channel'],higgs=settings['higgs'],mass=settings['mass'],coupling_value=settings['coupling_value'])
    Pull_File = FitDiagnostics_file.replace("fitDiagnostics","pulls")
    impacts_json = os.path.join(Final_Output_Dir,'results/impacts_t0_{year}_{channel}_M{higgs}{mass}_{coupling_value}.json'.format(year=settings['year'],channel=settings['channel'],higgs=settings['higgs'],mass=settings['mass'],coupling_value=settings['coupling_value'])) 

    
    
    CheckFile(Log_Path,True)
    settings['outputdir'] = Final_Output_Dir
    settings['Log_Path'] = Log_Path
    settings['workspace_root'] = workspace_root
    settings['datacards'] = datacards
    settings['FitDiagnostics_file'] = os.path.join(settings['outputdir'],FitDiagnostics_file)
    settings['Pull_File'] = os.path.join(settings['outputdir'],FitDiagnostics_file)
    settings['impacts_json'] = impacts_json
    settings['postFitPlot'] = os.path.join(Final_Output_Dir,'results/postFit_{}'.format(settings['channel']))
    MODE(settings=settings)
    if mode!='postFitPlot':
        print("* Please see {} for the output information.".format(Log_Path))
    print("\nRun time for {mode}: {runtime} sec".format(mode=mode,runtime=time.time()-start))



def datacard2workspace(settings=dict()):

    command = 'text2workspace.py {datacards}  -o {workspace_root}  --channel-mask > {Log_Path}'.format(datacards=settings['datacards'],workspace_root=settings['workspace_root'],Log_Path=settings['Log_Path'])
    print(command)
    os.system(command)
    print("A new Workspace root file: {} is created! ".format(settings['workspace_root']))

    print("\nNext mode: [FitDiagnostics]")

def FitDiagnostics(settings=dict()):
    command = "combine -M FitDiagnostics {workspace_root} --saveShapes --saveWithUncertainties -t -1 --expectSignal 0 -n _{year}_{channel}_{higgs}_{mass}_{coupling_value} --cminDefaultMinimizerStrategy 0 --rMin -20 --rMax 20".format(workspace_root = settings['workspace_root'], year=settings['year'],channel=settings['channel'],higgs=settings['higgs'],mass=settings['mass'],coupling_value=settings['coupling_value'])

    FitDiagnostics_file = 'fitDiagnostics_{year}_{channel}_{higgs}_{mass}_{coupling_value}.root'.format(year=settings['year'],channel=settings['channel'],higgs=settings['higgs'],mass=settings['mass'],coupling_value=settings['coupling_value'])
    print(command)
    command = command + ' > {Log_Path}'.format(Log_Path=settings['Log_Path'])
    os.system(command)
    #Status : MINIMIZE=0 HESSE=0

    os.system('mv {FitDiagnostics_file} {outputdir}'.format(FitDiagnostics_file=FitDiagnostics_file,outputdir=settings['outputdir']))
    
    FitDiagnostics_file = settings['FitDiagnostics_file']
    
    print("A new FitDiagnostics file: {} is created! \n".format(FitDiagnostics_file))
    print("* Use the following commands to check whether the Status: MINIMIZE=0 HESSE=0:\n")
    print("(1) root -l {FitDiagnostics_file}\n".format(FitDiagnostics_file=FitDiagnostics_file))
    print("(2) fit_s->Print()\n")
    print("For more detailed information about FitDiagnostics : https://cms-analysis.github.io/HiggsAnalysis-CombinedLimit/part5/longexercise/#c-using-fitdiagnostics") 
    print("\nNext mode: [postFitPlot]")

def PullCalculation(settings=dict()):
    command = 'python diffNuisances.py {FitDiagnostics_file} --abs --all -g {Pull_File}'.format(FitDiagnostics_file= settings['FitDiagnostics_file'],Pull_File=settings['Pull_File'])

    print(command)

    command += ' > {Log_Path}'.format(Log_Path=settings['Log_Path'])
    
    os.system(command)
    
    print("*Please see {} for more information.".format(settings['Log_Path']))
    print("*Pull root file: {} is created. ".format(settings['Pull_File']))
    print("\nNext mode: [PlotPulls]")


def PlotPulls(settings=dict()):
    
    command = 'root -l -b -q '+"'PlotPulls.C"+'("{Pull_File}","","_{year}_{channel}_{higgs}_{mass}_{coupling_value}")'.format(Pull_File=settings['Pull_File'],OutputFolder=settings['outputdir'],year=settings['year'],channel=settings['channel'],higgs=settings['higgs'],mass=settings['mass'],coupling_value=settings['coupling_value'])+"'"
    print(command)

    command += ' > {}'.format(settings['Log_Path'])
    os.system(command)
    os.system("mv {outputdir}/fitDiagnostics_* {outputdir}/results ".format(outputdir=settings['outputdir']))
    print("\n")
    print("*Please see {} for more information.".format(settings['Log_Path']))
    print("*Pull root file: {} is created. ".format(settings['Pull_File']))
    print("*Your pull plots and root files are moved under: {}/results".format(settings['outputdir']))
    print("\nNext mode: [Impact_doInitFit]")

def Impact_doInitFit(settings=dict()):
    command = 'combineTool.py -M Impacts -d {workspace_root} --doInitialFit --robustFit 1 -m 200 -t -1 --expectSignal 0 --rMin -20 --job-mode condor --task-name {year}-{channel}-{coupling_value}-M{higgs}{mass} '.format(workspace_root=settings['workspace_root'],year=settings['year'],channel=settings['channel'],higgs=settings['higgs'],mass=settings['mass'],coupling_value=settings['coupling_value'])+'--sub-opts='+"'+JobFlavour="+'"tomorrow"'+"'" +' --rMax 20'
    print(command)
    command += ' > {}'.format(settings['Log_Path'])
    os.system(command) 
    
    print("\n")
    print("You need to wait for the condor job is done, then move to the next step [Impact_doFits].")


def Impact_doFits(settings=dict()):
    
    command = 'combineTool.py -M Impacts -d {workspace_root} --doFits --robustFit 1 -m 200 -t -1 --expectSignal 0 --rMin -20 --job-mode condor --task-name {year}-{channel}-{coupling_value}-M{higgs}{mass} --parallel 256 '.format(workspace_root=settings['workspace_root'],year=settings['year'],channel=settings['channel'],higgs=settings['higgs'],mass=settings['mass'],coupling_value=settings['coupling_value'])+'--sub-opts='+"'+JobFlavour="+'"tomorrow"'+"'" +' --rMax 20'
    print(command)
    command += ' > {}'.format(settings['Log_Path'])
    os.system(command) 

    print("\n")
    print("You need to wait for the condor job is done, then move to the next step [Plot_Impacts].")
    print("\nNext mode: [Plot_Impacts]")

def Plot_Impacts(settings=dict()):
    os.system("mv *{year}-{channel}-{coupling_value}-M{higgs}{mass}*.err {outputdir}/err".format(year=settings['year'],channel=settings['channel'],coupling_value=settings['coupling_value'],higgs=settings['higgs'],mass=settings['mass'],outputdir=settings['outputdir']))
    os.system("mv *{year}-{channel}-{coupling_value}-M{higgs}{mass}*.out {outputdir}/output".format(year=settings['year'],channel=settings['channel'],coupling_value=settings['coupling_value'],higgs=settings['higgs'],mass=settings['mass'],outputdir=settings['outputdir']))
    os.system("mv *{year}-{channel}-{coupling_value}-M{higgs}{mass}*.log {outputdir}/log_condor".format(year=settings['year'],channel=settings['channel'],coupling_value=settings['coupling_value'],higgs=settings['higgs'],mass=settings['mass'],outputdir=settings['outputdir']))

    command = 'combineTool.py -M Impacts -d {workspace_root} -o {impacts_json} -m 200'.format(workspace_root=settings['workspace_root'],impacts_json=settings['impacts_json'],mass=settings['mass'])
    os.system(command)
    command = 'plotImpacts.py -i  {impacts_json} -o {impacts_json_prefix}'.format(impacts_json=settings['impacts_json'],impacts_json_prefix=settings['impacts_json'].replace(".json",""))
    os.system(command)
    print(command+"\n\n")
    print("Please check {impacts_json_prefix}.pdf".format(impacts_json_prefix=settings['impacts_json'].replace(".json","")))


def postFitPlot(settings=dict()):

    figDiagnostics_File = settings['FitDiagnostics_file']
    CheckFile(figDiagnostics_File)
    SampleName_File = "./data_info/Sample_Names/process_name_{year}.json".format(year=settings['year'])



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
    canvas.SetGrid(0,0)
    canvas.SetLeftMargin(0.12)

    fin = ROOT.TFile(figDiagnostics_File,"READ")

    first_dir = 'shapes_fit_b'
    second_dir = '/SR_{channel}/'.format(channel=settings['channel'])

    Histogram = dict()

    with open(SampleName_File,'r') as f:
        Sample_Names = json.load(f).keys()

    Histogram_Names = []

    for Sample_Name in Sample_Names:
        Histogram_Names.append(str(Sample_Name))


    Histogram = dict()
    Maximum = -1
    for Histogram_Name in Histogram_Names:
        Histogram[Histogram_Name] = fin.Get(first_dir+second_dir+Histogram_Name)
        if type(Histogram[Histogram_Name]) != ROOT.TH1F:
            raise ValueError("No such histogram, please check {SampleName_File} and {figDiagnostics_File}".format(SampleName_File=SampleName_File,figDiagnostics_File=figDiagnostics_File))
        else:
            print("Access: {}".format(Histogram_Name))
            print("Integral: {}\n".format(Histogram[Histogram_Name].Integral()))
            if Maximum < Histogram[Histogram_Name].GetMaximum():
                Maximum = Histogram[Histogram_Name].GetMaximum()

    #Color_List = [ROOT.kAzure,ROOT.kMagenta,ROOT.kRed,ROOT.kOrange,ROOT.kGreen]
    Color_Dict ={
            'DY':ROOT.kRed,
            'VV':ROOT.kCyan-9,
            'VVV':ROOT.kSpring - 9,
            'SingleTop':ROOT.kGray,
            'tttX':ROOT.kPink-3,
            'tZq':ROOT.kYellow-4,
            'TTTo2L':ROOT.kBlue,
            'ttW':ROOT.kGreen-2,
            'ttZ':ROOT.kCyan-2,
            'VBS':ROOT.kBlue-6,
            'ttVH':ROOT.kRed-9,
            'ttVV':ROOT.kOrange+3,
            'Nonprompt':ROOT.kViolet-4
            }
    ### Check the process name
    for Histogram_Name in Histogram_Names:
        if Histogram_Name not in Color_Dict.keys():
            raise ValueError("Make sure {} in Color_Dict.keys()".format(Histogram_Name)) 



    legend_NCol = int(len(Histogram_Names)/5)

    legend = ROOT.TLegend(.35, .65, .58+0.25*(legend_NCol-1), .890);
    legend.SetNColumns(int(len(Histogram_Names)/4))
    #legend.SetBorderSize(0);
    legend.SetFillColor(0);
    legend.SetShadowColor(0);
    legend.SetTextFont(42);
    legend.SetTextSize(0.03);


    for idx,Histogram_Name in enumerate(Histogram_Names):
        Histogram[Histogram_Name].SetFillColor(Color_Dict[Histogram_Name])
        if idx == 0:
            Histogram[Histogram_Name].SetMaximum(Maximum * Histogram_MaximumScale)
            Histogram[Histogram_Name].GetXaxis().SetTitle("BDT score")
        Histogram[Histogram_Name].Draw('HIST SAME')
        legend.AddEntry(Histogram[Histogram_Name],Histogram_Name , 'F')
    ### CMS Pad #####
    import CMS_lumi
    CMS_lumi.writeExtraText = 1
    CMS_lumi.extraText = "Internal"
    CMS_lumi.lumi_sqrtS = "13 TeV" # used with iPeriod = 0, e.g. for simulation-only plots (default is an empty string)
    iPos = 11
    if( iPos==0 ): CMS_lumi.relPosX = 0.12
    iPeriod=settings['year']

    CMS_lumi.CMS_lumi(canvas, iPeriod, iPos)

    ######


    legend.Draw("SAME")
    canvas.Update()
    canvas.SaveAs('{prefix}.pdf'.format(prefix=settings['postFitPlot']))
    canvas.SaveAs('{prefix}.png'.format(prefix=settings['postFitPlot']))

    print("Please check {prefix}.pdf".format(prefix=settings['postFitPlot']))
    print("Please check {prefix}.png".format(prefix=settings['postFitPlot']))

    print("\nNext mode: [PullCalculation]")
