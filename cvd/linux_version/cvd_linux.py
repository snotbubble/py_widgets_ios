import urllib.request
import datetime
import os
from math import sin, cos, sqrt, atan2, radians
import sys

# pythonista widget to show recent covid cases during the 2nd wave...
# written by c.p.brown using sources acknowledged below.
# last updated August 2020

# covid case data sourced from:
# https://data.nsw.gov.au/data/dataset/covid-19-cases-by-location

# postcode location dat sourced from Soon Van 'randomecho' : https://gist.github.com/randomecho/5020859
# ... who took and cribbed from blog.datalicious.com/free-download-all-australian-postcodes-geocod (now a 404 site)
# so this 3rd(or more)-hand data probably contains errors, use at your own risk

# getdist function posted by gwaramadze & fixed by Michael0x2a on stackexchange: https://stackoverflow.com/questions/19412462/getting-distance-between-two-points-based-on-latitude-longitude
# who got it from Andrew Hedges: # https://andrew.hedges.name/experiments/haversine/
# who got it from Bob Chamberlain (site unknown)

# distances rounded to 0.5 km for table grouping

cdr = os.path.split(os.path.realpath('cvd_linux.py'))[0]
rcsv = 'https://data.nsw.gov.au/data/dataset/97ea2424-abaf-4f3e-a9f2-b5c883f42b6a/resource/2776dbb8-f807-4fb2-b1ed-184a6fc2c8aa/download/covid-19-cases-by-notification-date-location-and-likely-source-of-infection.csv'
pcod = cdr + "/nswpostcodes.csv"
mypos = (-33.689990, 150.546212)
ago = 2 # number of prior days to check for cases

cases = []

def getdist(la, lb, oa, ob) :
	# function posted by gwaramadze & fixed by Michael0x2a on stackexchange, referring to Andrew Hedges, who referred to Bob Chamberlain
	# https://andrew.hedges.name/experiments/haversine/
	# https://stackoverflow.com/questions/19412462/getting-distance-between-two-points-based-on-latitude-longitude
	
	# approximate radius of earth in km
	R = 6371.0

	lat1 = lb
	lon1 = ob
	lat2 = la
	lon2 = oa

	dlon = radians(lon2 - lon1)
	dlat = radians(lat2 - lat1)
	
	a = (sin(dlat / 2) * sin(dlat / 2) + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) * sin(dlon / 2))
	c = 2 * atan2(sqrt(a), sqrt(1 - a))

	distance = R * c
	return(distance)

def orgtab(s) :
# function to clean up a non-aligned org table
# intedned for editing orgfile tables in editorial (ios)
	lines = s.split('\n')
	mxl = []
	tbl = ""
# get max column widths
	for i in lines :
		p = i.split('|')
		c = 0
		for s in p :
			if s != "" :
				sl = len(s)
				if len(mxl) <= c :
					mxl.append(sl)
				else :
					if sl > mxl[c] :
						mxl[c] = sl
				c = c + 1
# have the max column widths, now use them to pad cells...
	for i in lines :
		p = i.split('|')
		c = 0
		row = "|"
		if len(i.strip()) == 0 : row = ""
		for s in p :
			if s != "" :
				q = s.ljust(mxl[c]," ")
				if s.strip() != "" :
					if s[0] == "-" :
						q = s.ljust(mxl[c],"-")
				if s[0] == "-" :
					if c < len(p) - 3 :
						row = row + q + "+"
					else :
						row = row + q + "|"
				else :
					row = row + q + "|"
				c = c + 1
		if row.strip() != "" : row = row + "\n"
		tbl = tbl + row
	lines = 0	
	return tbl

def render(s,u,r) :
	if len(cases) > 0 :
		
# write case count
		
		c = str(len(cases)) + " new cases"
		
# sort and group cases using column key (r)
		
		values = set(map(lambda x:x[r], cases))
		if r == 1 :
			values = sorted(values, reverse=True)
		else :
			values = sorted(values)
		cg = [[y for y in cases if y[r]==x] for x in values]
		
# org-style table header
		
		o =     "| DIST | DATE | POST | SUBURB |\n"
		o = o + "|------|------|------|--------|\n"
		
		for g in cg :
			gl = len(g)
			for i in g :
				o = o + "| " + "{0:.2f}".format(i[0]) + "km | " + i[1] + " | " + i[2] + " | " + i[3] + ' |\n'
			o = o + "|------|------|------|--------|\n"
			o = o + "|      |      |      | = " + str(len(g)) + "|\n"
			o = o + "|------|------|------|--------|\n"
		
# tidy-up the table.
# inefficient doing this after the fact, but testing a general-purpose text-editing function for later
		
		o = orgtab(o)
		
# update ui
		
		return[o,c]
		
	else :
		o = ""
		c = "no new cases"
		return[o,c]

def btap() :
	r = int(sys.argv[2])
	ago = int(sys.argv[1])
	
	o = ""
	c = ""
	
# get the covid data from csv 
	
	ug = urllib.request.urlopen(rcsv)
	csv = ug.read().splitlines()[1:]
	ug = 0
	
# extract date info
	
	td = datetime.date.today()
	tx = td.toordinal()
	tw = td.strftime('%a')
	tt = td.day
	
# get postcode locations from csv
	
	f = open(pcod,'r')
	pcsv = f.read().splitlines()
	f.close()
	
	pcc = []
	loc = []
	for p in pcsv :
		seg = p.split(';')
		if not int(seg[0]) in pcc :
			pcc.append(int(seg[0]))
			ploc = (float(seg[2]),float(seg[3]))
			loc.append(ploc)
	
	pcsv = 0
	latest = []
	
# gather and format covid cases, filtered by age in days
	
	for l in csv :
		l = l.decode('utf-8')
		parts = l.split(',')
		if parts[1].strip() != '' :
			dt = parts[0]
			xo = datetime.datetime.strptime(dt,'%Y-%m-%d').date()
			xx = xo.toordinal()
			if tx - xx <= ago :
# match postcode to location data
				try:
					lidx = pcc.index(int(parts[1]))
				except:
					lidx = -1
				if lidx > -1 :
# have a location, get its distance, append to returned data
					itspos = loc[lidx]
					itsdist = getdist(mypos[0],itspos[0],mypos[1],itspos[1])
# compact the date
					tu = datetime.datetime.strftime(xo,'%y%m%d')
					cs = [itsdist,tu,parts[1],parts[6]]
					latest.append(cs)
	cases.clear()
	for j in latest : cases.append(j)
	latest = 0
	csv = 0
	
# if there are any cases, format and output information
	
	if len(cases) > 0 :
		return render(o,c,r)
	else :
		o = ""
		c = "no new cases"
		return[o,c]

thelist = btap()
if len(thelist[0]) == 0 :
	print("\n  No cases recorded since " + str(ago) + " days ago.\n  This may be due to delays in providing data.\n  Data sourced from:\n  https://data.nsw.gov.au/data/dataset/covid-19-cases-by-location")
else:
	print(thelist[1] + "\n\n" + thelist[0])

