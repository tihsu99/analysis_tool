import ROOT
from copy import deepcopy
from array import array
import numpy as np
import os

folder = '/eos/user/g/gkole/database/bHplus/25Apr2025/'

regions = {'NonPrompt_D': 'QCD_Lepton_pt_eta',
           'NonPrompt_C': 'bh_l1_pt_eta',
           'NonPrompt_D_0btag': 'QCD_Lepton_pt_eta',
           'NonPrompt_C_0btag': 'bh_l1_pt_eta'}

regions_vars = {'NonPrompt_D': 'abs(QCD_Lepton_eta):QCD_Lepton_pt',
                'NonPrompt_C': 'abs(Lepton_eta):Lepton_pt'
                }

years = ['2016apv', '2016postapv', '2017', '2018']
# years = ['2016postapv']  # for testing purposes,

channels = {'mu_resolved_data': [ 'SingleMuon' ],
            'mu_resolved_mc': ["DYnlo",  "tbarW", "TTtoHadronic", "TTTo1L", "TTTo2L", "tW", "WJets_HT70to100_LO", "WJets_HT100to200_LO", "WJets_HT200to400_LO", "WJets_HT400to600_LO",
                               "WJets_HT600to800_LO", "WJets_HT800to1200_LO", "WJets_HT1200to2500_LO", "WJets_HT2500toInf_LO", "tbar_tch", "t_tch",  "t_sch"],
            'mu_resolved_qcd': ["QCD_HT100to200", "QCD_HT200to300", "QCD_HT300to500", "QCD_HT500to700", "QCD_HT700to1000", "QCD_HT1000to1500",
                                "QCD_HT1500to2000", "QCD_HT2000toInf"],
            'ele_resolved_data': [ 'SingleEG', 'SinglePhoton' ],
            'ele_resolved_mc': ["DYnlo",  "tbarW", "TTtoHadronic", "TTTo1L", "TTTo2L", "tW", "WJets_HT70to100_LO", "WJets_HT100to200_LO", "WJets_HT200to400_LO", "WJets_HT400to600_LO",
                               "WJets_HT600to800_LO", "WJets_HT800to1200_LO", "WJets_HT1200to2500_LO", "WJets_HT2500toInf_LO", "tbar_tch", "t_tch",  "t_sch"],
            'ele_resolved_qcd': ["QCD_HT100to200", "QCD_HT200to300", "QCD_HT300to500", "QCD_HT500to700", "QCD_HT700to1000", "QCD_HT1000to1500",
                                "QCD_HT1500to2000", "QCD_HT2000toInf"],
            }
ROOT.gROOT.cd()
ROOT.gROOT.SetBatch(True)
def plot_subtract(year, channel, region, newxaxis, newyaxis, selection=''):
    datah = ROOT.TH2F(f"{region}_{year}_{channel}", ";lepton p_{T} [GeV]; lepton |#eta|", len(newxaxis) - 1, newxaxis, len(newyaxis) - 1, newyaxis)
    datah.SetDirectory(0)
    if year == '2018' and channel == 'ele_resolved':
        channels[channel+'_data'] = [ 'EGamma' ]
    if '0b' in region:
        string = '/'
    else:
        string = '_default/'
    print(region)
    for datafile in channels[channel+'_data']:
        print(datafile)
        datain = ROOT.TFile.Open(folder + '/' + region + '/' + year + '/' + region + string + channel + '/' + datafile + '.root')
        histo = ROOT.TH2F('temphist', ":lepton #p_{T} [GeV]; lepton |#eta|", len(newxaxis) - 1, newxaxis, len(newyaxis) - 1, newyaxis)
        tree = datain.Get("Events")
        tree.Project(histo.GetName(), regions_vars[region], selection)
        print(histo.Integral())
        print(histo.GetNbinsX(), histo.GetNbinsY())
        #print(datahtemp.Integral())
        #print(datahtemp.GetNbinsX(), datahtemp.GetNbinsY())
        datah.Add(histo)
        #histo.Reset('ICES')
        print(datah.Integral())
    for mcfile in channels[channel+'_mc']:
        print(mcfile)
        mcin = ROOT.TFile.Open(folder + '/' + region + '/' + year + '/' + region + string + channel + '/' + mcfile + '.root')
        histo = ROOT.TH2F('temphist', ":lepton #p_{T} [GeV]; lepton |#eta|", len(newxaxis) - 1, newxaxis, len(newyaxis) - 1, newyaxis)
        tree = mcin.Get("Events")
        tree.Project(histo.GetName(), regions_vars[region], 'weight_n_Norm*'+selection)
        datah.Add(histo, -1)
        histo.Reset('ICES')
        print(datah.Integral())
    #check the negative bins
    for ix in range(1, datah.GetNbinsX() + 1):
        for iy in range(1, datah.GetNbinsY() + 1):
            content = datah.GetBinContent(ix, iy)
            if content < 0:
                print(f"WARNING: bin ({ix},{iy}) has negative content: {content}")
                datah.SetBinContent(ix, iy, 0.0001)
                datah.SetBinError(ix, iy, 0.0001)

    # set y axis (eta) bincontent and error to zero for the range (1.4442 1.566) for electrons
    if channel == 'ele_resolved':
        for ix in range(1, datah.GetNbinsX() + 1):
            for iy in range(1, datah.GetNbinsY() + 1):
                y_center = datah.GetYaxis().GetBinCenter(iy)
                if 1.4442 < y_center < 1.566:
                    datah.SetBinContent(ix, iy, 0.0)
                    datah.SetBinError(ix, iy, 0.0)

    return datah

