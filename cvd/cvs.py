import urllib.request
import datetime
import appex, ui

rcsv = 'https://data.nsw.gov.au/data/dataset/97ea2424-abaf-4f3e-a9f2-b5c883f42b6a/resource/2776dbb8-f807-4fb2-b1ed-184a6fc2c8aa/download/covid-19-cases-by-notification-date-location-and-likely-source-of-infection.csv'
sc = 0
def btap(b) :
	ug = urllib.request.urlopen(rcsv)
	csv = ug.read().splitlines()[1:]
	td = datetime.date.today()
	tx = td.toordinal()
	tw = td.strftime('%a')
	tt = td.day
	latest = []
	for l in csv :
		l = l.decode('utf-8')
		parts = l.split(',')
		if parts[1].strip() != '' :
			dt = parts[0]
			xx = datetime.datetime.strptime(dt,'%Y-%m-%d').date().toordinal()
			#print('xx='+str(xx))
			if tx - xx <= 1:
				cs = dt + ' : ' + parts[1] + ' : ' + parts[6]
				latest.append(cs)
	csv = 0
	u.text = "cases : " + str(len(latest))
	for i in latest :
		#print(i)
		s.text = s.text + i + '\n'
	latest = 0

wh = 128
ww = 280	
s = ui.TextView(frame=(0, 0, ww,wh),font=("Menlo",8),alignment=ui.ALIGN_LEFT)
s.background_color = (0.2,0.3,0.4, 1.0)
s.text_color = (0.8,0.9,1.0,1.0)
#appex.set_widget_view(s)
b = ui.Button(font=("Menlo",14),alignment=ui.ALIGN_RIGHT)
b.frame = (ww, 0, wh, wh*0.5)
b.tint_color = (1.0,0.0,0.0,1.0)
b.title = "Refresh"
b.action = btap
u = ui.Label(font=("Menlo",12),alignment=ui.ALIGN_CENTER)
u.frame = (ww,wh*0.5,wh,wh*0.5)
u.background_color = (0.1,0.2,0.3,1.0)
u.text_color = (1.0,0.7,0.7,1.0)
view = ui.View()                                      
view.name = 'cvd'                                    
view.background_color = '#324958'
r = ui.ScrollView(bounces=True)
r.frame = (0,0,ww,wh)
r.add_subview(s)                                
view.add_subview(r)
view.add_subview(b)
view.add_subview(u)                 
appex.set_widget_view(view)
