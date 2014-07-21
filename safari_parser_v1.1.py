#
#safari_parser.py
#This will parse the Safari Internet History located under /Users/%username%/Libary/Safari/.
#The files it can parse are: History.plist, Downloads.plist, Bookmarks.plist and TopSites.plist.
#It will also parse the History.plist from an iPhone, the Bookmarks.db file, and the RecentSearches.plist.
#Choose either a single file to parse (-f) or and entire directory,which will process all files located in it.
#
#This program requires that the biplist library be installed
# Easyinstall can be used to install it:
# Linux -> sudo easy_install biplist
# 
# Windows -> Windows box, you can install the setup tools from python.org which contain easy_install. 
#            It will place easy_install.exe into your python directory in the scripts folder. 
#            To get biplist, just change into the scripts directory and run easy_install biplist.
# 
#Copyright (C) 2014 Mari DeGrazia (arizona4n6@gmail.com)
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You can view the GNU General Public License at <http://www.gnu.org/licenses/>
#
# Version History:
# v1.1 2014-7-20
#    
# 

__author__ = 'arizona4n6@gmail.com (Mari DeGrazia)'
__version__ = '1.1'
__copyright__ = 'Copyright (C) 2014 Mari DeGrazia'
__license__ = 'GNU'


from biplist import *
from optparse import OptionParser
import datetime
import sqlite3
import sys

#convert mac absolute time (seconds from 1/1/2001) to human readable
def convert_absolute(mac_absolute_time):
    try:
        bmd = datetime.datetime(2001,1,1,0,0,0)
        humantime = bmd + datetime.timedelta(0,mac_absolute_time)  
    except:
        return("Error on conversion")
    return(humantime)


#check to see if the plist file is a valid plist file
def check_plist_file(file):
    try:
        f = open(options.infile, "rb")
    except IOError as e:    
        return False
    
    #make sure the file is a binary plist file
    file_header = f.read(6)
    if str(file_header) != 'bplist' and str(file_header) != '<?xml ' and str(file_header) != "SQLite":
        return False
    #be polite and move back to the beginning of the file
    f.seek(0)
    return f
    
#check for the plist file in the given directory
def file_check(safari_file,xml=False,db=False):
    #try to open the files, if not there return false
    try:
        f = open(options.safari_dir + "/" + safari_file, "rb")
        filename = options.safari_dir + "/" + safari_file
    except IOError as e:
        try: 
            f = open(options.safari_dir + "\\" + safari_file, "rb")
            filename = options.safari_dir + "\\" + safari_file
        except:
            return False
    #test the plist file for the xml format
    if xml is True:        
        try:
            line1 = f.readline()
            line2 = f.readline()
            
            if  "plist" in line2:
                f.seek(0)
                return f  
        except:
            return False
    elif db is True:
        file_header = f.read(6)
                
        if str(file_header) != "SQLite":
            return False
        else:
            f.close()
            return filename
   
    else:
    
        #make sure the file is a binary plist file
        file_header = f.read(6)
        if str(file_header) != 'bplist':
            return False
          
        else:
            #be polite and move back to the beginning of the file
            f.seek(0)
            return f

#recursive function to get children for iPhone bookmarks
def get_children(parent_id,parent_name):
    global bookmarks_count
    t= (parent_id,)
    cursor.execute('SELECT id,title,URL,num_children FROM bookmarks WHERE parent = ?', t)
    children = cursor.fetchall()
    
    for child in children:
        
        bookmarks_count += 1
        output.write(parent_name.encode('utf-8') +"\t" + child[1].encode("utf-8") + "\t" + child[2].encode("utf-8") + "\n" )
        child_num_children = child[3]
        child_id = child[0]
        child_title = child[1]
        full_title = parent_name + ">" + child_title
        
        #does this row have a child, if so, get children
          
        if (child_num_children > 0): 
  
            get_children(child_id,full_title)

