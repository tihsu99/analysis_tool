import os
import sys
import time
import ROOT
import json
import math
import matplotlib.pyplot as plt
CURRENT_WORKDIR = os.getcwd()
sys.path.append(CURRENT_WORKDIR)
sys.path.append(os.path.join(CURRENT_WORKDIR, '../python'))
from common import Color_Dict_ref
ROOT.gROOT.SetBatch(ROOT.kTRUE)
from Util.General_Tool import CheckDir,CheckFile,CheckFile,binning,read_json
from collections import OrderedDict
from operator import itemgetter
from Util.aux import *
import numpy as np
import ctypes
from ROOT import gStyle
#from Util.OverlappingPlots import *
from plotstyle import *
import random
import matplotlib.pyplot as plt
from array import array
import cmsstyle as CMS
import tdrstyle

CMS.SetExtraText("Preliminary")
CMS.SetEnergy("13")

#####################
## Dict of regions ##
#####################

region_channel_dict = dict()
cut_regions = read_json('../data/cut.json')
for region_ in cut_regions:
  region_channel_dict[region_] = []
  for channel_ in cut_regions[region_]["channel_cut"]:
    region_channel_dict[region_].append(channel_)

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
        if (settings['expectSignal'] > 0.0):
            Fit_type+='s_plus_b'
        else:
            Fit_type+='b_only'


    CheckDir(os.path.join(settings['outdir'],"SignalExtraction/{year}/{region}/{channel}/{coupling_values}/{higgs}/{mass}/".format(year=settings['year'],channel=settings['channel'],coupling_values=settings['coupling_value'],mass=settings['mass'],higgs=settings['higgs'], region=settings['region'])), True)


#    CheckDir(os.path.join(settings['outdir'],"SignalExtraction"),True)
#    CheckDir(os.path.join(settings['outdir'],"SignalExtraction/{year}".format(year=settings['year'])),True)
#    CheckDir(os.path.join(settings['outdir'],"SignalExtraction/{year}/{channel}".format(year=settings['year'],channel=settings['channel'])),True)
#    CheckDir(os.path.join(settings['outdir'],"SignalExtraction/{year}/{channel}/{coupling_values}".format(year=settings['year'],channel=settings['channel'],coupling_values=settings['coupling_value'])),True)
 #   CheckDir(os.path.join(settings['outdir'],"SignalExtraction/{year}/{channel}/{coupling_values}/{higgs}".format(year=settings['year'],channel=settings['channel'],coupling_values=settings['coupling_value'],higgs=settings['higgs'])),True)
  #  CheckDir(os.path.join(settings['outdir'],"SignalExtraction/{year}/{channel}/{coupling_values}/{higgs}/{mass}/".format(year=settings['year'],channel=settings['channel'],coupling_values=settings['coupling_value'],mass=settings['mass'],higgs=settings['higgs'])),True)
    CheckDir(os.path.join(settings['outdir'],"SignalExtraction/{year}/{region}/{channel}/{coupling_values}/{higgs}/{mass}/{Fit_type}".format(year=settings['year'],channel=settings['channel'],coupling_values=settings['coupling_value'],higgs=settings['higgs'],Fit_type=Fit_type,mass=settings['mass'],region=settings['region'])),True)
    CheckDir(os.path.join(settings['outdir'],"SignalExtraction/{year}/{region}/{channel}/{coupling_values}/{higgs}/{mass}/{Fit_type}/err".format(year=settings['year'],channel=settings['channel'],coupling_values=settings['coupling_value'],higgs=settings['higgs'],Fit_type=Fit_type,mass=settings['mass'],region=settings['region'])),True)
    CheckDir(os.path.join(settings['outdir'],"SignalExtraction/{year}/{region}/{channel}/{coupling_values}/{higgs}/{mass}/{Fit_type}/output".format(year=settings['year'],channel=settings['channel'],coupling_values=settings['coupling_value'],higgs=settings['higgs'],Fit_type=Fit_type,mass=settings['mass'],region=settings['region'])),True)
    CheckDir(os.path.join(settings['outdir'],"SignalExtraction/{year}/{region}/{channel}/{coupling_values}/{higgs}/{mass}/{Fit_type}/log_condor".format(year=settings['year'],channel=settings['channel'],coupling_values=settings['coupling_value'],higgs=settings['higgs'],Fit_type=Fit_type,mass=settings['mass'],region=settings['region'])),True)
    CheckDir(os.path.join(settings['outdir'],"SignalExtraction/{year}/{region}/{channel}/{coupling_values}/{higgs}/{mass}/{Fit_type}/results".format(year=settings['year'],channel=settings['channel'],coupling_values=settings['coupling_value'],higgs=settings['higgs'],Fit_type=Fit_type,mass=settings['mass'],region=settings['region'])),True)
    CheckDir(os.path.join(settings['outdir'],"SignalExtraction/{year}/{region}/{channel}/{coupling_values}/{higgs}/{mass}/{Fit_type}/root".format(year=settings['year'],channel=settings['channel'],coupling_values=settings['coupling_value'],higgs=settings['higgs'],Fit_type=Fit_type,mass=settings['mass'],region=settings['region'])),True)


    Final_Output_Dir = os.path.join(settings['outdir'],"SignalExtraction/{year}/{region}/{channel}/{coupling_values}/{higgs}/{mass}/{Fit_type}".format(year=settings['year'],channel=settings['channel'],coupling_values=settings['coupling_value'],higgs=settings['higgs'],Fit_type=Fit_type,mass=settings['mass'],region=settings['region']))

    settings['outputdir'] = Final_Output_Dir
    settings['WorkDir'] = CURRENT_WORKDIR
    settings['condorDir'] = os.path.join(settings['WorkDir'],"SignalExtraction/{year}/{region}/{channel}/{coupling_values}/{higgs}/{mass}/{Fit_type}".format(year=settings['year'],channel=settings['channel'],coupling_values=settings['coupling_value'],higgs=settings['higgs'],Fit_type=Fit_type,mass=settings['mass'],region=settings['region']))

    Log_Path = os.path.relpath(datacards,os.path.dirname(datacards)).replace(".txt","_{}.log".format(mode))
    workspace_root = os.path.relpath(datacards,os.path.dirname(datacards)).replace("txt","root")
    FitDiagnostics_file = 'fitDiagnostics_{year}_{region}_{channel}_{higgs}_{mass}_{coupling_value}.root'.format(year=settings['year'],channel=settings['channel'],higgs=settings['higgs'],mass=settings['mass'],coupling_value=settings['coupling_value'], region=settings['region'])
    diffNuisances_File = os.path.join(Final_Output_Dir,FitDiagnostics_file.replace("fitDiagnostics","diffNuisances"))
    impacts_json = 'results/impacts_t0_{year}_{region}_{channel}_M{higgs}{mass}_{coupling_value}.json'.format(year=settings['year'],channel=settings['channel'],higgs=settings['higgs'],mass=settings['mass'],coupling_value=settings['coupling_value'],region=settings['region'])

    settings['Log_Path'] = os.path.join(settings['outputdir'],Log_Path)
    settings['workspace_root'] = os.path.join(settings['outputdir'],workspace_root)
    settings['datacards'] = os.path.join(settings['WorkDir'],datacards)
    settings['FitDiagnostics_file'] = os.path.join(settings['outputdir'],'results/'+FitDiagnostics_file)
    settings['diffNuisances_File'] = diffNuisances_File
    settings['impacts_json'] = impacts_json
    settings['shapePlot'] = '{}_{}'.format(settings['shape_type'],settings['channel'])
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
    channel_mask_command = " --channel-masks " if settings['channel_mask'] is not None else ""
    command = 'text2workspace.py {datacards}  -o {workspace_root} {channel_mask} '.format(datacards=settings['datacards'],workspace_root=settings['workspace_root'], channel_mask = channel_mask_command)
    print(ts+command+ns)

    command+=' >& {Log_Path} '.format(Log_Path=settings['Log_Path'])
    os.system(command)

    print("\nNext mode: [\033[0;32m FitDiagnostics \033[0;m]")
    print("\n* A new Workspace root file: \033[0;32m\033[4m{}\033[0;m is created!".format(os.path.join(settings['outputdir'],settings['workspace_root'])))

def GlobalSignificance(settings=dict()):

    nToys = settings['nToys']
    nToys_per_jobs = 40

    Log_Path = os.path.basename(settings['Log_Path'])

    farm_dir = f"{os.getcwd()}/Farm_Significance/{settings['mass']}"
    os.system("mkdir -p {farm_dir}".format(farm_dir = farm_dir))

    condor = open(os.path.join(farm_dir, 'condor.sub'), 'w')
    condor.write('output = %s/job_common_$(cfgFile).out\n'%farm_dir)
    condor.write('error  = %s/job_common_$(cfgFile).err\n'%farm_dir)
    condor.write('log    = %s/job_common_$(cfgFile).log\n'%farm_dir)
    condor.write('executable = %s/$(cfgFile)\n'%farm_dir)
    condor.write('+JobFlavour = "tomorrow"\n')
    condor.write('RequestCpus = 1\n')
    condor.write('queue 1 cfgFile in ')

    CheckDir((os.path.join(settings['outputdir'], 'GlobalSignificance')))
    os.chdir(os.path.join(settings['outputdir'], 'GlobalSignificance'))

    dc = dict()
    os.system("mkdir -p workspace")
    command = f"combine -M GenerateOnly {settings['workspace_root']} -m 125 -t {nToys} --seed 123456 --saveToys --expectSignal=0 --toysFrequentist \n"
    os.system(command)

    mass_list = [200, 300, 400, 500, 600, 700, 800, 900, 1000]
    seed_numbers = random.sample(range(1, 1000000), 1000)
    for mass_ in mass_list:
        wp_root = settings['workspace_root'].split('/')[-1].replace(str(settings['mass']), str(mass_))
        target_datacard = os.path.join('/'.join(settings['datacards'].split('/')[:-1]), settings['datacards'].split('/')[-1].replace(str(settings['mass']), str(mass_)))
        print('text2workspace.py {datacards}  -o workspace/{workspace_root} '.format(datacards=target_datacard,workspace_root=wp_root))
        if not os.path.exists(f'workspace/{wp_root}'):
            os.system('text2workspace.py {datacards}  -o workspace/{workspace_root} '.format(datacards=target_datacard, workspace_root=wp_root))
        workspace_for_certain_mass = os.path.join('workspace', wp_root)
        for iTask in range(int(nToys/nToys_per_jobs)):
           shell_file = f"global_significance_mass{mass_}_iTask{iTask}.sh"
           command    = f"cd {settings['outputdir']}/GlobalSignificance \n"
           root_file_pool = []
           for i in range(nToys_per_jobs):
               global_index = iTask * nToys_per_jobs + i + 1
               command += f"combine -M Significance {workspace_for_certain_mass}  --redefineSignalPOI r -n M{mass_}_{global_index} -D higgsCombineTest.GenerateOnly.mH125.123456.root:toys/toy_{global_index} --cminDefaultMinimizerStrategy 2 --cminDefaultMinimizerTolerance 0.5  --X-rtd FITTER_NEW_CROSSING_ALGO --X-rtd FITTER_NEVER_GIVE_UP --X-rtd FITTER_BOUND\n"
               root_file_pool.append(f'higgsCombineM{mass_}_{global_index}.Significance.mH120.root')
           command += f"hadd higgsCombineM{mass_}_{iTask}.root " + ' '.join(root_file_pool) + " \n"
           for root_file_ in root_file_pool:
             command += f'rm {root_file_}\n'
           prepare_shell(shell_file, command, condor, farm_dir, cmssw = True)
    condor.close()
    # os.system(f"condor_submit {farm_dir}/condor.sub")

