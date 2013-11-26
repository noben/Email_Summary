import xml.etree.ElementTree as ET
import sqlite3
import os
import subprocess
from sentiment.analysis import sentimentAnalysis

# Read XML files and parse it into memory
bc3_corpus_xml_doc = ET.parse('../bc3/corpus.xml')
bc3_annotation_xml_doc = ET.parse('../bc3/annotation.xml')
    
'''
TODO:give a similarity score for each sentence by comparing it with the email subject 
@author: Kevin Zhao
'''   
def get_subject_similarity(text):
    return 10
'''
Look bc3 corpus xml file into sqllite
@author: Kevin Zhao
'''
def load_bc3_corpus():
    #TODO:delete DB file in test setting
    os.remove("../bc3/bc3.db")
    # Load database file
    conn = sqlite3.connect('../bc3/bc3.db')
    # Get database cursor
    db_cursor = conn.cursor()
    # Create table
    db_cursor.execute('''CREATE TABLE thread
                 (id,subject)''')
    db_cursor.execute('''CREATE TABLE email
                 (id,thread_id,subject,
                 from_who,
                 to_whom,
                 cc)''')
    db_cursor.execute('''CREATE TABLE sentence
                 (id,email_id,text,length,similarity,extracted,sa_tag,sentiment)''')
#    db_cursor.execute('''CREATE TABLE sentence_summary
#                 (id,text,)''')
    
    
    # Get the root node in the xml file
    xml_root_node = bc3_corpus_xml_doc.getroot()
    #iterate through all the "thread_node" tags
    for thread_node in xml_root_node:
        subject = thread_node[0].text
        thread_list_no = thread_node[1].text
        # Insert a row of data in thread_node table
        db_cursor.execute("INSERT INTO thread VALUES (?,?)", (thread_list_no, subject))
        #iterate through all the "DOC" tags under the "thread_node" tags
        email_no = 0
        for email_node in thread_node.findall('.//DOC'):
            from_who = email_node[1].text
            to_whom = email_node[2].text
            email_subject = email_node[3].text
            #Insert a row of data in email_node table
            db_cursor.execute("INSERT INTO email VALUES (?,?,?,?,?,?)", (email_no, thread_list_no, email_subject, from_who, to_whom, ""))
            
            sentence_no = 0
            for sentence_node in email_node.findall('.//Text/Sent'):
                sentence_text = sentence_node.text
                sentiment_score = sentimentAnalysis(sentence_text)
                #Insert a row of data in sentence_node table
                db_cursor.execute("INSERT INTO sentence VALUES (?,?,?,?,?,?,?,?)", (sentence_no, email_no, sentence_text, len(sentence_text), get_subject_similarity(sentence_node.text), is_sentence_extracted(thread_list_no, email_no, sentence_no), "",sentiment_score))
                sentence_no = sentence_no + 1
                
            email_no = email_no + 1
            
        
    # Save (commit) the changes
    conn.commit()
    
    conn.close()
    
    
def get_thread_node_by_list_no(thread_list_no):
    # Get the root node in the xml file
    xml_root_node = bc3_annotation_xml_doc.getroot()
    # Get the unique thread_node through thread_list_no
    thread_node = bc3_annotation_xml_doc.findall(".//thread/[listno='" + thread_list_no + "']")
    
    return thread_node[0]

'''
if the sentence has been selected as one of the extractions by looking at annotation.xml
@author: Kevin Zhao
'''
def is_sentence_extracted(thread_list_no, email_id, sentence_id):
    thread_node = get_thread_node_by_list_no(thread_list_no)
    # construct sentence_id in the form of 1.2,1.3,1.4.....
    sentence_unque_id = str(email_id) + "." + str(sentence_id)
    # Find all the sent_node under the thread_node whose id is sentence_unque_id
    result_hits = thread_node.findall(".//annotation/sentences/sent[@id='" + sentence_unque_id + "']")
    
    return len(result_hits) != 0
#    
#def load_bc3_summary(thread_list_no):
#    # Load database file
#    conn = sqlite3.connect('../bc3/bc3.db')
#    # Get database cursor
#    db_cursor = conn.cursor()
#    
#    thread_node = get_thread_node_by_list_no(thread_list_no)
#    # Find all the sent_node under the thread_node whose id is sentence_unque_id
#    for sent_node in thread_node.findall('.//annotation/summary/sent'):
#        # Insert a row of data in summary table
#        db_cursor.execute("INSERT INTO summary VALUES (?,?)", (thread_no, subject))

'''
Run Speech act on email text and update sa_tag column in sentence table
@author: Kevin Zhao
'''
def load_generated_speech_act_tag():
    subprocess.call(['java', '-jar', '../libs/speech_act.jar', '../bc3/bc3.db'])
    
def main():
    print "Loading BC3 Corpus.....It may take couple of seconds"
    load_bc3_corpus()
##    load_bc3_summary()
    print "Loading generated speech act tag....."
    load_generated_speech_act_tag()
    
if __name__ == "__main__":
    main()
