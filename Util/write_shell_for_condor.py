import os

WorkDir = os.popen('pwd').read().split('\n')[0]
print(WorkDir)

if not os.path.isdir(os.path.join(WorkDir,'scripts')):
    print('You do not have [folder]: `scripts` under your current workspace: {}'.format(WorkDir))
    os.mkdir(os.path.join(WorkDir,'scripts'))
    print('`scripts` is created under your workspace')
else:pass