def GlobalSignificancePlot(settings=dict()):

    mass_list = [200, 300, 400, 500, 600, 700, 800, 900, 1000]
    nToys     = settings['nToys']
    nToys_per_job = 40

    significance_tensor = np.ones((nToys, len(mass_list)), dtype = float) * -1
    outputdir = "{outputdir}/GlobalSignificance".format(outputdir=settings['outputdir'])
    os.chdir(outputdir)
    import uproot

    for idx, mass_ in enumerate(mass_list):
        iglobal = 0
        print(mass_)
        for iTask in range(int(nToys / nToys_per_job)):
            if not (os.path.exists(f"higgsCombineM{mass_}_{iTask}.root")): #and os.path.getsize(f"higgsCombineM{mass_}_{iTask}.root") > 100):
                print(f"higgsCombineM{mass_}_{iTask}.root not exists")
                continue

            try:
              with uproot.open(f"higgsCombineM{mass_}_{iTask}.root") as file:
                tree = file["limit"]
                array = tree.arrays(["limit"], library = "np")
                if(len(array["limit"]) < nToys_per_job):
                    continue
                significance_tensor[iTask * nToys_per_job: iTask * nToys_per_job + len(array["limit"]), idx] = array["limit"]
            except Exception as e:
              print(f"Error processing higgsCombineM{mass_}_{iTask}.root: {e}")
              continue

    print(significance_tensor)
    significance_tensor = significance_tensor[~np.any(significance_tensor < 0, axis=1)]
    significance_max = np.max(significance_tensor, axis = 1)

    significance_file = os.path.join(settings['working_directory'], 'bin', settings['year'], settings['region'], settings['channel'], f'limits_bH_rtt0p6_rtc0p4_asimov_extYukawa_MH{settings["mass"]}_significance.txt')
    for ilongline in open(significance_file):
        significance_local = float(ilongline.rstrip().split()[2])

    print(len(significance_max), significance_local)

    p_value = len(significance_max[significance_max > significance_local]) / len(significance_max)
    global_significance = ROOT.TMath.NormQuantile(1 - p_value)

    histo = ROOT.TH1F("histo", ";#sigma_{max};nEntries", 100, 0, 5)
    for value in significance_max:
        histo.Fill(value)

    x_axis = histo.GetXaxis()
    y_axis = histo.GetYaxis()
    x_title = histo.GetXaxis().GetTitle()
    y_title = histo.GetYaxis().GetTitle()
    nbinX  = x_axis.GetNbins()
    nbinY  = y_axis.GetNbins()
    x_binnings = [x_axis.GetBinLowEdge(bin_+1) for bin_ in range(nbinX+1)]
    y_binnings = [y_axis.GetBinLowEdge(bin_+1) for bin_ in range(nbinY+1)]

    c = CMS.cmsCanvas('', min(x_binnings), max(x_binnings), 0, histo.GetMaximum() * 1.2, x_title, y_title, square = CMS.kSquare, extraSpace=0.03, iPos=0, with_z_axis=False)

    CMS.cmsDraw(histo, 'HIST', mcolor = ROOT.kBlack,  lcolor = ROOT.kBlack, msize=0, fstyle = 0)

    arr = ROOT.TArrow(significance_local, 0.001, significance_local, histo.GetMaximum() / 8, 0.02, "<|")
    arr.SetLineColor(ROOT.kBlue)
    arr.SetFillColor(ROOT.kBlue)
    arr.SetFillStyle(1001)
    arr.SetLineWidth(6)
    arr.SetLineStyle(1)
    arr.SetAngle(60)
    arr.Draw("<|same")

    latex = ROOT.TLatex()
    latex.SetTextSize(0.03)
    latex.SetTextAlign(12)
    latex.SetNDC()
    latex.SetTextFont(42)
    latex.DrawLatex(0.65, 0.8, f"nToys: {len(significance_max)}")
    latex.DrawLatex(0.65, 0.76, f"p-value: {p_value:.4f}")
    latex.DrawLatex(0.65, 0.72, f"global significance: {global_significance:.1f}#sigma")
    latex.DrawLatex(0.65, 0.68, f"local significance: {significance_local:.1f}#sigma")


    outfile_name = "../results/global_significance"
    c.SaveAs(outfile_name + ".png")
    c.SaveAs(outfile_name + ".pdf")
    c.SaveAs(outfile_name + ".C")


def BiasTest(settings=dict()):

    Log_Path = os.path.basename(settings['Log_Path'])
    os.system("mkdir -p {outputdir}/bias_test".format(outputdir=settings['outputdir']))
    command = ""
    farm_dir = "Farm_BiasTest"
    os.system("mkdir -p {farm_dir}".format(farm_dir = farm_dir))

    for r in [0.0, 0.05, 0.1, 0.2, 1.0, 2.0]:
      r_min = r - 10
      r_max = r + 10
      condor = open(os.path.join(farm_dir, 'condor_{}.sub'.format(r)), 'w')
      condor.write('output = %s/job_common_$(cfgFile).out\n'%farm_dir)
      condor.write('error  = %s/job_common_$(cfgFile).err\n'%farm_dir)
      condor.write('log    = %s/job_common_$(cfgFile).log\n'%farm_dir)
      condor.write('executable = %s/$(cfgFile)\n'%farm_dir)
      condor.write('+JobFlavour = "microcentury"\n')
      condor.write('RequestCpus = 1\n')
      condor.write('queue 1 cfgFile in ')
      seed_numbers = random.sample(range(1, 1000000), 100)
      for seed in seed_numbers:
        shell_file = "bias_test_r{r}_seed{seed}.sh".format(r=r, seed=seed)
        command = "cd {outputdir}/bias_test\n".format(outputdir=settings['outputdir'])
        command += "combine -M GenerateOnly {workspace_root} -m 125  -t 20 --seed {seed} --saveToys  --toysFrequentist --bypassFrequentistFit --expectSignal {r} -n r_{r}_toys --rMax {r_max} --rMin {r_min} {command}\n".format(workspace_root = settings['workspace_root'], r = r, r_min = r_min, r_max = r_max, seed = seed, command = settings["command"])

        command += "combine -M MultiDimFit {workspace_root} --toysFrequentist  -m 125  -t 20 -n  r_{r}_toys_{seed} --toysFile higgsCombiner_{r}_toys.GenerateOnly.mH125.{seed}.root --algo singles --rMax {r_max} --rMin {r_min} {command}   --cminDefaultMinimizerStrategy {cminDefaultMinimizerStrategy} --cminDefaultMinimizerTolerance={cminDefaultMinimizerTolerance}\n".format(workspace_root = settings['workspace_root'], r = r, r_min = r_min, r_max = r_max, cminDefaultMinimizerStrategy=settings['cminDefaultMinimizerStrategy'], cminDefaultMinimizerTolerance=settings['cminDefaultMinimizerTolerance'], seed = seed, command = settings["command"])
#        command += "combine -M GenerateOnly {datacards} -t 10 --saveToys --toysFrequentist --bypassFrequentistFit --seed {seed} --expectSignal {r} -n r_{r}_toys --rMax {r_max} --rMin {r_min} {command}\n".format(datacards=settings['datacards'], r = r, r_min = r_min, r_max = r_max, seed = seed, command = settings["command"])
#        command += "combineTool.py -M FitDiagnostics {datacards}  --skipBOnlyFit -t 10 -n  r_{r}_toys_{seed} --toysFile higgsCombiner_{r}_toys.GenerateOnly.mH120.{seed}.root --rMax {r_max} --rMin {r_min} {command}   --cminDefaultMinimizerStrategy {cminDefaultMinimizerStrategy} --cminDefaultMinimizerTolerance={cminDefaultMinimizerTolerance}\n".format(datacards=settings['datacards'], r = r, r_min = r_min, r_max = r_max, cminDefaultMinimizerStrategy=settings['cminDefaultMinimizerStrategy'], cminDefaultMinimizerTolerance=settings['cminDefaultMinimizerTolerance'], seed = seed, command = settings["command"])
        prepare_shell(shell_file, command, condor, farm_dir, cmssw = True)
      condor.close()
      os.system('condor_submit {farm_dir}/condor_{r}.sub'.format(farm_dir = farm_dir, r = r))
    return