def subtract(year, channel, region):
    if year == '2018' and channel == 'ele_resolved':
        channels[channel+'_data'] = [ 'EGamma' ]
    if '0b' in region:
        string = '/'
    else:
        string = '_default/'
    i = 0
    print(region)
    for datafile in channels[channel+'_data']:
        print(datafile)
        datain = ROOT.TFile.Open(folder + '/' + region + '/' + year + '/' + region + string + channel + '/' + datafile + '.root')
        #print(datain)
        datahtemp = datain.Get(regions[region]).Clone()
        if i == 0:
            datah = deepcopy(datahtemp)
        else:
            datah.Add(datahtemp)
        i += 1
        #print(datah.Integral())
    for mcfile in channels[channel+'_mc']:
        #print(mcfile)
        mcin = ROOT.TFile.Open(folder + '/' + region + '/' + year + '/' + region + string + channel + '/' + mcfile + '.root')
        mchtemp = mcin.Get(regions[region]).Clone()
        datah.Add(mchtemp, -1)
        datah.SetDirectory(0)
        #print(datah.Integral())
    return datah

def getratio(numerator, denominator):
    print(numerator.Integral(), denominator.Integral())
    ratio = numerator.Clone()
    ratio.Divide(denominator)
    # Get number of bins
    nbins_x = ratio.GetNbinsX()
    nbins_y = ratio.GetNbinsY()

    # Loop over bins
    for ix in range(1, nbins_x + 1):  # bins start at 1
        for iy in range(1, nbins_y + 1):
            content = ratio.GetBinContent(ix, iy)
            num_cont = numerator.GetBinContent(ix, iy)
            den_cont = denominator.GetBinContent(ix, iy)
            if content > 1:
                print('DANGER ', content, ' ',  num_cont, ' ', den_cont)
        #print(f"Bin ({ix},{iy}) at ({x_center:.2f}, {y_center:.2f}): {content:.2f}")
    return ratio


