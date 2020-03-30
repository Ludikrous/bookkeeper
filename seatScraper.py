#!/bin/python3

"""
This script takes in a certain college's page from the UMD course catalog and 
saves all the current registration info to InfluxDB.
"""

import argparse

import requests as r
from bs4 import BeautifulSoup as bs

from influxdb import InfluxDBClient
from datetime import datetime

# ==============================================================================

def process(page):
    # Get all the courses on this page so we can get a link to seat info
    rawCourses = [i.text for i in page.find_all("div", {"class":"course-id"})]
    seatsLink = "https://app.testudo.umd.edu/soc/202008/sections?courseIds=" + '&courseIds='.join(rawCourses)
    
    seatPage = bs(r.get(seatsLink).content, "lxml")
    sections = {}
    
    for course in seatPage.find_all("div", {"class":"course-sections"}):
        courseName = course['id'] + '-'
        
        for section in course.find_all("div", {"class":"section"}):
            sect = section.find("span", {"class":"section-id"}).text.strip()
            sectionName = courseName + sect
            sectionTot = section.find("",{"class":"total-seats-count"}).text.strip()
            sectionOpn = section.find("",{"class":"open-seats-count"}).text.strip()
            
            sections[sectionName] = [
                [courseName[:4], courseName[4:-1], sect, sect[0]],
                sectionOpn,
                str(int(sectionOpn)/int(sectionTot)) if (sectionTot != "0") else "0"]
    
    return sections

    
# ==============================================================================

def customToInflux(sections):
    influxJsons = []
    currTime = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
    
    for sectionName, val in sections.items():
        influxJsons.append({
            "measurement": sectionName,
            "tags": {
                "college": val[0][0],
                "course": val[0][1],
                "section": val[0][2],
                "level": val[0][3]
            },
            "time": currTime,
            "fields": {
                "Int_value": val[1],
                "Float_value": val[2]
            }
        })

    return influxJsons

# ==============================================================================

def main(args):
    # Instantiate a connection to the InfluxDB
    host = 'localhost'
    port = '8086'
    client = InfluxDBClient(host, port, '', '', 'bookkeeper')
    
    # Get raw data from Testudo
    page = bs(r.get(args.pagelink).content, "lxml")
    
    # Process the HTML to get a JSON/dict in the following format:
    # Send all info to InfluxDB
    client.write_points(customToInflux(process(page)))


# ==============================================================================

## RUN LIKE THIS
# onecourse.py https://app.testudo.umd.edu/soc/202008/CMSC

if __name__ == "__main__":
    """ This is executed when run from the command line """
    parser = argparse.ArgumentParser()

    # Optional argument flag which defaults to False
    parser.add_argument("-a", "--auto", action="store_true", default=False, dest="auto")
    
    # Required positional argument
    parser.add_argument("pagelink", help="A link to the page you wish to monitor (like https://app.testudo.umd.edu/soc/202008/CMSC)")
    
    # # Optional argument which requires a parameter (eg. -d test)
    # parser.add_argument("-n", "--name", action="store", dest="name")
    
    args = parser.parse_args()
    main(args)