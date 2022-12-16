import os
import pathlib
from textwrap import indent
from unicodedata import name
from numpy import True_
import pandas as pd
import yfinance as yf
from datetime import datetime, date, timedelta
from functions import base
from flask_sqlalchemy import SQLAlchemy
import json
import requests
from flask import Flask, session, abort, redirect, request, render_template ,url_for
from google.oauth2 import id_token
from google_auth_oauthlib.flow import Flow
from pip._vendor import cachecontrol
import google.auth.transport.requests
import stripe
import pymysql
pymysql.install_as_MySQLdb()

app = Flask("Monk Traders App")
app.secret_key = "aish"
app.config['SQLALCHEMY_DATABASE_URI'] = "mysql://root:@localhost/monktrad_db1"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


# This is your production secret API key.
stripe.api_key = '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'

# # This is your test secret API key.
# stripe.api_key = 'sk_test_51JD7iaSCgyYMC6HHXdHUp2SdKKWnc6L5gcg4XgoMBRa08trxwZzEf5OzDQnu3gohP9edY1rztiD6wEIQPmQLDXjK00dEczTMmk'

headings = ("Indicator","Action","Trigger Value",)
sym = str
a = base.triggers()
b = base.triggers()
c = base.triggers()
d = base.triggers()

os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

GOOGLE_CLIENT_ID = "922150483834-fgj4c1l3iqkrfdo4j403vhclkgir8vcb.apps.googleusercontent.com"
client_secrets_file = os.path.join(pathlib.Path(__file__).parent, "client_secret.json")

flow = Flow.from_client_secrets_file(
    client_secrets_file=client_secrets_file,
    scopes=["https://www.googleapis.com/auth/userinfo.profile", "https://www.googleapis.com/auth/userinfo.email", "openid"],
    redirect_uri="http://127.0.0.1:5000/callback"
)

# db classes
class Exchange(db.Model):
    E_ID = db.Column(db.Integer,primary_key=True)
    E_Name = db.Column(db.String(15),nullable = False)
    E_Country = db.Column(db.String(15),nullable = False)
    E_Segment = db.Column(db.String(15),nullable = False)

class Index_List(db.Model):
    I_Id = db.Column(db.Integer,primary_key=True)
    Index_name = db.Column(db.String(15),nullable = False)
    Index_Exch = db.Column(db.String(15),nullable = False)
    Index_last_Mod = db.Column(db.String(15),nullable = False)
    Cap = db.Column(db.String(15),nullable = False)

class nifty_50(db.Model):
    S_Name = db.Column(db.String(15),nullable = False)
    S_ID = db.Column(db.Integer,primary_key=True)
    S_Symbol = db.Column(db.String(15),nullable = False)

class script(db.Model):
    S_ID = db.Column(db.Integer,primary_key=True)
    E_ID = db.Column(db.Integer,nullable = False)
    S_Name = db.Column(db.String(15),nullable = False)
    S_Sym = db.Column(db.String(15),nullable = False)
    S_Segment = db.Column(db.String(15),nullable = False)
    S_Expiry = db.Column(db.String(15),nullable = False)
    S_Strike_Price = db.Column(db.String(15),nullable = False)
    S_Option_Type = db.Column(db.String(15),nullable = False)
    Suffex = db.Column(db.String(15),nullable = False)

class script_data(db.Model):
    S_ID = db.Column(db.Integer,primary_key=True)
    Date = db.Column(db.DateTime,nullable = False)
    S_Open = db.Column(db.Float,nullable = False)
    S_High = db.Column(db.Float,nullable = False)
    S_Low = db.Column(db.Float,nullable = False)
    S_Close = db.Column(db.Float,nullable = False)
    S_Volume = db.Column(db.Float,nullable = False)

class ta_list(db.Model):
    T_ID = db.Column(db.Integer,primary_key=True)
    T_Name = db.Column(db.String(15),nullable = False)
    T_Desc = db.Column(db.String(15),nullable = False)

class ta_values(db.Model):
    Index_Name = db.Column(db.String(15),nullable = False)
    S_Id = db.Column(db.Integer,primary_key=True)
    Script = db.Column(db.String(15),nullable = False)
    Date = db.Column(db.DateTime,nullable = False)
    MACD = db.Column(db.Float,nullable = False)
    EMA5 = db.Column(db.Float,nullable = False)
    EMA10 = db.Column(db.Float,nullable = False)
    Stoch = db.Column(db.Float,nullable = False)
    PSAR = db.Column(db.Float,nullable = False)
    BBTop = db.Column(db.Float,nullable = False)
    BBottom = db.Column(db.Float,nullable = False)
    CLOSE =  db.Column(db.Float,nullable = False)
    C_B_T = db.Column(db.String(15),nullable = False)
    C_B_TV = db.Column(db.Float,nullable = False)
    C_S_T = db.Column(db.String(15),nullable = False)
    C_S_TV =  db.Column(db.Float,nullable = False)

