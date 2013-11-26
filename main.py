import xml.etree.ElementTree as ET
tree = ET.parse('corpus.xml')
root = tree.getroot()
#iterate through all the "thread" tags
for thread in root:
    subject = thread[0].text
    #iterate through all the "DOC" tags under the "thread" tags
    for email in thread.findall('.//DOC'):
        from_who = email[1]
        to_whom = email[2]
        email_subject = email[3]
        email_text = 
        
        for text in email.findall('.//Text/Sent'):