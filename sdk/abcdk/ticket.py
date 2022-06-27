# -*- coding: utf-8 -*-

###########################################################
# Aldebaran Behavior Complementary Development Kit
# Tickets
# @author The usage team - Living Labs
# Aldebaran Robotics (c) 2016 All Rights Reserved - This file is confidential.
###########################################################


import datetime
import mutex
import pathtools
import random
import time


try: import dill #to save data
            # sudo pip install dill
            #ou scp directement sur le robot .local/lib/python2.7/site-packages
except: pass

# GLOBAL
#To use it on the robot please create a symbolic linc on the robot

MEMORYFILENAME="/home/nao/events/"
PATH_TO_SAVE = pathtools.getCachePath()
SERVER_NEWS_FILE_PATH = "/home/elagrue/Desktop/test/mydata2.txt"
FILENAME_TICKETS =PATH_TO_SAVE + "tickets.txt"
FILENAME_NEWS = PATH_TO_SAVE + "ticketsNews.txt"

# TICKETLIST represent the order in wich the element in ticket are classed
TICKETLIST = [  "ticketNum", 
                # 18
                #time of ticket creation
                "timeUTC","year","month","weekday","day","hour", "minute", "second",
                #1460452796.73, 2016, Apr, Tue, 12, 11, 19, 56,
                #time of action
                "yearOfAction","monthOfAction","weekDayOfAction","dayOfAction","hourOfAction","minuteOfAction","secondOfAction",
                #1970, Apr, Tue, 32, 0, 0, 0
                #action information
                "place","source","action","cible","objet","positionRefRobot","positionRef3D","actionDuration","verite","certitude","isQuestion" ,"newsKeywords"
                #livingroom,CALVIN,GIVE,LANNING,ROBOT,3metersfront,kitchen,5min,1.0,1.0,True,["happy" "mariage", "party"]
                ]

def getFilenameFromTime(timestamp=None):
    """
    get a string usable as a filename relative to the current datetime stamp.
    eg: "2012_12_18-11h44m49s049ms"
    timestamp : time.time()
    """
    if timestamp is None:
        datetimeObject = datetime.datetime.now()
    elif isinstance(timestamp, datetime.datetime):
        datetimeObject = timestamp
    else:
        datetimeObject = datetime.datetime.fromtimestamp(timestamp)
    strTimeStamp = datetimeObject.strftime( "%Y_%m_%d-%Hh%Mm%Ss%fms" );
    strTimeStamp = strTimeStamp.replace( "000ms", "ms" ); # because there's no flags for milliseconds
    return strTimeStamp;

def indexListTicket(label):
    # Return the index of the label in the ticket list. ex : "year" return 2
    index = 0
    for i in TICKETLIST:
        if (label == i):
            return index
        index+=1
    else:
        print("ERR :  label not found in list TICKETLIST, please check spelling")
        return None  
    
def isContentsEqual( t1, t2 ):
    #return the content of isContentEqual 
    return t1.isContentsEqual( t2 )
    
