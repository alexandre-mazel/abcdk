# -*- coding: utf-8 -*-

####
# Send all file and project to the nao
# Command line option:
# <scriptname> [nao_ip] [nao_personnalised_passwd] [specific file to send]
####

# copy ..\abcdk\sdk\abcdk\*.py C:\Python27\Lib\site-packages\abcdk\ /y


strNaoIp = "10.0.252.134";
#strRemotePath = "/home/nao/naoqi/lib/python"; # 1.10
strRemotePath = "/home/nao/.local/lib/python2.6/site-packages"; # 1.12
strRemotePath = "/home/nao/.local/lib/python2.7/site-packages"; # 1.16

import os
import sys
import datetime

# nao ip
if( len( sys.argv ) > 1 ):
	strNaoIp = sys.argv[1];
	
# nao pwd
if( len( sys.argv ) > 2 ):
	strPassword = sys.argv[2];
else:
	strPassword = "nao"

# specific file
if( len( sys.argv ) > 3 ):
	strFileMask = sys.argv[3];
else:
	strFileMask = "*"

def isOnWin32():
  "Are we on a ms windows system?"
  return os.name != 'posix';
# isOnWin32 - end

if( isOnWin32() ):
    pwd = "-pw %s" % strPassword;
else:
    pwd = "";
# ssh nao@10.0.252.193 mkdir -p /home/nao/naoqi/lib/python
# os.system( "ssh nao@%s mkdir -p %s" % ( strNaoIp, strRemotePath ) );
#strCommand = "scp %s -r abcdk/%s nao@%s:%s/abcdk/" % ( pwd, strFileMask, strNaoIp, strRemotePath );
if not isOnWin32():
    strCommand = "ssh nao@%s mkdir -p %s/abcdk/" % (strNaoIp, strRemotePath );
    print(strCommand)
    os.system( strCommand );
    
if not isOnWin32():
    strCommand = "rsync %s -azvr abcdk/%s nao@%s:%s/abcdk/" % ( pwd, strFileMask, strNaoIp, strRemotePath );
else:    
    pwd = "" #on some windows the pw isnot existing anymore
    strCommand = "scp -r %s abcdk/%s nao@%s:%s/abcdk/" % ( pwd, strFileMask, strNaoIp, strRemotePath );
    
print(strCommand)
os.system( strCommand );
strNow = str( datetime.datetime.now() );
print( "\ndone at %s" % strNow[0:len(strNow)-7] ); # remove microsec