def BiasTestPlot(settings=dict()):

    Log_Path = os.path.basename(settings['Log_Path'])
    outputdir = "{outputdir}/bias_test".format(outputdir=settings['outputdir'])
    os.chdir(outputdir)

    truth_r = np.array([])
    fit_r_mean = np.array([])

    for r in [0.0, 0.5, 1.0, 1.5, 2.0]:

      truth_r = np.append(truth_r, r)
      r_fit_collection = np.array([])

      os.system("rm  higgsCombiner_"+str(r)+"_toys.root")
      os.system("hadd  higgsCombiner_{r}_toys.root  higgsCombiner_{r}_toys_*.root".format(r = r))

      ROOT.gStyle.SetOptStat(111)
      ROOT.gStyle.SetOptFit(1)

      f = ROOT.TFile.Open("higgsCombiner_"+str(r)+"_toys.root")

      t=f.Get("limit")
      hist_pull = ROOT.TH1F("", "Pull distribution: truth=%.2f" % (r), 80, -4, 4)
      hist_pull.GetXaxis().SetTitle("Pull = (r_{truth}-r_{fit})/#sigma_{fit}")
      hist_pull.GetYaxis().SetTitle("Entries")

      sigma_values = np.array([])

      for i_toy in range(int(t.GetEntries()/3)):
        # Best-fit value
        t.GetEntry(i_toy * 3)
        r_fit = getattr(t, "r")
        # -1 sigma value
        t.GetEntry(i_toy * 3 + 1)
        r_lo = getattr(t, "r")

        # +1 sigma value
        t.GetEntry(i_toy * 3 + 2)
        r_hi = getattr(t, "r")

        if((r_hi == (r-10.0)) or (r_lo == r-10.0)):
          continue

        r_fit_collection = np.append(r_fit_collection, r_fit)
        diff = r - r_fit
        # Use uncertainty depending on where mu_truth is relative to mu_fit
        if diff > 0:
          sigma = abs(r_hi - r_fit)
        else:
          sigma = abs(r_lo - r_fit)
        if sigma != 0:
          sigma_values = np.append(sigma_values, sigma)
        else:
          sigma = sigma_values.mean()

        if sigma != 0:
           hist_pull.Fill(diff / sigma)

      c1 = ROOT.TCanvas()
      hist_pull.Draw()
      ROOT.gStyle.SetOptFit(111)
      hist_pull.Fit("gaus")
      c1.SaveAs("../results/BiasTest_pulls_"+str(r).replace('.', 'p')+".png")
      c1.SaveAs("../results/BiasTest_pulls_"+str(r).replace('.', 'p')+".pdf")
      f.Close()

      ROOT.gStyle.SetOptStat(0)
      ROOT.gStyle.SetOptFit(0)

      fit_r_mean= np.append(fit_r_mean, np.mean(r_fit_collection))

    x_line = np.linspace(min(truth_r), max(truth_r), 100)  # Generate 100 points between min and max of x
    y_line = x_line  # For x = y, y values are the same as x

    plt.scatter(truth_r, fit_r_mean, color='blue', marker='o')
    plt.plot(x_line, y_line, color='red', linestyle='--')
    plt.xlabel('truth r')
    plt.ylabel('fit r (mean)')

    plt.title('truth r v.s. fitted r')
    plt.savefig("../results/BiasTest_fit_r_summary.pdf")
    plt.savefig("../results/BiasTest_fit_r_summary.png")

def FitDiagnostics(settings=dict()):

    CheckFile(settings['FitDiagnostics_file'],True)
    os.system('cd {outputdir}'.format(outputdir=settings['outputdir']))
    os.chdir("{outputdir}".format(outputdir=settings['outputdir']))
    workspace_root = os.path.basename(settings['workspace_root'])
    Log_Path = os.path.basename(settings['Log_Path'])


    if settings['unblind']:
        command = "combine -M FitDiagnostics {workspace_root} --saveShapes -m {mass} --saveWithUncertainties  --saveOverallShapes  -n _{year}_{region}_{channel}_{higgs}_{mass}_{coupling_value} --cminDefaultMinimizerStrategy {cminDefaultMinimizerStrategy} --cminDefaultMinimizerTolerance={cminDefaultMinimizerTolerance} --rMin {rMin} --rMax {rMax} {command}".format(workspace_root = workspace_root, year=settings['year'],channel=settings['channel'],higgs=settings['higgs'],mass=settings['mass'],coupling_value=settings['coupling_value'],rMin=settings['rMin'],rMax=settings['rMax'],  cminDefaultMinimizerStrategy=settings['cminDefaultMinimizerStrategy'], cminDefaultMinimizerTolerance=settings['cminDefaultMinimizerTolerance'],region=settings['region'], command = settings["command"])
    else:
        command = "combine -M FitDiagnostics {workspace_root} --saveShapes -m {mass} --saveWithUncertainties  --saveOverallShapes -t -1 --expectSignal {expectSignal} -n _{year}_{region}_{channel}_{higgs}_{mass}_{coupling_value} --cminDefaultMinimizerStrategy {cminDefaultMinimizerStrategy} --cminDefaultMinimizerTolerance={cminDefaultMinimizerTolerance} --rMin {rMin} --rMax {rMax} {command}".format(workspace_root = workspace_root, year=settings['year'],region=settings['region'], channel=settings['channel'],higgs=settings['higgs'],mass=settings['mass'],coupling_value=settings['coupling_value'],expectSignal=settings['expectSignal'],rMin=settings['rMin'],rMax=settings['rMax'],  cminDefaultMinimizerStrategy=settings['cminDefaultMinimizerStrategy'], cminDefaultMinimizerTolerance=settings['cminDefaultMinimizerTolerance'], command = settings["command"])

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


    command = 'python3 ../../HiggsAnalysis/CombinedLimit/test/diffNuisances.py {FitDiagnostics_file} --all -g {diffNuisances_File} --abs {command}'.format(FitDiagnostics_file=settings['FitDiagnostics_file'],diffNuisances_File=settings['diffNuisances_File'], command = settings["command"])
    print(ts+command+ns)
    command += ' >& {Log_Path}'.format(Log_Path=settings['Log_Path'])

    os.system(command)

    print("\033[0;34m* diffNuisances root file: \033[4m{}\033[0;m is created. ".format(settings['diffNuisances_File']))
    print("\nNext mode: [\033[0;32m PlotPulls \033[0;m]")


def PlotPulls(settings=dict()):
    if settings['year'] == 'run2':n_canvas = '10'
    elif settings['channel']  =='C':n_canvas ='20'
    else:n_canvas = '10'

    command = 'root -l -b -q '+"'PlotPulls.C"+'("{diffNuisances_File}","","_{year}_{region}_{channel}_{higgs}_{mass}_{coupling_value}",{n_canvas},"{year}")'.format(diffNuisances_File=settings['diffNuisances_File'],year=settings['year'],channel=settings['channel'],higgs=settings['higgs'],mass=settings['mass'],coupling_value=settings['coupling_value'],n_canvas=n_canvas,region=settings['region'])+"'"
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
        command = 'combineTool.py -M Impacts -d {workspace_root} --doInitialFit --robustFit 1 -m {mass}  --rMin {rMin} --rMax {rMax} {command} --cminDefaultMinimizerStrategy {cminDefaultMinimizerStrategy} --cminDefaultMinimizerTolerance={cminDefaultMinimizerTolerance} --X-rtd MINIMIZER_skipDiscreteIterations  --X-rtd MINIMIZER_freezeDisassociatedParams  --setCrossingTolerance 0.00005 --X-rtd MINIMIZER_multiMin_maskConstraints --X-rtd MINIMIZER_multiMin_hideConstants '.format(workspace_root=workspace_root,mass=settings['mass'],rMin=settings['rMin'],rMax=settings['rMax'], cminDefaultMinimizerStrategy=settings['cminDefaultMinimizerStrategy'], cminDefaultMinimizerTolerance=settings['cminDefaultMinimizerTolerance'], command = settings["command"])
        #command = 'combineTool.py -M Impacts -d {workspace_root} --doInitialFit --robustFit 1 -m {mass}  --rMin {rMin} --rMax {rMax} {command} --cminDefaultMinimizerStrategy {cminDefaultMinimizerStrategy} --cminDefaultMinimizerTolerance={cminDefaultMinimizerTolerance}'.format(workspace_root=workspace_root,mass=settings['mass'],rMin=settings['rMin'],rMax=settings['rMax'], cminDefaultMinimizerStrategy=settings['cminDefaultMinimizerStrategy'], cminDefaultMinimizerTolerance=settings['cminDefaultMinimizerTolerance'], command = settings["command"])
    else:
        command = 'combineTool.py -M Impacts -d {workspace_root} --doInitialFit --robustFit 1 -m {mass} -t -1 --expectSignal {expectSignal} --rMin {rMin} --rMax {rMax} {command} --cminDefaultMinimizerStrategy {cminDefaultMinimizerStrategy} --cminDefaultMinimizerTolerance={cminDefaultMinimizerTolerance} --X-rtd MINIMIZER_skipDiscreteIterations  --X-rtd MINIMIZER_freezeDisassociatedParams  --setCrossingTolerance 0.00005 --X-rtd MINIMIZER_multiMin_maskConstraints --X-rtd MINIMIZER_multiMin_hideConstants '.format(workspace_root=workspace_root,mass=settings['mass'],expectSignal=settings['expectSignal'],rMin=settings['rMin'],rMax=settings['rMax'], cminDefaultMinimizerStrategy=settings['cminDefaultMinimizerStrategy'], cminDefaultMinimizerTolerance=settings['cminDefaultMinimizerTolerance'], command = settings["command"])

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
        command = 'combineTool.py -M Impacts -d {workspace_root} --doFits --robustFit 1 -m {mass} --rMin {rMin} --rMax {rMax} {command} --cminDefaultMinimizerStrategy {cminDefaultMinimizerStrategy} --cminDefaultMinimizerTolerance={cminDefaultMinimizerTolerance} --job-mode condor --task-name {year}-{region}-{channel}-{coupling_value}-M{higgs}{mass} --X-rtd MINIMIZER_skipDiscreteIterations  --X-rtd MINIMIZER_freezeDisassociatedParams  --setCrossingTolerance 0.00005 --X-rtd MINIMIZER_multiMin_maskConstraints --X-rtd MINIMIZER_multiMin_hideConstants '.format(workspace_root=workspace_root,year=settings['year'],channel=settings['channel'],higgs=settings['higgs'],mass=settings['mass'],coupling_value=settings['coupling_value'],rMin=settings['rMin'],rMax=settings['rMax'], cminDefaultMinimizerStrategy=settings['cminDefaultMinimizerStrategy'], cminDefaultMinimizerTolerance=settings['cminDefaultMinimizerTolerance'], region=settings['region'], command = settings["command"])+'--sub-opts='+"'+JobFlavour="+'"tomorrow"'+"'"
    else:
        command = 'combineTool.py -M Impacts -d {workspace_root} --doFits --robustFit 1 -m {mass} -t -1 --expectSignal {expectSignal} --rMin {rMin} --rMax {rMax} {command} --cminDefaultMinimizerStrategy {cminDefaultMinimizerStrategy} --cminDefaultMinimizerTolerance={cminDefaultMinimizerTolerance} --job-mode condor --task-name {year}-{region}-{channel}-{coupling_value}-M{higgs}{mass} --X-rtd MINIMIZER_skipDiscreteIterations  --X-rtd MINIMIZER_freezeDisassociatedParams  --setCrossingTolerance 0.00005 --X-rtd MINIMIZER_multiMin_maskConstraints --X-rtd MINIMIZER_multiMin_hideConstants '.format(workspace_root=workspace_root,year=settings['year'],channel=settings['channel'],higgs=settings['higgs'],mass=settings['mass'],coupling_value=settings['coupling_value'],expectSignal=settings['expectSignal'],rMin=settings['rMin'],rMax=settings['rMax'], cminDefaultMinimizerStrategy=settings['cminDefaultMinimizerStrategy'], cminDefaultMinimizerTolerance=settings['cminDefaultMinimizerTolerance'],region=settings['region'], command = settings["command"])+'--sub-opts='+"'+JobFlavour="+'"tomorrow"'+"'"


    print(ts+command+ns)
    command += ' >& {}'.format(Log_Path)
    os.system(command)

    print("\nNext mode: [\033[0;32m Plot_Impacts \033[1;33m]")
    print("\033[1;33m* You need to wait for the condor job is done, then move to the next step [Plot_Impacts]. \033[0;m")

