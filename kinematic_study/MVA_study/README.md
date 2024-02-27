# Produce MVA input file
To produce the MVA input file, you need to run
```
cd ../produce_root_file
python runcondor.py --Labels BDT_training --outdir [MVA_INPUT_DIR] [Other option like era...]
```
Then to train MVA file
```
[Under this directory]
python runcondor.py --indir [MVA_INPUT_DIR] --outdir [MVA_WEIGHT_DIR]
```
For the XGboost training code, you can also run it without `runcondor.py` wrap
```
python Training_xgboost.py --indir [MVA_INPUT_DIR] --outdir [MVA_WEIGHT_DIR] --signal [SIGNAL_NAME] [--hyperparameter_tuning] --era [ERA_LIST] --region [REGION_LIST] --channel [CHANNEL_LIST]
```
