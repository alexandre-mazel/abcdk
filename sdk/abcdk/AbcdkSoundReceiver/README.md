To use it as an app taping in the microphone of the robot:
computer$ python AbcdkSoundReceiver.py --qi-url IP_ROBOT

To use it as an app localy on the robot:
computer$ python sendsdk.py IP_ROBOT
computer$ ssh nao@IP_ROBOT
robot$ python .local/lib/python2.7/site-packages/abcdk/AbcdkSoundReceiver/AbcdkSoundReceiver.py

To use it on file:
computer$ arecord -f S16_LE test.wav
computer$ python test.py --qi-url IP_ROBOT

