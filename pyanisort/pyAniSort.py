#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import utilities
import seriesMatch
import findTitle
import logging
import logging.config
import argparse
import os

logging.config.fileConfig("logging.ini",disable_existing_loggers=False)
logger = logging.getLogger('root')


def main():
    parser = argparse.ArgumentParser(description='Will automatically sort and rename anime files in a folder based off information gathered from anidb.net')
    subparsers = parser.add_subparsers(help='subcommand help', dest='command')
    sortParser = subparsers.add_parser('sort', help='Will sort anime based on anidb info')
    sortParser.add_argument("fromDir", help="The directory with the files you want to sort")
    sortParser.add_argument("toDir", help="The directory where files will go once sorted")
    sortParser.add_argument("-s", "--silent", action="store_true",
                    help="Turn off output to console (will still log to file)")

    undoParser =  subparsers.add_parser('undo', help='undo file sorting based of of a history csv file')
    undoParser.add_argument("startLine", type=int, help="the line of the csv file to start rename undo (enter 0 0 to undo entire file)")
    undoParser.add_argument("endLine", type=int, help="the line of the csv file to end rename undo (enter 0 to only undo the line of startLine)")
    undoParser.add_argument("-f", "--file", help="history csv file containing the original path then the current path")
    args = parser.parse_args()



    if args.command == 'undo':
        logger.info('start moving file back to their original locations')
        try:
            if args.file is None:
                utilities.undoRename(args.startLine, args.endLine)
            else:
                utilities.undoRename(args.startLine, args.endLine, args.file)
        except ValueError:
            logger.error("Could not undo specified line please check history csv file and ensure that line isn't blank")
            exit(1)
        logger.info('files have finished moving back to their original locations')
    elif args.command == 'sort':
        #"/home/jeremy/.gvfs/torrents on jeremy-htpc/complete/"
        #fromDir = "test"
        #toDir = "final"
        fromDir = args.fromDir
        toDir = args.toDir
        silent = args.silent
        cacheDir='cache'

        #TODO add support for command line arguments
        version = 1

        logger.info("Starting to group files")
        try:
            allShows = seriesMatch.groupAnimeFiles(fromDir, silentMode=silent)
        except IOError as e:
            logger.error("Program exited with an error")
            exit(1)
        logger.info("Finished grouping files")

        logger.info("Starting to generate filenames")
        allNewFilenames = findTitle.generateFilenames(version, allShows, toDir, cacheDir)
        logger.info("Finished generating filenames")

        logger.info("Starting to rename files")
        utilities.renameFiles(allNewFilenames, storeHistory=True)
        logger.info("Files have been renamed")
    else:
        exit(1)

if __name__ == '__main__':
    main()
