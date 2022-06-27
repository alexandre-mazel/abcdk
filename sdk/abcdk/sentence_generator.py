# -*- coding: utf-8 -*-

###########################################################
# Aldebaran Behavior Complementary Development Kit
# Sentence Generator: generate natural speech sentence from scratch (fr/en/jp?)
# Author A. Mazel
# Aldebaran Robotics (c) 2010 All Rights Reserved - This file is confidential.
###########################################################

import time

"Sentence Generator"

print( "importing abcdk.sentence_generator" );

voyel = ['a', 'e', 'i',  'o', 'u', 'y']
pronominalFr = ["amuser"]

listVerb_Ir3rd = ["ouvrir", "dormir", "venir", "ecrir", "mourir", "ouvrir"]

listPeculiar_fr = {
    "etre":  [
                    ["suis", "es", "est", "sommes", "etes", "sont"],
                    ["étais", "étais", "était", "étions", "étiez", "étaient"],
                    ["serai", "seras", "sera", "serons", "serez", "seront"],
                ],
    "avoir":  [
                    ["ai", "as", "a", "avons", "avez", "ont"],
                    ["avais", "avais", "avait", "avions", "aviez", "avaient"],
                    ["aurai", "auras", "aura", "aurons", "aurez", "auront"],
                ]                
}

def removeAccent( voyel ):
    """
    return the unaccentuated form of a letter (or the letter if no accent)
    """
    
    if voyel in ["é", "è", "ê", "ë"] or ord(voyel) == 195:
        return "e"

    if voyel in ["ù"]:
        return "u"
        
    if voyel in ["ö"]:
        return "o"
        
    #~ print( "DBG: removeAccent: return: %s (ord:%s)" % (voyel, ord(voyel)) )
    return voyel
