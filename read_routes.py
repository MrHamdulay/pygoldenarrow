'''
Script to read bus validRoutes from golden arrow bus services
'''
import pickle
import requests
from bs4 import BeautifulSoup
from bs4.element import Tag

base_url = 'http://196.41.132.126/timetables_SSNew_T5.asp?formtype=3'

# start-end search page

def load_valid_routes():
  searchPage = requests.get(base_url)
  searchPage = BeautifulSoup(searchPage.text)

  validRoutes = {}
  for optionTag in searchPage.find(id='BusDepart').contents:
    if isinstance(optionTag, Tag):
      departurePlace = optionTag['value'].strip()
      if departurePlace == 'Select':
        continue
      print departurePlace
      arrivals = []

      # load all the places we can go from here
      arrivalsPage = BeautifulSoup(requests.get(base_url+'&BusDepart='+departurePlace).text)
      arrivalsTag = arrivalsPage.find(id='BusArrive').contents
      validRoutes[departurePlace] = [x['value'].strip() for x in arrivalsTag if isinstance(x, Tag) and x['value'] != 'Select']

  return validRotues

def load_route_times(validRotues):
  # monday-friday monday-thursday saturday sunday public-holiday
  departDays = 'AAAAAZZZ AAAAZZZZ ZZZZZAZZ ZZZZZZAZ ZZZZZZZA'.split()

  for departurePlace in validRoutes:
    for arrivalPlace in validRoutes[departurePlace]:
      for departDay in departDays:
        # check available routes and times

        post_data = {
            'BusDepart': departurePlace,
            'BusArrive': arrivalPlace,
            'DepartDay': departDay,
            'DepartTime': '500',
            'DepartTimeEnd': '2300'
            }
        timesPage = BeautifulSoup(requests.post(base_url, data=post_data).text)

        timesPage.find_all('table')
        for table in timesPage.find_all('tbody'):
          # if this table has a header row with "days, time and trip rows we've come to the right place"
          if table.children[0].find_all('th'):
            pass

if __name__ == '__main__':
  routes = {}
  try:
    with open('routes.pickle') as routesFile:
      routes = pickle.load(routesFile)
  except IOError:
    print 'Cache miss, loading routes'
    routes = load_valid_routes()
    with open('routes.pickle', 'w') as routesFile:
      pickle.dump(routes, routesFile)

  print routes