def overlay_efficiency_slices(numerator, denominator, axis='y', name_prefix='eff', xaxis_title='lepton p_{T} [GeV]', yaxis_title='Efficiency', savedir='plots_SF'):
    """
    Overlay TEfficiency slices for each bin in the chosen axis (default: y/eta) on one canvas.
    """
    colors = [ROOT.kRed, ROOT.kBlue, ROOT.kGreen+2, ROOT.kMagenta, ROOT.kOrange+2, ROOT.kCyan+2, ROOT.kBlack, ROOT.kViolet, ROOT.kGray+2]
    fr_list = []
    legend = ROOT.TLegend(0.45, 0.15, 0.75, 0.38)
    canvas = ROOT.TCanvas(f"c_{name_prefix}", f"Efficiency Slices {name_prefix}", 900, 700)
    first = True

    if axis == 'y':
        nbins = numerator.GetNbinsY()
        for iy in range(1, nbins+1):
            num_proj = numerator.ProjectionX(f"num_proj_{iy}", iy, iy)
            # print (f"Numerator projection for bin {iy}: {num_proj.Integral()}")
            den_proj = denominator.ProjectionX(f"den_proj_{iy}", iy, iy)
            # print (f"Denominator projection for bin {iy}: {den_proj.Integral()}")

            # Fix: Ensure numerator <= denominator in every bin
            epsilon = 1e-6
            for ibin in range(1, num_proj.GetNbinsX()+2):
                num_val = num_proj.GetBinContent(ibin)
                den_val = den_proj.GetBinContent(ibin)
                # Set negative values to zero
                if num_val < 0:
                    print(f"WARNING: Bin {ibin} in slice {iy}: numerator negative ({num_val}), setting to zero")
                    num_proj.SetBinContent(ibin, 0)
                    num_val = 0
                if den_val < 0:
                    print(f"WARNING: Bin {ibin} in slice {iy}: denominator negative ({den_val}), setting to zero")
                    den_proj.SetBinContent(ibin, 0)
                    den_val = 0
                    num_proj.SetBinContent(ibin, 0)
                    num_val = 0
                # Clip numerator to denominator (with epsilon)
                if num_val > den_val + epsilon:
                    print(f"WARNING: Bin {ibin} in slice {iy}: numerator {num_val} > denominator {den_val}, setting numerator = denominator")
                    num_proj.SetBinContent(ibin, den_val)

                # Print projections for debugging
                # print (f"Bin {ibin} in slice {iy}: numerator = {num_proj.GetBinContent(ibin)}, denominator = {den_proj.GetBinContent(ibin)}")
                # print (f"Bin {ibin} in slice {iy}: numerator error = {num_proj.GetBinError(ibin)}, denominator error = {den_proj.GetBinError(ibin)}")
                print (f"Final Bin {ibin} in slice {iy}: numerator i= {num_val}, denominator  = {den_val}")
            print(f"Numerator projection for bin {iy} after adjustments: {num_proj.Integral()}")
            print(f"Denominator projection for bin {iy} after adjustments: {den_proj.Integral()}")
            num_proj.ResetStats()
            den_proj.ResetStats()


            # Create TEfficiency only if denominator is non-empty
            if den_proj.Integral() > 0:
                eff = ROOT.TEfficiency(num_proj, den_proj)
                eff.SetLineColor(colors[(iy-1) % len(colors)])
                eff.SetMarkerColor(colors[(iy-1) % len(colors)])
                eff.SetMarkerStyle(20 + (iy-1) % 10)
                eff.SetTitle(f"{name_prefix}")
                label = f"{denominator.GetYaxis().GetBinLowEdge(iy):.2f} < |#eta| < {denominator.GetYaxis().GetBinUpEdge(iy):.2f}"
                legend.AddEntry(eff, label, "lp")
                drawopt = "AP" if first else "P SAME"
                eff.Draw(drawopt)
                ROOT.gPad.Update()
                graph = eff.GetPaintedGraph()
                graph.SetMinimum(0)
                graph.SetMaximum(1.2)
                ROOT.gPad.Update()
                print(f"Drawing Fakerate for bin {iy}: {label}")
                first = False
                fr_list.append(eff)

    # Set axis titles and draw legend
    if fr_list:
        # Use the first TEfficiency's total histogram to set axis titles
        fr_list[0].GetTotalHistogram().GetXaxis().SetTitle(xaxis_title)
        fr_list[0].GetTotalHistogram().GetYaxis().SetTitle(yaxis_title)
        canvas.Modified()
        canvas.Update()

    legend.Draw()
    canvas.Update()
    canvas.SaveAs(f"{savedir}/{name_prefix}_overlay.png")
    canvas.SaveAs(f"{savedir}/{name_prefix}_overlay.pdf")
    return canvas, fr_list

def write_histogram(histogram, year, channel, extra=''):
    outfile = ROOT.TFile.Open(f'./non_prompt_{year}{extra}.root', 'UPDATE')
    outfile.cd()
    histogram.SetName(f'{channel}')
    histogram.Write('', ROOT.TObject.kOverwrite)
    outfile.Close()

def draw_and_save(histo, name, options='COLZ', logz=True, savedir='plots_SF'):
    print('Drawing', histo.Integral())
    canvas = ROOT.TCanvas(name, name, 800, 600)
    histo.SetTitle('; lepton p_{T} [GeV]; lepton #eta')
    histo.Draw(options)
    histo.SetStats(0)
    if logz:
        canvas.SetLogz()
    canvas.Modified()
    canvas.Update()
    canvas.Print(f'{savedir}/{name}.png')
    canvas.Print(f'{savedir}/{name}.pdf')
    return canvas