def Plot_Impacts(settings=dict()):

    print("\033[0;35mcd {outputdir}\033[0;m -> Your current work directory".format(outputdir=settings['outputdir']))
    os.chdir(settings['outputdir'])
    Log_Path = os.path.basename(settings['Log_Path'])

    os.system("mv *{year}-{region}-{channel}-{coupling_value}-M{higgs}{mass}*.err err".format(year=settings['year'],region=settings['region'],channel=settings['channel'],coupling_value=settings['coupling_value'],higgs=settings['higgs'],mass=settings['mass']))
    os.system("mv *{year}-{region}-{channel}-{coupling_value}-M{higgs}{mass}*.log log_condor".format(year=settings['year'],region=settings['region'],channel=settings['channel'],coupling_value=settings['coupling_value'],higgs=settings['higgs'],mass=settings['mass']))
    os.system("mv *{year}-{region}-{channel}-{coupling_value}-M{higgs}{mass}*.out output".format(year=settings['year'],region=settings['region'],channel=settings['channel'],coupling_value=settings['coupling_value'],higgs=settings['higgs'],mass=settings['mass']))
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
    command = 'plotImpacts.py -i  {impacts_json} -o {impacts_json_prefix} {command}'.format(impacts_json=settings['impacts_json'],impacts_json_prefix=settings['impacts_json'].replace(".json",""), command = settings['command'])

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
            if category not in Histogram_Names:
                Histogram_Names.append(category)

    Histogram = OrderedDict()
    Integral= OrderedDict()

    for category in Histogram_Names:
        if ('TotalSig' in category) or  ('TotalProcs' in category):continue #In PostFitWorkspace
        if ('total_overall' in category) or ('total_signal' in category) or ('total' == category) or ('overall_total_covar' in category) or ('total_covar' in category): continue #In Fitdiagnostics
        if category == 'data_obs': category = 'Data' # In PostFitWorkspace, for postFit

        if category == 'data': #For preFit
            category = 'Data' # In FitDiagnostics
        elif category == 'total_background':
            category = 'TotalBkg'
        #Histogram[category] = ROOT.TH1F(category, '', len(binning) - 1, binning)
        Integral[category] = 0

    Maximum = -1
    Histogram_Registered = False
    for first_level in RootLevel.GetListOfKeys():
        first_level_name = first_level.GetName()
        print(first_level_name)
        if not(settings['shape_type'].lower() in first_level_name) and settings['shape_type'].lower() == 'postfit':
            continue
        if type(RootLevel.Get(first_level_name)) !=  ROOT.TDirectoryFile: continue

        for second_level in RootLevel.Get(first_level_name).GetListOfKeys():
            category = second_level.GetName()

            if (category =='TotalSig') or  (category == 'TotalProcs'):continue # In PostfitWorkspace
            if ('total_overall' in category) or ('total_signal' in category) or ('total' == category) or ('overall_total_covar' in category) or ('total_covar' in category): continue #In Fitdiagnostics
            fpath = first_level_name + '/' + category
    #        if settings['shape_type'].lower()  == 'postfit' and 'CG' in category:
    #            fpath = fpath.replace('postfit', 'prefit') # preFit make the signal looks significant
            h = RootLevel.Get(fpath).Clone()
            if type(h) != ROOT.TH1F and type(h) != ROOT.TGraphAsymmErrors: raise TypeError('No such Histogram in file: {}'.format(fpath))


            if isinstance(h, ROOT.TH1):
                # Binning from TH1
                nbin = h.GetNbinsX()
                bin_edges = [h.GetBinLowEdge(i + 1) for i in range(nbin)]
                bin_edges.append(h.GetBinLowEdge(nbin) + h.GetBinWidth(nbin))
            else:
               # Binning from TGraphAsymmErrors
               n_points = h.GetN()
               bin_edges = [h.GetX()[i] - h.GetErrorXlow(i) for i in range(n_points)]
               bin_edges.append(h.GetX()[n_points - 1] + h.GetErrorXhigh(n_points - 1))

            print(bin_edges)
            h_postfix = ROOT.TH1F(fpath, 'h', len(bin_edges) - 1, array('d', bin_edges))



            nbin = h_postfix.GetNbinsX()

            for ibin in range(nbin):

                if category == 'data_obs' or category == 'data':
                    if settings['shape_type'].lower()  == 'prefit':
                        # h is TGraphAsymmetryError in prefit case. See FitDiagnostics file.
                        error = h.GetErrorY(ibin)
                        bincontent = h.Eval(ibin + 0.5) #Graph
                    else:
                        error   = h.GetBinError(ibin+1) # just symmetrical error
                        bincontent = h.GetBinContent(ibin+1)
                    h_postfix.SetBinError(ibin+1, error)
                    print(bincontent, error, category, ibin)

                else:
                    bincontent = h.GetBinContent(ibin+1)
                    h_postfix.SetBinError(ibin+1,  h.GetBinError(ibin+1))
                h_postfix.SetBinContent(ibin+1, bincontent) # Modify the x-axis value

            if category == 'data_obs' or category == 'data':
                category = 'Data'
            elif category == 'total_background':
                category = 'TotalBkg'

            region_name = first_level_name.replace('_prefit', '').replace('_postfit', '').replace('era', '')
            if region_name not in Histogram:
                Histogram[region_name] = dict()
            Integral[category] += h_postfix.Integral()
            Histogram[region_name][category] = h_postfix.Clone()

            print('Access Histogram {fpath}'.format(fileName = outputFile, RootLevel = RootLevel, fpath = fpath))
    for region_ in Histogram:
      for category in Histogram[region_]:
        if ('TotalSig' in category) or  ('TotalProcs' in category):continue
        if ('total_overall' in category) or ('total_signal' in category) or ('total' == category) or ('overall_total_covar' in category) or ('total_covar' in category): continue #In Fitdiagnostics
        if category == 'total_background':
            category = 'TotalBkg'
        elif category == 'data_obs' or category == 'data': category = 'Data'
        if Maximum < Histogram[region_][category].GetMaximum():
            Maximum = Histogram[region_][category].GetMaximum()

    if settings['combined']:
        Histogram_merged       = dict()
        for region_ in Histogram:
            if settings['region'] == 'C':
                region_out = region_.replace("2016postapv_", "").replace("2017_", "").replace("2018_", "").replace("2016apv_", "").replace('era','')
            else:
                region_out = region_.replace('era', '').replace('merged_resolved', '')
                region_out += f"_{settings['region']}"
            if region_out not in Histogram_merged: Histogram_merged[region_out] = dict()
            for category in Histogram[region_]:
                if category not in Histogram_merged[region_out]:
                    Histogram_merged[region_out][category] = Histogram[region_][category].Clone()
                else:
                    Histogram_merged[region_out][category].Add(Histogram[region_][category].Clone())
                print(region_, category, Histogram[region_][category].GetBinContent(1), Histogram[region_][category].GetBinError(1))
        Histogram = Histogram_merged

