from PIL import Image
import imagehash
from imagehash import hex_to_hash
import numpy as np
from scipy import signal
from pydub import AudioSegment
import librosa as l


def loadAudioFile(filePath: str, fSeconds: float = None) -> dict:
    """
    Loads any audio file

    :param filePath: relative path of the file
    :param fSeconds: number of seconds you want to load, if not it will load all the file
    :return: Dictionary contains songName, array of the data, sample rate, dataType of the array
    """
    if fSeconds:
        audioFile = AudioSegment.from_mp3(filePath)[:fSeconds]
    else:
        audioFile = AudioSegment.from_mp3(filePath)
    songName = filePath.split('/')[-1].split('.mp3')[0]
    songData = np.array(audioFile.get_array_of_samples())
    sampleRate = audioFile.frame_rate
    songDataType = songData.dtype
    songDictionary = {
        "name": songName,
        "data": songData,
        "sRate": sampleRate,
        "dType": songDataType,
        "spectrogram_Hash": None,
        "melspectrogram_Hash": None,
        "mfcc_Hash": None,
        "chroma_stft_Hash": None,
    }
    return songDictionary


def _spectralFeatures(song: "np.ndarray"= None, S: "np.ndarray" = None, sr: int = 22050, window: str = 'hann'):
    """
    Calculates the Spectral Centroid of a given data or the data instantiated in the class

    Parameters
    -----------
    - song  : wav file array
    - S    : spectrogram readings
    - sr : sampling frequency default 22050
    - window: a string specifying the window applied default hann (see options)
    """
    return [l.feature.melspectrogram(y=song, S=S, sr=sr, window=window),
            l.feature.mfcc(y=song.astype('float64'), sr=sr),
            l.feature.chroma_stft(y= song, S=S, sr=sr, window=window)]


def mixSongs(song1: np.ndarray, song2: np.ndarray, dType: str = 'int16', w: float = 0.5) -> np.ndarray:
    """
    Mixes 2 songs with the given weight
    :param song1: data array of the song1
    :param song2: data array of the song2
    :param dType: data type of the song
    :param w: weight (percentage) of song1
    :return array of the mixing songs
    """
    return (w*song1 + (1.0-w)*song2).astype(dType)


def createPerceptualHash(arrayData: "np.ndarray") -> str:
    """
    Creates a perceptual hash of the given data
    :param arrayData: an array contains the data to be hashed
    :return: a string describe the hashed array (could be converted to hex using hex_to_hash())
    """
    dataInstance = Image.fromarray(arrayData)
    return imagehash.phash(dataInstance, hash_size=16).__str__()


def getHammingDistance(hash1: str, hash2: str) -> int:
    """
    Gets the hamming distance of 2 hashes
    :param hash1: value of first hash
    :param hash2: value of second hash
    :return: an integer describe the hamming distance between the 2 hashes
    """
    return hex_to_hash(hash1) - hex_to_hash(hash2)


def loadSong(filePath: str, fSeconds: float = None) -> dict:
    """
    Loads any audio file, create a spectrogram, extract some features and hash them.

    :param filePath: relative path of the file
    :param fSeconds: number of seconds you want to load, if not it will load all the file
    :return: Dictionary contains songName, array of the data, sample rate, dataType of the array and the hashes
    """
    song = loadAudioFile(filePath, fSeconds)
    sampleFreqs, sampleTime, colorMesh = signal.spectrogram(song['data'], fs=song['sRate'], window='hann')
    features = _spectralFeatures(song=song['data'], S=colorMesh, sr=song['sRate'])
    song['spectrogram_Hash'] = createPerceptualHash(colorMesh)
    song['melspectrogram_Hash'] = createPerceptualHash(features[0])
    song['mfcc_Hash'] = createPerceptualHash(features[1])
    song['chroma_stft_Hash'] = createPerceptualHash(features[2])
    return song


def mapRanges(inputValue: float, inMin: float, inMax: float, outMin: float, outMax: float):
    """
    Map a given value from range 1 -> range 2
    :param inputValue: The value you want to map
    :param inMin: Minimum Value of Range 1
    :param inMax: Maximum Value of Range 1
    :param outMin: Minimum Value of Range 2
    :param outMax: Maximum Value of Range 2
    :return: The new Value in Range 2
    """
    slope = (outMax-outMin) / (inMax-inMin)
    return outMin + slope*(inputValue-inMin)

