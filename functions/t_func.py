from dateutil.relativedelta import relativedelta
import pandas as pd
from ta.trend import ema_indicator as ema
from ta.volatility import BollingerBands as bb

class trigger(self):
    
    def mround(self,n):
        m=0.05
        a=round(n/m)*m
        return a

    def stoch(self,t,i):
        global Sn,dD,o,h,low,cl,dK
        x=pd.DataFrame()
        x['hhv']=t['High'].rolling(14).max()
        x['llv']=t['Low'].rolling(14).min()
        x['cl']=t['Close']-x['llv']
        x['hl']=x['hhv']-x['llv']
        x['ahl']=x['hl'].rolling(3).mean()
        x['acl']=x['cl'].rolling(3).mean()
        x['dK']=x['acl']*100/x['ahl']
        x['dD']=x['dK'].rolling(3).mean()   
        x['hhln']=t['High'].rolling(13).max()-t['Low'].rolling(13).min()
        x['Sn']=t['Low'].rolling(13).min()-x['cl'].rolling(2).sum()+(3*x['dK'].rolling(2).sum()*x['hhln']/200)
        r,c=x.shape
        #print(x)
        Sn=x.iloc[r-1,c-1]
        dK=x.iloc[r-1,c-4]
        dD=x.iloc[r-1,c-3]
        o=t['Open'].iloc[r-1]
        h=t['High'].iloc[r-1]
        low=t['Low'].iloc[r-1]
        cl=t['Close'].iloc[r-1]
        #x.to_csv("D:/Samco/Stoch1/"+i[:-3]+"S-n.csv")
        return mround(Sn)
    
    def macd(self,x):
        t=x
        t12 = round(ema(t['Close'],12),2)
        t26 = round(ema(t['Close'],26),2)
        
        em12=t12.iloc[-1]
        em26=t26.iloc[-1]
        m=em12-em26
        
        mv = (351* m /28)-(297*em12/28)+(325*em26/28)
        n=(351*mv/80)-(8019*em12/1120)+(845*em26/224)
        return mround(n)
    
    def psar(self,x):
        df =x
        af=[]
        PSAR=[]
        PSARn=[]
        EP=[]
        PSARdir = []
        AF_diff=[]
    
        for i in range (0,len(df)):
    
            if i == 0 :
                af.append(0.02)
                EP.append(df['High'].iloc[0])
                PSAR.append(df['Low'].iloc[0])
                AF_diff.append((EP[0]-PSAR[0])*af[0])
                PSARdir.append(1)
                PSARn.append(EP[0])
    
        #----------Calculate SAR--------------           
            if PSARdir[i-1] == 1 :
                if ((PSAR[i-1]+AF_diff[i-1]) > df['Low'].iloc[i]): #+AF_diff[i-1]
                    PSAR.append(PSAR[i-1])
                else :
                    PSAR.append(PSAR[i-1]+AF_diff[i-1]) 
            else : 
                if (PSAR[i-1]) < df['High'].iloc[i] : #+AF_diff[i-1])
                    PSAR.append(PSAR[i-1])
                else :
                    PSAR.append(PSAR[i-1]+AF_diff[i-1]) 
        #-------------Calculate SAR trend, EP -------------------                  
            if PSAR[i]<df['High'].iloc[i] :
                PSARdir.append(1)
                EP.append(max(EP[i-1],df['High'].iloc[i]))
    
            else:        
                PSARdir.append(0)                      
                EP.append(min(EP[i-1],df['Low'].iloc[i]))
    
        #---------------Calculate AF ----------------              
            if (PSARdir[i] == 1 ) and (PSARdir[i-1] == 1 ):
                if EP[i]>EP[i-1]:
                    af.append(min(0.2,af[i-1]+0.02))
                else:
                    af.append(af[i-1])
            else:
                if (PSARdir[i] ==0) and (PSARdir[i-1]==0):
                    if EP[i]<EP[i-1]:
                        af.append(min(0.2,af[i-1]+0.02))
                    else:
                        af.append(af[i-1])
                else:    
                    af.append(0.02)
    
            AF_diff.append((EP[i]-PSAR[i])*af[i])
    
            PSARn.append(PSAR[i]+AF_diff[i])
        SARN = float(PSARn[-1])
        return mround(SARN)
    
    def ema5(self,t):
        e = ema(t['Close'],5)
        e = round(e.iloc[-1],2)
        c = round(t['Close'].iloc[-1],2)
        ema5 = mround((c*2/6)+(e*(1-(2/6))))
        return ema5
        
    def RSI60(self,x):
        print(x)
    
    def ema10(self,x):
        e = ema(t['Close'],10)
        e = round(e.iloc[-1],2)
        c = round(t['Close'].iloc[-1],2)
        ema10 = mround((c*2/11)+(e*(1-(2/11))))
        return ema10
            
        print(x)
    
    def bbtop(self,x):
        y = bb(x['Close'],20,2)
        temp = y.bollinger_hband()
        return mround(temp[-1])
        
    
    def bbottom(self,x):
        y = bb(x['Close'],20,2)
        temp = y.bollinger_lband()
        
        return mround(temp[-1])
    
    def e5_21(self,x):
        print(x)