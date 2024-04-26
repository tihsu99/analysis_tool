# b-tag efficiency tool 
This tool allows to produce efficiency histograms for the b-tag algorithm.

## Instruction tu run the tool
A macro to run the tool is provided: submit_btageff.py

This allows to run the tool both locally and on condor. Command to run in condor is:
```
python submit_btageff.py -e 2018 -o /eos/home-u/username/btag_2018/ -r condor
```

If you want to try out the tool locally, you can use:
```
python submit_btageff.py -e 2018 -o ./ -r local
```

The submit_btageff.py macro can also be run in debug mode by adding the --debug option to the command:
```
python btageff_producer.py -i root://eosuser.cern.ch///eos/cms/store/group/phys_b2g/ExYukawa/bHplus/2017/v4/TTtoHadronic.root -o /eos/home-u/username/ -e 2017 --debug
```