class user_list(db.Model):
    User_id = db.Column(db.Integer,primary_key=True)
    User_name = db.Column(db.String(35),nullable = False)
    User_email = db.Column(db.String(35),nullable = False)
    User_mobile = db.Column(db.Integer)
    User_create_dt = db.Column(db.DateTime)
    User_status = db.Column(db.String(35),nullable = False)
    User_validity =db.Column(db.DateTime)

#global Variables
all_stocks = script.query.all()

indices_search = ta_values.query.with_entities(ta_values.Index_Name).distinct()
all_indices = [dict(zip(row.keys(), row)) for row in indices_search]

#GLobal 
def login_is_required(function):
    def wrapper(*args, **kwargs):
        if "google_id" not in session:
            return abort(401)  # Authorization required
        else:
            return function()

    return wrapper

# get subscription details
def fetch_subscription():
    subscription_status= False
    email=session['email']
    try:
        customer= stripe.Customer.list(email=email)
        customer = customer['data'][0]
        customer_id = customer['id']
        get_sub = stripe.Subscription.list(customer=customer_id)
        get_sub = get_sub['data'][0]
        subscription_status = get_sub['status']
        print("stripe")
    except:
        user = user_list.query.filter_by(User_email=email).first()
        if user.User_validity >= date.today():
            user.User_status="active"
            subscription_status = "active"
            print("active")
        else:
            print("expired")
            user.User_status = "expired"
            subscription_status = "trial expired"
        print("db")
    return subscription_status


@app.route("/login")
def login():
    authorization_url, state = flow.authorization_url()
    session["state"] = state
    return redirect(authorization_url)


@app.route("/callback")
def callback():
    flow.fetch_token(authorization_response=request.url)

    if not session["state"] == request.args["state"]:
        abort(500)  # State does not match!

    credentials = flow.credentials
    request_session = requests.session()
    cached_session = cachecontrol.CacheControl(request_session)
    token_request = google.auth.transport.requests.Request(session=cached_session)

    id_info = id_token.verify_oauth2_token(
        id_token=credentials._id_token,
        request=token_request,
        audience=GOOGLE_CLIENT_ID
    )

    session["google_id"] = id_info.get("sub")
    session["name"] = id_info.get("name")
    session['email'] = id_info.get('email')
    session["selected_date"] = ""
    session["selected_index"] = ""
    
    user = user_list.query.filter_by(User_email=session['email']).first()
    if user==None:
        validity= date.today() + timedelta(days=7)
        user = user_list(User_name=session['name'], User_mobile="", User_email=session['email'], User_create_dt=date.today(), User_status="active", User_validity= validity)
        db.session.add(user)
        db.session.commit()
    return redirect("/dashboard")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

@app.route('/', endpoint='/')
def homepage():
    return render_template('homepage.html')

# @app.route("/protected_area")
# @login_is_required
# def protected_area():
#     return f"Hello {session['name']}! <br/> <a href='/logout'><button>Logout</button></a>"

@app.route("/dashboard", endpoint='/dashboard')
@login_is_required
def dashboard():
    return render_template('xtreme-html/index.html', name=session['name'], email=session['email'])

