from flask import Flask, render_template, redirect
import datetime
from datetime import date
from scrapper import scrap,re_scrap, get_kisa_status
from load_write import append_todb, load_db_todict, load_db_tolist, write_todb


app = Flask("hsns")

@ app.route("/")
def home():
    kisa_status = get_kisa_status()
    #repl.it 에 올릴 때만 : current_timef = datetime.datetime.now(timezone('Asia/Seoul')).strftime('%Y-%m-%d %H:%M:%S')
    sorted_scrapped_news = scrap()
    current_time = load_db_todict("scrap_time")    
    return render_template("home.html",  t_info=kisa_status, article=sorted_scrapped_news, count=len(sorted_scrapped_news), today=current_time)


@ app.route("/re_scrap")
def rescrap():
    re_scrap()
    return  redirect("/")