class Ticket :
    def __init__(    self, place = None, source=None, action=None, cible=None, objet=None, positionRefRobot = None, positionRef3D = None, actionDuration = None,
                verite=None, certitude= None, yearOfAction = None, monthOfAction = None, weekDayOfAction = None, dayOfAction = None, hourOfAction = None, minuteOfAction = None, secondOfAction = None,
                year = None, month = None, weekDay = None, day =None, hour = None, minute = None, second = None, data = None , sameTimeTicketAction = False, isQuestion = False , newsKeywords = None):

        #In case we pass all the data (ex : after spliting a string with ',', be sure that nothing has been modified int the order of "getData()" and the argument order in "__init__")            
        if(data):
            print("INF : Copy of ticket created (data passed as argument, /!\ same Number of Ticket)")
            #copy all field from data
            self.ticketNum = data[indexListTicket("ticketNum")]
            #time of ticket cretion
            self.timeUTC =  data[indexListTicket("timeUTC")]
            self.year = data[indexListTicket("year")]
            self.month = data[ indexListTicket("month")]
            self.weekday =  data[indexListTicket("weekday")]
            self.day =  data[indexListTicket("day")]
            self.hour =  data[indexListTicket("hour")]
            self.minute =  data[indexListTicket("minute")]
            self.second=  data[indexListTicket("second")]
            #time of described action
            self.yearOfAction =  data[indexListTicket("yearOfAction")]
            self.monthOfAction = data[indexListTicket("monthOfAction")]
            self.weekDayOfAction =  data[indexListTicket("weekDayOfAction")]
            self.dayOfAction =  data[indexListTicket("dayOfAction")]
            self.hourOfAction =  data[indexListTicket("hourOfAction")]
            self.minuteOfAction =  data[indexListTicket("minuteOfAction")]
            self.secondOfAction =  data[indexListTicket("secondOfAction")]
            if sameTimeTicketAction :
                self.yearOfAction =  self.year
                self.monthOfAction = self.month
                self.weekDayOfAction =  self.weekday
                self.dayOfAction =  self.day
                self.hourOfAction =  self.hour
                self.minuteOfAction =  self.minute
                self.secondOfAction =  self.second
                
            #Action information
            self.place =  data[indexListTicket("place")].lower()
            self.source = data[indexListTicket("source")].lower()
            self.action =  data[indexListTicket("action")].lower()
            self.cible =  data[indexListTicket("cible")].lower()
            self.objet =  data[indexListTicket("objet")].lower()
            self.verite =  data[indexListTicket("verite")]
            self.certitude =  data[indexListTicket("certitude")]
            self.actionDuration =  data[indexListTicket("actionDuration")]
            self.positionRefRobot =  data[indexListTicket("positionRefRobot")]
            self.positionRef3D =  data[indexListTicket("positionRef3D")]
            self.isQuestion = data[indexListTicket("isQuestion")]
            if data[indexListTicket("newsKeywords")] != None:
                self.newsKeywords = data[indexListTicket("newsKeywords")].split(";")
            else:
                self.newsKeywords = data[indexListTicket("newsKeywords")]
            
        else:#check if we need to copy the tickect or not
            print("INF : new ticket created (all info passed )")
            self.ticketNum = None
                
            #time of ticket cretion
            self.timeUTC = time.time()
            ticketTime = time.asctime(time.localtime()).split()
            self.weekday,self.month,self.day,timeHMS,self.year = ticketTime
            self.hour = timeHMS[0:2]
            self.minute = timeHMS[3:5]
            self.second= timeHMS[6:8]
            #TODO :  add ligne to force ticket creation time in arg            
            if(year):self.year = year
            
            #time of described action
            self.yearOfAction = yearOfAction
            self.monthOfAction =monthOfAction
            self.weekDayOfAction = weekDayOfAction
            self.dayOfAction = dayOfAction
            self.hourOfAction = hourOfAction
            self.minuteOfAction = minuteOfAction 
            self.secondOfAction = secondOfAction 
            #Action information
            #TODO :  add ligne to lower all the string
            self.place = place
            self.source =source
            self.action = action
            self.cible = cible
            self.objet = objet
            self.verite = verite
            self.certitude = certitude
            self.actionDuration = actionDuration
            self.positionRefRobot = positionRefRobot
            self.positionRef3D = positionRef3D
            self.isQuestion = isQuestion
            if newsKeywords != None:
                self.newsKeywords = newsKeywords.split(";")
            else:
                self.newsKeywords = newsKeywords
        pass   

    def __repr__(self):
        # Display the ticket value
        #TODO : make a nice display of Ticket 's informations
        return "Ticket : " + str( self.getData() )

    def __str__(self, bFull = False):
        # Display the ticket value
        strOut = "Ticket:\n"
        strOut += "* ticketNum: %s\n" % str(self.ticketNum)
        strOut += "* source: %s\n" % str(self.source)
        strOut += "* action: %s\n" % str(self.action)
        strOut += "* cible: %s\n" % str(self.cible)
        strOut += "* objet: %s\n" % str(self.objet)
        strOut += "* verite: %s\n" % str(self.verite)
        
        if( bFull ):
            for attr in dir(self):
                at = getattr(self, attr)            
                if( type(at) != type( self.__init__ ) ): # don't print method
                    strOut += "** %s: %s\n" % (attr, at)
        return strOut

    def getData(self):
        # gather all the Tickets Attributes (do not modify the order, keep the same as ticket creation)
        data = [    self.ticketNum,self.timeUTC,self.year,self.month,self.weekday,self.day,self.hour,self.minute,self.second,
                        self.yearOfAction, self.monthOfAction, self.weekDayOfAction, self.dayOfAction, self.hourOfAction, self.minuteOfAction, self.secondOfAction,
                        self.place, self.source, self.action, self.cible, self.objet, self.positionRefRobot,  self.positionRef3D,  self.actionDuration, self.verite, self.certitude,self.isQuestion, self.newsKeywords]    
        return data
        
         
    def isContentsEqual( self, t2 ):
        t3 = t2 # deepcopy.copy(t2) # we'll just change numbers and not string
        t3.ticketNum = self.ticketNum
        t3.timeUTC = self.timeUTC
        t3.weekday,t3.month,t3.day,t3.year = self.weekday,self.month,self.day,self.year
        t3.hour, t3.minute, t3.second = self.hour, self.minute, self.second 
        print self
        print t3
        #~ return self == t3
        for attr in dir(self):
            at = getattr(self, attr)
            if( type(at) != type( self.__init__ ) ): # don't print method
                at3 = getattr(t3, attr)
                if at != at3:
                    return False
        return True

        
    def saveTicket(self):
        filename =   MEMORYFILENAME + getFilenameFromTime() +"_id_"+ str(self.ticketNum)+".txt"
        data = self.getData()
        with open(filename,'w') as myfile:
            for i in range(len(data)):
                myfile.write( str(data[i]) +',')
                #~ if ( not i == len(self.data)-1):
                    #~ myfile.write(",")
            print "DEBUG_PASS : i write " + str(data) + " and jump line"
            myfile.write("\n")


    def generateDictionnaryFromTicket(self):
        """
        Generates a dictionnary based on the content of the ticket

        Returns:
            dicitonnary - The dictionnary corresponding to the ticket
        """

        dictionnary                     = dict()
        dictionnary['ticketId']         = self.ticketNum
        dictionnary['weekday']          = self.weekday
        dictionnary['month']            = self.month
        dictionnary['day']              = self.day
        dictionnary['year']             = self.year
        dictionnary['hour']             = self.hour
        dictionnary['minute']           = self.minute
        dictionnary['second']           = self.second
        dictionnary['yearOfAction']     = self.yearOfAction
        dictionnary['monthOfAction']    = self.monthOfAction 
        dictionnary['weekDayOfAction']  = self.weekDayOfAction
        dictionnary['dayOfAction']      = self.dayOfAction 
        dictionnary['hourOfAction']     = self.hourOfAction
        dictionnary['minuteOfAction']   = self.minuteOfAction 
        dictionnary['secondOfAction']   = self.secondOfAction 
        dictionnary['place']            = self.place
        dictionnary['source']           = self.source
        dictionnary['action']           = self.action
        dictionnary['cible']            = self.cible
        dictionnary['objet']            = self.objet
        dictionnary['verite']           = self.verite
        dictionnary['certitude']        = self.certitude
        dictionnary['actionDuration']   = self.actionDuration
        dictionnary['positionRefRobot'] = self.positionRefRobot
        dictionnary['positionRef3D']    = self.positionRef3D
        dictionnary['isQuestion']       = self.isQuestion
        dictionnary['newsKeyword']      = self.newsKeywords

        return dictionnary
        



    def setTicketId(self, ticketId):
        #set the Ticket ID
        self.ticketNum=ticketId

    def timeDiff(self):
        #return the elapsed time between the ticket creation and the current time 
        currentTime = time.time()
        diffTime = currentTime - self.timeUTC 
        difftuple = time.gmtime(diffTime)
        return difftuple
          
