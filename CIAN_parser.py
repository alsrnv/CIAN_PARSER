# -*- coding: utf-8 -*-


import requests
import re
from bs4 import BeautifulSoup
import pandas as pd
import time
#import LatLon  # dist between two points
from vincenty import vincenty


def html_stripper(text):
    return re.sub('<[^<]+?>', '', str(text))
    

def getPrice(flat_page):
    try:
        price = flat_page.find('div', attrs={'class':'object_descr_price'})
        price = re.split('<div>|руб|\W', str(price))
        price = "".join([i for i in price if i.isdigit()][-3:])
        return int(price)
    except:
        return -99

    
def getCoords(flat_page):
    try:
        coords = flat_page.find('div', attrs={'class':'map_info_button_extend'}).contents[1]
        coords = re.split('&amp|center=|%2C', str(coords))
        coords_list = []
        for item in coords:
            if item[0].isdigit():
                coords_list.append(item)
        lat = float(coords_list[0])
        lon = float(coords_list[1])

        return lat, lon
    except:
        return 55.754093, 37.620407





    
    
def getRoom(flat_page):

    try:
        rooms = flat_page.find('div', attrs={'class':'object_descr_title'})
        rooms = html_stripper(rooms)
        room_number = ''
        for i in re.split('-|\n', rooms):
            if 'комн' in i:
                break
            else:
                room_number += i



        room_number = "".join(room_number.split())
        return room_number
    except:
        return -99


def extract_walk(flat_page):

    try:
         tag =flat_page.find_all('span', attrs={'class':'object_item_metro_comment'})
         if 'тран'.decode('utf-8') in tag[0].text:
             Walk = 0
         else:
              Walk = 1
         return Walk
    except:
        return -99






def extract_minutes(flat_page):
    try:
        MetrDist =flat_page.find_all('span', attrs={'class':'object_item_metro_comment'})
        return int ( MetrDist[0].text.split()[0])
    except:
        return -99








def extract_values(flat_page,type):
    tag = flat_page.find_all('table', attrs={'class':'object_descr_props flat sale'})
    tag_text = tag[0]
    for item in tag_text.find_all('tr'):
        if 'Жилая площадь'.decode('utf-8') in item.text:
            try:
                item_td = item.find('td')
                item_td_separated = item_td.text.split()
                Livesp = item_td_separated[0]
                #Livesp = float(item_td_separated[0].replace(",", "."))
            except:
                Livesp = -99




        if 'Общая площадь'.decode('utf-8') in item.text:
            try:
                item_td = item.find('td')
                item_td_separated = item_td.text.split()
                Totsp= item_td_separated[0]
                # Totsp = float(item_td_separated[0].replace(",", "."))
            except:
                Totsp = -99

        if 'Площадь кухни'.decode('utf-8') in item.text:
            try:
                item_td = item.find('td')
                item_td_separated = item_td.text.split()
                Kitsp = item_td_separated[0]
                # Kitsp = float(item_td_separated[0].replace(",", "."))
            except:
                Kitsp = -99


        if 'Этаж'.decode('utf-8') in item.text:
            try:
                item_td = item.find('td')
                item_td_separated = item_td.text.split('/')
                Floor = int(item_td_separated[0].strip())
                Nfloors = int(item_td_separated[1].strip())
            except:
                Floor = int(item_td.text.strip())
                Nfloors = -99





        if 'Тип дома'.decode('utf-8') in item.text:
                    item_td = item.find('td')
                    if 'новос'.decode('utf-8') in item_td.text:
                        New = 1
                    else:
                        New = 0
        else:
            New =0
        if 'Тип дома'.decode('utf-8') in item.text:
                    item_td = item.find('td')

                    if 'кир'.decode('utf-8') or 'мон'.decode('utf-8') or 'жб'.decode('utf-8') in item_td.text:
                        Brick = 1
                    else:
                        Brick = 0
        else:
            Brick =0
        if 'Телефон'.decode('utf-8') in item.text:
                    item_td = item.find('td')
                    if 'нет'.decode('utf-8') in item_td.text:
                        Tel = 0
                    else:
                        Tel = 1
        else:
            Tel = 0



    if type == 'Tel':
        return Tel
    elif type=='Brick':
        return Brick
    elif type =='New':
        return New
    elif type =='Floor':
        return Floor
    elif type =='Nfloors':
        return Nfloors
    elif type=='Kitsp':
        return Kitsp
    elif type =='Totsp':
        return Totsp
    elif type =='Livesp':
        return Livesp
    else:
        return -99

