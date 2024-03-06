import uproot
import torch
import ROOT
import os, sys
import json
import optparse, argparse
sys.path.insert(1, '../../python')
from common import *
import numpy as np
import optparse, argparse
import pandas as pd
from sklearn.preprocessing import StandardScaler
import pickle

def load_data(file_list, var, label, chunk, total_chunk, total_weight, mass):

  return_pd = None
    
  for file_ in file_list:
    event = uproot.open("{}:Events".format(file_))
    features = event.arrays(var, "weight_n_Norm>0", library='pd')
    features.insert(0, "Label", (np.ones(features.shape[0])*label).astype(int), True)
    features.insert(1, "Mass",  (np.ones(features.shape[0])*mass).astype(float), True)
    features = features.reset_index(drop=True)
    features = features[chunk::total_chunk]
    features = features.reset_index(drop=True)
    if return_pd is None:
      return_pd = features
    else:
      return_pd = pd.concat([return_pd, features], ignore_index=True)
    del event
    del features
  return_pd['class_weight'] = return_pd['weight_n_Norm'] / total_weight * 1000 # Norm to 1000
  return_pd = return_pd.reset_index(drop=True)
  return return_pd

def Integral_file_list(file_list,):
  count = 0
  weight = 0
  for file_ in file_list:
    event = uproot.open("{}:Events".format(file_))
    Weight = event.arrays('weight_n_Norm', 'weight_n_Norm>0', library="np")['weight_n_Norm']
    count += len(Weight)
    weight += np.sum(Weight)
    del Weight
    del event
  return count, weight

def Count_n_Weight(indir, eras, regions, channels, sample_json):
  Count_ = dict()
  Weight_ = dict()

  for era in eras:
    for region in regions:
      for channel in channels:
        Bkg_file_list = []
        Sig_file_list = []
        dir_ = os.path.join(indir, era, region, channel)
        # For background
        Bkg_list = Get_Sample(sample_json, ["MC", "Background"], era, withTail = False)
        Bkg_file_list += [os.path.join(dir_, '{}.root'.format(sample)) for sample in Bkg_list]
        count_, weight_ = Integral_file_list(Bkg_file_list)
        if "Background" not in Count_:
          Count_["Background"] = count_
          Weight_["Background"] = weight_
        else:
          Count_["Background"] += count_
          Weight_["Background"] += weight_

 
        # For signal
        Sig_list = Get_Sample(sample_json, ["MC", "Signal"], era, withTail = False)
        for sig_ in Sig_list:
          if "BG" in sig_: continue # TODO: remove bg signal just in current stage
          Sig_file_list = [os.path.join(dir_, '{}.root'.format(sig_))]
          count_, weight_ = Integral_file_list(Sig_file_list)
          if sig_ not in Count_:
            Count_[sig_] = count_
            Weight_[sig_] = weight_
          else:
            Count_[sig_] += count_
            Weight_[sig_] += weight_
        
  return Count_, Weight_ 

def Create_Shuffled_dataset(indir, outdir, eras, regions, channels, sample_json, chunk_size, var):

  Count_, Weight_ = Count_n_Weight(indir, eras, regions, channels, sample_json)
  num_chunk = (Count_["Background"] // chunk_size) + 1
  df_file_list = []

  for chunk_ in range(num_chunk):
    df = None
    for era in eras:
      for region in regions:
        for channel in channels:
          Bkg_file_list = []
          Sig_file_list = []
          dir_ = os.path.join(indir, era, region, channel)
    
          # For background
          Bkg_list = Get_Sample(sample_json, ["MC", "Background"], era, withTail=False)
          Bkg_file_list += [os.path.join(dir_, '{}.root'.format(sample)) for sample in Bkg_list]
          df_bkg = load_data(Bkg_file_list, var, 0, chunk_, num_chunk, Weight_["Background"], mass=-1)
          if df is None:
            df = df_bkg
          else:
            df = pd.concat([df, df_bkg], ignore_index=True)

          # For signal
          Sig_list = Get_Sample(sample_json, ["MC", "Signal"], era, withTail = False)
          for sig_ in Sig_list:
            if "BG" in sig_: continue # TODO: remove bg signal just in current stage
            mass = float(sig_.replace('CGToBHpm_a_','').replace('_rtt06_rtc04',''))
            Sig_file_list = [os.path.join(dir_, '{}.root'.format(sig_))]
            df_sig = load_data(Sig_file_list, var, 1, chunk_, num_chunk, Weight_[sig_], mass=mass)
            df = pd.concat([df, df_sig], ignore_index=True)
    df = df.reset_index(drop=True).sample(frac=1)
    print(df)
    df.to_hdf(os.path.join(outdir, 'training_data_{}_raw.h5'.format(chunk_)), key = 'df', mode='w')
    df_file_list.append(os.path.join(outdir, 'training_data_{}_raw.h5'.format(chunk_)))

  scaler = dict()

  var.append('Mass')

  for var_ in var:
    scaler[var_] = StandardScaler()
  for df_file_ in df_file_list:
    df_ = pd.read_hdf(df_file_, 'df')
    for var_ in var:
      scaler[var_].partial_fit(df_[[var_]].values)
  for var_ in var:
    if (scaler[var_].scale_ < 1e-14):
      scaler[var_].scale_=[1.0]
    print(var_, scaler[var_].mean_, scaler[var_].scale_)
  
  dbfile = open(os.path.join(outdir, 'preprocessor.pkl'), 'ab')
  pickle.dump(scaler, dbfile)
  for df_file_ in df_file_list:
    df_ = pd.read_hdf(df_file_, 'df')
    for var_ in var:
      var_transformed = var_ if not var_ == 'Mass' else 'Mass_transformed'
      df_[[var_transformed]] = scaler[var_].transform(df_[[var_]])
    df_.to_hdf(df_file_.replace('raw', 'scaled'), key='df', mode='w')
    print(df_)
  
if __name__ == '__main__':
  usage = 'usage: %prog [options]'
  parser =  argparse.ArgumentParser(description=usage)
  parser.add_argument('-e', '--era', dest='era', help='[2016apv/2016postapv/2017/2018]', default=['2017'], type=str, nargs='+')
  parser.add_argument('--region', type = str, nargs='+', default=['SR_3b3j'])
  parser.add_argument('--channel', type = str, nargs='+', default=['ele_resolved', 'mu_resolved'])
  parser.add_argument('--hyperparameter_tuning', action = 'store_true')
  parser.add_argument('--indir', type = str)
  parser.add_argument('--outdir', type = str, default = './')
  parser.add_argument('--sample_json', type=str, default="../../data/sample.json")
  parser.add_argument('--MVA_json', type=str, default="../../data/MVA.json")
  parser.add_argument('--postfix', type = str, default = 'CGToBHpm_a_500_rtt06_rtc04')
  parser.add_argument('--chunk_size', type=int, default = 100000)
  args = parser.parse_args()

  MVA_json = read_json(args.MVA_json)
  var = MVA_json['xgboost']
  var.append('weight_n_Norm')

  if not os.path.exists(args.outdir):
    os.system('mkdir -p {}'.format(args.outdir))
  Create_Shuffled_dataset(args.indir, args.outdir, args.era, args.region, args.channel, args.sample_json, args.chunk_size, var)
