import functools
import pandas as pd
from PAMI.fuzzyFrequentSpatialPattern.basic.abstract import *


class FFList:
    """
     A class represent a Fuzzy List of an element

    Attributes :
    ----------
         item: int
             the item name
         sumIUtil: float
             the sum of utilities of an fuzzy item in database
         sumRUtil: float
             the sum of resting values of a fuzzy item in database
         elements: list
             a list of elements contain tid,Utility and resting values of element in each transaction
    Methods :
    -------
        addElement(element)
            Method to add an element to this fuzzy list and update the sums at the same time.

        printElement(e)
            Method to print elements            

    """

    def __init__(self, itemName):
        self.item = itemName
        self.sumIUtil = 0.0
        self.sumRUtil = 0.0
        self.elements = []

    def addElement(self, element):
        """
            A Method that add a new element to FFList

            :param element: an element to be add to FFList
            :pram type: Element
        """
        self.sumIUtil += element.iUtils
        self.sumRUtil += element.rUtils
        self.elements.append(element)

    def printElement(self):
        """
            A Method to Print elements in the FFList
        """
        for ele in self.elements:
            print(ele.tid, ele.iUtils, ele.rUtils)


class Element:
    """
        A class represents an Element of a fuzzy list

    Attributes :
    ----------
        tid : int
            keep tact of transaction id
        iUtils: float
            the utility of an fuzzy item in the transaction
        rUtils : float
            the neighbourhood resting value of an fuzzy item in the transaction
    """

    def __init__(self, tid, iUtil, rUtil):
        self.tid = tid
        self.iUtils = iUtil
        self.rUtils = rUtil


class Regions:
    """
            A class calculate the regions

    Attributes :
    ----------
            low : int
                low region value
            middle: int 
                middle region value
            high : int
                high region values
        """

    def __init__(self, quantity, regionsNumber):
        self.low = 0
        self.middle = 0
        self.high = 0
        if regionsNumber == 3:  # if we have 3 regions
            if 0 < quantity <= 1:
                self.low = 1
                self.high = 0
                self.middle = 0
            elif 1 < quantity <= 6:
                self.low = float((6 - quantity) / 5)
                self.middle = float((quantity - 1) / 5)
                self.high = 0
            elif 6 < quantity <= 11:
                self.low = 0
                self.middle = float((11 - quantity) / 5)
                self.high = float((quantity - 6) / 5)
            else:
                self.low = 0
                self.middle = 0
                self.high = 1


class Pair:
    """
        A class to store item and it's quantity together
    """

    def __init__(self):
        self.item = 0
        self.quantity = 0


