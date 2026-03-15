import speech_recognition as sr
from IPython.display import Audio

class VoiceIn:

    def __init__(self,verbose=0):
        self.verbose = verbose
        self.recognizer = sr.Recognizer()
    
    def prepare(self):
        pass

    
    def speech_to_text(self, file):
        """
        Voice_To_Text
        these method is to takes the "voice file" and convert it into text
        """
        
        audio = self.recognizer.record(file)
        if self.verbose==1:
            print("Recognizing speech from file...")
        text = self.recognizer.recognize_google(audio, language="ar-EG")
        if self.verbose==1:
            print(text)
        return text

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
    
    def text_to_speech(self):
        """
        
        """
        
        pass

    def test(self):
        """
        
        """
        # Load audio file
        audio_file = "test2.wav"
        with sr.AudioFile(audio_file) as source:
            audio = self.recognizer.record(source)
        # Recognize speech using Google Web Speech API
        print("Recognizing speech from file...")
        text = self.recognizer.recognize_google(audio, language="ar-EG")
        
        if self.verbose==1:
            Audio("test2.wav", autoplay=True)
            print("Test:",text)
        return audio, text

