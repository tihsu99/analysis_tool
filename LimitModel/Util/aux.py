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
import array

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

def redefine_binning(Histogram_concatenated, new_binning):
    """
    Redefine the binning of histograms in Histogram_concatenated.

    Parameters:
    Histogram_concatenated (dict): Dictionary of histograms to be rebinned.
    new_binning (list): List of bin edges for the new binning.
    """
    for category, hist in Histogram_concatenated.items():
        # Create a new histogram with the new binning
        new_hist = ROOT.TH1F(hist.GetName() + "_rebin", hist.GetTitle(), len(new_binning) - 1, array.array('d', new_binning))

        # Fill the new histogram with the contents of the old histogram
        for bin_idx in range(1, new_hist.GetNbinsX() + 1):
            bin_content = hist.GetBinContent(bin_idx)
            bin_error = hist.GetBinError(bin_idx)
            # bin_center = hist.GetBinCenter(bin_idx)
            # new_bin_idx = new_hist.FindBin(bin_center)
            new_hist.SetBinContent(bin_idx, bin_content)
            new_hist.SetBinError(bin_idx, bin_error)

        # Replace the old histogram with the new histogram
        Histogram_concatenated[category] = new_hist