import requests
import operator
import pandas as pd
import re
import datetime
from datetime import date
from bs4 import BeautifulSoup
from flask import Flask, render_template, request
from operator import itemgetter

from_filter_csv = pd.read_csv('filter.csv')
filter_db = from_filter_csv.to_dict('records')

print(filter_db)