moscow_center = (55.754093,37.620407) #55.754093, 37.620407


districts ={
    1: # ЦАО
     'http://www.cian.ru/cat.php?deal_type=sale&district%5B0%5D=13&district%5B1%5D=14&district%5B2%5D=15&district%5B3%5D=16&district%5B4%5D=17&district%5B5%5D=18&district%5B6%5D=19&district%5B7%5D=20&district%5B8%5D=21&district%5B9%5D=22&engine_version=2&offer_type=flat&p={}&room1=1&room2=1&room3=1&room4=1&room5=1&room6=1',
    2:  #САО
    'http://www.cian.ru/cat.php?deal_type=sale&district%5B0%5D=5&district%5B10%5D=22&district%5B1%5D=13&district%5B2%5D=14&district%5B3%5D=15&district%5B4%5D=16&district%5B5%5D=17&district%5B6%5D=18&district%5B7%5D=19&district%5B8%5D=20&district%5B9%5D=21&engine_version=2&offer_type=flat&room1=1&room2=1&room3=1&room4=1&room5=1&room6=1',
    3: #СВАО
    'http://www.cian.ru/cat.php?deal_type=sale&district%5B0%5D=6&district%5B10%5D=22&district%5B1%5D=13&district%5B2%5D=14&district%5B3%5D=15&district%5B4%5D=16&district%5B5%5D=17&district%5B6%5D=18&district%5B7%5D=19&district%5B8%5D=20&district%5B9%5D=21&engine_version=2&offer_type=flat&room1=1&room2=1&room3=1&room4=1&room5=1&room6=1',
    4: #ВАО
    'http://www.cian.ru/cat.php?deal_type=sale&district%5B0%5D=7&district%5B10%5D=22&district%5B1%5D=13&district%5B2%5D=14&district%5B3%5D=15&district%5B4%5D=16&district%5B5%5D=17&district%5B6%5D=18&district%5B7%5D=19&district%5B8%5D=20&district%5B9%5D=21&engine_version=2&offer_type=flat&room1=1&room2=1&room3=1&room4=1&room5=1&room6=1',
    5:  #ЮВАО
    'http://www.cian.ru/cat.php?deal_type=sale&district%5B0%5D=8&district%5B10%5D=22&district%5B1%5D=13&district%5B2%5D=14&district%5B3%5D=15&district%5B4%5D=16&district%5B5%5D=17&district%5B6%5D=18&district%5B7%5D=19&district%5B8%5D=20&district%5B9%5D=21&engine_version=2&offer_type=flat&room1=1&room2=1&room3=1&room4=1&room5=1&room6=1',
    6:  #ЮАО
    'http://www.cian.ru/cat.php?deal_type=sale&district%5B0%5D=9&district%5B10%5D=22&district%5B1%5D=13&district%5B2%5D=14&district%5B3%5D=15&district%5B4%5D=16&district%5B5%5D=17&district%5B6%5D=18&district%5B7%5D=19&district%5B8%5D=20&district%5B9%5D=21&engine_version=2&offer_type=flat&room1=1&room2=1&room3=1&room4=1&room5=1&room6=1',
    7: #ЮЗАО
    'http://www.cian.ru/cat.php?deal_type=sale&district%5B0%5D=10&district%5B10%5D=22&district%5B1%5D=13&district%5B2%5D=14&district%5B3%5D=15&district%5B4%5D=16&district%5B5%5D=17&district%5B6%5D=18&district%5B7%5D=19&district%5B8%5D=20&district%5B9%5D=21&engine_version=2&offer_type=flat&room1=1&room2=1&room3=1&room4=1&room5=1&room6=1',
    8:  #ЗАО
    'http://www.cian.ru/cat.php?deal_type=sale&district%5B0%5D=11&district%5B10%5D=22&district%5B1%5D=13&district%5B2%5D=14&district%5B3%5D=15&district%5B4%5D=16&district%5B5%5D=17&district%5B6%5D=18&district%5B7%5D=19&district%5B8%5D=20&district%5B9%5D=21&engine_version=2&offer_type=flat&room1=1&room2=1&room3=1&room4=1&room5=1&room6=1',
    9:  #СЗАО
    'http://www.cian.ru/cat.php?deal_type=sale&district%5B0%5D=1&district%5B10%5D=22&district%5B1%5D=13&district%5B2%5D=14&district%5B3%5D=15&district%5B4%5D=16&district%5B5%5D=17&district%5B6%5D=18&district%5B7%5D=19&district%5B8%5D=20&district%5B9%5D=21&engine_version=2&offer_type=flat&room1=1&room2=1&room3=1&room4=1&room5=1&room6=1',

}
output = pd.DataFrame(columns=['District','Price','lat','lon','rooms','Livesp','Totsp','Nfloors','Floor','New','Brick','Tel','MetrDist','Walk','Dist','rownum'])

