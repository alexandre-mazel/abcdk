# -*- coding: utf-8 -*-

###########################################################
# Aldebaran Behavior Complementary Development Kit
# Data for object tools
# Author A. Mazel
# Aldebaran Robotics (c) 2010 All Rights Reserved - This file is confidential.
###########################################################

"Data for emotion tools (internal)"

print( "importing abcdk.object_list" );

#
# Some list of known object
#

# skul of name => [grabbable, walkable, climbable, pushable, specific action, [short explicit name - multilang], [funny comments - multilang] ]
# grabbable:
#  0: no
#  1: with one hand
#  2: with both hands
# walkable: can't walk straight to it
# climbable: (steppable) can't climb on it, then walk? (or half turn?)
# pushable: we can try to push it with hands
# throw_into: we can throw things on it
# specific action: an integer (ID) of some specific action

# but in fact, I should notice just the height, the weight, the fragileness, and so say: "if weight < 5 and not fragile => pushable"
listObject =  {

            "coquille": [0, False, False, False, False, -1, ["A box of Shelley pasta.", "Un paquet de coquillettes."], ["Woohoo, pasta!", "Chouette, des pates!"] ],
            "DevProg": [0, False, False, False, False, -1, ["A developer program flyer.", "Un tract du développeur programme."], ["Have you heard of the developer program? it's to teach me new tricks.", "Tu connais le dévelopeur program ? C'est pour m'apprendre des nouveaux tours",  ] ],
            "Lardon": [0, False, False, False, False, -1, [ "A package of bacon.","Un paquet de lardons."],["We could make a quiche or spaghetti carbonara.", "On pourrait faire une quiche, ou alors une tartiflette!" ] ],
            "beurre": [0, False, False, False, False, -1, ["A plate of butter.", "Une plaque de peur."], ["You ought to put that in the fridge, it's hot in here.","Tu devrais mettre ceci au frais, il fait très chaud ici." ] ], # # 5571: peur is better said than beurre
            "Farine": [0, False, False, False, False, -1, ["Some flour.", "Un paquet de farine."], ["What on earth are you doing with all this coke?", "Tu es fou! Qu'est ce que tu fais avec toute cette cocaine!"] ],
            "Jambon": [0, False, False, False, False, -1, ["Ham.", "Du jambon."], ["Oh look, ham!", "oh du jambon!"] ],
            "Saucise": [0, False, False, False, False, -1, ["a can of sausages with lentils.", "Une conserve de saucisses aux lentilles."],["Hmm, theses sausages look a bit ancient.", "Ouhlala, ca m'a l'air d'être du bon 10 ans d'ages tes saucisses aux lentilles."] ],
            "Nature": [0, False, False, False, False, -1, [ "4 yoghurts", "4 yaourts."], ["Yoghurt gives me tummy ache", "Beurk, des yaourts, c'est pas bon!"] ],
            "Javel": [0, False, False, False, False, -1, ["A carton of bleach.", "Un berlingot de Javel."], ["Watch out that's bleach.", "Attention, c'est de l'eau de javel" ] ],
            "Amande": [0, False, False, False, False, -1, ["A carton of almond milk soap.","Un berlingot de savon au lait d'amande."], ["Almond shower gel is good for my skin.", "Du lait d'amande pour la douche" ] ],
            "Nokia": [0, False, False, False, False, -1, ["A Nokia Navigator mobile.","Un téléphone Nokia Navigator."], [ "Alex, I've found your mobile.", "Alexandre, j'ai trouvé ton téléphone !" ] ],
            "Keys": [0, False, False, False, False, -1, ["A set of keys.","Un trousseau de clés."], [ "Alex, I've found your keys.", "Alexandre, j'ai trouvé tes clefs!" ] ],
            "Sigma": [0, False, False, False, False, -1, ["A Sigma bike computer.","Un compteur de vélo Sigma."], ["That's a strange place to leave a bicycle speedometer", "Oh, c'est bizarre de ranger un compteur de vélo, par terre !" ] ],
            "Cigarettes": [0, False, False, False, False, -1, ["A packet of cigarettes.","Un paquets de cigarettes."], [ "You shouldn't smoke it's bad for you!", "Tu devrais arrêter de fumer, c'est une dangeureuse habitude!" ] ],
            "Router": [0, False, True, False, False, -1, ["A kinsys router box.","Une boite deuh roue-teur linqueuh cise."], ["Finally I can go online.", "Je vais enfin pouvoir me connecter a l'internet" ] ],
            "Water":[2, False, False, False, False, -1, ["A glass of water.","Une bouteille d'eau."], [ "Drink!", "A boire!" ] ],
            "DoorMat": [0, True, False, False, False, -1, ["A doormat","Un paillasson."], ["I could wipe my feet on this doormat.", "Mon paillasson, je pourrais m'essuyer les pieds dessus!" ] ],
            "Book_PracticalRobotics": [0, False, False, False, False, -1, ["A robotics book.","Un livre sur la robotique."], ["Robotics is the future.", "C'est pratique la robotique." ] ],
            "Harem": [0, False, False, False, False, -1, ["A box of turkish candies.","Une boiteuh de loukoum."], ["Turkish Delight, yum.", "Allons voir ce qu'il y a dans ce harem de loukoum." ] ],
            "GreenBall": [0, True, False, False, False, -1, ["A green ball.","Une balle verte."], ["Shoot, shoot, shoot.","Shoote, shoote, shoote." ] ], # we wish to walk in the ball so we shoot it.
            "PenPot": [1, False, False, False, False, -1, ["A pencil jar.","Un pot a crayons."], [ "Pencil Jar", "Des crayons." ] ],
            "NaoCube": [0, False, False, False, False, -1, ["A naomark cube.","Un cube avec des naomarks."], ["My cube!", "Mon cube!" ] ],
            "Tortelloni": [2, False, False, False, False, -1, ["A box of prepared tortelloni with ricotta and spinach.","Une boite de tortelloni préparées avec de la ricotta et des épinards."], ["Not pasta again.","On mange encore des pates ce soir?" ] ],
            "Congos": [0, False, False, False, False, -1, ["Some reggae music.","Un CD de réggae."], [ "I've found the Reggae CD.", "J'ai trouvé le cd de Manu." ] ],
            "Rigoletto": [0, False, False, False, False, -1, ["Some classical music.","Un CD de musique classique."], ["I've found the classical CD", "J'ai trouvé ton cd d'opéra." ] ],
            "Youri": [0, False, False, False, False, -1, ["A disk of Youri.","Un CD de Youri."], [ "I've found the Youri CD", "J'ai trouvé le cd de Youri." ] ],
            "Poster_z6po": [0, False, False, False, False, -1, ["A C-3-P-O Poster.","Un postaire de Z-6-P-Oh."], [ "It's my ancestor", "C'est mon grand père." ] ],
            "TasseChaussette": [1, False, False, False, False, -1, ["A bulk of socks.","Un tas de chaussettes."], ["What's that sock doing here" , "Mais que fait cette chaussette ici?"] ],
            "NaoDuck": [1, False, False, False, False, -1, ["a little ducky.","Un petit canard."], [ "My little ducky.", "Mon petit canard!" ] ],
            "Organigramme": [0, False, False, False, False, -1, ["An organisation chart.","Un organigramme."], ["What a beautiful organisation chart","Oh le joli organigramme avec plein de couleurs." ] ],
            "kotobukiya": [0, False, False, False, False, -1, ["A box of japanese figurine.", "Une boite de figurine japonaise."], [ "A small japanese toy." , "Oh une petite figurine japonaise."] ],
            "Milka_TendresMoments": [0, False, False, False, False, -1, ["Some chocolate.","Une tablette de chocolat au laits milka."], ["Some chocolate.", "hum du chocolat." ] ],
            "DiaryOfDreams": [0, False, False, False, False, -1, ["A flyer of Diary Of Dreams.","Un fla-yeur de da yeuri off drimseuh."], [  "I don't know this music band.", "Un fla-yeur d'un groupe de musique que je ne connais pas." ] ],
            "Box_SweetGum": [0, False, False, False, False, -1, ["Chewing gum", "Des chewing gum." ], ["Chewing gum", "Des chewing gum." ] ],
            "Magasine_science_et_vie": [0, False, False, False, False, -1, [ "A science magazine.","Un magasine de science & vie."], ["A science magazine." , "Un magazine scientifique."] ],
            "DecapsuleurAllemand": [0, False, False, False, False, -1, ["A bottle opener.", "Un decapsuleur."], ["A bottle opener.", "Un decapsuleur." ] ],
            "PhotoCortoBonnet": [0, False, False, False, False, -1, ["A baby picture.","Une photo d'un bébé."], ["A baby picture.","Une photo d'un bébé." ] ],
            "TractDonDuSang": [0, False, False, False, False, -1, ["A leaflet for blood donation.","Un tract pour le don du sang."], ["A leaflet for blood donation.","Un tract pour le don du sang." ] ],
            "Pepito": [0, False, False, False, False, -1, ["A pack of pepito.","Un paquet de pépito choco-pépites." ], [ "Hey pepito!", "Hail pépito!" ] ],
            "Icon_Garbage": [0, False, False, False, True, -1, ["Some garbage collector.", "Une boîte de quouality street." ], ["Some garbage collector.", "Un emballage recyclé en poubelle." ] ],
            "HuileTournesol": [0, False, False, False, False, -1, ["Some sunflower oil.", "De l'huile de tournesol."], [ "Some sunflower oil.", "De l'huile de tournesol" ] ],
            "AlcoolABruler": [0, False, False, False, False, -1, ["Methylated spirits!","De l'alcool a bruler." ], [ "Methylated spirits!","De l'alcool a bruler." ] ],
            "ramette": [0, False, False, True, False, -1, ["A paper ream.", "Une ramette de papier."], [ "A paper ream.", "Une ramette de papier." ] ],
            "chinoise": [0, False, False, False, False, -1, ["A poster depicting two nude women in the process of touching.","Un poster représentant deux femmes dénudées en train de se toucher."], ["Oh, some japanese girls.", "Oh, des japonaises." ] ],
            "Medic_": [0, False, False, False, False, -1, ["A box of %s.", "Une boite de %s."], [ "You look sick, that's right, but don't take too much medicine.", "C'est vrai que tu as l'air un peu malade, mais n'abuse pas des médicaments, quand même." ] ],
            "Delichoc": [0, False, False, False, False, -1, ["A box of milky Dailichoc.", "Des délichoque au chocolat au lait." ], ["A box of milky Dailichoc.", "Des délichoque au chocolat au lait." ] ],
            "Gavottes": [0, False, False, False, False, -1, ["Lace pancakes with milk chocolate.", "Des crêpes dentelles au chocolat au lait."], [ "Lace pancakes with milk chocolate.", "Des crêpes dentelles au chocolat au lait." ] ],
            "Cassoulet": [0, False, False, False, False, -1, [ "A tin of french cassoulet.", "Une boite de cassoulai."], [ "A tin of cassoulet: a french fat specialities with beans." , "Tai, du bang cassoulai!" ] ],
            "HaricotsVerts": [0, False, False, False, False, -1, ["A green french bean", "Une boite d'haricots verts."], ["green french bean", "Une boite d'haricots verts, parfaits pour atteindre les 5 fruits et légumes par jours." ] ],
            "Conserve_Lentilles": [0, False, False, False, False, -1, ["Some lentils.", "Des lentilles a l'auvergnate."], [ "Some lentils.", "Des lentilles a l'auvergnate." ] ],
            };
# listObject - end

idx_grabbable = 0;
idx_walkable = 1;
idx_climbable = 2;
idx_pushable = 3;
idx_throw_into = 4;
idx_special_action = 5;
idx_desc = 6;
idx_comment = 7;
            
def getObjectInfo( strName ):
    "return info on an object or []"
    for k, v in listObject.iteritems():
        if( k in strName ):   
            return v;
    return [];
# getObjectInfo - end

def autoTest():
    print str( getObjectInfo( "Cigarettes Lucky Strike" ) );
# autoTest

if __name__ == "__main__":
    autoTest();