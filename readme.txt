Email_Summary
=============

Email Summary NLP project @ NYU

##########Functionality##########
(1)Import BC3 corpus xml files into sqllite db
(2)Feature extraction
	2.1)Generate speech act tag(Ddata,Deliver,Meet,Request,Commit) for each email sentences using speech_act.jar(https://github.com/KevinZhaoNY/SpeechActTagger)
	2.2)Sentiment Analysis (give a score between -3 and 3 to each sentence)
	2.3)Sentence Length
(3)TODO:Export sentence feature matrix to supervised machine learning algorithm


##########Program Structure##########
/bc3/annotation.xml --- email summary for bc3 corpus
/bc3/corpus.xml --- bc3 email corpus
/bc3/bc3/db --- bce email corpus database file (generated automatically after running main.py)

/docs -- documents and design graphs

/libs/speech_act.jar --- java program which generates speech act tag ,here is the link https://github.com/KevinZhaoNY/SpeechActTagger

/src/main.py  -- this is the main entry of the program
/src/db_tester.py -- shows you all the content in the sqlite database
/src/sentiment/analysis.py -- sentiment analysis module
/src/sentiment/AFINN-111.txt -- AFINN: A new word list for sentiment analysis on Twitter
/src/sentiment/topia --- Content Term Extraction using POS Tagging


##########DataBase Design##########

* thread 
-----------------
|Id    |Subject |
-----------------
|int   |char    |
---------------- -  


* email 
----------------------------------------------------
|Id    |thread_id |subject |from_who |to_whom |cc  |
----------------------------------------------------
|int   |int       |char    |char     |char    |char|
----------------------------------------------------

* sentence 
-------------------------------------------------------------
|Id    |email_id |text |length |similarity |extracted|sa_tag|
-------------------------------------------------------------
|int   |int      |char |int    |float      |boolean  |char  |
-------------------------------------------------------------


* summary  (not implemented yet)
--------------
|Id    |text |
--------------
|int   |char |
--------------
