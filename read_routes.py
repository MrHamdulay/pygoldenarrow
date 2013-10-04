'''
Script to read bus validRoutes from golden arrow bus services
'''
import pickle
import requests
from bs4 import BeautifulSoup
from bs4.element import Tag
from collections import defaultdict

base_url = 'http://196.41.132.126/timetables_SSNew_T5.asp?formtype=3'

# monday-friday monday-thursday saturday sunday public-holiday
departDays = 'AAAAAZZZ AAAAZZZZ ZZZZZAZZ ZZZZZZAZ ZZZZZZZA'.split()

def load_valid_routes():
  searchPage = requests.get(base_url)
  searchPage = BeautifulSoup(searchPage.text)

  validRoutes = {}
  for optionTag in searchPage.find(id='BusDepart').contents:
    if isinstance(optionTag, Tag):
      departurePlace = optionTag['value'].strip()
      if departurePlace == 'Select':
        continue
      print 'starting from %s' % departurePlace
      arrivals = defaultdict(list)

      # load all the places we can go from here
      arrivalsPage = BeautifulSoup(requests.get(base_url+'&BusDepart='+departurePlace).text)
      arrivalsTag = arrivalsPage.find(id='BusArrive').contents
      arrivalPlaces = [x['value'].strip() for x in arrivalsTag if isinstance(x, Tag) and x['value'] != 'Select']
      for arrivalPlace in arrivalPlaces:
        print 'ending at %s' % arrivalPlace
        for departDay in departDays:
          # check available routes and times

          post_data = {
              'BusDepart': departurePlace,
              'BusArrive': arrivalPlace,
              'DepartDay': departDay,
              'DepartTime': '500',
              'DepartTimeEnd': '2300'
              }

          # this piece of code makes me want to throw up a little
          timesPage = requests.post(base_url, data=post_data).text
          timesPage = BeautifulSoup(timesPage)
          started = False
          times = []
          for column in timesPage.find_all('td'):
            if column.string is None or len(column.string.strip()) == 0:
              continue
            #ugly ugly ugly hack so that we know we've started seeing times'
            if column.string not in 'SELECT YOUR TRAVEL TIMES SEARCH BY START AND END POINTS SELECT YOUR SEARCH CRITERIA':
              started = True
            if started:
              times.append(column.string.strip())

          # interesting trick to convert list into n-tuples
          it = iter(times)
          times = zip(it, it)
          # times = list of 2-tuples (departureDays, time string)
          print times
          arrivals[arrivalPlace].extend(times)
      print arrivals
      validRoutes[departurePlace] = arrivals

  return validRoutes


if __name__ == '__main__':
  routes = {}
  try:
    raise IOError()
    with open('routes.pickle') as routesFile:
      routes = pickle.load(routesFile)
  except IOError:
    print 'Cache miss, loading routes'
    routes = load_valid_routes()
    print routes
    with open('routes.pickle', 'w') as routesFile:
      pickle.dump(routes, routesFile)