@app.route("/search", methods=["GET", "POST"])
def home():
    if fetch_subscription() =="active":

        global all_stocks
        stocks =  [[stock.S_Sym, stock.Suffex] for stock in all_stocks]
        sym=str(request.form.get("ticker"))
        print(sym)
        
        try :
            t = yf.download(sym,period = "30d",interval = "1d")
            t5 = yf.download(sym,period = "2d",interval = "5m")
            t15= yf.download(sym,period = "2d",interval = "15m")
            t1h= yf.download(sym,period = "7d",interval = "1h")
            
            r1 = a.macd(t)
            r2 = a.ema5(t)
            r3 = a.ema10(t)
            r4 = a.bbtop(t)
            r5 = a.bbottom(t)
            r6 = a.stoch(t)
            r7 = a.psar(t)
            r11 = a.macd_signal
            r21 = a.ema5_signal
            r31 = a.ema10_signal
            r41 = a.bbtop_signal
            r51 = a.bbottom_signal
            r61 = a.stoch_signal
            r71 = a.psar_signal
            x_o = t['Open'][-1]
            x_h = t['High'][-1]
            x_l = t['Low'][-1]
            x_c = t['Close'][-1]
            
            
            #5min
            
            r51 = b.macd(t5)
            r52 = b.ema5(t5)
            r53 = b.ema10(t5)
            r54 = b.bbtop(t5)
            r55 = b.bbottom(t5)
            r56 = b.stoch(t5)
            r57 = b.psar(t5)
            r511 = b.macd_signal
            r521 = b.ema5_signal
            r531 = b.ema10_signal
            r541 = b.bbtop_signal
            r551 = b.bbottom_signal
            r561 = b.stoch_signal
            r571 = b.psar_signal
            x5_o = t5['Open'][-1]
            x5_h = t5['High'][-1]
            x5_l = t5['Low'][-1]
            x5_c = t5['Close'][-1]


            #15min
            
            r151 = c.macd(t15)
            r152 = c.ema5(t15)
            r153 = c.ema10(t15)
            r154 = c.bbtop(t15)
            r155 = c.bbottom(t15)
            r156 = c.stoch(t15)
            r157 = c.psar(t15)
            r1511 = c.macd_signal
            r1521 = c.ema5_signal
            r1531 = c.ema10_signal
            r1541 = c.bbtop_signal
            r1551 = c.bbottom_signal
            r1561 = c.stoch_signal
            r1571 = c.psar_signal
            x15_o = t15['Open'][-1]
            x15_h = t15['High'][-1]
            x15_l = t15['Low'][-1]
            x15_c = t15['Close'][-1]

            #15min
            
            r151 = c.macd(t15)
            r152 = c.ema5(t15)
            r153 = c.ema10(t15)
            r154 = c.bbtop(t15)
            r155 = c.bbottom(t15)
            r156 = c.stoch(t15)
            r157 = c.psar(t15)
            r1511 = c.macd_signal
            r1521 = c.ema5_signal
            r1531 = c.ema10_signal
            r1541 = c.bbtop_signal
            r1551 = c.bbottom_signal
            r1561 = c.stoch_signal
            r1571 = c.psar_signal
            x15_o = t15['Open'][-1]
            x15_h = t15['High'][-1]
            x15_l = t15['Low'][-1]
            x15_c = t15['Close'][-1]

            #1hr
            
            r1h1 = d.macd(t1h)
            r1h2 = d.ema5(t1h)
            r1h3 = d.ema10(t1h)
            r1h4 = d.bbtop(t1h)
            r1h5 = d.bbottom(t1h)
            r1h6 = d.stoch(t1h)
            r1h7 = d.psar(t1h)
            r1h11 = d.macd_signal
            r1h21 = d.ema5_signal
            r1h31 = d.ema10_signal
            r1h41 = d.bbtop_signal
            r1h51 = d.bbottom_signal
            r1h61 = d.stoch_signal
            r1h71 = d.psar_signal
            x1h_o = t1h['Open'][-1]
            x1h_h = t1h['High'][-1]
            x1h_l = t1h['Low'][-1]
            x1h_c = t1h['Close'][-1]

            
            data = (("MACD",r11,r1),("EMA5",r21,r2),("EMA10",r31,r3),("BB TOP",r41,r4),("BB Bottom",r51,r5),("Stochastic",r61,r6),("Parabolic SAR",r71,r7), (x_o,x_h,x_l,x_c))

            data5 = (("MACD",r511,r51),("EMA5",r521,r52),("EMA10",r531,r53),("BB TOP",r541,r54),("BB Bottom",r551,r55),("Stochastic",r561,r56),("Parabolic SAR",r571,r57), (x_o,x_h,x_l,x_c))

            data15 = (("MACD",r1511,r151),("EMA5",r1521,r152),("EMA10",r1531,r153),("BB TOP",r1541,r154),("BB Bottom",r1551,r155),("Stochastic",r1561,r156),("Parabolic SAR",r1571,r157), (x_o,x_h,x_l,x_c))

            data1h = (("MACD",r1h11,r1h1),("EMA5",r1h21,r1h2),("EMA10",r1h31,r1h3),("BB TOP",r1h41,r1h4),("BB Bottom",r1h51,r1h5),("Stochastic",r1h61,r1h6),("Parabolic SAR",r1h71,r1h7), (x_o,x_h,x_l,x_c))
                                                            
            bb_d = a.close_bs(data,x_c)
            bb_5 = b.close_bs(data,x5_c)
            bb_15 = c.close_bs(data,x15_c)
            bb_1h = d.close_bs(data,x1h_c)
                    
            print(data)
            if request.method == "POST":
                print(request.form)
                #data.append(request.form.get("A"))
                
                sym_org = sym.split(".")[0]
                sym_name = script.query.filter_by(S_Sym=sym_org).first().S_Name
                return render_template("table.html", name=session['name'], email=session['email'], sym_org=sym_org,sym_name=sym_name, headings = headings,data = data, data5 = data5,data15 = data15,data1h = data1h, bb_d=bb_d, bb_5=bb_5, bb_15=bb_15, bb_1h=bb_1h)
                    
        except:
            print("error")
            if request.method == "POST":
                print(request.form)

                sym_org = sym.split(".")[0]
                sym_name = script.query.filter_by(S_Sym=sym_org).first().S_Name
                #data.append(request.form.get("A"))
                return render_template("table.html", name=session['name'], email=session['email'], sym_org=sym_org,sym_name=sym_name, headings = headings,data = data, data5 = data5,data15 = data15,data1h = data1h, bb_d=bb_d, bb_5=bb_5, bb_15=bb_15, bb_1h=bb_1h)
        
        return render_template("search.html", all_stocks=stocks)
    else:
        return render_template("subscription/payment.html", name=session['name'], email=session['email'])


