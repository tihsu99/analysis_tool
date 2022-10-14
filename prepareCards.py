import os
import yaml
import numpy as np
from collections import OrderedDict
import pandas as pd
import sys, optparse,argparse
from Util.Tool_In_prepareCard import *
from Util.General_Tool import CheckFile,CheckDir
import json
## ----- command line argument
couplings_List = ['rtc','rtu','rtt']
cp_values_List = ['0p1','0p4','0p8','1p0']
coupling_value_choices=[]
for coupling in couplings_List:
    for value in cp_values_List:
        coupling_value_choices.append(coupling+value)


usage = "python prepareCards.py -y 2017 -c em -reg 'SR_em'"
parser = argparse.ArgumentParser(description=usage)
parser.add_argument("-y", "--year", dest="year", default="2016postapv",choices=["2016postapv","2016apv","2017","2018","run2"])
#parser.add_argument("-m", "--model", dest="model", default="ExY")
parser.add_argument("-c", "--category",  dest="category",default="all",choices=['ee','em','mm','all','C'])
parser.add_argument("-reg", nargs="+", default=["a", "b"])
parser.add_argument("--reset",action="store_true")
parser.add_argument("--coupling_value",default='rtc0p4',type=str,choices=coupling_value_choices)
parser.add_argument("--For",default='template',type=str,choices=['template','specific'])
parser.add_argument("--Masses",help='List of masses point. Default list=[200,300,350,400,500,600,700]',default=[200, 300, 350, 400, 500, 600, 700],nargs='+')


args = parser.parse_args()


year     = args.year
category = args.category
regions  = args.reg
args.coupling_value = args.coupling_value.replace("p","")
#modelName = args.model


#print (year,regions)#, category, regions, modelName)
'''
if category=='em' or category=='ee' or category=='mm':
    f = open('ttc.yaml')
else:
    print "no category"
    exit 

doc = yaml.safe_load(f)
'''



## for nuisnaces 
f_nuis = open('nuisances.yaml')
doc_nuis   = yaml.safe_load(f_nuis)


outdir = 'datacards_ttc_'+year



os.system('mkdir -p '+ outdir)


top_ = '''
imax *  number of channels
jmax *  number of backgrounds

kmax *  number of nuisance parameterS (sources of systematical uncertainties)
'''

if args.For == 'template':

    print("=======================")
    print("START WRITING TEMPLATE DATACARDS")
    print("=======================")

elif args.For =='specific':
    print("=======================")
    print("START WRITING DATACARDS")
    print("=======================")
#print (regions)
if category =='all':channels=['ee','em','mm','C']
else:channels=[category]



