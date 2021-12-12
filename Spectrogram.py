from scipy import signal
import json
import librosa as l
from numpy import ndarray

class spectrogram():
    """
    Responsible for creating spectrograms for any .wav file
    implements the following:
    - reads a loaded wav file data and creates the associated spectrum
    - save the spectrum created in an arbitrary file
    """
    def __init__(self):
        """
        Class Initializer

        Parameters
        -----------
        - sampleFreqs : holds the sampled frequencies
        - sampleTime : holds the sampled time rates
        - colorMesh : holds the value (intenisty) of the frequency component
        - container : a dictionary used in the saved process
        """
        self.sampleFreqs = None
        self.sampleTime = None
        self.colorMesh = None
        self.features = None
        self.container = None

    def __call__(self, songData: ndarray, songSR: int, window:str, fileName:str = None,
                 path:str = None, compressed: bool = False, featureize:bool = False):
        """
        Caller function for the class which maintains all it's implemented methods.

        Parameters
        -----------
        - songData: a numpy array of the read wav file
        - songSR : integer representing the sample rate
        - window : a str specifying the widow type used in creating the spectrogram
        - path : str if specified the file is saved in the given path
        - fileName : if provided the spectrogram will be saved as a json file
        - compressed : if True only the color mesh will be saved
        - featurize : if True spectrogram`s main features will be extracted and saved if specified saving
        """
        self._spectrogram(songData, songSR, window)
        if featureize:
            self.features= self.spectralFeatures(None, self.colorMesh, songSR,window)
        print("spectrogram created")

        if fileName:
            if path is None:
                self._saveFormat('', fileName, compressed=compressed, featurize=featureize)
                print("saved in main directory .. ")
            else:
                self._saveFormat(path, fileName, compressed=compressed, featurize=featureize)
            print("spectrogram saved")

    def _spectrogram(self, songData: ndarray, songSampleRate:int=22050, windowType: str="hann")->tuple:
        """
        Creates a Spectrogram of the given data

        Parameters
        -----------
        - songData : a numpy array of the read wav file
        - songSampleRate : integer representing the sample rate
        - windowType : a str specifying the widow type used in creating the spectrogram
        """
        if len(songData.shape) == 2:
            print("song is stereo")
            print("Converting ..")
            self.sampleFreqs, self.sampleTime, self.colorMesh = signal.spectrogram(songData[:, 0],
                                                                                   fs=songSampleRate, window=windowType)
        else:
            self.sampleFreqs, self.sampleTime, self.colorMesh = signal.spectrogram(songData,
                                                                                   fs=songSampleRate, window=windowType)
        return (self.sampleFreqs, self.sampleTime, self.colorMesh)

    def _saveFormat(self, folder:str, filename:str, featurize : bool = False, compressed: bool = False):
        """
        Save the spectrum in a specified filename.json

        Parameters
        -----------
        - folder : a path to the file location
        - filename : the file name
        - compressed : if True only the color mesh will be saved
        - featurize : if True adds the main features of the spectrogram
        """
        # TODO : Refactor this part .. return function
        if compressed:
            self.container = {"color_mesh": self.colorMesh.tolist()}
        else:
            self.container = {'sample_frequencies': self.sampleFreqs.tolist(),
                              "sample_time": self.sampleTime.tolist(),
                              "color_mesh": self.colorMesh.tolist()}
        if featurize:
            self.container['features'] = self.features

        with open(folder+filename+".json", 'w') as outfile:
            json.dump(self.container, outfile)

    def spectralFeatures(self, song: "ndarray"= None, S: "ndarray" = None, sr: int = 22050, window:'str'='hann'):
        """
        Calculates the Spectral Centroid of a given data or the data instantiated in the class.

        Parameters
        -----------
        - song  : wav file array
        - S    : spectrogram readings
        - sr : sampling frequency default 22050
        - window: a string specifying the window applied default hann (see options).


        Options
        -------
        - boxcar
        - triang
        - blackman
        - hamming
        - hann
        - bartlett
        - flattop
        - parzen
        - bohman
        - blackmanharris
        - nuttall
        - barthann
        - kaiser (needs beta)
        - gaussian (needs standard deviation)
        - general_gaussian (needs power, width)
        - slepian (needs width)
        - dpss (needs normalized half-bandwidth)
        - chebwin (needs attenuation)
        - exponential (needs decay scale)
        - tukey (needs taper fraction)
        """
        return (l.feature.melspectrogram(y=song, S=S, sr=sr, window=window),
                l.feature.mfcc(y=song.astype('float64'), sr=sr),
                l.feature.chroma_stft(y= song, S=S, sr=sr, window=window))

if __name__ == '__main__':
    # Basic Usage

    from scipy.io import wavfile
    sampleRate, songdata = wavfile.read("tests/Adele_Million_Years_Ago_10.wav")
    spectrum = spectrogram()
    spectrum(songdata, sampleRate,"hann", featureize=True)
    # print(spectrum.features
    # spectrogram()._spectralFeatures()



