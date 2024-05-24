import os

path = "/eos/cms/store/group/phys_b2g/ExYukawa/bHplus/NanoGEN_2017/v3/"

productions = ["bgth", "cgbh"]
productions = ["cgbh"]
masses = [200, 300, 350, 400, 500, 600, 700, 800, 900, 1000]
print(masses)
rhotts = ["01", "04", "06", "10"]
rhotcs = ["01", "04", "06", "10"]

for prod in productions:
    for mass in masses:
        for rhott in rhotts:
            for rhotc in rhotcs:
                filename = f"{prod}_H_M{mass}_rhott{rhott}_rhotc{rhotc}_rhotu00"
                print(f"Producing histograms for {filename}")
                os.system(f"python3 new_bH_GenWeight.py -i {path}{filename}.root -o {filename}_hist")

                