# removeAccent - end

        
class SentenceGeneratorFr:
    
    kTimePresent = 0
    kTimeImperfect = 1
    kTimeFuture = 2
    
    def __init__( self ):
        pass
        
    def conjugate_1st( self, nSubject0, strVerb, nTime = 0 ):
        skel = strVerb[:-2]
        aTimeEnd = [
                            ["e", "es", "e", "ons", "ez", "ent"],
                            ["ais", "ais", "ait", "ions", "iez", "aient"],
                            ["erai", "eras", "era", "erons", "erez", "eront"],
                        ]
        return skel + aTimeEnd[nTime][nSubject0]            
        
    def conjugate_2nd( self, nSubject0, strVerb, nTime = 0 ):
        skel = strVerb[:-2]
        aTimeEnd = [
                            ["is", "is", "it", "issons", "issez", "issent"],
                            ["issais", "issais", "issait", "issions", "issiez", "issaient"],
                            ["irai", "iras", "ira", "irons", "irez", "iront"],
                        ]
        return skel + aTimeEnd[nTime][nSubject0]            

    def conjugate_3rd( self, nSubject0, strVerb, nTime = 0 ):
        try:
            global listPeculiar_fr
            aTimeVerb = listPeculiar_fr[strVerb]
            return aTimeVerb[nTime][nSubject0]
        except KeyError: pass # not a peculiar verb
        except BaseException, err:  print( "ERR: conjugate_3rd: %s" % str(err) )
            
        if "oir" in strVerb[-3:]:
            # pouvoir: pouv-ant pouv-ons            
            skel = strVerb[:-3]
            if( not skel[-1] in voyel and skel[-2] in voyel and skel[-1] != 'l' ):
                if( nSubject0 < 3 and nTime == 0 ):
                    # sav-oir ==> sai
                    skel = skel[:-1] + 'i'
                #~ if( skel[-2:] == "av" and nTime == 2 ):
                if( nTime == 2 ):
                    skel = skel[:-1]
                    if( skel[-1] != 'u' ):
                        skel += "u"
                    else:
                        skel += "r"
                    skel += "r"
                aTimeEnd = [
                                    ["s", "s", "t", "ons", "ez", "ent"],
                                    ["issais", "issais", "issait", "issions", "issiez", "issaient"],
                                    ["ai", "as", "a", "ons", "ez", "ont"],
                                ]                
            else:
                # voul-oir #pouv-oir
                if( skel[-3:] == "oul" and nSubject0 < 3 and nTime == 0 ):
                    skel = skel[:-3] + "eu"
                aTimeEnd = [
                                    ["x", "x", "t", "ons", "ez", "ent"],
                                    ["ais", "ais", "ait", "ions", "iez", "aient"],
                                    ["irai", "iras", "ira", "irons", "irez", "iront"],
                                ]
            
        elif "ir" in strVerb[-2:]:
            # ouvrir : ouvr-ant; ouvr-ons
            skel = strVerb[:-2]
            if( skel[-1] == 'm' and nSubject0 < 3 ):
                skel = skel[:-1]
            if( not skel[-1] in voyel and not skel[-2] in voyel ):
                aTimeEnd = [
                                    ["e", "es", "e", "ons", "ez", "ent"],
                                    ["issais", "issais", "issait", "issions", "issiez", "issaient"],
                                    ["irai", "iras", "ira", "irons", "irez", "iront"],
                                ]                
            else:
                aTimeEnd = [
                                    ["s", "s", "t", "ons", "ez", "ent"],
                                    ["issais", "issais", "issait", "issions", "issiez", "issaient"],
                                    ["irai", "iras", "ira", "irons", "irez", "iront"],
                                ]
                            
        else:
            # -RE (comme METTRE : mett-ant; mett-ons)
            skel = strVerb[:-2]
            aTimeEnd = [
                                ["ais", "ais", "ait", "avons", "avez", "avent"],
                                ["issais", "issais", "issait", "issions", "issiez", "issaient"],
                                ["irai", "iras", "ira", "irons", "irez", "iront"],
                            ]            
            
        return skel + aTimeEnd[nTime][nSubject0]            
        return         
        
    def conjugate( self, nSubject0, strVerb, rTime = 0. ):
        """
        return a string with the conjugation of a verb
        - nSubject: subject 0..5
        """
        
        nTime = SentenceGeneratorFr.kTimePresent
        if( rTime < -10. ):
            nTime = SentenceGeneratorFr.kTimeImperfect
        elif( rTime > 10. ):
            nTime = SentenceGeneratorFr.kTimeFuture
        
        if "er" in strVerb[-2:]:
            return self.conjugate_1st( nSubject0, strVerb = strVerb, nTime = nTime )
        
        if "oir" in strVerb[-3:] or strVerb in listVerb_Ir3rd or not "ir" in strVerb[-2:]:
            #~ if # #~ devenir-aller-faire-devoir-valoir-sortir-mettre-vouloir
            return self.conjugate_3rd( nSubject0, strVerb = strVerb, nTime = nTime )
            
        return self.conjugate_2nd( nSubject0, strVerb = strVerb, nTime = nTime )
            
    def getAdjectifIntensity( self, rIntensity ):
        """
        return an intensity value
        - rIntensity: 1: beaucoup, 0: moyen, -1: pas du tout
        """
        
        #~ print( "getAdjectifIntensity: rIntensity: %s" % rIntensity )        
        
        # a list of sorted adjectiv
        aAdjectiv = [
            -1, "du tout",  # this is the minimal threshold to tell this
            0, "",
            1., "beaucoup",
        ]
        
        strLast = aAdjectiv[0+1]
        rIntensityLast = aAdjectiv[0]
        for i in range( 0, len(aAdjectiv), 2 ):
            if rIntensity < aAdjectiv[i]:
                return strLast
            strLast = aAdjectiv[i+1]
            rIntensityLast = aAdjectiv[i]
            
        out = ""
        
        # add intensificator
        #~ print( "rIntensity: %s" % rIntensity )
        #~ print( "rIntensityLast: %s" % rIntensityLast )
        rDiff = rIntensity-rIntensityLast
        while( rDiff >= 1. ):
            out += "tr�s "
            rDiff -= 1.
        out += strLast
        return out

    def getTimeWord(self, tic):
        import naoqitools
        strTimeStamp = time.strftime( "%Y_%B_%d_")
        timeZone = naoqitools.myGetProxy("ALSystem")
        timeZone.timezone
        timeZone.setTimezone("Etc/Universal")

        # choose the city of your timezone
        # Paris in default
        fuseau = 2

        H = time.strftime("%H")
        H = int(H) + fuseau

        if H > 24:
            H = H - 24;
        if H < 0 :
            H = 24 + H;

        strTimeStamp = strTimeStamp + str(H) + time.strftime("_%M" )

        strTimeStamp = strTimeStamp.split("_")
        if str(tic.year) == str(strTimeStamp[0]):
            if str(tic.month) in str(strTimeStamp[1]):
                if str(tic.day)in str(strTimeStamp[2]):
                    if str(tic.hour)== str(strTimeStamp[3]):
                        nbmin = int(strTimeStamp[4]) - int(tic.minute)
                        if nbhour > 1 :
                            return "il y a " + str(nbmin) +" minutes."
                        else:
                            return "� l'instant."
                        
                    else:
                        nbhour = int(strTimeStamp[3]) - int(tic.hour)
                        if nbhour > 1 :
                            return "il y a " + str(nbhour) +" heures."
                        else:
                            return "il y a une heure."
                else:
                    import speech 
                    day = speech.getWeekDayLibelle_En()
                    d1 =int(strTimeStamp[2])
                    d2 = int(tic.day)
                    nbday = d1 - d2
                    if nbday > 1 :
                        return "il y a " + str(nbday) + " jours."
                    else:
                        return "hier."
            else:
                import speech 
                month = speech.getMonthLibelle_En()
                m1 =([i for i in range(0,len(month)) if str(tic.month) in str(month[i])])[0]
                m2 =([i for i in range(0,len(month)) if str(strTimeStamp[1]) in str(month[i])])[0]
                nbmonth = m1 - m2
                if nbmonth > 1 :
                    return "il y a " + str(nbmonth) + " mois." 
                else:
                    return "le mois dernier." 
        else:
            nbyear = int(strTimeStamp[0]) - int(tic.year)
            if nbyear > 1:
                return "il y a " + str(nbyear) + " ans."
            else:
                return "l'ann�e derni�re"

    def generate( self, nSubject, strVerb, rIntensity = 1., rTime = 0., strOptionnalName = None ):
        """
        - rTime: temps en secondes ?
        - rIntensity: 0: neutral, 1: positive, 2: very positive, -1 negative
        - strOptionnalName: give the name of the actor, eg: "Alexandre"
        
        eg: 1, aimer, 1.: => j'aime
        eg: 2, aimer, 2.: => tu aimes beaucoup
        eg: 1, aimer, -1.: => je n'aime pas
        eg: 1, aimer, -2.: => je n'aime pas du tout
        """
        nSubject0 = nSubject-1
        aSubject = ["je", "tu", "il", "nous", "vous", "ils" ]
        aPronominal = ["me", "te", "se", "nous", "vous", "se" ]
        
        out = aSubject[nSubject0]
        if( strOptionnalName != None ):
            out = strOptionnalName
            
        out += " "
        bNeg = False
        if rIntensity < 0.:
            bNeg = True
        
        if( bNeg ):
            out += "ne "
            
        bPronominal = strVerb in pronominalFr
        if( bPronominal ):
            out += aPronominal[nSubject0] + " "
                    
            
        # elision before verb
        #~ if( nSubject0 ==0 and strVerb[0] in voyel ):
        strConjugateVerb = self.conjugate( nSubject0, strVerb, rTime )
        if( out[-2] in voyel and not out[-2] == 'u' and removeAccent(strConjugateVerb[0]) in voyel and out[-3] in ["j", "n", "m", "t"] ):
            if strOptionnalName == None or bNeg:
                out = out[:-2] + "'"
            
        out +=  strConjugateVerb

        if( bNeg ):
            out += " pas"
            
        # intensity
        try:
            if( rIntensity > 1. ):
                out += " " + self.getAdjectifIntensity( rIntensity - 1 )
            if( rIntensity < -1. ):
                out += " " + self.getAdjectifIntensity( rIntensity + 1 )
        except:
            print "INF : sentence_generator in generate : error in out + self.getAdjectifIntensity()"
            
        return out

    def innerTest( self ):
        from test import assert_check
        
        assert_check( self.getAdjectifIntensity( 1. ), "beaucoup" )
        assert_check( self.getAdjectifIntensity( -1. ), "du tout" )
        
        assert_check( self.generate( 1, "aimer", 1. ), "j'aime" )
        assert_check( self.generate( 2, "jouer", 1. ), "tu joues" )
        assert_check( self.generate( 3, "rigoler", 1. ), "il rigole" )
        assert_check( self.generate( 4, "plaisanter", 1. ), "nous plaisantons" )
        assert_check( self.generate( 1, "aimer", 1., strOptionnalName = "Alexandre" ), "Alexandre aime" )        
        
        assert_check( self.generate( 5, "rembourser", 2. ), "vous remboursez beaucoup" )
        assert_check( self.generate( 6, "assurer", -1 ), "ils n'assurent pas" )
        assert_check( self.generate( 1, "amuser", -2 ), "je ne m'amuse pas du tout" )
        
        assert_check( self.generate( 2, "amuser", 4 ), "tu t'amuses tr�s tr�s beaucoup" )
        assert_check( self.generate( 5, "nager", -4 ), "vous ne nagez pas du tout" )
        assert_check( self.generate( 5, "amuser", -1, -60 ), "vous ne vous amusiez pas" )
        assert_check( self.generate( 6, "papillonner", -1, 60 ), "ils ne papillonneront pas" )
        
        assert_check( self.generate( 1, "finir", 1. ), "je finis" )
        assert_check( self.generate( 2, "hair", 1. ), "tu hais" )
        assert_check( self.generate( 3, "franchir", 2., 60 ), "il franchira beaucoup" )
        assert_check( self.generate( 4, "convertir", 1. ), "nous convertissons" )
        
        # 3rd
        assert_check( self.generate( 1, "etre", 1. ), "je suis" )
        assert_check( self.generate( 2, "etre", 1. ), "tu es" )
        assert_check( self.generate( 3, "etre", 1. ), "il est" )
        assert_check( self.generate( 4, "etre", 1. ), "nous sommes" )
        assert_check( self.generate( 5, "etre", 1. ), "vous etes" )
        assert_check( self.generate( 6, "etre", 1. ), "ils sont" )

        assert_check( self.generate( 1, "etre", 1., 60. ), "je serai" )
        assert_check( self.generate( 4, "etre", 1., 60. ), "nous serons" )
        assert_check( self.generate( 6, "etre", 1., 60. ), "ils seront" )

        assert_check( self.generate( 1, "etre", 1., -60. ), "j'étais" )
        assert_check( self.generate( 4, "etre", 1., -60. ), "nous étions" )
        assert_check( self.generate( 6, "etre", 1., -60. ), "ils étaient" )
        
        assert_check( self.generate( 1, "avoir", 1. ), "j'ai" )
        assert_check( self.generate( 2, "avoir", 1. ), "tu as" )
        assert_check( self.generate( 3, "avoir", 1. ), "il a" )
        assert_check( self.generate( 4, "avoir", 1. ), "nous avons" )
        assert_check( self.generate( 5, "avoir", 1. ), "vous avez" )
        assert_check( self.generate( 6, "avoir", 1. ), "ils ont" )

        assert_check( self.generate( 1, "avoir", 1., 60. ), "j'aurai" )
        assert_check( self.generate( 4, "avoir", 1., 60. ), "nous aurons" )
        assert_check( self.generate( 6, "avoir", 1., 60. ), "ils auront" )

        assert_check( self.generate( 1, "avoir", 1., -60. ), "j'avais" )
        assert_check( self.generate( 4, "avoir", 1., -60. ), "nous avions" )
        assert_check( self.generate( 6, "avoir", 1., -60. ), "ils avaient" )        

        assert_check( self.generate( 1, "dormir", 1. ), "je dors" )
        assert_check( self.generate( 3, "dormir", 1. ), "il dort" )
        assert_check( self.generate( 4, "dormir", 1. ), "nous dormons" )

        assert_check( self.generate( 1, "ouvrir", 1. ), "j'ouvre" )
        assert_check( self.generate( 3, "ouvrir", 1. ), "il ouvre" )
        assert_check( self.generate( 4, "ouvrir", 1. ), "nous ouvrons" )
        
        assert_check( self.generate( 1, "savoir", 1. ), "je sais" )
        assert_check( self.generate( 6, "savoir", 1. ), "ils savent" )
        
        assert_check( self.generate( 1, "vouloir", 1. ), "je veux" )
        assert_check( self.generate( 4, "vouloir", 1. ), "nous voulons" )        
        assert_check( self.generate( 1, "vouloir", 1., -60 ), "je voulais" )
        
        assert_check( self.generate( 2, "savoir", 1., 60 ), "tu sauras" )
        assert_check( self.generate( 5, "savoir", 1., 60 ), "vous saurez" )
        
        assert_check( self.generate( 2, "pouvoir", 1., 60 ), "tu pourras" )
        assert_check( self.generate( 5, "pouvoir", 1., 60 ), "vous pourrez" )        
        assert_check( self.generate( 2, "vouloir", 1., 60 ), "tu voudras" )
        assert_check( self.generate( 5, "vouloir", 1., 60 ), "vous voudriez" )        
        
        assert_check( self.generate( 2, "ouvrir", 1., 60 ), "tu sauras" )
        assert_check( self.generate( 5, "ouvrir", 1., 60 ), "vous saurez" )        

        assert_check( self.generate( 2, "dormir", 1., 60 ), "tu sauras" )
        assert_check( self.generate( 5, "dormir", 1., 60 ), "vous saurez" )        

        assert_check( self.generate( 2, "mettre", 1., 60 ), "tu sauras" )
        assert_check( self.generate( 5, "mettre", 1., 60 ), "vous saurez" )        
        
        assert_check( self.generate( 1, "ouvrir", 1., 0 ), "tu sauras" )
        assert_check( self.generate( 4, "mettre", 1., 0 ), "vous saurez" )        
           
        assert_check( self.generate( 2, "venir", 1., 0 ), "tu sauras" )
        assert_check( self.generate( 5, "venir", 1., 0 ), "vous saurez" )
        assert_check( self.generate( 2, "venir", 1., -60 ), "tu sauras" )
        assert_check( self.generate( 5, "venir", 1., -60 ), "vous saurez" )
        assert_check( self.generate( 2, "venir", 1., 60 ), "tu sauras" )
        assert_check( self.generate( 5, "venir", 1., 60 ), "vous saurez" )        
# class SentenceGenerator - end

def autoTest():
    sg = SentenceGeneratorFr()
    sg.innerTest()
# autoTest - end
    
if( __name__ == "__main__" ):
    autoTest()
