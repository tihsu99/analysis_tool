# https://raw.githubusercontent.com/menglu21/GEN_staff/2bad2a4a8071e8ca52816d95481f21156c0fb8d4/GenValidation_PlotCode/histo.py
# Last used
# python TTC_GEN_plots.py -i /eos/cms/store/group/phys_top/ExtraYukawa/NanoGEN_2017/TTC_a0_M1000_rhotu00_rhotc01_rhott00.root -o TTC_a0_M1000_rhotu00_rhotc01_rhott00_old
##########
import os, copy
import sys
import ROOT
import math
from array import array
import uuid
from optparse import OptionParser

ROOT.gROOT.SetBatch(True) # no flashing canvases  

def applyweights(hist_weight, hist):
  '''takes a histogram and applies the weights to the central value'''
  hist_up = hist.Clone()
  hist_up.Reset("ICES")
  hist_down = hist.Clone()
  hist_down.Reset("ICES")
  for i in range(1, hist_weight.GetNbinsX()+1):
      hist_up.SetBinContent(i, hist.GetBinContent(i) * (1+hist_weight.GetBinContent(i)))
      hist_down.SetBinContent(i, hist.GetBinContent(i) * (1-hist_weight.GetBinContent(i)))
  return hist_up, hist_down

def makehisto(list_hists, title_labels, outputname, central_hist = None):
    '''takes a list of histograms or a histogram and makes and stores the plot  '''
    canv = ROOT.TCanvas("c1", "L", 1200, 1200)
    canv.SetLogy()
    legend = ROOT.TLegend(0.6,0.5,0.87,0.85)
    color_cnt = 2
    if type(list_hists) != type([]):
        list_hists = [list_hists]
    maxval = []
    
    for hist in list_hists:
      maxval.append(hist.GetMaximum())
    ymax = max(maxval)*1.1
    
    # print("interval of maxval: {}, ymax = {}".format(maxval, ymax))
    for hist in list_hists:
        legend.AddEntry(hist, hist.GetTitle(), "l")
        hist.SetTitle("{}".format(title_labels))
        hist.SetLineColorAlpha(color_cnt, 1)
        hist.SetLineWidth(2)
        hist.GetYaxis().SetTitleOffset(1.3)
        hist.GetXaxis().SetTitleOffset(1.1)
        hist.SetMaximum(ymax) # good for most plots ymax = 1.2
        hist.SetStats(0) #stat box in top-right corner will not print
        color_cnt += 1
        hist.Draw("hist ESAME")
    if central_hist:
        legend.AddEntry(central_hist, central_hist.GetTitle(), "l")
        central_hist.SetLineColor(ROOT.kBlack)
        central_hist.SetLineWidth(2)
        central_hist.Draw("hist SAME")

    legend.SetTextSize(0.02)
    # Sets the fraction of the width which the symbol in the legend takes
    #legend.SetMargin(0)
    legend.SetBorderSize(0)
    legend.Draw("SAME")
    canv.Print(f"/eos/user/{os.getenv('USER')[0]}/{os.getenv('USER')}/www/bHplus/NanoGEN/{outputname}.png")

def draw1DHisto(chain, variableString, binning, selectionString, weightString, binningIsExplicit = False, addOverFlowBin = None, isProfile = False):
    
  tmp = str(uuid.uuid4())
  if binningIsExplicit:
    binningArgs = (len(binning)-1, array('d', binning))
  else:
    binningArgs = binning

  # print ("binningArgs: ", binningArgs)
  if isProfile:
    if type(isProfile) == type(""):
      res = ROOT.TProfile(tmp, tmp, *( binningArgs + (isProfile,)) )
    else:
      res = ROOT.TProfile(tmp, tmp, *binningArgs)
  else:
    res = ROOT.TH1D(tmp, tmp, len(binningArgs)-1 , binningArgs)
  
  # print ("("+weightString_+")*("+selectionString_+")")
  chain.Draw(variableString+">>"+tmp, "("+weightString+")*("+selectionString+")", 'goff')

  return res

