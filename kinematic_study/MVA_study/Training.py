import uproot
from xgboost import XGBClassifier
import xgboost as xgb
from sklearn.model_selection import train_test_split, GridSearchCV, StratifiedKFold
from sklearn.metrics import accuracy_score, roc_curve, auc, RocCurveDisplay
import numpy as np
import pandas as pd
from xgboost import cv
import matplotlib.pyplot as plt
from sklearn import metrics
import ROOT
import os, sys
import json
import optparse, argparse
sys.path.insert(1, '../../python')
from common import *


def GridSearch_xgb(init_params, param_grid, X, Y, W, scoring = 'roc_auc', n_jobs=-1, cv = 5, std_threshold = 0.01):

    if len(param_grid) == 1:
        for key in param_grid:
            if (len(param_grid[key]) == 1):
                print(param_grid)
                init_params[key] = param_grid[key][0]
                return init_params
    print(param_grid)
    gsearch = GridSearchCV(estimator = XGBClassifier(**init_params), param_grid = param_grid, scoring = scoring, n_jobs = n_jobs, cv = cv)
    gsearch.fit(X, Y, sample_weight = W)
    params_list = gsearch.cv_results_["params"]
    rank_test_score = gsearch.cv_results_["rank_test_score"]
    mean_test_score = gsearch.cv_results_["mean_test_score"]
    std_test_score  = gsearch.cv_results_["std_test_score"]
    rank_test_score_index = np.argsort(rank_test_score)
    
    for idx in rank_test_score_index:
        # if ((std_test_score[idx] / mean_test_score[idx]) > std_threshold): continue 
        for param in params_list[idx]:
            init_params[param] = params_list[idx][param]
        return init_params



    return init_params


def load_data(file_list, var, label):

  return_pd = None
  for file_ in file_list:
    event = uproot.open("{}:Events".format(file_))
    features = event.arrays(var, "weight_n_Norm>0", library='pd')
    features.insert(0, "Label", (np.ones(features.shape[0])*label).astype(int), True)
    if return_pd is None:
      return_pd = features
    else:
      return_pd = pd.concat([return_pd, features], ignore_index=True)
    del event
    del features
  return_pd['weight_n_Norm'] = return_pd['weight_n_Norm']/(return_pd['weight_n_Norm'].sum(axis=0))*1000 # totl weight sum to be 1000
  return return_pd


def Evaulate(model, file_list, var, label, bkg_pred, bkg_weight):
    data = load_data(file_list, var, 1)
    X = data.drop(['Label', 'weight_n_Norm'], axis=1)
    Y = data['Label']
    W = (data['weight_n_Norm']).to_numpy()

    Y_pred = model.predict_proba(X)[:,1] # discrete number
    Y_pred = np.concatenate([Y_pred, bkg_pred])
    bkg_true = np.zeros_like(bkg_pred)
    Y_true = np.concatenate([Y, bkg_true])
    W_total = np.concatenate([W, bkg_weight])

    fpr, tpr, thresholds = metrics.roc_curve(Y_true, Y_pred, pos_label=1, sample_weight=W_total)
    roc_auc = metrics.auc(fpr, tpr)
    return roc_auc

def Training(signal_list, bkg_list, var, Hyperparameter_Tuning, outdir, valid_signal_dict):

  ##############
  ##  Sample  ##
  ##############

  var.append('weight_n_Norm')

  print('signal', signal_list)
  print('background', bkg_list)

  signal = load_data(signal_list, var, 1)
  background = load_data(bkg_list, var, 0)


  ################
  ##  DataFrame ##
  ################

  df = pd.concat([signal, background], ignore_index=True)  
  df_train, df_test = train_test_split(df, test_size=0.5, train_size=0.1, shuffle=True)
  del df
  del df_test
  df_train = df_train.reset_index(drop=True)
  X = (df_train.drop(['Label', 'weight_n_Norm'], axis=1))
  Y = (df_train['Label'])
  W = (df_train['weight_n_Norm'])
