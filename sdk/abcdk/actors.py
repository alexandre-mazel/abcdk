# -*- coding: utf-8 -*-

###########################################################
# Aldebaran Behavior Complementary Development Kit
# Actors
# @author The usage team - Living Labs
# Aldebaran Robotics (c) 2016 All Rights Reserved - This file is confidential.
###########################################################

import html_manager
import mutex
import pathtools
import time

#import dill used to save data => no used here (save and load in txt instead)

try:
    import dill     # sudo pip install dill or scp on the robot to .local/lib/python2.7/site-packages
except: 
    print "WRG : Failed importing dill (actors.py)"
    pass

PATH_ABSOLUTE_TO_PICTURE_DIRECTORY = "/home/nao/data2/faces/"
PATH_WEB_TO_PICTURE_DIRECTORY = "/data2/faces/"
PATH_TO_SAVE = pathtools.getCachePath()
PATH_TO_SAVE_TXT = pathtools.getCachePath() + "actorsSave.txt"


class Actor():
    '''
    Class Actor defined by : idNumber,fistName,lastName,gender
    method :    -setFirstName // getFirstName
                -setLastName // getLastName
                -setGender // getGender
                -getId
                -addTicket
                -getTicket
                -printTicket
                -pickPicture
                -
    '''
    def __init__(self, idNumber=None, firstName=None, lastName=None , gender = None):    
        
        self.idNumber = idNumber
        
        if firstName:
            self.firstName = firstName.title()
        else :
            self.firstName = ""
        if lastName:
            self.lastName = lastName.upper()
        else :
            self.lastName = ""    
            
        self.gender = gender
        self.tickets = []
        #~ filetools.makedirsQuiet( PATH_TO_PICTURE_DIRECTORY )
        self.pictureFileName =  self.firstName.lower() + "__" + self.lastName.lower() +".jpg"
        self.pickPicture()
        pass
    
    def __str__(self):
        return "Actor number : %s ,\t first: %s, name: %s \t (gender : %s) " % (str(self.idNumber) , self.firstName.title() , self.lastName.upper(), self.gender )

    def addTicket(self, newTicket):
        # add a new tickets to the Actor's tickets list
        self.tickets.append(newTicket)      
  
    def getFirstName(self):
        #return the first name of the actor
        return self.firstName
        
    def getGender(self):
        #return the gender of the actor
        return self.gender

    def getId(self):
        #return the Id number of the Actor
        return self.idNumber
      
    def getLastName(self):
        #return the last name of the actor
        return self.lastName    
       
    def getTicket(self, ticketsId):
        # This method return all the tickets corresponding to the tickets Id (can pass several tickets Id)
        # arg : tickets Id list ex [1,5,8]
        # return list of tickets found  

        #check if they pass a list of tickets Id as argument
        if not isinstance( ticketsId, list ):
            ticketsId = [ticketsId]
        
        tmpList = []
        ticketfound = ""

        # check for each tickets if there were found
        for tmpTicket in self.tickets :
            if tmpTicket[0]  in ticketsId :
                tmpList.append(tmpTicket)
                ticketfound += "%s ," % str(tmpTicket[0])

        #check if all the searched tickets were found
        if tmpList :
            if len(tmpList) < len(ticketsId):
                print "INF (in actors.getTicket) : Not all the tickets were found, only tickets number : %s " % (ticketfound)
            return tmpList
        else :
            print "INF (in actors.getTicket): Ticket  number : %s not found for this Actor. " % (ticketsId)
            return None
                    
    def pickPicture( self ):
        import facerecognition
        strHuman = self.firstName.lower() + "_" + self.lastName.lower()
        print( "INF: pickPicture: looking for a nice picture of '%s'" % strHuman )
        try:
            strNiceFace = facerecognition.findNiceFace( "/tmp/rec_faces_cropped/", strHuman )
            if( strNiceFace != None ):
                import filetools
                filetools.makedirsQuiet( PATH_ABSOLUTE_TO_PICTURE_DIRECTORY )
                filetools.copyFile( strNiceFace, PATH_ABSOLUTE_TO_PICTURE_DIRECTORY + self.pictureFileName, True )
        except:
            print("INF: No file /tmp/rec_faces_cropped/")

    def printTicket(self):
        #print all the tickets of the Actor
        if self.tickets:
            print "Ticket : "
            for ticket in self.tickets :
                print ticket

    def setFirstName(self, firstName = None ):
        #set the first  name of the actor
        self.firstName = firstName.title()

    def setGender(self, gender = None ):
        #set the gender of the actor
        self.gender = gender

    def setLastName(self, lastName ):
        #set the  last name of the actor
        self.lastName = lastName.upper()    
                         
