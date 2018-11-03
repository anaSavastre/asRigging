import os
import sys
import fileinput


import os
os.listdir("path") # returns list


fileToSearch  = "C:/Users/Kari Noriy/OneDrive for Business/AVECT/AVET_SURFACETOP/scripts/test.ma"

tempFile = open( fileToSearch, 'r+' )

textToSearch = "student"
textToReplace = ""

for line in fileinput.input( fileToSearch ):
    # if textToSearch in line :
    #     print('Match Found')
    # else:
    #     print('Match Not Found!!')
    tempFile.write( line.replace( textToSearch, textToReplace ) )
tempFile.close()


def cleanFile (filePath, searchText="student", replaceText=""):
    tempFile = open( filePath, 'r+' )
    
    for line in fileinput.input( fileToSearch ):
        # if textToSearch in line :
        #     print('Match Found')
        # else:
        #     print('Match Not Found!!')
        tempFile.write( line.replace( searchText, replaceText ) )
    tempFile.close()



    