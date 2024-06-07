import ROOT
from optparse import OptionParser 
import sys
import os
from array import array
import math
from statistics import mean

def applyweights(hist, histvarup, histvardown=None):
    '''takes a histogram and applies the weights to the central value'''
    ''' if weights are symmetric only hist_up is needed '''
    hist_up = hist.Clone()
    hist_up.SetTitle("NanoGEN_var_up")
    hist_up.Reset("ICES")
    hist_down = hist.Clone()
    hist_down.SetTitle("NanoGEN_var_down")
    hist_down.Reset("ICES")
    for i in range(1, histvarup.GetNbinsX()+1):
        if not histvardown:
            hist_up.SetBinContent(i, hist.GetBinContent(i) * (1+histvarup.GetBinContent(i)))
            hist_down.SetBinContent(i, hist.GetBinContent(i) * (1-histvarup.GetBinContent(i)))
        else:
            hist_up.SetBinContent(i, hist.GetBinContent(i) * (1+histvarup.GetBinContent(i)))
            hist_down.SetBinContent(i, hist.GetBinContent(i) * (1-histvardown.GetBinContent(i)))
    return hist_up, hist_down

def makehisto(list_hists, title_labels, outputname, central_hist = None, logscale = False):
    '''takes a list of histograms or a histogram and makes and stores the plot  '''
    canv = ROOT.TCanvas("c1", "L", 1200, 1200)
    if logscale:
        canv.SetLogy()
    legend = ROOT.TLegend(0.6,0.5,0.87,0.85)
    color_cnt = 2
    if type(list_hists) != type([]):
        list_hists = [list_hists]
    maxval = []
    minval = []
    
    for hist in list_hists:
      maxval.append(hist.GetMaximum())
      minval.append(hist.GetMinimum())
    ymax = max(maxval)*1.1
    ymin = min(minval)
    
    # print("interval of maxval: {}, ymax = {}".format(maxval, ymax))
    for hist in list_hists:
        legend.AddEntry(hist, hist.GetTitle(), "l")
        hist.SetTitle("{}".format(title_labels))
        hist.SetLineColorAlpha(color_cnt, 1)
        hist.SetLineWidth(2)
        hist.GetYaxis().SetTitleOffset(1.3)
        hist.GetXaxis().SetTitleOffset(1.1)
        hist.SetMaximum(ymax) # good for most plots ymax = 1.2
        hist.SetMinimum(ymin) 
        hist.SetStats(0) #stat box in top-right corner will not print
        color_cnt += 1
        hist.Draw("hist SAME")
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
    canv.Print(f"/eos/user/{os.getenv('USER')[0]}/{os.getenv('USER')}/www/bHplus/NanoGEN/{outputname}.pdf")

