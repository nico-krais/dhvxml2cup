#!/usr/bin/python
# -*- coding: utf-8 -*-

import argparse
from xml.etree import ElementTree
from typing import Tuple


def print_detail(detail, file, prefix=None):
    """If the given detail is set (is not None), prints the detail and the given prefix (if any) to the
    given file.
    """
    if not detail:
        return
    detail_string = str(detail)
    if prefix:
        detail_string = prefix + detail_string
    file.write(detail_string)
    file.write('\n')


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


def main():
    # define and parse arguments
    parser = argparse.ArgumentParser(description='Convert DHV XML flying site data to SeeYou file format (.cup)')
    parser.add_argument('-d', '--details', help='Create additional .txt file with flying site details', action='store_true')
    parser.add_argument('-o', '--output', help='Name of output file (excluding extension)')
    parser.add_argument('xmlfile', help='XML file containing flying site data')

    args = parser.parse_args()

    # read the xml tree
    tree = ElementTree.parse(args.xmlfile)
    root = tree.getroot()

    # open the output .cup file (already existing files will be overwritten!)
    cup_file = open(args.output + '.cup', 'w', encoding='utf-8')
    if args.details:
        txt_file = open(args.output + '.txt', 'w', encoding='utf-8')
    # iterate over all flying sites in the xml file
    for flying_site in root.iter('FlyingSite'):
        # collect information that are common to all locations at this flying site
        site_remarks = flying_site.find('SiteRemarks').text
        requirements = flying_site.find('Requirements').text
        site_type = flying_site.find('SiteType').text
        max_height = flying_site.find('HeightDifferenceMax').text
        # iterate over all locations at this flying site (might be only one)
        for location in flying_site.findall('Location'):
            # check if this location is suitable for paragliders
            paragliding = location.find('Paragliding').text == 'true'
            if not paragliding:
                continue
            # collect information that are specific to this location
            location_name = location.find('LocationName').text
            location_id = int(location.find('LocationID').text)
            coordinates = location.find('Coordinates').text.split(',')
            altitude = float(location.find('Altitude').text)
            location_remarks = location.find('LocationRemarks').text
            location_country = location.find('LocationCountry').text
            location_type = int(location.find('LocationType').text)  # 1: Take-off, 2: Landing: 3: Towing
            directions = location.find('DirectionsText').text
            towing_length = location.find('TowingLength').text
            towing_height1 = location.find('TowingHeight1').text
            towing_height2 = location.find('TowingHeight2').text
            suitability = location.find('SuitabilityPG').text
            if location.find('GuestRulesApply') is None:
                guest_rule = False
            else:
                guest_rule = location.find('GuestRulesApply').text == 'true'
            if guest_rule:
                guest_rules = location.find('GuestRules').text

            # convert the decimal degree representation of the coordinates to degree decimal minute
            lat_string = lat_dd_to_cup_ddm(float(coordinates[1]))
            lon_string = lon_dd_to_cup_ddm(float(coordinates[0]))
            # prepare the line that will be written to the .cup file for this location and do the writing
            location_string = '"%s","%i",%s,%s,%s,%.1fm,4,,,,"%s"' % (
                location_name, location_id, location_country, lat_string, lon_string, altitude, location_name)
            cup_file.write(location_string)
            cup_file.write('\n')

            # if chosen by the user, write available detailed information of the site to the .txt file
            if args.details:
                title_string = '[%s]' % location_name
                txt_file.write(title_string)
                txt_file.write('\n\n')
                txt_file.write(site_type)
                txt_file.write('\n\n')
                if location_type in [1, 3]:  # towing site or take-off
                    print_detail(directions, txt_file, 'Startrichtung: ')
                if location_type == 3:  # towing site
                    print_detail(towing_length, txt_file, 'Schlepplänge: ')
                    print_detail(towing_height1, txt_file, 'Schlepphöhe: ')
                    print_detail(towing_height2, txt_file, 'Schlepphöhe: ')
                print_detail(altitude, txt_file, 'Höhe: ')
                print_detail(max_height, txt_file, 'Maximale Höhendifferrenz: ')
                print_detail(suitability, txt_file, 'Eignung: ')
                if guest_rule:
                    prefix = 'Gästeregelung beachten!'
                    txt_file.write(prefix)
                    txt_file.write('\n')
                    print_detail(guest_rules, txt_file)
                txt_file.write('\n')
                print_detail(site_remarks, txt_file)
                txt_file.write('\n')
                print_detail(requirements, txt_file)
                txt_file.write('\n')
                print_detail(location_remarks, txt_file)

    cup_file.close()
    if args.details:
        txt_file.close()


if __name__ == "__main__":
    main()
