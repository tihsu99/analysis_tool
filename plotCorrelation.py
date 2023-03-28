import os
import ROOT
import json
import matplotlib.pyplot as plt
import numpy as np


def plotCorrelation(FitDiagnostics_file='', outputdir='', impacts_json = ''):

    inFile = ROOT.TFile.Open(FitDiagnostics_file ,"READ")

    Impact_Rank = 30
    Corr_Rank= 15
    CorrelationMatrix = inFile.Get('covariance_fit_s')

    with open(impacts_json) as f:
        data = json.load(f)

    POIs = [ele['name'] for ele in data['POIs']]
    POI = POIs[0]


    Params = data['params']
    print('Start to ranking impacts')
    Params.sort(key = lambda x: abs(x['impact_%s' % POI]), reverse = True)


    Impact_Rank_Top_param = dict()
    for idx, param in enumerate(Params):
        #if idx > Impact_Rank: break
        paramInfo = dict()
        paramInfo['Name'] = param['name']
        paramInfo['bin'] = -1
        paramInfo['Rk'] = idx+1
        Impact_Rank_Top_param[param['name']] = paramInfo
    print('Start to retrieve correlation information for nuisance')
    Impact_Rank_Top_param_List = sorted(Impact_Rank_Top_param.items(), key = lambda x: x[1]['Rk'], reverse = True)
    for idx, param in enumerate(Impact_Rank_Top_param_List):
        for ibin in range(CorrelationMatrix.GetNbinsX() + 1):
            if CorrelationMatrix.GetXaxis().GetBinLabel(ibin+1) == param[1]['Name']:
                Impact_Rank_Top_param_List[idx][1]['bin'] = ibin+1
                
    print('Plotting')
    for idx,param in enumerate(Impact_Rank_Top_param_List):
        if param[1]['Name']  != 'jes' :continue
        Correlation = []

        for ibin in range(CorrelationMatrix.GetNbinsY()):
            Info = {}
            Info['name'] = CorrelationMatrix.GetYaxis().GetBinLabel(ibin+1) 
            Info['correlation'] = CorrelationMatrix.GetBinContent(param[1]['bin'], ibin+1)
            Correlation.append(Info)



        Correlation.sort(key = lambda x: abs(x['correlation']), reverse = True)
        #Correlation = Correlation[:Corr_Rank]
        correlation_array = []
        name_array = []
        for jdx, corr in enumerate(Correlation):
            if jdx < Corr_Rank:
                correlation_array.append(corr['correlation'])
                if corr['name'] == 'r':
                    name_array.append(corr['name'])
                else:
                    name_array.append(corr['name'] + ':Rk(%s)' % Impact_Rank_Top_param[corr['name']]['Rk'])
            else:break

        ypos = np.arange(len(name_array))
        plt.rcdefaults()
        fig, ax = plt.subplots()
        fig.set_size_inches(20.5, 10.5)
        ax.barh(ypos, np.array(correlation_array), align = 'center')
        ax.set_yticks(ypos)

        ax.set_yticklabels(name_array)
        
        for tick in ax.yaxis.get_major_ticks():
            tick.label.set_fontsize(10) 
        ax.invert_yaxis()
        ax.set_xlabel('Correlation')
        ax.set_title('Correlation Ranking for %s' %param[1]['Name'])
        
        output = os.path.join(outputdir, 'ImpactRank%s_CorrelationFor-%s.png'%(param[1]['Rk'], param[1]['Name']))
        
        fig.savefig(output, dpi=100)
        print('\033[1;33m* Please check plot: \033[4m{}\033[0;m'.format(output))

