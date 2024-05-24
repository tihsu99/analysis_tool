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
    hist_scaleup = ROOT.TH1F('scaleup','scaleup', len(binning)-1, binning)
    hist_scaledown = ROOT.TH1F('scaledown','scaledown', len(binning)-1, binning)
    hist_PSup = ROOT.TH1F('PSup','PSup', len(binning)-1, binning)
    hist_PSdown = ROOT.TH1F('PSdown','PSdown', len(binning)-1, binning)
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
        pdfweights = [treein.LHEPdfWeight[i] for i in range(1, 101)]
        pdfmean = mean(pdfweights)
        rms_hes = math.sqrt(sum([(x-pdfmean)**2 for x in pdfweights]))
        alpha_var = (treein.LHEPdfWeight[102] - treein.LHEPdfWeight[101])/2
        total_pdfunc = math.sqrt(rms_hes**2 + alpha_var**2)
        hist_pdf.Fill(fill_var, 1+total_pdfunc)
        #Histograms for scale uncertainties
        hist_scaleup.Fill(fill_var, max([treein.LHEScaleWeight[i] for i in range(treein.nLHEScaleWeight)]))
        hist_scaledown.Fill(fill_var, min([treein.LHEScaleWeight[i] for i in range(treein.nLHEScaleWeight)]))
        # for NanoGEN the Default PS weights (ISR-FSR = 0.5-2.0) are in the range 2-3 and 24-25. This could change in the future!!!
        hist_PSup.Fill(fill_var, max([treein.PSWeight[i] for i in [2,3,24,25]]))
        hist_PSdown.Fill(fill_var, min([treein.PSWeight[i] for i in [2,3,24,25]]))
        #hist_PSup.Fill(fill_var, max([treein.PSWeight[i] for i in range(treein.nPSWeight)]))
        #hist_PSdown.Fill(fill_var, min([treein.PSWeight[i] for i in range(treein.nPSWeight)]))
        hist_central.Fill(fill_var, 1)

    makehisto([hist_PSup, hist_PSdown, hist_scaleup, hist_scaledown, hist_pdf], "; Leading jet p_{T} [GeV]; Nr. Event", f"comparison_{outname}_{variable}", hist_central)
    
    if is_comparison:
        scaleupGEN, scaledownGEN = applyweights(hist_central, hist_scaleupGEN, hist_scaledownGEN)
        PSupGEN, PSdownGEN = applyweights(hist_central, hist_PSupGEN, hist_PSdownGEN)
        makehisto([scaleupGEN, scaledownGEN, hist_scaleup, hist_scaledown], "; Leading jet p_{T} [GeV]; Nr. Event", f"comparison_NanoAOD-GEN_scale_{outname}_{variable}", hist_central)
        makehisto([PSupGEN, PSdownGEN, hist_PSup, hist_PSdown], "; Leading jet p_{T} [GeV]; Nr. Event", f"comparison_NanoAOD-GEN_PS_{outname}_{variable}", hist_central)
    else:   
        hist_pdfvarup = ROOT.TH1D('pdfvarup','pdfvarup', len(binning)-1, binning)
        hist_scalevarup = ROOT.TH1D('scalevarup','scalevarup', len(binning)-1, binning)
        hist_psvarup = ROOT.TH1D('psvarup','psvarup', len(binning)-1, binning)
        hist_pdfvardown = ROOT.TH1D('pdfvardown','pdfvardown', len(binning)-1, binning)
        hist_scalevardown = ROOT.TH1D('scalevardown','scalevardown', len(binning)-1, binning)
        hist_psvardown = ROOT.TH1D('psvardown','psvardown', len(binning)-1, binning)
        for k in range(1, hist_central.GetNbinsX()+1):
            hist_pdfvarup.SetBinContent(k, abs(hist_pdf.GetBinContent(k) - hist_central.GetBinContent(k))/ hist_central.GetBinContent(k) if hist_central.GetBinContent(k) > 0 else 0)
            hist_pdfvardown.SetBinContent(k, abs(hist_pdf.GetBinContent(k) - hist_central.GetBinContent(k))/ hist_central.GetBinContent(k) if hist_central.GetBinContent(k) > 0 else 0)
            hist_scalevarup.SetBinContent(k, abs(hist_scaleup.GetBinContent(k) - hist_central.GetBinContent(k))/ hist_central.GetBinContent(k) if hist_central.GetBinContent(k) > 0 else 0)
            hist_scalevardown.SetBinContent(k, abs(hist_scaledown.GetBinContent(k) - hist_central.GetBinContent(k))/ hist_central.GetBinContent(k) if hist_central.GetBinContent(k) > 0 else 0)
            hist_psvarup.SetBinContent(k, abs(hist_PSup.GetBinContent(k) - hist_central.GetBinContent(k))/ hist_central.GetBinContent(k) if hist_central.GetBinContent(k) > 0 else 0)
            hist_psvardown.SetBinContent(k, abs(hist_PSdown.GetBinContent(k) - hist_central.GetBinContent(k))/ hist_central.GetBinContent(k) if hist_central.GetBinContent(k) > 0 else 0)

        fileout = ROOT.TFile.Open(opt.outputfiles+'.root','RECREATE')
        fileout.cd()
        hist_scalevarup.Write()
        hist_scalevardown.Write()
        hist_psvarup.Write()
        hist_psvardown.Write()
        hist_pdfvarup.Write()
        hist_pdfvardown.Write()
        fileout.Close()
        makehisto([hist_psvarup, hist_psvardown, hist_scalevarup, hist_scalevardown, hist_pdfvarup, hist_pdfvardown], "; Leading jet p_{T} [GeV]; percent var", f"percent_variation_{outname}_{variable}")

if __name__ == "__main__":
  sys.exit(main())