#  X_test  = df_test.drop('Label', axis=1)
#  Y_test = df_test['Label']


  params = {
                   'objective':'binary:logistic',
                   'max_depth': 4,
                   'min_child_weight': 1,
                   'gamma': 0,
                   'subsample': 0.8,
                   'colsample_bytree': 0.8,
                   'scale_pos_weight': 1,
                   'alpha': 10,
                   'learning_rate': 0.1,
                   'n_estimators':100
             }


  #############################
  ##  Hyperparameter Tuning  ##
  #############################

  if Hyperparameter_Tuning:  # No parameter assigned, perform hyperparameter scan ...

    # Hyperparameter tuning reference: https://www.analyticsvidhya.com/blog/2016/03/complete-guide-parameter-tuning-xgboost-with-codes-python/
    grid_schedule = [{'learning_rate': [0.1]},
                     {'n_estimators': range(100, 400, 50)}, 
                     {'max_depth': range(3,10,1), 'min_child_weight': range(1,6,1)},
                     {'gamma': [i/10.0 for i in range(5)]}, 
                     {'subsample': [0.6, 0.7, 0.8, 0.9], 'colsample_bytree':[0.6, 0.7, 0.8, 0.9]},
                     {'reg_alpha':[1e-5, 1e-3, 5e-3, 1e-2, 5e-2, 0.1, 0.5,  1, 5, 10, 50, 100]}, 
                     {'learning_rate': [0.02]},
                     {'n_estimators': [500 + 500*i for i in range(0,10)]}]
    for param_grid_ in grid_schedule:
      params = GridSearch_xgb(init_params = params, X = X, Y = Y, W = W, param_grid = param_grid_, scoring = 'roc_auc', n_jobs = -1, cv = 5)

  with open(os.path.join(outdir, 'params.json'), 'w') as outfile:
    json.dump(params, outfile, indent=4)


  ######################################
  ##  Training (w k-fold validation)  ##
  ######################################

  # ROC Curve with cross validation. Reference: https://scikit-learn.org/stable/auto_examples/model_selection/plot_roc_crossval.html#sphx-glr-auto-examples-model-selection-plot-roc-crossval-py
  n_splits = 5
  cv = StratifiedKFold(n_splits=n_splits)

  tprs = []
  aucs = []
  mean_fpr = np.linspace(0, 1, 100)

  fig, ax = plt.subplots(figsize = (6,6))
  for fold, (train, test) in enumerate(cv.split(X, Y)):

    classifier = XGBClassifier(**params)
    classifier.fit(X.iloc[train], Y.iloc[train], sample_weight=W.iloc[train])

    fpr, tpr, thresholds = metrics.roc_curve(Y.iloc[test].to_numpy(), classifier.predict_proba(X.iloc[test])[:,1], pos_label=1, sample_weight=(W.iloc[test]).to_numpy())
    roc_auc = metrics.auc(fpr, tpr)
    viz = RocCurveDisplay(
          fpr = fpr,
          tpr = tpr,
          roc_auc = roc_auc,
        )
    viz.plot(          
          name = "ROC fold {}".format(fold),
          alpha = 0.3,
          lw    = 1,
          ax    = ax,
#          plot_channel_level = (fold == n_splits - 1)
          )
    interp_tpr = np.interp(mean_fpr, fpr, tpr)
    interp_tpr[0] = 0.0
    tprs.append(interp_tpr)
    aucs.append(viz.roc_auc)

  mean_tpr = np.mean(tprs, axis=0)
  mean_tpr[-1] = 1.0
  mean_auc = auc(mean_fpr, mean_tpr)
  std_auc = np.std(aucs)

  ax.plot(
    mean_fpr,
    mean_tpr,
    color = "b",
    label = "Mean ROC (AUC = %0.3f $\pm$ %0.3f)"%(mean_auc, std_auc),
    lw = 2,
    alpha = 0.8
  )

  std_tpr = np.std(tprs, axis=0)

  tprs_upper = np.minimum(mean_tpr + std_tpr, 1)
  tprs_lower = np.maximum(mean_tpr - std_tpr, 0)
  ax.fill_between(
    mean_fpr,
    tprs_lower,
    tprs_upper,
    color="grey",
    alpha=0.2,
    label=r"$\pm$ 1 std. dev.",
  )

  ax.set(
    xlabel="False Positive Rate (background efficiency)",
    ylabel="True Positive Rate (sigal efficiency)",
    title=f"Mean ROC curve with variability\n(Positive label: signal)",
  )
  ax.legend(loc="lower right")
  plt.show()
  plt.savefig(os.path.join(outdir, "ROC.png"))


  #############################
  ##  Final Model Treatment  ##
  #############################
  xgb_clf = classifier # Use the last one of the trained models from k-fold validation
  X_train = X.iloc[train]
  Y_train = Y.iloc[train]
  W_train = (W.iloc[train]).to_numpy()
  X_test  = X.iloc[test]
  Y_test  = Y.iloc[test]
  W_test  = (W.iloc[test]).to_numpy()

  ###########################
  ##  Variable Importance  ##
  ###########################

  feature_important = xgb_clf.get_booster().get_score(importance_type='weight')
  keys = list(feature_important.keys())
  values = list(feature_important.values())

  data = pd.DataFrame(data=values, index=keys, columns=["score"]).sort_values(by = "score", ascending=False)
  print(data)
  data.nlargest(40, columns="score").plot(kind='barh', figsize = (20,10)) ## plot top 40 features
  plt.xlabel("score")
  plt.ylabel("feature")
  plt.title("Variable Importance")
  plt.savefig(os.path.join(outdir, "Variable_Importance.png"))

  #######################
  ##  BDT distribution ##
  #######################

  pred_train = xgb_clf.predict_proba(X_train)[:,1]
  pred_test  = xgb_clf.predict_proba(X_test)[:,1]

  background_pred_train = pred_train[Y_train == 0]
  background_weight_train = W_train[Y_train == 0]

  background_pred_test  = pred_test[Y_test == 0]
  background_weight_test = W_test[Y_test == 0]

  signal_pred_train     = pred_train[Y_train==1]
  signal_weight_train = W_train[Y_train==1]

  signal_pred_test      = pred_test[Y_test==1]
  signal_weight_test = W_test[Y_test==1]

  fig, ax = plt.subplots(figsize = (9,6))
  binning = np.linspace(0, 1, 20)
  h_train_bkg = ax.hist(background_pred_train, binning, color = 'r', alpha = 0.5, label = 'bkg (Train)', weights=background_weight_train,density=True)
  h_train_sig = ax.hist(signal_pred_train, binning, color = 'b', alpha=0.5, label = 'sig (Train)', weights=signal_weight_train, density = True)
  bkg,bins = np.histogram(background_pred_test, binning, weights=background_weight_test, density=True)
  sig,bins = np.histogram(signal_pred_test, binning, weights=signal_weight_test, density=True)

  ax.scatter(bins[:-1]+ 0.5*(bins[1:] - bins[:-1]), bkg, marker='o', c='red', s=40, alpha=1, label = 'bkg (Test)')
  ax.scatter(bins[:-1]+ 0.5*(bins[1:] - bins[:-1]), sig, marker='o', c='blue', s=40, alpha=1, label = 'sig (Test)')
  ax.legend()
  plt.title("Distribution")
  plt.xlabel("BDT score")
  plt.ylabel("Density")

  plt.savefig(os.path.join(outdir, 'BDT_distribution.png'))


  ##################################
  ##  Valid in all signal sample  ##
  ##################################

  AUC_across_signal = dict()
  for validation_signal_ in valid_signal_dict:
      if (valid_signal_dict[validation_signal_][0] in signal_list):
          AUC_across_signal[validation_signal_] = aucs[-1] # To be consistent with current model
      else:
          AUC_across_signal[validation_signal_] = Evaulate(xgb_clf, valid_signal_dict[validation_signal_], var, 1, background_pred_test, background_weight_test)
  with open(os.path.join(outdir, 'AUC_accross_signal.json'), 'w') as outfile:
    json.dump(AUC_across_signal, outfile, indent=4)

  ##################
  ##  Save Model  ##
  ##################
  