rownum=0
for id,district in districts.items():
    page = 1
    links = []
    for page in range(1, 30):
            page_url =  district.format(page)
            search_page = requests.get(page_url)
            search_page = search_page.content
            search_page = BeautifulSoup(search_page, 'lxml')

            flat_urls = search_page.findAll('div', attrs = {'ng-class':"{'serp-item_removed': offer.remove.state, 'serp-item_popup-opened': isPopupOpen}"})
            flat_urls = re.split('http://www.cian.ru/sale/flat/|/" ng-class="', str(flat_urls))
            for link in flat_urls:
                if link.isdigit():
                    links.append(link)




    for page in links:
        flat_url = 'http://www.cian.ru/sale/flat/' + str(page) + '/'

        flat_page = requests.get(flat_url)
        flat_page = flat_page.content
        flat_page = BeautifulSoup(flat_page, 'lxml')
        rownum = rownum+1
        print rownum
        flatStats = {'rownum':rownum}
        flatStats = {'District':id}
        flatStats['Price'] = getPrice(flat_page)
        flatStats['lat'], flatStats['lon'] = getCoords(flat_page)
        flatStats['rooms'] = getRoom(flat_page)
        flatStats['Livesp'] = extract_values(flat_page,'Livesp')
        flatStats['Totsp'] = extract_values(flat_page,'Totsp')
        flatStats['Nfloors'] = extract_values(flat_page,'Nfloors')
        flatStats['Floor'] = extract_values(flat_page,'Floor')
        flatStats['New'] = extract_values(flat_page,'New')
        flatStats['Brick'] = extract_values(flat_page,'Brick')
        flatStats['Tel'] = extract_values(flat_page,'Tel')
        flatStats['MetrDist'] = extract_minutes(flat_page)
        flatStats['Walk'] = extract_walk(flat_page)
        flatStats['Dist'] =  1.60934*vincenty(moscow_center,(flatStats['lat'],flatStats['lon']),miles=True)  #moscow_center.distance(Latlon(Latitude(flatStats['lat']), Longitude(flatStats['lon'])))

        to_append = {'District':flatStats['District'],'Price':flatStats['Price'],'lat':flatStats['lat'],
             'lon':flatStats['lon'],'rooms':flatStats['rooms'],
             'Livesp':flatStats['Livesp'],'Totsp':flatStats['Totsp'],
             'Nfloors':flatStats['Nfloors'],'Floor':flatStats['Floor'],
             'New':flatStats['New'],'Brick':flatStats['Brick'],
             'Tel':flatStats['Tel'],'MetrDist':flatStats['MetrDist'],'Walk':flatStats['Walk']
             ,'Dist':flatStats['Dist'],'rownum':rownum}
        output = output.append(to_append,ignore_index=True)



output.to_csv(r'C:\Users\alexander.saranov\Desktop\DataScience\CIAN\output.csv',encoding='utf-8')






            







