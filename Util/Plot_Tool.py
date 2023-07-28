import os
import sys
from array import array
import numpy as np
CURRENT_WORKDIR = os.getcwd()
sys.path.append(CURRENT_WORKDIR)
from array import  array
from ROOT import TGraph, TFile, TGraphAsymmErrors
import ROOT as rt
import ROOT
import argparse
from Util.General_Tool import CheckDir,CheckFile
from scipy.optimize import minimize

ROOT.gROOT.SetBatch(True) # no flashing canvases

####################
## Find Zero Root ##
####################

def Find_Intersection(itp, min_x=0.1, max_x=1.0, EPS=5E-2, eps=1E-2, AddBound=False):
  solutions = []
  for x in np.linspace(min_x, max_x, 10):
    solution = minimize(pred,
                        x0 = [x],
                        args = (itp,1),
                        bounds=[(min_x,max_x)])
    find_solution = True
    for s in solutions:
      if  abs(solution.x-s) < EPS:
        find_solution = False
    if find_solution and (abs(itp.Eval(solution.x))<eps or abs(solution.x-max_x) < EPS):
      if abs(solution.x-max_x)<EPS and AddBound:
        solutions.append(float(solution.x)+EPS*0.98) # Draw outside the boundary
      elif not abs(solution.x-max_x)<EPS:
        solutions.append(float(solution.x)) 
  return solutions

def pred(x, itp, r):
  return (itp.Eval(x[0])-0)**2

###################
## 1D Limit Plot ##
###################

