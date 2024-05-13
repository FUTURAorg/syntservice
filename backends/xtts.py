
import numpy as np
import torch
from .backend import SyntBackend
from TTS.api import TTS

class XttsBackend(SyntBackend):
    
    def __init__(self, speaker_audio=None):
        super().__init__()
        
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        print(self.device)
        self.name = 'xTTS'
        
        self.speaker = speaker_audio
        self.model = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to(self.device)
        
    def generate_audio(self, text):
        
        return np.array(self.model.tts(text, language='ru', speaker_wav=self.speaker))

    def generate_to_file(self, text):
        self.model.tts_to_file(text, language='ru', speaker_wav=self.speaker)

    
if __name__ == "__main__":
    xtts = XttsBackend('speakers/1.ogg')

    xtts.generate_to_file("Тест")