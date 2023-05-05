import ROOT
import json
from Util.General_Tool import CheckDir, CheckFile
import argparse
import os,sys, array
from collections import OrderedDict
from operator import itemgetter

CURRENT_WORKDIR = os.getcwd()
sys.path.append(CURRENT_WORKDIR)

change_map = {'wz_qcd': 'WZ_qcd', 
              'ww':     'osWW',
              'ttW':    'ttWtoLNu',
              'ttWToQQ':'ttWtoQQ',
              'www1':   'WWW',
              'wwz1':   'WWZ',
              'zzz1':   'ZZZ',
              'tZq':    'tzq'}

binning = array.array('d', [-0.6, -0.2, 0.2, 0.6, 1.0])

def DrawDistribution(category, settings):
  os.system('mkdir -p ' + settings['outputdir'])
  Color_plate = [ROOT.kRed, ROOT.kCyan-9, ROOT.kSpring-9, ROOT.kViolet-4, ROOT.kYellow-4, ROOT.kBlue, ROOT.kGreen-2, ROOT.kCyan-2, ROOT.kBlue-6, ROOT.kRed-9, ROOT.kOrange+3, ROOT.kGray, ROOT.kYellow-5, ROOT.kRed+2, ROOT.kBlue+3, ROOT.kGreen-5, ROOT.kOrange-3,ROOT.kSpring, ROOT.kViolet+5, ROOT.kYellow-3]

  ROOT.gStyle.SetOptTitle(0)
  ROOT.gStyle.SetOptStat(0)
  ROOT.gROOT.SetBatch(1)

  canvas = ROOT.TCanvas("","",620,600)
  Set_Logy = settings['logy']
  if Set_Logy:
    canvas.SetLogy(1)
    Histogram_MaximumScale = 1000
  else:
    Histogram_MaximumScale = 1.5

  canvas.SetGrid(1,1)
  canvas.SetLeftMargin(0.12)
  canvas.SetRightMargin(0.08)
  
  Integrals = dict()
  Histograms = dict()

  for sample in settings['Category'][category]:
    Integrals[sample]  = settings['Integrals'][sample]
    Histograms[sample] = settings['Histograms'][sample]

  legend_NCol = int(len(Histograms.keys())/7+1)
  legend = ROOT.TLegend(.15, .65, .15+0.37*max(1,(legend_NCol-1)), .890);
  legend.SetNColumns(legend_NCol)
  legend.SetBorderSize(0);
  legend.SetFillColor(0);
  legend.SetShadowColor(0);
  legend.SetTextFont(42);
  legend.SetTextSize(0.03);


  Ordered_Integral = OrderedDict(sorted(Integrals.items(), key=itemgetter(1)))

  h_stack = ROOT.THStack()
  Total_Integral  = 0.0
  for idx, Histogram_Name in enumerate(Ordered_Integral):
    Histograms[Histogram_Name].SetFillColorAlpha(Color_plate[idx], 0.65)
    h_stack.Add(Histograms[Histogram_Name])
    legend.AddEntry(Histograms[Histogram_Name], Histogram_Name+'[{:.1f}]'.format(Integrals[Histogram_Name]),'F')
    Total_Integral += Ordered_Integral[Histogram_Name]
  h_stack.SetTitle("Pre-Fit Distribution; BDT score; Events/bin")
  h_stack.SetMaximum((h_stack.GetStack().Last().GetMaximum())*Histogram_MaximumScale)
  h_stack.SetMinimum(1)
  h_stack.Draw("HIST")
  legend.Draw("SAME")
  import CMS_lumi
  CMS_lumi.writeExtraText = 1
  CMS_lumi.extraText = "Internal"
  CMS_lumi.lumi_sqrtS = "13 TeV" # used with iPeriod = 0, e.g. for simulation-only plots (default is an empty string)
  iPos = 11
  if( iPos==0 ): CMS_lumi.relPosX = 0.12
  iPeriod='run2'

  CMS_lumi.CMS_lumi(canvas, iPeriod, iPos)

  ######
  if Set_Logy:
    log_tag = "_log"
  else:
    log_tag = ""
  canvas.Update()
  canvas.SaveAs('{prefix}{log}.pdf'.format(prefix=settings['outputdir']+ '/' + category ,log=log_tag))
  canvas.SaveAs('{prefix}{log}.png'.format(prefix=settings['outputdir']+ '/' + category ,log=log_tag)) 

