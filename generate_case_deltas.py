import csv
import urllib2
import time
import json
import gspread
from oauth2client.client import SignedJwtAssertionCredentials

def findConfirmed(row):
    for i, col in enumerate(row):
        if col == '#affected+infected+confirmed':
            return i

    return False


directory = ''
zonesURL = "https://proxy.hxlstandard.org/data.csv?filter01=count&count-tags01=%23adm2%2Bhealth&count-type01-01=count&count-header01-01=Count&count-column01-01=%23meta%2Bcount&filter02=cut&cut-include-tags02=%23adm2%2Bhealth%2Bname&url=https%3A%2F%2Fdocs.google.com%2Fspreadsheets%2Fd%2Fe%2F2PACX-1vSrr9DRaC2fXzPdmOxLW-egSYtxmEp_RKoYGggt-zOKYXSx4RjPsM4EO19H7OJVX1esTtIoFvlKFWcn%2Fpub%3Fgid%3D1564028913%26single%3Dtrue%26output%3Dcsv"

response = urllib2.urlopen(zonesURL)
zonesReader = csv.reader(response)

output = []
column = False
prevValue = 0

for i, zone in enumerate(zonesReader):
    print zone
    if i > 1:
        casesURL = "https://proxy.hxlstandard.org/data.csv?filter01=select&select-query01-01=%23adm2+%3D+"+zone[0]+"&filter02=sort&sort-tags02=%23date&url=https%3A%2F%2Fdocs.google.com%2Fspreadsheets%2Fd%2Fe%2F2PACX-1vSrr9DRaC2fXzPdmOxLW-egSYtxmEp_RKoYGggt-zOKYXSx4RjPsM4EO19H7OJVX1esTtIoFvlKFWcn%2Fpub%3Fgid%3D1564028913%26single%3Dtrue%26output%3Dcsv&force=1"
        response = urllib2.urlopen(casesURL)
        casesReader = csv.reader(response)

        for j, row in enumerate(casesReader):
            print row
            if i==2:
                if j==0:
                    row.append('change in confirmed cases')
                    output.append(row)
                if j==1:
                    row.append('#affected +infected+confirmed+new')
                    column = findConfirmed(row)
                    output.append(row)
                
            if j==2:
                row.append(0)
                prevValue = int(row[column])
                output.append(row)
            if j>2:
                currentValue = row[column]
                if currentValue == '':
                    currentValue = 0
                else:
                    currentValue = int(currentValue)
                delta = currentValue - prevValue
                if delta<0:
                    delta = 0
                prevValue = currentValue
                row.append(delta)
                output.append(row)

outputlength = len(output)
print outputlength

for row in output:
    print row

json_key = json.load(open(directory+'python_scraper-d4dd99f5d776.json'))
scope = ['https://spreadsheets.google.com/feeds']

credentials = SignedJwtAssertionCredentials(json_key['client_email'], json_key['private_key'], scope)

gc = gspread.authorize(credentials)

sh = gc.open("Ebola DRC case tracker")
worksheet = sh.sheet1

print "Writing new content"


x=0
while x*500<outputlength:
    print x
    print 'A'+str(x*500+1)+':R'+str((x+1)*500)
    cell_list = worksheet.range('A'+str(x*500+1)+':R'+str((x+1)*500))
    for i in range(0,500):
        print i
        index = i+1+x*500
        if(i+1+x*500<=outputlength):
            row = output[x*500+i]
            for j,c in enumerate(row):
                cellpos = i*len(row)+j
                cell_list[cellpos].value = c
    worksheet.update_cells(cell_list)
    x=x+1