# end of class Ticket  


class TicketsManager :
    
    def __init__(self ,tickets= None, isNews = False):
        # Two way of initialize a memory , by giving the .txt file or giving data
        self.memory=[]
        self.nextTicketId=0
        self.isNews = isNews
        self.mutexCreateNew = mutex.mutex()
        if tickets:
            self.memory = tickets
        #loading the tickets from the sevor 
        else:
            try :
                self.loadTicketsFromTxt()
            except :
                print " WRG : File not found (loadTickets)"
                pass

            if (self.isNews):
                try:
                    self.addNewNews()
                except:
                    print "WRG : TicketsManager.__init__ , Failed loading the news from the txt file (HTML page)"
      
    def addNewNews (self):
        with open(SERVER_NEWS_FILE_PATH) as f:
            content = f.readlines()
                #~ print "content"
                #~ print content
            for i in range(len(content)):
                # if (not content[i]=='\n'):
                    # self.memory.append(content[i].split(',')[:-1])   
                tmpContent = content[i].split(',') [:-1]
                print len(tmpContent)
                print tmpContent
                tmpyearOfAction ,tmpmonthOfAction,tmpweekDayOfAction,tmpdayOfAction,tmphourOfAction,tmpminuteOfAction,tmpsecondOfAction,tmpplace,tmpsource,tmpaction,tmpcible,tmpobjet,tmpactionDuration,tmpKeywords= tmpContent
                tmpKeywords = tmpKeywords.split(';')
                tmpTicket = Ticket(yearOfAction=tmpyearOfAction,monthOfAction=tmpmonthOfAction,weekDayOfAction=tmpweekDayOfAction,dayOfAction=tmpdayOfAction,hourOfAction=tmphourOfAction,minuteOfAction=tmpminuteOfAction,secondOfAction=tmpsecondOfAction,place=tmpplace,source=tmpsource,action=tmpaction,cible=tmpcible,objet=tmpobjet,actionDuration=tmpactionDuration,newsKeywords=tmpKeywords)
                print tmpTicket
                self.createNewTicket(tmpTicket)

        self.clearNewNews()

    def askRandomQuestion(self, cible, action = "aimer"):
        self.loadTickets()
        alea = [1,2,3,4,5]
        random.shuffle(alea)
        ticketQuestion = self.getAllQuestion()

        if ticketQuestion == None:
            return None
        if len(ticketQuestion) < 1 :
            return None
        lastQuestion = ticketQuestion[-1]
        if alea[0] != 1 : 
            ticketQuestion = self.getQuestionWithTalk(action)

        if isinstance( ticketQuestion, list ):
            random.shuffle(ticketQuestion)
            ticketQuestion = list(set(ticketQuestion))
            #print "newQuestion " + str(ticketQuestion)
            i = 0 
            for tmpTicket in ticketQuestion:
                if not (tmpTicket.objet in [lastQuestion.objet]):
                    print "INF : ticket : askRandomQuestion : 1 ticket choose with the objet " + str(tmpTicket.objet)
                    return tmpTicket
            return None
        else :
            if not (ticketQuestion.objet in [lastQuestion.objet]):
                print "INF : ticket : askRandomQuestion : 2 ticket choose with the objet " + str(tmpTicket.objet)
                return ticketQuestion
            else:
                return None

    def clearNewNews (self):
        #clear the news
        open(SERVER_NEWS_FILE_PATH).close()

    def clearTickets(self):
        #clear the actors save on the servor
        if self.isNews :
                filename = 'news.pkl'
        else :
                filename ='ticketsManager.pkl'

        open(PATH_TO_SAVE+filename, 'w').close()
        print "Tickets has been erased at :%s" % PATH_TO_SAVE+filename
        pass

    def clearTicketsFromTxt(self):
        self.memory = []
        self.nextTicketId=0
        #clear 
        if self.isNews :
            fileName = FILENAME_NEWS
        else :
            fileName = FILENAME_TICKETS

        open(fileName, 'w').close()
        print "Tickets has been erased at :%s" % fileName
        pass

    def createNewTicket(self,newticket = None):
        if  not newticket :
            newticket = Ticket()
        newticket.setTicketId(self.getNewTicketId())
        self.memory.append(newticket)
        if (not self.isNews):
            newticket.saveTicket()
        self.saveTicketsToTxt()
        return self.memory[-1]
        
    def deleteTickets(self, indexes ):
        # Delete the tickets passed in argument (tickets numbers) then refresh the memory .txt files
        # input :  list of the desired tickets list to delete ex : [1,12,36]
        datatmp=[]
        for ticket in self.memory:
            if (int(ticket.ticketNum)in indexes ):
                datatmp.append(ticket)
        #TODO : fixe bug when delete and going trought the data OR FIND AN OTHER METHOD (without iteration)
        for ticket in datatmp:
            self.memory.remove(ticket)
            print(" Tickets number %s deleted !" % str(data[0]))
        #~ self.saveMemory()
        self.memory = datatmp

    def findTickets(self,listCoupleIndexValue, listOfTickets = None):
        # return all the ticket corresponding  to the desired value
        # /!\ :  if you want to find search keyword use findTicketByKeyword
        # input : label - desired couple label  for the research (see DICTIONNARY) ex : findTickets([["place","PROTOLAB"],["cible","CIBLE"],["year",2013,2015]])
        #          value - desired value corresponding to the label
        # output :  all the ticket corresponding to the input argument
        if listOfTickets == None :
            listOfTickets = self.memory

        if not isinstance( listOfTickets, list ):
            listOfTickets = [listOfTickets]

        filteredMemory=[]
        # Test each ticket with the label/value couple
        for tmpTicket in listOfTickets :
            flag = True            
            for coupleIdVal in listCoupleIndexValue:#for each couple
                #get index of the label 
                if (str(coupleIdVal[0]) == "keywords"):
                    index = len(TICKETLIST)
                else:
                    index = indexListTicket(coupleIdVal[0])
                    
                if (len(coupleIdVal) == 2):#check if target is a precise value (couple label / value )
                    if (index == (len(TICKETLIST)) ):#check if not a news
                        if (not ( str(coupleIdVal[1]) in getattr(tmpTicket, coupleIdVal[0] ) )):
                            #~ print ("FALSE for keyword \"%s\" :\t%s not in to %s " % (coupleIdVal[0], tmpTicket[index]    , coupleIdVal[1]))  
                            flag =False
                            break
                    else:
                        if (not (str(getattr(tmpTicket, coupleIdVal[0] )) == str(coupleIdVal[1])) ):
                            #~ print ("FALSE for label \"%s\" :\t%s not equal to %s " % (coupleIdVal[0], tmpTicket[index]    , coupleIdVal[1]))  
                            flag =False
                            break
                elif (len(coupleIdVal) == 3):#check if target is a range of value (couple label / value1 / value 2 )
                    import qi
                    qi.info("WARNING BORDEL","................." + str( coupleIdVal[0] ) + " ... " + str(tmpTicket))
                    if (  not ((int(getattr(tmpTicket, coupleIdVal[0] )) >= min(coupleIdVal[1:3])) and (int(getattr(tmpTicket, coupleIdVal[0] )) <= max(coupleIdVal[1:3])) )) :        
                        #~ print ("False for ticket position : %s, label \"%s \" :\t %s not between %s and %s" % (str(tmpTicket[0]),str(coupleIdVal[0]),tmpTicket[index],str(coupleIdVal[1]),str(coupleIdVal[2])))
                        flag =False
                        break
                else:#Wrong value of couple index/value
                    print "ERR : findTickets : Wrong value of couple index/value "
                    
            if (flag == True ):        
                print ("INF: findTickets : --> TICKET FOUND <--, ticket number is : %s" % tmpTicket.ticketNum )
                filteredMemory.append(tmpTicket)
        #return filtered memory if not empty        
        if(len(filteredMemory) <=0):
            print ("WRG : findTickets :  ==>> Ticket not found  <<==")
            return None
        else :
            print ("INF : findTickets :  ==>> Ticket found  <<==")
            return TicketsManager(tickets=filteredMemory)
         
    def findTicketByKeyword(self , keywords):
        # return all the ticket corresponding  to the desired value
        # input : label - desired label for the research (see DICTIONNARY) ex : "place" "year"
        #          value - desired value corresponding to the label
        # output :  all the ticket corresponding to the input argument
                        
        filteredMemory=[]
        for tmpTicket in self.memory :# Test each ticket 
            flag = True
            for keyword in  keywords :# Test each keyword
                if (not ( keyword in tmpTicket.newsKeywords)):
                    print ("FALSE : keyword not matching: %s not in %s " % ( keyword   , tmpTicket.newsKeywords ))
                    flag =False
                    break
            if (flag == True ):        
                print ("Ticket found, Id : %s" % str(tmpTicket.ticketNum) )
                filteredMemory.append(tmpTicket)
        #return filtered memory if not empty        
        if(len(filteredMemory) <=0):
            print ("  ==>> Ticket not found  <<==")
            return None
        else :
            return News(None,filteredMemory)
        pass    

    def getAllQuestion(self):
        # Return all the question ("isQuestion" => True)
        try:
            return (self.findTickets([["isQuestion",True]])).memory
        except:
            print "No question found"
            return None

    def getAnswerToQuestion(self, action, objet , ticketNum):
        taille = len(self.memory)
        ticketFind = []
        for tmpTicket in self.memory:
            if tmpTicket.action == action and tmpTicket.objet == objet and tmpTicket.ticketNum != ticketNum :
                if str(tmpTicket.isQuestion) == "False":
                    ticketFind.append(tmpTicket)
                else:
                    i = int(tmpTicket.ticketNum) + 1
                    if i < taille:
                        if self.memory[i].objet in ["oui","non"] :
                            ticketFind.append(tmpTicket)
        if ticketFind == []:
            return None
        else:
            return ticketFind

    def getLastQuestion(self,answerTicket= None):

        if answerTicket == None :
            tmp = self.memory
            for i in range(1,len(tmp)):
                if tmp[-i].isQuestion == True:
                    return tmp[-i]
            return None
        else :
            #return the latest question asked before the UTCtime of the ticket passed as argument

            #find all the tickets that are questions and published before the answerTicket passed as argument
            questionTickets= self.findTickets([["isQuestion", True ],["action",answerTicket.action]])
            # sorted by time all the corresponding tickets
            print "questTicket :::::"
            if questionTickets == None:
                return None
            for i in questionTickets.memory :
                print i.timeUTC
            #sort the result by time    
            sortedQuestionTickets = sorted(questionTickets.memory, key=lambda x: x.timeUTC, reverse=True)
            # return the latest
            return sortedQuestionTickets[0]

    def getListIdTicket (self, tickets=None):
        #return a list of the Id of the tickets passed as argument
        if tickets == None :
            return None
        else:
            listID =[]
            for ticket in tickets :
                listID.append(tickets[0])
            return listID

    def getNewTicketId(self):
        #return an Identity Number for a new ticket
        while self.mutexCreateNew.testandset() == False:
            print " Waiting for the mutex to be unlocked"
            time.sleep( 0.01)
        nId = self.nextTicketId
        self.nextTicketId += 1
        self.mutexCreateNew.unlock()
        return nId            
        
    def getQuestionWithTalk(self, action):
        # Return all the question ("isQuestion" => True)
        try:
            return (self.findTickets([["action",action]])).memory
        except:
            print "No question found"
            return None

    def getRelatedTickets(self, ticket,listCoupleIndexValueWeights, weightsTimeDiff = None):
        #return a list of Ticket sorted by the similitude to the Ticket passed as argument according to the weights of each labels    
        # input : a tickets 
        #        some couple of label value weights ex :["year",2013,2015,1]
        #        some negative weight for the time difference between the check and the  tickets creation [years, months, days, hours, minutes, seconds]
        # output a list of tickets sorted by similitude to the input 
        if hasattr(ticket, 'keywords'):
            flagNews = True
        else:
            flagNews = False
        #Initialize weights to 0
        weights=([0]*len(TICKETLIST))
        if(not weightsTimeDiff):
            weightsTimeDiff=([0]*6)
        allScoreList=[]
        for tmpTicket in self.memory:
            tmpScore = 0
            dataTicket = tmpTicket.getData()
            for coupleIDW in listCoupleIndexValueWeights:#for each couple    
                
                if (str(coupleIDW[0]) == "keywords"):
                    index = len(TICKETLIST)
                else:
                    index = indexListTicket(coupleIDW[0])
                
                if (len(coupleIDW) == 3):#check if target is a precise value (couple label / value )
                    if (coupleIDW[0]  == "keywords" ):
                        #~ print coupleIDW[1][indexKW]
                        if (( str(coupleIDW[1]) in getattr(tmpTicket, coupleIDW[0] )) ):
                            tmpScore += coupleIDW[2] 
                    else:
                        if ( (str(getattr(tmpTicket, coupleIDW[0] )) == str(coupleIDW[1])) ):
                            #~ print ("True for: %s and %s " % (tmpTicket[index]    , coupleIDW[1])  )
                            tmpScore += coupleIDW[2]
                elif (len(coupleIDW) == 4):#check if target is a range of value (couple label / value1 / value 2 )    
                    if (  (int(getattr(tmpTicket, coupleIDW[0] )) >= min(coupleIDW[1:3])) and (int(getattr(tmpTicket, coupleIDW[0] )) <= max(coupleIDW[1:3]) )) :        
                        #~ print ("True for ticket position is : %s, %s : %s between %s and %s" % (str(tmpTicket[0]),str(coupleIDW[0]),tmpTicket[index],str(coupleIDW[1]),str(coupleIDW[2])))
                        tmpScore += coupleIDW[3]
                else:#Wrong value of couple index/value
                    print "Wrong value of couple index/value "
            #add the time difference penality    
            if (flagNews):
                timeUTC=ticket.ticket.timeUTC
            else:
                timeUTC=ticket.timeUTC
                
            timediff = self.timeDiffTickets(timeUTC,tmpTicket.timeUTC)
            tmpScore +=timediff.tm_year * weightsTimeDiff[0] + timediff.tm_mon * weightsTimeDiff[1] +timediff.tm_mday * weightsTimeDiff[2] + timediff.tm_hour * weightsTimeDiff[3] + timediff.tm_hour * weightsTimeDiff[4]
            allScoreList.append([ tmpTicket.ticketNum ,tmpScore])
    
        #sort the list in descending order according to the score
        allScoreListSorted = sorted(allScoreList,key=lambda l:l[1], reverse=True)
        #sort the first ex aequo in the most recent order according to the ticket number
        numExAequo = 0
        while (allScoreListSorted[0][1] == allScoreListSorted[numExAequo][1]  and numExAequo < len(allScoreListSorted)-1):
            numExAequo +=1    
            
        allScoreListSorted[0:numExAequo ] =  sorted(allScoreListSorted[0:numExAequo ],key=lambda l:l[0], reverse=True)
        
        if (allScoreListSorted):
            return allScoreListSorted
        else:
            print("INF : Empty list returned !")
            return None
    
    def getTicket(self, ticketId):
        #return the desired tickets
        # input :  the index of the desired tickets (not corresponding to the line in the txt)
        # output : return the Tickets
        for ticket in self.memory :
            if (int(ticket.ticketNum) == int(ticketNumber)):
                #~ print ("INF : copy of ticket number %s" % ticketNumber)
                try:
                    tmpTicket = Ticket(data=i )
                    return  tmpTicket
                except IndexError:
                    #~ print (" ERR : wrong value of index (index out of range")
                    return None
        print " Ticket number %s is not in this memory" % str(ticketNumber) 
        return None    
        
    def loadTickets(self):
        #TODO adapt for news
        try:
            if self.isNews :
                    filename = 'news.pkl'
            else :
                    filename ='ticketsManager.pkl'
            print "LOAD ::::::::::::::"+PATH_TO_SAVE + filename 
            with open(PATH_TO_SAVE +filename, 'rb') as f:
                    self.memory = dill.load(f)
                    self.nextTicketId = dill.load(f)
                    self.isNews = dill.load(f)
                    pass
        except :
            print " WRG : File not found (loadTickets)"
            pass

    def loadTicketsFromTxt(self):  
        if self.isNews :
            fileName = FILENAME_NEWS
        else :
            fileName = FILENAME_TICKETS

        #try:
        self.memory = []
        nbId = 0
        with open(fileName) as f:
            content = f.readlines()
            for line in content:
                nbId = nbId + 1
                dataTicket = line.split(',')
                print "INF : loadTicketsFromTxt : " + str(len(dataTicket)) +" and " +str(len(TICKETLIST)) 
                # try:
                #     dataTicket[-1]=dataTicket[-1].split(";")
                # except:
                #     print "WRG : loadTicketsFromTxt() :failed spliting keywords"
                print "INF : loadTicketsFromTxt : " + str(dataTicket)
                tmpTicket = Ticket(data=dataTicket)
                print "INF : loadTicketsFromTxt : //"+str(tmpTicket)+"//"
                self.memory.append(tmpTicket)
        self.nextTicketId = nbId
        #except:
        #    print "ERROR : loadTicketsFromTxt :  Fail loading Tickets form txt : %s" % fileName
                    
    def printMemory(self):
        #Display the tickets contained in the memory
        print ("Printing Tickects : ")
        for ticket in self.memory:            
            print ticket
          
    def readNews( self, numbNews = 1):
        #load actor manager and ticket manager (we are currently in news manager)
        import actors
        aMan = actors.actorsManager
        tickMan = ticketsManager

        #get current Actors
        curActId = aMan.getCurrentActor()
        curAct = aMan.getActors( actorsId = curActId)

        #get current Actor's tickets and pass it to a new ticketManager to use it
        # tmptickMan = TicketsManager(tickets= curAct[0].tickets )

        #extract all already read news
        try :
            ticketsReadNews = (self.findTickets([["action","read news"]],listOfTickets=curAct[0].tickets)).memory
            print "INF: readNews : " + str(ticketsReadNews)
        except:
            ticketsReadNews = None
        #gather all the read news ID        

        idOfReadNews=[]
        listOfUnreadNews=[]
        #TODO add if self mem
        if ticketsReadNews == None:
            print "INF: readNews : No read news in the memory"
            # import speech
            # speech.sayAndLight("Désolé je n'ai pas de nouvelle à te donner")
            # return
            listOfUnreadNews = self.memory
        else:
            for ticketReadNew in ticketsReadNews :
                idOfReadNews.append(ticketReadNew.objet)

        #get the list of all unread news tickets
            for new in self.memory:
                print "INF: readNews : idOfReadNews //"+ str(idOfReadNews)+"// compare with //" + str(new.ticketNum) + "//"
                if new.ticketNum not in idOfReadNews:
                    listOfUnreadNews.append(new)

        print "INF: readNews : memory = //"+ str(self.memory) + "//"
        

        if listOfUnreadNews == []:
            import speech
            speech.sayAndLight("Désolé je n'ai pas de nouvelle à te donner")
            return

        #sort the unread news by timeUTC
        sortedNews = sorted( listOfUnreadNews, key=lambda x: x.timeUTC, reverse=True)

        #read desired number of news
        i = 0
        print "INF : readNews : before for loop : //" + str(sortedNews) + "//"
        for new in sortedNews :
            print "INF : readNews : in loop : //" + str(new) + "//"
            i+=1
            if (i > len(sortedNews)):
                print "INF : readNews : No more News to tell"
                return 1
            if i> numbNews :
                print ("INF : readNews : all %d News have been read" % (numbNews) )
                return
            #read news
            import rodin
            import speech
            print "readNews ticket : //"+ str(new) + "//"
            str2Say = rodin.rodin.generateSentence(tic=new)
            print "readNews say //" + str2Say +"//"
            speech.sayAndLight(str2Say)
            try:
                #for each news read add Tickets to Actors
                newTicket = Ticket( source=curActId ,action="read news" ,cible=curActId,objet=new.ticketNum)
                #ad ticket to global memory
                tickMan.createNewTicket(newticket = newTicket)
                print "INF :readNews : tickets added to ticket manager"
            except:
                print "WRG :readNews : failed adding tickets to ticketsManagers"

            #add ticket to actors
            try:
                aMan.addTicket(curActId ,newTicket)
                print "INF :readNews :succesfully added newticket to the actors ticket"
            except:
                print "WRG :readNews : failed adding tickets to actors tickets list"

        print "INF : readNews : end loop"
        #exit

    def saveTickets(self):
        #TODO adapt for news
        try:
            if self.isNews :
                    filename = 'news.pkl'
            else :
                    filename ='ticketsManager.pkl'

            print "SAVE :::::::::: "+ PATH_TO_SAVE +filename
            with open(PATH_TO_SAVE +filename, 'wb') as f:
                 dill.dump(self.memory, f)
                 dill.dump(self.nextTicketId, f)
                 dill.dump(self.isNews, f)
        except BaseException, err:
            print( "ERR: ActorsManager.saveActors: error while saving: %s" % str(err) )

    def saveTicketsToTxt(self):

        if self.isNews :
            fileName = FILENAME_NEWS
        else :
            fileName = FILENAME_TICKETS
        flagfirst = True
        # open(fileName, 'w').close()
        with open( fileName,'w') as myfile:
            for ticket in self.memory :
                flagfirst = True
                data = ticket.getData()
                for dt in data:
                    if dt == data[-1]:# if keywords
                        try:
                            for i in dt :
                                if i == dt[0]:
                                    myfile.write(","+str(i).replace('\n',''))
                                else:
                                    myfile.write(";"+str(i).replace('\n',''))
                        except:
                            myfile.write(",")
                            print "WRG: saveTicketsToTxt(): No keyword "

                    else: #all other elements
                        if flagfirst:
                            flagfirst = False
                            myfile.write( str(dt) )
                        else:
                            myfile.write( "," + str(dt) )
                myfile.write("\n")

    def timeDiffTickets(self, newticketUTC, oldticketUTC):
        #diffTime = (tm_year=2016, tm_mon=4, tm_mday=12, tm_hour=12, tm_min=35, tm_sec=8, tm_wday=1, tm_yday=103, tm_isdst=0)
        diffTime= float(newticketUTC) - float(oldticketUTC)
        diffTime = time.gmtime(diffTime)
        return diffTime
        

