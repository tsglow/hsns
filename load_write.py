import operator
import pandas as pd
import re
import datetime
from datetime import date
from operator import itemgetter


def load_db_tolist(args):     
    from_csv = pd.read_csv(f'{args}.csv')    
    loaded_db = from_csv.search_word.to_list()
    return loaded_db

def load_db_todict(args):     
    from_csv = pd.read_csv(f'{args}.csv')    
    loaded_db = from_csv.to_dict('records')
    return loaded_db        

def write_todb(args,filename):
    make_df = pd.DataFrame(args)
    make_df.to_csv(f'{filename}.csv', index = False)    

def append_todb(args,filename):
    make_df = pd.DataFrame(args)
    make_df.to_csv(f'{filename}.csv', mode = "a", header = None, index = False)   