#end of Actor class        


class ActorsManager():
    '''
    Class ActorsManager defined by : actorList,nextActorId,currentActor,currentActorUTC
    allows us to manage a group of Actors
    method :    -getCurrentActor // setCurrentActor
                -timeDiffSecUTC
                -printActors
                -createNew
    '''   
    def __init__(self, actorList =None):
        #mutex use to create a new actor Id
        self.mutexCreateNew = mutex.mutex()

        if actorList :
            self.actorList = actorList
        else:
            self.actorList = []
        
        self.nextActorId = 1 
        self.currentActor = -1
        self.currentActorUTC = time.time()

        #loading the actor from the sevor 
        # self.loadActors()# use dill (=> import dill)
        self.loadActorsFromTxt()

    def __str__( self ):
        # return all the Actors in actorList

        strOut = "Actors, %d actor(s):\n" % len(self.actorList)
        for a in self.actorList:
            strOut += str(a) + "\n"
        return strOut

    def addTicket(self ,idnum ,ticket):
        # Add a ticket to an Actor determined by its identity number
        # input :   -actors identity number
        #           -ticket to add (Ticket class from ticket.py)

        # check if no id number or id number < 0
        if (not (idnum == None or idnum < 0) ):
            for actor in self.actorList :
                 if (actor.idNumber == idnum):
                    actor.addTicket(ticket)
            # self.saveActors()#use dill
            self.saveActorsToTxt()
        else:
            print "WRG in ActorsManager.addTicket: WRONG Actor Id number passed as argument "
   
    def clearActors(self):
        #clear the actors saved in the text file located at PATH_TO_SAVE_TXT
        try:
            open(PATH_TO_SAVE_TXT, 'w').close()
            #reset nextActorId and actorList
            self.actorList = []
            self.nextActorId = 0
        except:
            print ("ERR :in ActorsManager.clearActors : Failed to clear the txt file ")
        

    def createNew(self, newActor=None, firstName=None, lastName=None , gender=None):        #Create a new actor and add it to the Actors list
        # save it in PATH_TO_SAVE_TXT
        # input :   -new actor firstName AND lastName AND gender
        #           -OR newActor (class Actor ) 
        #return the last created actors

        if newActor :
            newActor.idNumber =  self.getNewActorId()
            self.actorList.append( newActor )    
        else : 
            self.actorList.append(Actor(self.getNewActorId(), firstName, lastName , gender ))

        #save the actor list on the servor
        # self.saveActors()#using dill
        self.saveActorsToTxt()
        return self.actorList[-1]
       
    def getCurrentActor(self):
        # Return the current Actor
        # If last actor not seen for number of second set in timeDiffSecUTC return -1

        if (self.timeDiffSecUTC(self.currentActorUTC)):
            self.setCurrentActor(-1)
        return self.currentActor    

    def getActors(self, actorsId = None ,firstNameList=None, lastNameList=None , genderList=None, ticketKeywordList = None):
        """
        Input :     -getActorsactorsId: int or array of int
                    -firstNameList, lastNameList string
                    -
        """
        #return the list of actors corresponding to 
        if not isinstance( actorsId, list ):
            actorsId = [actorsId]

        tmpMatchingActors = []

        #check for each actors
        for actor in self.actorList :
            flagMatch = True

            if actorsId :
                if (int(actor.idNumber) not in actorsId):
                    flagMatch= False
                    continue

            if firstNameList :
                for i in range(len(firstNameList)):
                    firstNameList[i]=firstNameList[i].title()
                    
                if (actor.firstName.title() not in firstNameList):
                    flagMatch= False
                    continue    

            if lastNameList :
                for i in range(len(lastNameList)):
                    lastNameList[i]=lastNameList[i].upper()                
                if (actor.lastName.upper() not in lastNameList):
                    flagMatch= False
                    continue  

            if ticketKeywordList:
                for keyword in ticketKeywordList : 
                    flagKeyword = False
                    #check if keyword inside one of the actor's tickets
                    for ticket in actor.tickets:
                        if (keyword.lower() in ticket):
                            flagKeyword =True
                            #~ print "INF : Keyword %s found in tickets % s" % (keyword,ticket[0])
                            break
                    if not flagKeyword: 
                        flagMatch= False
                        continue

            # add the actor to the list if it passed all the step         
            if flagMatch :
                tmpMatchingActors.append(actor)
        # Return the result if some Actors matched the argument        
        if tmpMatchingActors:
            return tmpMatchingActors
        else :
            print "INF : No matching actors found "
            return None

    def getNewActorId(self):
        #return a new actor Id based on self.nextActorId (protected by a mutex)
        # then increase this number by one 

        while self.mutexCreateNew.testandset() == False:
            print " INF : in ActorsManagers.getNewActorId : Waiting for the mutex to be unlocked"
            time.sleep( 0.01)
        
        nId = self.nextActorId
        self.nextActorId += 1
        self.mutexCreateNew.unlock()
        return nId    
        
    def loadActors(self):
        #load the actor list from the servor using dill
        try:
            with open(PATH_TO_SAVE+'actorList.pkl', 'rb') as f:
                self.actorList = dill.load(f)
                self.nextActorId = dill.load(f)
                self.currentActorUTC = dill.load(f)
        except :
            print " WRG : File not found (loadActors)"
            pass

    def loadActorsFromTxt(self): 
        # LOAD the actors list and tickets in a txt file located at PATH_TO_SAVE_TXT
        # each actors use one line
        # For each lines, actor's information and tickets are separrated by  '///''
        # actor's information are separated with ':'
        # actor's ticket field are separated with ','
        # eg : 
        #2:Edo:LAGRUE:ProtoTeam
        #///None,1462528408.88,2016,May,Fri,6,11,53,28,None,None,None,None,None,None,None,coucou5,none,none,none,none,None,None,None,None,None,False,None,
        #///None,1462528408.88,2016,May,Fri,6,11,53,28,None,None,None,None,None,None,None,coucou6,none,none,none,none,None,None,None,None,None,False,None,

        self.actorList = []

        #open the file in read mode
        try:
            with open(PATH_TO_SAVE_TXT,'r') as f:
                content = f.readlines()
        except:
            print " WRG : actors : loadActorsFromTxt : File not found  :  %s" %PATH_TO_SAVE_TXT
            return

        # if the file is not empty, Browse each line of the file (corresponding to one Actor)
        if content :
            import ticket
            for line in content :

                #separate the actor info and ticketS (separated by '///)
                lineContent = line.split('///')

                # Extract and Add actor info
                actorInfo = lineContent[0]
                # Extract all the actor's information (separated by ':')
                # Then create an actor (class Actor) with these informations
                firstLineContent =actorInfo.split(':')
                self.actorList.append(Actor(idNumber = firstLineContent[0], firstName=firstLineContent[1], lastName=firstLineContent[2] , gender = firstLineContent[3]))
                
                # If there is some tickets save associated to this actors (on the same line)
                # Add each tickets to the actors
                if len(lineContent)>1 :
                    actorTickets = lineContent[1:]

                    for rawTicket in actorTickets :
                        dataTicket = rawTicket.split(',')
                        tmpTicket = ticket.Ticket(data=dataTicket)
                        #add ticket to actor 
                        self.addTicket( firstLineContent[0] ,tmpTicket)

        #set the next actor Id according to the maximum of the id number within the loaded list               
        if self.actorList:
            self.nextActorId = max(int(actor.idNumber) for actor in self.actorList)+1
        else :
            self.nextActorId = 0
        self.saveActorsToTxt()
        print "Actors loaded from txt file located at : %s" % PATH_TO_SAVE_TXT

        # f.close()

    def printActors(self):
        #print all the actors
        for actor in self.actorList:
            print "printActors :" + actor.__str__()  

    def removeLastActors(self):
        # Read the save file located at PATH_TO_SAVE_TXT
        # copy all the line except the last one (corresponding to the last actors)
        readFile = open(PATH_TO_SAVE_TXT)
        lines = readFile.readlines()
        readFile.close()

        w = open(PATH_TO_SAVE_TXT,'w')
        w.writelines([item for item in lines[:-1]])
        w.close()
        # load Actors to refresh the actual attribut 
        self.loadActorsFromTxt()

    def saveActors(self):
        #save the actor list on the servor using dill
        try:
            with open(PATH_TO_SAVE+'actorList.pkl', 'wb') as f:
                dill.dump(self.actorList, f)
                dill.dump(self.nextActorId, f)
                dill.dump(self.currentActorUTC, f)
        except BaseException, err:
            print( "ERR: ActorsManager.saveActors: error while saving: %s" % str(err) )    

    def saveActorsToTxt(self):
        # SAVE the actors list and tickets in a txt file located at PATH_TO_SAVE_TXT
        # each actors use one line
        # For each lines, actor's information and tickets are separrated by  '///''
        # actor's information are separated with ':'
        # actor's ticket field are separated with ','
        # eg : 
        #2:Edo:LAGRUE:ProtoTeam
        #///None,1462528408.88,2016,May,Fri,6,11,53,28,None,None,None,None,None,None,None,coucou5,none,none,none,none,None,None,None,None,None,False,None,
        #///None,1462528408.88,2016,May,Fri,6,11,53,28,None,None,None,None,None,None,None,coucou6,none,none,none,none,None,None,None,None,None,False,None,



        with open( PATH_TO_SAVE_TXT,'w') as myfile:
            
            #for each actors
            for actor in self.actorList :
                # Write actor information (firstName,...)
                myfile.write( str(actor.idNumber) +":")
                myfile.write( actor.firstName +":")
                myfile.write( actor.lastName +":")
                myfile.write( str(actor.gender) )
                import ticket
                actorTickets = None
                actorTickets = ticket.ticketsManager.findTickets([["source",str(actor.getId())]])
                
                if actorTickets != None :
                    actor.tickets = actorTickets.memory

                # Write actor's tickets
                if actor.tickets :
                    for ticket in actor.tickets:
                        myfile.write( "///")
                        tmpdata = ticket.getData()
                        for data in tmpdata :
                            myfile.write( str(data) +",")

                #Start a new line for the next actor except if actor is last actors
                if actor.idNumber != self.actorList[-1].idNumber :
                    myfile.write("\n")

        # myfile.close()

    def setCurrentActor(self, Id ):
        # Set the current actor according to 
        self.currentActorUTC = time.time() 

        if( self.currentActor != int(Id) ):
            print( "INF: ActorsManager.setCurrentActor: new current actor : '%s'" % Id )
            self.currentActor = int(Id)
            #refresh image of human
            self.actorList[self.currentActor].pickPicture()
            # change human face and give id
            html_manager.showHumanFace(idH = int(Id))
        else:#same current actors
            return
        
    def timeDiffSecUTC(self, timeUTC):
        # Return true if difference between current time and the one passed as argument lower that the "limitTime" value in second
        # Input : 
        limitTime = 10
        if ( (time.time() - timeUTC) > limitTime ):
            return True
        return False        
        