def GetHist(mass, interference, coupling, input_dir, outdir, GenerateUnc=False):

  if interference:
    dir_name = 'ttc_a_' + str(mass) + "_s_" +  str(mass-50) + "_" + coupling + "04"
  else:
    dir_name = 'ttc_a_' + coupling + "04_MA" + str(mass)

  ERA = ['2016apv', '2016postapv', '2017', '2018']
  CHANNEL = ['ee', 'em', 'mm']

  Hists = dict()
  Integrals = dict()

  for era in ERA:
    with open('./data_info/Sample_Names/process_name_' + era + '.json') as f:
      sample_list = json.load(f)
    with open('./data/sample_' + era + 'UL.json') as f:
      xsec_list = json.load(f)
  
    for category in sample_list:
#      print("processing " + category)
      samples = sample_list[category]
      for sample in samples:
        xsec = xsec_list[sample][0]
        xsec_unc = xsec_list[sample][-1]

        for channel in CHANNEL:
          input_file = os.path.join(input_dir, era, dir_name, 'TMVApp_' + str(mass) + "_" + channel + ".root")
          f_in = ROOT.TFile.Open(input_file,'READ')
          hist = f_in.Get(str("ttc" + era + "_" + sample)).Rebin(len(binning)-1, "", binning).Clone()
          hist.SetDirectory(0)
          f_in.Close()
          name = sample if sample not in change_map else change_map[sample]
          if name not in Hists:
            Hists[name] = hist
            Integrals[name] = hist.Integral()
          else:
            Hists[name].Add(hist)
            Integrals[name] += hist.Integral()
  with open('./data/sample_2017UL.json') as f:
    xsec_list = json.load(f)
  with open('./data_info/Sample_Names/process_name_' + era + '.json') as f:
    sample_list = json.load(f)
  samples = []
  small_sample_list = dict()
  for category in sample_list:
    for sample in sample_list[category]:
      small_sample_list[sample] = [sample]

  if interference:
    interference_name = 'interference'
  else:
    interference_name = 'Non-interference'
  settings = {
    'Category':   sample_list,
    'Histograms': Hists,
    'Integrals':  Integrals,
    'logy': False,
    'outputdir': './'
  }

  Unc = dict()
  for category in sample_list:
    if not GenerateUnc:
      settings['Category'] = sample_list
      settings['outputdir'] = os.path.join(outdir, 'plot', interference_name, str(mass), 'category')
      settings['logy'] = True
      DrawDistribution(category, settings)
      settings['logy'] = False
      DrawDistribution(category, settings)
    else:
      unc = 0.0
      total_yield = 0.0
#      print("-------- %s -------"%category)
      for sample in sample_list[category]:
        total_yield += Hists[sample].Integral()
      for sample in sample_list[category]:
        xsec = xsec_list[sample][0]
        xsec_unc = xsec_list[sample][-1]
        yield_   = Hists[sample].Integral()
        unc += (xsec_unc*yield_)**2
#        print("%s: %.2f +/- %.2f %% (%.2f %% of %s)"%(sample, yield_, xsec_unc*100, yield_/total_yield*100, category))
      Unc[category] = (unc)**0.5/total_yield
#      print("Total: %.2f "%(Unc[category]*100))
  print(dir_name)
  for category in Unc:
    print(category, Unc[category])
           
  for category in small_sample_list:
    if not GenerateUnc:
      for Category in sample_list:
        if category in sample_list[Category]:
           Category_name = Category
      settings['Category'] = small_sample_list
      settings['outputdir'] = os.path.join(outdir, 'plot', interference_name, str(mass), Category_name)
      settings['logy'] = True
      DrawDistribution(category, settings)
      settings['logy'] = False
      DrawDistribution(category, settings)

           
parser = argparse.ArgumentParser()

parser.add_argument('-m','--method')

args = parser.parse_args()

if args.method == 'plot':
  for mass in [200, 300, 350, 400, 500, 600, 700, 800, 900, 1000]:
    GetHist(mass, False, "rtu", '/eos/cms/store/group/phys_top/ExtraYukawa/BDT_Jan2023/BDT_output/', '/eos/user/t/tihsu/Limit_bkg_study') 
  for mass in [250, 300, 350, 400, 550, 700, 800, 900, 1000]:
    GetHist(mass, True, "rtu", '/eos/cms/store/group/phys_top/ExtraYukawa/BDT_Jan2023/BDT_output/', '/eos/user/t/tihsu/Limit_bkg_study')
else:
  for mass in [200, 300, 350, 400, 500, 600, 700, 800, 900, 1000]:
    GetHist(mass, False, "rtu", '/eos/cms/store/group/phys_top/ExtraYukawa/BDT_Jan2023/BDT_output/', '/eos/user/t/tihsu/Limit_bkg_study', True)
  for mass in [250, 300, 350, 400, 550, 700, 800, 900, 1000]:
    GetHist(mass, True, "rtu", '/eos/cms/store/group/phys_top/ExtraYukawa/BDT_Jan2023/BDT_output/', '/eos/user/t/tihsu/Limit_bkg_study',True)