#recursive function to process children for the bookmarks.plist file
def process_child(parent_node,child_node):
    global bookmark_count  
    for item in child_node:
                    
        if "URIDictionary" in item:
            bookmark_count += 1
            output.write(parent_node + "\t")
            try:
                output.write(item["URIDictionary"]["title"] + "\t")
            except:
                output.write(item["URIDictionary"]["title"].encode("utf-8") + "\t")
       
        if "URLString" in item:
            output.write(item["URLString"]) 
            output.write("\t")
        
        if  "ReadingList" in item:
            str(item["ReadingList"]["DateAdded"])
            try:
                output.write(str(item["ReadingList"]["DateAdded"]) + "\t")
            except:
                print "\t"
            
            try:
                output.write(str(item["ReadingList"]["PreviewText"].encode("utf-8")) + "\t")             
            except:
                print "\t"
                
        if "ReadingListNonSync" in item:
            
            try:
                output.write(str(item["ReadingListNonSync"]["DateLastFetched"]))
                output.write("\t")
            except:
                output.write("\t")
            try:
                output.write(str(item["ReadingListNonSync"]["FetchResult"]))
                output.write("\t")
            except:
                ouput.write("\t")
            try:
                output.write(str(item["ReadingListNonSync"]["AddedLocally"])+ "\t")
            except:
                print "\t"
            try:
                output.write(str(item["ReadingListNonSync"]["ArchiveOnDisk"])+ "\t")
            except:
                print "\t"

        #end the line        
        output.write("\n")
        
        if "Children" in item:
            child_list_entry = item["Children"]
        if "Title" in item:
            bookmarkType = item["Title"] 
            full_path = parent_node + ">"+ bookmarkType  
            process_child(full_path,child_list_entry)
          
###############################  MAIN  ################################################

#help menu, etc
usage = "\nThis will parse the Safari Internet History located on OS X under /Users/%USERNAME%/Library/Safari.\n\
The Safari files it can parse are: History.plist, Downloads.plist, Bookmarks.plist and TopSites.plist.\n\
The iPhones files it can parse are History.plist, RecentSearches.plist and Bookmarks.db (various locations - check iTunes backups too).\n\
Choose either a single file to parse (-f) or a directory (-d),which will parse any of the above files located in it.\n\
Designate an output directory to hold the generated reports (-o).\n\n\
Examples: \n\
safari_parser.py -d /Users/HelloKitty/Library/Safari -o /Users/MyAccount/Documents/ParsedReports\n\
safari_parser.py -d /MyFolder/iphonefiles -o /Users/MyAccount/Documents/ParsedReports\n\
safari_parser.py --history -f History.plist -o /Users/MyAccount/Documents/ParsedReports/history.tsv\n\
safari_parser.py --bookmarks -f Bookmarks.plist -o /Users/MyAccount/Documents/ParsedReports/bookmarks.tsv\n"

parser = OptionParser(usage=usage)

parser.add_option("-f", dest = "infile", help = "file to parse", metavar = "History.plist")
parser.add_option("-o", dest = "outfile", help = "directory to hold output", metavar = "/MyDocuments/reports")
parser.add_option("-d", dest = "safari_dir", help = "folder containing history files", metavar = "/Users/username/library/Safari")

parser.add_option("--history", action ="store_true", dest = "history", help = "Parse History.plist File (including iPhone)")
parser.add_option("--topsites", action ="store_true", dest = "topsites", help = "Parse TopSite.plist File")
parser.add_option("--downloads", action ="store_true", dest = "downloads", help = "Parse Download.plist File")
parser.add_option("--bookmarks", action ="store_true", dest = "bookmarks", help = "Parse Bookmarks.plist File")
parser.add_option("--iPhonebookmarks", action ="store_true", dest = "iPhonebookmarks", help = "Parse iPhone Bookmarks.db File")
parser.add_option("--recentsearches", action ="store_true", dest = "recentsearches", help = "Parse iPhone recentsearches.plist File")


(options,args)=parser.parse_args()

#no arguments given by user,exit
if len(sys.argv) == 1:
    parser.error("Please select an option")
    

if options.infile == None and options.safari_dir == None:
    parser.error("Select either a file to parse, or a directory to parse")
    exit()
if options.outfile == None:
    parser.error("Specify the output")
    
     
if options.safari_dir == None and options.history == None and options.topsites == None and options.downloads == None and options.bookmarks == None and options.iPhonebookmarks == None and options.recentsearches == None:
    parser.error("Choose a file type or a directory to process")
    