#    for name in Histogram_merged:
#        for process in Histogram_merged[name]:
#          print(name, process, Histogram_merged[name][process].GetBinContent(1), Histogram_merged[name][process].GetBinError(1))


    Histogram_concatenated = dict()
    region_binning         = dict()


    for region_ in Histogram:

        Histogram_concatenated_tmp = dict()
        region_binning_tmp        = dict()
        Integral_tmp              =dict()
        year_tmp = settings['year']
        for year_candidate in ['2016apv', '2016postapv', '2017', '2018']:
          if year_candidate in region_:
              year_tmp = year_candidate


        for category in Histogram_Names:
            # print("gkole->", Histogram.keys())
            if ('TotalSig' in category) or ('TotalProcs' in category):
                continue
            if ('total_overall' in category) or ('total_signal' in category) or ('total' == category) or ('overall_total_covar' in category) or ('total_covar' in category):
                continue  # In Fitdiagnostics
            if category == 'total_background':
                category = 'TotalBkg'
            elif category == 'data_obs' or category == 'data':
                category = 'Data'


            if category not in Histogram[region_]:
                htemp = Histogram[region_]["TotalBkg"].Clone()
                for ibin in range(htemp.GetNbinsX() + 2):
                  htemp.SetBinContent(ibin, 0)
                  htemp.SetBinError(ibin, 0)

            else:
                htemp = Histogram[region_][category]

            region_name = region_ if settings['region'] == 'C' else region_ + f"_{settings['region']}"
            Histogram_concatenated_tmp[category] = htemp.Clone()
            Integral_tmp[category] = htemp.Integral()

        shape_type = settings['shape_type'].lower()
        if settings['shape_type'].lower() == 'prefit':
            Title = 'Pre-Fit Distribution'
        else:
            Title = 'Post-Fit Distribution'

        # may be redifine a histogram and add the bin content and error
        for region_candidate in settings['region_info']:
          print(region_candidate, region_)
          if region_candidate in region_:
            correct_region = region_candidate

        # ABCD method bins only use 1 bin (Poisson)
        isABCD = False
        for ABCD_region in ['CRb', 'CRc', 'CRd']:
            if ABCD_region in region_:
                isABCD = True

        xaxisTitlestring = 'mass'
        if correct_region.startswith('CR'):
            new_binning = settings['region_info'][correct_region]['POI_binnings']['Normal'] if not isABCD else [0, 1]
            xaxisTitlestring = settings['region_info'][correct_region]['POI_name']
            redefine_binning(Histogram_concatenated_tmp, new_binning)
        elif correct_region.startswith('SR'):
            # check if the DNNMASS bin present or not
            print (settings['region_info'][correct_region]["POI"][0]+settings['mass'])
            xaxisTitlestring = settings['region_info'][correct_region]['POI_name'].replace('MASS', settings['mass'])
            print("xaxisTitlestring ", xaxisTitlestring)
            temp_string = settings['region_info'][correct_region]["POI"][0]+settings['mass']
            if temp_string in settings['region_info'][correct_region]['POI_binnings']:
                new_binning = settings['region_info'][correct_region]['POI_binnings'][temp_string] if not isABCD else [0, 1]
                redefine_binning(Histogram_concatenated_tmp, new_binning)
            else:
                new_binning = settings['region_info'][correct_region]['POI_binnings']['Normal'] if not isABCD else [0, 1]
                redefine_binning(Histogram_concatenated_tmp, new_binning)


        else:
            print ('Region musts name with CR_1b4j or SR')


        for category in Histogram_concatenated_tmp:
           htemp = Histogram_concatenated_tmp[category]
           if category not in Histogram_concatenated:
                Histogram_concatenated[category] = htemp.Clone()
           else:
                Histogram_concatenated[category] = combine_histograms(Histogram_concatenated[category], htemp)

           if region_ not in region_binning:
                region_binning[region_name] = [Histogram_concatenated[category].GetNbinsX() - htemp.GetNbinsX(), Histogram_concatenated[category].GetNbinsX()]
                region_binning_tmp[region_name] = [0, htemp.GetNbinsX()]

        print(os.path.join(CURRENT_WORKDIR, os.path.join(settings['outputdir'], shape_type, year_tmp, f"{settings['shapePlot']}_{region_}")))
        CheckDir(os.path.join(CURRENT_WORKDIR, os.path.join(settings['outputdir'], shape_type, year_tmp)))
        template_settings = {
            "Maximum": Maximum,
            "Integral": Integral_tmp,
            "Histogram": Histogram_concatenated_tmp,
            "outputfilename": os.path.join(CURRENT_WORKDIR, os.path.join(settings['outputdir'], shape_type, year_tmp, f"{settings['shapePlot']}_{region_}")),
            "year": year_tmp,
            "Title": Title,
            "xaxisTitle": xaxisTitlestring,
            "yaxisTitle": 'Events/bin',
            "channel": settings['channel'],
            "coupling_value": settings['coupling_value'],
            "mass": settings["mass"],
            "text_y": settings["text_y"],
            "logy": settings["logy"],
            "unblind": settings['unblind'],
            "expectSignal": settings['expectSignal'],
            "plotRatio": settings['plotRatio'],
            "paper": settings['paper'],
            "Region_binning": region_binning_tmp,
            "region_info": settings['region_info'],
            "combined": settings['combined'],
            "pull": settings['pull'],
            'shape_type': settings['shape_type'].lower(),
            'xaxisSize': 1500,
            'stack_signal': settings['stack_signal']
        }
        template_settings["Signal_Name"] = settings['signal_name']
        print("\n")
        Plot_Histogram(template_settings=template_settings)


    shape_type = settings['shape_type'].lower()

    if settings['shape_type'].lower() == 'prefit':
        Title = 'Pre-Fit Distribution'
    else:
        Title = 'Post-Fit Distribution'


    template_settings= {
            "Maximum":Maximum,
            "Integral":Integral,
            "Histogram":Histogram_concatenated,
            "outputfilename":os.path.join(CURRENT_WORKDIR,os.path.join(settings['outputdir'], shape_type, 'unrolled')),
            "year":settings['year'],
            "Title":Title,
            "xaxisTitle":"",
            "yaxisTitle":'Events/bin',
            "channel":settings['channel'],
            "coupling_value":settings['coupling_value'],
            "mass":settings["mass"],
            "text_y":settings["text_y"],
            "logy":settings["logy"],
            "unblind":settings['unblind'],
            "expectSignal":settings['expectSignal'],
            "plotRatio":settings['plotRatio'],
            "paper":settings['paper'],
            "Region_binning": region_binning,
            "region_info": settings['region_info'],
            "combined": settings['combined'],
            "pull": settings['pull'],
            'shape_type': settings['shape_type'].lower(),
            'xaxisSize': 6500,
            'stack_signal': settings['stack_signal']
            }
    #if settings["unblind"] or settings["expectSignal"]:
    template_settings["Signal_Name"] = settings['signal_name']
    #else:
    #  template_settings["Signal_Name"] = "DEFAULT"
    print("\n")
    #template_settings["Signal_Name"] = template_settings["Signal_Name"].replace("01","04").replace("10","04")

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
    #tdrstyle.setTDRStyle()
    print("\n\033[0;35mPlotting Histogram...\033[0;m")
    Color_Dict = Color_Dict_ref
    if template_settings["unblind"]:
        Color_Dict['Data'] = ROOT.kBlack
    #if template_settings["unblind"] or template_settings["expectSignal"]:
    Color_Dict[template_settings["Signal_Name"]] = ROOT.kBlack
    print(template_settings["Signal_Name"])


    #### Canvas ####
    ROOT.gStyle.SetOptTitle(0)
    ROOT.gStyle.SetOptStat(0)
    #ROOT.gStyle.SetErrorX(0.001)
    ROOT.gROOT.SetBatch(1)

    if template_settings['plotRatio']:
      if template_settings['combined']:
        canvas = ROOT.TCanvas("","",template_settings['xaxisSize'],1500)
      else:
        canvas = ROOT.TCanvas("","",template_settings['xaxisSize'],1500)

    else:
      canvas = ROOT.TCanvas("","",500,500)

    Set_Logy = template_settings['logy']

    if template_settings['plotRatio']:
      pad1 = ROOT.TPad('pad1','',0.00, 0.25, 1, 1)
      pad2 = ROOT.TPad('pad2','',0.00, 0.00, 1, 0.25)
      pad1.SetBottomMargin(0.02)
      pad1.SetLeftMargin(0.16)
      pad1.SetRightMargin(0.04)
      if template_settings['pull']:
        pad2.SetTopMargin(0.008);
      else:
        pad2.SetTopMargin(0.005);
      pad2.SetLeftMargin(0.16)
      pad2.SetRightMargin(0.04)
      pad2.SetBottomMargin(0.40);
      pad1.SetBorderMode(1)
      pad2.SetBorderMode(1)
      pad1.SetTicks(1,1)
      pad2.SetTicks(1,1)
      # pad2.SetGrid(5,5)
      if not template_settings['combined']:
        pad1.SetLeftMargin(0.1)
        pad2.SetLeftMargin(0.1)

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
        Histogram_MaximumScale = 100000
    else:
        Histogram_MaximumScale = 2.0

    canvas.SetGrid(1,1)
    canvas.SetLeftMargin(0.12)
    canvas.SetRightMargin(0.08)
    ###############

    #### Legend ####
    legend_NCol = int(len(Color_Dict.keys())/5)
    legend = ROOT.TLegend(.12, .62, .95, .87);
    legend.SetNColumns(legend_NCol)
    legend.SetBorderSize(0);
    legend.SetFillColor(0);
    legend.SetShadowColor(0);
    legend.SetTextFont(42);
    if not template_settings['plotRatio']:
      legend.SetTextSize(0.045);
    else:
      legend.SetTextSize(0.045);
      legend2 = ROOT.TLegend(.12, .83, .25, .97);
      legend2.SetBorderSize(0);
      legend2.SetFillColor(0);
      legend2.SetShadowColor(0);
      legend2.SetTextFont(42);
      legend2.SetTextSize(0.14);
    #### Ordered_Integral ####
    Ordered_Integral = OrderedDict(sorted(template_settings['Integral'].items(), key=itemgetter(1)))
    ##########################

    if template_settings['unblind']:
      nDigits = int(np.log10(template_settings['Integral']["Data"]))+1
      for idx, Histogram_Name in enumerate(Ordered_Integral):
        if Histogram_Name == "Data": continue
        template_settings['Integral'][Histogram_Name] += 1e-6
        #print(Histogram_Name, Yield)
        #if int(np.log10(Yield))+1 >= nDigits:
        #  template_settings['Integral'][Histogram_Name] = (str(Yield)[:nDigits])
        #else:
        #  template_settings['Integral'][Histogram_Name] = (str(Yield)[:nDigits+1])

    #### Histogram Settings ####
    h_stack = ROOT.THStack()
    h_stack.SetName("stack")
    hh_total = None
    hh_total = template_settings['Histogram']['TotalBkg'].Clone()
    h_sig = None
    mass = ''

    for Histogram_Name in Ordered_Integral:
        if template_settings["Signal_Name"] in Histogram_Name and template_settings["Signal_Name"] != "DEFAULT":
            if h_sig is None:
              h_sig = template_settings['Histogram'][Histogram_Name].Clone()
              h_sig.SetLineColor(Color_Dict[template_settings["Signal_Name"]]) # Histogram_Name = Signal_Name + ("_2b" or "_3b")
              h_sig.SetLineWidth(5)
            else:
              h_sig.Add(template_settings['Histogram'][Histogram_Name].Clone())
            mass = Histogram_Name.replace('CGToBHpm_a_', '').replace('_rtt06_rtc04', '').replace('_2b', '').replace('_3b', '')
        else:
            if Histogram_Name == 'Data':
                if template_settings['unblind']:
