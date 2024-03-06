import sys
import os, time, argparse, torch, shap, fnmatch
from torch import nn
from torch.utils.data import DataLoader, Dataset, SubsetRandomSampler, random_split
from sklearn.model_selection import train_test_split, KFold
from tqdm import tqdm
sys.path.append('../../python')
from common import *
from MVA_helper import *
import pandas as pd
import matplotlib.pyplot as plt
import json
import random
import tempfile
import ray
from ray import train, tune
from ray.train import Checkpoint
from ray.tune.schedulers import ASHAScheduler

class custom_dataset(Dataset):
  def __init__(self, df, input_columns, target_columns, weight_columns, device):
    self.df = df
    source_combs = self.df[input_columns].values
    target_combs = self.df[target_columns].values
    weight_combs = self.df[weight_columns].values
    self.x_train = torch.tensor(source_combs, dtype = torch.float32, device=device)
    self.y_train = torch.tensor(target_combs, dtype = torch.float32, device=device)
    self.w_train = torch.tensor(weight_combs, dtype = torch.float32, device=device)

  def __len__(self):
    return len(self.df)

  def __getitem__(self, index):
    x_ = self.x_train[index]
    y_ = self.y_train[index]
    w_ = self.w_train[index]
    return x_, y_, w_


class DNN(nn.Module):
  def __init__(self, nvars, l1=48, l2=24, dropout=0.0):
    super().__init__()
    self.linear_relu_stack = nn.Sequential(
      nn.Linear(nvars, l1),
      nn.ReLU(),
      nn.Dropout(p=dropout),
      nn.Linear(l1, l2),
      nn.ReLU(),
      nn.Dropout(p=dropout),
      nn.Linear(l2, 1),
    )
  def forward(self, x):
    logits = self.linear_relu_stack(x)
    return logits


def reset_weights(m):
  '''
    Try resetting model weights to avoid
    weight leakage.
  '''
  for layer in m.children():
   if hasattr(layer, 'reset_parameters'):
    print(f'Reset trainable parameters of layer = {layer}')
    layer.reset_parameters()
  return m

def Train_loop(dataloader, model, loss_fn, optimizer):
  size = len(dataloader.dataset)
  batch_loss = 0.0
  x_in = None
  y_true = np.array([])
  y_pred = np.array([])
  weight = np.array([])

  for batch, (x,y,w) in enumerate(dataloader):
    optimizer.zero_grad()
    y = y.unsqueeze(1)
    logits = model(x)
    loss = loss_fn(logits, y) * w
    loss = torch.sum(loss)
    loss.backward()
    optimizer.step()
    batch_loss += loss.item()
    x_in   = x if x_in is None else torch.cat([x_in, x])
    y_true = np.append(y_true, y.detach().cpu().numpy())
    y_pred = np.append(y_pred, torch.sigmoid(logits).detach().cpu().numpy())
    weight = np.append(weight, w.detach().cpu().numpy())
  return batch_loss, model, y_true, y_pred, weight

def Test_loop(dataloader, model, loss_fn):
  size = len(dataloader.dataset)
  batch_loss = 0.0
  x_in = None
  y_true = np.array([])
  y_pred = np.array([])
  weight = np.array([])
  with torch.no_grad():
    for batch, (x,y,w) in enumerate(dataloader):
      y = y.unsqueeze(1)
      logits = model(x)
      loss = loss_fn(logits, y) * w
      loss = torch.sum(loss)
      batch_loss += loss.item()
      x_in   = x if x_in is None else torch.cat([x_in, x])
      y_true = np.append(y_true, y.detach().cpu().numpy())
      y_pred = np.append(y_pred, torch.sigmoid(logits).detach().cpu().numpy())
      weight = np.append(weight, w.detach().cpu().numpy())
  return batch_loss, y_true, y_pred, weight, x_in


