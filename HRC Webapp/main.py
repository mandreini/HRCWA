"""
Created on July, 2014
@author: ma56nin9 / Matt
Contact: ma56nin@hotmail.com
"""

try:
    import Skype4Py
except: 
    print("Skype4Py not able to import, check installation") 
    exit
import customization
import time   
import datetime
import sqlite3
import sql
import manual_edit
import features
            
def start_log(): #infinite loop, runs main() every minute
    t = time.gmtime()
    while True:
        if time.gmtime()[4] != t[4]:
            add_new_reports(manual_edit.indiv_report())
            main()
            start_log()
        if time.gmtime()[1] != t[2]:
            pass
            #refresh month database
            #update player/mod activity log
        if time.gmtime()[3] != t[3]:
            pass
            #refresh day and week database

def add_new_reports(new_reports):
    #input: list of strings directly inputted ("Reporter IGN verdict day-month-year")
    for n in new_reports:
        try:
            n = n.strip("\n")
            n = n.strip(" ")
            today = datetime.datetime.today()
            date = [today.year, today.month, today.day]
            new_rep = n.split(" ")
            new_rep += [date, "Unknown"]
            write_report(new_rep)
            determine_dict(new_rep)
            print("Report added successfully!")            
        except:
            print("The report '" + n + "' was not compatible. Please recheck the syntaxing")
            
def main(): #extract the skype logs
    for c in skype.BookmarkedChats:
        msg_list = []
        if c.Topic[0:3] == "HRC": # if c.Topic[0:6] == "HRC Pi": #loop through only HRC chats
            msg_list = list(c.Messages) #loop through msg_list, add everything after the last (first) message in Running_list
            new_messages = msg_list[:msg_list.index(Running_list[c.Topic][0])]
            if new_messages: #if new_messages is not a NoneType
                Running_list[c.Topic] = new_messages + Running_list[c.Topic]
                log(new_messages,Running_list[c.Topic]) #reverse of new_messages not needed

def log(new_messages,LIST): #log the report
    #input: new_messages = [<SkypeMessage1>,...]; LIST = All messages of Running_list for the chat
    print("New message to log")
    for line in new_messages: 
        msg = line.Body.encode("utf-8")
        print msg
        if is_copied(msg)[0]:
            mods,bans,cleans = customization.open_files() #allows dynamic change of mod lists
            find_handle(line,LIST,is_copied(msg)[1])   

def is_copied(message): #checks for the copy syntaxing - triple-checked, needs mac checking
    #message: <SkypeMesage>
    if len(message) >= 14:
        if (message[0] == "[" and message.find("]",6,13) != -1 and (message[3] == ":" or message[2] == ":")): #PC test
            return [True,False]
        elif message[0:2] == "On" and (message[4] == "/" or message[5] == "/") and message.find(",",9,12) != -1: #mac test
            return [True,True]
    return [False,False] #[is_copied,is_a_mac]

def find_handle(Chat,LIST,mac): #generate info to create a report
    #inputs: Chat: <Skypechatobject>, LIST: list of all messages for chat, mac: boolean: is a mac quote (if True)
    message = Chat.Body.encode("utf-8")
    if mac:
        IGN = message[message.find("\r\n")+4:message.rfind("\r\n")-1]
        verdict = message[message.rfind("\r\n")+2:]
        Fname = message[message.find(",",10)+2:message.rfind(" ",1,message.find(":",16))]
    else:
        IGN = message[message.find(":",8)+2:message.find("\r\n\r\n")]
        verdict = message[message.rfind("<<<")+4:]
        Fname = message[message.find("]")+2:message.find(":",message.find("]")+2)] #to triple check report
    
    print "finding handle for " + Fname + "'s report of " + IGN
    
    for ch in LIST[:50]: #won't go 50 messages back!
        if ch.Body.encode("utf-8").find(IGN) != -1 and not is_copied(ch.Body.encode("utf-8"))[0]: #IGN loction that isn't the verdict
        #If there is a guy with the same name, take his handle. If not, take all handles where needed
            if ch.Sender.FullName == Fname: 
                create_report(ch.Sender.FullName,IGN,verdict,ch,Chat)
            else: #check if proper indentation/improvement
                for new_ch in LIST[:50]:
                    if new_ch.Body.find(IGN) != -1:
                        if not is_copied(new_ch.Body.encode("utf-8")):             
                            create_report(ch.Sender.Fullname,IGN,verdict,ch,Chat)
                            #differentiate between mod and player ch/Chat
                       
def create_report(Reporter,IGN,verdict,ch,Chat): #create report to log    
    #string, string, string, chatmessage of mod-who-banned, chatmessage of reporter
    print "creating report for " + Reporter + "'s report of " + IGN
    print "report created by " + Chat.Sender.Handle
    onSdb = features.get_oldSkype_newSkype("oldnewskype_layover.txt") #oldnewSkypedatabase
    Reporter = features.check_for_new(Reporter,onSdb) #Reporter will be current skype 
    old_report_info = "" #to remove duplicates
    if Chat.Sender.Handle in mods:
        date = [ch.Datetime.year,ch.Datetime.month,ch.Datetime.day]
        report_info = [ch.Sender.Handle,IGN,verdict.lower(),"*",Chat.Sender.Handle]
        Info = report_info; Info[3] = date #date should be its own list inside of info
        total_records.append(Info)
        if report_info != old_report_info:                
            old_report_info = report_info
            write_report(Info)
            determine_dict(Info)
                
            
