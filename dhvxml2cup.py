#!/usr/bin/python
# -*- coding: utf-8 -*-

import argparse
import xml.etree.ElementTree as ET
from typing import Tuple


def printDetail(detail, file, prefix=None):
    """Checks if a specified detail is set. If it is, converts the detail to the correct encoding and prints it to file.
    Optionally specify a prefix for the detail.
    """
    detailString = '%s' % detail
    if detailString != 'None':
        if detailString != '':
            if prefix:
                prefixString = prefix
                detailString = prefixString + detailString
            file.write(detailString)
            file.write('\n')
            return


def dd_to_ddm(dd: float) -> Tuple[int, float]:
    """Convert a coordinate representation from decimal degrees to degrees and decimal minutes.
    """
    degrees = int(dd)
    decimal_minutes = 60. * (abs(dd) - abs(degrees))
    return degrees, decimal_minutes


def lat_dd_to_cup_ddm(lat: float) -> str:
    """Take a latitude value, given in decimal degrees (e.g. -77.35875) and convert it in the appropriate cup
    format, which is in degree decimal minutes. For the given example, the result would be "7720.153S".
    Format specification: Two characters degrees, then the decimal minutes value with two characters before the
    decimal separator and three afterwards. Then either S or N.
    """
    degrees, decimal_minutes = dd_to_ddm(lat)
    if degrees > 0:
        hemisphere = "N"
    else:
        hemisphere = "S"
    return '%02i%06.3f%s' % (abs(degrees), decimal_minutes, hemisphere)


def lon_dd_to_cup_ddm(lat: float) -> str:
    """Take a longitude value, given in decimal degrees (e.g. -77.35875) and convert it in the appropriate cup
    format, which is in degree decimal minutes. For the given example, the result would be "07720.153W".
    Format specification: Three characters degrees, then the decimal minutes value with two characters before the
    decimal separator and three afterwards. Then either E or W.
    """
    degrees, decimal_minutes = dd_to_ddm(lat)
    if degrees > 0:
        hemisphere = "E"
    else:
        hemisphere = "W"
    return '%03i%06.3f%s' % (abs(degrees), decimal_minutes, hemisphere)


if __name__ == "__main__":
    # define and parse arguments
    parser = argparse.ArgumentParser(description='Convert DHV XML flying site data to SeeYou file format (.cup)')
    parser.add_argument('-d', '--details', help='Create additional .txt file with flying site details', action='store_true')
    parser.add_argument('-o', '--output', help='Name of output file (excluding extension)')
    parser.add_argument('xmlfile', help='XML file containing flying site data')

    args = parser.parse_args()

    # read the xml tree
    tree = ET.parse(args.xmlfile)
    root = tree.getroot()
    # open the output .cup file (already existing files will be overwritten!)
    cupFile = open(args.output + '.cup', 'w', encoding='utf-8')
    if args.details:
        txtFile = open(args.output + '.txt', 'w', encoding='utf-8')
    # iterate over all flying sites in the xml file
    for flyingSite in root.iter('FlyingSite'):
        # collect information that are common to all locations at this flying site
        siteRemarks = flyingSite.find('SiteRemarks').text
        requirements = flyingSite.find('Requirements').text
        siteType = flyingSite.find('SiteType').text
        maxHeight = flyingSite.find('HeightDifferenceMax').text
        # iterate over all locations at this flying site (might be only one)
        for location in flyingSite.findall('Location'):
            # check if this location is suitable for paragliders
            paragliding = location.find('Paragliding').text == 'true'
            if not paragliding:
                continue
            # collect information that are specific to this location
            locationName = location.find('LocationName').text
            locationID = int(location.find('LocationID').text)
            coordinates = location.find('Coordinates').text.split(',')
            altitude = float(location.find('Altitude').text)
            locationRemarks = location.find('LocationRemarks').text
            locationCountry = location.find('LocationCountry').text
            locationType = int(location.find('LocationType').text)  # 1: Starting point, 2: Landing point: 3: Towing point
            directions = location.find('DirectionsText').text
            towingLength = location.find('TowingLength').text
            towingHeight1 = location.find('TowingHeight1').text
            towingHeight2 = location.find('TowingHeight2').text
            suitability = location.find('SuitabilityPG').text
            if location.find('GuestRulesApply') is None:
                guestRule = False
            else:
                guestRule = location.find('GuestRulesApply').text == 'true'
            if guestRule:
                guestRules = location.find('GuestRules').text

            # convert the decimal degree representation of the coordinates to degree decimal minute
            latString = lat_dd_to_cup_ddm(float(coordinates[1]))
            lonString = lon_dd_to_cup_ddm(float(coordinates[0]))
            # prepare the line that will be written to the .cup file for this location and do the writing
            locationString = '"%s","%i",%s,%s,%s,%.1fm,4,,,,"%s"' % (
                locationName, locationID, locationCountry, latString, lonString, altitude, locationName)
            cupFile.write(locationString)  # encoding necessary to deal with mutated vowels
            cupFile.write('\n')

            # if chosen by the user, write available detailed information of the site to the .txt file
            if args.details:
                titleString = '[%s]' % locationName
                txtFile.write(titleString)
                txtFile.write('\n\n')
                txtFile.write(siteType)
                txtFile.write('\n\n')
                if locationType in [1, 3]:  # towing site or take-off
                    printDetail(directions, txtFile, 'Startrichtung: ')
                if locationType == 3:  # towing site
                    printDetail(towingLength, txtFile, 'Schlepplänge: ')
                    printDetail(towingHeight1, txtFile, 'Schlepphöhe: ')
                    printDetail(towingHeight2, txtFile, 'Schlepphöhe: ')
                printDetail(altitude, txtFile, 'Höhe: ')
                printDetail(maxHeight, txtFile, 'Maximale Höhendifferrenz: ')
                printDetail(suitability, txtFile, 'Eignung: ')
                if guestRule:
                    prefix = 'Gästeregelung beachten!'
                    txtFile.write(prefix)
                    txtFile.write('\n')
                    printDetail(guestRules, txtFile)
                txtFile.write('\n')
                printDetail(siteRemarks, txtFile)
                txtFile.write('\n')
                printDetail(requirements, txtFile)
                txtFile.write('\n')
                printDetail(locationRemarks, txtFile)

    cupFile.close()
    if args.details:
        txtFile.close()