for reg in regions:
     
    if args.For == 'template':
        if year=='run2' :
            if CheckDir('datacards_ttc_run2',False):
                os.system('rm -ifr datacards_ttc_run2')
            print('mkdir datacards_ttc_run2') 
            os.system('mkdir datacards_ttc_run2')
            for channel in channels:
            
                print('cp ./datacards_ttc_2016apv/ttc_datacard_2016apv_SR_{}_{}_template.txt ./datacards_ttc_run2'.format(channel,channel))
                os.system('cp ./datacards_ttc_2016apv/ttc_datacard_2016apv_SR_{}_{}_template.txt ./datacards_ttc_run2'.format(channel,channel))
                print('cp ./datacards_ttc_2016postapv/ttc_datacard_2016postapv_SR_{}_{}_template.txt ./datacards_ttc_run2'.format(channel,channel))
                os.system('cp ./datacards_ttc_2016postapv/ttc_datacard_2016postapv_SR_{}_{}_template.txt ./datacards_ttc_run2'.format(channel,channel))
                print('cp ./datacards_ttc_2017/ttc_datacard_2017_SR_{}_{}_template.txt ./datacards_ttc_run2'.format(channel,channel))
                os.system('cp ./datacards_ttc_2017/ttc_datacard_2017_SR_{}_{}_template.txt ./datacards_ttc_run2'.format(channel,channel))
                print('cp ./datacards_ttc_2018/ttc_datacard_2018_SR_{}_{}_template.txt ./datacards_ttc_run2'.format(channel,channel))
                os.system('cp ./datacards_ttc_2018/ttc_datacard_2018_SR_{}_{}_template.txt ./datacards_ttc_run2'.format(channel,channel))
                print('combineCards.py year2016apv=./datacards_ttc_run2/ttc_datacard_2016apv_SR_{}_{}_template.txt year2016postapv=./datacards_ttc_run2/ttc_datacard_2016postapv_SR_{}_{}_template.txt year2017=./datacards_ttc_run2/ttc_datacard_2017_SR_{}_{}_template.txt year2018=./datacards_ttc_run2/ttc_datacard_2018_SR_{}_{}_template.txt > ./datacards_ttc_run2/ttc_datacard_run2_SR_{}_{}_template.txt'.format(channel,channel,channel,channel,channel,channel,channel,channel,channel,channel))
                os.system('combineCards.py year2016apv=./datacards_ttc_run2/ttc_datacard_2016apv_SR_{}_{}_template.txt year2016postapv=./datacards_ttc_run2/ttc_datacard_2016postapv_SR_{}_{}_template.txt year2017=./datacards_ttc_run2/ttc_datacard_2017_SR_{}_{}_template.txt year2018=./datacards_ttc_run2/ttc_datacard_2018_SR_{}_{}_template.txt > ./datacards_ttc_run2/ttc_datacard_run2_SR_{}_{}_template.txt'.format(channel,channel,channel,channel,channel,channel,channel,channel,channel,channel,))
                print('\n./datacards_ttc_run2/ttc_datacard_run2_SR_{}_{}_template.txt is prepared.'.format(channel,channel))
        else:
            for channel in channels:
                cat_str = channel+"_"+channel
                template_card = "datacards_ttc_"+year+"/ttc_datacard_"+year+"_SR_"+cat_str+"_template.txt"
                
                outputfile = template_card
                #delete the datacard before creating
                CheckFile(template_card,True)
                if channel != 'C':
                
                    with open('./data_info/Datacard_Input/{}/Datacard_Input_{}.json'.format(year,channel),'r') as f:
                        Datacards_Input = json.load(f)
                    with open('./data_info/NuisanceList/nuisance_list_{}_{}.json'.format(year,channel),'r') as f:
                        nuisance_ordered_list = json.load(f)

                    print(len(nuisance_ordered_list.keys()))
                    
                    df0 = pd.DataFrame(Get_BinProcRate(Datacards_Input))
                    #delete the datacard before creating
                    #os.system('rm {}/ttc_datacard_{}_{}*'.format(outdir,year,category))    
                        
                    #print ("reg:",reg)
                    #print ("doc[reg]: {}".format(doc[reg]))
                    #print("getbinProcRate(doc[reg]): {}".format(getbinProcRate(doc[reg])))
                    
                    
                    #print(getbinProcRate(doc[reg]))
                    
                    
                    df0 = df0.rename(columns={"process1":"process"})   ## replacing process1 by process
                    df1 =  pd.DataFrame(Get_ProcSyst(Datacards_Input,nuisance_ordered_list))

                    
                    df1 =  df1.replace("LUMIVAL",doc_nuis["LUMIVAL"]["y"+str(year)])
                    df1.rename(columns=lambda s: s.replace("YEAR", year), inplace=True)
                    
                    print(template_card)
                    fout = open(template_card,'w')
                    p0 = df0.T.to_string(justify='right',index=True, header=False)
                    p1 = df1.T.to_string(justify='right',index=True, header=False)
                    
                    part1 = top_
                    part2 = getUpperPart2(reg,year)
                    part2 = part2.replace("CHANNELNAME",category)
                    
                    print ("part2: ",part2)
                    part3 = getUpperPart3(reg)
                    
                    fout.write(part1+'\n')
                    fout.write('------------'+'\n')
                    fout.write(part2+'\n')
                    fout.write('------------'+'\n')
                    fout.write(part3+'\n')
                    fout.write('observation -1'+'\n')
                    fout.write('------------'+'\n')
                    
                 
                    fout.write(p0+'\n')
                    fout.write(p1+'\n')
                    fout.write("* autoMCStats 10 0 1  "+'\n')
                #   Since we have proper cross sections taken into account in the inputs we do not need this line below.    
                #    fout.write("sigscale rateParam * TAToTTQ_COUPLINGVALUE_MAMASSPOINT 0.01 [0.009999,0.01111]"+'\n')
                    # fout.write(p1+'\n')
                    
                    #fout.write('------------'+'\n')
                    #fout.write(p+'\n')
                    #fout.write(part4+'\n')
                    fout.close()
                    print(outputfile+' is prepared!')
                    print("===================================================")
                    print("")
                else:    
                    os.system('combineCards.py em=datacards_ttc_{}/ttc_datacard_{}_SR_em_em_template.txt ee=datacards_ttc_{}/ttc_datacard_{}_SR_ee_ee_template.txt  mm=datacards_ttc_{}/ttc_datacard_{}_SR_mm_mm_template.txt > datacards_ttc_{}/ttc_datacard_{}_SR_C_C_template.txt'.format(year,year,year,year,year,year,year,year))
                    print(template_card+ ' is prepared')
    elif args.For == 'specific':
        for channel in channels:
            cat_str = channel+"_"+channel
            template_card = "datacards_ttc_"+year+"/ttc_datacard_"+year+"_SR_"+cat_str+"_template.txt"
            dc_tmplate=open(template_card).readlines()
            for imass in args.Masses:
                mA = str(imass)
                parameters = "MA"+str(imass)+"_"+args.coupling_value # MA200_rtc0p4, for example.
                card_name = template_card.replace("template",parameters)
                CheckFile(card_name,RemoveFile=True)
                

                fout = open(card_name,'w')
                dc_out =  ([iline.replace("MASSPOINT",str(imass)) for iline in dc_tmplate] )
                dc_out =  ([iline.replace("COUPLINGVALUE",args.coupling_value) for iline in dc_out] ) ## mind that now it is dc_out
                if year =='run2':
                    for y in ['2016apv','2016postapv','2017','2018','run2']:
                        dc_out =  ([iline.replace("datacards_ttc_{}/".format(y),"") for iline in dc_out] )
                else:
                    dc_out =  ([iline.replace("datacards_ttc_{}/".format(year),"") for iline in dc_out] )
                

                
                fout.writelines(dc_out)
                fout.close()
                print ("\nA new datacard: {} is created\n".format( card_name))
    else:raise ValueError('')

'''
[khurana@lxplus752 LimitModel]$ combineCards.py mm=datacards_ttc_2017/ttc_datacard_2017_SR_mm_mm_template.txt ee=datacards_ttc_2017/ttc_datacard_2017_SR_ee_ee_template.txt em=datacards_ttc_2017/ttc_datacard_2017_SR_em_em_template.txt > combo.txt
'''