#                    legend.AddEntry(template_settings['Histogram'][Histogram_Name],Histogram_Name, 'PE') #+' [{:.0f}]'.format(template_settings['Integral'][Histogram_Name]) , 'PE')
                    legend.AddEntry(template_settings['Histogram'][Histogram_Name], Histogram_Name, 'PE')
                    template_settings['Histogram'][Histogram_Name].SetMarkerStyle(8)
                    template_settings['Histogram'][Histogram_Name].SetMarkerSize(3.5)
                    template_settings['Histogram'][Histogram_Name].SetMarkerColor(1)
                    template_settings['Histogram'][Histogram_Name].SetLineWidth(4)
                    template_settings['Histogram'][Histogram_Name].SetLineColor(1)
            else:
                if Histogram_Name == 'TotalBkg': continue
                template_settings['Histogram'][Histogram_Name].SetFillColorAlpha(Color_Dict[Histogram_Name],0.65)
                template_settings['Histogram'][Histogram_Name].SetLineWidth(0)
                h_stack.Add(template_settings['Histogram'][Histogram_Name])
                print(Histogram_Name, template_settings['Integral'][Histogram_Name])
                #legend.AddEntry(template_settings['Histogram'][Histogram_Name],Histogram_Name.replace("TTTo2L","t#bar{t}").replace("ttW","t#bar{t}W").replace("ttH","t#bar{t}H"), 'F') # + ' [{:.0f}]'.format(template_settings['Integral'][Histogram_Name]), 'F')
                #legend.AddEntry(template_settings['Histogram'][Histogram_Name],Histogram_Name.replace("TT","t#bar{t}").replace("ttW","t#bar{t}W").replace("ttX","t#bar{t}X").replace("QCD", "NonPrompt"), 'F') # + ' [%.1f]'%(float(template_settings['Integral'][Histogram_Name])), 'F')

    for Histogram_Name in reversed(Ordered_Integral):
        if template_settings["Signal_Name"] in Histogram_Name and template_settings["Signal_Name"] != "DEFAULT":
            continue
        else:
            if Histogram_Name == 'Data':
               continue
            else:
                if Histogram_Name == 'TotalBkg': continue
                legend.AddEntry(template_settings['Histogram'][Histogram_Name],Histogram_Name.replace("TT","t#bar{t}").replace("tt","t#bar{t}").replace("QCD", "NonPrompt").replace('SingleTop', 'Single t').replace('DY', 'Z+jets').replace('WJets', 'W+jets'), 'F') 

    h_stack.SetTitle("{};{};Events/bin ".format(template_settings['Title'], template_settings['xaxisTitle']))

    h_stack.SetTitle("{};{};Events/bin ".format(template_settings['Title'], template_settings['xaxisTitle']))
    h_stack.SetMaximum(h_stack.GetStack().Last().GetMaximum() * Histogram_MaximumScale)
    if Set_Logy:
      h_stack.SetMinimum(.1)
    else:
      h_stack.SetMinimum(0.1)
    h_stack.Draw()
    h_stack.GetYaxis().SetTitle("Events/bin")
    if template_settings['plotRatio']:
      h_stack.GetYaxis().SetTitleSize(0.05) # THStack should first be drawn and then can do this step
      h_stack.GetYaxis().SetLabelSize(0.05)
      h_stack.GetYaxis().SetTitleOffset(1.06)
      h_stack.GetXaxis().SetLabelOffset(3.2)
    else:
      h_stack.GetYaxis().SetTitleSize(0.03) # THStack should first be drawn and then can do this step
      h_stack.GetYaxis().SetLabelSize(0.03)
      h_stack.GetYaxis().SetTitleOffset(1.5)
      h_stack.GetXaxis().SetTitleOffset(0.5)
      h_stack.GetXaxis().SetLabelSize(0.03)
    h_stack.GetXaxis().SetTitleSize(0.05)
    h_stack.GetYaxis().SetTickLength(0.02)
#    pad1.Modified()
#    pad1.Update()
    h_stack.Draw("HIST")
    # For uncert.
    hh_total.SetFillStyle(3345)
    hh_total.SetFillColor(ROOT.kGray + 2)
    hh_total.SetMarkerSize(0)
    hh_total.SetLineWidth(100)
    print("Integral of TotalBkg: ", hh_total.Integral())
    print("Content of TotalBkg: ", hh_total.GetBinContent(1))
    print("Error of TotalBkg: ", hh_total.GetBinError(1))
    hh_total.Draw("E2 SAME")
    legend.AddEntry(hh_total,'Syst unc.','F')

    sep_line = dict()
    sep_line_ratio = dict()
    label_text = dict()
    for region_ in template_settings['Region_binning']:
        x_line = template_settings['Region_binning'][region_][1]
        x_text = (hh_total.GetBinLowEdge(template_settings['Region_binning'][region_][0] + 1) + hh_total.GetBinLowEdge(template_settings['Region_binning'][region_][1] + 1)) / 2
        sep_line[region_] = ROOT.TLine(x_line, 0, x_line, hh_total.GetMaximum()* 1.2)
        sep_line[region_].SetLineColor(ROOT.kBlack)
        sep_line[region_].SetLineStyle(2)
        sep_line[region_].SetLineWidth(5)
        #sep_line[region_].Draw()

        region_name = ''
        channel_name = ''
        region_list = []

        for era_candidate in ['16apv', '16postapv', '2017', '2018']:
          if era_candidate in region_:
            era_name = era_candidate
            if era_candidate == '16apv':
              era_name = '16pre'
            elif era_candidate == '16postapv':
              era_name = '16post'
            region_list.append(era_name)
        for region_candidate in template_settings['region_info']:
            if region_candidate in region_:
                region_name = region_candidate.replace('SR_','').replace('CR_', '')
                region_list.append(region_name)
        for QCD_ABCD in ["CRb", "CRc", "CRd"]:
            if QCD_ABCD in region_:
              region_list = [QCD_ABCD.replace("CR", "")]
        for channel_ in ['ele_resolved', 'mu_resolved', 'merged_resolved']:
          if channel_ in region_:
            channel_name = channel_.replace('_resolved', '').replace('ele', 'e').replace('mu', '#mu')
            region_list.append(channel_name)
        print(region_list)
        region_list_final = [', '.join(region_list[::-1])]
        for region_height, region_text in enumerate(region_list_final):
          if Set_Logy: y_text_log = 10**((2.2 - 0.5 * region_height)) * hh_total.GetMaximum() / 10
          else: y_text_log = (1.1 - 0.05 * region_height) * hh_total.GetMaximum()
          print(x_text, y_text_log,  region_text)
          label_text[region_ + region_text] = ROOT.TLatex(x_text, y_text_log,  region_text)
          label_text[region_ + region_text].SetTextAlign(22)  # Center align
          label_text[region_ + region_text].SetTextSize(0.05)
          label_text[region_ + region_text].SetTextFont(42)
          label_text[region_ + region_text].Draw("SAME")


    if type(h_sig )== ROOT.TH1F and not template_settings["stack_signal"]:
        h_sig.Scale(2.5)
        h_sig.Draw("HIST SAME")
        legend.AddEntry(h_sig,'m_{H^{#pm}} = ' + mass + ' GeV (x2.5)', 'L')
    if template_settings['unblind']:
        template_settings['Histogram']["Data"].SetMarkerSize(2)
        template_settings['Histogram']["Data"].Draw("SAME EP")
    if template_settings['plotRatio']:
        pad2.cd()
        hMC     = h_stack.GetStack().Last()
        h_ratio = (template_settings['Histogram']["Data"].Clone())
        h_data = (template_settings['Histogram']["Data"].Clone())
        # h_ratio.Sumw2()
        hh_total_sumw2 = hh_total.Clone()
        for bin_idx in range(1, hh_total_sumw2.GetNbinsX() + 1):
          bin_content = hh_total_sumw2.GetBinContent(bin_idx)
          poisson_error = bin_content**0.5 if bin_content > 0 else 0
          hh_total_sumw2.SetBinError(bin_idx, poisson_error)

        if template_settings['pull']:
            for bin_idx in range(1, h_ratio.GetNbinsX() + 1):
                if h_data.GetBinError(bin_idx) == 0:
                  unc = 1.0
                else:
                  unc =  h_data.GetBinError(bin_idx)
                bin_content = (h_data.GetBinContent(bin_idx) - hh_total.GetBinContent(bin_idx)) / unc
                bin_error   = h_data.GetBinError(bin_idx) / unc
                h_ratio.SetBinContent(bin_idx, bin_content)
                h_ratio.SetBinError(bin_idx, bin_error)

            h_ratio_max = 6 if template_settings['shape_type'] == 'postfit' else 105.0
            h_ratio_min = -6 if template_settings['shape_type'] == 'postfit' else -105.0
            h_ratio.GetYaxis().SetTitle("#frac{data-MC}{#sigma_{data}}")

        else:
            h_ratio.Divide(hh_total_sumw2)
            h_ratio_max = 1.3
            h_ratio_min = 0.7
            h_ratio.GetYaxis().SetTitle("Obs/Exp")

        h_ratio.SetMaximum(h_ratio_max)
        h_ratio.SetMinimum(h_ratio_min)
        h_ratio.SetMarkerStyle(20)
        h_ratio.SetMarkerSize(3.5)
        h_ratio.SetMarkerColor(1)
        h_ratio.SetLineWidth(3)

        h_ratio.GetYaxis().CenterTitle()
        h_ratio.GetYaxis().SetNdivisions(4)
        h_ratio.GetYaxis().SetTitleOffset(0.28)
        h_ratio.GetYaxis().SetTitleSize(0.15)
        h_ratio.GetYaxis().SetLabelSize(0.14)
        h_ratio.GetYaxis().SetTickLength(0.02)
        h_ratio.GetXaxis().SetLabelSize(0.14)
        h_ratio.GetXaxis().SetTitleOffset(1.0)
        h_ratio.GetXaxis().SetTitleSize(0.15)
        if h_stack.GetXaxis().GetTitle().startswith('pDNN'):
            h_ratio.GetXaxis().SetTitle("pDNN score")
        else:
           h_ratio.GetXaxis().SetTitle(h_stack.GetXaxis().GetTitle())
        if template_settings['unblind']:
          h_ratio.SetMarkerSize(1)
          h_ratio.Draw("P E")
        else:
          h_ratio.Draw("AXIS")

        for region_ in template_settings['Region_binning']:
            x_line = template_settings['Region_binning'][region_][1]
            sep_line_ratio[region_] = ROOT.TLine(x_line, h_ratio_min, x_line, h_ratio_max)
            sep_line_ratio[region_].SetLineColor(ROOT.kBlack)
            sep_line_ratio[region_].SetLineStyle(2)
            sep_line_ratio[region_].SetLineWidth(5)
            sep_line_ratio[region_].Draw("SAME")

            y_text = h_ratio_min - (h_ratio_max - h_ratio_min) * 0.25

            print('region', region_)
            for region_candidate in template_settings['region_info']:
                if region_candidate in region_:
                    region_name = region_candidate
            x_text = (template_settings['Region_binning'][region_][0] + template_settings['Region_binning'][region_][1]) / 2
            label_text[region_ + region_text + "axis"] = ROOT.TLatex(x_text, y_text, template_settings['region_info'][region_name]["POI_name"].replace("MASS", template_settings['mass']))
            label_text[region_ + region_text + "axis"].SetTextAlign(22)  # Center align
            label_text[region_ + region_text + "axis"].SetTextSize(0.16)
            label_text[region_ + region_text + "axis"].SetTextFont(42)
            #label_text[region_ + region_text + "axis"].Draw("SAME")

        x = []
        y = []
        xerror_l = []
        xerror_r = []
        yerror_u = []
        yerror_d = []

        for i in range(0,h_ratio.GetNbinsX()):
          x.append(h_ratio.GetBinCenter(i+1))
          xerror_l.append(0.5*h_ratio.GetBinWidth(i+1))
          xerror_r.append(0.5*h_ratio.GetBinWidth(i+1))
          # print (h_ratio.GetBinContent(i+1)*math.pow(math.pow(template_settings['Histogram']["Data"].GetBinError(i+1) / template_settings['Histogram']["Data"].GetBinContent(i+1), 2)+math.pow(hh_total.GetBinError(i+1)/hMC.GetBinContent(i+1),2),0.5))
          # print ("black point error: ",h_ratio.GetBinError(i+1))
          # print ("old band", hh_total.GetBinError(i+1)/hMC.GetBinContent(i+1))
          if hMC.GetBinContent(i+1) > 0.0:
            err_tmp = hh_total.GetBinError(i+1)/hMC.GetBinContent(i+1)
          else:
            err_tmp = 0.0

          if template_settings['pull']:
              y.append(0.0)
              if h_data.GetBinError(i+1) == 0:
                yerror_u.append(0.0)
                yerror_d.append(0.0)
              else:
                yerror_u.append( hh_total.GetBinError(i+1) / h_data.GetBinError(i+1))
                yerror_d.append( hh_total.GetBinError(i+1) / h_data.GetBinError(i+1))
          else:
              y.append(1.0)
              yerror_u.append(err_tmp)
              yerror_d.append(err_tmp)

        ru = ROOT.TGraphAsymmErrors(len(x), np.array(x), np.array(y),np.array(xerror_l),np.array(xerror_r), np.array(yerror_d), np.array(yerror_u))
        ru.SetFillStyle(3345)
        ru.SetFillColor(ROOT.kGray+3)
        #ru.SetFillColor(ROOT.kOrange-3) #ROOT.TColor.GetColor("#e76300")
        ru.SetMarkerSize(0)
        ru.SetLineWidth(100)
        legend2.AddEntry(ru, 'Syst unc./Stat unc.', 'F')
