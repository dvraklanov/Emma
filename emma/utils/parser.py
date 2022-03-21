import re
from pprint import pprint
from datetime import datetime, timedelta

import requests

from bs4 import BeautifulSoup

from data.config import MC_URL, HEADERS, BASE_URL, FORECAST_RATE
from keyboards.inline import match_cb
import logging

#Получить информацию о матче
def get_match_info(cb : str) -> dict:

    info = {}
    today = datetime.now()

    sport = match_cb.parse(cb)['sport']
    date = match_cb.parse(cb)['date']
    champ_id = match_cb.parse(cb)['champ_id']
    match_num = int(match_cb.parse(cb)['match_num'])
    review_type = match_cb.parse(cb)['review_type']

    url = MC_URL.format(date=date)

    response = requests.get(url=url,
                            headers=HEADERS)
    logging.info(f"url = {url}, response code = {response.status_code}")

    url = BASE_URL + response.json()['matches'][sport]['tournaments'][f'{sport}-{champ_id}']['matches'][match_num]['link']
    response = requests.get(url=url,
                            headers=HEADERS)
    logging.info(f"url = {url}, response code = {response.status_code}")

    main_match_html = BeautifulSoup(response.text, "html.parser")
    status = main_match_html.select_one(".match-info__status").text.strip()
    home_name, away_name = [team.text.strip() for team in main_match_html.select(".match-info__rival a[class = 'match-info__team-link']")]
    main_match_title = f'{home_name} - {away_name}'

    if review_type == '_': info['stat'] = get_stat(html = main_match_html)

    else:

        if review_type in ['h2h', 'fore']:

            h2h_matches = main_match_html.select(".match-history__row")
            h2h_links = []
            h2h_order = ''
            total = {'mut' : 0,
                     'home' : 0,
                     'away' : 0}

            for match in h2h_matches:

                date = datetime.strptime(match.select_one('.match-history__date').text, "%d.%m.%Y")
                link = match.find('a', class_="table-item__count")

                if link:
                    score = list(map(int, re.findall(r'\d+', match.select_one('.match-history__count').text.strip())[:2]))
                    match_title = match.find('a', class_="table-item__count")['title']

                    if not main_match_title in match_title: score = score[::-1]

                    if today - timedelta(days = 365 * 2) <= date:

                        h2h_links.append(link['href'])
                        h2h_order += compare_score(score=score)
                        total['home'] += score[0]
                        total['away'] += score[1]
                        total['mut'] += sum(score)

            if len(h2h_links) > 7: h2h_links = h2h_links[:7]

            total = {t : round(total[t]/len(h2h_links), 2) for t in total.keys() if h2h_links}
            h2h_order = h2h_order[:len(h2h_links)]
            h2h_stat = get_avg_stat(h2h_links)
            h2h_info = {'order' : h2h_order,
                        'total' : total}
            h2h_info.update(h2h_stat)
            info.update({'h2h': h2h_info})

        if review_type in ['last', 'fore']:

            teams_info = get_team_info(match_html = main_match_html)
            info.update({'home' : teams_info['home'],
                         'away' : teams_info['away']})

    return info

#Получить статистику матча
def get_stat(html : BeautifulSoup) -> dict:

    stat = {}
    stat_rows = html.find('div', attrs = {'data-type' : 'stats'}).select(".stat-graph__row")

    for row in stat_rows:

        home = row.select_one(".stat-graph__value._left").text.strip()
        away = row.select_one(".stat-graph__value._right").text.strip()
        title = row.select_one(".stat-graph__title").text

        if not (home == away == '0'):
            stat.update({title: {'home': float(home),
                                 'away': float(away)}})

    return stat