#if the Safari folder was selected, check for each file that can be parsed
if options.safari_dir:
        
    #What OS for file path
    if '\\' in options.outfile:
        seperator = "\\"
    if '/' in options.outfile:
        seperator = "/"
    
    #check for history file
    history_file = file_check("History.plist")
    if history_file == False:
        print "History.plist file not located or not correct format (OSX,iPhone)"
    else:
        options.history = True
        output_history = open(options.outfile + seperator + "history.tsv", 'w')
        
    #check for bookmark file
    bookmarks_file = file_check("Bookmarks.plist")
    if bookmarks_file == False:
        print "Bookmarks.plist file not located or not correct format (OSX)"
    else:
        options.bookmarks = True
        output_bookmarks = open(options.outfile + seperator + "bookmarks.tsv", 'w')
        
    #check for downloads file
    downloads_file = file_check("Downloads.plist")
    if downloads_file == False:
        print "Downloads.plist file not located or not correct format (OSX)"
    else:
        options.downloads = True
        output_downloads = open(options.outfile + seperator + "downloads.tsv", 'w')
        
    #check for TopSites file
    topsites_file = file_check("TopSites.plist")
    if topsites_file == False:
        print "TopSites.plist file not located or not correct format (OSX)"
    else:
        options.topsites = True
        output_topsites = open(options.outfile + seperator + "topsites.tsv", 'w')
    
    #check for recentsearch.plist file
    recentsearches_file = file_check("RecentSearches.plist",True)    
    if recentsearches_file == False:
            print "RecentSearches.plist file not located or not correct format (iPhone)"
    else:
        
        options.recentsearches = True
        output_recentsearches = open(options.outfile + seperator + "recentsearches.tsv", 'w')
        
    #check for recentsearch.plist file
    bookmarks_db_file = file_check("Bookmarks.db",False,True)    
    
    if bookmarks_db_file == False:
            print "Bookmarks.db file not located or not sqlite format (iPhone)"
    else:
        
        options.iPhonebookmarks = True
        output_iPhonebookmarks = open(options.outfile + seperator + "iPhonebookmarks.tsv", 'w')
    
    #check for bookmarks.db file for iPhone

#user chose just to process one file, check it
if not options.safari_dir:
    output = open(options.outfile, 'w')
    
    if check_plist_file(options.infile) == False:
        print options.infile + " not located or not a binary plist file"


#process TopSites.plist file
if options.topsites == True:
    if options.safari_dir:
        plist = readPlist(topsites_file)
        output = output_topsites
       
    else:
        plist = readPlist(options.infile)
    
    output.write("URL\tTitle\tIs Pinned\tIs Built In\tIs Banned\n")
    #start at the root
    topsites_count = 0
    for key,value in plist.iteritems():

        #print key,value
        if "DisplayedSitesLastModified" in key:
            topsiteLastModified = str(value)
        
        if key == "BannedURLStrings":
            for bannedURLs in value:
                output.write(bannedURLs)
                output.write("\t\t\t\tTRUE\n")
                topsites_count += 1
        
        if key == "TopSites":
            #loop through each topsite entry
            for topsites in value:
                topsites_count += 1                   
                try:
                    output.write(str(topsites["TopSiteURLString"] + "\t"))
                except:
                    output.write("\t")
                
                try:
                    output.write(str(topsites["TopSiteTitle"] + "\t"))
                except:
                    output.write("\t")
                if "TopSiteIsPinned" in topsites:
                    output.write(str(topsites["TopSiteIsPinned"]) + "\t")
                    #output.write("True\t")
                else:
                    output.write("\t")
                
                if "TopSiteIsBuiltIn" in topsites:
                    
                    output.write(str(topsites["TopSiteIsBuiltIn"]))
                    output.write("\n")                 
                    
                else:
                    output.write("\n")
                
                
    output.close()
    print "Top Sites parsed: \t" + str(topsites_count) 
    print "Top Sites last modified date: " + topsiteLastModified
 
#process Downloads.plist file
if options.downloads == True:
    download_count = 0
    if options.safari_dir:
        plist = readPlist(downloads_file)
        output = output_downloads
       
    else:
        plist = readPlist(options.infile)
  
    output.write("Download URL\tDownload Path\tProgressBytesSoFar\tTotalToLoad\n")
    for key,value in plist.iteritems():
        
        if key == "DownloadHistory":
            #loop through each topsite entry
            for downloads in value:
                   
                try:
                    output.write(str(downloads["DownloadEntryURL"] + "\t"))
                except:
                    output.write ("\t")
                try:
                    output.write(str(downloads["DownloadEntryPath"] + "\t"))
                except:
                    output.write("\t")
                    
                try:
                    output.write(str(downloads["DownloadEntryProgressBytesSoFar"]))
                    output.write("\t")
                except:
                    output.write("\t")
                try:    
                    output.write(str(downloads["DownloadEntryProgressTotalToLoad"]))
                except:
                    output.write("")
                output.write("\n")
                download_count += 1
                #downoads_count = downloads_counts + 1
                
    output.close()
    print "Downloads parsed: \t" + str(download_count)

