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
    db_cursor.execute('''CREATE TABLE IF NOT EXISTS thread
                 (id,subject)''')
    db_cursor.execute('''CREATE TABLE IF NOT EXISTS email
                 (id,thread_id,subject,
                 from_who,
                 to_whom,
                 cc,num_replies)''')
    db_cursor.execute('''CREATE TABLE IF NOT EXISTS sentence
                 (id,email_id,thread_id,text,length,similarity,extracted,sa_tag,sentiment)''')
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
        email_no = 1
        for email_node in thread_node.findall('.//DOC'):
            from_who = email_node[1].text
            to_whom = email_node[2].text
            email_subject = email_node[3].text
            number_of_replies = 0
            # get number of replies
            for email_node_for_num_replies in thread_node.findall('.//DOC'):
                to_whom_for_num_replies = email_node_for_num_replies[2].text
                if to_whom_for_num_replies is None:
                    continue
                try:
                    if from_who in to_whom_for_num_replies:
                        number_of_replies=number_of_replies+1;
                except TypeError as e:
                        print e
            #Insert a row of data in email_node table
            db_cursor.execute("INSERT INTO email VALUES (?,?,?,?,?,?,?)", (email_no, thread_list_no, email_subject, from_who, to_whom, "",number_of_replies))
            
            sentence_no = 1
            for sentence_node in email_node.findall('.//Text/Sent'):
                sentence_text = sentence_node.text
                sentiment_score = sentimentAnalysis(sentence_text)
                #Insert a row of data in sentence_node table
                db_cursor.execute("INSERT INTO sentence VALUES (?,?,?,?,?,?,?,?,?)", (sentence_no, email_no, thread_list_no, sentence_text, len(sentence_text), get_subject_similarity(sentence_node.text), is_sentence_extracted(thread_list_no, email_no, sentence_no), "", sentiment_score))
                sentence_no = sentence_no + 1
                
            email_no = email_no + 1
            
        
    # Save (commit) the changes
    conn.commit()
    
    conn.close()
    
    
def get_thread_node_by_list_no_from_xml(thread_list_no):
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
    thread_node = get_thread_node_by_list_no_from_xml(thread_list_no)
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
#    thread_node = get_thread_node_by_list_no_from_xml(thread_list_no)
#    # Find all the sent_node under the thread_node whose id is sentence_unque_id
#    for sent_node in thread_node.findall('.//annotation/summary/sent'):
#        # Insert a row of data in summary table
#        db_cursor.execute("INSERT INTO summary VALUES (?,?)", (thread_no, subject))

def feature_extraction():
    # Load database file
    conn = sqlite3.connect('../bc3/bc3.db')
    # Get database cursor
    sentence_db_cursor = conn.cursor()
    # Create table
    sentence_db_cursor.execute('''CREATE TABLE IF NOT EXISTS feature 
                 (sentence_id,email_id,thread_id,extracted ,f_length ,
                 f_sentiment ,f_thread_line_number ,f_relative_thread_line_num,
                 f_centroid_similarity,f_local_centroid_similarity,f_tfidf_sum,
                 f_tfidf_avg,f_email_number,f_relative_email_number,f_subject_similarity,
                 f_reply_number,f_recipients_number,f_sa_tag)''')
    
    #get data from sentence table for feature extraction
    sentence_id = ""
    email_id = ""
    thread_id = ""
    sentence_text = ""
    f_sentence_length = ""
    f_sentence_subject_similarity = ""
    sentence_extracted = ""
    f_sentence_sa_tag = ""
    f_sentence_sentiment = ""
    
    sentence_db_cursor = conn.execute("SELECT *  from sentence")
    
    feature_db_insert_cursor= conn.cursor()
    for row in sentence_db_cursor:
        sentence_id = row[0]
        email_id = row[1]
        thread_id = row[2]
        sentence_text = row[3]
        f_sentence_length = row[4]
        f_sentence_subject_similarity = row[5]
        sentence_extracted = row[6]
        f_sentence_sa_tag = row[7]
        f_sentence_sentiment = row[8]
        #TODO : features to be extracted
        f_sentence_thread_line_number = "" #TODO:
        f_sentence_relative_thread_line_num = "" #TODO:sentenceid/sum(all the sentences in a thread)
        f_sentence_centroid_similarity=""
        f_sentence_local_centroid_similarity=""
        f_sentence_tfidf_sum=""
        f_sentence_tfidf_avg=""
        f_sentence_email_number=""
        f_sentence_relative_email_number=""
        
        #get number of replies
        email_db_cursor = conn.execute("SELECT num_replies from email where id =? and thread_id = ?",(email_id,thread_id))
        for row_in_email_table in email_db_cursor:
            f_sentence_reply_number=row_in_email_table[0]
        #get number of recipients
        f_sentence_recipients_number=""
        #insert feature data into database
        feature_db_insert_cursor.execute("INSERT INTO feature VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", (sentence_id,email_id,thread_id,sentence_extracted,f_sentence_length,f_sentence_sentiment,f_sentence_thread_line_number,f_sentence_relative_thread_line_num,f_sentence_centroid_similarity,f_sentence_local_centroid_similarity,f_sentence_tfidf_sum,f_sentence_tfidf_avg,f_sentence_email_number,f_sentence_relative_email_number,f_sentence_subject_similarity,f_sentence_reply_number,f_sentence_recipients_number,f_sentence_sa_tag))
   
    # Save (commit) the changes
    conn.commit()
    
    conn.close()
   
   
'''
Run Speech act on email text and update sa_tag column in sentence table
@author: Kevin Zhao
'''
def load_generated_speech_act_tag():
    subprocess.call(['java', '-jar', '../libs/speech_act.jar', '../bc3/bc3.db'])
    
def main():
    print "1.Pre-processing"
    print "Loading BC3 Corpus.....It may take couple of seconds"
#    load_bc3_corpus()
    print "Loading generated speech act tag....."
#    load_generated_speech_act_tag()
    
    print "2.Feature extraction..."
    feature_extraction()
    
    print "Done!"
    
if __name__ == "__main__":
    main()
