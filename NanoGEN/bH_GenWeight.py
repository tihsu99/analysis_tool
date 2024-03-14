# https://raw.githubusercontent.com/menglu21/GEN_staff/2bad2a4a8071e8ca52816d95481f21156c0fb8d4/GenValidation_PlotCode/histo.py
# Last used
# python TTC_GEN_plots.py -i /eos/cms/store/group/phys_top/ExtraYukawa/NanoGEN_2017/TTC_a0_M1000_rhotu00_rhotc01_rhott00.root -o TTC_a0_M1000_rhotu00_rhotc01_rhott00_old
# python TTC_GEN_plots.py -i /eos/cms/store/group/phys_top/ExtraYukawa/NanoGEN_2017/TTC_a0_M1000_rhotu00_rhotc01_rhott00_new.root -o TTC_a0_M1000_rhotu00_rhotc01_rhott00_new
##########
import os, copy
import sys
import optparse
import ROOT
import math
import array
import uuid

from ROOT import TH1F, TFile, TTree, TLorentzVector, TVectorD
from optparse import OptionParser
from math import cos, sin, sinh
MW_=80.379

ROOT.gROOT.SetBatch(True) # no flashing canvases  

class extend_p4:
  p4_vector=ROOT.TLorentzVector()
  pdgid=11
  def __init__(self, ltvector, pid):
    self.p4_vector=ltvector
    self.pdgid=pid

def wreco(lepp4, metpt, metphi):
  nu4=TLorentzVector()
  px=metpt*cos(metphi)
  py=metpt*sin(metphi)
  pz=0.
  pxl=lepp4.Px()
  pyl=lepp4.Py()
  pzl=lepp4.Pz()
  El=lepp4.E()
  a=MW_*MW_ + 2.*pxl*px + 2.*pyl*py
  A=4.*(El*El - pzl*pzl)
  B=-4.*a*pzl
  C=4.*El*El*(px*px+py*py)-a*a
  tmproot=B*B - 4.*A*C

  if tmproot<0:
    pz=-1.*B/(2*A)
  else:
    tmpsol1 = (-B + math.sqrt(tmproot))/(2.0*A)
    tmpsol2 = (-B - math.sqrt(tmproot))/(2.0*A)
    if abs(tmpsol2-pzl)<abs(tmpsol1-pzl):
      pz=tmpsol2
    else:
      pz=tmpsol1
  if abs(pz)>300:
    if abs(tmpsol1)<abs(tmpsol2):
      pz=tmpsol1
  else:
      pz=tmpsol2
  nu4.SetPxPyPzE(px,py,pz,math.sqrt(px*px+py*py+pz*pz))
  wp4=lepp4+nu4
  return wp4



def scaling(histogram):
    '''Rescales the histogram s.t. the normalization is 1                                                                                                                      
    '''
    try:
      scale = 1./histogram.Integral()
      print ("scale", scale)
      histogram.Scale(scale, option = "nosw2")
    except:
      print("{} has no events -> normalization failed".format(histogram.GetName()))

def makehisto(list_hists, title, outputname, xlabel, ylabel):
    '''takes a list of histograms or a histogram and makes and stores the plot
    '''
    canv = ROOT.TCanvas("c1", "L", 1200, 1200)
    canv.SetLogy()
    legend = ROOT.TLegend(0.67,0.44,0.98,0.74)
    color_cnt = 2
    if type(list_hists) != type([]):
        list_hists = [list_hists]
    maxval = []
    
    for hist in list_hists:
      # print("GetEntries: {}",format(hist.GetEntries()))
      # scaling(hist)
      maxval.append(hist.GetMaximum())
    ymax = max(maxval)*1.1
    
    # print("interval of maxval: {}, ymax = {}".format(maxval, ymax))
    for hist in list_hists:
        legend.AddEntry(hist, hist.GetTitle(), "l")
        hist.SetTitle("{}".format(title))
        hist.SetLineColorAlpha(color_cnt, 1)
        hist.SetLineWidth(2)
        hist.SetXTitle(xlabel)
        hist.SetYTitle(ylabel)
        hist.GetYaxis().SetTitleOffset(1.0)
        hist.GetXaxis().SetTitleOffset(1.1)
        hist.SetMaximum(ymax) # good for most plots ymax = 1.2
        hist.SetStats(0) #stat box in top-right corner will not print
        color_cnt += 1
        hist.Draw("hist SAME")

    legend.SetTextSize(0.02)
    # Sets the fraction of the width which the symbol in the legend takes
    legend.SetMargin(0.1)
    legend.Draw("SAME")
    canv.Print("/eos/user/a/adeiorio/www/bHplus/NanoGEN/{}".format(outputname)+".png")