#process Bookmarks.plist file
if options.bookmarks == True:
    bookmark_count = 0
    if options.safari_dir:
        plist = readPlist(bookmarks_file)
        output = output_bookmarks
       
    else:
        plist = readPlist(options.infile)
        
    #prepare the output file
    output.write("Bookmark Category\tTitle\tURL\tDate Added (Reading List)\tPreview Text (Reading List)\tDate Last Fetched (Reading List)\tFetchResult (Reading List)\tAdded Locally (Reading List) \tArchive On Disk (Reading List)\n")
    list_entry = {}    
    
    for key,value in plist.iteritems():
     
        if key == "Children":
            
            #loop through each topsite entry
            for subkey in value:
                
                #each subkey contains entries for each type of bookmark, Fav bar, reading list, folder etc
                
                if "Children" in subkey:                    
                    list_entry = subkey["Children"]
                 
                #The Title key holds what type of bookmark category it is
                if "Title" in subkey:
                    bookmarkType = subkey["Title"]
                    #recurse through the subfolders of each bookmark
                    process_child(bookmarkType,list_entry) 
   
    print "Bookmarks parsed: \t" + str(bookmark_count)
    output.close()   

#process History.plist file
if options.history == True:    
    history_count = 0
    if options.safari_dir:
            plist = readPlist(history_file)
            output = output_history
          
    else:
        plist = readPlist(options.infile)

#start at the root
    output.write("Last Visit Date (UTC)\tURL\tTitle\tVisit Count\tRedirect URLs\n")
    for key,value in plist.iteritems():
         
        #go through the webhistory dictionary first
        if key == "WebHistoryDates":
            #loop through each history entry
            for history_entry in value:
                history_count += 1
                #for whatever stupid reason, the key is blank for the URL in the plist file
                URL = history_entry[""]
                            
                if "lastVisitedDate" in history_entry:
                    lastVisitedDate = history_entry["lastVisitedDate"]
                    lastVisitedDate =  long(lastVisitedDate[:-2])
                    lastVisitedDate =  convert_absolute(lastVisitedDate)
                                
                else:
                    lastVisitedDate = ""
                
                if "visitCount" in history_entry:
                    visitCount = history_entry["visitCount"]
                else:
                    visitCount = ""
                       
                output.write(str(lastVisitedDate) + "\t" + str(URL)+"\t")
                                       
                if "title" in history_entry:                       
                        
                    try:
                        output.write(str(history_entry["title"])+"\t")
                    except:
                        title = history_entry["title"]
                        output.write(title.encode("utf-8") + "\t")
                else:
                    output.write("" + "\t")
                
                output.write(str(visitCount) + "\t")
                
                if "redirectURLs" in history_entry:
                    for url in history_entry["redirectURLs"]:
                        output.write(url + " ")
                else:
                    output.write("")
            
                output.write("\n")
    print "History parsed: \t" + str(history_count)
    output.close()
    
#iPhonebookmarks are stored in an SQLite database file
if options.iPhonebookmarks == True:
    
    bookmarks_count = 0
    
    if options.safari_dir:
       
        output = output_iPhonebookmarks
        options.infile = bookmarks_db_file
        
    
    output.write("Bookmark Category\tTitle\tURL\n")
    
    #connect to database
    try:
        db = sqlite3.connect(options.infile)
    except:
        "Error connecting to database"
        exit()
    cursor = db.cursor()
    
    #get the top level, root bookmark
    
    cursor.execute('''SELECT id,title,URL,num_children FROM bookmarks where id = 0''')
    row = cursor.fetchone()
    
    num_children = row[3]
    id = row[0]
    title = row[1]
            
    #does this row have a child, if so, get children
    if (num_children > 0): 
        get_children(id,title)
         
    db.close()
    print "iPhone Bookmarks parsed: \t" + str(bookmarks_count)
    
if options.recentsearches == True:
       
    
    recentsearches_count = 0
    
    if options.safari_dir:
        plist = readPlist(recentsearches_file)
        output = output_recentsearches 
       
    else:
        plist = readPlist(options.infile)
  
    for key,value in plist.iteritems():
        if key == "RecentSearches":
            for entry in value:
                output.write(str(entry) + "\n")
                recentsearches_count +=1        
        
    print "Recent Searches parsed: \t" + str(recentsearches_count)
    
    output.close()    