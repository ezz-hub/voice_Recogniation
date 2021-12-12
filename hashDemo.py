from helpers import *
from math import ceil

hammingDifferences = []        # List contains the hamming distance of spectrogram hashes of all the songs and the mix
feature1Differences = []       # List contains the hamming distance of feature 1 hashes of all the songs and the mix
feature2Differences = []       # List contains the hamming distance of feature 2 hashes of all the songs and the mix
feature3Differences = []       # List contains the hamming distance of feature 3 hashes of all the songs and the mix

similarities = []              # List contains the similarity percentage of all the songs and the mix (Using Spectrogram Hash Only)
feature1Similarities = []      # List contains the similarity percentage of all the songs and the mix (Using feature 1 Hash Only)
feature2Similarities = []      # List contains the similarity percentage of all the songs and the mix (Using feature 2 Hash Only)
feature3Similarities = []      # List contains the similarity percentage of all the songs and the mix (Using feature 3 Hash Only)

avgSimilaritiesAll = []        # List contains the similarity percentage of all the songs and the mix (Using average hash of Spectrogram and all the features)
weight = 0.8                   # Weight of the first song when mixing 2 songs

# Load Songs
song1 = loadSong("Songs/Adele_Million_Years_Ago_10.mp3", 60000)
song2 = loadSong("Songs/ImagineDragons_natural_10.mp3", 60000)
song3 = loadSong("Songs/Birdy_strange_birds_10.mp3", 60000)
song4 = loadSong("Songs/Spacetoon_remi_11.mp3", 60000)
song5 = loadSong("Songs/Adele_Million_Years_Ago_10_music.mp3", 60000)
song6 = loadSong("Songs/Adele_Million_Years_Ago_10_vocals.mp3", 60000)
songs = [song1, song2, song3, song4, song5, song6]

# Mix 2 songs -> Create Spectrogram -> Create Hash
mixedSong = mixSongs(song1['data'], song2['data'], w=weight)
sampleFrequency, sampleTime, colorMesh = signal.spectrogram(mixedSong, fs=song1['sRate'], window='hann')
f1 = l.feature.melspectrogram(y= mixedSong, S=colorMesh, sr=song1['sRate'], window = 'hann')
f2 = l.feature.mfcc(y= mixedSong.astype('float64'), sr=song1['sRate'])
f3 = l.feature.chroma_stft(y= mixedSong, S=colorMesh, sr=song1['sRate'], window = 'hann')

hashMix = createPerceptualHash(colorMesh)
f1HashMix = createPerceptualHash(f1)
f2HashMix = createPerceptualHash(f2)
f3HashMix = createPerceptualHash(f3)

# Calculate Hamming Distance and Map the values
# For the spectrogram and the 3 features (melspectrogram, mfcc and chroma_stft)
for i in range(4):
    hammingDifferences.append(getHammingDistance(hash1=songs[i]['spectrogram_Hash'], hash2=hashMix))

    feature1Differences.append(getHammingDistance(hash1=songs[i]['melspectrogram_Hash'], hash2=f1HashMix))
    feature2Differences.append(getHammingDistance(hash1=songs[i]['mfcc_Hash'], hash2=f2HashMix))
    feature3Differences.append(getHammingDistance(hash1=songs[i]['chroma_stft_Hash'], hash2=f3HashMix))

    feature1Similarities.append(mapRanges(feature1Differences[i], 0, 255, 0, 1))
    feature2Similarities.append(mapRanges(feature2Differences[i], 0, 255, 0, 1))
    feature3Similarities.append(mapRanges(feature3Differences[i], 0, 255, 0, 1))

    similarities.append(mapRanges(hammingDifferences[i], 0, 255, 0, 1))

# Calculate the average of spectrogram hash and all features hashes
for i in range(4):
    avg = (hammingDifferences[i]+feature1Differences[i]+feature2Differences[i]+feature3Differences[i])/4
    avgMap = mapRanges(avg, 0, 255, 0, 1)
    result = (1 - avgMap) * 100
    avgSimilaritiesAll.append(result)

