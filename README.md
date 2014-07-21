Safari-Internet-History-Parser
==============================

This will parse the Safari Internet History located under /Users/%username%/Libary/Safari/.
The files it can parse are: History.plist, Downloads.plist, Bookmarks.plist and TopSites.plist.
It will also parse the History.plist from an iPhone, the Bookmarks.db file, and the RecentSearches.plist.
Choose either a single file to parse (-f) or an entire directory,which will process all files located in it.

####Required Library 
  Install the biplist on Linux/OS X using:

    sudo easy_install biplist
    
  For Windows, if you don't already have it installed, you'll need to grab the easy install utility which is included in the   setup tools from python.org, https://pypi.python.org/pypi/setuptools.  The setup tools will place easy_install.exe into your Python directory in the Scripts folder.   Change into this directory and run:

    easy_install.exe biplist
  
  Or download the biplist library from http://github.com/wooster/biplist and manually install it.

####Usage Examples

    safari_parser.py -d /Users/HelloKitty/Library/Safari -o /Users/MyAccount/Documents/ParsedReports
    safari_parser.py -d /MyFolder/iphonefiles -o /Users/MyAccount/Documents/ParsedReports
    safari_parser.py --history -f History.plist -o /Users/MyAccount/Documents/ParsedReports/history.tsv
    safari_parser.py --bookmarks -f Bookmarks.plist -o /Users/MyAccount/Documents/ParsedReports/bookmarks.tsv"

  Switches:
  --history         (Parse History.plist File,including iPhone)
  
  --topsites        (Parse TopSite.plist File)
  
  --downloads       (Parse Download.plist File)
  
  --bookmarks       (Parse Bookmarks.plist File)
  
  --iPhonebookmarks (Parse iPhone Bookmarks.db File)
  
  --recentsearches  (Parse iPhone recentsearches.plist File)
  
  --f   (use file for input)
  
  --d   (use directory containing files for input)

####More Information

View the blog post at http://az4n6.blogspot.com for more information


Email Mari > arizona4n6 at gmail dot com for help/questions/bugs