def rebin2D(histo, histo_rebin):
    for ix in range(1, histo.GetNbinsX() + 1):
        for iy in range(1, histo.GetNbinsY() + 1):
            content = histo.GetBinContent(ix, iy)
            error = histo.GetBinError(ix, iy)
            x_center = histo.GetXaxis().GetBinCenter(ix)
            y_center = histo.GetYaxis().GetBinCenter(iy)
            #print(f"Bin ({ix},{iy}) at ({x_center:.2f}, {y_center:.2f}): {content:.2f}")
            #print(f"Content: {content}, Error: {error}")
            if content < 0:
                content = 0.0001
            ix_new = histo_rebin.GetXaxis().FindBin(x_center)
            iy_new = histo_rebin.GetYaxis().FindBin(y_center)
            if ix_new == 0 or iy_new == 0 or ix_new > histo_rebin.GetNbinsX() or iy_new > histo_rebin.GetNbinsY():
                print(f"WARNING: bin ({x_center:.2f}, {y_center:.2f}) out of range")
                continue
            histo_rebin.AddBinContent(ix_new, iy_new, content)
            histo_rebin.SetBinError(ix_new, iy_new, (histo_rebin.GetBinError(ix_new, iy_new)**2 + error**2)**0.5)
            #print(f"New Bin: {new_bin}, New Content: {histo_rebin.GetBinContent(new_bin)}, New Error: {histo_rebin.GetBinError(new_bin)}")
    return histo_rebin

newxaxis = array('d', [0, 20, 30, 40, 50, 60, 70, 80, 90, 100, 120, 140, 160, 180, 200, 240, 280, 320, 360, 400])
newxaxis = array('d', [0, 30, 50, 70, 90, 120, 160, 200, 280, 360, 400])



# newyaxis = array('d', list(np.arange(0, 2.4, 0.4)))

# ele bins
newyaxis_ele = array('d', [0, 0.9, 1.4442, 1.566, 2.0, 2.5])
newxaxis_ele = array('d', [0, 30, 50, 70, 90, 120, 160, 200, 280, 360, 400])

# mu_eta bins
newyaxis_mu = array('d', [0, 1.4, 2.4])
newxaxis_mu = array('d', [0, 50, 70, 90, 120, 160, 400])

ROOT.gStyle.SetPaintTextFormat("1.2f")

