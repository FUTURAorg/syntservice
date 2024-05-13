import numpy as np
from .backend import SyntBackend

import scipy
from transformers import AutoProcessor, BarkModel
from scipy.io.wavfile import write as write_wav


class BarkBackend(SyntBackend):
    
    def __init__(self, speaker_audio=None):
        super().__init__()
        
        self.speaker = speaker_audio
        self.processor = AutoProcessor.from_pretrained("suno/bark")
        self.model = BarkModel.from_pretrained("suno/bark").to('cuda')
        self.voice_preset = "v2/ru_speaker_6"
        self.sample_rate =  self.model.generation_config.sample_rate
        
    def generate_audio(self, text) -> tuple[np.ndarray, int]:
        inputs = self.processor(text, voice_preset=self.voice_preset).to('cuda')
        audio_array = self.model.generate(**inputs)
        audio_array = audio_array.cpu().numpy().squeeze() 
        
        return audio_array, self.sample_rate


if __name__ == "__main__":
    bark = BarkBackend()
    
    bark.generate_audio("Тестовое аудио")