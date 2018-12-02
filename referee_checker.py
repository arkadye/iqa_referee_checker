# Written by Arkady English (suicidalduckling@gmail.com)
#
# Useage:
# Install Python 3.6 (or higher) from here: https://www.python.org/downloads/
# Put this file in the same folder as "volunteers.csv".
# Run it - preferably from the command line, or from IDLE (which is bundled with the Python install.)

# Format of volunteers.csv: Comma separated values.
# No header line.
# One referee per line, split columns with commas.
# 1st column = name (should match name on http://www.iqareferees.org)
# 2nd column = Manually checked (yes/no). Should default to "no", but can be marked as "yes".
#	If "yes", this indicates that this referee was checked manually, and has passed.
#	It is used to eliminate false-positive results, which occasionally happen for some reason.
#	(The error is on the iqareferees.org end not sending ALL the data.)
# 3rd column = Team the referee is with. This can in future be used to automatically check
#	volunteer quotas. For now, it's just so referees can be grouped sensibly in the results.
# 4th, 5th, 6th, etc... list the qualifications the referee is assumed to have, one per column.
# All text is case insensitive - capitalisation doesn't matter!
#
# Example:
# Arkady English,No,Sheffield Squids,head referee,assistant referee, Snitch referee

import json

import urllib.parse
import urllib.request

import time

user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'

header = {'User-Agent' : user_agent}


def getFromURL(url):
    req = urllib.request.Request(url, headers=header)
    try:
        result = urllib.request.urlopen(req)
        the_page = result.read()
        return str(the_page,'utf8')
    except urllib.error.HTTPError as e:
        print(str(e.code) + ' ' + e.reason)
    return

def LogToFile(OutputFile, string):
    print(string)
    OutputFile.write(string + "\n")

class Referee:
    name = ""
    club = "None"
    hr = False
    ar = False
    sr = False
    def short_name(this):
        return this.name + " (" + this.club + ")"
    def to_csv(this):
        result = this.first_name + ',' + this.last_name + ',' + this.club
        if this.hr: result = result + ',' + "head referee"
        if this.ar: result = result + ',' + "assistant referee"
        if this.sr: result = result + ',' + "snitch referee"
        return result
    def qualification_str(this):
        result = ""
        if this.hr:
            result = result + "HR "
        if this.ar:
            result = result + "AR "
        if this.sr:
            result = result + "SR"
        return result.strip()
    def to_str(this):
        return this.short_name() + " " + this.qualification_str()

class Volunteer(Referee):
    manually_checked = False

def fix(string):
    return string.strip().replace('"','').upper()

def order_referee(referee):
    return fix(referee.name).replace(" ","")

def processJsonReferee(referee, all_referees):
    if referee['type'] != 'referee':
        print("Error: not a referee type: " + referee['type'])
        return
    r = Referee()
    r.club = "N/A"
    attributes = referee['attributes']
    first_name = fix(str(attributes['first_name']))
    last_name = fix(str(attributes['last_name']))
    r.name = first_name +" "+ last_name

    certs = referee['relationships']['certifications']
    for certification in certs['data']:
        if certification['type'] != "certification":
            print("Error: not a certification type: " + certification['type'])
            continue
        id = int(certification['id'])
        if id == 3: r.hr = True
        if id == 2: r.ar = True
        if id == 1: r.sr = True

    all_referees.append(r)
    print("Got referee:" + r.to_str())

def getRefereeList(TestData = False):
    all_referees = []
    base_url = "https://iqareferees.org/api/v1/referees?page="
    next_page = 1


    while True:
        next_url = base_url + str(next_page)
        if not TestData:
            file = getFromURL(next_url)
            next_page = next_page + 1
        else:
            test_file = open("referees_json.txt",'r')
            file = test_file.read()
        
        data = json.loads(file)
        arr = data['data']
        if len(arr) == 0:
            break
        for referee in data['data']:
            processJsonReferee(referee, all_referees)

        print("Processed page: " + next_url)
        if TestData:
            break

        #time.sleep(1)
    all_referees.sort(key=order_referee)
    return all_referees

