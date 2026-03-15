import speech_recognition as sr

class VoiceIn:

    def __init__(self,verbose=0):
        self.verbose = verbose
        self.recognizer = sr.Recognizer()
    
    def speech_to_text(self, path, language):
        """
        Voice_To_Text
        these method is to takes the "path of a voice file" and convert it into text
        """
        
        with sr.AudioFile(path) as source:
            audio = self.recognizer.record(source)
        if language == 'Arabic':
            text = self.recognizer.recognize_google(audio, language="ar-EG")
        else:
            text = self.recognizer.recognize_google(audio, language="en-US")
        return text
    
