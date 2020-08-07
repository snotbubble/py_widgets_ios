# cvd.py
> pythonista widget to show recent covid cases during the 2nd wave...
> written by c.p.brown using sources acknowledged below.
> last updated August 2020

> covid case data sourced from:
> https://data.nsw.gov.au/data/dataset/covid-19-cases-by-location

> postcode location dat sourced from Soon Van 'randomecho' : https://gist.github.com/randomecho/5020859
> ... who took and cribbed from blog.datalicious.com/free-download-all-australian-postcodes-geocod (now a 404 site)
> so this 3rd(or more)-hand data probably contains errors, use at your own risk

> getdist function posted by gwaramadze & fixed by Michael0x2a on stackexchange: https://stackoverflow.com/questions/19412462/getting-distance-between-two-points-based-on-latitude-longitude
> who got it from Andrew Hedges: # https://andrew.hedges.name/experiments/haversine/
> who got it from Bob Chamberlain (site unknown)

> distances rounded to 0.5 km for table grouping


# usage
- import both cvd.py and cvd.pyui into pythonista
- import nswpostcodes.csv into pythonista
- run cvd.py

# screenie
![](/cvd/cvd_screenie.jpg?raw=true)
