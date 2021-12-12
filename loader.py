from pathlib import Path
import numpy as np
from pydub import AudioSegment


def loadPath(folderPath: str) -> tuple:
    """
    Gets Path for each file in folder

    :param folderPath: relative path of the folder
    :return: list containing file name and file path
    """
    basePath = Path(folderPath)
    filesInPath = (item for item in basePath.iterdir() if item.is_file())
    for item in filesInPath:
        yield (item.stem, item.relative_to(basePath.parent))


def mp3ToData(filePaths: str, fMilliSeconds: float = None) -> tuple:
    """
    Loads MP3 audio file 

    :param filePath: relative path of the file
    :param fSeconds: number of millie seconds you want to load, if not it will load all the file
    :return: data of song and frame rate
    """
    if fMilliSeconds:
        audioFile = AudioSegment.from_mp3(filePaths)[:fMilliSeconds]
    else:
        audioFile = AudioSegment.from_mp3(filePaths)
    data = np.array(audioFile.get_array_of_samples())
    rate = audioFile.frame_rate
    print(data[0:100])
    return data, rate

# testing shit
# Songs = loadPath("Songs/")
# for song in Songs:
# print(song)

# data , rate = mp3ToData(Songs[0][1], 10000)
# print(data)
# print(rate)