def main():
  usage = 'usage: %prog [options]'
  parser = OptionParser(usage)
  parser.add_option('-i', '--in', dest='inputfiles', help='name of input files', default=None, type='string')
  parser.add_option('-o', '--out', dest='outputfiles', help='name output files', default=None, type='string')
  (opt, args) = parser.parse_args()

  if not os.path.isfile(opt.inputfiles): 
    print(f'inputfile {opt.inputfile} does not exist!!')
  filein = ROOT.TFile.Open(opt.inputfiles)
  treein = filein.Get('Events')
  npos = treein.GetEntries('genWeight>0')
  nneg = treein.GetEntries('genWeight<0')
  outname = opt.inputfiles.split('/')[-1].replace('.root','')

  # calculate the weights
  scale_indices       = [0, 1, 2, 3, 5, 6, 7, 8] #4 central
  ps_indices          = [0, 1, 2, 3]
  pdf_indices         = range(100)
  aS_variations16     = ["abs(LHEPdfWeight[100])", "abs(LHEPdfWeight[101])"]
  aS_variations       = ["abs(LHEPdfWeight[101])", "abs(LHEPdfWeight[102])"]
  
  scale_variations    = [ "abs(LHEScaleWeight[%i])"%i for i in scale_indices ]
  ps_variations       = [ "abs(PSWeight[%i])"%i for i in ps_indices ]
  PDF_variations      = [ "abs(LHEPdfWeight[%i])"%i for i in pdf_indices ]

  variable = "GenJet_pt[0]"
  binning = array('d', [20, 35, 50, 80, 120, 160, 200, 260, 320, 450, 700, 1000] )
  selection = "nGenJet>=2 && nGenDressedLepton == 1"
  weightH   = "1"
  
  hist_pdf = ROOT.TH1D('pdf_unc','pdf_unc', len(binning)-1, binning)
  hist_scale = ROOT.TH1D('scale_unc','scale_unc', len(binning)-1, binning)
  hist_ps = ROOT.TH1D('ps_unc','ps_unc', len(binning)-1, binning)

  print("selection: ", selection)
  central = draw1DHisto(treein, variable, binning, selection, weightH)
  central.SetTitle("central")
  print("central.GetMean(): ", central.GetMean() )

  # Scale
  scalesHists = []
  namescales = ["LHEScaleWeight[0]", "LHEScaleWeight[1]", "LHEScaleWeight[2]", "LHEScaleWeight[3]", "LHEScaleWeight[5]", "LHEScaleWeight[6]", "LHEScaleWeight[7]", "LHEScaleWeight[8]"]
  for var, namescale in zip(scale_variations, namescales):
    print(weightH+"*%s"%var)
    scalesHists.append( draw1DHisto(treein, variable, binning, selection, weightH+"*%s"%var) )
    scalesHists[-1].SetTitle(namescale)
    
  scales = []
  for i in range(len(binning)):
    scales.append( max( [abs(h.GetBinContent(i+1) - central.GetBinContent(i+1)) / central.GetBinContent(i+1) if central.GetBinContent(i+1) > 0 else 0 for h in scalesHists] ) ) #may be not devide by  central? 
    hist_scale.SetBinContent(i+1, scales[i])

  makehisto(scalesHists, "theory scale varies leading genjet pt; Leading jet p_{T} [GeV]; Nr. Event", outname + "_1stgenjet_scale", central) #, "", ""
  
  # PS weight
  #PS weights (w_var / w_nominal); [0] is ISR=0.5 FSR=1; [1] is ISR=1 FSR=0.5; [2] is ISR=2 FSR=1; [3] is ISR=1 FSR=2
  psHists = []
  namepsHists = ["PSWeight[0]", "PSWeight[1]", "PSWeight[2]", "PSWeight[3]"]
  for var, nameps in zip(ps_variations, namepsHists):
    print(weightH+"*%s"%var)
    psHists.append( draw1DHisto(treein, variable, binning, selection, weightH+"*%s"%var) )
    psHists[-1].SetTitle(nameps)

  ps = []
  for i in range(len(binning)):
    ps.append( max( [abs(h.GetBinContent(i+1) - central.GetBinContent(i+1)) / central.GetBinContent(i+1) if central.GetBinContent(i+1) > 0 else 0 for h in psHists] ) ) #may be not devide by  central? 
    hist_ps.SetBinContent(i+1, ps[i])
    
  makehisto(psHists, "theory ps weight varies leading genjet pt; Leading jet p_{T} [GeV]; Nr. Event", outname + "_1stgenjet_psweight", central) #, "", ""
  
  # PDF
  pdfHists = []
  for var in PDF_variations:
    pdfHists.append( draw1DHisto(treein, variable, binning, selection, weightH+"*%s"%var) )
    # pdfHists.append( sample.get1DHistoFromDraw( variable, binning=binning, selectionString=selection, weightString=weight+"*%s"%var, addOverFlowBin="upper", binningIsExplicit=True ) )

  pdf = []
  for i in range(len(binning)):
    centVal = central.GetBinContent(i+1)
    unc = 0
    if centVal > 0:
      deltas = [h.GetBinContent(i+1) for h in pdfHists]
      deltas = sorted(deltas)
      upper = int(len(deltas)*84/100 - 1)
      lower = int(len(deltas)*16/100 - 1)
      delta_sigma = abs(deltas[upper]-deltas[lower])*0.5
      unc = delta_sigma/centVal
    pdf.append(unc)
    hist_pdf.SetBinContent(i+1, unc)

  # total
  tot = [ math.sqrt( scales[i]**2 + pdf[i]**2 ) for i in range(len(binning)) ]
  print("bins: ", binning)
  print("pdf unc: ", pdf)
  print("scale unc: ", scales)
  print("ps unc: ", ps)
  print("total(pdf+scale): ", tot)

  fileout = ROOT.TFile.Open(opt.outputfiles+'.root','RECREATE')
  fileout.cd()
  hist_pdf.Write()
  hist_scale.Write()
  hist_ps.Write()
  fileout.Close()

  # producing histogram from the file ...
  mass = "300"
  year = "2018"
  filein2 = ROOT.TFile.Open(f'/eos/cms/store/group/phys_b2g/ExYukawa/bHplus/{year}/v4/CGToBHpm_a_{mass}_rtt06_rtc04.root')
  treein2 = filein2.Get('Events') 
  selection2 = 'bh_nl==1 && bh_region==1 && nHad_tau==0 && bh_jets==1'
  variable2 = 'Jet_pt[0]'
  central2 = draw1DHisto(treein2, variable2, binning, selection2, weightH)
  central2.SetTitle("central")
  hist_pdf2 = ROOT.TH1D('pdf_unc2','pdf_unc2', len(binning)-1, binning)
  hist_scale2 = ROOT.TH1D('scale_unc2','scale_unc', len(binning)-1, binning)
  hist_ps2 = ROOT.TH1D('ps_unc2','ps_unc', len(binning)-1, binning)
  scalesHists2 = []
  #pdf2_hist = ROOT.TH1F()
  for var in scale_variations:
    print(weightH+"*%s"%var)
    scalesHists2.append( draw1DHisto(treein2, variable2, binning, selection2, weightH+"*%s"%var) )

  scales2 = []
  for i in range(len(binning)):
    scales2.append( max( [abs(h.GetBinContent(i+1) - central2.GetBinContent(i+1)) / central2.GetBinContent(i+1) if central2.GetBinContent(i+1) > 0 else 0 for h in scalesHists2] ) ) #may be not devide by  central? 
    hist_scale2.SetBinContent(i+1, scales2[i])

  up_true, down_true = applyweights(hist_scale2, central2)
  up_rew, down_rew = applyweights(hist_scale, central2)
  up_rew.SetTitle("Scale up NanoGEN") 
  up_true.SetTitle("Scale up sample weights") 
  down_rew.SetTitle("Scale down NanoGEN") 
  down_true.SetTitle("Scale down sample weights") 
  makehisto([up_true, down_true, up_rew, down_rew], "; Leading jet p_{T} [GeV]; Nr. Event", f"comparison_scale_MH{mass}_{year}", central2)

  psHists2 = []
  for var in ps_variations:
    print(weightH+"*%s"%var)
    psHists2.append( draw1DHisto(treein2, variable2, binning, selection2, weightH+"*%s"%var) )

  ps2 = []
  for i in range(len(binning)):
    ps2.append( max( [abs(h.GetBinContent(i+1) - central2.GetBinContent(i+1)) / central2.GetBinContent(i+1) if central2.GetBinContent(i+1) > 0 else 0 for h in psHists2] ) ) #may be not devide by  central? 
    hist_ps2.SetBinContent(i+1, ps2[i])
    
  up_true, down_true = applyweights(hist_ps2, central2)
  up_rew, down_rew = applyweights(hist_ps, central2)
  up_rew.SetTitle("PS up NanoGEN") 
  up_true.SetTitle("PS up sample weights") 
  down_rew.SetTitle("PS down NanoGEN") 
  down_true.SetTitle("PS down sample weights") 
  makehisto([up_true, down_true, up_rew, down_rew], "; Leading jet p_{T} [GeV]; Nr. Event", f"comparison_PS_MH{mass}_{year}", central2)
  # PDF
  pdfHists2 = []
  for var in PDF_variations:
    pdfHists2.append( draw1DHisto(treein2, variable2, binning, selection2, weightH+"*%s"%var) )
    # pdfHists.append( sample.get1DHistoFromDraw( variable, binning=binning, selectionString=selection, weightString=weight+"*%s"%var, addOverFlowBin="upper", binningIsExplicit=True ) )

  pdf2 = []
  for i in range(len(binning)):
    print(f"PDF variations for bin {i}")
    centVal = central2.GetBinContent(i+1)
    unc = 0
    if centVal > 0:
      deltas = [h.GetBinContent(i+1) for h in pdfHists2]
      deltas = sorted(deltas)
      upper = int(len(deltas)*84/100 - 1)
      lower = int(len(deltas)*16/100 - 1)
      delta_sigma = abs(deltas[upper]-deltas[lower])*0.5
      unc = delta_sigma/centVal
    pdf2.append(unc)
    hist_pdf2.SetBinContent(i+1, unc)

  up_true, down_true = applyweights(hist_pdf2, central2)
  up_rew, down_rew = applyweights(hist_pdf, central2)
  up_rew.SetTitle("PDF up NanoGEN") 
  up_true.SetTitle("PDF up sample weights") 
  down_rew.SetTitle("PDF down NanoGEN") 
  down_true.SetTitle("PDF down sample weights") 
  makehisto([up_true, down_true, up_rew, down_rew], "; Leading jet p_{T} [GeV]; Nr. Event", f"comparison_PDF_MH{mass}_{year}", central2)


if __name__ == "__main__":
  sys.exit(main())