# # Print the results
# print(f'''
# -- Spectrogram Hash --
# hash1 (Adele)  : {song1['spectrogram_Hash']}
# hash2 (Imagine): {song2['spectrogram_Hash']}
# hash3 (Birdy)  : {song3['spectrogram_Hash']}
# hash4 (Remi)   : {song4['spectrogram_Hash']}
# {weight}: {song1['name']}
# {ceil((1-weight)*10)/10}: {song2['name']}
# mixHash: {hashMix}
#
# ---- Checking Using Spectrogram Hashing ----
# Difference {song1['name']} and Mix = {hammingDifferences[0]}
# Difference {song2['name']} and Mix = {hammingDifferences[1]}
# Difference {song3['name']} and Mix = {hammingDifferences[2]}
# Difference {song4['name']} and Mix = {hammingDifferences[3]}
#
# Similarity of {song1['name']} with the mix = {(1-similarities[0])*100}%
# Similarity of {song2['name']} with the mix = {(1-similarities[1])*100}%
# Similarity of {song3['name']} with the mix = {(1-similarities[2])*100}%
# Similarity of {song4['name']} with the mix = {(1-similarities[3])*100}%
# ''')
#
# print(f'''
# ---- Checking Using melspectrogram Hashing ----
# hash1: {song1['melspectrogram_Hash']}
# hash2: {song2['melspectrogram_Hash']}
# hash3: {song3['melspectrogram_Hash']}
# hash4: {song4['melspectrogram_Hash']}
#
# Difference {song1['name']} and Mix = {feature1Differences[0]}
# Difference {song2['name']} and Mix = {feature1Differences[1]}
# Difference {song3['name']} and Mix = {feature1Differences[2]}
# Difference {song4['name']} and Mix = {feature1Differences[3]}
#
# Similarity of {song1['name']} with the mix = {(1-feature1Similarities[0])*100}%
# Similarity of {song2['name']} with the mix = {(1-feature1Similarities[1])*100}%
# Similarity of {song3['name']} with the mix = {(1-feature1Similarities[2])*100}%
# Similarity of {song4['name']} with the mix = {(1-feature1Similarities[3])*100}%
# ''')
#
# print(f'''
# ---- Checking Using mfcc Hashing ----
# hash1: {song1['mfcc_Hash']}
# hash2: {song2['mfcc_Hash']}
# hash3: {song3['mfcc_Hash']}
# hash4: {song4['mfcc_Hash']}
#
# Difference {song1['name']} and Mix = {feature2Differences[0]}
# Difference {song2['name']} and Mix = {feature2Differences[1]}
# Difference {song3['name']} and Mix = {feature2Differences[2]}
# Difference {song4['name']} and Mix = {feature2Differences[3]}
#
# Similarity of {song1['name']} with the mix = {(1-feature2Similarities[0])*100}%
# Similarity of {song2['name']} with the mix = {(1-feature2Similarities[1])*100}%
# Similarity of {song3['name']} with the mix = {(1-feature2Similarities[2])*100}%
# Similarity of {song4['name']} with the mix = {(1-feature2Similarities[3])*100}%
# ''')
#
# print(f'''
# ---- Checking Using chroma_stft Hashing ----
# hash1: {song1['chroma_stft_Hash']}
# hash2: {song2['chroma_stft_Hash']}
# hash3: {song3['chroma_stft_Hash']}
# hash4: {song4['chroma_stft_Hash']}
#
# Difference {song1['name']} and Mix = {feature3Differences[0]}
# Difference {song2['name']} and Mix = {feature3Differences[1]}
# Difference {song3['name']} and Mix = {feature3Differences[2]}
# Difference {song4['name']} and Mix = {feature3Differences[3]}
#
# Similarity of {song1['name']} with the mix = {(1-feature3Similarities[0])*100}%
# Similarity of {song2['name']} with the mix = {(1-feature3Similarities[1])*100}%
# Similarity of {song3['name']} with the mix = {(1-feature3Similarities[2])*100}%
# Similarity of {song4['name']} with the mix = {(1-feature3Similarities[3])*100}%
# ''')
#
#
# print(f'''
# ---- Checking Using Average Of (Spectrogram + All Features) Hashing ----
# Similarity of {song1['name']} with the mix = {avgSimilaritiesAll[0]}%
# Similarity of {song2['name']} with the mix = {avgSimilaritiesAll[1]}%
# Similarity of {song3['name']} with the mix = {avgSimilaritiesAll[2]}%
# Similarity of {song4['name']} with the mix = {avgSimilaritiesAll[3]}%
# ''')
