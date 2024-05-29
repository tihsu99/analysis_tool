# Instruction to use the NanoGEN tools
Activate the environment if you have not done it already:

```
source ../script/env.sh
```

## Merge the NanoGEN files
Once all the NanoGEN jobs are finished you can proceed to merge all parts in a single file. To do so you can use the merger macro:

```
python merger.py
```

The macro has a path variable that is the default one `/eos/cms/store/group/phys_b2g/ExYukawa/bHplus/NanoGEN_2017/`. Change it if you used a different one.

## Produce the histograms for theoretical uncertainties
The macro `bH_GenWeight.py` produces the ROOT files with histograms containing the variations to be applied to NanoAOD files. The systematic uncertainties produced are scale, Parton Shower (PS) and PDF variations. These variations are given in percent error as function of the leading GenJet $p_T$.
To run the macro you should use:
```
python merger.py -i input_file_path -o _output_file_name
```

To run over all the files in one go you can also use the `histo_producer.py` routine the loops over the full NanoGEN production:

```
python histo_producer.py
```