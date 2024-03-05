import os
import sys
import ROOT
import json
import ROOT
from collections import OrderedDict
from math import sqrt

cwd = os.getcwd()
dir_list = cwd.split('/')
cmssw_list = []
for dir_ in dir_list:
  cmssw_list.append(dir_)
  if 'CMSSW' in dir_: break
cmsswBase = '/'.join(cmssw_list)

##########################
## Check python version ##
##########################

python_version = int(sys.version.split('.')[0])

############
##  Path  ##
############

inputFile_path = {
  '2016apv':     '/eos/cms/store/group/phys_top/ExtraYukawa/2016apvMerged/',
  '2016postapv': '/eos/cms/store/group/phys_top/ExtraYukawa/2016postapvMerged/',
  '2017':        '/eos/cms/store/group/phys_b2g/ExYukawa/bHplus/2017/v4',
  '2018':        '/eos/cms/store/group/phys_b2g/ExYukawa/bHplus/2018/'
}

subera_list = {
  '2016apv':     ['B2', 'C', 'D', 'E', 'F'],
  '2016postapv': ['F',  'G', 'H'],
  '2017':        ['B',  'C', 'D', 'E', 'F'],
  '2018':        ['A',  'B', 'C', 'D_0','D_1']
}

###########
## Lumi  ##
###########

Lumi = {
  '2016apv': 19520.,
  '2016postapv': 16810.,
  '2017': 41480.,
  '2018': 59830.
}

#############
##  Shell  ##
#############

def prepare_shell(shell_file, command, condor, FarmDir):

###############
# Func: prepare sh file and add it to the condor schedule.
###############

  cwd = os.getcwd()
  with open(os.path.join(FarmDir, shell_file), 'w') as shell:
    shell.write('#!/bin/bash\n')
    shell.write('WORKDIR=%s\n'%cwd)
    shell.write('cd %s\n'%cmsswBase)
    #shell.write('eval `scram r -sh`\n')
    shell.write('cd ${WORKDIR}\n')
    shell.write('source script/env.sh\n')
    shell.write(command)

  condor.write('cfgFile=%s\n'%shell_file)
  condor.write('queue 1\n') 
 

##########
## json ##
##########

def read_json(fname):
  jsonfile = open(fname)
  if python_version == 2:
    return_ =  json.load(jsonfile, encoding='utf-8', object_pairs_hook=OrderedDict)
  else:
    return_ =  json.load(jsonfile, object_pairs_hook=OrderedDict)
  jsonfile.close()
  return return_

##############
##  Sample  ##
##############


def find_all(name, path):
    result = []
    for root, dirs, files in os.listdir(path):
        if name in files:
            result.append(os.path.join(root, name))
    return result

def Get_Sample(json_file_name, Labels, era, withTail=True):

####################################################
# Train_idx:                                       #
#  -1: not used for any case                       #
#   0: not used for training, but for application  #
#   1: used for both training and application      #
####################################################

  jsonfile = open(json_file_name)
  if python_version == 2:
    samples  = json.load(jsonfile, encoding='utf-8', object_pairs_hook=OrderedDict).items()
  else:
    samples  = json.load(jsonfile, object_pairs_hook=OrderedDict).items() 
  jsonfile.close()

  File_List = []
  for process, desc in samples:
    Flag = True

    for Label in Labels:
      if Label not in desc["Label"]:
        Flag = False
    if Flag:
      if withTail:
        dirs = os.listdir(inputFile_path[era])
        if "subfile" in desc: sublist_ = desc["subfile"]
        elif "Data" in desc["Label"]: sublist_ = ["_" + subera for subera in subera_list[era]]
        else: sublist_ = [""]
        for sub_ in sublist_:
          file_ = process + sub_ + ".root"
          if not os.path.exists(os.path.join(inputFile_path[era], file_)): print(os.path.join(inputFile_path[era], file_), 'not exists')
          else:
            File_List.append(file_)
      else:
        File_List.append(process)
  return File_List

##########################
##  Color For Plotting  ##
##########################

pdgId_Dict = {'d':1, 'u':2, 's':3, 'c':4, 'b':5, 't':6, 'e': 11, '#nu_{e}': 12, '#mu': 13, '#nu_{#mu}': 14, '#tau': 15, '#nu_{#tau}':16, 'g': 21, '#gamma':22, 'z':23, 'w':24, 'h':25, 'H+':26}

