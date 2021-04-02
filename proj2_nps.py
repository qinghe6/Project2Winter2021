#################################
#####  Name: Qingyuan He   ######
#####   Uniqname: qyhe     ######
#################################

from bs4 import BeautifulSoup
import requests
import json
import secrets  # file that contains your API key
CACHE_FILENAME = "cache.json"
CACHE_DICT = {}


class NationalSite:
    '''a national site
    Instance Attributes
    -------------------
    category: string
        the category of a national site (e.g. 'National Park', '')
        some sites have blank category.

    name: string
        the name of a national site (e.g. 'Isle Royale')
    address: string
        the city and state of a national site (e.g. 'Houghton, MI')
    zipcode: string
        the zip-code of a national site (e.g. '49931', '82190-0168')
    phone: string
        the phone of a national site (e.g. '(616) 319-7906', '307-344-7381')
    '''

    def __init__(self, category, name, address, zipcode, phone):
        self.category = category
        self.name = name
        self.address = address
        self.zipcode = zipcode
        self.phone = phone

    def info(self):
        '''Gives the information of NationalSite

        Parameters
        ----------
        self:
            represents the instance of the class. By using the “self” keyword we can access the attributes
            and methods of the class.

        Returns
        -------
        “<name> (<category>): <address> <zip>”

        '''

        return self.name + " (" + self.category + "): " + self.address + " " + self.zipcode


def open_cache():
    ''' opens the cache file if it exists and loads the JSON into the FIB_CACHE dictionary.
    if the cache file doesn't exist, creates a new cache dictionary
    Parameters
    ----------
    None

    Returns
    -------
    The opened cache
    '''

    try:
        cache_file = open(CACHE_FILENAME, 'r')
        cache_contents = cache_file.read()
        cache_dict = json.loads(cache_contents)
        cache_file.close()
    except:
        cache_dict = {}
    return cache_dict


def save_cache(cache_dict):
    ''' saves the current state of the cache to disk
    Parameters
    ----------
    cache_dict: dict
    The dictionary to save
    Returns
    -------
    None
    '''

    dumped_json_cache = json.dumps(cache_dict)
    fw = open(CACHE_FILENAME, "w")
    fw.write(dumped_json_cache)
    fw.close()


def make_url_request_using_cache(url, cache):
    '''Check the cache for a saved result for this url.
    If the result is found, return it. Otherwise send a new
    request, save it, then return it.
    Parameters
    ----------
    url: string
        The URL for the API endpoint
    cache: dictionary
        The cache dictionary to store the previous url
    Returns
    -------
    string
        the results of the query as a Python object
    '''

    if (url in cache.keys()):
        print("Using Cache")
        return cache[url]
    else:
        print('Fetching')
        response = requests.get(url)
        cache[url] = response.text
        save_cache(cache)
        return cache[url]


def make_request(url):
    '''Make a request to the Web API using the url
    Parameters
    ----------
    baseurl: string
        The URL for the API endpoint
    Returns
    -------
    string
        the results of the query as a Python object loaded from JSON
    '''

    response = requests.get(url)
    return response.json()


def make_request_with_cache(url):
    '''Check the cache for a saved result for this url.
    If the result is found, return it. Otherwise send a new
    request, save it, then return it.
    Parameters
    ----------
    url: string
        The URL for the API endpoint
    Returns
    -------
    string
        the results of the query as a Python object loaded from JSON
    '''

    if url in CACHE_DICT.keys():
        print("Using cache")
        return CACHE_DICT[url]
    else:
        print("Fetching")
        CACHE_DICT[url] = make_request(url)
        save_cache(CACHE_DICT)
        return CACHE_DICT[url]


def build_state_url_dict():
    ''' Make a dictionary that maps state name to state page url from "https://www.nps.gov"
    Parameters
    ----------
    None
    Returns
    -------
    dict
        key is a state name and value is the url
        e.g. {'michigan':'https://www.nps.gov/state/mi/index.htm', ...}
    '''

    dic = {}
    list1 = []
    list2 = []
    url = 'https://www.nps.gov/findapark/index.htm'
    soup = BeautifulSoup(make_url_request_using_cache(url, CACHE_DICT), 'html.parser')
    searching_div = soup.find(id='state')
    id = searching_div.find_all('option')
    for i in searching_div:
        if i != '\n':
            list1.append(i.string)
    for i in range(len(id)):
        list2.append(id[i]['value'])

    list1.pop(0)
    list2.pop(0)
    for i in range(len(list1)):
        dic[list1[i].lower()] = 'https://www.nps.gov/state/' + list2[i] + '/index.htm'

    return dic