def main():
    usage = 'usage: %prog [options]'
    parser = OptionParser(usage)
    parser.add_option('-i', '--in', dest='inputfiles', help='name of input files', default=None, type='string')
    parser.add_option('-o', '--out', dest='outputfiles', help='name output files', default=None, type='string')
    (opt, args) = parser.parse_args()
    ROOT.gROOT.SetBatch(True)
    ROOT.TH1.SetDefaultSumw2()

    binning = array('d', [20, 35, 50, 80, 120, 160, 200, 260, 320, 450, 700, 1000] )
    #binning = array('d', [2, 3, 4, 5, 6, 7, 8, 9, 10] )

    if not os.path.isfile(opt.inputfiles): 
        print(f'inputfile {opt.inputfile} does not exist!!')
    filein = ROOT.TFile.Open(opt.inputfiles)
    treein = filein.Get('Events')
    outname = opt.inputfiles.split('/')[-1].replace('.root','')
    hist_murup = ROOT.TH1F('murup','murup', len(binning)-1, binning)
    hist_murdown = ROOT.TH1F('murdown','murdown', len(binning)-1, binning)
    hist_mufup = ROOT.TH1F('mufup','mufup', len(binning)-1, binning)
    hist_mufdown = ROOT.TH1F('mufdown','mufdown', len(binning)-1, binning)
    hist_ISRup = ROOT.TH1F('ISRup','ISRup', len(binning)-1, binning)
    hist_ISRdown = ROOT.TH1F('ISRdown','ISRdown', len(binning)-1, binning)
    hist_FSRup = ROOT.TH1F('FSRup','FSRup', len(binning)-1, binning)
    hist_FSRdown = ROOT.TH1F('FSRdown','FSRdown', len(binning)-1, binning)
    hist_central = ROOT.TH1F('central','central', len(binning)-1, binning)
    hist_pdf = ROOT.TH1F('pdf','pdf', len(binning)-1, binning)


    variable = 'GenJet_pt'
    #variable = 'nJet'

    is_comparison = False
    max_entries = treein.GetEntries()

    if is_comparison:
        max_entries = 10001
        file_weights = ROOT.TFile.Open('prova.root')
        hist_scaleupGEN = file_weights.Get('scalevarup')
        hist_scaledownGEN = file_weights.Get('scalevardown')
        hist_PSupGEN = file_weights.Get('psvarup')
        hist_PSdownGEN = file_weights.Get('psvardown')

    for i in range(max_entries):
        treein.GetEntry(i)
        if i%5000 == 0: print(f'processing {i}th event')
        # selection
        if treein.nGenJet < 2 and treein.nGenDressedLepton != 1: continue

        if "pt" in variable:
            fill_var = getattr(treein,variable)[0]
        else:
            fill_var = getattr(treein,variable)

        # PDF weights are in the range 1-100
        # for uncertainties we refer to section 6.2 of the PDF4LHC recommendations (https://arxiv.org/pdf/1510.03865)
        # the uncertainties are implemented according to the formula for PDF uncertainties for Hessian sets (Eq.20) 
        rms_hes = math.sqrt(sum([(treein.LHEPdfWeight[i]-treein.LHEPdfWeight[0])**2 if abs(treein.LHEPdfWeight[i])<2 else 1 for i in range(1, 101)]))
        alpha_var = (treein.LHEPdfWeight[102] - treein.LHEPdfWeight[101])/2
        if abs(alpha_var) > 10: # check to remove crazy weights
            alpha_var = 0.05
        total_pdfunc = math.sqrt(rms_hes**2 + alpha_var**2)
        hist_pdf.Fill(fill_var, 1+total_pdfunc)
        #Histograms for scale uncertainties
        #LHE scale variation weights (w_var / w_nominal); [0] is MUF="0.5" MUR="0.5"; [1] is MUF="1.0" MUR="0.5"; [2] is MUF="2.0" MUR="0.5"; [3] is MUF="0.5" MUR="1.0"; 
        #[4] is MUF="1.0" MUR="1.0"; [5] is MUF="2.0" MUR="1.0"; [6] is MUF="0.5" MUR="2.0"; [7] is MUF="1.0" MUR="2.0"; [8] is MUF="2.0" MUR="2.0"
        # for uncertainties we refer to the TopSystematic twiki (https://twiki.cern.ch/twiki/bin/viewauth/CMS/TopSystematics#Factorization_and_renormalizatio)
        hist_murup.Fill(fill_var, treein.LHEScaleWeight[7])
        hist_murdown.Fill(fill_var, treein.LHEScaleWeight[1])
        hist_mufup.Fill(fill_var, treein.LHEScaleWeight[8])
        hist_mufdown.Fill(fill_var, treein.LHEScaleWeight[3])
        # for NanoGEN the Default PS weights (ISR-FSR = 0.5-2.0) are in the range 2-3 and 24-25. This could change in the future!!!
        # for uncertainties we refer to the TopSystematic twiki (https://twiki.cern.ch/twiki/bin/viewauth/CMS/TopSystematics#Parton_shower_uncertainties)
        hist_ISRup.Fill(fill_var, treein.PSWeight[25])
        hist_ISRdown.Fill(fill_var, treein.PSWeight[24])
        hist_FSRup.Fill(fill_var, treein.PSWeight[3])
        hist_FSRdown.Fill(fill_var, treein.PSWeight[2])
        #hist_PSup.Fill(fill_var, max([treein.PSWeight[i] for i in range(treein.nPSWeight)]))
        #hist_PSdown.Fill(fill_var, min([treein.PSWeight[i] for i in range(treein.nPSWeight)]))
        hist_central.Fill(fill_var, 1)

    makehisto([hist_ISRup, hist_ISRdown, hist_FSRup, hist_FSRdown, hist_murup, hist_murdown, hist_mufup, hist_mufdown, hist_pdf], "; Leading jet p_{T} [GeV]; Nr. Event", f"comparison_{outname}_{variable}", hist_central)
    
    if is_comparison:
        scaleupGEN, scaledownGEN = applyweights(hist_central, hist_scaleupGEN, hist_scaledownGEN)
        PSupGEN, PSdownGEN = applyweights(hist_central, hist_PSupGEN, hist_PSdownGEN)
        makehisto([scaleupGEN, scaledownGEN, hist_scaleup, hist_scaledown], "; Leading jet p_{T} [GeV]; Nr. Event", f"comparison_NanoAOD-GEN_scale_{outname}_{variable}", hist_central)
        makehisto([PSupGEN, PSdownGEN, hist_PSup, hist_PSdown], "; Leading jet p_{T} [GeV]; Nr. Event", f"comparison_NanoAOD-GEN_PS_{outname}_{variable}", hist_central)
    else:   
        hist_pdfvarup = ROOT.TH1D('pdfvarup','pdfvarup', len(binning)-1, binning)
        hist_murvarup = ROOT.TH1D('murvarup','murvarup', len(binning)-1, binning)
        hist_mufvarup = ROOT.TH1D('mufvarup','mufvarup', len(binning)-1, binning)
        hist_ISRvarup = ROOT.TH1D('ISRvarup','ISRvarup', len(binning)-1, binning)
        hist_FSRvarup = ROOT.TH1D('FSRvarup','FSRvarup', len(binning)-1, binning)
        hist_pdfvardown = ROOT.TH1D('pdfvardown','pdfvardown', len(binning)-1, binning)
        hist_murvardown = ROOT.TH1D('murvardown','murvardown', len(binning)-1, binning)
        hist_mufvardown = ROOT.TH1D('mufvardown','mufvardown', len(binning)-1, binning)
        hist_ISRvardown = ROOT.TH1D('ISRvardown','ISRvardown', len(binning)-1, binning)
        hist_FSRvardown = ROOT.TH1D('FSRvardown','FSRvardown', len(binning)-1, binning)
        for k in range(1, hist_central.GetNbinsX()+1):
            max_var = .7
            hist_pdfvarup.SetBinContent(k, min(max_var, abs(hist_pdf.GetBinContent(k) - hist_central.GetBinContent(k))/ hist_central.GetBinContent(k)) if hist_central.GetBinContent(k) > 0 else 0)
            hist_pdfvardown.SetBinContent(k, min(max_var, abs(hist_pdf.GetBinContent(k) - hist_central.GetBinContent(k))/ hist_central.GetBinContent(k)) if hist_central.GetBinContent(k) > 0 else 0)
            hist_murvarup.SetBinContent(k, min(max_var, abs(hist_murup.GetBinContent(k) - hist_central.GetBinContent(k))/ hist_central.GetBinContent(k)) if hist_central.GetBinContent(k) > 0 else 0)
            hist_murvardown.SetBinContent(k, min(max_var, abs(hist_murdown.GetBinContent(k) - hist_central.GetBinContent(k))/ hist_central.GetBinContent(k)) if hist_central.GetBinContent(k) > 0 else 0)
            hist_mufvarup.SetBinContent(k, min(max_var, abs(hist_mufup.GetBinContent(k) - hist_central.GetBinContent(k))/ hist_central.GetBinContent(k)) if hist_central.GetBinContent(k) > 0 else 0)
            hist_mufvardown.SetBinContent(k, min(max_var, abs(hist_mufdown.GetBinContent(k) - hist_central.GetBinContent(k))/ hist_central.GetBinContent(k)) if hist_central.GetBinContent(k) > 0 else 0)
            hist_ISRvarup.SetBinContent(k, min(max_var, abs(hist_ISRup.GetBinContent(k) - hist_central.GetBinContent(k))/ hist_central.GetBinContent(k)) if hist_central.GetBinContent(k) > 0 else 0)
            hist_ISRvardown.SetBinContent(k, min(max_var, abs(hist_ISRdown.GetBinContent(k) - hist_central.GetBinContent(k))/ hist_central.GetBinContent(k)) if hist_central.GetBinContent(k) > 0 else 0)
            hist_FSRvarup.SetBinContent(k, min(max_var, abs(hist_FSRup.GetBinContent(k) - hist_central.GetBinContent(k))/ hist_central.GetBinContent(k)) if hist_central.GetBinContent(k) > 0 else 0)
            hist_FSRvardown.SetBinContent(k, min(max_var, abs(hist_FSRdown.GetBinContent(k) - hist_central.GetBinContent(k))/ hist_central.GetBinContent(k)) if hist_central.GetBinContent(k) > 0 else 0)

        fileout = ROOT.TFile.Open(opt.outputfiles+'.root','RECREATE')
        fileout.cd()
        hist_mufvarup.Write()
        hist_mufvardown.Write()
        hist_murvarup.Write()
        hist_murvardown.Write()
        hist_ISRvarup.Write()
        hist_ISRvardown.Write()
        hist_FSRvarup.Write()
        hist_FSRvardown.Write()
        hist_pdfvarup.Write()
        hist_pdfvardown.Write()
        fileout.Close()
        makehisto([hist_ISRvarup, hist_ISRvardown, hist_FSRvarup, hist_FSRvardown, hist_mufvarup, hist_mufvardown, hist_murvarup, hist_murvardown, hist_pdfvarup, hist_pdfvardown], "; Leading jet p_{T} [GeV]; percent var", f"percent_variation_{outname}_{variable}")

if __name__ == "__main__":
  sys.exit(main())