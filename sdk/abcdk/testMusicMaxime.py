import ticket as tkt

#example of how to use tickets with musicManager

MEMORYFILENAME_MUSIC =  "memoryMusic.txt"

def testMusicTicket():
	
	#crea ticket
	tNew= tkt.Ticket(place ="protolab",source="pepper",action="play music" ,cible="Maxime",objet="ACDC_-_TNT.mp3", memoryFileName=MEMORYFILENAME_MUSIC )
	tNew.addToMemory()#ajout dans la memoire
	print tNew
	#chargement de la memoire
	memoMusic = tkt.Memory(fileName =MEMORYFILENAME_MUSIC)
	memoMusic.printMemory()
	
	#find in memory : 
	#song play for Maxime between 2015-2016
	filteredMemory = memoMusic.findTickets([["cible","Maxime"],["year",2015,2016]])
	filteredMemory.printMemory()	
	#People who play the song passed as argument
	filteredMemory2 = memoMusic.findTickets([["objet","ACDC_-_7TNT.mp3"]])
	filteredMemory2.printMemory()
	
	
if __name__ == '__main__':
	print "launching \"ticket.main\" method "

	testMusicTicket()