def Evaluate(model, df, var, signal_mass, loss_function, device, pNN, test_id_ = None):
  signal_mass.append(-1)
  df,_ = train_test_split(df, test_size=0.5, shuffle=False)
  df = df[df['Mass'].isin(signal_mass)]
  if pNN:
    # assign mass variable to background
    Mass_transformed_pool = df[df['Mass']>-1]['Mass_transformed'].value_counts()
    elements = Mass_transformed_pool.index.tolist()
    counts   = Mass_transformed_pool.tolist()
    df.loc[(df['Mass'] == -1), 'Mass_transformed'] = random.choices(elements, counts, k=len(df[df['Mass'] == -1]))
  bkg_weight_sum = df[df['Label']==0]['class_weight'].sum()
  sig_weight_sum = df[df['Label']==1]['class_weight'].sum()
  df.loc[(df['Label']==1), 'class_weight'] = df.loc[df['Label']==1, 'class_weight'] * bkg_weight_sum / sig_weight_sum
  dataset = custom_dataset(df, var, 'Label', 'class_weight', device)
  data_loader = DataLoader(dataset, batch_size=1024, shuffle=False)
  loss_test_, y_true_, y_pred_, weight_, x_tmp    = Test_loop(data_loader, model, loss_function)
  fpr, tpr, thresholds = metrics.roc_curve(y_true_, y_pred_, pos_label=1, sample_weight=weight_)
  roc_auc = metrics.auc(fpr, tpr)
  return roc_auc


def Simple_Training(config, data):
  
  # Simple training function used for hyperparameter tuning.

  # config contains following keys: var, l1, l2, lr, df_train, batch_size, weight_decay
  var = config["var"]
  model = DNN(len(var), config["l1"], config['l2'], config['dropout'])
  device = 'cuda' if torch.cuda.is_available() else 'cpu'
  model.to(device)

  loss_function = nn.BCEWithLogitsLoss(reduction='none')
  optimizer     = torch.optim.NAdam(model.parameters(), lr=config['lr'], weight_decay=config['weight_decay'])
  train_df      = data

  if train.get_checkpoint():
    loaded_checkpoint = train.getcheckpoint()
    with loaded_checkpoint.as_directory() as loaded_checkpoint_dir:
      model_state, optimizer_state = torch.load(
        os.path.join(loaded_checkpoint_dir, "checkpoint.pt")
        )
      model.load_state_dict(model_state)
      optimizer.load_state_dict(optimizer_state)

  train_subset, test_subset = train_test_split(train_df, test_size=0.2, shuffle=True)
  train_dataset_ = custom_dataset(train_subset, var, 'Label', 'class_weight', device)
  test_dataset_  = custom_dataset(test_subset,  var, 'Label', 'class_weight', device)
  training_data_loader_ = DataLoader(train_dataset_, batch_size=config['batch_size'], shuffle=True)
  test_data_loader_     = DataLoader(test_dataset_,  batch_size=config['batch_size'], shuffle=False)
  
  for epoch in range(10):
    loss_, model, y_true_train, y_pred_train, weight_train = Train_loop(training_data_loader_, model, loss_function, optimizer)
    loss_test_, y_true_, y_pred_, weight_, x_tmp    = Test_loop(test_data_loader_, model, loss_function)
    av_training_loss = loss_/len(training_data_loader_.sampler)
    av_testing_loss  = loss_test_/len(test_data_loader_.sampler)

    with tempfile.TemporaryDirectory() as temp_checkpoint_dir:
      path = os.path.join(temp_checkpoint_dir, "checkpoint.pt")
      torch.save(
          (model.state_dict(), optimizer.state_dict()), path
      )
      checkpoint = Checkpoint.from_directory(temp_checkpoint_dir)
      train.report(
          {"loss": av_testing_loss / config['batch_size']},
            checkpoint=checkpoint,
      )
  print("Finished Training")

