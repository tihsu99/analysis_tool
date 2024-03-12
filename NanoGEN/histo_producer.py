import os

path = "/eos/cms/store/group/phys_b2g/ExYukawa/bHplus/NanoGEN_2017/v3/"

productions = ["bgth", "cgbh"]
masses = [200, 300, 350, 400, 500, 600, 700, 800, 900, 1000] #[mass for mass in range(200, 1100, 100)]
print(masses)
rhotts = ["01", "04", "06", "10"]
rhotcs = ["01", "04", "06", "10"]

# bgth_H_M800_rhott01_rhotc01_rhotu00.root

for prod in productions:
    for mass in masses:
        for rhott in rhotts:
            for rhotc in rhotcs:
                #filename = "bgth_H_M800_rhott01_rhotc01_rhotu00"
                filename = f"{prod}_H_M{mass}_rhott{rhott}_rhotc{rhotc}_rhotu00"
                print(f"Producing histograms for {filename}")
                os.system(f"python3 bH_GenWeight.py -i {path}{filename}.root -o {filename}_hist")

                