def Plot_1D_Limit_For(log_files_dict={},unblind=False,y_max=10000,y_min=0.001,year=['run2'],channel=['C'],Coupling_value=['rtc0p4'],outputFolder='./',Masses=[200],interference=False, paper=False, AN=False, mode="Coupling"):
    
    
    y_max=y_max # scale of y axis 
    y_min=y_min # scale of y axis 
    
    
    rt.gStyle.SetOptTitle(0)
    rt.gStyle.SetOptStat(0)
    rt.gROOT.SetBatch(1)
    c = rt.TCanvas("c","c",620, 600)
    c.SetGrid(0,0)
    c.SetLogy(1)
    c.SetTopMargin(0.085)
    c.SetLeftMargin(0.12)
    c.SetTicks(1,1)
    
    ##Frame    
    model_ = '2HDM+a'
    ### Legend ####
    leg = rt.TLegend(.57, .62, .80, .86);
    leg.SetBorderSize(0);
    leg.SetFillColor(0);
    leg.SetShadowColor(0);
    leg.SetTextFont(42);
    leg.SetTextSize(0.03);
    
    
    colors = [2,4,6,28]     
    line_style = [2,6,3]
    
    mg =ROOT.TMultiGraph("mg","mg")
    mg.SetTitle(";m_{A} [GeV];95% CL upper limit on #mu=#sigma/#sigma_{theory}")
    mg.SetMinimum(y_min);
    mg.SetMaximum(y_max);

    keys = log_files_dict.keys()
    end_point = len(keys)-1

    if mode == "Coupling":
      print(mode) 
      year = year[0]
      channel = channel[0] 
      limit_pdf_file = 'Merged_Limit_Plots_For_{year}_{channel}.pdf'.format(year=year,channel=channel)
      signal_information = year + " " + channel
      colors = [2,4,6,28]   
      OBS = []
      for idx,coupling_value in enumerate(Coupling_value):
        File_path_per_coupling_value = log_files_dict[coupling_value]
        coupling_value=coupling_value.replace('p','.')
        coupling_type = coupling_value.replace('0.1','').replace('0.4','').replace('0.8','').replace('1.0','').replace('r','') #gkole
        #### Set the Name in legend ####
        if 'rtc' in coupling_value :
            value = coupling_value.split('rtc')[-1]
            prefix = '#rho_{tc} = %s'%(value)
        elif 'rtu' in coupling_value :
            value = coupling_value.split('rtu')[-1]
            prefix = '#rho_{tu} = %s'%(value)
        elif 'rtt' in coupling_value :
            value = coupling_value.split('rtt')[-1]
            prefix = '#rho_{tt} = %s'%(value)
        else:
            raise ValueError("No such coupling: {}".format(coupling_value))
        Limit_Name = prefix 
        ###############################
        
        File_per_coupling_value = ROOT.TFile(File_path_per_coupling_value,'READ')
        
        exp2s =  File_per_coupling_value.Get("exp2")
        exp2s.SetMarkerStyle(20)
        exp2s.SetMarkerSize(1.1)
        exp2s.SetLineWidth(2)
        exp2s.SetFillColorAlpha(rt.kYellow,0.6);
        exp2s.SetLineColor(rt.kYellow)
        exp2s.GetXaxis().SetTitleOffset(1.1)
        exp2s.GetYaxis().SetTitleOffset(1.7)
        exp2s.GetYaxis().SetNdivisions(20,5,0);
        
        mg.Add(exp2s,"A 3")

        exp1s =  File_per_coupling_value.Get("exp1")
        exp1s.SetMarkerStyle(20)
        exp1s.SetMarkerSize(1.1)
        exp1s.SetLineWidth(2)
        exp1s.SetFillColorAlpha(rt.kGreen,0.8);
        exp1s.SetLineColor(rt.kGreen)
        mg.Add(exp1s,"3")
    
        exp =  File_per_coupling_value.Get("expmed")
        exp.SetMarkerStyle(1)
        exp.SetMarkerSize(1.1)
        exp.SetLineStyle(line_style[idx])
        exp.SetLineWidth(3)
        mg.Add(exp,"L")
        if unblind:
            obs =  File_per_coupling_value.Get("obs")
            obs.SetMarkerStyle(20)
            obs.SetMarkerSize(1.1)
            obs.SetLineWidth(3)
            OBS.append(obs)
        leg.AddEntry(exp, Limit_Name+" Expected", "LP");
        if idx==end_point:
            leg.AddEntry(exp1s,"68% expected","F")
            leg.AddEntry(exp2s,"95% expected","F")
            if unblind:
              leg.AddEntry(obs, "Observed", "L");
        else:pass
      if unblind:
        for obs in OBS:
          mg.Add(obs, "LP")

    elif mode=='Year':      

      year = 'run2'
      coupling_value = Coupling_value[0]
      channel = channel[0] 
      limit_pdf_file = 'Merged_Limit_Plots_For_{coupling_value}_{channel}.pdf'.format(coupling_value=coupling_value,channel=channel)
      channel = channel.replace("C","ee+em+mm").replace('m','#mu')
      coupling_value = coupling_value.replace('p','.')

      if 'rtc' in coupling_value :
        value = coupling_value.split('rtc')[-1]
        signal_information = '#rho_{tc}=%s'%(value) + " " + channel
      elif 'rtu' in coupling_value :
        value = coupling_value.split('rtu')[-1] + " " + channel
        signal_information = '#rho_{tu}=%s'%(value)
      elif 'rtt' in coupling_value :
        value = coupling_value.split('rtt')[-1] + " " + channel
        signal_information = '#rho_{tt}=%s'%(value)

      colors = [2,3,4,5,1]     
  

      for idx,YEAR in enumerate(keys):
        File_path_per_coupling_value = log_files_dict[YEAR]
        coupling_value=coupling_value.replace('p','.')
        
        File_per_coupling_value = ROOT.TFile(File_path_per_coupling_value,'READ')
        if not unblind:
          exp =  File_per_coupling_value.Get("expmed")
        else:
          exp =  File_per_coupling_value.Get("obs")

        exp.SetMarkerStyle(21)
        exp.SetMarkerColor(colors[idx])
        exp.SetMarkerSize(1.1)
        exp.SetLineColor(colors[idx])
        exp.SetLineWidth(3)
        mg.Add(exp,"LP")
        if not unblind:
          leg.AddEntry(exp, YEAR + "(exp)", "LP");
        else:
          leg.AddEntry(exp, YEAR + "(obs)", "LP");



    else: 

      year = year[0]
      coupling_value = Coupling_value[0]
      limit_pdf_file = 'Merged_Limit_Plots_For_{coupling_value}_{year}.pdf'.format(coupling_value=coupling_value,year=year)
      coupling_value = coupling_value.replace('p','.')

      if 'rtc' in coupling_value :
        value = coupling_value.split('rtc')[-1]
        signal_information = year + ' #rho_{tc}=%s'%(value)
      elif 'rtu' in coupling_value :
        value = coupling_value.split('rtu')[-1]
        signal_information = year + ' #rho_{tu}=%s'%(value)
      elif 'rtt' in coupling_value :
        value = coupling_value.split('rtt')[-1]
        signal_information = year + ' #rho_{tt}=%s'%(value)

      colors = [2,3,4,1]     
  

      for idx,channel in enumerate(keys):
        File_path_per_coupling_value = log_files_dict[channel]
        
        File_per_coupling_value = ROOT.TFile(File_path_per_coupling_value,'READ')
        
        if not unblind: 
          exp =  File_per_coupling_value.Get("expmed")
        else:
          exp = File_per_coupling_value.Get("obs")

        exp.SetMarkerStyle(21)
        exp.SetMarkerColor(colors[idx])
        exp.SetMarkerSize(1.1)
        exp.SetLineColor(colors[idx])
        exp.SetLineWidth(2)
        mg.Add(exp,"LP")
        channel = channel.replace('C','ee+em+mm').replace('m','#mu')
        if not unblind:
          leg.AddEntry(exp, channel + "(exp)", "LP");
        else:
          leg.AddEntry(exp, channel + "(obs)", "LP");




    c.cd()
    mg.Draw("same") 
    leg.Draw("same")

    
    import CMS_lumi
    CMS_lumi.writeExtraText = 1
    if paper:
      CMS_lumi.extraText = ""
      CMS_lumi.relPosY = 0.045
      CMS_lumi.relPosX = 0.06
    else:
      CMS_lumi.extraText = "Preliminary"
    CMS_lumi.lumi_sqrtS = "13 TeV" # used with iPeriod = 0, e.g. for simulation-only plots (default is an empty string)
    iPos = 11
    if( iPos==0 ): CMS_lumi.relPosX = 0.12
    iPeriod=year
    CMS_lumi.relPosX = 0.15 #gkole
    CMS_lumi.CMS_lumi(c, iPeriod, iPos, 0.14)

    
    
    line = rt.TLine(c.GetUxmin(),1.0,c.GetUxmax(),1.0);
    line.SetLineColor(rt.kRed)
    line.SetLineWidth(2)
    line.Draw('same ')

    latex =  rt.TLatex();
    latex.SetNDC();
    latex.SetTextFont(42);
    latex.SetTextSize(0.03);
    latex.SetTextAlign(31);
    latex.SetTextAlign(12);
    latex.DrawLatex(0.19, 0.82, "g2HDM")
    if AN:
      latex.DrawLatex(0.19, 0.74, year + " " + channel)
    if interference:
      latex.DrawLatex(0.19, 0.78, "m_{A} - m_{H} = 50 GeV");

    
    c.Update()
    
    if interference:
      type_ = "interference"
    else:
      type_ = "pure"

    ### Output File Setting ###
    OUT_DIR = os.path.join(outputFolder,"plots_limit","r" + coupling_type, type_)
    
    CheckDir(OUT_DIR,True)
    limit_pdf_file  = os.path.join(OUT_DIR,limit_pdf_file)
    CheckFile(limit_pdf_file,True)
    c.SaveAs(limit_pdf_file)

    limit_png_file = limit_pdf_file.replace(".pdf",".png")
    CheckFile(limit_png_file,True)
    c.SaveAs(limit_png_file)

    limit_C_file = limit_pdf_file.replace(".pdf",".C")
    CheckFile(limit_C_file,True)
    c.SaveAs(limit_C_file)
    
    limit_root_file = limit_pdf_file.replace(".pdf",".root")
    CheckFile(limit_root_file,True)
    c.SaveAs(limit_root_file)

    c.Close()