def Training(indir, MVA_json, n_epoch, batch_size, signal_mass=[500], learning_rate=1e-3, k_folds=5, outdir='./', pNN=False, hyperparameter_tuning=False, ray_silence=False):
   
  # More dedicated training function that perform in k-fold way with full setting.



  ##############
  ##  Device  ##
  ##############

  device = 'cuda' if torch.cuda.is_available() else 'cpu'
  print('cuda is available: ', torch.cuda.is_available())
  os.system('nvidia-smi')

  #########################
  ##  Basic Information  ##
  #########################

  print('torch version: ', torch.__version__)
  print('Running on device: ', device)
  if torch.cuda.is_available():
    print('Cuda used to build pyTorch: ', torch.version.cuda)
    print('Current device: ', torch.cuda.current_device())
    print('Cuda arch list: ', torch.cuda.get_arch_list())

  ######################
  ##  File Name List  ##
  ######################

  file_list = []
  for filename in os.listdir(indir):
    if fnmatch.fnmatch(filename, 'training_data_*_scaled.h5'):
      file_list.append(os.path.join(indir, filename))

  print(file_list)

  #############
  ##  Model  ##
  #############

  MVA_json = read_json(MVA_json)
  var = MVA_json['xgboost']
  if pNN:
    var.append('Mass_transformed')
  model = DNN(len(var)).to(device)
  print(model)

  loss_function = nn.BCEWithLogitsLoss(reduction='none')
  optimizer     = torch.optim.NAdam(model.parameters(), lr=learning_rate)

  ###############
  ##  Dataset  ##
  ###############

  df = None
  for file_ in file_list:
    df_ = pd.read_hdf(file_, 'df')
    if df is None:
      df = df_
    else:
      df = pd.concat([df, df_], ignore_index=True)

  signal_mass.append(-1)


  train_df_raw, val_df = train_test_split(df, test_size=0.5, shuffle=True)
  train_df = train_df_raw[train_df_raw['Mass'].isin(signal_mass)]

  
  if pNN:
    # assign mass variable to background
    Mass_transformed_pool = train_df[train_df['Mass']>-1]['Mass_transformed'].value_counts()
    elements = Mass_transformed_pool.index.tolist()
    counts   = Mass_transformed_pool.tolist()
    print(Mass_transformed_pool)
    train_df.loc[(train_df['Mass'] == -1), 'Mass_transformed'] = random.choices(elements, k=len(train_df[train_df['Mass'] == -1])) # Each mass hypothesis has been normalized to 1 by weight, so when assigning Mass feature to background, each mass hypothesis should have the same ratio.
  bkg_weight_sum = train_df[train_df['Label']==0]['class_weight'].sum()
  sig_weight_sum = train_df[train_df['Label']==1]['class_weight'].sum()
  train_df.loc[(train_df['Label']==1), 'class_weight'] = train_df.loc[train_df['Label']==1, 'class_weight'] * bkg_weight_sum / sig_weight_sum



  #train_dataset = custom_dataset(train_df, var, 'Label', 'class_weight', device)
  #test_dataset  = custom_dataset(test_df,  var, 'Label', 'class_weight', device)

  #training_data_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
  #test_data_loader     = DataLoader(test_dataset,  batch_size=batch_size, shuffle=False)

  #train_features, train_labels, train_weight = next(iter(training_data_loader))
  #print("Features batch shapes: ", train_features.size())
  #print("Labels batch shapes: ", train_labels.size())


  best_config = {"l1":48, 'l2':24, 'weight_decay': 0.0, 'lr':learning_rate, 'batch_size':batch_size, 'dropout':0.0}


  if hyperparameter_tuning:
    print('hyperparameter', sys.path)
    os.environ['RAY_memory_monitor_refresh_ms'] = '0'

    if ray_silence:
      import logging
      def logging_setup_func():
        logger = logging.getLogger("ray")
        logger.setLevel(logging.WARNING)
        #warnings.simplefilter("always")

      ray.init(runtime_env={"worker_process_setup_hook": logging_setup_func})
      logging_setup_func() 
      verbose = 0
    else:
      ray.init(_temp_dir='/tmp/tihsu/')
      verbose = 1
    config = {
      'l1': tune.sample_from(lambda _: 2**np.random.randint(2,8)),
      'l2': tune.sample_from(lambda _: 2**np.random.randint(1,7)),
      'dropout': tune.uniform(0.0, 0.25),
      'weight_decay': tune.loguniform(1e-6, 1e-1),
      'lr': tune.loguniform(1e-4, 1e-1),
      'batch_size': tune.choice([128, 256, 512, 1024]),
      'var': var,
    }
