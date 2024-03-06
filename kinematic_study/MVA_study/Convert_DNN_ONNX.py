import torch
from torch import nn
from sklearn.preprocessing import StandardScaler
import numpy as np
import ROOT
import optparse, argparse
import sys, os
from torch import nn
from Training_DNN import DNN
sys.path.insert(1, '../../python')
from common import *
import pickle
import torchvision.transforms as transform

class Preprocessor(nn.Module):
  def __init__(self, mean, std):
    super().__init__()
    self.mean = mean
    self.std = std
  def forward(self, x):
    x_transformed = (x - self.mean)/self.std
    return x_transformed

if __name__ == '__main__':
  usage = 'usage: %prog [options]'
  parser =  argparse.ArgumentParser(description=usage)
  parser.add_argument('--indir',  type = str)
  parser.add_argument('--preprocessor', type=str)
  parser.add_argument('--outdir', type = str, default='./')
  args = parser.parse_args()

  if not os.path.exists(args.outdir):
    os.system('mkdir -p {}'.format(args.outdir))

  param = read_json(os.path.join(args.indir, 'param.json'))
  with open(args.preprocessor, 'rb') as f:
    preprocessor = pickle.load(f)


  mean = []
  std  = []
  for var_ in param['var']:
    if var_ == 'Mass_transformed':
      var_ = 'Mass'
    print(var_, preprocessor[var_].mean_, preprocessor[var_].scale_)
    mean.append(preprocessor[var_].mean_)
    std.append(preprocessor[var_].scale_)

  mean = torch.FloatTensor(np.array(mean).reshape((1, len(param['var']))))
  std  = torch.FloatTensor(np.array(std).reshape((1, len(param['var']))))

  preprocessor = Preprocessor(mean, std)

  model = DNN(len(param['var']), l1 = param['l1'], l2 = param['l2'], dropout = param['dropout']) 
  model = torch.load(os.path.join(args.indir, 'model.pt'), map_location=torch.device('cpu'))
  #model = nn.Sequential(preprocessor, model, nn.Sigmoid()) #SOFIE do not support Constant Operation -> preporcessor block is not possible
  model = nn.Sequential(model, nn.Sigmoid())
  model.eval()
  xinput = torch.zeros((1, len(param['var'])))
#  print(preprocessor(xinput))
#  print(model(xinput))
  torch.onnx.export(model, xinput, os.path.join(args.outdir, "DNN.onnx"), export_params=True)
