from sklearn.metrics import accuracy_score, roc_curve, auc, RocCurveDisplay
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn import metrics

def ROC_kfold(Y_true, Y_pred, W, foutput, nClass = 1):
  tprs = []
  aucs = []
  mean_fpr = np.linspace(0, 1, 100)

  color_idx = ["b", "r", "g"]
  fig, ax = plt.subplots(figsize = (6,6))
  for class_idx in range(1, nClass+1):
    for kfold in range(len(Y_true)):
      selection = np.logical_or((Y_true[kfold] == 0), (Y_true[kfold] == class_idx))
      if Y_pred[kfold].ndim >= 2:
      # Calculate Y_pred_score if there is a second dimension
        Y_pred_score = Y_pred[kfold][:, class_idx] / (Y_pred[kfold][:, 0] + Y_pred[kfold][:, class_idx])
      else:
       # Handle the case where there is no second dimension
        Y_pred_score = Y_pred[kfold]
      fpr, tpr, thresholds = metrics.roc_curve(Y_true[kfold][selection], Y_pred_score[selection], pos_label=class_idx, sample_weight=W[kfold][selection])
      roc_auc = metrics.auc(fpr, tpr)
      viz = RocCurveDisplay(
            fpr = fpr,
            tpr = tpr,
            roc_auc = roc_auc,
          )
      viz.plot(
            name = "ROC fold {} (pos: {})".format(kfold, class_idx),
            alpha = 0.3,
            lw    = 1,
            ax    = ax,
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
      color = color_idx[class_idx-1],
      label = "Mean ROC (AUC = %0.3f $\pm$ %0.3f) (pos: %s)"%(mean_auc, std_auc, class_idx),
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
  plt.savefig(foutput)
  return mean_auc

def ROC_kfold_from_train_result(train_result, foutput):
  tprs = []
  aucs = []
  mean_fpr = np.linspace(0, 1, 100)

  class_idx = 1
  color_idx = ["b", "r", "g"]
  fig, ax = plt.subplots(figsize = (6,6))
  for kfold in range(len(train_result)):
      fpr = train_result[kfold]['ROC_fpr']
      tpr = train_result[kfold]['ROC_tpr']
      roc_auc = metrics.auc(fpr, tpr)
      viz = RocCurveDisplay(
            fpr = fpr,
            tpr = tpr,
            roc_auc = roc_auc,
          )
      viz.plot(
            name = "ROC fold {} (pos: {})".format(kfold, class_idx),
            alpha = 0.3,
            lw    = 1,
            ax    = ax,
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
      color = color_idx[class_idx-1],
      label = "Mean ROC (AUC = %0.3f $\pm$ %0.3f) (pos: %s)"%(mean_auc, std_auc, class_idx),
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
  plt.savefig(foutput)
  return mean_auc

