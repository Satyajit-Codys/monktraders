import pandas as pd
import datetime
from ta.trend import ema_indicator as ema
from ta.volatility import BollingerBands as bb

class triggers:
    
    def __init__(self):
        self.stoch_tv = None
        self.stoch_trend = None
        self.stoch_signal =None
        self.stoch_k = None
        self.stoch_d = None
        self.macd_tv = None
        self.macd_fast = None
        self.macd_slow = None
        self.macd_value = None
        self.macd_trend = None
        self.macd_signal = None
        self.ema5_tv = None
        self.ema5_value = None
        self.ema5_trend = None
        self.ema5_signal = None
        self.ema10_tv = None
        self.ema10_value = None
        self.ema10_trend = None
        self.ema10_signal = None
        self.psar_tv = None
        self.psar_value = None
        self.psar_trend = None
        self.psar_signal = None
        self.bbtop_tv = None
        self.bbtop_value = None
        self.bbtop_trend = None
        self.bbtop_signal = None
        self.bbottom_tv = None
        self.bbottom_value = None
        self.bbottom_trend = None
        self.bbottom_signal = None



        self.utrend = "Up Trend"
        self.dtrend = "Down Trend"
        self.babove = "Buy Above"
        self.sbelow = "Sell Below"
        
        return



    def mround(self,n):
        m=0.05
        try:
            a=round(n/m)*m
        except:
            a=n
        return a

    def close_bs(self,data,cl):
        df = pd.DataFrame(data,columns=["A","B","Value","X"])
        df = df.drop(7)
        df["diff"]=cl-df["Value"]
        df["buy_t"]=df["diff"].apply(lambda x : 100000 if x<=0 else x)
        df["sell_t"]=df["diff"].apply(lambda x : 100000 if x>=0 else x)
        df["b_rank"]=df["buy_t"].rank(ascending =True)
        df["s_rank"]=df["sell_t"].rank(ascending =True)
        bb_indicator = df.loc[df['b_rank']==1]
        bs_indicator = df.loc[df['s_rank']==1]
        if bb_indicator.empty:
            bb_i_name = "No Closest Buy"
            bb_i_value =""
        else:
            bb_i_name = bb_indicator.iloc[-1][0]
            bb_i_value = bb_indicator.iloc[-1][2] 
            
        if bs_indicator.empty:
            bs_i_name = "No Closest Buy"
            bs_i_value =""
        else:
            bs_i_name = bs_indicator.iloc[-1][0]
            bs_i_value  = bs_indicator.iloc[-1][2]
        
        ret_tup = (bb_i_name,bb_i_value,bs_i_name,bs_i_value)
        #print(ret_tup)
        return ret_tup
        
        

    def lastTF(self,a,b,c,d):
        ltf1 = a.index[-1]+datetime.timedelta(days=1)
        ltf5 = b.index[-2]+ datetime.timedelta(minutes=5)
        ltf15 = c.index[-2]+ datetime.timedelta(minutes=15)
        ltf1h = d.index[-2]+ datetime.timedelta(hours=1)

        return ltf1,ltf5,ltf15,ltf1h

    def stoch(self,t):
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
        
        Sn=x.iloc[r-1,c-1]
        dK=x.iloc[r-1,c-4]
        dD=x.iloc[r-1,c-3]
        o=t['Open'].iloc[r-1]
        h=t['High'].iloc[r-1]
        low=t['Low'].iloc[r-1]
        cl=t['Close'].iloc[r-1]
        self.stoch_k = x['dK'][-1]
        self.stoch_tv = Sn
        if t['Close'][-1] <Sn : 
            self.stoch_trend = self.dtrend 
            self.stoch_signal = self.babove
        else: 
            self.stoch_trend = self.utrend
            self.stoch_signal = self.sbelow
        
        self.stoch_k = dK
        self.stoch_d = dK
                
        return self.mround(Sn)
    
    def macd(self,t):
        
        t12 = round(ema(t['Close'],12),2)
        t26 = round(ema(t['Close'],26),2)
        
        em12=t12.iloc[-1]
        em26=t26.iloc[-1]
        m=em12-em26
        
        mv = (351* m /28)-(297*em12/28)+(325*em26/28)
        n=(351*mv/80)-(8019*em12/1120)+(845*em26/224)
        
        self.macd_tv = n
        self.macd_fast = em12
        self.macd_slow = em26
        self.macd_value = m

        if t['Close'][-1] < self.macd_tv : 
            self.macd_trend = self.dtrend
            self.macd_signal = self.babove
        else :
            self.macd_trend = self.utrend
            self.macd_signal = self.sbelow
                    
        return self.mround(n)
    
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
        
        self.psar_tv = SARN
        self.psar_value = PSARn[-2]

        if x['Close'][-1] < self.psar_tv : 
            self.psar_trend = self.dtrend
            self.psar_signal = self.babove
        else :
            self.psar_trend = self.utrend
            self.psar_signal = self.sbelow
        
        
        return self.mround(SARN)
    
    def ema5(self,t):
        e = ema(t['Close'],5)
        e = round(e.iloc[-1],2)
        c = round(t['Close'].iloc[-1],2)
        ema5 = self.mround((c*2/6)+(e*(1-(2/6))))
        self.ema5_tv = ema5
        self.ema5_value = ema5

        if t['Close'][-1] < self.ema5_tv : 

            self.ema5_trend = self.dtrend
            self.ema5_signal = self.babove
        else :
            self.ema5_trend = self.utrend
            self.ema5_signal = self.sbelow      
        
        return ema5
    
    
    def RSI60(self,x):
        print(x)
    
    def ema10(self,t):
        e = ema(t['Close'],10)
        e = round(e.iloc[-1],2)
        c = round(t['Close'].iloc[-1],2)
        ema10 = self.mround((c*2/11)+(e*(1-(2/11))))
        
        self.ema10_tv = ema10
        self.ema10_value = ema10
    
        if t['Close'][-1] < self.ema10_tv : 
    
            self.ema10_trend = self.dtrend
            self.ema10_signal = self.babove
        else :
            self.ema10_trend = self.utrend
            self.ema10_signal = self.sbelow      
        
        return self.mround(ema10)
    
    def bbtop(self,t):
        y = bb(t['Close'],20,2)
        temp = y.bollinger_hband()
        tx=self.mround(temp[-1])
        self.bbtop_tv = tx
        self.bbtop_value = tx

        if t['Close'][-1] < tx :    
    
            self.bbtop_trend = self.dtrend
            self.bbtop_signal = self.babove
    
        else :    
            self.bbtop_trend = self.utrend
            self.bbtop_signal = self.sbelow

        return tx
        
    
    def bbottom(self,t):
        y = bb(t['Close'],20,2)
        temp = y.bollinger_lband()

        self.bbottom_tv = self.mround(temp[-1])
        self.bbottom_value = self.mround(temp[-1])


        if t['Close'][-1] < self.bbottom_tv:    
        
            self.bbottom_trend = self.dtrend
            self.bbottom_signal = self.babove
    
        else :
            
            self.bbottom_trend = self.utrend
            self.bbottom_signal = self.sbelow
        
        return self.mround(temp[-1])