class FFSPMiner(fuzzySpatialFrequentPatterns):
    """
        Fuzzy Frequent Spatial Pattern-Miner is desired to find all Spatially frequent fuzzy patterns
        which is on-trivial and challenging problem to its huge search space.we are using efficient pruning
         techniques to reduce the search space.

    Attributes :
    ----------
        iFile : file
            Name of the input file to mine complete set of fuzzy spatial frequent patterns
        oFile : file
               Name of the oFile file to store complete set of fuzzy spatial frequent patterns
        minSup : float
            The user given minimum support
        neighbors: map
            keep track of neighbours of elements
        memoryRSS : float
                To store the total amount of RSS memory consumed by the program
        startTime:float
               To record the start time of the mining process
        endTime:float
            To record the completion time of the mining process
        itemsCnt: int
            To record the number of fuzzy spatial itemSets generated
        mapItemsLowSum: map
            To keep track of low region values of items
        mapItemsMidSum: map
            To keep track of middle region values of items
        mapItemsHighSum: map
            To keep track of high region values of items
        mapItemSum: map
            To keep track of sum of Fuzzy Values of items
        mapItemRegions: map
            To Keep track of fuzzy regions of item
        jointCnt: int
            To keep track of the number of FFI-list that was constructed
        BufferSize: int
            represent the size of Buffer
        itemBuffer list
            to keep track of items in buffer
    Methods :
    -------
        startMine()
            Mining process will start from here
        getPatterns()
            Complete set of patterns will be retrieved with this function
        savePatterns(oFile)
            Complete set of frequent patterns will be loaded in to a output file
        getPatternsAsDataFrame()
            Complete set of frequent patterns will be loaded in to a dataframe
        getMemoryUSS()
            Total amount of USS memory consumed by the mining process will be retrieved from this function
        getMemoryRSS()
            Total amount of RSS memory consumed by the mining process will be retrieved from this function
        getRuntime()
            Total amount of runtime taken by the mining process will be retrieved from this function            
        convert(value):
            To convert the given user specified value
        FSFIMining( prefix, prefixLen, fsFim, minSup)
            Method generate FFI from prefix
        construct(px, py)
            A function to construct Fuzzy itemSet from 2 fuzzy itemSets
        Intersection(neighbourX,neighbourY)
            Return common neighbours of 2 itemSet Neighbours
        findElementWithTID(uList, tid)
            To find element with same tid as given
        WriteOut(prefix, prefixLen, item, sumIUtil,period)
            To Store the patten
    
    Executing the code on terminal :
    -------
        Format:
            python3 FFSPMiner.py <inputFile> <outputFile> <neighbours> <minSup> <sep>
        Examples:
            python3  FFSPMiner.py sampleTDB.txt output.txt sampleN.txt 3  (minSup will be considered in support count or frequency)

            python3  FFSPMiner.py sampleTDB.txt output.txt sampleN.txt 0.3 (minSup and maxPer will be considered in percentage of database)
                                                            (will consider "\t" as separator in both input and neighbourhood files)

            python3  FFSPMiner.py sampleTDB.txt output.txt sampleN.txt 3 ,
                                                              (will consider "," as separator in both input and neighbourhood files)
    Sample run of importing the code:
    -------------------------------
        
        from PAMI.fuzzyFrequentSpatialPattern import FFSPMiner as alg

        obj = alg.FFSPMiner("input.txt", "neighbours.txt", 2)

        obj.startMine()

        fuzzySpatialFrequentPatterns = obj.getPatterns()

        print("Total number of fuzzy frequent spatial patterns:", len(fuzzySpatialFrequentPatterns))

        obj.savePatterns("outputFile")

        memUSS = obj.getMemoryUSS()

        print("Total Memory in USS:", memUSS)

        memRSS = obj.getMemoryRSS()

        print("Total Memory in RSS", memRSS)

        run = obj.getRuntime()

        print("Total ExecutionTime in seconds:", run)

    Credits:
    -------
            The complete program was written by B.Sai Chitra under the supervision of Professor Rage Uday Kiran.
    """
    startTime = float()
    endTime = float()
    minSup = str()
    maxPer = float()
    finalPatterns = {}
    iFile = " "
    oFile = " "
    nFile =" "
    memoryUSS = float()
    memoryRSS = float()
    sep="\t"
    transactions = []
    fuzzyValues = []

    def __init__(self, iFile, nFile, minSup, sep="\t"):
        super().__init__(iFile, nFile, minSup, sep)
        self.mapItemNeighbours = {}
        self.startTime = 0
        self.endTime = 0
        self.itemsCnt = 0
        self.mapItemsLowSum = {}
        self.mapItemsMidSum = {}
        self.mapItemsHighSum = {}
        self.mapItemSum = {}
        self.mapItemRegions = {}
        self.joinsCnt = 0
        self.BufferSize = 200
        self.itemSetBuffer = []
        self.finalPatterns = {}
        self.dbLen = 0

    def compareItems(self, o1, o2):
        """
            A Function that sort all FFI-list in ascending order of Support
        """
        compare = self.mapItemSum[o1.item] - self.mapItemSum[o2.item]
        if compare == 0:
            return o1.item - o2.item
        else:
            return compare

    def convert(self, value):
        """
        To convert the given user specified value
        :param value: user specified value
        :return: converted value
        """
        if type(value) is int:
            value = int(value)
        if type(value) is float:
            value = (self.dbLen * value)
        if type(value) is str:
            if '.' in value:
                value = (self.dbLen * value)
            else:
                value = int(value)
        return value

    def creatingItemSets(self):
        self.transactions, self.fuzzyValues = [], []
        if isinstance(self.iFile, pd.DataFrame):
            if self.iFile.empty:
                print("its empty..")
            i = self.iFile.columns.values.tolist()
            if 'Transactions' in i:
                self.transactions = self.iFile['Transactions'].tolist()
            if 'fuzzyValues' in i:
                self.fuzzyValues = self.iFile['Utilities'].tolist()

        if isinstance(self.iFile, str):
            if validators.url(self.iFile):
                data = urlopen(self.iFile)
                for line in data:
                    line = line.decode("utf-8")
                    line = line.split("\n")[0]
                    parts = line.split(":")
                    items = parts[0].split(self.sep)
                    quantities = parts[2].split(self.sep)
                    self.transactions.append([x for x in items])
                    self.fuzzyValues.append([x for x in quantities])
            else:
                try:
                    with open(self.iFile, 'r', encoding='utf-8') as f:
                        for line in f:
                            line = line.split("\n")[0]
                            parts = line.split(":")
                            items = parts[0].split(self.sep)
                            quantities = parts[2].split(self.sep)
                            self.transactions.append([x for x in items])
                            self.fuzzyValues.append([x for x in quantities])
                except IOError:
                    print("File Not Found")
                    quit()

    def mapNeighbours(self):
        if isinstance(self.nFile, pd.DataFrame):
            data, items = [], []
            if self.nFile.empty:
                print("its empty..")
            i = self.nFile.columns.values.tolist()
            if 'items' in i:
                items = self.nFile['items'].tolist()
            if 'Neighbours' in i:
                data = self.nFile['Neighbours'].tolist()
            for k in range(len(items)):
                self.mapItemNeighbours[items[k]] = data[k]

        if isinstance(self.nFile, str):
            if validators.url(self.nFile):
                data = urlopen(self.nFile)
                for line in data:
                    line = line.decode("utf-8")
                    line = line.split("\n")[0]
                    parts = [i.rstrip() for i in line.split(self.sep)]
                    parts = [x for x in parts]
                    item = parts[0]
                    neigh1 = []
                    for i in range(1, len(parts)):
                        neigh1.append(parts[i])
                    self.mapItemNeighbours[item] = neigh1
            else:
                try:
                    with open(self.iFile, 'r', encoding='utf-8') as f:
                        for line in f:
                            line = line.split("\n")[0]
                            parts = [i.rstrip() for i in line.split(self.sep)]
                            parts = [x for x in parts]
                            item = parts[0]
                            neigh1 = []
                            for i in range(1, len(parts)):
                                neigh1.append(parts[i])
                            self.mapItemNeighbours[item] = neigh1
                except IOError:
                    print("File Not Found")
                    quit()

    def startMine(self):
        """ Frequent pattern mining process will start from here
        """
        self.startTime = time.time()
        self.creatingItemSets()
        self.finalPatterns = {}
        self.mapNeighbours()
        for line in range(len(self.transactions)):
            items = self.transactions[line]
            quantities = self.fuzzyValues[line]
            self.dbLen += 1
            for i in range(0, len(items)):
                regions = Regions(int(quantities[i]), 3)
                item = items[i]
                if item in self.mapItemsLowSum.keys():
                    low = self.mapItemsLowSum[item]
                    low += regions.low
                    self.mapItemsLowSum[item] = low
                else:
                    self.mapItemsLowSum[item] = regions.low
                if item in self.mapItemsMidSum.keys():
                    mid = self.mapItemsMidSum[item]
                    mid += regions.middle
                    self.mapItemsMidSum[item] = mid
                else:
                    self.mapItemsMidSum[item] = regions.middle
                if item in self.mapItemsHighSum.keys():
                    high = self.mapItemsHighSum[item]
                    high += regions.high
                    self.mapItemsHighSum[item] = high
                else:
                    self.mapItemsHighSum[item] = regions.high
        listOfFFList = []
        mapItemsToFFLIST = {}
        self.minSup = self.convert(self.minSup)
        minSup = self.minSup
        for item1 in self.mapItemsLowSum.keys():
            item = item1
            low = self.mapItemsLowSum[item]
            mid = self.mapItemsMidSum[item]
            high = self.mapItemsHighSum[item]
            if low >= mid and low >= high:
                self.mapItemSum[item] = low
                self.mapItemRegions[item] = "L"
            elif mid >= low and mid >= high:
                self.mapItemSum[item] = mid
                self.mapItemRegions[item] = "M"
            elif high >= low and high >= mid:
                self.mapItemRegions[item] = "H"
                self.mapItemSum[item] = high
            if self.mapItemSum[item] >= self.minSup:
                fuList = FFList(item)
                mapItemsToFFLIST[item] = fuList
                listOfFFList.append(fuList)
        listOfFFList.sort(key=functools.cmp_to_key(self.compareItems))
        tid = 0
        for line in range(len(self.transactions)):
            items = self.transactions[line]
            quantities = self.fuzzyValues[line]
            revisedTransaction = []
            for i in range(0, len(items)):
                pair = Pair()
                pair.item = items[i]
                regions = Regions(int(quantities[i]), 3)
                item = pair.item
                if self.mapItemSum[item] >= minSup:
                    if self.mapItemRegions[pair.item] == "L":
                        pair.quantity = regions.low
                    elif self.mapItemRegions[pair.item] == "M":
                        pair.quantity = regions.middle
                    elif self.mapItemRegions[pair.item] == "H":
                        pair.quantity = regions.high
                    if pair.quantity > 0:
                        revisedTransaction.append(pair)
            revisedTransaction.sort(key=functools.cmp_to_key(self.compareItems))
            for i in range(len(revisedTransaction) - 1, -1, -1):
                pair = revisedTransaction[i]
                remainUtil = 0
                for j in range(len(revisedTransaction) - 1, i, -1):
                    if self.mapItemNeighbours.get(pair.item) is None:
                        continue
                    if revisedTransaction[j].item in self.mapItemNeighbours[pair.item]:
                        remainUtil += revisedTransaction[j].quantity
                remainingUtility = remainUtil
                if mapItemsToFFLIST.get(pair.item) is not None:
                    FFListOfItem = mapItemsToFFLIST[pair.item]
                    element = Element(tid, pair.quantity, remainingUtility)
                    FFListOfItem.addElement(element)
            tid += 1
        itemNeighbours = list(self.mapItemNeighbours.keys())
        self.FSFIMining(self.itemSetBuffer, 0, listOfFFList, self.minSup, itemNeighbours)
        self.endTime = time.time()
        process = psutil.Process(os.getpid())
        self.memoryUSS = float()
        self.memoryRSS = float()
        self.memoryUSS = process.memory_full_info().uss
        self.memoryRSS = process.memory_info().rss

    def FSFIMining(self, prefix, prefixLen, FSFIM, minSup, itemNeighbours):
        """Generates FFSPMiner from prefix

        :param prefix: the prefix patterns of FFSPMiner
        :type prefix: len
        :param prefixLen: the length of prefix
        :type prefixLen: int
           :param FSFIM: the Fuzzy list of prefix itemSets
           :type FSFIM: list
           :param minSup: the minimum support of 
           :type minSup:int
           :param itemNeighbours: the set of common neighbours of prefix
           :type itemNeighbours: list or set
        """
        for i in range(0, len(FSFIM)):
            X = FSFIM[i]
            if X.sumIUtil >= minSup:
                self.WriteOut(prefix, prefixLen, X.item, X.sumIUtil)
            newNeighbours = self.Intersection(self.mapItemNeighbours.get(X.item), itemNeighbours)
            if X.sumRUtil >= minSup:
                exULs = []
                for j in range(i + 1, len(FSFIM)):
                    Y = FSFIM[j]
                    if Y.item in newNeighbours:
                        exULs.append(self.construct(X, Y))
                        self.joinsCnt += 1
                self.itemSetBuffer.insert(prefixLen, X.item)
                self.FSFIMining(self.itemSetBuffer, prefixLen + 1, exULs, minSup, newNeighbours)

    def Intersection(self, neighbourX, neighbourY):
        """
            A function to get common neighbours from 2 itemSets
            :param neighbourX: the set of neighbours of itemSet 1
            :type neighbourX: set or list
            :param neighbourY: the set of neighbours of itemSet 2
            :type neighbourY: set or list
            :return : set of common neighbours of 2 itemSets
            :rtype :set
        """
        result = []
        if neighbourX is None or neighbourY is None:
            return result
        for i in range(0, len(neighbourX)):
            if neighbourX[i] in neighbourY:
                result.append(neighbourX[i])
        return result

    def getMemoryUSS(self):
        """Total amount of USS memory consumed by the mining process will be retrieved from this function

        :return: returning USS memory consumed by the mining process
        :rtype: float
        """

        return self.memoryUSS

    def getMemoryRSS(self):
        """Total amount of RSS memory consumed by the mining process will be retrieved from this function

        :return: returning RSS memory consumed by the mining process
        :rtype: float
       """
        return self.memoryRSS

    def getRuntime(self):
        """Calculating the total amount of runtime taken by the mining process


        :return: returning total amount of runtime taken by the mining process
        :rtype: float
       """
        return self.endTime - self.startTime

    def construct(self, px, py):
        """
            A function to construct a new Fuzzy itemSet from 2 fuzzy itemSets

            :param px:the itemSet px
            :type px:FFI-List
            :param py:itemSet py
            :type py:FFI-List
            :return :the itemSet of pxy(px and py)
            :rtype :FFI-List
        """
        pxyUL = FFList(py.item)
        for ex in px.elements:
            ey = self.findElementWithTID(py, ex.tid)
            if ey is None:
                continue
            eXY = Element(ex.tid, min([ex.iUtils, ey.iUtils], key=lambda x: float(x)), ey.rUtils)
            pxyUL.addElement(eXY)
        return pxyUL

    def findElementWithTID(self, uList, tid):
        """
            To find element with same tid as given
            :param uList:fuzzyList
            :type uList:FFI-List
            :param tid:transaction id
            :type tid:int
            :return:element tid as given
            :rtype: element if exist or None
        """
        List = uList.elements
        first = 0
        last = len(List) - 1
        while first <= last:
            mid = (first + last) >> 1
            if List[mid].tid < tid:
                first = mid + 1
            elif List[mid].tid > tid:
                last = mid - 1
            else:
                return List[mid]
        return None

    def WriteOut(self, prefix, prefixLen, item, sumIUtil):
        """
            To Store the patten
            :param prefix: prefix of itemSet
            :type prefix: list
            :param prefixLen: length of prefix
            :type prefixLen: int
            :param item: the last item
            :type item: int
            :param sumIUtil: sum of utility of itemSet
            :type sumIUtil: float

        """
        self.itemsCnt += 1
        res = ""
        for i in range(0, prefixLen):
            res += str(prefix[i]) + "." + str(self.mapItemRegions[prefix[i]]) + " "
        res += str(item) + "." + str(self.mapItemRegions.get(item))
        res1 = str(sumIUtil)
        self.finalPatterns[res] = res1

    def getPatternsAsDataFrame(self):
        """Storing final frequent patterns in a dataframe

        :return: returning frequent patterns in a dataframe
        :rtype: pd.DataFrame
        """

        dataFrame = {}
        data = []
        for a, b in self.finalPatterns.items():
            data.append([a, b])
            dataFrame = pd.DataFrame(data, columns=['Patterns', 'Support'])
        return dataFrame

    def getPatterns(self):
        """ Function to send the set of frequent patterns after completion of the mining process

        :return: returning frequent patterns
        :rtype: dict
        """
        return self.finalPatterns

    def savePatterns(self, outFile):
        """Complete set of frequent patterns will be loaded in to a output file

        :param outFile: name of the output file
        :type outFile: file
        """
        self.oFile = outFile
        writer = open(self.oFile, 'w+')
        for x, y in self.finalPatterns.items():
            patternsAndSupport = str(x) + " : " + str(y)
            writer.write("%s \n" % patternsAndSupport)


if __name__ == "__main__":
    ap = str()
    if len(sys.argv) == 5 or len(sys.argv) == 6:
        if len(sys.argv) == 6:
            ap = FFSPMiner(sys.argv[1], sys.argv[3], sys.argv[4], sys.argv[5])
        if len(sys.argv) == 5:
            ap = FFSPMiner(sys.argv[1], sys.argv[3], sys.argv[4])
        ap.startMine()
        fuzzySpatialFrequentPatterns = ap.getPatterns()
        print("Total number of fuzzy frequent Spatial Patterns:", len(fuzzySpatialFrequentPatterns))
        ap.savePatterns(sys.argv[2])
        memUSS = ap.getMemoryUSS()
        print("Total Memory in USS:", memUSS)
        memRSS = ap.getMemoryRSS()
        print("Total Memory in RSS", memRSS)
        run = ap.getRuntime()
        print("Total ExecutionTime in seconds:", run)
    else:
        print("Error! The number of input parameters do not match the total number of parameters provided")
