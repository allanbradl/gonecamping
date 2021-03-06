#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Feb  8 10:28:24 2019
Data cleaning for public campsites:
1. add activities and facilities as columns
2. map activities and facilities to private campsites' corresponding ones
3. drop uncessary columns
4. add latitude and longitude
5. output final data to public_campsites_ready.csv

@author: hongxiu
"""
import numpy as np
import pandas as pd
import re
import os

def break_af_str(text):
    result = set()
    if(type(text) == float):
        return result
    arr = text.split(',')
    arr = [i for i in arr if not i.startswith('Campsites (total)')]
    for i in arr:
        result.add(re.sub('\(\d+\)', '', i))
    return result

pb = pd.read_csv("./data/public_campsites.csv", encoding='utf-8') 
#add everything in activities and facilities
pb_af_total = set()
for index, row in pb.iterrows():
    pb_af_total = pb_af_total.union(break_af_str(row['facilities_icon']))
    pb_af_total = pb_af_total.union(break_af_str(row['activities_icon']))
#add the column and set default value to 0
for t in pb_af_total:
    pb[t] = 0

pb['Birding'] = 0
#add values to the columns    
for index, row in pb.iterrows():
    af = break_af_str(row['facilities_icon']).union(break_af_str(row['activities_icon']))
    birding = False
    if(type(row['activities']) is not float):
        birding = row['activities'].find('Birding') > -1
    for feature in af:
        if(feature=='Birding'):
            pb.at[index, feature] = birding
        else:
            pb.at[index, feature] = 1
#rename the columns to make sure public campsites and private campsites have the same columns   
renames = {
    'Campsites (Electrical)':'Electrical',
    'Campsites (Seasonal Campsite Rental)':'Seasonal Sites',
    'All Terrain Wheelchairs':'Accessible facilities',
    'Campsites (Dog Free)':'Pet-friendly',
    'Visitor Centres':'Store',
    'Pools':'Swimming (indoor pool)',
    'Horseback Riding':'horseback riding',
    'Fishing': 'fishing',
    'Whitewater Paddling': 'whitewater rafting',
    'Golf':'golf',
    'Hunting': 'hunting',
    'Rock Climbing':'rock climbing/bouldering',
    'Swimming': 'Swimming (lake, river, or beach)',
    'Boating – Motorboat Restrictions': 'motorboats allowed',
    'Snowmobiling':'snowmobiling',
    'Showers':'Toilets/showers (comfort station)',
    'Campsites (Dog Free)': 'Pet-friendly',
    'introduction':'overview'
}
pb = pb.rename(columns = renames)

#public campites use "Dog Free" while private campsites use "Pet Friendly"
pb['Pet-friendly'] = 1 - pb['Pet-friendly']

#non-motorized boat
nm_boating =['Rentals - Canoe', 'Rentals - Kayak', 'Rentals - Paddleboat', 'Rentals - Stand Up Paddleboard']
pb['boat rental (non-motorized)'] = pb['Rentals - Canoe'] | pb['Rentals - Kayak'] | pb['Rentals - Paddleboat'] | pb['Rentals - Stand Up Paddleboard'] 
pb.drop(columns=nm_boating, inplace=True)

#motorboat restriction
pb['motorboats allowed'] = 1 - pb['Boating - Motorboat Restrictions']

#hiking
hiking = ['Hiking', 'Hiking - Overnight Trails']
pb['walking/hiking trails'] = pb['Hiking'] | pb['Hiking - Overnight Trails']
pb.drop(columns=hiking, inplace=True)

#biking
biking = ['Biking', 'Biking - (Mountain Bike)']
pb['cycling'] = pb['Biking'] | pb['Biking - (Mountain Bike)']
pb.drop(columns=biking, inplace=True)

#birding
pb['wildlife viewing/birding'] = pb['Birding'] | pb['Birding - Festivals']
pb.drop(columns=['Birding', 'Birding - Festivals'], inplace=True)

pb.set_index('name', inplace=True)

pb['review'] = ''
#public reviews
files = os.listdir('./reviews')
for f in files:
    print('process %s' % (f))
    temp = pd.read_csv('./reviews/'+f, encoding='utf-8')
    temp.dropna(inplace=True)
    r = ' '.join(temp['review'].tolist())
    pb.at[f.replace('.csv', ''), 'review'] = r

pb['ov_rv'] = pb['overview'] + pb['review']
#drop unnecessary columns
columns_to_drop = ['camping', 'activities', 'facilities', 'camping_raw',
       'activities_raw', 'facilities_raw','activities_icon', 'facilities_icon']
pb.drop(columns=columns_to_drop, inplace=True)

#latitude and longitude
temp = pd.read_csv('./data/public_campsites_latlng.csv', encoding='utf-8')
temp.set_index('name', inplace=True)
temp = temp[['latitude','longitude']]

pb = pd.merge(pb,temp, left_index=True, right_index=True)
pb.to_csv('./data/public_campsites_ready.csv', encoding='utf-8', header=True, index=True)