Color_Dict_ref = {
  'cgTotH':ROOT.kRed,
  'bgTotH':ROOT.kCyan-9,
  'VVV':ROOT.kSpring - 9,
  'tttX':ROOT.kPink-3,
  'TT1L':ROOT.kViolet-4,
  'tZq':ROOT.kYellow-4,
  'TT2L':ROOT.kBlue,
  'ttW':ROOT.kGreen-2,
  'ttZ':ROOT.kCyan-2,
  'VBS':ROOT.kBlue-6,
  'ttH':ROOT.kRed-9,
  'WJet':ROOT.kOrange+3,
  'SingleTop':ROOT.kGray,
  'DY': ROOT.kYellow-4,
  'Nonprompt': ROOT.kOrange-2
}

Color_List_Signal = [ROOT.kRed, ROOT.kOrange, ROOT.kBlue, ROOT.kViolet, ROOT.kPink, ROOT.kCyan, ROOT.kCyan-9, ROOT.kBlue+2, ROOT.kOrange+3, ROOT.kViolet-1, ROOT.kRed+2]

def overunder_flowbin(h1):
  h1.SetBinContent(1,h1.GetBinContent(0)+h1.GetBinContent(1))
  h1.SetBinError(1,sqrt(h1.GetBinError(0)*h1.GetBinError(0)+h1.GetBinError(1)*h1.GetBinError(1)))
  h1.SetBinContent(h1.GetNbinsX(),h1.GetBinContent(h1.GetNbinsX())+h1.GetBinContent(h1.GetNbinsX()+1))
  h1.SetBinError(h1.GetNbinsX(),sqrt(h1.GetBinError(h1.GetNbinsX())*h1.GetBinError(h1.GetNbinsX())+h1.GetBinError(h1.GetNbinsX()+1)*h1.GetBinError(h1.GetNbinsX()+1)))
  return h1

########################
##  OverFlow Binning  ##
########################


def overunder_flowbin(h1):
  h1.SetBinContent(1,h1.GetBinContent(0)+h1.GetBinContent(1))
  h1.SetBinError(1,sqrt(h1.GetBinError(0)*h1.GetBinError(0)+h1.GetBinError(1)*h1.GetBinError(1)))
  h1.SetBinContent(h1.GetNbinsX(),h1.GetBinContent(h1.GetNbinsX())+h1.GetBinContent(h1.GetNbinsX()+1))
  h1.SetBinError(h1.GetNbinsX(),sqrt(h1.GetBinError(h1.GetNbinsX())*h1.GetBinError(h1.GetNbinsX())+h1.GetBinError(h1.GetNbinsX()+1)*h1.GetBinError(h1.GetNbinsX()+1)))
  return h1

def Add_2Dbin(h,addedX,addedY,addX,addY):
  h.SetBinContent(addedX, addedY, h.GetBinContent(addedX,addedY) + h.GetBinContent(addX,addY))
  h.SetBinError(addedX, addedY, sqrt(h.GetBinError(addedX, addedY)*h.GetBinError(addedX, addedY) + h.GetBinError(addX,addY)*h.GetBinError(addX,addY)))
  return h

def overunder_flowbin2D(h1):
  nbinX = h1.GetNbinsX()
  nbinY = h1.GetNbinsY()

  # Add Edge
  for i in range(nbinX):
    h1 = Add_2Dbin(h1, i+1,     1, i+1,       0)
    h1 = Add_2Dbin(h1, i+1, nbinY, i+1, nbinY+1)
  for i in range(nbinY):
    h1 = Add_2Dbin(h1,     1, i+1,       0, i+1)
    h1 = Add_2Dbin(h1, nbinX, i+1, nbinX+1, i+1)

  # Add Corner
  h1 = Add_2Dbin(h1, 1,         1,       0,       0)
  h1 = Add_2Dbin(h1, 1,     nbinY,       0, nbinY+1)
  h1 = Add_2Dbin(h1, nbinX,     1, nbinX+1,       0)
  h1 = Add_2Dbin(h1, nbinX, nbinY, nbinX+1, nbinY+1)
  return h1
