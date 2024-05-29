# Trigger scale factor study
To generate the needed root file
```
python runcondor.py --era [ERA] --region [bh/boost/all] --channel [Electron/Muon/all] --outdir [OUTDIR]  
```
**TODO: Function checking if the produced root file is okay or not is not perfect, need extra work (now just reproduce manually since only several jobs fail)**
To generate Trigger scale factor
```
python derive_trigger_efficiency.py --indir [INDIR] --era [ERA]
```