#end of ActorManager class

# SINGLETON (use actorsManager when call in a function, NOT ActorsManager)
actorsManager = ActorsManager() # abcdk.actor.actorManager.createNewActors() => a new id

def testActor():
    print "-------------testActor()---------------"
    
    newActor = Actor(idNumber=12, firstName="hopias", lastName="PROTOLAB", gender = "ProtoTeam")
    print newActor
    newActor.setName(firstName= "PROTOLAB ROCKS!!!")
    print newActor
    
    print"--addTicket(self, newTicket)---"
    newActor.addTicket([0,"coucou",15,18])
    newActor.addTicket([1,"salut","eureka",28])
    print newActor.tickets
    print 15 in newActor.tickets[0]
    print 15 in newActor.tickets[1]
    print "--getTicket---"
    print newActor.getTicket([0,1])
    print newActor.getTicket([0,2])
    
def testActorManager():
    print "---------------create-----------------"
    actors = ActorsManager ()
    # actors.clearActors()
    actors.printActors()
    print "----------after print------------then creat all actors "
    actor1 = Actor( firstName="hopias", lastName="PROTOLAB", gender = "ProtoTeam")
    actor2 = Actor( firstName="Alex", lastName="Mazel", gender = "ProtoTeam")
    actor3 = Actor( firstName="Edo", lastName="Lagrue", gender = "ProtoTeam")
    actor4 = Actor( firstName="Max", lastName="Caniot", gender = "ProtoTeam")

    print "----------after create------------add actors"
    
    actors.createNew(newActor=actor1)
    print "65465143514684684135143514688468416846819814681468"
    print actor1.idNumber
    actors.addTicket( actor1.idNumber, ticket.Ticket(place="coucou1"))
    actors.addTicket( actor1.idNumber, ticket.Ticket(place="coucou2"))
    actors.createNew(newActor=actor2)
    actors.addTicket( actor2.idNumber, ticket.Ticket(place="coucou3"))
    actors.addTicket( actor2.idNumber, ticket.Ticket(place="coucou4"))
    actors.createNew(newActor=actor3)
    actors.addTicket( actor3.idNumber, ticket.Ticket(place="coucou5"))
    actors.addTicket( actor3.idNumber, ticket.Ticket(place="coucou6"))
    actors.createNew(newActor=actor4)
    actors.addTicket( actor4.idNumber, ticket.Ticket(place="coucou7"))
    actors.addTicket( actor4.idNumber, ticket.Ticket(place="coucou8"))
    print "----------after print 2------------"

    actors.printActors()

    print "----------after print 3------------"
    
    # actors.saveActors()
    # print "------------loading--------"
    # actors222 = ActorsManager ()
    # actors222.loadActors()
    # print"---print-----"
    # actors222.printActors()
    # print actors222.nextActorId
    #~ actors.createNew(actor2)
    #~ actors.createNew(actor3)
    #~ actors.createNew(actor4)
    #~ actors.createNew(actor1)
    #~ actors.createNew(actor2)
    #~ actors.createNew(actor3)
    #~ actors.createNew(actor4)
    
    
    #~ print "---------------print-----------------"

    #~ actors.printActors()
    
    #~ print"-----getActors()---actorsId--"
    #~ #(self, actorsId = None ,firstNameList=None, lastNameList=None , genderList=None, ticketKeywordList = None):
    #~ matchingActors = ActorsManager(actorList =actors.getActors(actorsId=[1,3]))
    #~ matchingActors.printActors()
    #~ print"-----getActors()---firstNameList--"
    #~ matchingActors = ActorsManager(actorList =actors.getActors(firstNameList=["Alex","Max"]))
    #~ matchingActors.printActors()
    #~ print"-----getActors()---lastNameList--"
    #~ matchingActors = ActorsManager(actorList =actors.getActors(lastNameList=["MaZel","LaGrue"]))
    #~ matchingActors.printActors()
    #~ print"-----getActors()---ticketKeywordList--"
    #~ matchingActors = ActorsManager(actorList =actors.getActors(ticketKeywordList=["couCou","saLut"]))
    #~ matchingActors.printActors()
    #~ pass
    
if __name__ == '__main__':
     
    print "launching \"actor.main\" main method "
    print"----------------------------------------"
    # testActor()
    # testActorManager()