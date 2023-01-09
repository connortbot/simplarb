### ARBITRAGE RATER ###
import requests

SPORTS = {
    "all": 'upcoming',
    "NBA": 'basketball_nba',
    "NHL": 'icehockey_nhl',
    "NFL": 'americanfootball_nfl'
}


# NOT ACCESSIBLE TO CANADIANS: BANNED_PLATFORMS = ['Betfair', 'William Hill (US)']

# Ontario, 18yo
BANNED_PLATFORMS = [] # place strings here of the platforms that won't be scanned.

""" INCOMPLETE LIST
NOTE: Platforms have varying age restrictions, depending on country of origin.
on.pointsbet.ca [Canadian] 19+
Unibet on.unibet.ca [Canadian] 19+
SugarHouse on.betrivers.ca [Canadian] 19+
DraftKings sportsbook.draftkings.com [Canadian] 19+
BetMGM on.betmgm.ca [Canadian] 19+
BetRivers on.betrivers.ca [Canadian] 19+

Bodog bodog.eu [EU] [18+]
LowVig.ag www.lowvig.ag [Antiguan+Barbudan] 18+
BetOnline.ag www.betonline.ag [Panaman] 18+
BetUS www.betus.com [Costa Rican/Canadian/International] 18+
GTbets gtbets.ag [Curacao] 18+

MyBookie.ag mybookie.ag [???] 21+

US platforms require 21+, and are only available in the states (many even limited to specific states. Must be accessed with a VPN)
Barstool Sportsbook www.barstoolsportsbook.com [US] 21+
TwinSpires www.twinspires.com [US] 21+
WynnBET www.wynnbet.com [US] 21+
FOX Bet www.foxbet.com [US] 21+
SuperBook superbook.com [US] 21+

Bovada bovada.lv [???] 21+
"""

# An api key is emailed to you when you sign up to a plan
# Get a free API key at https://api.the-odds-api.com/
API_KEY = ''

SPORT = 'upcoming' # use the sport_key from the /sports endpoint below, or use 'upcoming' to see the next 8 games across all sports
#americanbasketball_nba, americanfootball_nfl, icehockey_nhl, 

REGIONS = 'us' # uk | us | eu | au. Multiple can be specified if comma delimited

MARKETS = 'h2h' # h2h | spreads | totals. Multiple can be specified if comma delimited

ODDS_FORMAT = 'decimal' # decimal | american

DATE_FORMAT = 'iso' # iso | unix

stake = input("STAKE: ")
s = input("Filter (all/NBA/NHL/NFL):")
SPORT = SPORTS[s]


def req():
    sports_response = requests.get(
        'https://api.the-odds-api.com/v4/sports', 
        params={
            'api_key': API_KEY
        }
    )
    if sports_response.status_code != 200:
        print(f'Failed to get sports: status_code {sports_response.status_code}, response body {sports_response.text}')

    else:
        print('List of in season sports:', sports_response.json())
    odds_response = requests.get(
        f'https://api.the-odds-api.com/v4/sports/{SPORT}/odds',
        params={
            'api_key': API_KEY,
            'regions': REGIONS,
            'markets': MARKETS,
            'oddsFormat': ODDS_FORMAT,
            'dateFormat': DATE_FORMAT,
        }
    )
    if odds_response.status_code != 200:
        print(f'Failed to get odds: status_code {odds_response.status_code}, response body {odds_response.text}')

    else:
        odds_json = odds_response.json()
        print('Number of events:', len(odds_json))
        print(odds_json)

        # Check the usage quota
        print('Remaining requests', odds_response.headers['x-requests-remaining'])
        print('Used requests', odds_response.headers['x-requests-used'])
        return odds_json

DATA = req()

gamenum = 0
for game in DATA:
    print(" ")
    full = []
    team1 = game["away_team"]
    team2 = game["home_team"]
    bill = game["away_team"]+" @ "+game["home_team"]
    percentages = []
    print("Game "+str(gamenum+1)+": "+bill)
    for book in game["bookmakers"]:
        away_odds = book["markets"][0]["outcomes"][0]["price"]
        home_odds = book["markets"][0]["outcomes"][1]["price"]
        full.append([book["title"],away_odds,home_odds])

    allcombinations = []
    for o in full:
        ix = full.index(o)
        for entry in range(0,len(full)):
            chance = ((1/float(o[1]))+(1/float(full[entry][2])))*100
            percentages.append(chance)
            allcombinations.append([o[0],full[entry][0],chance,float(o[1]),float(full[entry][2])])
    unverified = True
    if len(percentages) == 0:
        best_odd = "null"
        unverified = False
    else:
        i = percentages.index(min(percentages))
        best_odd = allcombinations[i]

    while unverified:
        unverified = False
        for p in BANNED_PLATFORMS:
            if p == best_odd[0] or p == best_odd[1]:
                percentages.remove(min(percentages))
                if len(percentages) == 0:
                    best_odd = "null"
                    break
                else:
                    allcombinations.remove(allcombinations[i])
                    i = percentages.index(min(percentages))
                    best_odd = allcombinations[i]
                    unverified = True
        if best_odd == "null":
            unverified = False
        
            
    
    print("Analysis:")
    if best_odd == "null":
        print("There were no available bets on allowed platforms.")
        continue
    if best_odd[2] > 100:
        print("There is no available arbitrage bet.")
    else:
        print("There is an arbitrage bet for "+str(best_odd[2])+"%")
    print("=> Profit is "+str(float(stake)/(best_odd[2]/100)-float(stake)))
    print("=> Optimal bet for "+team1+" is "+str((float(stake)*(1/float(best_odd[3])))/(best_odd[2]/100))+" @ "+best_odd[0]+"   ["+str(best_odd[3])+"]")
    print("=> Optimal bet for "+team2+" is "+str((float(stake)*(1/float(best_odd[4])))/(best_odd[2]/100))+" @ "+best_odd[1]+"   ["+str(best_odd[4])+"]")

    gamenum += 1

    
        