# end of class Memory

def commandLoop():
    global player
    global fileId
    mem = naoqitools.myGetProxy( "ALMemory" );
    mem.insertData( "tabletResponse", "" );
    print "begin command loop in music_manager.py"
    while mem.getData("tabletResponse")!= "Pepper stop":
        response = mem.getData("tabletResponse")
        if response != "":
            mem.insertData("tabletResponse","") 
            print "command sent : " + response
            choiceCommand(response)
    #~ sendStop()    

# SINGLETON (use ticketsManager when call in a function, NOT TicketsManager)
#           (use ticketsNews when call in a function, NOT TicketsManager(isNews =True))
ticketsManager = TicketsManager() 
ticketsNews = TicketsManager(isNews =True) 

  
#_______________ Test METHOD________________________

def test():#Test index dictionnary
    
    tRef = Ticket( action = "tester" )
    t1 = tRef
    t2 = Ticket( action = "tester" )
    t3 = Ticket( action = "manger" )
    assert( tRef == t1 )
    assert( t1.isContentsEqual( t2 ) )
    assert( not t1.isContentsEqual( t3 ) )    
    assert( tRef == t1 )    
    
    newticket = Ticket(isQuestion=True)
    memo = TicketsManager()
    memo.printMemory()
    memo.createNewTicket (Ticket(isQuestion=True))
    
    

    #~ filteredMemory = memo.findTickets([["place","kkpart"],["year",2013,2017]])    
    #~ filteredMemory.printMemory()
    #~ print "<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<end "
    #~ tNew =Ticket ()
    #~ score = memo.getRelatedTickets(tNew,[["place","kkpart",1]])
    #~ print score
    
    answerTicket = Ticket()
    
    time.sleep(1)
    memo.createNewTicket (Ticket(isQuestion=True))
    time.sleep(1)
    memo.createNewTicket (newticket)
    memo.printMemory()
    
    print"---------------------------------"
    print answerTicket
    print"-------------------------------------"
    print memo.getLastQuestion(answerTicket)
    #~ #find all the tickets that are questions and published before the answerTicket passed as argument
    #~ questionTickets= self.findTickets(tNew,[["isQuestion", True ,3],["timeUTC",answerTicket.timeUTC - 20,answerTicket.timeUTC,3]])
    #~ # sorted by time all the corresponding tickets
    #~ sortedQuestionTickets = sorted(questionTickets, key=lambda x: x.timeUTC, reverse=True)
    #~ return sortedQuestionTickets[0]
 
def testNews():
    
    news = ticketsNews
    news.clearTickets()
    news.printMemory()
    print "-------------------------------------------"
    
    news.createNewTicket (Ticket(newsKeywords=["happy", "coucou"]))
    news.createNewTicket (Ticket(newsKeywords=["hello", "coucou"]))
    news.createNewTicket (Ticket(newsKeywords=["happy", "coucou"]))
    print news.memory[0].newsKeywords
    print news.findTicketByKeyword(["hello"])
#____________________________________________________________________________________________________________________________________________________________________________
#____________________________________________________________________________________________________________________________________________________________________________
if __name__ == '__main__':
    print " :::::::: MAIN :::::::: "
    # test()
    # testNews()
    