def get_site_instance(site_url):
    '''Make an instances from a national site URL.

    Parameters
    ----------
    site_url: string
        The URL for a national site page in nps.gov

    Returns
    -------
    instance
        a national site instance
    '''

    url = site_url
    soup = BeautifulSoup(make_url_request_using_cache(url, CACHE_DICT), 'html.parser')
    searching_div = soup.find(id='HeroBanner')
    name = searching_div.find('a', {'class': 'Hero-title'}).text
    if searching_div.find('span', {'class': 'Hero-designation'}) is None or \
            len(searching_div.find('span', {'class': 'Hero-designation'}).text) == 0:
        category = 'no category'
    else:
        category = searching_div.find('span', {'class': 'Hero-designation'}).text
    searching_div1 = soup.find(id='ParkFooter')
    if searching_div1.find('span', {'itemprop': 'addressLocality'}) is None or \
            searching_div1.find('span', {'itemprop': 'addressRegion'}) is None:
        address = 'no address'
    else:
        address1 = searching_div1.find('span', {'itemprop': 'addressLocality'}).text
        address2 = searching_div1.find('span', {'itemprop': 'addressRegion'}).text
        address = address1 + ', ' + address2
    if searching_div1.find('span', {'itemprop': 'postalCode'}) is None:
        zipcode = 'no zipcode'
    else:
        zipcode = searching_div1.find('span', {'itemprop': 'postalCode'}).text.strip()
    if searching_div1.find('span', {'itemprop': 'telephone'}) is None:
        phone = 'no phone'
    else:
        phone = searching_div1.find('span', {'itemprop': 'telephone'}).text[1:]
    x = NationalSite(category, name, address, zipcode, phone)
    return x


def get_sites_for_state(state_url):
    '''Make a list of national site instances from a state URL.

    Parameters
    ----------
    state_url: string
        The URL for a state page in nps.gov

    Returns
    -------
    list
        a list of national site instances
    '''

    list1 = []
    list2 = []
    url = state_url
    soup = BeautifulSoup(make_url_request_using_cache(url, CACHE_DICT), 'html.parser')
    searching_div = soup.find(id='list_parks')
    item = searching_div.find_all('li', {'class': 'clearfix'})
    for i in range(len(item)):
        list1.append(item[i]['id'][6:])
    for i in list1:
        list2.append(get_site_instance('https://www.nps.gov/' + i + '/index.htm'))
    return list2


def get_nearby_places(site_object):
    '''Obtain API data from MapQuest API.

    Parameters
    ----------
    site_object: object
        an instance of a national site

    Returns
    -------
    dict
        a converted API return from MapQuest API
    '''

    zipcode = site_object.zipcode
    url = 'https://www.mapquestapi.com/search/v2/radius?origin=' + \
          zipcode + '&radius=10&maxMatches=10&ambiguities=ignore&outFormat=json&key=OJNCApu7H1Tdn4oY5uZqTyF6ALhZJi5J'
    res = make_request_with_cache(url)
    with open('data.json', 'w') as fp:
        json.dump(res, fp)
    with open('data.json') as json_file:
        dic = json.load(json_file)
    return dic


if __name__ == "__main__":
    a = 1
    while True:
        if a == 1:
            dic = build_state_url_dict()
            input1 = input('Enter a state name (e.g. Michigan, michigan) or "exit":')
            input2 = input1.lower()
            input3 = input2[0].upper() + input2[1:]
            if input2 == 'exit':
                print("Bye!")
                break
            if input2 in dic:
                list1 = get_sites_for_state(dic[input2])
                print('----------------------------------')
                print('List of national sites in ' + input3)
                print('----------------------------------')
                for i in range(len(list1)):
                    print('[' + str(i + 1) + '] ' + list1[i].info())
                a = 0
            else:
                print("[Error] Enter proper state name")
                a = 1
        else:
            input4 = input('Choose the number for detail search or "exit" or "back":')
            if input4.lower() == 'back':
                a = 1
            elif input4.lower() == 'exit':
                print("Bye!")
                break
            elif not input4.isdigit():
                print("[Error] Invalid input")
                a = 0
            elif input4.isdigit():
                if int(input4) < 1 or int(input4) > len(list1):
                    print("[Error] Invalid input")
                    a = 0
                else:
                    if (list1[int(input4)-1].address == 'no address'):
                        print("[Error] This site does not have an address. Please try another one!")
                        a = 0
                    else:
                        print('----------------------------------')
                        print('Places near ' + list1[int(input4)-1].name)
                        print('----------------------------------')
                        dic = get_nearby_places(list1[int(input4)-1])
                        for i in range(len(dic['searchResults'])):
                            name = dic['searchResults'][i]['name']
                            category = dic['searchResults'][i]['fields']['group_sic_code_name']
                            address = dic['searchResults'][i]['fields']['address']
                            city = dic['searchResults'][i]['fields']['city']
                            if category == '':
                                category = 'no category'
                            if address == '':
                                address = 'no address'
                            if city == '':
                                city = 'no city'
                            print('- ' + name + ' (' + category + '): ' + address + ', ' + city)
                        a = 0