#    os.system('ray status')
    scheduler = ASHAScheduler(
        max_t=10,
        grace_period=1,
        reduction_factor=4)

    tuner = tune.Tuner(
        tune.with_resources(
            tune.with_parameters(Simple_Training, data=train_df[:int(len(train_df)/10)]),
            resources={"cpu": 2}
        ),
        tune_config=tune.TuneConfig(
            metric="loss",
            mode="min",
            scheduler=scheduler,
            num_samples=90,
        ),
        run_config = train.RunConfig(storage_path='/tmp/tihsu/ray_results/',local_dir='/tmp/tihsu/ray_results', verbose=verbose),
        param_space=config,
    )

    results = tuner.fit()
    best_result = results.get_best_result("loss", "min")
    best_config = best_result.config
    print("Best trial config: {}".format(best_result.config))
    print("Best trial final validation loss: {}".format(best_result.metrics["loss"]))
  


  #############
  ##  Model  ##
  #############

  model = DNN(len(var), best_config['l1'], best_config['l2'], best_config['dropout']).to(device)
  print(model)

  loss_function = nn.BCEWithLogitsLoss(reduction='none')
  optimizer     = torch.optim.NAdam(model.parameters(), lr=best_config['lr'], weight_decay=best_config['weight_decay'])


  with open(os.path.join(outdir, 'param.json'), 'w') as outfile:
    json.dump(best_config, outfile, indent=4)
  ################
  ##  Training  ##
  ################

  kfold = KFold(n_splits=k_folds, shuffle=True)
  train_losses = []
  test_losses  = []
  Y_true       = []
  Y_pred       = []
  W            = []

  fig, ax = plt.subplots(figsize=(8,8))
  ax.set_ylabel('Loss')
  ax.set_xlabel('Epoch')
  ax.set_yscale('log')

  marker_list = ['.', 's', 'v', '^', 'p', '>']
  for fold, (train_id_, test_id_) in enumerate(kfold.split(train_df)):
    model = DNN(len(var), best_config['l1'], best_config['l2'], best_config['dropout'])
    model.to(device)
    optimizer     = torch.optim.NAdam(model.parameters(), lr=learning_rate)
    train_df_ = train_df.iloc[train_id_]
    test_df_  = train_df.iloc[test_id_]
    train_dataset_ = custom_dataset(train_df_, var, 'Label', 'class_weight', device)
    test_dataset_  = custom_dataset(test_df_,  var, 'Label', 'class_weight', device)
    training_data_loader_ = DataLoader(train_dataset_, batch_size=best_config['batch_size'], shuffle=True)
    test_data_loader_     = DataLoader(test_dataset_,  batch_size=best_config['batch_size'], shuffle=False)

    train_losses.append([])
    test_losses.append([])
    Y_true.append([])
    Y_pred.append([])
    W.append([])
    iters = 0
    for epoch in tqdm(range(n_epoch)):
      loss_, model, y_true_train, y_pred_train, weight_train = Train_loop(training_data_loader_, model, loss_function, optimizer)
      loss_test_, y_true_, y_pred_, weight_, x_tmp    = Test_loop(test_data_loader_, model, loss_function)
      av_training_loss = loss_/len(training_data_loader_.sampler)
      av_testing_loss  = loss_test_/len(test_data_loader_.sampler)
      train_losses[fold].append(av_training_loss)
      test_losses[fold].append(av_testing_loss)

    Y_true[fold] = y_true_
    Y_pred[fold] = y_pred_
    W[fold] = weight_

    ax.plot(train_losses[fold], c='blue', alpha=0.5, label='train(fold {})'.format(fold), marker = marker_list[fold])
    ax.plot(test_losses[fold],  c='orange', alpha=0.5, label='test(fold {})'.format(fold), marker = marker_list[fold])
    ax.legend(loc="upper right")
  fig.savefig(os.path.join(outdir, 'loss_vs_epoch.png'))
  torch.save(model, os.path.join(outdir, 'model.pt'))
  mean_auc = ROC_kfold(Y_true, Y_pred, W, os.path.join(outdir, 'ROC.png'))
  
  ###########################
  ##  Variable Importance  ##
  ###########################

  plt.clf()
  shapX_ = x_tmp[:1000]
  dexplainer = shap.DeepExplainer(model, shapX_)
  dex_shap_values_ = dexplainer.shap_values(shapX_)
  shap.summary_plot(dex_shap_values_, shapX_.detach().cpu().numpy(), var)
  plt.savefig(os.path.join(outdir,'shap_vals.png'))

  ####################
  ##  Distribution  ##
  ####################


  background_pred_train = y_pred_train[y_true_train == 0]
  background_weight_train = weight_train[y_true_train == 0]

  background_pred_test  = y_pred_[y_true_ == 0]
  background_weight_test = weight_[y_true_ == 0]

  signal_pred_train     = y_pred_train[y_true_train == 1]
  signal_weight_train = weight_train[y_true_train == 1]

  signal_pred_test      = y_pred_[y_true_==1]
  signal_weight_test = weight_[y_true_==1]

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
  plt.xlabel("DNN score")
  plt.ylabel("Density")

  plt.savefig(os.path.join(outdir, 'Distribution.png'))

  ##################################
  ##  Valid in all signal sample  ##
  ##################################

  AUC_across_signal = dict()
  all_mass = [200, 300, 350, 400, 500, 600, 700, 800, 900, 1000]
  for mass_ in all_mass:
    if mass_ in signal_mass and len(signal_mass)==2: 
      AUC_across_signal[mass_] = mean_auc # To be consistent with current model
    else:
      AUC_across_signal[mass_] = Evaluate(model, val_df, var, [mass_], loss_function, device, pNN)
  with open(os.path.join(outdir, 'AUC_accross_signal.json'), 'w') as outfile:
    json.dump(AUC_across_signal, outfile, indent=4)

if __name__ == '__main__':
  usage = 'usage: %prog [options]'
  parser =  argparse.ArgumentParser(description=usage)
  parser.add_argument('--MVA_json', type=str, default="../../data/MVA.json")
  parser.add_argument('--indir', type=str, default='./')
  parser.add_argument('--outdir', type=str, default='./')
  parser.add_argument('--n_epoch', type=int, default=300)
  parser.add_argument('--batch_size', type=int, default=128)
  parser.add_argument('--k_folds', type=int, default=3)
  parser.add_argument('--Masses', type=int, nargs='+', default=[500])
  parser.add_argument('--pNN', action='store_true')
  parser.add_argument('--hyperparameter_tuning', action='store_true')
  parser.add_argument('--ray_silence', action='store_true')
  args = parser.parse_args()
  if not os.path.exists(args.outdir):
    os.system('mkdir -p {}'.format(args.outdir))
  Training(args.indir, args.MVA_json, args.n_epoch, args.batch_size, signal_mass=args.Masses, k_folds=args.k_folds, outdir=args.outdir, pNN=args.pNN, hyperparameter_tuning=args.hyperparameter_tuning, ray_silence=args.ray_silence)
