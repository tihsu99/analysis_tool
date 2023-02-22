import os
import sys
CURRENT_WORKDIR = os.getcwd()
sys.path.append(CURRENT_WORKDIR)
from array import  array
from ROOT import TGraph, TFile, TGraphAsymmErrors
import ROOT as rt
import ROOT
import argparse
import csv 
import pandas as pd
from Util.General_Tool import CheckDir,CheckFile
 



def Plot_1D_Limit_For(log_files_dict={},unblind=False,y_max=10000,y_min=0.001,year='run2',channel='C',outputFolder='./',Masses=[200],interference=False):
    
    coupling_values = log_files_dict.keys()
    
    y_max=y_max # scale of y axis 
    y_min=y_min # scale of y axis 
    
    
    rt.gStyle.SetOptTitle(0)
    rt.gStyle.SetOptStat(0)
    rt.gROOT.SetBatch(1)
    c = rt.TCanvas("c","c",620, 600)
    c.SetGrid(0,0)
    c.SetLogy(1)
    c.SetLeftMargin(0.12)
    
    ##Frame
    
    model_ = '2HDM+a'
    ### Legend ####
    leg = rt.TLegend(.45, .65, .68, .890);
    leg.SetBorderSize(0);
    leg.SetFillColor(0);
    leg.SetShadowColor(0);
    leg.SetTextFont(42);
    leg.SetTextSize(0.03);
    
    
    colors = [2,4,6,28]     
    
    mg =ROOT.TMultiGraph("mg","mg")
    mg.SetTitle(";M_{A} [GeV];95% C.L. #mu=#sigma/#sigma_{theory}")
    mg.SetMinimum(y_min);
    mg.SetMaximum(y_max);
    end_point = len(coupling_values) -1
    for idx,coupling_value in enumerate(coupling_values):
        File_path_per_coupling_value = log_files_dict[coupling_value]
        coupling_value=coupling_value.replace('p','.')
        #### Set the Name in legend ####
        if 'rtc' in coupling_value :
            value = coupling_value.split('rtc')[-1]
            prefix = '#rho_{tc}=%s'%(value)
        elif 'rtu' in coupling_value :
            value = coupling_value.split('rtu')[-1]
            prefix = '#rho_{tu}=%s'%(value)
        elif 'rtt' in coupling_value :
            value = coupling_value.split('rtt')[-1]
            prefix = '#rho_{tt}=%s'%(value)
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
        #exp2s.GetXaxis().SetNdivisions(505);
        #exp2s.GetXaxis().SetMoreLogLabels()
        #exp2s.GetXaxis().SetRangeUser(10,750)
        
        mg.Add(exp2s,"A 3")

        exp1s =  File_per_coupling_value.Get("exp1")
        exp1s.SetMarkerStyle(20)
        exp1s.SetMarkerSize(1.1)
        exp1s.SetLineWidth(2)
        exp1s.SetFillColorAlpha(rt.kGreen,0.8);
        exp1s.SetLineColor(rt.kGreen)
        #exp1s.Draw("3")
        mg.Add(exp1s,"3")
    
        exp =  File_per_coupling_value.Get("expmed")
        exp.SetMarkerStyle(1)
        exp.SetMarkerSize(1.1)
        exp.SetLineColor(colors[idx])
        exp.SetLineStyle(2)
        exp.SetLineWidth(3)
        #exp.Draw("L")
        mg.Add(exp,"L")
        if unblind:
            obs =  File_per_coupling_value.Get("obs")
            obs.SetMarkerStyle(20)
            obs.SetMarkerSize(1.1)
            obs.SetLineWidth(3)
            mg.Add(obs, "LP") 
        leg.AddEntry(exp, Limit_Name+" CL_{S} Exp 95% Upper Limit", "LP");
        if idx==end_point:
            leg.AddEntry(exp1s,"Expected limit #pm 1 std. deviation","F")
            leg.AddEntry(exp2s,"Expected limit #pm 2 std. deviation","F")
            leg.AddEntry(obs, "Observed limit", "L");
        else:pass


    c.cd()
    #mg.SetTitleName(";Mass[GeV];#mu=#sigma/#sigma_{theory}")
    mg.Draw("same") 
    leg.Draw("same")

    
    import CMS_lumi
    CMS_lumi.writeExtraText = 1
    CMS_lumi.extraText = "Internal"
    CMS_lumi.lumi_sqrtS = "13 TeV" # used with iPeriod = 0, e.g. for simulation-only plots (default is an empty string)
    iPos = 11
    if( iPos==0 ): CMS_lumi.relPosX = 0.12
    iPeriod=year

    CMS_lumi.CMS_lumi(c, iPeriod, iPos)

    
    
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
    latex.DrawLatex(0.20, 0.84, "ExtraYukawa")
    latex.DrawLatex(0.20, 0.8, year + " " + channel)
    if interference:
      latex.DrawLatex(0.20, 0.76, "m_{A}-m_{H} = 50 GeV");

    
    c.Update()
    

    ### Output File Setting ###
    OUT_DIR = os.path.join(outputFolder,"plots_limit")

    limit_pdf_file = 'Merged_Limit_Plots_For_{year}_{channel}.pdf'.format(year=year,channel=channel)
    
    CheckDir(OUT_DIR,True)
    limit_pdf_file  = os.path.join(OUT_DIR,limit_pdf_file)
    
    CheckFile(limit_pdf_file,True)
    
    c.SaveAs(limit_pdf_file)
    limit_png_file = limit_pdf_file.replace(".pdf",".png")

    CheckFile(limit_png_file,True)
    c.SaveAs(limit_png_file)
    
    c.Close()

