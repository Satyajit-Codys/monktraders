from dateutil.relativedelta import relativedelta
import yfinance as yf
import pandas as pd
import datetime,csv
from ta.trend import ema_indicator as ema
from ta.volatility import BollingerBands as bb


def mround(n):
    m=0.05
    a=round(n/m)*m
    return a

def stoch(t,i):
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

def macd(x):
    t=x
    t12 = round(ema(t['Close'],12),2)
    t26 = round(ema(t['Close'],26),2)
    
    em12=t12.iloc[-1]
    em26=t26.iloc[-1]
    m=em12-em26
    
    mv = (351* m /28)-(297*em12/28)+(325*em26/28)
    n=(351*mv/80)-(8019*em12/1120)+(845*em26/224)
    return mround(n)

def psar(x):
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

def ema5(t):
    e = ema(t['Close'],5)
    e = round(e.iloc[-1],2)
    c = round(t['Close'].iloc[-1],2)
    ema5 = mround((c*2/6)+(e*(1-(2/6))))
    return ema5
    
def RSI60(x):
    print(x)

def ema10(x):
    e = ema(t['Close'],10)
    e = round(e.iloc[-1],2)
    c = round(t['Close'].iloc[-1],2)
    ema10 = mround((c*2/11)+(e*(1-(2/11))))
    return ema10
        
    print(x)

def bbtop(x):
    y = bb(x['Close'],20,2)
    temp = y.bollinger_hband()
    return mround(temp[-1])
    

def bbottom(x):
    y = bb(x['Close'],20,2)
    temp = y.bollinger_lband()
    
    return mround(temp[-1])

def e5_21(x):
    print(x)

x= datetime.datetime.today()
x3m=x-relativedelta(months=3)
st = x3m.strftime("%Y-%m-%d")
et = x.strftime("%Y-%m-%d")
print(st,et)
list1={}
script=[]
stoch_l = []
macd_list = []
SAR_list=[]
ema5_list = []
ema10_list = []
bb_top_list = []
bb_bottom_list = []
close =[]

with open('..\\Scriptmaster.csv','r') as f :
    a = csv.reader(f)   
    for row in a:
        script.append(row[0])
        sym=str((row[0])+".NS")
        t = yf.download(sym,start=st,end=et, interval="1d")
        Sn = round(stoch(t,row[0]),2)
        n = round(macd(t),2)
        #psar = psar(t) #round(psar(t),2)
        ema5_value = ema5(t)
        ema10_value = ema10(t)
        
        bb_top = bbtop(t)
        bb_bottom = bbottom(t)
        print(f"Script : {row[0]}, \nSn : {Sn} , \nMACD : {n}, \nEMA5 : {ema5_value},\nEMA10 : {ema10_value},\nBBTOP : {bb_top},\nBBBOTTOM : {bb_bottom}")
        stoch_l.append(Sn)
        macd_list.append(n)
        SAR_list.append(psar)
        ema5_list.append(ema5_value)
        ema10_list.append(ema10_value)
        bb_top_list.append(bb_top)
        bb_bottom_list.append(bb_bottom)
        close.append(t['Close'][-1])
        
        


print(f"Script : {len(script)}, \nSn : {len(stoch_l)} , \nMACD : {len(macd_list)}, \nEMA5 : {len(ema5_list)},\nEMA10 : {len(ema10_list)},\nBBTOP : {len(bb_top_list)},\nBBBOTTOM : {len(bb_bottom_list)}")

list1['Script']=script
list1['MACD']=macd_list
list1['Ema5']=ema5_list
list1['RSI 60']=close
list1['BBTOP']=bb_top_list
list1['EMA10']=ema10_list
list1['BBOT']=bb_bottom_list
list1['RSI 40']=close
list1['Stoch']=stoch_l
list1['EMA5-21']=close
list1['SAR']=close
list1['Close']=close

list1=pd.DataFrame(list1)
list1.to_csv("../Indicator_sheet.csv",index=False)
print("Complete")


