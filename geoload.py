#crawls from google and store in database 
#Running- press ctrl+Z to inturrupt on windows ctrl+c on Linix or Mac
#interupt and check the database what is written and run again to see the added data 
#refresh the database

import urllib
import sqlite3
import json
import time
import ssl

# If you are in China use this URL:
# serviceurl = "http://maps.google.cn/maps/api/geocode/json?"
serviceurl = "http://maps.googleapis.com/maps/api/geocode/json?"

# Deal with SSL certificate anomalies Python > 2.7
# scontext = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
scontext = None

#create the database
conn = sqlite3.connect('geodata.sqlite')
cur = conn.cursor()

#create the table Location from from python in the geodata database
cur.execute('''
CREATE TABLE IF NOT EXISTS Locations (address TEXT, geodata TEXT)''')

#open the file where.data
fh = open("where.data")
count = 0
for line in fh:
    if count > 200 : break
	#the address is the entire line
    address = line.strip()
	
    print ''
	
	#replace the ? with the address after the ,comma clean up the address
    cur.execute("SELECT geodata FROM Locations WHERE address= ?", (buffer(address), ))
	
#fetchone gets one row in the form of list. [0]gets the first in the list.(column)
#checks if it already has it in the data base before retrieving it
    try:
        data = cur.fetchone()[0]
        print "Found in database ",address
        continue #continue the for loop if there is data in the database
    except:
        pass
		
#if there is no data in the database
#connect to google
    print 'Resolving', address
    url = serviceurl + urllib.urlencode({"sensor":"false", "address": address})
    print 'Retrieving', url
    uh = urllib.urlopen(url, context=scontext)
    data = uh.read()
    print 'Retrieved',len(data),'characters',data[:20].replace('\n',' ')
    count = count + 1
	#check if the data is okay 
    try: 
        js = json.loads(str(data))
        # print js  # We print in case unicode causes an error
    except: 
        continue
#the status is in Json file, sheck if it is ok or not
    if 'status' not in js or (js['status'] != 'OK' and js['status'] != 'ZERO_RESULTS') : 
        print '==== Failure To Retrieve ===='
        print data
        break

    cur.execute('''INSERT INTO Locations (address, geodata) 
            VALUES ( ?, ? )''', ( buffer(address),buffer(data) ) )
    conn.commit() 
    time.sleep(1)

print "Run geodump.py to read the data from the database so you can visualize it on a map."
