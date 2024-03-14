import os

path = "/eos/cms/store/group/phys_b2g/ExYukawa/bHplus/NanoGEN_2017/"

listdirs = os.listdir(path)
for folder in listdirs:
    if os.path.isdir(path + folder):
        all_subfolders = [x[0] for x in os.walk(path + folder) if folder.startswith("cgbh") or folder.startswith("bgth")]
        if all_subfolders:
            if not os.path.exists(f"{all_subfolders[-2]}/{folder}_1.root"):
                print(f"********* No files in {all_subfolders[-2]} ")
            else:
                print(f"Merging {path}/v3/{folder}.root")
                os.system(f"haddnano.py {path}/v3/{folder}.root {all_subfolders[-2]}/{folder}_*.root")
