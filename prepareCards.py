import os
import yaml
import numpy as np
from collections import OrderedDict
import pandas as pd
import sys, optparse,argparse
from Util.Tool_In_prepareCard import *
from Util.General_Tool import CheckFile,CheckDir
import json
import copy
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
parser.add_argument("--scale", action="store_true")
parser.add_argument("--interference", action="store_true")
parser.add_argument("--For",default='template',type=str,choices=['template','specific'])
parser.add_argument("--Masses",help='List of masses point. Default list=[200,300,350,400,500,600,700]',default=[200, 300, 350, 400, 500, 600, 700],nargs='+')


args = parser.parse_args()


year     = args.year
category = args.category
regions  = args.reg
cp_scaleTo = args.coupling_value

if "rtc" in args.coupling_value:
    signal_process_name = "ttc"
    coupling_name       = "rhotc"
elif "rtu" in args.coupling_value:
    signal_process_name = "ttu"
    coupling_name       = "rhotu"
elif "rtt" in args.coupling_value:
    signal_process_name = "ttt"
    coupling_name       = "rhott"
else:raise ValueError("No such coupling value {}".format(args.coupling_value))

if(args.scale):
    if signal_process_name=="ttc":
        args.coupling_value = 'rtc0p4'
    elif signal_process_name=="ttu":
        args.coupling_value = 'rtu0p4'
    elif signal_process_name=="ttu":
        args.coupling_value = 'rtt0p4'
    else:raise ValueError("No such coupling value {}".format(args.coupling_value))
args.coupling_value = args.coupling_value.replace("p","")

signal_process_name = 'ttc' #Keep the naming rule, suggested by Gouranga.

args.scale = args.scale and not (cp_scaleTo.replace("p","") == args.coupling_value)
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