def write_report(report): #allows you to start the process, then terminate and restart it (i.e. update) without anything (or much)
    #input report: [<reporter>, <IGN>, <verdict>, <date in [yyyy,mm,dd]>, <mod-who-banned>]
    print "writing report"
    my_reports.append(report)
    b = open("reports_record.dat","r+")
    b.readlines()
    b.write('\n'+str(report[0])+"\t"+str(report[1])+"\t"+str(report[2])+"\t"+str(report[3][2])+"-"+str(report[3][1])+"-"+str(report[3][0])+"\t"+report[4])
    b.close()

def determine_dict(report):
    print "determining dictionary"
    #same as write_report()'s
    add_to_dict(all_time_reports,report)
    ddif = (datetime.date(report[3][0],report[3][1],report[3][2]) - datetime.date.today()).days
    if ddif < 0:
        ddif *= -1 #idk why it does that...
    if ddif == 0:
        add_to_dict(current_day_reports,report)
    if ddif <= 7:
        add_to_dict(this_week_reports,report)
    if ddif <= 30:
        add_to_dict(last_month_reports,report)
        
def add_to_dict(dictionary,report):
    #inputs: dictionary - which dictionary to add, find out report
    print("Adding to dictionary for SQLite3 database")
    if not dictionary.has_key(report[0]):
        dictionary[report[0]] = [0,0,0]
    dictionary[report[0]][2] += 1
    if report[2].find("autobanned") != -1:
        pass #don't confuse autoban with ban!
    else:
        for ban in bans:
            if report[2].find(ban) != -1:
                dictionary[report[0]][0] += 1
                update_database(dictionary,report[0],"Ban")          
                return
        for clean in cleans:
            if report[2].find(clean) != -1:
                dictionary[report[0]][1] += 1
                update_database(dictionary,report[0],"Clean")
                return
                
def update_database(table_dict,rep_name,verdict): #add the report to the database
    #table_dict: which database to update, string, string
    if table_dict["name"] == sql.tables[0]: #to allow for different tables
        table = sql.tables[0]
    elif table_dict["name"] == sql.tables[1]:
        table = sql.tables[1]
    elif table_dict["name"] == sql.tables[2]:
        table = sql.tables[2]
    elif table_dict["name"] == sql.tables[3]:
        table = sql.tables[3]
    
    conn = sqlite3.connect("HRC_records.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM " + table + " WHERE Reporter = ?",(rep_name,))
    data = cursor.fetchall()
    if len(data) == 0: #if the reporter is not in the database, add him.
        sql.db.insert(table,Reporter=rep_name,Ban=0,Clean=0,Accuracy="0.0",Total=0)
    conn.execute("UPDATE " + table + " SET " + verdict + " = " + verdict + " + 1 WHERE Reporter = '" + rep_name + "';")
    if table_dict[rep_name][0] == 0 and table_dict[rep_name][1] == 0:
        new_acc = 0.
    else:
        new_acc = int((float(table_dict[rep_name][0]) / float(table_dict[rep_name][0] + table_dict[rep_name][1]))*100.)
    conn.execute("UPDATE " + table + " SET Accuracy = " + str(new_acc) + " WHERE Reporter = '" + rep_name + "';")
    conn.commit()
    conn.close()    
    
#initialize Skype4Py
skype = Skype4Py.Skype()
skype.FriendlyName = 'Extract_chat_history'
skype.Attach()
print("Successfully connected to Skype account '" + Skype4Py.Skype.User(skype).Handle + "'.")

#set up report structure
all_time_reports = {"name": sql.tables[0]} #place to store all reports; #records: {Reporter_skype_handle: [bans, clean, reports], ... }; will need to change
last_month_reports = {"name": sql.tables[1]} #same as all_time, but only past 30 days
this_week_reports = {"name": sql.tables[2]} #same as all_time, but only past 7 days
current_day_reports = {"name": sql.tables[3]} #same as all_time, but only today
Running_list = {} #the growing list for the chats, key is "u'<Topic>'"
chat_list = [] #to know which chats are being logged
total_records = [] #[[<reporter>, <IGN>, <verdict>, <mod_who_banned>, [dd,mm,yyy]], ... ]
name_list = [] #to get the id for updating the database
mods, bans, cleans = customization.open_files()

#setup the database
for t in sql.tables:
    sql.try_table(t)
my_reports = []

#load old reports
old_list = manual_edit.open_reports()
for old_report in old_list:
    old_report[2] = old_report[2].lower()
    determine_dict(old_report)
 
#create Running_list to compare Handles with and name_list for activity tracking
for b in skype.BookmarkedChats:
    if b.Topic[0:3] == "HRC": 
        chat_list.append(str(b.Topic))
        Running_list[b.Topic] = list(b.Messages) #used to find the IGN
        name_list.append([str(b.Topic)] + list(b.Members))
        
print("Logging the reports from " + ', '.join(chat_list))

start_log() #start!