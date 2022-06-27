# -*- coding: utf-8 -*-

###########################################################
# Aldebaran Behavior Complementary Development Kit
# User profile tools
# Aldebaran Robotics (c) 2010 All Rights Reserved - This file is confidential.
###########################################################

"""User profile tools"""
print( "importing abcdk.user" );

import time
import datetime
import random

import filetools
import nettools
import pathtools

class User:
    """
    This class handle users from their IP Usage
    """
    
    def __init__( self, strFirstName, strLastName, strLastIP = None ):
        self.strFirstName = strFirstName;
        self.strLastName = strLastName;
        self.nDayLastSeen = -1;
        self.nTimeLastSeen = -1;
        self.bPresent = -1;
        strDir = pathtools.getCachePath() + "users/";
        filetools.makedirsQuiet( strDir );
        self.strFilesave = strDir + "%s_%s.dat" % ( self.strLastName, self.strFirstName );
        self.read();
        if( strLastIP != None ):
            self.strLastIP = strLastIP;  # overrid ip with given one  
    # __init__ - end
    
    def __del__( self ):
        self.write();
    # __del__ - end
    
    def read( self ):
        "read user from disk"
        try:
            file = open( self.strFilesave , "r" );
        except:
            file = False;
        if( not file ):
            print( "WRN: no prev info about user '%s %s'" % ( self.strLastName, self.strFirstName ) );
            return;
        self.strFirstName, self.strLastName, self.strLastIP, self.nDayLastSeen, self.nTimeLastSeen, self.bPresent = eval( file.read() );
        file.close();
        print( "INF: User.read: %s: last day seen: %d, time since last seen: %f, last present: %d" % ( self.strLastName, self.nDayLastSeen, time.time() - self.nTimeLastSeen, self.bPresent ) );
    # read - end
    
    def write( self ):
        "write user to disk"
        print( "INF: User.write" );
        file = open( self.strFilesave , "w" );
        file.write( str( [self.strFirstName, self.strLastName, self.strLastIP, self.nDayLastSeen, self.nTimeLastSeen, self.bPresent] ) );
        file.close();
        print( "INF: User.write - end" );
    # write - end
    
    def update( self, nLang = 0 ):
        "update the presence of one user"
        "return sentence to say"
        strOut = "";
        bPresent = nettools.ping( self.strLastIP );
        bMustAutosave = False;
        if( bPresent != self.bPresent ):
            # verify
            bPresent = nettools.ping( self.strLastIP, bPleaseBeSure = True );
        if( bPresent != self.bPresent ):
            if( bPresent ):
                # welcome him
                print( "INF: user.update: user %s incoming" % self.strLastName );
                strOut += self.constructMessage( 1, nLang = nLang );
                print( "INF: user.update: message is: '%s'" % strOut );
                
            if( not bPresent ):
                # wave him good bye
                print( "INF: user.update: user %s has disappear" % self.strLastName );
                # strOut += self.constructMessage( 2, nLang = nLang );  # pb: each time I cut the ethernet of my robot => boing
            self.bPresent = bPresent;
            bMustAutosave = True;
            
        if( bPresent ):
            # update info
            nTime = time.time();
            nDay = int( datetime.datetime.now().strftime( "%d" ) );
            if( nDay != self.nDayLastSeen or nTime - self.nTimeLastSeen > 90*60 ):
                bMustAutosave = True;
                
            self.nTimeLastSeen = nTime;
            self.nDayLastSeen = nDay;
            
        if( bMustAutosave ):
            self.write();
            
        return strOut;
    # update - end
    
    def constructMessage( self, nType, nLang = 0 ):
        "construct some message to users"
        "  1: welcome message"
        "  2: goodbye message"
        
        strOut = "";
        nDay = int( datetime.datetime.now().strftime( "%d" ) );
        nHour = int( datetime.datetime.now().strftime( "%H" ) );
        nMin = int( datetime.datetime.now().strftime( "%M" ) );
        nTime = time.time();
        
        astrMorning = [
            [ "Good morning %s, I wish you a good day! ", "Bonjour %s, je te souhaites une bonne journée. " ],
            [ "Hi %s! ", "Salut %s! " ],
            [ "Hello %s! ", "Hello %s! " ],
            [ "Hihaw %s! ", "Coucou %s! " ],
        ];
        
        astrVariation = [
            [ "Sorry, I haven't seen you. ", "Désolé je ne t'avais pas vu. " ],
            [ "Oh oh are you hidding? ", "Oh oh tu te caches! " ],
            [ "I like your clothes! ", "J'aimes bien tes fringues! " ],
            [ "Your hair looks a bit wild, do you need a comb? ", "Pas terrible ta coiffure aujourd'hui, tu veux que je t'offres un peigne? " ],
            [ "Just because I don't shower doesn't mean you don't need to! ", "C'est pas parce que je ne prend pas de douche que ca t'empeches d'en prendre une. " ],
        ];
        
        
        
        astrSoon = [
            [ "You're up early!", "tu es bien matinal!" ],
            [ "By comign early you'll do big stuffs! ", "c'est en arrivant tot qu'on fait de grandes choses!" ],
        ];
                
        
        astrLate = [
            [ "Did you sleep well ?", "tu as fait une bonne grasse mate?" ],
            [ "At least you've got time to think.", "au moins tu as eu le temps de réfléchir a ce que tu allais faire aujourd'hui." ],
            [ "Too much traffic duty ?", "toujours cette fichue circulation ?" ],
            [ "Did you have problem to park your car?", "tu as eu du mal a trouver une place pour te garer ?" ],
        ];

        astrArriveAfternoon = [
            [ "What did you do that morning?", "Tu faisais quoi ce matin?" ],
        ];        

        astrHoliday = [
            [ "What about your holiday ?", "C'était bien tes vacances?" ],
            [ "You look tanned!", "T'as pas beaucoup bronzé dis donc!" ],
        ];

        astrGoodbye = [
            [ "Good bye %s. ", "Au revoir %s. " ],
            [ "Bye %s. ", "tchao %s. " ],
            [ "Bye bye %s, have a nice trip. ", "Salut %s, rentres bien. " ],
        ];
        
        astrEvening = [
            [ "Good evening!", "Bonne soirée!" ],
            [ "Good Night!", "Bonne nuit." ],
        ];
        
        astrAfterNoon = [
            [ "Good afternoon!", "Bonne après midi!" ],
        ];
        
        if( nType == 1 ):
            if( nTime - self.nTimeLastSeen < 90*60 ):
                # just a small pause meeting, plantage, deconnection, perte du réseau, ...
                return strOut;
            
            if( self.nDayLastSeen != nDay ):        
                listToSay = astrMorning;            
                strOut += listToSay[int( random.random() * len( listToSay ) )][nLang] % self.strFirstName;
                
                if( ( nHour == 9 and nMin < 30 ) or nHour < 9 ):
                    listToSay = astrSoon;            
                    strOut += listToSay[int( random.random() * len( listToSay ) )][nLang];
                elif( nHour > 14 ):
                    listToSay = astrArriveAfternoon;            
                    strOut += listToSay[int( random.random() * len( listToSay ) )][nLang];
                elif( ( nHour == 10 and nMin > 30 ) or nHour > 10 ):
                    listToSay = astrLate;            
                    strOut += listToSay[int( random.random() * len( listToSay ) )][nLang];
                elif( random.random() > 0.8 ):                    
                    listToSay = astrVariation;
                    strOut += listToSay[int( random.random() * len( listToSay ) )][nLang];                    
        elif( nType == 2 ):
                listToSay = astrGoodbye;
                strOut += listToSay[int( random.random() * len( listToSay ) )][nLang] % self.strFirstName;
                
                if( nHour < 18 ):
                    listToSay = astrAfterNoon;            
                    strOut += listToSay[int( random.random() * len( listToSay ) )][nLang];
                    
                if( nHour > 18 ):
                    listToSay = astrEvening;            
                    strOut += listToSay[int( random.random() * len( listToSay ) )][nLang];        
        return strOut;
    # constructMessage - end
    
    def simulateArrival( self ):
        "fake a departure and an arrival of some user, so next update it will say something"
        self.nDayLastSeen -= 1;
        self.nTimeLastSeen -= 24*60*60;
        self.bPresent = False;
    # simulateArrival - end
        
    
# class User - end


def autoTest():
    u = User( "Alexandre", "Mazel", "10.0.252.216" );
    print "update: " + u.update();
    print "update: " + u.update();
    u.strLastIP = "1.2.3.4";
    print "update: " + u.update();
# autoTest - end

# autoTest();