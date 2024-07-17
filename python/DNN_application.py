import ROOT
from sklearn.preprocessing import StandardScaler
import torch
import os, sys
sys.path.append('../../python')
from common import *
import pickle

def Build_DNN_Command(var, DNN_Label = 'DNN', DNN_dir = './'):
  ROOT.gInterpreter.Declare('#include "../../data/{}/{}.hxx"'.format(DNN_dir,DNN_Label))
  with open('../../data/{}/preprocessor_{}.pkl'.format(DNN_dir, DNN_Label), 'rb') as f:
     preprocessor = pickle.load(f)

  mean_array = []
  std_array  = []
  input_def = ''
  func_input = []
  for idx, var_ in enumerate(var):
    input_def += 'input[{idx}] = {var_};\n'.format(idx=idx, var_=var_)
    func_input.append('float {var_}'.format(var_=var_))
    mean_array.append(preprocessor[var_].mean_[0])
    std_array.append(preprocessor[var_].scale_[0])

  mean_array = ['{}'.format(x) for x in mean_array]
  std_array  = ['{}'.format(x) for x in std_array]
  mean_array = '{' + ', '.join(mean_array) + '}'
  std_array  = '{' + ', '.join(std_array)  + '}'

  func_def = 'vector<float> {}({})'.format(DNN_Label, ','.join(func_input))


  command = '\
  #include "ROOT/RDataFrame.hxx"\n\
  TMVA_SOFIE_{DNN_Label}::Session model("../../data/{DNN_dir}/{DNN_Label}.dat");\n\
  {func_def} {{ \n\
    float Preprocessor_mean[{nvar}] = {mean_array};\n\
    float Preprocessor_std[{nvar}]  = {std_array};\n\
    float input[{nvar}]; \n\
    {input_def}; \n\
    for(int input_idx=0; input_idx < {nvar}; input_idx++){{\n\
      input[input_idx] = (input[input_idx]-Preprocessor_mean[input_idx])/Preprocessor_std[input_idx];\n\
    }}\n\
    vector<float> score = model.infer(input);\n\
    return score;\
  }}\
  '.format(func_def=func_def, nvar=len(var), mean_array=mean_array, std_array=std_array, input_def=input_def, DNN_Label=DNN_Label, DNN_dir = DNN_dir)

  ROOT.gInterpreter.Declare(str(command))
  print(command)

def Build_EnsembleDNN_Command(var, DNN_Label = 'DNN', DNN_dir = './'):

  test_loss = read_json(os.path.join('../../data', DNN_dir, 'test_loss_{DNNLabel}.json'.format(DNNLabel = DNN_Label)))
  total_inv_loss = 0
  for fold in test_loss:
    ROOT.gInterpreter.Declare('#include "../../data/{DNN_dir}/{DNN_Label}_fold{fold}.hxx"'.format(DNN_dir=DNN_dir, fold = fold, DNN_Label = DNN_Label))
    total_inv_loss += 1.0 / test_loss[fold]
  weight = dict()
  for fold in test_loss:
    weight[fold] = 1.0 / test_loss[fold] / total_inv_loss

  with open('../../data/{}/preprocessor_{}.pkl'.format(DNN_dir, DNN_Label), 'rb') as f:
    preprocessor = pickle.load(f)

  mean_array = []
  std_array  = []
  input_def = ''
  func_input = []
  for idx, var_ in enumerate(var):
    input_def += 'input[{idx}] = {var_};\n'.format(idx=idx, var_=var_)
    func_input.append('float {var_}'.format(var_=var_))
    mean_array.append(preprocessor[var_].mean_[0])
    std_array.append(preprocessor[var_].scale_[0])

  mean_array = ['{}'.format(x) for x in mean_array]
  std_array  = ['{}'.format(x) for x in std_array]
  mean_array = '{' + ', '.join(mean_array) + '}'
  std_array  = '{' + ', '.join(std_array)  + '}'

  func_def = 'vector<float> {}({})'.format(DNN_Label, ','.join(func_input))

  Ensemble_Model_command = 'float score = 0;\n'
  TMVA_IMPORT = ''
  for fold in test_loss:
    TMVA_IMPORT += 'TMVA_SOFIE_{DNN_Label}_fold{fold}::Session model{fold}("../../data/{DNN_dir}/{DNN_Label}_fold{fold}.dat");\n'.format(fold=fold, DNN_Label=DNN_Label,DNN_dir=DNN_dir)
    Ensemble_Model_command += '\
      score += model{fold}.infer(input)[0] * {weight};\n\
    '.format(fold = fold, weight = weight[fold])

  command = '\
  #include "ROOT/RDataFrame.hxx"\n\
  {TMVA_IMPORT}\n\
  {func_def} {{ \n\
    vector<float> out;\n\
    float Preprocessor_mean[{nvar}] = {mean_array};\n\
    float Preprocessor_std[{nvar}]  = {std_array};\n\
    float input[{nvar}]; \n\
    {input_def}; \n\
    for(int input_idx=0; input_idx < {nvar}; input_idx++){{\n\
      input[input_idx] = (input[input_idx]-Preprocessor_mean[input_idx])/Preprocessor_std[input_idx];\n\
    }}\n\
    {Ensemble_Model_command}\n\
    out.push_back(1.0/(1.0 + std::exp(-1.0*score)));\n\
    return out;\n\
  }}\
  '.format(func_def=func_def, nvar=len(var), mean_array=mean_array, std_array=std_array, input_def=input_def, Ensemble_Model_command = Ensemble_Model_command, TMVA_IMPORT=TMVA_IMPORT)


  print(command)
  ROOT.gInterpreter.Declare(str(command))


