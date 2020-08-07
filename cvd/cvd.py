import urllib.request
import datetime
import os
from math import sin, cos, sqrt, atan2, radians
import appex, ui
import location

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

cdr = os.path.split(os.path.realpath('cvd.py'))[0]
rcsv = 'https://data.nsw.gov.au/data/dataset/97ea2424-abaf-4f3e-a9f2-b5c883f42b6a/resource/2776dbb8-f807-4fb2-b1ed-184a6fc2c8aa/download/covid-19-cases-by-notification-date-location-and-likely-source-of-infection.csv'
pcod = cdr + "/nswpostcodes.csv"
mypos = (-33.689990, 150.546212)
ago = 5 # number of prior days to check for cases

location.start_updates()
loc = location.get_location()
location.stop_updates()
mypos = (loc['latitude'],loc['longitude'])
#print("mypos = " + str(mypos))

cases = []
oldago = 1

def getdist(la, lb, oa, ob) :

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
	distance = round(distance * 2.0) / 2.0
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
		row = ""
		for s in p :
			if s != "" :
				q = s.ljust(mxl[c]," ")
				if s.strip() != "" :
					if s[0] == "-" :
						q = s.ljust(mxl[c],"-")
				row = row + "|" + q
				c = c + 1
		if row.strip() != "" : row = row + "|\n"
		tbl = tbl + row
	lines = 0	
	return tbl

def render(s,u,r) :
	#print("len(cases) = " + str(len(cases)))
	if len(cases) > 0 :
# write case count
		
		c = str(len(cases)) + " new cases"
		
# sort cases 		
		
		#cases.sort(key=lambda x: x[r])
			
		values = set(map(lambda x:x[r], cases))
		values = sorted(values)
		#print("group vals : " + str(values))
		cg = [[y for y in cases if y[r]==x] for x in values]
		#print("grouped list : " + str(newlist))
			
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
		
		s.text = o
		u.text = c
	else :
		s.text = ""
		u.text = "no new cases"


def btap(sender) :
	'@type sender: ui.Button'
	s = sender.superview['thetext']
	u = sender.superview['resultslabel']
	r = sender.superview['sortby'].selected_index
	sago = sender.superview['daysago'].text

	try:
		ago = int(sago)
		oldago = 1
	except:
		ago = 1
		sender.superview['daysago'].text = "1"
		oldago = 1
	#print("days to check : " + str(ago))
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
					#print("appending case : " + str(cs))
				
	cases.clear()
	for j in latest : cases.append(j)
	latest = 0
	csv = 0
	
# if there are any cases, format and output information
	#print("len(cases) in btap is : " + str(len(cases)))
	if len(cases) > 0 :
		render(s,u,r)
	else :
		s.text = ""
		u.text = "no new cases"

def retap(sender) :
	'@type sender: ui.SegmentedControl'
	s = sender.superview['thetext']
	u = sender.superview['resultslabel']
	r = sender.selected_index
	sago = sender.superview['daysago'].text
	try:
		ago = int(sago)
	except:
		ago = 1
		sender.superview['daysago'].text = "1"
	if ago == oldago :
		if len(latest) > 0 :
			render(s,u,r)
		else :
			s.text = ""
			u.text = "no new cases"
	else:
		btap(sender)

# start pythonista UI....

# the main ui container
sv = ui.load_view("cvd.pyui")
scx = ui.get_screen_size().x
if scx > 380 :
	sv.frame = (0,0,400,600)
	sv.present('sheet')
else:
	sv.present('fullscreen')
