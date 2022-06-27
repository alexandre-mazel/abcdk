


#~ import ticket as tk
#~ import actor as act

#~ tNew= tk.Ticket(place ="protolab",source="pepper",action="play music" ,cible="Maxime",objet="ACDC_-_TNT.mp3", memoryFileName=None )

#~ print tNew

#~ actor1 = act.Actor(idNumber=1, firstName="hopias", lastName="PROTOLAB", gender = "ProtoTeam")

#~ actor1.addTicket(tNew)

#~ print "-----------------------------------------------------------"
#~ print "-----------------------------------------------------------"
#~ print actor1
#~ actor1.printTicket()



class Testo():
	
	def __init__(self, a=None,b=None):
		self.a=a
		self.b=b
		
	def __str__(self):
		return str(self.a)+" et " +str(self.b)


var=Testo(a=2,b=3)
print var
acces = getattr(var, "a")
print acces


char = ["a","b"]

for i in char :
	print "var."+i
