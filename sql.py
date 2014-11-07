import sqlite3
import web
        
class index:
    def GET(self):
        reports = db.select('all_time')
        return render.index(reports)
        
class contact:
    def GET(self):
        return

def close_table():
    conn = sqlite3.connect("HRC_records.db")
    conn.execute("DROP TABLE all_time");
    conn.close()
    return
    
def create_table():   
    conn = sqlite3.connect("HRC_records.db")
    conn.execute('''CREATE TABLE all_time  
       (id integer primary key,
         Reporter text,
         Ban integer,
         Clean integer,
         Accuracy text,
         Total integer,
         created timestamp DEFAULT current_timestamp);''')
    
    conn.close()
    return

def try_table():
    try:
        create_table()
    except sqlite3.OperationalError:
        print "Refreshing table"
        close_table()
        create_table()
        #change to update table or something
        
render = web.template.render('templates/',base='base')
db = web.database(dbn='sqlite', db='HRC_records.db')
urls = (
    '/', 'index', 
    '/', 'contact',)