if args.For == 'template':
    CheckDir('datacards_{}_template'.format(year),True,True)



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
            CheckDir('datacards_run2_template',True)
            for channel in channels:
                for i_year in ["2016apv","2016postapv","2017","2018"]:
                    CheckFile("datacards_run2_template/template_couplingvalue_datacard_{year}_SR_{channel}_{channel}_parameters.txt".format(year=i_year,channel=channel))
                    print('cp ./datacards_{year}_template/template_couplingvalue_datacard_{year}_SR_{channel}_{channel}_parameters.txt ./datacards_run2_template'.format(year=i_year,channel=channel))
                    os.system('cp ./datacards_{year}_template/template_couplingvalue_datacard_{year}_SR_{channel}_{channel}_parameters.txt ./datacards_run2_template'.format(year=i_year,channel=channel))


                print('cd datacards_run2_template;combineCards.py year2016apv=template_couplingvalue_datacard_2016apv_SR_{channel}_{channel}_parameters.txt year2016postapv=template_couplingvalue_datacard_2016postapv_SR_{channel}_{channel}_parameters.txt year2017=template_couplingvalue_datacard_2017_SR_{channel}_{channel}_parameters.txt year2018=template_couplingvalue_datacard_2018_SR_{channel}_{channel}_parameters.txt > template_couplingvalue_datacard_run2_SR_{channel}_{channel}_parameters.txt'.format(channel=channel))
                os.system('cd datacards_run2_template;combineCards.py year2016apv=template_couplingvalue_datacard_2016apv_SR_{channel}_{channel}_parameters.txt year2016postapv=template_couplingvalue_datacard_2016postapv_SR_{channel}_{channel}_parameters.txt year2017=template_couplingvalue_datacard_2017_SR_{channel}_{channel}_parameters.txt year2018=template_couplingvalue_datacard_2018_SR_{channel}_{channel}_parameters.txt > template_couplingvalue_datacard_run2_SR_{channel}_{channel}_parameters.txt'.format(channel=channel))
                print('\n./datacards_run2_template/template_couplingvalue_datacard_run2_SR_{channel}_{channel}_parameters.txt is prepared.'.format(channel=channel))
                
                for i_year in ["2016apv","2016postapv","2017","2018"]:
                    print('rm ./datacards_run2_template/template_couplingvalue_datacard_{year}_SR_{channel}_{channel}_parameters.txt'.format(year=i_year,channel=channel))
                    os.system('rm ./datacards_run2_template/template_couplingvalue_datacard_{year}_SR_{channel}_{channel}_parameters.txt'.format(year=i_year,channel=channel))
        else:
            for channel in channels:
                cat_str = channel+"_"+channel
                template_card = "datacards_"+year+"_template/template_couplingvalue_datacard_"+year+"_SR_"+cat_str+"_parameters.txt"
                
                outputfile = template_card
                #delete the datacard before creating
                CheckFile(template_card,True)
                if channel != 'C':
                
                    with open('./data_info/Datacard_Input/{}/Datacard_Input_{}.json'.format(year,channel),'r') as f:
                        Datacards_Input = json.load(f)
                    with open('./data_info/NuisanceList/corrected_nuisance_list_{}_{}.json'.format(year,channel),'r') as f:
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
                    os.system('cd datacards_{y}_template/;combineCards.py em=template_couplingvalue_datacard_{y}_SR_em_em_parameters.txt ee=template_couplingvalue_datacard_{y}_SR_ee_ee_parameters.txt  mm=template_couplingvalue_datacard_{y}_SR_mm_mm_parameters.txt > template_couplingvalue_datacard_{y}_SR_C_C_parameters.txt'.format(y=year))
                    print(template_card+ ' is prepared')
    elif args.For == 'specific':
        CheckDir("datacards_"+year+"_"+signal_process_name,True,True)
        for channel in channels:
            cat_str = channel+"_"+channel
            template_card = "datacards_"+year+"_template/template_couplingvalue_datacard_"+year+"_SR_"+cat_str+"_parameters.txt"
            dc_tmplate=open(template_card).readlines()



            for imass in args.Masses:
                dc_out = copy.deepcopy(dc_tmplate)
                mA = str(imass+"_COUPLINGVALUE")
                if not args.interference:
                  parameters = "MA"+str(imass) # MA200_rtc0p4, for example.
                else:
                  parameters = "MA" + str(imass) + "_MS" + str(int(imass)-50)
         
                if args.scale:
                  if not args.interference:
                    df = pd.read_fwf("ttc_cross_sections.txt")
                  else:
                    df = pd.read_fwf("ttc_cross_sections_with_interference.txt")
                  cp_value = int(cp_scaleTo.replace('rtc','').replace('rtt','').replace('rtu','').replace('p',''))*0.1
                  for i in range(len(df)):
                    if df['PID'][i] == 'a0' and df['Mass'][i] == int(imass) and df[coupling_name][i] == cp_value:
                      xs_scaleTo       = float(df["cross_section"][i])
                      xs_scaleTo_err   = float(df["Err(cross-section)"][i])
                    if df['PID'][i] == 'a0' and df['Mass'][i] == int(imass) and df[coupling_name][i] == 0.4:
                      xs_reference     = float(df["cross_section"][i])
                      xs_reference_err = float(df["Err(cross-section)"][i])
                  scale       = xs_scaleTo/xs_reference
                  scale_sigma = (xs_scaleTo_err**2/(xs_reference**2) + (xs_reference_err**2)*(xs_scaleTo**2)/(xs_reference**4))**0.5

                  dc_out.append("sigscale rateParam * TAToTTQ_COUPLINGVALUE_MAMASSPOINT %f [%f,%f]"%(scale,scale-scale_sigma,scale+scale_sigma)+'\n')

                card_name = template_card.replace("template",signal_process_name)
                card_name = card_name.replace("parameters",parameters)
                coupling_value = args.coupling_value.split(signal_process_name)[-1]
                card_name = card_name.replace("couplingvalue",coupling_value)
                if(args.scale):
                  card_name = card_name.replace(args.coupling_value,cp_scaleTo.replace('p',''))
                CheckFile(card_name,RemoveFile=True)
                

                fout = open(card_name,'w')

                if args.interference:
                  dc_out = ([iline.replace("SIGNALPROCESS_a_COUPLINGVALUE_MAMASSPOINT", str(signal_process_name + "_a_" + str(imass) + "_s_" + str(int(imass)-50) + "_COUPLINGVALUE")) for iline in dc_out])
                  dc_out =  ([iline.replace("TAToTTQ_COUPLINGVALUE_MAMASSPOINT", "TAToTTQ_" + str(imass) + "_s_" + str(int(imass)-50)+"_COUPLINGVALUE") for iline in dc_out])

                dc_out =  ([iline.replace("SIGNALPROCESS",str(signal_process_name)) for iline in dc_out] )
                
                dc_out =  ([iline.replace("MASSPOINT",str(imass)) for iline in dc_out] )
                dc_out =  ([iline.replace("COUPLINGVALUE",args.coupling_value) for iline in dc_out] ) ## mind that now it is dc_out
                if year =='run2':
                    for y in ['2016apv','2016postapv','2017','2018','run2']:
                        dc_out =  ([iline.replace("datacards_{}_{}/".format(signal_process_name,y),"") for iline in dc_out] )
                else:
                    dc_out =  ([iline.replace("datacards_{}_{}/".format(signal_process_name,year),"") for iline in dc_out] )
                

                
                fout.writelines(dc_out)
                fout.close()
                print ("\nA new datacard: {} is created\n".format( card_name))
    else:raise ValueError('')

'''
[khurana@lxplus752 LimitModel]$ combineCards.py mm=datacards_ttc_2017/ttc_datacard_2017_SR_mm_mm_template.txt ee=datacards_ttc_2017/ttc_datacard_2017_SR_ee_ee_template.txt em=datacards_ttc_2017/ttc_datacard_2017_SR_em_em_template.txt > combo.txt
'''
