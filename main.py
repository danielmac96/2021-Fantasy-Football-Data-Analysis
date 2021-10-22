#Import relevant libraries
import requests
import pandas as pd

league_id =41861601
    #41861601 friends league
    #41716067 work league
season = 2021

url = 'https://fantasy.espn.com/apis/v3/games/ffl/seasons/' + \
      str(season) + '/segments/0/leagues/' + str(league_id) + \
      '?view=mMatchup&view=mMatchupScore'

data = []
print('Week ', end='')
for week in range(1, 7):
    print(week, end=' ')

    r = requests.get(url,
                     params={'scoringPeriodId': week},
                     cookies={"SWID": "{EF24C1E9-FDED-4248-88DA-55C7DBE39ACA}", "espn_s2": "AEBga%2BX7U8W6R8BdN%2FuoHhkz3zIpg9yrf9WIkZLLc2sa80N3tp6zykj9prSq4gpjnl03HOWmtHSQIgg%2FN0Nu7fIfUzcWCZoRaRZJdVLvb9Udx4fMS%2FyPYxu9pzLTu%2BToYcW2l8hqkREagYvmVt19IZh9VXP5GJAln9BhlMMq989ovot%2FZIk7Yf3GenNPbUFPKjHpCW9Q8KoAltTHzQInFrA6K1Jo584a7fvubHAF%2Fewnt8zDphwDcYwGOmqBhPflDRNwZnn2XAvvR7CN74PyiAU0"})
    d = r.json()

    for tm in d['teams']:
        tmid = tm['id']
        for p in tm['roster']['entries']:
            name = p['playerPoolEntry']['player']['fullName']
            slot = p['lineupSlotId']
            # injured status (need try/exc bc of D/ST)
            inj = 'NA'
            try:
                inj = p['playerPoolEntry']['player']['injuryStatus']
            except:
                pass
            # projected/actual points
            proj, act = None, None
            for stat in p['playerPoolEntry']['player']['stats']:
                if stat['scoringPeriodId'] != week:
                    continue
                if stat['statSourceId'] == 0:
                    act = stat['appliedTotal']
                elif stat['statSourceId'] == 1:
                    proj = stat['appliedTotal']

            data.append([
                week, tmid, name, slot, inj, proj, act
            ])
print('\nComplete.')

data = pd.DataFrame(data,
                    columns=['Week', 'Team', 'Player', 'Slot',
                              'Status', 'Proj', 'Actual'])
#data['Slot'].unique()
SlotCodes = [0,2,3,4,6,7,16,17,20,21,23]
SlotNames = ["QB","RB","RB/WR","WR","TE","OP","Def","K","Bench","IR","Flex"]
data['Slot'] = data['Slot'].replace(SlotCodes, SlotNames)
data['Status'] = data['Status'].replace("NA", "ACTIVE")
#data

sch = []
for i in range(0, 42):
    gameid = d['schedule'][i]['id']
    weekid = d['schedule'][i]['matchupPeriodId']
    homeid = d['schedule'][i]['home']['teamId']
    awayid = d['schedule'][i]['away']['teamId']
    homeptsactual = d['schedule'][i]['home']['totalPoints']
    awayptsactual = d['schedule'][i]['away']['totalPoints']
    sch.append([
        gameid,weekid,homeid,awayid,homeptsactual,awayptsactual
    ])
schedule = pd.DataFrame(sch,
                    columns=['gameid', 'weekid', 'homeid', 'awayid',
                              'homeptsactual', 'awayptsactual'])
csv_data = data.to_csv('2021_The_Federation_of_Bros_Position.csv', index = True)
csv_schedule = schedule.to_csv('2021_The_Federation_of_Bros_Schedule.csv', index = True)
print('\nCSV String:\n', csv_data)
print('\nCSV String:\n', csv_schedule)

### NOTES AND JSON EXPLORATION
d['schedule'][0]['id'] #game id
d['schedule'][0]['matchupPeriodId'] #week id
d['schedule'][0]['home']['teamId'] #Home ID of first game of wk 1, games 0-6 are wk 1
d['schedule'][0]['home']['pointsByScoringPeriod']['1'] #Home actual pts wk 1
d['schedule'][0]['winner'] #Winning team
d['schedule'][0]['home']['cumulativeScore']['scoreByStat'] #dictionary of score types
#3 pass yds, 4 pass td, 24 rush yds, 25 rush td, 68 fumbl,53 rec, 43 rec td,123 fumble,



