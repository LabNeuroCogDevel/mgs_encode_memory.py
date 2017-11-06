import pandas as pd, numpy as np
near= lambda x,y,t: abs(x-y)<t

df=pd.read_csv("info.txt",sep="\t")

pb_mean=df['pbright'].mean()
pb_std=df['pbright'].std()

s_and_c = df[ 
         ( near(df['pbright'],pb_mean+.5*pb_std,pb_std)) & 
         (near(df['r'],.33,.1) ) & 
         (near(df['g'],.33,.1)) & 
         (near(df['b'],.33,.1)) & 
         (near(df['w']/df['h'],1,.1) ) ]

s_and_c.to_csv('example2.txt',index=False,header=False,sep="\t")

s_and_c.groupby(['generic','specific']).\
 agg({'cat': {"ncat": lambda x: len(x.unique() ), "n": len }}).\
 reset_index().\
 sort_values([('cat','n')],ascending=False)

s_and_c['gs'] = s_and_c.apply(lambda x: "%s:%s"%(x['generic'],x['specific']),axis=1)

# hand pick some catagories
d = s_and_c.query(' \
                gs == "outdoor, natural:water, ice, snow" or \
                gs == "outdoor, natural:forest, field, jungle" or\
                gs == "outdoor, man-made:man-made elements" or\
                gs == "indoor:home or hotel" or\
                gs == "indoor:workplace (office building, factory, lab, etc.)" or\
                gs == "indoor:shopping and dining" ')[['gs','cat','file']]

#import matplotlib.pyplot as plt
