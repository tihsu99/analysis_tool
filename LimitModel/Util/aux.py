#! /usr/bin/env python

#================================================================================================ 
# Imports
#================================================================================================ 
import sys
sys.path.insert(1,'Util')
import ShellStyles as ShellStyles
import os
import hashlib
import imp
import re
import stat
import ROOT
import ctypes
import getpass
import socket

#================================================================================================ 
# Shell colours
#================================================================================================ 
ss = ShellStyles.SuccessStyle()
ns = ShellStyles.NormalStyle()
ts = ShellStyles.NoteStyle()
hs = ShellStyles.HighlightAltStyle()
ls = ShellStyles.HighlightStyle()
es = ShellStyles.ErrorStyle()
cs = ShellStyles.CaptionStyle()

#================================================================================================ 
# Function definition
#================================================================================================ 
def Verbose(msg, printHeader=True, verbose=False):
    '''
    Calls Print() only if verbose options is set to true
    '''
    if not verbose:
        return
    Print(msg, printHeader)
    return

def Print(msg, printHeader=True):
    '''
    Simple print function. If verbose option is enabled prints, otherwise does nothing
    '''
    fName = __file__.split("/")[-1]
    if printHeader:
        print("=== ", fName)
    print("\t", msg)
    return

def PrintFlushed(msg, printHeader=True):
    '''
    Useful when printing progress in a loop
    '''
    msg = "\r\t" + msg
    ERASE_LINE = '\x1b[2K'
    if printHeader:
        print("=== aux.py")
    sys.stdout.write(ERASE_LINE)
    sys.stdout.write(msg)
    sys.stdout.flush()
    return

def combine_histograms(hist1, hist2):
    """
    Combines two TH1F histograms by concatenating their bins.
    
    :param hist1: First TH1F histogram
    :param hist2: Second TH1F histogram
    :return: New TH1F histogram with concatenated bins from hist1 and hist2
    """
    # Determine the new histogram's binning and range
    nbins_combined = hist1.GetNbinsX() + hist2.GetNbinsX()
    
    # Create a new histogram with combined bins
    hist_combined = ROOT.TH1F("hist_combined", "Combined Histogram", nbins_combined, 0, nbins_combined)
    
    # Fill the new histogram with contents from hist1 and hist2
    for i in range(1, hist1.GetNbinsX() + 1):
        hist_combined.SetBinContent(i, hist1.GetBinContent(i))
        hist_combined.SetBinError(i, hist1.GetBinError(i))
        
    for i in range(1, hist2.GetNbinsX() + 1):
        hist_combined.SetBinContent(i + hist1.GetNbinsX(), hist2.GetBinContent(i))
        hist_combined.SetBinError(i + hist1.GetNbinsX(), hist2.GetBinError(i))
    
    return hist_combined

cwd = os.getcwd()
dir_list = cwd.split('/')
cmssw_list = []
for dir_ in dir_list:
  cmssw_list.append(dir_)
  if 'CMSSW' in dir_: break
cmsswBase = '/'.join(cmssw_list)

def prepare_shell(shell_file, command, condor, FarmDir, cmssw = False):

###############
# Func: prepare sh file and add it to the condor schedule.
###############

  cwd = os.getcwd()
  with open(os.path.join(FarmDir, shell_file), 'w') as shell:
    shell.write('#!/bin/bash\n')
    shell.write('WORKDIR=%s\n'%cwd)
    shell.write('cd %s\n'%cmsswBase)
    if cmssw:
      shell.write('eval `scram r -sh`\n')
    shell.write('cd ${WORKDIR}\n')
    if not cmssw:
      shell.write('source script/env.sh\n')
    shell.write(command)

  condor.write('%s,'%shell_file)
