from helpers import createPerceptualHash
from Spectrogram import spectrogram
import loader
import json

def updateDB(filePath:str, fileOut:str, mode: str = "a"):
    """
    Responsible for creating the database from a folder given.

    Implements the following :

    - Loads a specific folder given in the command
    - Create Spectrogram and feature hashes
    - Save these hashes in a specified json file

    ============= ==========================================
    **Arguments**
    filePath      A string path to the input file with the database songs.
    fileOut       A string path to the output directory to save the json file.
    mode          String used to write in json file.
    ============= ==========================================
    """
    d = {}

    for audFile, path in loader.loadPath(filePath):
        data, rate = loader.mp3ToData(path, 60000)
        _, _, mesh = spectrogram()._spectrogram(data, rate)

        feats = spectrogram().spectralFeatures(data, mesh, rate)
        features = []
        spectrohash = createPerceptualHash(mesh)
        for feature in feats :
            features.append(createPerceptualHash(feature))

        d.update({audFile: {"spectrohash": spectrohash, "features": features}})
        print("%s is hashed" % audFile)

    with open(fileOut+"db.json", mode) as outfile:
        json.dump(d, outfile, indent=4)


def readJson(file):
    """
    Reads a specified json file and return its contents.

    implements the following :

    - open a given json file and create a generator
      returning it's contents with a yield

    ============= ===================================================================================
    **Arguments**
    file          a string path to the file to be read
    ============= ===================================================================================
    """
    with open(file) as jsonFile:
        data = json.load(jsonFile)
    for song in data:
        yield song, data[song]


if __name__ == '__main__':
    import sys
    import warnings

    warnings.filterwarnings("ignore")

    if sys.argv[1] and sys.argv[2]:
        updateDB(sys.argv[1], sys.argv[2], "w")
    else:
        for i in readJson("db.json"):
            print(i)
            print("File paths not given")

    print("End of Script")
