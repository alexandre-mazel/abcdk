# -*- coding: utf-8 -*-

###########################################################
# Aldebaran Behavior Complementary Development Kit
# Sentence
# Aldebaran Robotics (c) 2010 All Rights Reserved - This file is confidential.
###########################################################

"Sentence tools: sentence generator and stuffs"
print( "importing abcdk.sentence" );

import arraytools


def concateneRandom( listlistword ):
    "take a list of word list and concatene it"
    "each list contains a word and an optionnal probability (see array.chooseOneElem)"
    # strSentence = arraytools.chooseOneElem( 'hello' );
    # strSentence = arraytools.chooseOneElem( ['hello', 'goodbye'] );
    # strSentence = arraytools.chooseOneElem( ['sometimes', ['often',10] ] );    
    strSentence = "";
    for aList in listlistword:
        strSentence += arraytools.chooseOneElem( aList ) + ' ';
    return strSentence;
# concateneRandom - end

def wordlist_AddOccurenceModel( listwords, nOccurenceModel = 10 ):
    "add occurence model to a word list"
    # nOccurenceModel == 10: pick always one word
    # nOccurenceModel == 3: pick nearly always one word
    # nOccurenceModel == 2: pick sometimes one word
    # nOccurenceModel == 1: pick rarely one word
    # nOccurenceModel == 0: pick never one word (no use)!    
    nbrTotalWord = len( listwords );
    if( nOccurenceModel == 10 ):
        pass # nothing to do
    elif( nOccurenceModel == 3 ):
        listwords += "";
    elif( nOccurenceModel == 2 ):
        listwords.append( ["",nbrTotalWord] );
    elif( nOccurenceModel == 1 ):
        listwords.append( ["",nbrTotalWord*10] );
    else:
        return ""; # case 0
    return listwords;
# wordlist_AddOccurenceModel

def wordlist_things( nOccurenceModel = 10 ):
    listword = ["cette chose", "ce truc", ["ce machin",5], "ce zigouigoui", "cette drole de chose", "se bidule", "se bitonio", "cet objet", "ce bazar", "cette amas bizarre", "ce binhsse", "cette cochonnerie" ];
    return wordlist_AddOccurenceModel( listword, nOccurenceModel );
# wordlist_things - end

def wordlist_interjection( nOccurenceModel = 2 ):
    "return a list word of a certain type/function, using some frequency model"
    listword  = [ "Ah mais", "oh", "ah bein ca", "je me disait bien, mais","oh la la la", "crénom", "vingt dieux", "parbleu", "ca alors", "ohlolo", "croudablou", "hey!", "ah ca donc" ];
    listword = wordlist_AddOccurenceModel( listword, nOccurenceModel );
    return listword;
# wordlist_interjection - end

def wordlist_bonus( nOccurenceModel = 2 ):
    "return a list word of a certain type/function, using some frequency model"
    listword  = ["grave.", "c'est bizarre.", "ne trouves tu pas?",  "tro ouf!",  "trop zarbi, non?", "plom.", "mince!", "peuchère." ];
    listword = wordlist_AddOccurenceModel( listword, nOccurenceModel );
    return listword;
# wordlist_bonus - end

def generatePhraseWithAdjectif( listAdj ):
    "generate a sentence desbcribing an adjectif"
    introduction = [ ["",10], "je trouve que", "actuellement", "oh", "ouais bein moi", "en ce moment", "aujourd'hui", "il parait que", "certains m'ont dit que", "mon petit doigt m'a dit que" ];
    subject = [ ["j'ai",3]];
    adverbe = [ ["",6], "un peu", "beaucoup", "grave", "tres", "de temps en temps"];
    # adjectif as params
    amplificateur = [ ["", 7], "trop grave", "depuis longtemps", ", si si je te jure", "beaucoup"];
    
    return concateneRandom( [introduction, subject, adverbe, adverbe, listAdj, amplificateur] );
