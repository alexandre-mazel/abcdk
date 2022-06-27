# -*- coding: utf-8 -*-

####
# Send all file and project to the nao
# Command line option:
# <scriptname> [nao_ip]
####


strNaoIp = "10.0.252.134";
strRemotePath = "/home/nao/naoqi/lib/python";

import os
import sys
import datetime

# nao ip
if( len( sys.argv ) > 1 ):
	strNaoIp = sys.argv[1];


def isOnWin32():
  "Are we on a ms windows system?"
  return os.name != 'posix';
# isOnWin32 - end

if( isOnWin32() ):
    pwd = "-pw nao";

# os.system( "ssh nao@%s mkdir -p %s" % ( strNaoIp, strRemotePath ) );
os.system( "scp %s -r ../../appu_work/altools.py nao@%s:%s" % ( pwd, strNaoIp, strRemotePath ) );
os.system( "scp %s -r ../../appu_work/naoconfig.py.sample nao@%s:%s/naoconfig.py" % ( pwd, strNaoIp, strRemotePath ) );
os.system( "scp %s -r ../../appu_work/behaviordata.py nao@%s:%s" % ( pwd, strNaoIp, strRemotePath ) );
strNow = str( datetime.datetime.now() );
print( "\ndone at %s" % strNow[0:len(strNow)-7] ); # remove microsec