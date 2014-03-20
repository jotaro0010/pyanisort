#!/usr/bin/env python3
# -*- coding: utf-8 -*-

try:
    import pyanisort.utilities as utilities
except ImportError:
    import utilities
    
import os
import re
import xml.etree.ElementTree as ET
import logging
from time import sleep

logger = logging.getLogger(__name__)
aid=''
version=''

#download series xml file from anidb server
def downloadSeriesXML(xmlFileName, aid, version):
    logger.info("Downloading information for {1}".format(xmlFileName, aid))
    # wait to prevent ban on anidb server
    sleep(3)
    url = 'http://api.anidb.net:9001/httpapi?request=anime&client=pyanisort&'
    url += 'clientver=' + str(version)
    url += '&protover=1&aid=' + str(aid)
    utilities.downloadFile(url, xmlFileName)
    

#parse through series xml file and make a list of all titles
#with corresponding episode number
def parseSeriesXML(seriesXMLFilename):
    # open xml file download it if it doesn't exist
    try:
        xmlFile = utilities.openFile(seriesXMLFilename)
    except IOError as e:
        logger.warning("There is no local information for series: {0}".format(aid))
        downloadSeriesXML(seriesXMLFilename, aid, version)
        xmlFile = utilities.openFile(seriesXMLFilename)
    tree = ET.parse(xmlFile)
    root = tree.getroot()
    episodes = root.find('episodes')

    #if the episodes tag is none check for error
    if episodes is None:
        if root.tag == 'error':
            if utilities.checkFileAge(seriesXMLFilename, 0.20):
                logger.debug("File '{0}' is several hours old re-downloading".format(seriesXMLFilename))
                downloadSeriesXML(seriesXMLFilename, aid, version)
                try:
                    xmlFile = utilities.openFile(seriesXMLFilename)
                except IOError as e:
                    logger.error("IOError[{0}] in file {1}: {2}".format(e.errno, seriesXMLFilename, e.strerror))
                    return
                tree = ET.parse(xmlFile)
                root = tree.getroot()
                episodes = root.find('episodes')
                if episodes is None:
                    if root.tag == 'error':
                        logger.error("Error parsing through {0}: {1}".format(seriesXMLFilename, root.text))
                        return
                    else:
                        logger.error('unknown error occured parsing {0}'.format(seriesXMLFilename))
                        return
            else:
                logger.error("Error parsing through {0}: {1}".format(seriesXMLFilename, root.text))
                return
        else:
            logger.error('unknown error occured parsing {0}'.format(seriesXMLFilename))
            return

    allEpInfo = []
    for episode in episodes.iterfind('episode'):
        epInfo=[]
        episodeNo = episode.find('epno')
        if (episodeNo.get('type') == '1'):
            title = episodeNo.text
            title = int(title)
            epInfo.append('{0:0=2d}'.format(title))
            for title in episode.findall('title'):
                langAttrib = '{http://www.w3.org/XML/1998/namespace}lang'
                if title.get(langAttrib) == 'en':
                    t = title.text
                    # replace any |/\ with a comma
                    t = re.sub('\s?[\\/|]', ',', t)
                    epInfo.append(t)
                    allEpInfo.append(epInfo)
    return allEpInfo

#generate list of new file names for anime in the form 'series - 00 - title'
#return a list of file names and new names to be renamed later.
#TODO create a way to customize new name formating
def generateFilenamesSeries(xmlFilename, outDir,
                            seriesName, filenames, titleList):
        # sort descending for faster matching later
        filenames = sorted(filenames, reverse=True)
        titleList = sorted(titleList, reverse=True)

        # if the highest file episode is > the highest episode from the xmlFile
        if (filenames[0][0] > titleList[0][0]):
            if utilities.checkFileAge(xmlFilename, 0.5):
                downloadSeriesXML(xmlFilename, aid, version)
                logger.info("Downloading newer file '{0}' for show {1}".format(xmlFilename, seriesName))
                try:
                    xmlFile = utilities.openFile(xmlFilename)
                except IOError as e:
                    logger.error("IOError[{0}] in file {1}: {2}".format(e.errno, filename, e.strerror))
                titleList = parseSeriesXML(xmlFilename)
                titleList = sorted(titleList, reverse=True)
            else:
                logger.error('{0} xml file is up to date'.format(seriesName))

        #start generating new names
        newNames = []
        for fileEp, file in filenames:
            filename, ext = os.path.splitext(file)
            path, filename = os.path.split(file)

            # checks if file is and ending or opening
            if fileEp[0] == 'E' or fileEp[0] == 'e':
                    m = re.search('\d{1,2}',fileEp)
                    try:
                        ep = m.group(0)
                        ep = '{0:0=2d}'.format(int(ep))
                    except AttributeError:
                        ep = '01'
                    newFilename = '{0} - ED{1}{2}'.format(
                        seriesName, ep, ext)
                    newFilename = os.path.join(outDir, seriesName, newFilename)
                    newNames.append([file, newFilename])
                    continue
            elif fileEp[0] == 'O' or fileEp[0] == 'o':
                m = re.search('\d{1,2}',fileEp)
                try:
                    ep = m.group(0)
                    ep = '{0:0=2d}'.format(int(ep))
                except AttributeError:
                    ep = '01'
                newFilename = '{0} - OP{1}{2}'.format(
                    seriesName, ep, ext)
                newFilename = os.path.join(outDir, seriesName, newFilename)
                newNames.append([file, newFilename])
                continue
            
            # If it isn't then it is an episode
            for ep, title in titleList:
                if fileEp == ep:
                    newFilename = '{0} - {1} - {2}{3}'.format(
                        seriesName, ep, title, ext)
                    newFilename = os.path.join(outDir, seriesName, newFilename)
                    newNames.append([file, newFilename])
                    break
                elif (fileEp > ep):
                    title = 'Episode {0}'.format(fileEp)
                    newFilename = '{0} - {1} - {2}{3}'.format(
                        seriesName, fileEp, title, ext)
                    newFilename = os.path.join(outDir, seriesName, newFilename)
                    newNames.append([file, newFilename])
        return newNames

#generate a list of new names for all files based off database info
def generateFilenames(ver, allShows, outDir, cacheDir):
    global version
    global aid
    version = ver

    outDir = os.path.abspath(outDir)
    allNewFilenames = []
    for series in allShows:
        aid = series[0]
        seriesName = series[1]
        filenames = series[2:]
        xmlFilename = os.path.join(cacheDir, '{0}.xml.gz'.format(aid))

        logger.debug("Now processing information for show {0}, {1}".format(aid, seriesName))

        #get list of episodes and titles
        titleList = parseSeriesXML(xmlFilename)
        if titleList is None:
            logger.error('an error has occured while processing information for series {0}'.format(seriesName))
            continue

        #use all previous info ro generate list of new names
        newFilenames = generateFilenamesSeries(xmlFilename, outDir, seriesName,
                                               filenames, titleList)
        # validate file names
        if len(newFilenames) != 0:
            for name in newFilenames:
                name[1] = utilities.validateFilename(name[1])
                allNewFilenames.append(name)

    return allNewFilenames


