#!/usr/bin/python

import stk.runner
from sound_analyser import SoundAnalyser
import logging

if __name__ == "__main__":
    logging.basicConfig(filename='test.log',
        level=logging.DEBUG,
        format='%(levelname)s %(relativeCreated)6d %(threadName)s %(message)s (%(module)s.%(lineno)d)',
        filemode='w')

    logging.info("start")
    qiapp = stk.runner.init()
    test = SoundAnalyser(qiapp,bKeepAudioFiles = True, strUseLang = "fr-FR")
    vals = test.asrFile("/home/jmmontanier/test.wav")
    logging.debug(str(vals))
    logging.info("end")