#        ru.SetFillStyle(3005)
        ru.Draw("SAME 2")
        legend2.Draw("SAME E2")
        if template_settings['unblind']:
          h_ratio.SetMarkerSize(1)
          h_ratio.Draw("P E SAME")
        #  print("in unblind if h_ratio.GetXaxis().GetTitle() = ", h_ratio.GetXaxis().GetTitle())
        pad1.cd()

    ###########################
    #value = int(template_settings['coupling_value'].split(coupling)[-1]) * 0.1
    legend.Draw("SAME")

    latex = ROOT.TLatex()
    latex.SetTextSize(0.05)
    latex.SetTextAlign(12)
    latex.SetNDC()
    latex.SetTextFont(42)
    #latex.DrawLatex(0.180, 0.59, "#rho_{t%s} = %.1f,  m_{A} = %s GeV"%(quark, value,template_settings['mass']))

    ### CMS Pad #####

    import CMS_lumi
    CMS_lumi.writeExtraText = 1
    if template_settings['paper']:
      CMS_lumi.extraText = ""
      CMS_lumi.relPosX = 0.06
      CMS_lumi.relPosY = 0.03
    else:
      CMS_lumi.extraText = "Preliminary"
      CMS_lumi.relPosY = 0.03
      CMS_lumi.relPosX = 0.12
    CMS_lumi.lumi_sqrtS = "13 TeV" # used with iPeriod = 0, e.g. for simulation-only plots (default is an empty string)
    iPos = 11
    if( iPos==0 ): CMS_lumi.relPosX = 0.15

    iPeriod=template_settings['year']

    if template_settings['plotRatio']:
      CMS_lumi.CMS_lumi(pad1, iPeriod, iPos, 0.12, 0.08)
    else:
      CMS_lumi.CMS_lumi(pad1, iPeriod, iPos, 0.09)
    ######
    if Set_Logy:
      log_tag = "_log"
    else:
      log_tag = ""
    canvas.Update()

    combined_text = "_combined" if template_settings['combined'] else ""
    canvas.SaveAs('{prefix}{log}{combined}.pdf'.format(prefix=template_settings['outputfilename'],log=log_tag, combined = combined_text))
    canvas.SaveAs('{prefix}{log}{combined}.png'.format(prefix=template_settings['outputfilename'],log=log_tag, combined = combined_text))
    canvas.SaveAs('{prefix}{log}{combined}.C'.format(prefix=template_settings['outputfilename'],log=log_tag, combined = combined_text))
    #canvas.SaveAs('{prefix}{log}{combined}.root'.format(prefix=template_settings['outputfilename'],log=log_tag, combined = combined_text))




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
    if settings['group'] == 0:
      Group = dict()
    else:
        with open('./data_info/NuisanceList/group_set{group}.json'.format(group = int(settings['group']))) as f:
            Group = json.load(f)


    os.chdir(settings['outputdir'])
    workspace_root = os.path.basename(settings['workspace_root'])
    plot1Dscan = os.path.join(CURRENT_WORKDIR, '../../HiggsAnalysis/CombinedLimit/scripts/plot1DScan.py')

    # safety check:
    if not os.path.isfile(workspace_root):
          raise Exception("First run: --mode datacard2workspace step")

    Log_Path = os.path.basename(settings['Log_Path'])
    commands = []
    rMin = settings['rMin']
    rMax = settings['rMax']
    points = 50

    #if not settings['unblind']:
    #    print('Do not support blind option')
    #    return

    commands.append('echo datacard_workspace File: {workspace_root}'.format(workspace_root = workspace_root ))
    commands.append('echo Start to do likelihood Scan')
    commands.append('echo single scan ...')

    common_pattern = '.{year}.{region}.{channel}.{coupling}.unblind.Set{group}'.format(year = settings['year'], region = settings['region'], channel = settings['channel'], coupling = settings['coupling_value'], group = settings['group'])



    SingleScan_pattern = '.singlescan' + common_pattern
    Snapshot_pattern = '.snap' + common_pattern

    SingleScan_root = 'higgsCombine' + SingleScan_pattern + '.MultiDimFit.mH{mass}.root'.format(mass = settings['mass'])
    ### Single Fit ####
    Snapshot_root = 'higgsCombine' + Snapshot_pattern + '.MultiDimFit.mH{mass}.root'.format(mass = settings['mass'])

    commands.append('combine -M MultiDimFit {workspace_root} -n {SingleScan_pattern} -m {mass} --rMin {rMin} --rMax {rMax} {command} --algo grid --points {points}'.format(workspace_root = workspace_root, SingleScan_pattern = SingleScan_pattern, mass = settings['mass'], rMin = settings['rMin'], rMax = settings['rMax'], points = points, command = settings["command"]))

    commands.append('python3 {plot1Dscan}  {SingleScan_root} -o Likelihood{SingleScan_pattern}'.format(plot1Dscan = plot1Dscan, SingleScan_root = SingleScan_root, SingleScan_pattern = SingleScan_pattern))

    ####################
    ####  SnapShot #####
    ####################

    #commands.append('combine -M MultiDimFit {workspace_root} -n {Snapshot_pattern} -m {mass} --rMin {rMin} --rMax {rMax} {command} --saveWorkspace'.format(workspace_root = workspace_root, Snapshot_pattern = Snapshot_pattern, mass = settings['mass'], rMin = settings['rMin'], rMax = settings['rMax'], command = settings["command"]))

    #####################
    #### Profile Scan ###
    #####################

    #commands.append('echo Start to do breakdown')
    #commands.append('combine -M MultiDimFit {Snapshot_root} -n {common_pattern} -m {mass} --rMin {rMin} --rMax {rMax} {command} --algo grid --points {points} --snapshotName MultiDimFit'.format(Snapshot_root = Snapshot_root, common_pattern = common_pattern, mass = settings['mass'], rMin = settings['rMin'], rMax = settings['rMax'], points = points, command = settings["command"]))

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
        #commands.append('combine -M MultiDimFit {workspace_root}  -n {pattern} -m {mass} --rMin {rMin} --rMax {rMax} {command} --algo grid --points {points} --freezeNuisanceGroups {FREEZE} --snapshotName MultiDimFit'.format(workspace_root = Snapshot_root, pattern = FreezeGroup_pattern[Idx], mass = settings['mass'], rMin = settings['rMin'], rMax = settings['rMax'], points = points, FREEZE = FREEZE, command = settings["command"]))

    freeze_pattern = '.freeze.All' + common_pattern

    FileName = 'higgsCombine' + freeze_pattern + '.MultiDimFit.mH{mass}.root'.format(mass = settings['mass'])
    FreezeGroup_root.append(FileName)
    FreezeGroup_pattern.append(freeze_pattern)



    #commands.append('combine -M MultiDimFit {workspace_root}  -n {pattern} -m {mass} --rMin {rMin} --rMax {rMax} {command} --algo grid --points {points}  --snapshotName MultiDimFit --freezeParameters allConstrainedNuisances'.format(workspace_root = Snapshot_root, pattern = freeze_pattern, mass = settings['mass'], rMin = settings['rMin'], rMax = settings['rMax'], points = points, command = settings["command"]))

    ## Plot ##
    Queue = ''

    for Idx, File in enumerate(FreezeGroup_root):
        if Idx != len(FreezeGroup_root) - 1:
            Queue += '{File}:"Freeze {FreezeGroup_name}":{Idx} '.format(File = File, FreezeGroup_name = FreezeGroup_names[Idx], Idx = Idx+1)
        else:
            Queue += '{File}:"Stat. Only":{Idx} '.format(File = File, Idx = Idx + 1)

    BREAKDOWN_LIST = ','.join(Group)
    POSTFIX = ''
    #commands.append('{plot1DScan} {SingleScan_root} --main-label "Total Uncert." -o Likelihood.breakdown.mH{mass}{common_pattern} --others {Queue} --breakdown "{BREAKDOWN_LIST}"'.format(mass = settings['mass'], plot1DScan = plot1Dscan, SingleScan_root = SingleScan_root,common_pattern = common_pattern, Queue = Queue, BREAKDOWN_LIST = BREAKDOWN_LIST + ', Stat.') + ' --year {year} --channel {channel} --mass {mass} --postfixname Set{group} {POSTFIX}'.format(year = settings['year'], channel = settings['channel'], mass = settings['mass'], group = settings['group'], POSTFIX = POSTFIX) ) #TODO add region

    ### Scan NLL under each nuisance variation
    commands.append('combineTool.py -M FastScan -w {workspace_root}:w'.format(workspace_root = workspace_root))

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

    if settings['bonly_gof']:
      result_dir = "GoF_results_bonly"
      gof_command = " --fixedSignalStrength 0 "
    else:
      result_dir = "GoF_results"
      gof_command = ""

    outputdir = os.path.join(settings['outputdir'], result_dir)
    os.system("mkdir -p {outputdir}".format(outputdir = outputdir))
    print("\033[0;35mcd {outputdir}\n\033[0;m".format(outputdir=outputdir))

    os.chdir(outputdir)
    os.system("rm {outputdir}/higgsCombine*.{COUPLING}.{YEAR}.{REGION}.{CHANNEL}.{MASS}.{ALGO}.GoodnessOfFit.mH${MASS}.*.root".format(outputdir = outputdir, COUPLING = settings['coupling_value'], YEAR = settings['year'], REGION = settings['region'], CHANNEL = settings['channel'], MASS = settings['mass'], ALGO = settings['GoF_Algorithm']))
    os.system("cp {DATACARD_DIR}/{DATACARD_NAME} {DATACARD_NAME}".format(DATACARD_DIR = settings['datacard_dir'], DATACARD_NAME = settings['datacard_name']))

    nJobs = 20
    for t in range(1, nJobs +1):
        command = "combineTool.py -m {MASS} -M GoodnessOfFit {datacards} --algo={ALGO}  -t 50 --job-mode condor --sub-opts='+JobFlavour=\"workday\"\nRequestCpus=2' --task-name {t}  --seed {seed} -n toys{t}.{COUPLING}.{YEAR}.{REGION}.{CHANNEL}.{MASS}.{ALGO}  --cminDefaultMinimizerStrategy {cminDefaultMinimizerStrategy} --cminDefaultMinimizerTolerance={cminDefaultMinimizerTolerance} --rMin {rMin} --rMax {rMax} --toysFrequentist {command} > SubmitGoF_{t}.log".format(MASS = settings['mass'], datacards = settings['datacard_name'], ALGO =  settings['GoF_Algorithm'], t = t, seed = 123456 * t, COUPLING = settings['coupling_value'], YEAR = settings['year'], REGION = settings['region'], CHANNEL = settings['channel'], cminDefaultMinimizerStrategy = settings['cminDefaultMinimizerStrategy'], cminDefaultMinimizerTolerance = settings['cminDefaultMinimizerTolerance'], rMin = settings['rMin'], rMax = settings['rMax'], command = gof_command)
        print(command)
        os.system(command)
    if settings['unblind']:
        command = "combineTool.py -m {MASS} -M GoodnessOfFit {datacards} --algo={ALGO} -n Data.{COUPLING}.{YEAR}.{REGION}.{CHANNEL}.{MASS}.{ALGO}  --cminDefaultMinimizerStrategy {cminDefaultMinimizerStrategy} --cminDefaultMinimizerTolerance={cminDefaultMinimizerTolerance} --rMin {rMin} --rMax {rMax} {command} ".format(MASS = settings['mass'], datacards = settings['datacard_name'], ALGO =  settings['GoF_Algorithm'], t = t, seed = 123456 * t, COUPLING = settings['coupling_value'], YEAR = settings['year'], REGION = settings['region'], CHANNEL = settings['channel'], cminDefaultMinimizerStrategy = settings['cminDefaultMinimizerStrategy'], cminDefaultMinimizerTolerance = settings['cminDefaultMinimizerTolerance'], rMin = settings['rMin'], rMax = settings['rMax'], command = gof_command)
        print(command)
        os.system(command)

    condorDir = os.path.join(settings['condorDir'], result_dir)
    CheckDir(condorDir)
    print ("condorDir", condorDir)
    command = "cp {origin}/*.s* {dest}/.".format(origin = outputdir, dest = condorDir)
    os.system(command)
    for f in os.listdir(condorDir):
      if 'sub' in f:
        os.chdir("{dest}".format(dest = condorDir))
        os.system("condor_submit {submit_file}".format(submit_file = f))
        os.chdir("{dest}".format(dest = settings['WorkDir']))

