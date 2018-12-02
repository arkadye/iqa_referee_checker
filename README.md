# iqa_referee_checker
This Python script will compare a CSV list of referees, with what qualifications they require, against the IQA database of qualifications, and flags up unqualified referees.

To use it, place volunteers.csv in the same directory as the referee_checker.py and run it.

Requires Python 3.6 or later.

Outputs:
- A fill list of referees checked and volunteers found is printed to the command line, as well as a brief report on who is missing which qualfication.
- qualified_referees.csv: a CSV file listing all volunteers, and their qualifications.
- unqualified_referees_report.txt: a short report listing who isn't qualified, and which qualification they are missing.
