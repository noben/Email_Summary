import xml.etree.ElementTree as ET
import sqlite3
import os
import subprocess
from sentiment.analysis import sentimentAnalysis
#   regular expression is used to convert sentences into words list -- calculate tf-idf
import re
#   Counter is used to calculate the frequency of a word in threads and emails
from collections import Counter
import math

#   NLTK tools for feature extracting
#   import nltk

#   Read XML files and parse it into memory
bc3_corpus_xml_doc = ET.parse('../bc3/corpus.xml')
bc3_annotation_xml_doc = ET.parse('../bc3/annotation.xml')
    
'''
TODO:give a similarity score for each sentence by comparing it with the email subject 
@author: Kevin Zhao
'''  
#   undone 
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
                 cc, num_replies)''')
    db_cursor.execute('''CREATE TABLE IF NOT EXISTS sentence
                 (id,email_id,thread_id,text,length,similarity,extracted,sa_tag,sentiment,position, sentence_tfidf_sum, sentence_tfidf_avg)''')
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
        
        #shouldn't email_no starts from '1' ?
        email_no = 1
        #total sentences number for calculating the thread line number 
        total_sentence_position = 1
        
        # convert the thread_words_list to a "list of list of words" in which every sub-list is an email
        # calculate sum tf-idf and average tf-idf of every sentence
        # below thread_words_list is a list of lists in which every email is a list of words:
        thread_words_list = []
        for email_node in thread_node.findall('.//DOC'):
            email_words_list = []
            for sentence_node in email_node.findall('.//Text/Sent'):
                string = sentence_node.text
                wordList = re.sub("[^\w]", " ",  string).split()
                for word in wordList:
                    email_words_list.append(word)
            thread_words_list.append(email_words_list)
        # now thread_words_list is composed of all emails with every email as a sub-list -- to be used for idf
        # below is the total number of emails in a thread:
        total_no_emails_thread = len(thread_words_list)
        
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
            db_cursor.execute("INSERT INTO email VALUES (?,?,?,?,?,?,?)", (email_no, thread_list_no, email_subject, from_who, to_whom, "", number_of_replies))

            # shouldn't sentence_no starts from '1' ?
            sentence_no = 1
            
            # convert the email_words_list to a set of words (list type)
            # calculate words list of an email for calculating tf value of a word
            # here sentence_node.text is an u'string'
            email_words_list = []
            for sentence_node in email_node.findall('.//Text/Sent'):
                string = sentence_node.text
                wordList = re.sub("[^\w]", " ",  string).split()
                for word in wordList:
                    email_words_list.append(word)
            # now email_words_list is composed of all words in the email -- to be used for tf
            # below is the word frequency dictionary in an email:
            word_freq_email_dict = Counter(email_words_list)
            total_no_words_email = len(email_words_list)
                
            for sentence_node in email_node.findall('.//Text/Sent'):
                sentence_text = sentence_node.text
                sentiment_score = sentimentAnalysis(sentence_text)
                
                # calculate the "sum tf-idf" and "avg tf-idf" value of a sentence here:
                sentence_words_list = re.sub("[^\w]", " ",  sentence_text).split()
                sentence_len = len(sentence_words_list)
                
                sentence_tfidf_sum = 0
                for word in sentence_words_list:
                    tf_word = word_freq_email_dict[word]/total_no_words_email
                    # count the number of emails containing "word" in the thread:
                    no_emails_with_word = 0
                    for email in thread_words_list:
                        if word in email:
                            no_emails_with_word = no_emails_with_word + 1
                    idf_word = math.log(total_no_emails_thread/no_emails_with_word)
                    
                    sentence_tfidf_sum = sentence_tfidf_sum + tf_word*idf_word
                
                sentence_tfidf_avg = sentence_tfidf_sum/(sentence_len+1)

                # Insert a row of data in sentence_node table, Luming added: "total_sentence_no"
                db_cursor.execute("INSERT INTO sentence VALUES (?,?,?,?,?,?,?,?,?,?,?,?)", (sentence_no, email_no, thread_list_no, sentence_text, len(sentence_text), get_subject_similarity(sentence_node.text), is_sentence_extracted(thread_list_no, email_no, sentence_no), "", sentiment_score, total_sentence_position, sentence_tfidf_sum, sentence_tfidf_avg))
                sentence_no = sentence_no + 1
                #total sentence number
                total_sentence_position = total_sentence_position + 1
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


#   define the txt file open function here
#   NLTK methods for extracting
#   this function could be put into feature extraction file


def feature_extraction():
    # Load database file
    conn = sqlite3.connect('../bc3/bc3.db')
    # Get database cursor
    db_cursor = conn.cursor()
    # Create table
    db_cursor.execute('''CREATE TABLE IF NOT EXISTS feature 
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
    
    db_cursor = conn.execute("SELECT *  FROM sentence")
    db_insert_cursor= conn.cursor()
    for row in db_cursor:
        sentence_id = row[0]
        email_id = row[1]
        thread_id = row[2]
        
        #get the total number of sentences in an email:
        total_sentence_no = conn.execute("SELECT MAX(position) FROM sentence WHERE thread_id=?", [thread_id])
        total_sentence_no = total_sentence_no.fetchone()[0]
        #get the total number of emails in a thread:
        total_email_no = conn.execute("SELECT MAX(email_id) FROM sentence WHERE thread_id=?", [thread_id])
        total_email_no = total_email_no.fetchone()[0]
        sentence_text = row[3]
        f_sentence_length = row[4]
        f_sentence_subject_similarity = row[5]
        sentence_extracted = row[6]
        f_sentence_sa_tag = row[7]
        f_sentence_sentiment = row[8]
        #TODO : features to be extracted
        f_sentence_thread_line_number = row[9]   #sentence position in whole thread            #luming
        f_sentence_relative_thread_line_num = f_sentence_thread_line_number/total_sentence_no  #luming
        f_sentence_centroid_similarity= ""
        f_sentence_local_centroid_similarity=""
        f_sentence_tfidf_sum = row[10]                                                         #luming
        f_sentence_tfidf_avg = row[11]                                                         #luming
        f_sentence_email_number = email_id               #=email ID                            #luming
        f_sentence_relative_email_number = email_id/total_email_no    #email ID/sum of email   #luming
        
        #get number of replies                                                                 #done by Yuan
        email_db_cursor = conn.execute("SELECT num_replies from email where id =? and thread_id = ?",(email_id,thread_id))
        for row_in_email_table in email_db_cursor:
            f_sentence_reply_number=row_in_email_table[0]
        f_sentence_recipients_number=""                                                        #to be done by Yuan
        #insert feature data into database
        db_insert_cursor.execute("INSERT INTO feature VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", (sentence_id,email_id,thread_id,sentence_extracted,f_sentence_length,f_sentence_sentiment,f_sentence_thread_line_number,f_sentence_relative_thread_line_num,f_sentence_centroid_similarity,f_sentence_local_centroid_similarity,f_sentence_tfidf_sum,f_sentence_tfidf_avg,f_sentence_email_number,f_sentence_relative_email_number,f_sentence_subject_similarity,f_sentence_reply_number,f_sentence_recipients_number,f_sentence_sa_tag))
   
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
    load_bc3_corpus()
    print "Loading generated speech act tag....."
    load_generated_speech_act_tag()
    
    print "2.Feature extraction..."
    feature_extraction()
    
if __name__ == "__main__":
    main()