if __name__ == '__main__':
    extra = '_1b_notopcut' #'_0btag' n_bjet_DeepB_v
    savedir = f"plots_SF{extra}"
    if not os.path.exists(savedir):
        os.makedirs(savedir)
    # Define the selection criteria
    selection = '(n_bjet_DeepB_v == 1 && bh_met > 0.0)' #&& (top_reco_mass<120 || top_reco_mass>400)
    for year in years:
        for lep in ['mu_resolved', 'ele_resolved']:
            print('Processing year:', year, 'channel:', lep)
            if lep == "mu_resolved":
                if year == '2016apv':
                    newyaxis_mu = array('d', [0, 2.4])
                    newxaxis_mu = array('d', [0, 50, 400])
                else:
                    newyaxis_mu = array('d', [0, 1.4, 2.4])
                    newxaxis_mu = array('d', [0, 50, 70, 90, 120, 160, 400])
                numerator = plot_subtract(year, lep, 'NonPrompt_C', newxaxis_mu, newyaxis_mu, selection)
                print('Numerator: ', numerator.Integral())
                draw_and_save(numerator.Clone(), f'nonprompt_{year}_{lep}_numerator{extra}', savedir=savedir)
                denominator = plot_subtract(year, lep, 'NonPrompt_D', newxaxis_mu, newyaxis_mu, selection)
                print('Denominator: ', denominator.Integral())
            elif lep == "ele_resolved":
                numerator = plot_subtract(year, lep, 'NonPrompt_C', newxaxis_ele, newyaxis_ele, selection)
                print('Numerator: ', numerator.Integral())
                draw_and_save(numerator.Clone(), f'nonprompt_{year}_{lep}_numerator{extra}', savedir=savedir)
                denominator = plot_subtract(year, lep, 'NonPrompt_D', newxaxis_ele, newyaxis_ele, selection)
                print('Denominator: ', denominator.Integral())
            else:
                print ("choose either ele or muon")
            draw_and_save(denominator.Clone(), f'nonprompt_{year}_{lep}_denominator{extra}', savedir=savedir)
            denominator.Add(numerator)
            draw_and_save(denominator.Clone(), f'nonprompt_{year}_{lep}_fulldenom{extra}', savedir=savedir)

            # For muons (overlay eta slices as function of pt)
            if lep == 'mu_resolved':
                canvas, fr_list = overlay_efficiency_slices(numerator, denominator, axis='y', name_prefix=f'fakerate_{year}_{lep}', xaxis_title='lepton p_{T} [GeV]', yaxis_title='Fakerate', savedir=savedir)

                # After you have fr_list from overlay_fakerate_slices
                fr2d = ROOT.TH2F("fr2d", "fakerate 2D;lepton p_{T} [GeV];lepton |#eta|",
                  numerator.GetNbinsX(), numerator.GetXaxis().GetXbins().GetArray(),
                  numerator.GetNbinsY(), numerator.GetYaxis().GetXbins().GetArray())

                for iy, eff in enumerate(fr_list, 1):
                    for ix in range(1, numerator.GetNbinsX()+1):
                        eff_val = eff.GetEfficiency(ix)
                        eff_err = eff.GetEfficiencyErrorUp(ix)
                        print (f"Fakerate for bin ({ix},{iy}): {eff_val} ± {eff_err}")
                        fr2d.SetBinContent(ix, iy, eff_val)
                        fr2d.SetBinError(ix, iy, eff_err)

                outfile = ROOT.TFile.Open(f'fr2d_{lep}_{year}{extra}.root', 'RECREATE') # change the fine name
                #non_prompt_2016postapv_2b_notopcut.root
                fr2d.Write(lep)
                outfile.Close()

                canvas2d = ROOT.TCanvas("c_fr2d", "Fakerate 2D", 800, 600)
                fr2d.Draw("COLZ TEXTE")
                canvas2d.SaveAs(f'{savedir}/fr2d_{lep}_{year}.png')
                canvas2d.SaveAs(f'{savedir}/fr2d_{lep}_{year}.pdf')

            ratio = getratio(numerator.Clone(), denominator.Clone())
            write_histogram(ratio, year, lep, extra)
            draw_and_save(ratio.Clone(), f'ratio_{year}_{lep}{extra}', logz=False, options='COLZ TEXTE', savedir=savedir)
            '''
            numerator = subtract(year, lep, 'NonPrompt_C' + extra)
            print('Before rebinning: ', numerator.Integral())
            numerator.RebinY(5)
            if newyaxis is None:
                newyaxis = array('d', [numerator.GetYaxis().GetBinLowEdge(1)] + [numerator.GetYaxis().GetBinUpEdge(i) for i in range(1, numerator.GetNbinsY() + 1)])
            numerator_rebin = ROOT.TH2F(f"numerator_rebinned_{year}_{lep}", numerator.GetTitle(), len(newxaxis) - 1, newxaxis, len(newyaxis) - 1, newyaxis)
            numerator_rebin = rebin2D(numerator, numerator_rebin)
            print('After rebinning: ',  numerator_rebin.Integral())
            draw_and_save(deepcopy(numerator_rebin), f'nonprompt_{year}_{lep}_numerator{extra}')
            denominator = subtract(year, lep, 'NonPrompt_D' + extra)
            #rebinning
            denominator.RebinY(5)
            denominator_rebin = ROOT.TH2F(f"denominator_rebinned_{year}_{lep}", denominator.GetTitle(), len(newxaxis) - 1, newxaxis, len(newyaxis) - 1, newyaxis)
            denominator_rebin = rebin2D(denominator, denominator_rebin)
            draw_and_save(deepcopy(denominator_rebin), f'nonprompt_{year}_{lep}_denominator{extra}')
            denominator_rebin.Add(numerator_rebin)
            draw_and_save(denominator_rebin, f'nonprompt_{year}_{lep}_fulldenom{extra}')
            ratio = getratio(numerator_rebin, denominator_rebin)
            write_histogram(ratio, year, lep, extra)
            draw_and_save(ratio, f'ratio_{year}_{lep}{extra}', logz=False)
            '''