maxiter = 1000
def main():
  usage = 'usage: %prog [options]'
  parser = optparse.OptionParser(usage)
  parser.add_option('-i', '--in', dest='inputfiles', help='name of input files', default=None, type='string')
  parser.add_option('-o', '--out', dest='outputfiles', help='name output files', default=None, type='string')
  (opt, args) = parser.parse_args()

  histo_array = {}

  h_weight = TH1F('weight','weight',2,-1,1)
  h_Generator_weight = TH1F('Generator_weight','Generator_weight',100,-1,1)
  h_LHEScaleWeight = TH1F('LHEScaleWeight','LHEScaleWeight',100,0,2)
  h_LHEPdfWeight = TH1F('LHEPdfWeight','LHEPdfWeight',100,0,2)

  #LHE histos
  h_lep1pt_LHE = TH1F('lep1pt_LHE', 'lep1pt_LHE', 75, 0, 150)
  h_lep1eta_LHE = TH1F('lep1eta_LHE', 'lep1eta_LHE', 60, -3, 3)
  h_lep1phi_LHE = TH1F('lep1phi_LHE', 'lep1phi_LHE', 80, -4, 4)
  h_lep2pt_LHE = TH1F('lep2pt_LHE', 'lep2pt_LHE', 75, 0, 150)
  h_lep2eta_LHE = TH1F('lep2eta_LHE', 'lep2eta_LHE', 60, -3, 3)
  h_lep2phi_LHE = TH1F('lep2phi_LHE', 'lep2phi_LHE', 80, -4, 4)
  h_Vpt_LHE = TH1F('Vpt_LHE', 'Vpt_LHE', 75, 0, 150)
  h_HT_LHE = TH1F('HT_LHE', 'HT_LHE', 60, 0, 300)
  h_Njets_LHE = TH1F('Njets_LHE', 'Njets_LHE', 5, 0, 5)
  
  h_j1pt_LHE = TH1F('j1pt_LHE', 'j1pt_LHE', 100, 0, 200)
  h_j1eta_LHE = TH1F('j1eta_LHE', 'j1eta_LHE', 100, -5, 5)
  h_j1phi_LHE = TH1F('j1phi_LHE', 'j1phi_LHE', 80, -4, 4)
  h_j1mass_LHE = TH1F('j1mass_LHE', 'j1mass_LHE', 40, 0, 40)
  h_j2pt_LHE = TH1F('j2pt_LHE', 'j2pt_LHE', 100, 0, 200)
  h_j2eta_LHE = TH1F('j2eta_LHE', 'j2eta_LHE', 100, -5, 5)
  h_j2phi_LHE = TH1F('j2phi_LHE', 'j2phi_LHE', 80, -4, 4)
  h_j2mass_LHE = TH1F('j2mass_LHE', 'j2mass_LHE', 40, 0, 40)
  h_j3pt_LHE = TH1F('j3pt_LHE', 'j3pt_LHE', 100, 0, 200)
  h_j3eta_LHE = TH1F('j3eta_LHE', 'j3eta_LHE', 100, -5, 5)
  h_j3phi_LHE = TH1F('j3phi_LHE', 'j3phi_LHE', 80, -4, 4)
  h_j3mass_LHE = TH1F('j3mass_LHE', 'j3mass_LHE', 40, 0, 40)

  h_drlep1j1_LHE = TH1F('drlep1j1_LHE', 'drlep1j1_LHE', 60, 0, 3)
  h_drlep1j2_LHE = TH1F('drlep1j2_LHE', 'drlep1j2_LHE', 60, 0, 3)
  h_drlep1j3_LHE = TH1F('drlep1j3_LHE', 'drlep1j3_LHE', 60, 0, 3)
  h_drlep2j1_LHE = TH1F('drlep2j1_LHE', 'drlep2j1_LHE', 60, 0, 3)
  h_drlep2j2_LHE = TH1F('drlep2j2_LHE', 'drlep2j2_LHE', 60, 0, 3)
  h_drlep2j3_LHE = TH1F('drlep2j3_LHE', 'drlep2j3_LHE', 60, 0, 3)
  h_drl1l2_LHE = TH1F('drl1l2_LHE', 'drl1l2_LHE', 60, 0, 3)
  h_drj1j2_LHE = TH1F('drj1j2_LHE', 'drj1j2_LHE', 60, 0, 3)
  h_drj1j3_LHE = TH1F('drj1j3_LHE', 'drj1j3_LHE', 60, 0, 3)
  h_drj2j3_LHE = TH1F('drj2j3_LHE', 'drj2j3_LHE', 60, 0, 3)
  

  #GEN histos
  h_ngenjet_GEN = TH1F('ngenjet', 'ngenjet', 10, 0, 10)
  h_j1pt_GEN = TH1F('j1pt_GEN', 'j1pt_GEN', 100, 0, 200)
  h_j1eta_GEN = TH1F('j1eta_GEN', 'j1eta_GEN', 100, -5, 5)
  h_j1phi_GEN = TH1F('j1phi_GEN', 'j1phi_GEN', 80, -4, 4)
  h_j1mass_GEN = TH1F('j1mass_GEN', 'j1mass_GEN', 40, 0, 40)
  h_j2pt_GEN = TH1F('j2pt_GEN', 'j2pt_GEN', 100, 0, 200)
  h_j2eta_GEN = TH1F('j2eta_GEN', 'j2eta_GEN', 100, -5, 5)
  h_j2phi_GEN = TH1F('j2phi_GEN', 'j2phi_GEN', 80, -4, 4)
  h_j2mass_GEN = TH1F('j2mass_GEN', 'j2mass_GEN', 40, 0, 40)
  h_j3pt_GEN = TH1F('j3pt_GEN', 'j3pt_GEN', 100, 0, 200)
  h_j3eta_GEN = TH1F('j3eta_GEN', 'j3eta_GEN', 100, -5, 5)
  h_j3phi_GEN = TH1F('j3phi_GEN', 'j3phi_GEN', 80, -4, 4)
  h_j3mass_GEN = TH1F('j3mass_GEN', 'j3mass_GEN', 40, 0, 40)
  h_HT_GEN = TH1F('HT_GEN', 'HT_GEN', 80, 0, 400)
  
  h_Dressedlep1pt_GEN = TH1F('Dressedlep1pt_GEN', 'Dressedlep1pt_GEN', 75, 0, 150)
  h_Dressedlep1eta_GEN = TH1F('Dressedlep1eta_GEN', 'Dressedlep1eta_GEN', 60, -3, 3)
  h_Dressedlep1phi_GEN = TH1F('Dressedlep1phi_GEN', 'Dressedlep1phi_GEN', 80, -4, 4)
  h_Dressedlep2pt_GEN = TH1F('Dressedlep2pt_GEN', 'Dressedlep2pt_GEN', 75, 0, 150)
  h_Dressedlep2eta_GEN = TH1F('Dressedlep2eta_GEN', 'Dressedlep2eta_GEN', 60, -3, 3)
  h_Dressedlep2phi_GEN = TH1F('Dressedlep2phi_GEN', 'Dressedlep2phi_GEN', 80, -4, 4)
  
  h_Zmass_GEN = TH1F('Zmass_GEN', 'Zmass_GEN', 80, 50, 130)
  h_Zpt_GEN = TH1F('Zpt_GEN', 'Zpt_GEN', 100, 0, 200)
  h_Zeta_GEN = TH1F('Zeta_GEN', 'Zeta_GEN', 100, -5, 5)
  h_Zphi_GEN = TH1F('Zphi_GEN', 'Zphi_GEN', 80, -4, 4)
  h_Wpt_GEN = TH1F('Wpt_GEN', 'Wpt_GEN', 100, 0, 200)
  h_Weta_GEN = TH1F('Weta_GEN', 'Weta_GEN', 100, -5, 5)
  h_Wphi_GEN = TH1F('Wphi_GEN', 'Wphi_GEN', 80, -4, 4)
  
  h_drlep1j1_GEN = TH1F('drlep1j1_GEN', 'drlep1j1_GEN', 60, 0, 3)
  h_drlep1j2_GEN = TH1F('drlep1j2_GEN', 'drlep1j2_GEN', 60, 0, 3)
  h_drlep1j3_GEN = TH1F('drlep1j3_GEN', 'drlep1j3_GEN', 60, 0, 3)
  h_drlep2j1_GEN = TH1F('drlep2j1_GEN', 'drlep2j1_GEN', 60, 0, 3)
  h_drlep2j2_GEN = TH1F('drlep2j2_GEN', 'drlep2j2_GEN', 60, 0, 3)
  h_drlep2j3_GEN = TH1F('drlep2j3_GEN', 'drlep2j3_GEN', 60, 0, 3)
  
  h_drl1l2_GEN = TH1F('drl1l2_GEN', 'drl1l2_GEN', 60, 0, 3)
  h_drj1j2_GEN = TH1F('drj1j2_GEN', 'drj1j2_GEN', 60, 0, 3)
  h_drj1j3_GEN = TH1F('drj1j3_GEN', 'drj1j3_GEN', 60, 0, 3)
  h_drj2j3_GEN = TH1F('drj2j3_GEN', 'drj2j3_GEN', 60, 0, 3)
  
  h_Vistaupt_GEN = TH1F('Vistaupt_GEN', 'Vistaupt_GEN', 100, 0, 200)
  h_Vistaueta_GEN = TH1F('Vistaueta_GEN', 'Vistaueta_GEN', 60, -3, 3)
  h_Vistauphi_GEN = TH1F('Vistauphi_GEN', 'Vistauphi_GEN', 80, -4, 4)
  
  h_METpt_GEN = TH1F('METpt_GEN', 'METpt_GEN', 50, 0, 100)
  h_METphi_GEN = TH1F('METphi_GEN', 'METphi_GEN', 80, -4, 4)
  
  #add histos dictionary
  histo_array['h_weight']=h_weight
  histo_array['h_Generator_weight']=h_Generator_weight
  histo_array['h_LHEScaleWeight']=h_LHEScaleWeight
  histo_array['h_LHEPdfWeight']=h_LHEPdfWeight
  histo_array['h_lep1pt_LHE']=h_lep1pt_LHE
  histo_array['h_lep1eta_LHE']=h_lep1eta_LHE
  histo_array['h_lep1phi_LHE']=h_lep1phi_LHE
  histo_array['h_lep2pt_LHE']=h_lep2pt_LHE
  histo_array['h_lep2eta_LHE']=h_lep2eta_LHE
  histo_array['h_lep2phi_LHE']=h_lep2phi_LHE
  histo_array['h_Vpt_LHE']=h_Vpt_LHE
  histo_array['h_HT_LHE']=h_HT_LHE
  histo_array['h_Njets_LHE'] = h_Njets_LHE

  histo_array['h_j1pt_LHE']=h_j1pt_LHE
  histo_array['h_j1eta_LHE']=h_j1eta_LHE
  histo_array['h_j1phi_LHE']=h_j1phi_LHE
  histo_array['h_j1mass_LHE']=h_j1mass_LHE
  histo_array['h_j2pt_LHE']=h_j2pt_LHE
  histo_array['h_j2eta_LHE']=h_j2eta_LHE
  histo_array['h_j2phi_LHE']=h_j2phi_LHE
  histo_array['h_j2mass_LHE']=h_j2mass_LHE
  histo_array['h_j3pt_LHE']=h_j3pt_LHE
  histo_array['h_j3eta_LHE']=h_j3eta_LHE
  histo_array['h_j3phi_LHE']=h_j3phi_LHE
  histo_array['h_j3mass_LHE']=h_j3mass_LHE
  
  histo_array['h_drlep1j1_LHE']=h_drlep1j1_LHE
  histo_array['h_drlep1j2_LHE']=h_drlep1j2_LHE
  histo_array['h_drlep1j3_LHE']=h_drlep1j3_LHE
  histo_array['h_drlep2j1_LHE']=h_drlep2j1_LHE
  histo_array['h_drlep2j2_LHE']=h_drlep2j2_LHE
  histo_array['h_drlep2j3_LHE']=h_drlep2j3_LHE
  histo_array['h_drl1l2_LHE']=h_drl1l2_LHE
  histo_array['h_drj1j2_LHE']=h_drj1j2_LHE
  histo_array['h_drj1j3_LHE']=h_drj1j3_LHE
  histo_array['h_drj2j3_LHE']=h_drj2j3_LHE


  histo_array['h_ngenjet_GEN']=h_ngenjet_GEN
  histo_array['h_j1pt_GEN']=h_j1pt_GEN
  histo_array['h_j1eta_GEN']=h_j1eta_GEN
  histo_array['h_j1phi_GEN']=h_j1phi_GEN
  histo_array['h_j1mass_GEN']=h_j1mass_GEN
  histo_array['h_j2pt_GEN']=h_j2pt_GEN
  histo_array['h_j2eta_GEN']=h_j2eta_GEN
  histo_array['h_j2phi_GEN']=h_j2phi_GEN
  histo_array['h_j2mass_GEN']=h_j2mass_GEN
  histo_array['h_j3pt_GEN']=h_j3pt_GEN
  histo_array['h_j3eta_GEN']=h_j3eta_GEN
  histo_array['h_j3phi_GEN']=h_j3phi_GEN
  histo_array['h_j3mass_GEN']=h_j3mass_GEN
  histo_array['h_HT_GEN']=h_HT_GEN
  histo_array['h_Dressedlep1pt_GEN']=h_Dressedlep1pt_GEN
  histo_array['h_Dressedlep1eta_GEN']=h_Dressedlep1eta_GEN
  histo_array['h_Dressedlep1phi_GEN']=h_Dressedlep1phi_GEN
  histo_array['h_Dressedlep2pt_GEN']=h_Dressedlep2pt_GEN
  histo_array['h_Dressedlep2eta_GEN']=h_Dressedlep2eta_GEN
  histo_array['h_Dressedlep2phi_GEN']=h_Dressedlep2phi_GEN
  histo_array['h_Zmass_GEN']=h_Zmass_GEN
  histo_array['h_Zpt_GEN']=h_Zpt_GEN
  histo_array['h_Zeta_GEN']=h_Zeta_GEN
  histo_array['h_Zphi_GEN']=h_Zphi_GEN
  histo_array['h_Wpt_GEN']=h_Wpt_GEN
  histo_array['h_Weta_GEN']=h_Weta_GEN
  histo_array['h_Wphi_GEN']=h_Wphi_GEN
  histo_array['h_drlep1j1_GEN']=h_drlep1j1_GEN
  histo_array['h_drlep1j2_GEN']=h_drlep1j2_GEN
  histo_array['h_drlep1j3_GEN']=h_drlep1j3_GEN
  histo_array['h_drlep2j1_GEN']=h_drlep2j1_GEN
  histo_array['h_drlep2j2_GEN']=h_drlep2j2_GEN
  histo_array['h_drlep2j3_GEN']=h_drlep2j3_GEN
  histo_array['h_drl1l2_GEN']=h_drl1l2_GEN
  histo_array['h_drj1j2_GEN']=h_drj1j2_GEN
  histo_array['h_drj1j3_GEN']=h_drj1j3_GEN
  histo_array['h_drj2j3_GEN']=h_drj2j3_GEN
  histo_array['h_Vistaupt_GEN']=h_Vistaupt_GEN
  histo_array['h_Vistaueta_GEN']=h_Vistaueta_GEN
  histo_array['h_Vistauphi_GEN']=h_Vistauphi_GEN
  histo_array['h_METpt_GEN']=h_METpt_GEN
  histo_array['h_METphi_GEN']=h_METphi_GEN
  
  for key in histo_array:
    histo_array[key].SetStats(0)
    histo_array[key].Sumw2()
    histo_array[key].GetYaxis().SetTitle("a.u.")
    histo_array[key].GetYaxis().SetTitleSize(0.05);
    histo_array[key].GetYaxis().SetTitleOffset(0.75);
    histo_array[key].GetXaxis().SetTitle(key)
    histo_array[key].SetMinimum(0)

  if not os.path.isfile(opt.inputfiles): 
    print ('inputfile does not exist!!')
  filein=TFile.Open(opt.inputfiles)
  treein=filein.Get('Events')
  npos=treein.GetEntries('genWeight>0')
  nneg=treein.GetEntries('genWeight<0')
  h_weight.SetBinContent(1,nneg)
  h_weight.SetBinContent(2,npos)
  
  
  icnt = 0
  
  def draw1DHisto(chain, variableString, binning, selectionString , weightString , binningIsExplicit = False, addOverFlowBin = None, isProfile = False):
    
    selectionString_ = selectionString
    weightString_    = weightString
    
    tmp=str(uuid.uuid4())
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
    chain.Draw(variableString+">>"+tmp, "("+weightString_+")*("+selectionString_+")", 'goff')

    return res


  # calculate the weights
  scale_indices       = [0,1,3,5,7,8] #4 central?
  ps_indices          = [0,1, 2, 3]
  pdf_indices         = range(100)
  aS_variations16     = ["abs(LHEPdfWeight[100])", "abs(LHEPdfWeight[101])"]
  aS_variations       = ["abs(LHEPdfWeight[101])", "abs(LHEPdfWeight[102])"]
  
  scale_variations    = [ "abs(LHEScaleWeight[%i])"%i for i in scale_indices ]
  ps_variations       = [ "abs(PSWeight[%i])"%i for i in ps_indices ]
  PDF_variations      = [ "abs(LHEPdfWeight[%i])"%i for i in pdf_indices ]

  #if args.variable == "pt":
  variable = "GenJet_pt[0]"
  binning = array.array('d', [20, 35, 50, 80, 120, 160, 200, 260, 320] )
  selection = "nGenJet>2 && nGenDressedLepton >1"
  weightH   = "1"

  
  # draw1D histogram: (variable, binning, selection, weight)
  print ("selection: ", selection)
  central = draw1DHisto(treein, variable, binning, selection, weightH)
  print ("central.GetMean(): ", central.GetMean() )

  # Scale
  scalesHists   = []
  for var in scale_variations:
    # scalesHists.append( get1DHistoFromDraw( variable, binning=binning, selectionString=selection, weightString=weight+"*%s"%var, addOverFlowBin="upper", binningIsExplicit=True ) )
    print (weightH+"*%s"%var)
    scalesHists.append( draw1DHisto(treein, variable, binning, selection, weightH+"*%s"%var) )
  
  nameH = ["LHEScaleWeight[0]", "LHEScaleWeight[1]", "LHEScaleWeight[3]", "LHEScaleWeight[5]", "LHEScaleWeight[7]", "LHEScaleWeight[8]"]
  for i, h in enumerate(scalesHists):
    # set name
    h.SetTitle(nameH[i])
    # print ("scaleH Mean: ", h.GetMean())
    
  makehisto(scalesHists, "theory scale varies leading genjet pt", "1stgenjet_{}".format(maxiter), "Jet Pt", "Nr. Events")
    
  scales        = []
  for i in range(len(binning)):
    scales.append( max( [abs(h.GetBinContent(i+1) - central.GetBinContent(i+1)) / central.GetBinContent(i+1) if central.GetBinContent(i+1) > 0 else 0 for h in scalesHists] ) ) #may be not devide by  central? 
  # print "scales", scales

  
  # PS weight
  #PS weights (w_var / w_nominal); [0] is ISR=0.5 FSR=1; [1] is ISR=1 FSR=0.5; [2] is ISR=2 FSR=1; [3] is ISR=1 FSR=2
  psHists = []
  for var in ps_variations:
    # scalesHists.append( get1DHistoFromDraw( variable, binning=binning, selectionString=selection, weightString=weight+"*%s"%var, addOverFlowBin="upper", binningIsExplicit=True ) )
    print (weightH+"*%s"%var)
    psHists.append( draw1DHisto(treein, variable, binning, selection, weightH+"*%s"%var) )
  
  
  ps        = []
  for i in range(len(binning)):
    ps.append( max( [abs(h.GetBinContent(i+1) - central.GetBinContent(i+1)) / central.GetBinContent(i+1) if central.GetBinContent(i+1) > 0 else 0 for h in psHists] ) ) #may be not devide by  central? 

  nameHH = ["PSWeight[0]", "PSWeight[1]", "PSWeight[2]", "PSWeight[3]"]
  for i, h in enumerate(psHists):
    # set name
    h.SetTitle(nameHH[i])
    print ("psWight Mean: ", h.GetMean())
    
  makehisto(psHists, "theory ps weight varies leading genjet pt", "1stgenjet_psweight_{}".format(maxiter), "Jet Pt", "Nr. Events")
  

  # PDF
  pdfHists   = []
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
    pdf.append( unc )
    
  # print "pdf", pdf
    
  # total
  tot = [ math.sqrt( scales[i]**2 + pdf[i]**2 ) for i in range(len(binning)) ]
  print ("bins: ", binning)
  print ("pdf unc: ", pdf)
  print ("scale unc: ", scales)
  print ("ps unc: ", ps)
  print ("total(pdf+scale): ", tot)
  

  # events loop starts
  for entry in range(treein.GetEntries()):
    icnt += 1
    p4temp = TLorentzVector()
    wp4temp = TLorentzVector()
    zp4 = TLorentzVector()
    LHElep = []
    LHEjet = []
    GENjet = []
    GENDressLep = []
    HT_GEN = 0.
    treein.GetEntry(entry)
    weight=(treein.genWeight)/(abs(treein.genWeight))
    # print ("weight: ", weight) # this is "1"

    #LHE info
    histo_array['h_Vpt_LHE'].Fill(treein.LHE_Vpt, weight)
    histo_array['h_Njets_LHE'].Fill(ord(treein.LHE_Njets), weight)
    histo_array['h_HT_LHE'].Fill(treein.LHE_HT, weight)

    # Generator_weight
    histo_array['h_Generator_weight'].Fill(treein.Generator_weight, weight)
    for ii in range(0, treein.nLHEPdfWeight):
      # print ("treein.LHEPdfWeight[ii]", treein.LHEPdfWeight[ii])
      histo_array['h_LHEPdfWeight'].Fill(treein.LHEPdfWeight[ii], weight)
      
    for ii in range(0, treein.nLHEScaleWeight):
      # print ("ii: ", ii)
      # print ("treein.LHEScaleWeight[ii]", treein.LHEScaleWeight[ii])
      histo_array['h_LHEScaleWeight'].Fill(treein.LHEScaleWeight[ii], weight)

      #for ii in range(0, treein.nPSWeight):
      #print ("ii: ", ii)
      #print ("PSWeight[ii] ", treein.PSWeight[ii])
    # print ("scale_variations: ", scale_variations)
    # print ("PDF_variations:   ", PDF_variations)

    # draw1D histogram: (variable, binning, selection, weight)
    # print ("Drawing histos")
    ## central = draw1DHisto(treein, variable, binning, selection, weightH)
    # print ("type(central)", type(central))
    # print ("central.GetMean(): ", central.GetMean() )

    # histo_array['h_LHEScaleWeight'].Fill(treein.LHEPdfWeight, weight)

    #GEN info
    histo_array['h_ngenjet_GEN'].Fill(treein.nGenJet, weight)
    
    '''
    for ijet in range(0, treein.nGenJet):
      HT_GEN = HT_GEN+treein.GenJet_pt[ijet]
      p4temp.SetPtEtaPhiM(treein.GenJet_pt[ijet], treein.GenJet_eta[ijet], treein.GenJet_phi[ijet],treein.GenJet_mass[ijet])
      GENjet.append(p4temp.Clone())#no need to sort
    if treein.nGenJet>2:
      histo_array['h_j1pt_GEN'].Fill(treein.GenJet_pt[0], weight)
      histo_array['h_j1eta_GEN'].Fill(treein.GenJet_eta[0], weight)
      histo_array['h_j1phi_GEN'].Fill(treein.GenJet_phi[0], weight)
      histo_array['h_j1mass_GEN'].Fill(treein.GenJet_mass[0], weight)
      histo_array['h_j2pt_GEN'].Fill(treein.GenJet_pt[1], weight)
      histo_array['h_j2eta_GEN'].Fill(treein.GenJet_eta[1], weight)
      histo_array['h_j2phi_GEN'].Fill(treein.GenJet_phi[1], weight)
      histo_array['h_j2mass_GEN'].Fill(treein.GenJet_mass[1], weight)
      histo_array['h_j3pt_GEN'].Fill(treein.GenJet_pt[2], weight)
      histo_array['h_j3eta_GEN'].Fill(treein.GenJet_eta[2], weight)
      histo_array['h_j3phi_GEN'].Fill(treein.GenJet_phi[2], weight)
      histo_array['h_j3mass_GEN'].Fill(treein.GenJet_mass[2], weight)
      histo_array['h_drj1j2_GEN'].Fill(GENjet[0].DeltaR(GENjet[1]), weight)
      histo_array['h_drj1j3_GEN'].Fill(GENjet[0].DeltaR(GENjet[2]), weight)
      histo_array['h_drj2j3_GEN'].Fill(GENjet[1].DeltaR(GENjet[2]), weight)
      
    elif treein.nGenJet>1:
      histo_array['h_j1pt_GEN'].Fill(treein.GenJet_pt[0], weight)
      histo_array['h_j1eta_GEN'].Fill(treein.GenJet_eta[0], weight)
      histo_array['h_j1phi_GEN'].Fill(treein.GenJet_phi[0], weight)
      histo_array['h_j1mass_GEN'].Fill(treein.GenJet_mass[0], weight)
      histo_array['h_j2pt_GEN'].Fill(treein.GenJet_pt[1], weight)
      histo_array['h_j2eta_GEN'].Fill(treein.GenJet_eta[1], weight)
      histo_array['h_j2phi_GEN'].Fill(treein.GenJet_phi[1], weight)
      histo_array['h_j2mass_GEN'].Fill(treein.GenJet_mass[1], weight)
      histo_array['h_drj1j2_GEN'].Fill(GENjet[0].DeltaR(GENjet[1]), weight)
    elif treein.nGenJet>0:
      histo_array['h_j1pt_GEN'].Fill(treein.GenJet_pt[0], weight)
      histo_array['h_j1eta_GEN'].Fill(treein.GenJet_eta[0], weight)
      histo_array['h_j1phi_GEN'].Fill(treein.GenJet_phi[0], weight)
      histo_array['h_j1mass_GEN'].Fill(treein.GenJet_mass[0], weight)
    else: 
      pass
    histo_array['h_HT_GEN'].Fill(HT_GEN, weight)

    if treein.nGenDressedLepton>0:
      for idressedlep in range(0, treein.nGenDressedLepton):
        if treein.GenDressedLepton_hasTauAnc[idressedlep]: continue
        p4temp.SetPtEtaPhiM(treein.GenDressedLepton_pt[idressedlep],treein.GenDressedLepton_eta[idressedlep],treein.GenDressedLepton_phi[idressedlep],treein.GenDressedLepton_mass[idressedlep])
        GENDressLep.append(extend_p4(p4temp.Clone(), treein.GenDressedLepton_pdgId[idressedlep]))
      GENDressLep.sort(key=lambda x: x.p4_vector.Pt())
      if len(GENDressLep)==1:
        # wp4temp=wreco(GENDressLep[0].p4_vector, treein.GenMET_pt, treein.GenMET_phi)
        # histo_array['h_Weta_GEN'].Fill(wp4temp.Eta(), weight)
        # histo_array['h_Wpt_GEN'].Fill(wp4temp.Pt(), weight)
        # histo_array['h_Wphi_GEN'].Fill(wp4temp.Phi(), weight)
        histo_array['h_Dressedlep1pt_GEN'].Fill(GENDressLep[0].p4_vector.Pt(), weight)
        histo_array['h_Dressedlep1eta_GEN'].Fill(GENDressLep[0].p4_vector.Eta(), weight)
        histo_array['h_Dressedlep1phi_GEN'].Fill(GENDressLep[0].p4_vector.Phi(), weight)
        if treein.nGenJet>2:
          histo_array['h_drlep1j1_GEN'].Fill(GENDressLep[0].p4_vector.DeltaR(GENjet[0]), weight)
          histo_array['h_drlep1j2_GEN'].Fill(GENDressLep[0].p4_vector.DeltaR(GENjet[1]), weight)
          histo_array['h_drlep1j3_GEN'].Fill(GENDressLep[0].p4_vector.DeltaR(GENjet[2]), weight)
        elif treein.nGenJet>1:
          histo_array['h_drlep1j1_GEN'].Fill(GENDressLep[0].p4_vector.DeltaR(GENjet[0]), weight)
          histo_array['h_drlep1j2_GEN'].Fill(GENDressLep[0].p4_vector.DeltaR(GENjet[1]), weight)
        elif treein.nGenJet>0:
          histo_array['h_drlep1j1_GEN'].Fill(GENDressLep[0].p4_vector.DeltaR(GENjet[0]), weight)
      else:
          pass
      if len(GENDressLep)==2:
        histo_array['h_Dressedlep1pt_GEN'].Fill(GENDressLep[0].p4_vector.Pt(), weight)
        histo_array['h_Dressedlep1eta_GEN'].Fill(GENDressLep[0].p4_vector.Eta(), weight)
        histo_array['h_Dressedlep1phi_GEN'].Fill(GENDressLep[0].p4_vector.Phi(), weight)
        histo_array['h_Dressedlep2pt_GEN'].Fill(GENDressLep[1].p4_vector.Pt(), weight)
        histo_array['h_Dressedlep2eta_GEN'].Fill(GENDressLep[1].p4_vector.Eta(), weight)
        histo_array['h_Dressedlep2phi_GEN'].Fill(GENDressLep[1].p4_vector.Phi(), weight)
        histo_array['h_drl1l2_GEN'].Fill(GENDressLep[0].p4_vector.DeltaR(GENDressLep[1].p4_vector),weight)
        if treein.nGenJet>2:
          histo_array['h_drlep1j1_GEN'].Fill(GENDressLep[0].p4_vector.DeltaR(GENjet[0]), weight)
          histo_array['h_drlep1j2_GEN'].Fill(GENDressLep[0].p4_vector.DeltaR(GENjet[1]), weight)
          histo_array['h_drlep1j3_GEN'].Fill(GENDressLep[0].p4_vector.DeltaR(GENjet[2]), weight)
          histo_array['h_drlep2j1_GEN'].Fill(GENDressLep[1].p4_vector.DeltaR(GENjet[0]), weight)
          histo_array['h_drlep2j2_GEN'].Fill(GENDressLep[1].p4_vector.DeltaR(GENjet[1]), weight)
          histo_array['h_drlep2j3_GEN'].Fill(GENDressLep[1].p4_vector.DeltaR(GENjet[2]), weight)
        elif treein.nGenJet>1:
          histo_array['h_drlep1j1_GEN'].Fill(GENDressLep[0].p4_vector.DeltaR(GENjet[0]), weight)
          histo_array['h_drlep1j2_GEN'].Fill(GENDressLep[0].p4_vector.DeltaR(GENjet[1]), weight)
          histo_array['h_drlep2j1_GEN'].Fill(GENDressLep[1].p4_vector.DeltaR(GENjet[0]), weight)
          histo_array['h_drlep2j2_GEN'].Fill(GENDressLep[1].p4_vector.DeltaR(GENjet[1]), weight)
        elif treein.nGenJet>0:
          histo_array['h_drlep1j1_GEN'].Fill(GENDressLep[0].p4_vector.DeltaR(GENjet[0]), weight)
          histo_array['h_drlep2j1_GEN'].Fill(GENDressLep[1].p4_vector.DeltaR(GENjet[0]), weight)
      else:
          pass

      if (len(GENDressLep)==2 and (GENDressLep[0].pdgid+GENDressLep[1].pdgid)==0):
        zp4=GENDressLep[0].p4_vector+GENDressLep[1].p4_vector
        histo_array['h_Zmass_GEN'].Fill(zp4.M(), weight)
        histo_array['h_Zeta_GEN'].Fill(zp4.Eta(), weight)
        histo_array['h_Zpt_GEN'].Fill(zp4.Pt(), weight)
        histo_array['h_Zphi_GEN'].Fill(zp4.Phi(), weight)
    '''
    # MET
    histo_array['h_METpt_GEN'].Fill(treein.GenMET_pt, weight)
    histo_array['h_METphi_GEN'].Fill(treein.GenMET_phi, weight)

    # print ("icnt: ", icnt)
    if icnt >= maxiter:
      break
  fileout=TFile.Open(opt.outputfiles+'.root','RECREATE')
  fileout.cd()
  for key in histo_array:
    histo_array[key].Write()
  fileout.Close()

if __name__ == "__main__":
  sys.exit(main())