@app.route("/indices", endpoint='/indices', methods=['GET','POST'])
@login_is_required
def indices():
    if fetch_subscription() =="active":  
        global all_indices
        if request.method=="POST":
            # print(request.form)
            session['selected_index'] = (request.form['index_name'])
            session['selected_date'] = (request.form['date'])

            return redirect(url_for('/indices'))
        else:
            company_list = ta_values.query.filter_by(Index_Name=session['selected_index'], Date=session['selected_date']).all()

            return render_template('indices.html', company_list=company_list,indices=all_indices, selected_index=session['selected_index'], selected_date=session['selected_date'], name=session['name'], email=session['email'])

    else:
        return render_template("subscription/payment.html", name=session['name'], email=session['email'])

@app.route("/profile", endpoint='/profile')
@login_is_required
def profile():
    email=session['email']
    if fetch_subscription() =="active":     
        
        try:
            # customer = stripe.Customer.search(query="email:'satyajitdebnath87@gmail.com'")
            # customer = stripe.Customer.retrieve("cus_M9aq9IgKFkS7aK")

            customer= stripe.Customer.list(email=email)
            # print(customer)

            customer = customer['data'][0]
            # print("a", customer)

            customer_id = customer['id']
            get_sub = stripe.Subscription.list(customer=customer_id)
            get_sub = get_sub['data'][0]
            print(get_sub)

            customer_details = {
                "city": customer['address']['city'],
                "country": customer['address']['country'],
                "address1": customer['address']['line1'],
                "postal_code": customer['address']['postal_code'],
                "state": customer['address']['state'],
            } 

            sub_start = datetime.fromtimestamp(get_sub['current_period_start']).strftime('%d-%m-%y')
            sub_end = datetime.fromtimestamp(get_sub['current_period_end']).strftime('%d-%m-%y')

            subscription_details = {
                "sub_start" : sub_start,
                "sub_end" : sub_end,
                "sub_id": get_sub['id'],
                "product_id": get_sub['plan']['product'],
                "product_status": get_sub['status'],
                "invoice_id": get_sub['latest_invoice']
            }
            print(subscription_details)
            
                
            return render_template('profile.html',customer=customer_details, subscription=subscription_details, name=session['name'], email=email)

        except:
            customer_details = {
            "city": "",
            "country": "",
            "address1": "",
            "postal_code": "",
            "state": "",
            }

            subscription_details = {
                "sub_start" : "",
                "sub_end" : "",
                "sub_id": "",
                "product_id": "",
                "product_status": "",
                "invoice_id": ""
            }

            return render_template('profile.html',customer=customer_details, subscription=subscription_details, name=session['name'], email=session['email'])


@app.route("/payment", endpoint='/payment')
@login_is_required
def payment():
    return render_template('subscription/payment.html', name=session['name'], email=session['email'])


if __name__ == '__main__':
    app.run(debug=True)