def interpolate(Hist, noninterp_bin, interp_bin, axis='x', itp_type = rt.Math.Interpolation.kPOLYNOMIAL, EPS=5E-2, Title=""):

  noninterp_bin_x = noninterp_bin[0]
  noninterp_bin_y = noninterp_bin[1]
  interp_bin_x    = interp_bin[0]
  interp_bin_y    = interp_bin[1]

  Hist_interp     = rt.TH2D("",str(Title),len(interp_bin_x)-1, interp_bin_x, len(interp_bin_y)-1, interp_bin_y) 

  final_limit_interp     = array('d', [])
  interp                 = array('d', [])
  final_limit_interp_second = array('d', [])
  interp_second             = array('d', [])

  if axis == 'x':
    perturbed_axis_noninterp    = noninterp_bin_x
    perturbed_axis_interp       = interp_bin_x
    nonperturbed_axis_noninterp = noninterp_bin_y
    nonperturbed_axis_interp    = interp_bin_y
  else:
    perturbed_axis_noninterp    = noninterp_bin_y
    perturbed_axis_interp       = interp_bin_y
    nonperturbed_axis_noninterp = noninterp_bin_x
    nonperturbed_axis_interp    = interp_bin_x

  

  for idx_nonperturbed, value_nonperturbed in enumerate(nonperturbed_axis_noninterp[:-1]):
    value_vector         = rt.vector('double')()
    log_limit_vector     = rt.vector('double')()
    for idx_perturbed, value_perturbed in enumerate(perturbed_axis_noninterp[:-1]):
      if axis == 'x':
        idx_x = idx_perturbed + 1
        idx_y = idx_nonperturbed + 1
      else:
        idx_x = idx_nonperturbed + 1
        idx_y = idx_perturbed + 1

      obs = Hist.GetBinContent(idx_x, idx_y)
      value_vector.push_back(value_perturbed)
      log_limit_vector.push_back(np.log(obs))

    itp = ROOT.Math.Interpolator(value_vector, log_limit_vector, itp_type)
    limits_interp = Find_Intersection(itp, perturbed_axis_noninterp[0], perturbed_axis_noninterp[-2],EPS=EPS, AddBound= axis=='x')    
    # print(value_nonperturbed, limits_interp)  

    # Only record min and max(if there is second root), ignore the strange fluctuation in the middle(though haven't seen that case ever)
    if len(limits_interp) > 0:
      limits_interp_ = [min(limits_interp)]
      for limit_interp in limits_interp_:
        final_limit_interp.append(limit_interp)
        interp.append(value_nonperturbed)
    if len(limits_interp) > 1: 
      limits_interp_ = [max(limits_interp)]
      for limit_interp in limits_interp:
        final_limit_interp_second.insert(0, limit_interp)
        interp_second.insert(0, value_nonperturbed)
 
    
    for idx_perturbed, value_perturbed in enumerate(perturbed_axis_interp[:-1]):
      if axis == 'x':
        idx_x = idx_perturbed + 1
        idx_y = idx_nonperturbed + 1
      else:
        idx_x = idx_nonperturbed + 1
        idx_y = idx_perturbed + 1
      Hist_interp.SetBinContent(idx_x, idx_y, np.exp(itp.Eval(value_perturbed))) 

  if axis == 'x':
    exclusion = ROOT.TGraph(len(interp), final_limit_interp, interp)
  else:
    exclusion = ROOT.TGraph(len(interp), interp, final_limit_interp)
 #   if len(final_limit_interp_second)>0:
 #     for idx, final_limit_second in enumerate(final_limit_interp_second):
 #       exclusion.SetPoint(exclusion.GetN(), interp_second[idx], final_limit_second)


  exclusion.SetLineWidth(2)
  exclusion.SetLineColor(rt.kRed)
  Hist_interp.GetYaxis().SetTitleOffset(0.95)
  Hist_interp.GetZaxis().SetTitleOffset(1.55)

  return Hist_interp, exclusion


