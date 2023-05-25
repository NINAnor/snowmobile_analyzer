import librosa
import numpy as np

RANDOM = np.random.RandomState(42)

class AudioList():

    def __init__(self, length_segments = 3, overlap = 0, sample_rate=44100):
        self.sample_rate = sample_rate
        self.length_segments = length_segments
        self.overlap = overlap
        
    def read_audio(self, audio_path):
        """Read the audio, change the sample rate and randomly pick one channel"""
        sig, _ = openAudioFile(audio_path, sample_rate=self.sample_rate)
        return sig

    def split_segment(self, array):
        splitted_array = splitSignal(array, rate=self.sample_rate, seconds=self.length_segments, overlap=self.overlap, minlen=3)
        return splitted_array

    def get_processed_list(self, audio_path):
        track = self.read_audio(audio_path)      
        list_divided = self.split_segment(track)
        return list_divided
        
def openAudioFile(path, sample_rate=44100, offset=0.0, duration=None):    
    try:
        sig, rate = librosa.load(path, sr=sample_rate, offset=offset, duration=duration, mono=True, res_type='kaiser_fast')
    except:
        sig, rate = [], sample_rate
    return sig, rate

def splitSignal(sig, rate, seconds, overlap, minlen):

    # Split signal with overlap
    sig_splits = []
    for i in range(0, len(sig), int((seconds - overlap) * rate)):
        split = sig[i:i + int(seconds * rate)]

        # End of signal?
        if len(split) < int(minlen * rate):
            break
        
        # Signal chunk too short?
        if len(split) < int(rate * seconds):
            split = np.hstack((split, noise(split, (int(rate * seconds) - len(split)), 0.5)))
        
        sig_splits.append(split)

    return sig_splits

def noise(sig, shape, amount=None):

    # Random noise intensity
    if amount == None:
        amount = RANDOM.uniform(0.1, 0.5)

    # Create Gaussian noise
    try:
        noise = RANDOM.normal(min(sig) * amount, max(sig) * amount, shape)
    except:
        noise = np.zeros(shape)

    return noise.astype('float32')
