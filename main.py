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
import web
import sql
import sqlite3
from sql import index #needed to make the webapp work, ignore spyder
import manual_edit
            
def start_log(): #infinite loop, runs main() every minute
    tmin = time.gmtime()[4]
    while True:
        if time.gmtime()[4] != tmin:
            add_new_reports(manual_edit.indiv_report())
            main()
            start_log()          

def add_new_reports(new_reports):
    for n in new_reports:
        try:
            new_rep = n.split(" ")
            new_rep[3] = new_rep[4].split("-")
            new_rep[3] = [int(new_rep[3][d] for d in range(3))] #convert date to integers
            if new_rep[3][2].find("\n") != -1:
                new_rep[3][2].split("\n")
            print(new_rep)
            write_report(new_rep)
            determine_dict(new_rep)            
        except:
            print("The report '" + n + "' was not compatible. Please recheck the spacings on it")
            
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
    print("New message to log")
    for line in new_messages: 
        if is_copied(line.Body)[0]:
            customization.open_files() #allows dynamic change of mod lists
            find_handle(line,LIST,is_copied(line.Body)[1])   

def is_copied(message): #checks for the copy syntaxing - triple-checked, needs mac checking
    if len(message) >= 14:
        if (message[0] == "[" and message.find("]",6,13) != -1 and (message[3] == ":" or message[2] == ":")): #PC test
            return [True,False]
        elif message[0:2] == "On" and (message[4] == "/" or message[5] == "/") and message.find(",",9,12) != -1: #mac test
            return [True,True]
    return [False,False] #[is_copied,is_a_mac]

def find_handle(Chat,LIST,mac): #generate info to create a report
    message = Chat.Body
    if mac:
        IGN = message[message.find("\r\n")+4:message.rfind("\r\n")-1]
        verdict = message[message.rfind("\r\n")+2:]
        Fname = message[message.find(",",10)+2:message.rfind(" ",1,message.find(":",16))]
    else:
        IGN = message[message.find(":",8)+2:message.find("\r\n\r\n")]
        verdict = message[message.rfind("<<<")+4:]
        Fname = message[message.find("]")+2:message.find(":",message.find("]")+2)] #to triple check report
#uncomment following 2 lines, fix the latter
#    while verdict == "": #check
#        verdict = Running_list[Running_list[Chat.Topic].index(Chat)+1].Body
    for ch in LIST:
        if ch.Body.find(IGN) != -1 and not is_copied(ch.Body)[0]: #IGN loction that isn't the verdict
        #If there is a guy with the same name, take his handle. If not, take all handles where needed
            if ch.Sender.FullName == Fname: 
                create_report(ch.Sender.FullName,IGN,verdict,ch,Chat)
            else: #check if proper indentation/improvement
                for new_ch in LIST:
                    if new_ch.Body.find(IGN) != -1:
                        if not is_copied(new_ch.Body):             
                            create_report(ch.Sender.Fullname,IGN,verdict,ch,Chat)
                            #differentiate between mod and player ch/Chat
                       
def create_report(Reporter,IGN,verdict,ch,Chat): #create report to log    
    old_report_info = "" #to remove duplicates
    for mod in mods:
        if Chat.Sender.Handle == mod:
            date = [ch.Datetime.year,ch.Datetime.month,ch.Datetime.day]
            report_info = [ch.Sender.Handle,IGN,verdict.lower(),Chat.Sender.Handle]
            Info = report_info + [date] #date should be its own list inside of info
            if report_info != old_report_info:                
                old_report_info = report_info
                write_report(Info)
                determine_dict(Info) #check if should be indented
            
def write_report(report): #allows you to start the process, then terminate and restart it (i.e. update) without anything (or much)
    print("Writing report to local record")
    my_reports.append(report)
    b = open("reports_record.txt","r+")
    b.readlines()
    b.write('\n'+str(report[0])+"\t"+str(report[1])+"\t"+str(report[2])+"\t"+str(report[4][2])+"-"+str(report[4][1])+"-"+str(report[4][0]))
    b.close()

def determine_dict(report):
    add_to_dict(all_time_reports,report)
#    ddif = (datetime.date(report[3][2],report[3][1],report[3][0]) - datetime.date.today()).days
#    if ddif < 0:
#        ddif *= -1 #idk why it does that...
#    if ddif == 1:
#        add_to_dict(current_day_reports,report)
#    if ddif <= 7:
#        add_to_dict(this_week_reports,report)
#    if ddif <= 30:
#        add_to_dict(last_month_reports,report)
        
def add_to_dict(dictionary,report):
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
    print("Updating SQLite3 database")
    if table_dict == all_time_reports: #to allow for different tables
        table = "all_time"
    else:
        table = "all_time"
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
all_time_reports = {} #place to store all reports; #records: {Reporter_skype_handle: [bans, clean, reports], ... }; will need to change
last_month_reports = {} #same as all_time, but only past 30 days
this_week_reports = {} #same as all_time, but only past 7 days
current_day_reports = {} #same as all_time, but only today
Running_list = {} #the growing list for the chats, key is "u'<Topic>'"
chat_list = [] #to know which chats are being logged
total_records = [] #[[<reporter>, <IGN>, <verdict>, [dd,mm,yyy]], ... ]
name_list = [] #to get the id for updating the database
mods = customization.mods_of_HRC
bans = customization.ban_verdicts
cleans=customization.clean_verdicts

#setup the database
web.config.debug = True
sql.try_table()
my_reports = []
#load old reports
old_list = manual_edit.open_reports()
for old_report in old_list:
    old_report[2] = old_report[2].lower()
    determine_dict(old_report)
 
#create Running_list to compare Handles with
for b in skype.BookmarkedChats:
    if b.Topic[0:3] == "HRC": 
        chat_list.append(str(b.Topic))
        Running_list[b.Topic] = list(b.Messages) #used to find the IGN

print("Logging the reports from " + ', '.join(chat_list))

start_log() #start!