def Plot_2D_Limit_For(log_files_dict={}, unblind=False,year='run2', channel='C', outputFolder='./',Masses=[200], interference=False, paper=False):


  # Obtain coupling information

  coupling_values = log_files_dict.keys()
  coupling_values_list = []
  
  for coupling_value in coupling_values:
  
      value = coupling_value.replace('rtc','').replace('rtu','')
      coupling_type = coupling_value.replace(value,'').replace('r','')
      value = float(value.replace('p',''))*0.1
      coupling_values_list.append(value)

  # Set Canvas Parameter

  rt.gStyle.SetOptTitle(0)
  rt.gStyle.SetOptStat(0)
  rt.gStyle.SetPaintTextFormat(".2f");
  rt.TColor.InvertPalette();

  c = rt.TCanvas("c", "c", 620, 600)
  c.SetGrid(0,0)
  c.SetLogz(1)
  c.SetTopMargin(0.085)
  c.SetLeftMargin(0.07)
  c.SetRightMargin(0.18)
  c.SetTicks(1,1)

  # CMS style
  
  import CMS_lumi
  CMS_lumi.writeExtraText = 1
  if paper:
    CMS_lumi.extraText = ""
    CMS_lumi.relPosY = 0.045
  else:
    CMS_lumi.extraText = "Preliminary"
  CMS_lumi.lumi_sqrtS = "13 TeV" # used with iPeriod = 0, e.g. for simulation-only plots (default is an empty string)
  iPos = 11
  if( iPos==0 ): CMS_lumi.relPosX = 0.12
  iPeriod=year
  CMS_lumi.relPosX = 0.15
  CMS_lumi.CMS_lumi(c, iPeriod, iPos, 2)
  c.Update()

  # Output directory setting

  if interference:
    type_ = "interference"
  else:
    type_ = "pure"

  OUT_DIR = os.path.join(outputFolder, "plots_limit_2D","r" + coupling_type, type_)
  CheckDir(OUT_DIR,True)


  # Binning

  coupling_values_bin = np.array(coupling_values_list)
  np.sort(coupling_values_bin)
  mass_bin = np.array(Masses).astype('float')
  coupling_values_bin = np.append(coupling_values_bin, coupling_values_bin[-1]+0.005)
  mass_bin            = np.append(mass_bin, mass_bin[-1]+1)

  # Interpolation Binning

  # -- Coupling value --
  nbin = 90
  coupling_value_min = coupling_values_bin[0]
  coupling_value_max = coupling_values_bin[-2]
  coupling_interp_bin = array('d',[])
  for i in range(nbin):
    coupling_interp_bin.append(coupling_value_min + (coupling_value_max - coupling_value_min)/float(nbin)*float(i))
  coupling_interp_bin.append(coupling_interp_bin[-1] + 0.005)

  # -- Mass --
  bin_width_mass = 5
  mass_interp_bin = array('d',[])
  mass_start = mass_bin[0]
  while mass_start <= mass_bin[-2]:
    mass_interp_bin.append(mass_start)
    mass_start += bin_width_mass
  mass_interp_bin.append(mass_interp_bin[-1] + 1)

  
  # Histogram

  if unblind:
    Target_Object = "obs"
  else:
    Target_Object = "expmed"

  Title = ";m_{A} [GeV];#rho_{%s};95%% CL upper limit on #mu=#sigma/#sigma_{theory}(%s)"%(coupling_type, Target_Object)
  Hist   = rt.TH2D("",str(Title),
                   len(mass_bin)-1, array('d',mass_bin.tolist()),
                   len(coupling_values_bin)-1, array('d',coupling_values_bin.tolist()))
  Hist_exp = Hist.Clone()

  # Draw Limit Plot from discrete point

  for idx_coupling, coupling_value in enumerate(coupling_values):

    File_per_coupling_value = rt.TFile(log_files_dict[coupling_value])
    obs = File_per_coupling_value.Get(str(Target_Object))
    exp = File_per_coupling_value.Get("expmed")
    
    value = float(coupling_value.replace('rtc','').replace('rtu','').replace('p',''))*0.1

    for idx_mass, mass in enumerate(Masses):
        limit_obs = obs.GetY()[idx_mass]
        limit_exp = exp.GetY()[idx_mass]
        Hist.SetBinContent(idx_mass+1, idx_coupling+1, limit_obs)
        Hist_exp.SetBinContent(idx_mass+1, idx_coupling+1, limit_exp)

    File_per_coupling_value.Close()

  Hist.GetZaxis().SetTitleOffset(1.3)

  Hist.Draw("COLZ TEXT")
  CMS_lumi.CMS_lumi(c, iPeriod, iPos, 0.135)

  limit_pdf_file = os.path.join(OUT_DIR,'Merged_Limit2D_Plots_For_{year}_{channel}.pdf'.format(year=year,channel=channel))
  c.SaveAs(limit_pdf_file)
  c.SaveAs(limit_pdf_file.replace('pdf','png'))

  # Interpolation

  Hist_interp_mass, exclusion = interpolate(Hist,
                                             [mass_bin, coupling_values_bin],
                                             [mass_interp_bin, coupling_values_bin],
                                             axis='x',
                                             itp_type = rt.Math.Interpolation.kLINEAR,
                                             EPS=5, Title=Title)
  Hist_interp_mass_exp, exclusion_exp = interpolate(Hist_exp,
                                             [mass_bin, coupling_values_bin],
                                             [mass_interp_bin, coupling_values_bin],
                                             axis='x',
                                             itp_type = rt.Math.Interpolation.kLINEAR,
                                             EPS=5, Title=Title)
  
  Hist_interp_mass.Draw("COLZ")
  if unblind:
    exclusion.Draw("same")
  exclusion_exp.Draw("same")
  exclusion_exp.SetLineStyle(2)
 
  ## Text
  latex =  rt.TLatex();
  latex.SetNDC();
  latex.SetTextFont(42);
  latex.SetTextSize(0.03);
  latex.SetTextAlign(31);
  latex.SetTextAlign(12);
  latex.DrawLatex(0.62, 0.24, "g2HDM")
  if interference:
    latex.DrawLatex(0.62, 0.20, "m_{A} - m_{H} = 50 GeV");


  ## Legend
  leg = rt.TLegend(.40, .82, .78, .80);
  leg.SetBorderSize(0);
  leg.SetFillColorAlpha(0,0.0);
  leg.SetShadowColor(0);
  leg.SetTextFont(42);
  leg.SetTextSize(0.10);
  if unblind:
    leg.AddEntry(exclusion, "Observed", "L")
  leg.AddEntry(exclusion_exp, "Expected", "L")
  leg.Draw("same")
 
  CMS_lumi.CMS_lumi(c, iPeriod, iPos, 0.135)


  limit_pdf_file = os.path.join(OUT_DIR,'Merged_Limit2D_Plots_For_{year}_{channel}_interp.pdf'.format(year=year,channel=channel))
  c.SaveAs(limit_pdf_file)
  c.SaveAs(limit_pdf_file.replace(".pdf",".png"))

  # Extra interpolation (linear in log mass)

  Hist_interp_extra, exclusion_extra = interpolate(Hist_interp_mass,
                                             [mass_interp_bin, coupling_values_bin],
                                             [mass_interp_bin, coupling_interp_bin],
                                             axis='y',
                                             itp_type = rt.Math.Interpolation.kPOLYNOMIAL,
                                             EPS=1E-2, Title=Title)
  Hist_interp_extra_exp, exclusion_extra_exp = interpolate(Hist_interp_mass_exp,
                                             [mass_interp_bin, coupling_values_bin],
                                             [mass_interp_bin, coupling_interp_bin],
                                             axis='y',
                                             itp_type = rt.Math.Interpolation.kPOLYNOMIAL,
                                             EPS=1E-2, Title=Title)
  if coupling_type == "tc":
    exclusion_extra.SetPoint(exclusion_extra.GetN(), exclusion.GetX()[-1],  1.0)
    exclusion_extra_exp.SetPoint(exclusion_extra_exp.GetN(), exclusion_exp.GetX()[-1],  1.0)

  exclusion_extra_exp.SetLineStyle(2)
  Hist_interp_extra.GetYaxis().SetNdivisions(505)
  Hist_interp_extra.GetYaxis().SetTitleSize(0.055)
  Hist_interp_extra.GetYaxis().SetTitleOffset(0.45) #gkole
  Hist_interp_extra.GetXaxis().SetTitleSize(0.05)
  Hist_interp_extra.GetXaxis().SetTitleOffset(0.80)

  Hist_interp_extra.Draw("COLZ")
  if unblind:
    exclusion_extra.Draw("same")
  exclusion_extra_exp.Draw("same")

  ## Text
  latex =  rt.TLatex();
  latex.SetNDC();
  latex.SetTextFont(42);
  latex.SetTextSize(0.03);
  latex.SetTextAlign(31);
  latex.SetTextAlign(12);
  latex.DrawLatex(0.16, 0.84, "g2HDM")
  if interference:
    latex.DrawLatex(0.16, 0.80, "m_{A} - m_{H} = 50 GeV");
  latex.SetTextSize(0.05)
  latex.SetTextColor(rt.kRed)
  if not interference and coupling_type == "tc":
    latex.DrawLatex(0.20, 0.72, "excluded")
  else:
    latex.DrawLatex(0.24,0.68, "excluded")

  ## Legend
  leg = rt.TLegend(.60, .72, .80, .80);
  leg.SetBorderSize(0);
  leg.SetFillColorAlpha(0,0.0);
  leg.SetShadowColor(0);
  leg.SetTextFont(42);
  leg.SetTextSize(0.04);
  if unblind:
    leg.AddEntry(exclusion_extra, "Observed", "L")
  leg.AddEntry(exclusion_extra_exp, "Expected", "L")
  leg.Draw("same")
 
  CMS_lumi.CMS_lumi(c, iPeriod, iPos, 0.135)

  limit_pdf_file = os.path.join(OUT_DIR,'Merged_Limit2D_Plots_For_{year}_{channel}_interp_extra.pdf'.format(year=year,channel=channel))
  c.SaveAs(limit_pdf_file)
  c.SaveAs(limit_pdf_file.replace(".pdf",".png"))
  c.SaveAs(limit_pdf_file.replace(".pdf",".C"))
  c.SaveAs(limit_pdf_file.replace(".pdf",".root"))



  ## Contour version

  Hist_interp_extra.SetContour(12, array('d',[10**(float(i)/3.-1.) for i in range(12)]))
  Hist_interp_extra.Draw("CONT4Z")
  CMS_lumi.CMS_lumi(c, iPeriod, iPos, 0.135)

  latex =  rt.TLatex();
  latex.SetNDC();
  latex.SetTextFont(42);
  latex.SetTextSize(0.03);
  latex.SetTextAlign(31);
  latex.SetTextAlign(12);
  latex.DrawLatex(0.62, 0.20, "g2HDM")
  if interference:
    latex.DrawLatex(0.62, 0.16, "m_{A} - m_{H} = 50 GeV");
  latex.SetTextSize(0.05)
  latex.SetTextColor(rt.kRed)

  if not interference and coupling_type == "tc":
    latex.DrawLatex(0.20, 0.72, "excluded")
  else:
    latex.DrawLatex(0.24,0.68, "excluded")

  limit_pdf_file = os.path.join(OUT_DIR,'Merged_Limit2D_Plots_For_{year}_{channel}_interp_extra_cont.pdf'.format(year=year,channel=channel))
  c.SaveAs(limit_pdf_file)
  c.SaveAs(limit_pdf_file.replace(".pdf",".png"))

  
  c.Close()
