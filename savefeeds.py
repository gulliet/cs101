#!/usr/bin/env python

from time import localtime
from urllib2 import urlopen, URLError, HTTPError

def make_unique_file_name(directory = './data/', title = 'RSS', ext = 'xml'):
    datetime_stamp = '%4d-%02d-%02dT-%02d-%02d-%02d' % localtime()[:6]
    file_name = '%s%s-%s.%s' % (directory, title, datetime_stamp, ext)
    return file_name
    
def save_live_feeds():
    try:
        print 'Getting list of live feeds to save...'
        file = open('live_feed_list.txt')
    except IOError, e:
        print 'ERROR: could not open configuration file: ', e
        return -1

    data = file.readlines()
    feeds = []
    for line in data:
        feeds.append(line.strip())
    file.close()
    print 'OK'
    
    file_list = []
    for url in feeds:
        print '-- Reading', url
        try:
            file = urlopen(url)
        except HTTPError, e:
            print 'The server couldn\'t fulfill the request.'
            print 'Error code: ', e.code
            break
        except URLError, e:
            print 'We failed to reach the server.'
            print url
            print 'Reason: ', e.reason
            break
        
        data = file.read()
        file.close()
        
        file_name = make_unique_file_name()
        
        print '-- Writing', file_name
        file = open(file_name, 'w')
        file.write(data)
        file.close()
        
        file_list.append(file_name)

    print 'Updating test_feed_list.txt'
    file = open('test_feed_list.txt', 'a')
    for entry in file_list:
        file.write('%s\n' % entry)
    file.close()
    print 'Done!'

save_live_feeds()