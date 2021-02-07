from flask import Flask, render_template, redirect
from scrapper import scrap,re_scrap, get_kisa_status, current_time
from load_write import append_todb, load_db_todict, load_db_tolist, write_todb


app = Flask(__name__)

@ app.route("/")
def home():
    kisa_status = get_kisa_status()
    sorted_scrapped_news = scrap()    
    return render_template("home.html",  t_info=kisa_status, article=sorted_scrapped_news, count=len(sorted_scrapped_news), today=current_time)


@ app.route("/re_scrap")
def rescrap():
    re_scrap()
    return  redirect("/")