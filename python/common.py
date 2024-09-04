import os
import sys
import json
import ROOT
from collections import OrderedDict
from math import sqrt
import copy
from termcolor import cprint 

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
   '2016apv':     '/eos/cms/store/group/phys_b2g/ExYukawa/bHplus/2016apv/v6/', 
   '2016postapv': '/eos/cms/store/group/phys_b2g/ExYukawa/bHplus/2016/v6/', 
   '2017':        '/eos/cms/store/group/phys_b2g/ExYukawa/bHplus/2017/v7/', 
   '2018':        '/eos/cms/store/group/phys_b2g/ExYukawa/bHplus/2018/v6/'
}

subera_list = {
  '2016apv':     ['B2', 'C', 'D', 'E', 'F'],
  '2016postapv': ['F',  'G', 'H'],
  '2017':        ['B',  'C', 'D', 'E', 'F'],
  '2018':        ['A',  'B', 'C', 'D_1', 'D_2']
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


Lumi_text = {
  '2016apv': '19.5',
  '2016postapv': '16.8',
  '2017': '41.5',
  '2018': '59.8'
}
#############
##  Shell  ##
#############

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

def store_json(dict_, fname):
  with open(fname, 'w') as json_file:
    json.dump(dict_, json_file, indent = 4)

##############
##  Sample  ##
##############


def find_all(name, path):
    result = []
    for root, dirs, files in os.listdir(path):
        if name in files:
            result.append(os.path.join(root, name))
    return result


def Extend_sample_dict(dict_, key_word = 'MASS'):
  dict_clone = copy.deepcopy(dict_)
  for sample_ in dict_:
    has_keyword = False
    if key_word in dict_[sample_]: has_keyword = True
    if has_keyword:
      for element_ in dict_[sample_][key_word]:
        new_sample = sample_.replace(key_word, str(element_))
        dict_clone[new_sample] = dict()
        for key in dict_[sample_]:
          if isinstance(dict_[sample_][key], str):
            dict_clone[new_sample][key] = dict_[sample_][key].replace(key_word, str(element_))
          else:
            dict_clone[new_sample][key] = dict_[sample_][key]
      del dict_clone[sample_]
  return dict_clone
        

def Get_Sample(json_file_name, Labels, era, withTail=True):

####################################################
# Train_idx:                                       #
#  -1: not used for any case                       #
#   0: not used for training, but for application  #
#   1: used for both training and application      #
####################################################

  jsonfile = open(json_file_name)
  if python_version == 2:
    samples  = json.load(jsonfile, encoding='utf-8')
  else:
    samples  = json.load(jsonfile)
  jsonfile.close()

  samples = Extend_sample_dict(samples, key_word = 'MASS')
  samples = samples.items()
  File_List = []
  for process, desc in samples:
    Flag = True
    for Label in Labels:
      if Label not in desc["Label"]:
        Flag = False

    if ("Era" in desc) and (era not in desc["Era"]): continue
    
    if Flag:
      if withTail:
        dirs = os.listdir(inputFile_path[era])
        if "subfile" in desc: sublist_ = desc["subfile"][era]
        elif "Data" in desc["Label"]: sublist_ = ["_" + subera for subera in subera_list[era]]
        else: sublist_ = [""]
        for sub_ in sublist_:
          file_ = process + sub_ + ".root"
          if not os.path.exists(os.path.join(inputFile_path[era], file_)): cprint(os.path.join(inputFile_path[era], file_) +  ' not exists', 'yellow')
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
  'ttXY':ROOT.kPink-3,
  'TT1L':ROOT.kViolet-4,
  'tZq':ROOT.kYellow+1,
  'TT2L':ROOT.kBlue,
  'ttW':ROOT.kGreen-2,
  'ttZ':ROOT.kCyan-2,
  'VBS':ROOT.kBlue-6,
  'ttH':ROOT.kRed-9,
  'WJets':ROOT.kOrange+3,
  'SingleTop':ROOT.kGray,
  'DY': ROOT.kYellow-4,
  'QCD': ROOT.kOrange-2,
  'TTHad': ROOT.kBlue + 1
}

Color_Dict_ref = {
  'TT': ROOT.TColor.GetColor("#3f90da"),
  'WJets': ROOT.TColor.GetColor("#ffa90e"),
  'SingleTop': ROOT.TColor.GetColor("#bd1f01"),
  'QCD': ROOT.TColor.GetColor("#94a4a2"),
  'DY': ROOT.TColor.GetColor("#832db6"),
  'VVV': ROOT.TColor.GetColor("#a96b59"),
  'ttX': ROOT.TColor.GetColor("#e76300"),
  'ttW': ROOT.TColor.GetColor("#b9ac70"),
  'ttXY': ROOT.TColor.GetColor("#717581"),
  'cgTotH': ROOT.TColor.GetColor("#92dadd")
}

Color_List_Signal = [ROOT.TColor.GetColor("#92dadd"), ROOT.kOrange, ROOT.kCyan, ROOT.kBlue+2, ROOT.kViolet-1, ROOT.kPink, ROOT.kCyan-9, ROOT.kBlue, ROOT.kOrange+3, ROOT.kViolet, ROOT.kRed+2]


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
  h.SetBinContent(addX, addY, 0)
  h.SetBinError(addX, addY, 0)
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


def CheckDir(path):
  if not os.path.exists(path):
    os.system('mkdir -p {}'.format(path))