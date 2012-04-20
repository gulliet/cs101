cs101
=====

Project FeedInformant, my official entry to the Udacity CS101 contest (Apr 2012)

Submission: 
FeedInformant, a personal AI assistant to automatically classify your RSS feeds. 

Concept: 
FeedInformant use an unsupervised machine-learning algorithm to automatically sort the articles sent by your choice of RSS sources in pertinent categories. The result is similar to a press review. If you have subscribed to dozens of RSS feeds that send numerous daily updates, FeedInformant is going to save your a good deal of time when looking for the most important trends of the day. 

Background: 
Everyday, I get several hundreds of bits of information sent by more than 50 news sources, mainly in sciences and technology. If a topic is hot, dozens of similar articles are going to show up. Randomly going through all of them just to decide whether they are worth reading is a time consuming process. Though the idea to have "someone" doing the sorting for me (another option would be to unsubscribe to many feeds, but in this case that would also mean missing many interesting news). In Fall 2011, I attended the first presentation of the free online course "Introduction to Artificial Intelligence" taught by Peter Norvig and Sebastian Thrun. That was a thrilling and inspiring class, but unfortunately I could not make use of any of the many mind-blowing concepts we saw since I was not able to program them. Then came Udacity CS101 and the situation has dramatically changed! So, when this programming contest was announced, I decided to tackle the issue I faced with the RSS feeds. 

Design: 
The basic process is as follow. 
First, FeedInformant fetches the articles available from the various RSS sources (XML files) and extracts title and contents from each article. 
Second, the program scans the database and sanitizes the textual information by removing links to images or multimedia (usually advertisement), punctuation, and common words (such as 'a', 'an', 'but', etc.). 
Third, an index of keywords and their frequencies is built (according to a process very similar to what we have seen when designing the CS101 Web crawler). 
From there, the classifier algorithm is called and it assesses the similarity of each document against the others in successive iterations. 
Finally, the results are formatted as a Web page than can be read by any Web browser.

Each steps but the last were challenging to code. Although RSS feeds are XML files, there exists at least nine (9) different "standards'! In such conditions, even assuming that the documents were well formatted, parsing directly the XML code was a nightmare. Fortunately, the `Internet and some fantastic people from the Python community (StakOverFlow is an invaluable resource), I have eventually used FeedParser, which is an Open Source Python library. 
The code that cleans the text within the articles is far from perfect but at least it exists, though in a very rudimentary form (for instance, names such as "Mac OS X" or "Pythagoras' Theorem" are not parsed as one word, which conceptually they are). 
To build the index database of keywords and frequencies, I have settled for a dictionary of dictionaries (data structure I get familiar with and feel confortable to use thanks to CS101): 

{'article_1_permanent_id': {'word_11': frequency_in_document_1, 'word_12': frequency_in_document_1, ... }, 'article_2_permanent_id': {'word_21': frequency_in_document_2, 'word_22': frequency_in_document_2, ... }, ... } 

The main benefice of this structure is that it can be used to represents *sparse* vectors and matrices (i.e. a compact representation of vectors and matrices for which many entries are zeroes). 
Accordingly, I wrote the code that computes the various distances (Manhattan, Euclid, cosine, Pearson, and Tanimoto for now) and the unsupervised classifier (K-Means algorithm) to take advantage of this by unpacking the vectors on the fly, only if a dense representation is needed, or doing computation without even using the hidden dimensions for which the corresponding values are zero. 
Consequently, the program is fast and memory efficient. 

For the classification process, I have opted for the K-means algorithm since it belongs to the family of the *unsupervised* learning algorithm, that is no intervention or feedback from the user is required. 
Eventually, FeedInformant could be spawn as a Background process and it will push the new result to the user by a notification mechanism such as the Open Source software Growl. 