#Получить среднеюю статистику по списку матчей
def get_avg_stat(links : list, team_name : str = '') -> dict:

    avg_stat = {}
    win_point = {'home' : 0,
                 'away' : 0}

    for link in links:

        url = BASE_URL + link
        response = requests.get(url=url,
                                headers=HEADERS)
        logging.info(f"url = {url}, response code = {response.status_code}")

        match_html = BeautifulSoup(response.text, 'html.parser')
        stats = get_stat(match_html)
        cur_home = match_html.select_one(".match-info__team-name").text

        for title, value in stats.items():

            if team_name:
                if cur_home == team_name:
                    if title in avg_stat:avg_stat[title]['home'] += value['home']
                    else: avg_stat.update({title : {'home' : value['home']}})

                else:
                    if title in avg_stat: avg_stat[title]['home'] += value['away']
                    else: avg_stat.update({title : {'home' : value['away']}})

            else:
                if title in avg_stat:

                    avg_stat[title]['home'] += value['home']
                    avg_stat[title]['away'] += value['away']

                else: avg_stat.update({title : {'home' : value['home'],
                                                'away' : value['away']}})

    for stat in avg_stat.keys():

        if team_name:

            avg_stat[stat]['home'] = round(avg_stat[stat]['home'] / len(links), 2)
            if stat in FORECAST_RATE: win_point['home'] += avg_stat[stat]['home'] * FORECAST_RATE[stat]

        else:

            home, away = avg_stat[stat]['home'], avg_stat[stat]['away']
            home = round(home / len(links), 2)
            away = round(away / len(links), 2)
            if stat in FORECAST_RATE:


                if home < away: win_point['home'] += FORECAST_RATE[stat]
                elif away > home: win_point['away'] += FORECAST_RATE[stat]
                #win_point['home'] += home * FORECAST_RATE[stat]
                #win_point['away'] += away * FORECAST_RATE[stat]

            home, away = compare_score([home, away]) + ' ' + str(home), str(away) + ' ' + compare_score([away, home])
            avg_stat[stat]['home'], avg_stat[stat]['away'] = home, away

    return {'avg' : avg_stat,
            'win_point' : win_point}

#Получить информацию по команде
def get_team_info(match_html : BeautifulSoup) -> dict:

    team_info = {'home' : {'avg' : {},
                           'win_point' : {},
                           'order' : '',
                           'total' : {}},
                 'away' : {'avg' : {},
                           'win_point' : {},
                           'order' : '',
                           'total' : {}}}
    team_links = [team['href'] for team in match_html.select(".match-info__rival a[class = 'match-info__team-link']")]

    for link, team in zip(team_links, ['home', 'away']):

        total = {'self': 0,
                 'mut': 0}
        url = BASE_URL + link
        response = requests.get(url=url,
                                headers=HEADERS)
        logging.info(f"url = {url}, response code = {response.status_code}")
        tour_html = BeautifulSoup(response.text, "html.parser")
        team_name = tour_html.select_one(".entity-header__title-name").text.strip().replace('-мол.', '')
        team_page_link = tour_html.select_one(".entity-header__title-link a")
        if team_page_link:

            url = BASE_URL + team_page_link['href']
            response = requests.get(url=url,
                                    headers=HEADERS)
            logging.info(f"url = {url}, response code = {response.status_code}")
            team_html = BeautifulSoup(response.text, "html.parser")

            matches = [match for match in team_html.select('.match-embed a') if match.select_one('.match-info__status').text.strip() == 'Окончен']
            matches_links = []
            matches_order = ''

            for match in matches:

                matches_links.append(match['href'])
                cur_name = match.select_one('.match-info__rival').text.strip().split('\n')[0].replace('-мол.', '')
                score = list(map(int, re.findall(r'\d+', match.select_one('.match-info__score').text.strip())[:2]))
                if cur_name != team_name: score = score[::-1]
                matches_order += compare_score(score = score)
                total['self'] += score[0]
                total['mut'] += sum(score)

            total['self'] = round(total['self'] / len(matches), 1)
            total['mut'] = round(total['mut'] / len(matches), 1)

            stat  = get_avg_stat(matches_links, team_name = team_name)
            team_info[team].update({'avg' :  stat['avg'],
                                    'win_point' : stat['win_point'],
                                    'order' : matches_order,
                                    'total' : total})

    return team_info

#Сравнение счета
def compare_score(score : list) -> str:

    if score[0] > score[1]: smile = '✅'
    elif score[0] == score[1]: smile = '〰'
    else: smile = '❌'

    return smile

if __name__ == "__main__":

    get_match_info(cb='')