# generatePhraseWithAdjectif - end


    
def generateQuestionAboutThings( aThingsDescriptor ):
    "generate a sentence about something"
    subject = ["quel est", "qu'est ce que c'est que", "je n'ai jamais vu", "je ne connais rien qui ressemble a", "une fois j'ai vu quelque chose qui me rappelle" ];
    adverbe = [ ["",6], ""];
    things = wordlist_things();
    amplificateur = [ ["", 50], "pourri", "moche", "dans ma vie", ", vu cette semaine", "tel qu'aujourd'hui", "disparu depuis longtemps", "en train de trainer dans le coin", "a cette place", "près de ma main", ", sauf dans un avion", "qui ressemble a ca", "qui traine", "a sa place", ", vu récemment", ", a part dans une brocante", "qui ressemble a rien qui existe"];
    
    bonus = wordlist_bonus(2);
    
    return concateneRandom( [wordlist_interjection(), subject, adverbe, things, aThingsDescriptor, amplificateur, "?", bonus ] );
# generateQuestionAboutThings - end

def generateComparison():
    "generate comparisons 'comme un nain dans un avion'"
    adj = [ ["comme",5], "autant que", "plus que", "largement plus que", "un peu comme", "légèment plus que", "identique a" ];
    object = ["une planche", "un robot", "un avion", "une pomme", "un train", "un vélo", "une mobilette", "un couteau", "une fourchette", "un mur", "la mer", "un boulon", "un vibromasseur", "un vilebrequin", "un supermarché", "un cadavre", "une balle", "un pistolet", "un ordinateur", "une plaie"];
    name = ["Ferdinand", "Céline", "Alexandre", "Jéme", "Flora", "Manuel", "Julien", "Inetissar", "Valentin", "Bruno"];
    human = ["un nain", "un monstre", "un magicien", "un pretre", "un homme", "un bébé", "ta mêre", "une ombre", "un vieillard", "un cadavre", "un fou", "une belle femme", "un bogosse", ];
    animal = ["un ver de terre", "ton chien", "une girafe", "une lionne", "un cafard"];
    star = ["la belle mère de Sarkozi", "le pape", "Zinédine Zidane", "Nao", "Jonnny Halidai" ];
    subject = object + name + animal + human + star;
    comp = [ ["qui",6] ];
    action = ["cuisinerait", "taperait", "mangerait", "fumerait", "pisserait sur", "jetterais", "irait plus vite que" , "vomirait", "aurait une relation sexuelle avec", "aurait une relation sexuelle tarifée, avec", "aurait une relation professionnelle avec", "conduirait", "piloterait", "volerait", "dévorerait", "torturait"];
    return concateneRandom( [adj, subject, comp, action, subject] );
# generateComparison - end

def generateRecognise( aThingsDescriptor ):
    "generate recognise 'ca ressembla a (mon jouet)"
    things = wordlist_things();    
    recognise = [ "a la même tête que", "ressemble a", ", ca ressemble a", "on dirait", "a le style de", "ressemble de loin a" ];
    return concateneRandom( [wordlist_interjection( 1 ), things,  recognise, aThingsDescriptor] );
# generateComparison - end


def generateBof():
    "generate a bof adulescent sentence"
    bof = [ "c'est bof", "c'est presque nul", "c'est pas chant-mé", "ca craint", "c'est pas terrible", "ca n'a rien de particulierement intéressant", "c'est limite crainiausse", "ca casse pas 3 pattes a un canard", "je trippe pas grave", "on dirait un film de Rohmére", "Ennuyeux, comme une radio qui diffuserait un film muet", "c'est quelquonque"  ];
    bonus = wordlist_bonus(2);
    return concateneRandom( [bof , "!", bonus] );
# generateComparison - end

def autoTest():
    print( generateBof() );
    print( generateComparison() );
    print( generateQuestionAboutThings( "rose" ) + generateBof() ); # eg: parbleu une fois j'ai vu quelque chose qui me rappelle  ce truc rose  , plom. ? ca n'a rien de particulierement int�ressant ! peuch�re. 
    print( generateQuestionAboutThings( "grisatre" ) );
# autoTest - end
    
# autoTest();