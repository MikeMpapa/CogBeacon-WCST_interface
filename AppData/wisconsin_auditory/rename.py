import os 
filelist = os.listdir('.')
for file in filelist:
    fname = file.split('.')
    if fname[1] == 'wav':
        parts = fname[0].split('_')
        os.rename(file, parts[2]+'_'+parts[1]+'_'+parts[0]+'.wav' )