The accuracy of the categorization process by the K-means algorithm is highly dependent of the metric used to compute the similarity among the various documents. This is why I have coded and experimented with several concepts of distances (we saw the edit-distance in the course), such as the Manhattan distance (or Taxi-cab distance), the very classic and widely known Euclidean distance (or L2-norm, from Pythagoras' Theorem), the cosine distance (that depends on the angle between two vectors), the Pearson distance (a statistical measure of the similarity of two sets of observations, here two sets of words and their frequencies), and the Tanimoto distance. 

Usage: 
As of today, the FeedInformant is a command line utility that can be launch form the python interpreter,

$ python feedinformant.py

or directly from the prompt,

$ ./feedinformant.py --help usage: feedinformant.py [-h] [-l] [-d DIST] [-c CAT] [--version]

AI classifying RSS feeds.

optional arguments: 
-h, --help            show this help message and exit 
-l, -L, --live        use live Internet feeds (rather than test data) 
-d DIST, --dist DIST  distance to use: manhattan, euclidean, cosine, pearson, tanimoto (default) 
-c CAT, --cat CAT     number of categories to use for classification between 2 and 100 (default: 10) 
--version             show program's version number and exit

The output is a very crude (only headings, lists, and href are used) HTML file called "readnews.html" that can be read by any Web browser, even from within the terminal if you have Lynx installed:

$ lynx readnews.html

By default, FeedInformant uses pre-fetched feeds located in the directory "./data". The files that are really going to be parsed are those listed in the configuration file "test_feed_list.txt". 
To go live, just use the switch "--live" and FeedInformant will fetch the feeds listed in the configuration file "live_feed_list.txt". You can of course, edit any of these configuration files as you wish but they must contain only url or file names and only one entry per line.

Code link: 
Note that FeedInformant imports only standard Python modules, except for FeedParser.py that must be located in the same directory as FeedInformant (this is not required, of course, if you already have a working install of FeedParser). 

Participant: 
Udacity forum name: gulliet 
Real name: Jean-Marc Gulliet 
Email: jeanmarc (dot) gulliet (at) gmail (dot) com 

License: 
This software is licensed under the Creative Commons Attribution-Noncommercial-Share Alike 3.0 License (CC BY-NC-SA 3.0) 
For more info, see http://creativecommons.org/licenses/by-nc-sa/3.0/ 

References: 
"Introduction to Artificial Intelligence", Fall 2011, Peter Norvig and Sebastian Thrun, Stanford Engineering, free online class at https://www.ai-class.com/home/
"Machine Learning", Fall 2011, Andrew Ng, Stanford Engineering, free online class at http://www.ml-class.org/course/class/index 
"Artificial Intelligence, a Modern Approach", 3rd Ed., Stuart Russell and Peter Norvig, 2010, Pearson Education International 
"Speech and Language Processing", 2nd Ed., Daniel Jurafsky and James Martin, 2009, Pearson Education International 
"FeedParser", a Python library that parses feeds in all known formats, including Atom, RSS, and RDF. It runs on Python 2.4+. Available at http://code.google.com/p/feedparser/ 
"Guide to Data Mining", chapter 2, last acceded on Friday 20 April 2012, http://guidetodatamining.com/guide/ch2/DataMining-ch2.pdf 
"Mining Similarity Using Euclidean Distance, Pearson Correlation, and Filtering", last acceded on Friday 20 April 2012 http://mines.humanoriented.com/classes/2010/fall/csci568/portfolio_exports/lguo/similarity.html "
Clustering Microarray Data", Andrea Vijverberg, Advisor: Professor Hardin, Pomona College, Department of Mathematics, Spring 2007, last acceded on Friday 20 April 2012 at http://pages.pomona.edu/~jsh04747/Student%20Theses/vivjverberg_07.pdf

"Pearson's Correlation Coefficient Calculation - Worked Solution", Laerd Statistics, last acceded on Friday 20 April 2012 at https://statistics.laerd.com/calculators/pearsons-product-moment-correlation-coefficient-calculator-1.php 
"A Proof of the Triangle Inequality for the Tanimoto Distance", A H Lipkus, Journal of Mathematical Chemistry (1999) Volume: 26, Issue: 1, Publisher: Springer Netherlands, Pages: 263-265


