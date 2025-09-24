import pymupdf4llm
import pymupdf
import edge_tts
import re
import torch 
import logging

logger = logging.getLogger('Main')
#from TTS.api import TTS

class textToSpeech():
    def __init__(self):
        self.text = ''
        self.pdf = None
        self.speaker = ''
        self.outputName = ''

    def setText(self, text):
        self.text = text

    def setVoice(self, voice):
        match int(voice):
            case 0:
                self.speaker = 'en-GB-SoniaNeural'
            case 1:
                self.speaker = 'en-AU-WilliamNeural'
            case 2:
                self.speaker = 'en-US-ChristopherNeural'
            case _:
                self.speaker = 'en-US-SteffanNeural'


    def getVoice(self):
        return self.speaker
    
    def setPDF(self, pdf):
        self.pdf = pdf

    def setOutputName(self, outputname):
        self.outputName = outputname

    def textToSpeechEdge(self):
        if self.pdf is not None:
            try:
                with open(self.pdf, "r", encoding="utf-8") as file:
                    self.text = file.read()
            except FileNotFoundError:
                print(f"Error: The file '{self.pdf}' was not found.")
                self.text = f"Error: The file '{self.pdf}' was not found."  # Or handle the error as needed
            except Exception as e:
                print(f"An error occurred while reading the file: {e}")
                self.text = f"An error occurred while reading the file: {e}"
            speech = edge_tts.Communicate(self.text, self.speaker)

        else:
            if len(self.text) > 0:
                speech = edge_tts.Communicate(self.text, self.speaker)
            else:
                speech = edge_tts.Communicate('No Text Entered', self.speaker)
        
        if len(self.outputName) < 2:
            speech.save_sync('result.mp3')
            logger.error("No Output Name Given")
        else:
            speech.save_sync(self.outputName)

    def textToSpeechTTS():
        return 

    def createTextFileFromPDF(self, removeSpaces=False, removeNumStrings=False):        
        doc = pymupdf.open(self.pdf)
        out = open('text.txt', "wb") # create a text output
        for page in doc: # iterate the document pages
            text = page.get_text() # get plain text (is in UTF-8)
            if removeSpaces:
                text = re.sub(r'[\x00-\x1F\x7F]', '', text)
            if removeNumStrings:
                text = re.sub(r'\\b\\d{5,}\\b', '', text)
            out.write(text.encode("utf8")) # write text of page
            out.write(bytes((12,))) # write page delimiter (form feed 0x0C)
        out.close()
        self.pdf = 'text.txt'

#testing
'''
createTextFileFromPDF('BriskK.pdf', 'textfile.txt', True, True)
textToSpeechEdge('textfile.txt', 0, 'test.mp3')
'''

