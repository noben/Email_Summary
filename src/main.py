import xml.etree.ElementTree as ET
import sqlite3
import os

def get_subject_similarity(text):
    return 10

#delete DB file in testing
os.remove("../bc3/bc3.db")

conn = sqlite3.connect('../bc3/bc3.db')
c = conn.cursor()
# Create table
c.execute('''CREATE TABLE thread
             (id,subject)''')
c.execute('''CREATE TABLE email
             (id,thread_id,subject,
             from_who,
             to_whom,
             cc,sa_tag)''')
c.execute('''CREATE TABLE sentence
             (id,email_id,text,length,similarity)''')


tree = ET.parse('../bc3/corpus.xml')
root = tree.getroot()
#iterate through all the "thread" tags
thread_no = 0
for thread in root:
    subject = thread[0].text
    # Insert a row of data in thread table
    c.execute("INSERT INTO thread VALUES (?,?)", (thread_no, subject))
    #iterate through all the "DOC" tags under the "thread" tags
    email_no = 0
    for email in thread.findall('.//DOC'):
        from_who = email[1].text
        to_whom = email[2].text
        email_subject = email[3].text
        #Insert a row of data in email table
        c.execute("INSERT INTO email VALUES (?,?,?,?,?,?,?)", (email_no, thread_no, email_subject, from_who, to_whom,"", ""))
        
        sentence_no = 0
        for sentence in email.findall('.//Text/Sent'):
            #Insert a row of data in sentence table
            c.execute("INSERT INTO sentence VALUES (?,?,?,?,?)", (sentence_no, email_no, sentence.text, len(sentence.text), get_subject_similarity(sentence.text)))
            sentence_no = sentence_no + 1
            
        email_no = email_no + 1
        
    thread_no = thread_no + 1
    
# Save (commit) the changes
conn.commit()

conn.close()
