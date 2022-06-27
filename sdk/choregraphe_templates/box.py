import traceback

class MyClass(GeneratedClass):
    def __init__(self):
        GeneratedClass.__init__(self)
        self.bIsRunning=False

    def onLoad(self):
        #put initialization code here
        pass

    def onUnload(self):
        self.onInput_onStop()

    def onInput_onStart(self, p):
        if self.bIsRunning:
            self.log("%s is already running, quitting" % self.boxName)
            return
        self.bIsRunning = True
        try:
            # YOUR CODE HERE
        except:
            self.log( traceback.format_exc())

        self.bIsRunning=False


    def onInput_onStop(self):
        if self.bIsRunning:
            self.log("%s: Calling Stop" % self.boxName)
            # YOUR STOPING CODE here

            self.bIsRunning=False