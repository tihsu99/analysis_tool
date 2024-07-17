import torch
from torch import nn
from sklearn.preprocessing import StandardScaler
import numpy as np
import ROOT
import optparse, argparse
import sys, os
from torch import nn
from model import DNN, Ensemble_DNN
sys.path.insert(1, '../../python')
from common import *
import pickle
import torchvision.transforms as transform

CWD = os.getcwd()

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
  parser.add_argument('--Ensemble', action='store_true')
  parser.add_argument('--postfix', type=str, default='')
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

  if not args.Ensemble:
    model = DNN(len(param['var']), l1 = param['l1'], l2 = param['l2'], l3 = param['l3'], dropout = param['dropout']) 
    model = torch.load(os.path.join(args.indir, 'model.pt'), map_location=torch.device('cpu'))
    model = nn.Sequential(model, nn.Sigmoid())
    model.eval()
    xinput = torch.zeros((1, len(param['var'])))
    torch.onnx.export(model, xinput, os.path.join(args.outdir, "DNN{}.onnx".format(args.postfix)), export_params=True)
  else:
    test_loss = dict()
    for file_ in os.listdir(args.indir):
      if not ("training_result_kfold" in file_): continue
      training_result = read_json(os.path.join(args.indir, file_))
      fold = file_.replace("training_result_kfold", '').replace('.json', '')
      test_loss[fold] = training_result['test_losses'][-1]
    store_json(test_loss, os.path.join(args.indir, 'test_loss.json'))
    test_loss_json = test_loss
    os.system('cp {test_loss_json} {outdir}/test_loss_DNN{postfix}.json'.format(test_loss_json = os.path.join(args.indir, 'test_loss.json'), outdir = args.outdir, postfix=args.postfix))
    models = []
    test_loss = []
    for fold in test_loss_json:
      model = DNN(len(param['var']), l1 = param['l1'], l2 = param['l2'], l3 = param['l3'], dropout = param['dropout'])
      model = torch.load(os.path.join(args.indir, 'model_fold{}.pt'.format(fold)), map_location=torch.device('cpu'))
      model.eval()
      xinput = torch.zeros((1, len(param['var'])))
      test_loss.append(test_loss_json[fold])
      torch.onnx.export(model, xinput, os.path.join(args.outdir, "DNN{}_fold{}.onnx".format(args.postfix, fold)), export_params=True)


  os.chdir(args.outdir)
  os.system('cp {preprocessor} preprocessor_DNN{postfix}.pkl'.format(preprocessor=args.preprocessor, postfix = args.postfix))
  if not args.Ensemble:
    os.system('root -l -b -q {CWD}/../..//script/TMVA_SOFIE_ONNX.C\\(\\"DNN{postfix}.onnx\\"\\)'.format(CWD=CWD, postfix = args.postfix))
  else:
    for fold in test_loss_json:
      os.system('root -l -b -q {CWD}/../../script/TMVA_SOFIE_ONNX.C\\(\\"DNN{postfix}_fold{fold}.onnx\\"\\)'.format(postfix = args.postfix, fold=fold, CWD=CWD))
#  model = nn.Sequential(preprocessor, model, nn.Sigmoid()) #SOFIE do not support Constant Operation -> preporcessor block is not possible
#  print(preprocessor(xinput))
#  print(model(xinput))
