#!/usr/bin/env python3

'''
wip

parses 

'''

# funsies: +/- 1 month in range
import sys, subprocess, os, re, calendar
from datetime import datetime

USAGE="USAGE: python3 "+os.path.basename(__file__)+" [power chart pdf file]"

'''
class AbsoluteDecimal:

    def left():
        raise NotImplementedError

    def right():
        raise NotImplementedError

    def absolute(self):
        return self.absolute
'''

class Age:

    YEARS = re.compile(r'(\d+) (Y|y)ear(s?)')
    MONTHS = re.compile(r'(\d+) (M|m)onth(s?)')
    
    def __init__(self, age_str):
        ym = Age.YEARS.search(age_str)
        self.years = float(ym.group(1)) if ym else 0.0
        mm = Age.MONTHS.search(age_str)
        self.months = float(mm.group(1)) if mm else 0.0
        if self.months > 11.0:
            self.years += self.months // 12
            self.months = self.months % 12
        self.absolute = self.years + (self.months / 12)

    def __repr__(self):
        if self.absolute >= 2.0:
            return str(int(self.years))
        elif self.absolute < 1.0:
            return str(int(self.months)) + "mo"
        elif self.absolute == 1.0:
            return "1"
        else:
            return str(int((self.years * 12) + self.months)) + "mo"

class Duration:

    HOURS = re.compile(r'((\d+) hr)s?')
    MINUTES = re.compile(r'((\d+) min)s?')
    
    def __init__(self, dur_str):
        hm = Duration.HOURS.search(dur_str)
        self.hours = float(hm.group(2)) if hm else 0.0

class Patient:

    def __init__(self, time, clinic, duration, name, age, gender, mrn, fin, dob):
        self.time = time.split(" ")[0] + time.split(" ")[-1].lower()
        self.clinic = clinic
        self.duration = duration
        self.name = name.title().strip()
        self.age = Age(age)
        self.gender = gender.strip().lower()
        self.mrn = int(mrn.replace("-",""))
        self.fin = fin
        self.dob = dob

    def __repr__(self):
        return self.name + " @ " + self.time + " seeing ???\n" + str(self.mrn) +"\nAge " + str(self.age) +"\n"

    def in_age_range(self, l, h):
        return self.age.absolute >= float(l) and self.age.absolute <= float(h)

    def is_age(self, a):
        return self.age.absolute == float(a)

    def is_male(self):
        return self.gender == "male"

    def is_female(self):
        return self.gender == "female"

class UnmatchableFile(Exception):
    pass
    
class PatientMatcher:

    PATIENT = re.compile(r'(\d{1,2}:\d{1,2} [A|P]M) *([^\d]*)((\d+ (mins?|hrs?)( ?)){0,2})\n\n(Patient *\n)?([^\n]*)\n(\d* (Year|Month)s?), (Male|Female)[^\n]*\n(MRN : (\d{3}-\d{2}-\d{2}))? *(FIN : (\d*))? *(DOB : (\d{2}\/\d{2}\/\d{4}))?')

    def __init__(self, str):

        TIME = 0
        CLINIC = 1
        DURATION = 2
        NAME = 7
        AGE = 8
        GENDER = 10
        MRN = 12
        FIN = 14
        DOB = 16

        self.raw_matches = PatientMatcher.PATIENT.findall(str)

        self.patients = []
        for m in self.raw_matches:
            self.patients.append(Patient(m[TIME], m[CLINIC], m[DURATION], m[NAME], m[AGE], m[GENDER], m[MRN], m[FIN], m[DOB]))
            
        self.num_matches = len(self.raw_matches)

class DateMatcher:

    DATE = re.compile(r'(January|February|March|April|May|June|July|August|September|October|November|December) (\d{1,2}), (\d{4})')

    def __init__(self, str):

        MONTH = 1
        DATE = 2
        YEAR = 3

        self.first = DateMatcher.DATE.search(str)

        if not self.first:
            raise UnmatchableFile(DateMatcher.DATE)

        date_str = lambda m: m.group(1) + " " + m.group(2) + " " + m.group(3)
        self.dt = datetime.strptime(date_str(self.first), "%B %d %Y")

        self.formated_date = self.dt.strftime("%m/%d/%Y")

        self.dow = calendar.day_name[self.dt.weekday()]

    def __repr__(self):
        underline = lambda s: "\033[4m" + s + "\033[0m"
        return underline(self.dow + " " + self.formated_date) + "\n"
    

def file_data(fname):
    try:
        with open(fname, "r") as stream:
            data = stream.read()
        assert(stream.closed)
    except IOError as e:
        print("could not read file named " + fname)
        print(USAGE)
        sys.exit(1)
    return data

def pdf_to_text(pdf_fname):
    subprocess.call(["pdftotext", pdf_fname])
    return pdf_fname.replace("pdf", "txt")

def input_file_name(cl_args):
    if len(cl_args) > 2:
        print(USAGE)
        sys.exit(1)
        
    if len(cl_args) > 1:
        return cl_args[1]
    else:
        return input()
    
def main(cl_args):
    pdf_fname = input_file_name(cl_args)
    if ".pdf" not in pdf_fname:
        print(USAGE)
        sys.exit(1)
    txt_fname = pdf_to_text(pdf_fname)

    data = file_data(txt_fname)
    print(DateMatcher(data))
    
    tdm = PatientMatcher(data)
    two_to_three = filter(lambda p: p.in_age_range(2,3), tdm.patients)
    for p in two_to_three:
        print(p)

if __name__ == "__main__":
    main(sys.argv)
