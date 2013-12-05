#   Author Luming
#   converting standard email input to XML file
#   important: to use this piece of code, the NLTK library is required to be installed
import os
import nltk
import re
import nltk.data
#   the libs imported below are used for parsing emails with standard format
import rfc822, StringIO
import xml.etree.cElementTree as ET

#   set the destiny path of output file as below
path_to_formatted_files = "/Users/nieluming/Desktop/NLP_luming_final_version/Email_Summary/formatted_email_input/formatted_thread.xml"

#   A good english sentence tokenizer based on punkt/english.pickle in nltk
sent_tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')


#   build up the structure of the xml tree
root = ET.Element("root")
thread = ET.SubElement(root, "thread")
name = ET.SubElement(thread, "name")
listno = ET.SubElement(thread, "listno")
DOC = ET.SubElement(thread, "DOC")
From = ET.SubElement(DOC, "From")
To = ET.SubElement(DOC, "To")
Cc = ET.SubElement(DOC, "Cc")
Subject = ET.SubElement(DOC, "Subject")
Text = ET.SubElement(DOC, "Text")


#   function for parsing a single email
#   first step: parse the standard email from raw input - <header>, <subject>, <to_whom>, <Cc>, <from_who> etc.
#   here assume the path_to_raw_email is as below, and it should be changed in real time operating
path_to_raw_email = "./raw_email_input/standard_email_format_test.txt"

def parse_raw_email(path_to_raw_email):
    with open (path_to_raw_email, "r") as email:
        data=email.read()

    email_as_string = StringIO.StringIO(data)
    message = rfc822.Message(email_as_string)
    
    #   assign values to the right tag
    for (k,v) in message.items():

        if k == 'from':
            print '------------------------------------------------'
            To.text = v
        elif k == 'to':
            print '------------------------------------------------'
            From.text = v
        elif k == 'subject':
            print '------------------------------------------------'
            Subject.text = v
        elif k == 'cc':
            print '------------------------------------------------'
            Cc.text = v
            
        print "The information of email being parsing is <%s>%s</%s>" % (k,v,k)

    email_body = email_as_string.read()

    #   splited_sent is a list of strings of sentences
    splited_sent = sent_tokenizer.tokenize(email_body)
    #   
    for sent in splited_sent:
        
        Sent = ET.SubElement(Text, "Sent")
        Sent.set('id', 'None')
        Sent.text = sent
        
#   write the file as an xml file to the "formatted_email_input" file
    tree = ET.ElementTree(root)
    tree.write(path_to_formatted_files)


if __name__ == "__main__":
    parse_raw_email(path_to_raw_email)











