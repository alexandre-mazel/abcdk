# -*- coding: utf-8 -*-

###########################################################
# Aldebaran Behavior Complementary Development Kit
# text_comprehension Tools
# Author A. Mazel
# Aldebaran Robotics (c) 2010 All Rights Reserved - This file is confidential.
###########################################################

"text_comprehension: understand text and convert them to tickets. Current lang: fr"

print( "importing abcdk.text_comprehension" );

import ticket



class TextComprehension:
    def __init__( self ):
        pass

    def analyse( self, txt, strSpeakerName = "me" ):
        """
        analyse a text and create the associated ticket.
        or return None if not understood
        """
        print( "INF: TextComprehension.analyse( '%s', '%s' ) - begin" % (txt,strSpeakerName)  )
        
        tic = None
        
        strLike = "j'aime"
        strDontLike = "je n'aime pas"
        strDontLikeAlt = "j'aime pas"
        if strLike in txt or strDontLike in txt or strDontLikeAlt in txt:
            print( "INF: TextComprehension.analyse: like" )
            source = "me"
            action = "aimer"
            
            verite = 1.
            if( strDontLike in txt ):
                strLike = strDontLike
                verite = -1.

            if( strDontLikeAlt in txt ):
                strLike = strDontLikeAlt
                verite = -1.
            
            objet = txt[txt.find(strLike)+len(strLike):]
            objet = objet.strip()
            objet = objet.strip(".,!?")
            
            tic = ticket.Ticket( source = source, action = action, objet = objet, verite=verite )
            return tic

        return tic
        
    def innerTest( self ):
        import test
        test.assert_check_comp( self.analyse( "j'aime les poireaux" ), ticket.Ticket( source = "me", action = "aimer", objet = "les poireaux", verite=1. ), ticket.isContentsEqual )
        test.assert_check_comp( self.analyse( "j'aime les poireaux." ), ticket.Ticket( source = "me", action = "aimer", objet = "les poireaux", verite=1. ), ticket.isContentsEqual )
        test.assert_check_comp( self.analyse( "je n'aime pas les vélos." ), ticket.Ticket( source = "me", action = "aimer", objet = "les vélos", verite=-1. ), ticket.isContentsEqual )
        test.assert_check_comp( self.analyse( "j'aime manger" ), ticket.Ticket( source = "me", action = "aimer", objet = "manger", verite=1. ), ticket.isContentsEqual )
        pass
# class TextComprehension - end

textComprehension = TextComprehension()

def autoTest():
    tc = TextComprehension()
    tc.innerTest()

if( __name__ == "__main__" ):
    autoTest()
    