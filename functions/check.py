import base
import yfinance as yf

a = base.triggers()
x = input("Enter name of Script :")
t= yf.download(str(x+".NS"), period="max", interval="1d")
print(a.ema5(t))