#  xgb_clf.save_model(os.path.join(outdir, 'XGB.json'))
  xgb_clf.get_booster().feature_names = ['f{}'.format(idx) for idx in range(len(xgb_clf.get_booster().feature_names))]
  ROOT.TMVA.Experimental.SaveXGBoost(xgb_clf, "XGB", os.path.join(outdir, "XGB.root"))


if __name__ == "__main__":
  usage = 'usage: %prog [options]'
  parser =  argparse.ArgumentParser(description=usage)
  parser.add_argument('-e', '--era', dest='era', help='[2016apv/2016postapv/2017/2018]', default=['2017'], type=str, nargs='+')
  parser.add_argument('--region', type = str, nargs='+')
  parser.add_argument('--channel', type = str, nargs='+')
  parser.add_argument('--hyperparameter_tuning', action = 'store_true')
  parser.add_argument('--indir', type = str)
  parser.add_argument('--outdir', type = str, default = './')
  parser.add_argument('--signal', type = str, nargs='+', default=['CGToBHpm_a_500_rtt06_rtc04'])
  parser.add_argument('--sample_json', type=str, default="../../data/sample.json")
  parser.add_argument('--MVA_json', type=str, default="../../data/MVA.json")
  parser.add_argument('--postfix', type = str, default = 'CGToBHpm_a_500_rtt06_rtc04')
  args = parser.parse_args()
  if 'all' in args.era:
      args.era = ['2016apv', '2016postapv', '2017', '2018']

  Sig_file_list = []
  valid_signal_dict = dict()
  Bkg_file_list = []
  for era in args.era:
    for region in args.region:
      for channel in args.channel:
        dir_ = os.path.join(args.indir, era, region, channel)
        Bkg_list = Get_Sample(args.sample_json, ["MC", "Background"], era, withTail = False)
        Bkg_file_list += [os.path.join(dir_, '{}.root'.format(sample)) for sample in Bkg_list]
        for sig in args.signal:
          Sig_file_list.append(os.path.join(dir_, '{}.root'.format(sig)))
        Sig_list = Get_Sample(args.sample_json, ["MC", "Signal"], era, withTail = False)
        for sig_ in Sig_list:
            file_ = os.path.join(dir_, '{}.root'.format(sig_))
            if sig_ not in valid_signal_dict:
                valid_signal_dict[sig_] = [file_]
            else:
                valid_signal_dict[sig_].append(file_)
  args.outdir = os.path.join(args.outdir, args.postfix)

  MVA_json = read_json(args.MVA_json)
  var = MVA_json['xgboost']

  if not os.path.exists(args.outdir):
      os.system("mkdir -p {}".format(args.outdir))
  print("postfix: ", args.postfix)
  Training(signal_list=Sig_file_list, bkg_list=Bkg_file_list, var = var, Hyperparameter_Tuning=args.hyperparameter_tuning, outdir = args.outdir, valid_signal_dict = valid_signal_dict)
