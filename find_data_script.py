import pandas as pd
import numpy as np

story = pd.read_csv('C:/Users/Leo/Desktop/Story Rewards List.csv')
gallery = pd.read_csv('C:/Users/Leo/Desktop/Galley List.csv')
gallery.replace(np.nan, '', inplace=True)

def get_quests(item):
    result = []
    for rows in range(0, len(story)):
        if item in story['Rewards'][rows]:
            locations = {
                'item': item,
                'location': story['Quest'][rows]
            }
            result.append(locations)
    return result

where = []
for row in range(0, len(gallery)):
    quests = pd.DataFrame(get_quests(gallery['Item'][row]))
    for location in quests['location']:
        if location not in gallery['Location'][row]:
            missing = {
                'item': gallery['Item'][row],
                'where': location
            }
            where.append(missing)

pd.DataFrame(where).to_csv('./missing.csv')