def GoFPlot(settings = dict()):
    ROOT.gStyle.SetOptTitle(0)
    ROOT.gStyle.SetOptStat(0)
    ROOT.gROOT.SetBatch(1)
    algo = settings['GoF_Algorithm']

    if settings['bonly_gof']:
      result_dir = "GoF_results_bonly"
      postfix = "_bonly"
    else:
      result_dir = "GoF_results"
      postfix = ""
    outputdir = os.path.join(settings['outputdir'], result_dir)
    os.chdir(outputdir)
    print('Processing {algo} algorithm...'.format(algo = algo))

    analysis = "ExtraYukawa"
    OutputFile = 'GoF_{algo}_{coupling_value}_{year}_{region}_{channel}_mH{mass}.root'.format(year = settings['year'], region = settings['region'], channel = settings['channel'], mass = settings['mass'], coupling_value = settings['coupling_value'], algo = algo)
    rootToysFiles = 'higgsCombinetoys*.{coupling_value}.{year}.{region}.{channel}.{mass}.{algo}.GoodnessOfFit.mH{mass}.*.root'.format(year = settings['year'], region = settings['region'],  channel = settings['channel'], mass = settings['mass'], coupling_value = settings['coupling_value'],  algo = algo)
    rootDataFiles = 'higgsCombineData.{coupling_value}.{year}.{region}.{channel}.{mass}.{algo}.GoodnessOfFit.mH{mass}.root'.format(year = settings['year'], region = settings['region'], channel = settings['channel'], mass = settings['mass'], coupling_value = settings['coupling_value'],  algo = algo)
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
        print('Please check whether {rootDataFiles} {outputdir}/results/{year}/{region}/{channel}'.format(rootDataFiles = rootDataFiles, outputdir=settings['outputdir'], year = settings['year'], region = settings['region'], channel = settings['channel']))

    plotname = 'GoF{postfix}_{algo}.{coupling_value}.{year}.{region}.{channel}.{mass}.mH{mass}'.format(year = settings['year'], region = settings['region'], channel = settings['channel'], mass = settings['mass'], coupling_value = settings['coupling_value'], algo = algo, postfix=postfix)
    plotname = os.path.join(settings['outputdir'], 'results', plotname)

    print (ts +"You may Clean up the following files"+ ns)
    print (os.path.join(settings['outputdir']+'/results',OutputFile))
    print (os.path.join(settings['outputdir']+'/results',rootToysFiles))
    print (os.path.join(settings['outputdir']+'/results',rootDataFiles))


    command = "combineTool.py -M CollectGoodnessOfFit --input {DataFiles} {OutputFile} -m {mass} -o gof.json \n".format(DataFiles = rootDataFiles if settings['unblind'] else OutputFile, OutputFile = OutputFile, mass = settings['mass'])
    command += "{cmssw}/src/HiggsAnalysis/CombinedLimit/scripts/plotGof.py gof.json --statistic saturated --mass {mass:.1f} -o gof_plot --range 0 500\n".format(cmssw = cmsswBase, mass = int(settings['mass']), output = plotname)
    command += "mv gof_plot.png {plotname}.png\n".format(plotname = plotname)
    command += "mv gof_plot.pdf {plotname}.pdf\n".format(plotname = plotname)
    settings['Log_Path'] = 'ttc_{algo}_{coupling_value}_{year}_{region}_{channel}_MA{mass}_doGoFPlot.log'.format(year = settings['year'], region = settings['region'], channel = settings['channel'], mass = settings['mass'], coupling_value = settings['coupling_value'], algo = algo)

    print(command)
    os.system(command)
    print (ts +"You may Clean up the following files"+ ns)
    print (os.path.join(settings['outputdir']+'/results',OutputFile))
    print (os.path.join(settings['outputdir']+'/results',rootToysFiles))
    print (os.path.join(settings['outputdir']+'/results',rootDataFiles))


def FinalYieldComputation(settings=dict()):

    # add a safety loop whether "FitDiagnostics_root" and "workspace_root" files are there or not! gkole fix me
    workspace_root = settings['workspace_root']
    FitDiagnostics_root = settings['FitDiagnostics_file']
    if os.path.isfile(workspace_root) and os.path.isfile(FitDiagnostics_root):
        print ("FitDiagnostics_root and workspace_root files are there!")
    else:
      raise Exception("First run: --mode datacard2workspace and --mode FitDiagnostics steps")

    outputFile = os.path.join(settings['outputdir'], 'results/PostFitShapesFromWorkspace_output_.root')
    command = "PostFitShapesFromWorkspace -w {workspace_root} --output {outputFile} -m 350 -f {FitDiagnostics_root}:fit_s --postfit --sampling --print".format(workspace_root = settings['workspace_root'], FitDiagnostics_root = settings['FitDiagnostics_file'], outputFile = outputFile)
    command+=' >& {Log_Path} '.format(Log_Path=settings['Log_Path'])
    print(command)
    os.system(command)
    FileIn = ROOT.TFile.Open(outputFile, 'READ')


    Yield = dict()

    region_channel_dict_local_ = dict()
    if settings['region'] == 'C':
      for region_ in region_channel_dict:
        region_channel_dict_local_[region_] = []
    else:
      region_channel_dict_local_[settings['region']] = []

    for region_ in region_channel_dict_local_:
      if settings['channel'] == 'C':
        region_channel_dict_local_[region_] = region_channel_dict[region_]
      else:
        region_channel_dict_local_[region_] = [settings['channel']]

    if settings['year'] == 'run2':
        years = ['2016apv', '2016postapv', '2017', '2018']

    process_name_list = []
    for first_level in FileIn.GetListOfKeys():
        first_level_name = first_level.GetName()
        for second_level in FileIn.Get(first_level_name).GetListOfKeys():
            process_name_list.append(second_level.GetName())
        break

    channel_name_list = []
    for region_ in region_channel_dict_local_:
      for channel_ in region_channel_dict_local_[region_]:
        channel_name_list.append(region_ + "_" + channel_)

    for process in process_name_list:
        Yield[process] = dict()
        for Type in ['postfit', 'prefit']:
            Yield[process][Type] = dict()
            for channel in channel_name_list:
                Yield[process][Type][channel] = dict()
                Yield[process][Type][channel]['Central'] = 0
                Yield[process][Type][channel]['Error'] = 0


    return 0 #TODO work on tex file

    for first_level in FileIn.GetListOfKeys():
        first_level_name = first_level.GetName()
        print(first_level_name)
        print('In Dir: {}'.format(first_level_name))
        if settings['year'] == "run2":
            year = first_level_name.split('_')[0]
            Type = first_level_name.split('_')[-1]
            channel = '_'.join(first_level_name.split('_')[1:-1])
        else:
            Type = first_level_name.split('_')[-1]
            for channel_name_ in channel_name_list:
              if channel_name_ in first_level_name:
                channel = channel_name_
#            channel = '_'.join(first_level_name.split('_')[1:-1])
#            print(first_level_name)

#        if (len(region_channel_dict_local_) == 1): channel = list(region_channel_dict_local_.keys())[0] + "_" + channel
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
            for channel in channel_name_list:
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
    PostFixstr += "-" + settings['region']
    PostFixstr += "-" + settings['channel']
    PostFixstr += "-" + settings['coupling_value']
    PostFixstr += "-m" + settings['higgs'] + settings['mass']

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

            for channel in channel_name_list:

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
