import sys
import copy
import numpy as np
from scipy.spatial import distance
from scipy import stats
from statsmodels.distributions.empirical_distribution import ECDF

inputFile=open(sys.argv[1],"r")

q = lambda i,j,n: n*j - j*(j+1)/2 + i - 1 - j

# load structure data
inputLoci = []
inputData = []
for inputFileLine in inputFile:
    inputFileLineData = inputFileLine.strip().split()
    inputLoci.append(int(inputFileLineData[1]))
    inputData.append(map(float, inputFileLineData[2:]))
numOfLoci = len(inputLoci)
numOfStructures = len(inputData[0])/3
numOfPairs = numOfLoci*(numOfLoci-1)/2
sys.stderr.write('read '+str(numOfLoci)+' loci from '+str(numOfStructures)+' structures\n')
inputLociNumpy = np.array(inputLoci, dtype=int)
inputDataNumpy = np.array(inputData, dtype=float)

# find resolution and max separation
lociPdist = distance.pdist(np.reshape(inputLociNumpy, [numOfLoci, 1])).astype(int)
resolution = min(lociPdist)
maxSeparation = max(lociPdist)
sys.stderr.write('resolution = '+str(resolution)+' max separation = '+str(maxSeparation)+'\n')

# calculate pairwise distance
pdistArray = np.empty([numOfPairs, numOfStructures], dtype=float)
for i in range(numOfStructures):
    sys.stderr.write('calculating pairwise distances for structure '+str(i+1)+'\n')
    pdistArray[:,i] = distance.pdist(inputDataNumpy[:,(3*i):(3*i+3)])

# calculate KS for each separation
testMatrix = np.empty(numOfPairs, dtype=float)
pMatrix = np.empty(numOfPairs, dtype=float)
for separation in range(resolution, maxSeparation+resolution, resolution):
    sys.stderr.write('performing U tests for separation '+str(separation/1e6)+' Mb\n')
    pdistIndices = np.where(lociPdist == separation)
    backgroundDistances = pdistArray[pdistIndices, :].flatten()
    for pdistIndex in np.nditer(pdistIndices):
        testResult = stats.mannwhitneyu(pdistArray[pdistIndex, :], backgroundDistances)
        testMatrix[pdistIndex] = testResult[0]
        pMatrix[pdistIndex] = testResult[1]
np.savetxt('test.txt', testMatrix, delimiter='\t')
np.savetxt('p.txt', pMatrix, delimiter='\t')