def processCsvVolunteer(line,all_volunteers):
    data = line.split(',')
    r = Volunteer()
    r.name = fix(data[0])
    r.manually_checked = (fix(data[1]) == "YES")
    r.club = fix(data[2])
    if len(r.club) == 0:
        r.club = "Non-playing"
    index = 3
    while index < len(data):
        datum = fix(data[index])
        if datum == "HEAD REFEREE": r.hr = True
        if datum == "ASSISTANT REFEREE": r.ar = True
        if datum == "SNITCH REFEREE": r.sr = True
        index = index + 1
    if r.hr or r.ar or r.sr:
        all_volunteers.append(r)
        print("Got volunteer: " + r.to_str())

def order_volunteer(volunteer):
    return fix(volunteer.club + volunteer.name).replace(" ","")

def getVolunteerList(FileName):
    all_volunteers = []
    has_header = False
    with open(FileName,'r',encoding="utf8") as file:
        for line in file:
            if has_header:
                has_header = False
                continue
            else:
                processCsvVolunteer(line,all_volunteers)
    all_volunteers.sort(key=order_volunteer)
    return all_volunteers

def getQualifiedString(v,r):
    if v and r:
        return "Yes"
    if v and not r:
        return "UNQUALIFIED"
    if not v:
        return "No"

def checkVolunteer(volunteer, referee, outputFile,reportFile,hasRecord):
    hr = volunteer.hr and not referee.hr
    ar = volunteer.ar and not referee.ar
    sr = volunteer.sr and not referee.sr
    if volunteer.manually_checked:
        outputFile.write(volunteer.name + "," + volunteer.club + ",")
        outputFile.write(getQualifiedString(volunteer.hr,True) + ",")
        outputFile.write(getQualifiedString(volunteer.ar,True) + ",")
        outputFile.write(getQualifiedString(volunteer.sr,True) + ",")
        outputFile.write("Checked manually\n")
        return
    if hr or ar or sr:
        if hasRecord:
            LogToFile(reportFile,volunteer.to_str() + ": NOT QUALIFIED:")
        else:
            LogToFile(reportFile,volunteer.to_str() + ": NOT FOUND:")
        if hr:
           LogToFile(reportFile,"\tHR missing.")
        if ar:
            LogToFile(reportFile,"\tAR missing.")
        if sr:
            LogToFile(reportFile,"\tSR missing")
    outputFile.write(volunteer.name + "," + volunteer.club + ",")
    outputFile.write(getQualifiedString(volunteer.hr,referee.hr) + ",")
    outputFile.write(getQualifiedString(volunteer.ar,referee.ar) + ",")
    outputFile.write(getQualifiedString(volunteer.sr,referee.sr) + ",")
    if hasRecord:
        outputFile.write("Yes\n")
    else:
        outputFile.write("NO\n")
    return

def noReferee(volunteer,outputFile,reportFile):
    ref = Referee()
    ref.name = volunteer.name
    ref.club = volunteer.club
    checkVolunteer(volunteer,ref,outputFile,reportFile,False)

def findReferee(referees, volunteer,outputFile,reportFile):
    volunteer_name = order_referee(volunteer)
    if len(referees) == 0:
        noReferee(volunteer,outputFile)
        return
    trial = int(len(referees) / 2)
    ref_name = order_referee(referees[trial])

    if volunteer_name == ref_name:
        checkVolunteer(volunteer,referees[trial],outputFile,reportFile,True)
    elif volunteer_name < ref_name and len(referees) > 1:
        findReferee(referees[:trial],volunteer,outputFile,reportFile)
    elif volunteer_name > ref_name and len(referees) > 1:
        findReferee(referees[trial:],volunteer,outputFile,reportFile)
    else:
        noReferee(volunteer,outputFile,reportFile)
    
volunteers = getVolunteerList("volunteers.csv")

referees = getRefereeList()
outputFile = open("qualified_referees.csv","w+",encoding="utf8")
reportFile = open("unqualified_referee_report.txt","w+",encoding="utf8")
outputFile.write("Name,Club,HR,AR,SR,IQA Database\n")

for volunteer in volunteers:
    findReferee(referees,volunteer,outputFile,reportFile)
    
outputFile.close()
reportFile.close()
