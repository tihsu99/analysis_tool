import argparse
import os
import sys
import numpy as np
CURRENT_WORKDIR = os.getcwd()
sys.path.append(CURRENT_WORKDIR)

def ExtractLimit(Mass, Limit):
  Limit_result = []
#  print(Mass, Limit)
  for i in range(len(Limit)-1):
    if((Limit[i] <= 1 and Limit[i+1] >= 1) or (Limit[i] >= 1 and Limit[i+1] <= 1)):
      y1 = float(Limit[i])
      y2 = float(Limit[i+1])
      m1 = float(Mass[i])
      m2 = float(Mass[i+1])
      limit = m1 + (m2 - m1) * np.log(1./y1) / np.log(y2/y1)
      Limit_result.append(round(limit,3))
  if len(Limit_result) == 0:
    if Limit[0] > 1:
      return "no limit"
    else:
      return [Mass[0], Mass[-1] ] 
  else:
    Limit_result.insert(0,Mass[0])
    return Limit_result


parser = argparse.ArgumentParser()
channel_choices = ['C', 'ee', 'em', 'mm']
year_choices    = ['2016apv', '2016postapv', '2017', '2018', 'run2']
coupling_choices = ['rtc','rtu']

parser.add_argument('-y','--year',help='Years of data.', default='run2',choices=year_choices)
parser.add_argument('-c','--channel',help='Channel of data.', default='C',choices=channel_choices)
parser.add_argument('--coupling_values',help='coupling type',default=['rtc0p4'],nargs='+')
parser.add_argument("--interference",action='store_true')
parser.add_argument("--unblind", action='store_true')

args = parser.parse_args()

for coupling in args.coupling_values:
  InputFile = 'bin/%s/%s/limits_ttc_%s_asimov_extYukawa.txt'%(args.year,args.channel,coupling) 
  if args.interference:
    InputFile = InputFile.replace('extYukawa','extYukawa_interference')
  FileIn = open(InputFile,'r')
  records = FileIn.readlines()
  Mass = []
  Limit = []
  Limit_observed = []
  for record in records:
    record = record.split(' ')
    Mass.append(float(record[1]))
    Limit.append(float(record[4]))
    if args.unblind:
      Limit_observed.append(float(record[7]))
  if not args.unblind:
    print("----------- blind ------------")
    Limit = ExtractLimit(Mass, Limit)
    print(coupling,Limit)
  else:
    print("----------- unblind -------------")
    Limit = ExtractLimit(Mass, Limit)
    Limit_observed = ExtractLimit(Mass, Limit_observed)
    print(coupling,'Observed',Limit_observed,'Expected',Limit)
  FileIn.close()
