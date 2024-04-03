from sklearn.metrics import accuracy_score, roc_curve, auc, RocCurveDisplay
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn import metrics

def ROC_kfold(Y_true, Y_pred, W, foutput):
  tprs = []
  aucs = []
  mean_fpr = np.linspace(0, 1, 100)

  fig, ax = plt.subplots(figsize = (6,6))
  for kfold in range(len(Y_true)):
    fpr, tpr, thresholds = metrics.roc_curve(Y_true[kfold], Y_pred[kfold], pos_label=1, sample_weight=W[kfold])
    roc_auc = metrics.auc(fpr, tpr)
    viz = RocCurveDisplay(
          fpr = fpr,
          tpr = tpr,
          roc_auc = roc_auc,
        )
    viz.plot(
          name = "ROC fold {}".format(kfold),
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
  plt.savefig(foutput)
  return mean_auc
