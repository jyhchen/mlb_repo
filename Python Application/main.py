
import pymysql
from utils import *
import pandas as pd

def get_cnx():
    try:
        cnx = pymysql.connect(
            host='localhost', 
            user='root', 
            password='justin2001',
            db='mlb', 
            charset='utf8mb4', 
            cursorclass=pymysql.cursors.DictCursor
            )
        print('connection success')
    except pymysql.err.OperationalError:
        print('connection error')
    return cnx

def main():
    chosen_view = make_choice('user view', 'admin')
    if chosen_view == '0':
        user_main()
    else:
        admin_main()

def admin_main():
    print('Welcome to player management\n')
    chosen_view = input('(add), (edit), or (delete) a player: ')
    lock = not chosen_view in ['add', 'edit', 'delete']
    if lock:
        print('Unknown input, try again')

    if chosen_view == 'add':
        name = input('Input new player name: ')[0:100]
        lock = True
        while lock:
            position = input('Input new player position (0, hitter; 1, pitcher): ')
            if position not in ['0', '1']:
                print('Unknown input, try again')
            else:
                lock = False
        lock = True
        while lock:
            team = input('Input new player team: ')
            team_cur = cnx.cursor()
            try:
                team_cur.callproc('get_team', (team,))
                teams = team_cur.fetchall()
                team_df = pd.DataFrame(teams)
            except pymysql.Error as e:
                print(e)
            team_cur.close()
            if not team_df.empty:
                lock = False
                team_id = dict(team_df.iloc[0]).get('team_id')
            else:
                print('Team not found, try again')

        is_int = False
        while not is_int:
            height = input('Input new player height: ')
            try:
                height = int(height)
                is_int = True
            except ValueError:
                is_int = False
                print('Not an int, try again')

        is_int = False
        while not is_int:
            weight = input('Input new player weight: ')
            try:
                height = int(height)
                is_int = True
            except ValueError:
                is_int = False
                print('Not an int, try again')
        school = input('Input new player school: ')[0:100]
        country = input('Input new player nationality: ')[0:10]
        try:
            insert_player_cur = cnx.cursor()
            insert_player_cur.callproc('add_player', (name, position, team_id, height, weight, school, country))
            cnx.commit()
            insert_player_cur.close()
            print('Success!')
        except pymysql.Error as e:
            print(e)

    elif chosen_view == 'edit':
        is_int = False
        while not is_int:
            p_id = input('Enter ID of player to edit: ')
            try:
                p_id = int(p_id)
                is_int = True
            except ValueError:
                is_int = False
                is_int('Not an int, try again')
        lock = True
        while lock:
            to_update = input('Choose column to update: ')
            if to_update in ['name', 'position', 'team', 'height', 'weight', 'school', 'country']:
                lock = False
            else:
                print('Not valid column, try again')

        lock = True
        while lock:
            val = input(f'New {to_update} value: ')
            if to_update == 'position':
                if val in ["0", "1"]:
                    lock = False
                else:
                    print('not valid position, try again')
            elif to_update == 'team':
                team_cur = cnx.cursor()
                try:
                    team_cur.callproc('get_team', (val,))
                    teams = team_cur.fetchall()
                except pymysql.error as e:
                    print(e)
                team_df = pd.DataFrame(teams)
                if not team_df.empty:
                    lock = False
                    val = dict(team_df.iloc[0]).get('team_id')
                else:
                    print('Team not found, try again')
            elif to_update in ['height', 'weight']:
                try:
                    val = int(val)
                    lock = True
                except ValueError:
                    lock = False
                    print('Not an int, try again')
            elif to_update == 'country':
                val = "\'" + val[0:10] + "\'"
                lock = False
            else:
                val = "\'" + val[0:100] + "\'"
                lock = False
        try:
            update_cur = cnx.cursor()
            update = f"update player set {to_update}={val} where player_id = {p_id};"
            update_cur.execute(update)
            cnx.commit()
            print('success')
        except pymysql.err as e:
            print(e)
        
    else: #delete
        player_id = input('Input player_id to delete: ')
        try:
            player_id = int(player_id)
            is_int = True
        except ValueError:
            is_int = False
            print('Not an int, try again')
        delete_player_cur = cnx.cursor()
        try:
            delete_player_cur.callproc('delete_player', (player_id,))
            cnx.commit()
        except pymysql.error as e:
            print(e)
        delete_player_cur.close()
        print('Success!')

def user_main():
    lock = True
    while lock:
        chosen_view = input('Choose view (player, team, league): ')
        lock = not chosen_view in ['player', 'team', 'league']
        if lock:
            print('Unknown input, try again')

        if chosen_view == 'player':
            player()
        elif chosen_view == 'team':
            team()
        elif chosen_view == 'league':
            league()
            

def player():
    lock = True

    p_dict = input_get_player()

    to_get = make_choice('biography', 'stats')
    if to_get == '0': # biography
        display_str = f"""
        name: {p_dict.get('name')}\n
        team: {p_dict.get('team.team')}
        height: {p_dict.get('height')}
        weight: {p_dict.get('weight')}
        school: {p_dict.get('school') if p_dict.get('school') is not None else 'N/A'}
        nationality: {p_dict.get('country')}\n"""
        transaction_cur = cnx.cursor()
        try:
            transaction_cur.callproc('get_player_transactions', (p_dict.get('player_id'),))
            transactions = pd.DataFrame(transaction_cur.fetchall())
        except pymysql.Error as e:
            print(e)
        transaction_cur.close()
        if transactions.empty:
            display_str += 'No recent transactions'
        else:
            transaction_str = 'Transactions:\n'
            for row in transactions.iterrows():
                row = dict(row[1])
                transaction_str += f"{row.get('description')}, ({row.get('date')})\n"
            display_str += transaction_str
        print(display_str)

    else:
        to_get = make_choice('individual', 'matchup')
        
        if to_get == '1': # matchup
            matchup_player = input_get_player(text= 'Matchup with who? ')
            pitcher = matchup_player.get('player_id') if p_dict.get('position') == 0 else p_dict.get('player_id')
            hitter = matchup_player.get('player_id') if p_dict.get('position') == 1 else p_dict.get('player_id')
            try:
                matchup_cur = cnx.cursor()
                matchup_cur.callproc('get_matchup', (hitter, pitcher))
                all_pitches = matchup_cur.fetchall()
                pitch_df = pd.DataFrame(all_pitches)
                matchup_dict = dict(pitch_df.iloc[0])
            except pymysql.Error as e:
                print(e)
            matchup_cur.close()
            velo, la, ev = get_advanced_avg(pitch_df)
            if matchup_dict.get('velocity') is None:
                print(f"No matchups found between {p_dict.get('name')} and {matchup_player.get('name')}")
            else:
                print(f"""
                {p_dict.get('name')} vs {matchup_player.get('name')}\n
                avg pitch speed: {velo}\n
                avg exit velo: {ev}\n
                avg launch angle: {la}
                """)
        else: # individual stats
            to_get = make_choice('basic', 'advanced')
            stats_cur = cnx.cursor()
            position = p_dict.get('position')
            if to_get == '0': # basic
                try:
                    stats_cur.callproc('get_player_stats', (p_dict.get('player_id'), position))
                    stats = stats_cur.fetchall()
                    stats_df = pd.DataFrame(stats)
                except pymysql.Error as e:
                    stats_df = pd.DataFrame()
                    print(e)
                if stats_df.empty:
                    print(f"No stats avaliable for {p_dict.get('name')}")
                else:
                    stats_dict = dict(stats_df.iloc[0])
                    display_str = f"{p_dict.get('name')} basic stats:\n"
                    for key in stats_dict:
                        if key != 'player_id':
                            display_str += f'{key}: {stats_dict.get(key)}\n'
                    print(display_str)
            else: # advanced
                try:
                    stats_cur = cnx.cursor()
                    stats_cur.callproc('get_advanced_stats', (p_dict.get('player_id'), position))
                    pitches = stats_cur.fetchall()
                    pitches_df = pd.DataFrame(pitches)
                    velo, la, ev = get_advanced_avg(pitches_df)
                    if position == 0:
                        pitch_text = 'seen'
                        hit_text = ''
                    else:
                        pitch_text = 'thrown'
                        hit_text = 'allowed'
                    print(f"""
                    {p_dict.get('name')} Statcast Advanced Stats
                    avg {pitch_text} pitch speed: {velo}
                    avg {hit_text} exit velo: {ev}
                    avg {hit_text} launch angle: {la}
                    """)
                except pymysql.Error as e:
                    print(e)
            stats_cur.close()

def team():
    lock = True
    while lock:
        team_name = input('Enter team name: ')
        try:
            team_cur = cnx.cursor()
            team_cur.callproc('get_team', (team_name,))
            teams = team_cur.fetchall()
            team_df = pd.DataFrame(teams)
        except pymysql.Error as e:
            print(e)
            team_df = pd.DataFrame()
        if not team_df.empty:
            lock = False
        else:
            print('Team not found, try again')
    team_cur.close()
    team_dict = dict(team_df.iloc[0])
    to_get = make_choice('information', 'stats')
    if to_get == '0': # information
        winning_pct = round(float(team_df['wins'].sum()/(team_df['wins'].sum()+team_df['losses'].sum())), 3)

        info_str = f"""
        {team_dict.get('name')} Information:
        City: {team_dict.get('city')}
        Owner: {team_dict.get('owner')}
        Record: {team_df['wins'].sum()}-{team_df['losses'].sum()} ({winning_pct})\n
        Pitchers: {', '.join(list(team_df.loc[team_df['position'] == 1]['player.name']))}
        Hitters: {', '.join(list(team_df.loc[team_df['position'] == 0]['player.name']))}
        """
        print(info_str)
    else: # stats
        to_get = make_choice('basic', 'advanced')
        display_str = ''
        if to_get == '0': # basic
            pitcher_cur = cnx.cursor()
            try:
                pitcher_cur.callproc('get_team_stats', (team_dict.get('team_id'), 1))
                pitchers = pitcher_cur.fetchall()
                pitcher_cur.close()
                pitchers_df = pd.DataFrame(pitchers)

                innings, era, whip, so, bb = get_team_pitching(pitchers_df)
                display_str = f"""{team_dict.get('name')} Stats
                Pitchers:
                Innings: {innings}
                ERA: {era}
                WHIP: {whip}
                SO: {so}
                bb: {bb}\n
                """
            except pymysql.Error as e:
                print(e)
            try:
                hitter_cur = cnx.cursor()
                hitter_cur.callproc('get_team_stats', (team_dict.get('team_id'), 0))
                hitters = hitter_cur.fetchall()
                hitters_df = pd.DataFrame(hitters)
                hitter_cur.close()
                pa, ba, obp, slg, hr = get_team_hitting(hitters_df)
                display_str += f"""
                Hitters: 
                PA: {pa}
                HR: {hr}
                BA: {ba}
                OBP: {obp}
                SLG: {slg}
                """
            except pymysql.Error as e:
                print(e)

            print(display_str)
            
        else: #advanced
            try:
                pitcher_cur = cnx.cursor()
                pitcher_cur.callproc('get_team_advanced', (team_dict.get('team_id'), 1))
                pitchers = pitcher_cur.fetchall()
                pitcher_cur.close()
                pitchers_df = pd.DataFrame(pitchers)
            except pymysql.Error as e:
                pitchers_df = pd.DataFrame()
                print(e)

            p_velo, p_la, p_ev = get_advanced_avg(pitchers_df)

            try:
                hitter_cur = cnx.cursor()
                hitter_cur.callproc('get_team_advanced', (team_dict.get('team_id'), 0))
                hitters = hitter_cur.fetchall()
                hitters_df = pd.DataFrame(hitters)
                hitter_cur.close()
            except pymysql.Error as e:
                hitters_df = pd.DataFrame()
            h_velo, h_la, h_ev = get_advanced_avg(hitters_df)

            advanced_str = f"""{team_dict.get('name')} Advanced Averages:
            Pitchers:
            avg thrown pitch speed: {p_velo}
            avg allowed exit velo: {p_ev}
            avg allowed launch angle: {p_la}\n
            Hitters:
            avg thrown pitch speed: {h_velo}
            avg allowed exit velo: {h_ev}
            avg allowed launch angle: {h_la}
            """
            print(advanced_str)


def league():
    lock = True
    while lock:
        league_name = input('Enter league name: ')
        try:
            league_cur = cnx.cursor()
            league_cur.callproc('get_league', (league_name,))
            leagues = league_cur.fetchall()
            league_df = pd.DataFrame(leagues)
        except pymysql.Error as e:
            print(e)
        if not league_df.empty:
            lock = False
        else:
            print('League not found, try again')
    league_cur.close()

    league_dict = dict(league_df.iloc[0])
    to_get = make_choice('information', 'standings')
    if to_get == '0': # information
        winning_pct = round(float(league_df['wins'].sum()/(league_df['wins'].sum()+league_df['losses'].sum())), 3)
        league_str = f"""
        {league_name}
        founded: {league_dict.get('founded')}
        teams: {', '.join(list(league_df['team.name']))}
        record: {league_df['wins'].sum()}-{league_df['losses'].sum()} ({winning_pct})
        """
        print(league_str)
    else: # standings
        league_df['winning_pct'] = league_df.apply(
            lambda r: round(float(r.get('wins')/(r.get('wins')+r.get('losses'))), 3), axis=1)
        league_df = league_df.sort_values('winning_pct', ascending=False)
        count = 1
        standing_str = f"{league_name} standings:\n"
        for row in league_df.iterrows():
            row = row[1]
            standing_str += f"{count}) {row.get('team.name')}, {row.get('wins')}-{row.get('losses')} ({row.get('winning_pct')})\n"
            count += 1
        print(standing_str)

def input_get_player(text = 'Enter player name: '):
    lock = True
    while lock:
        name = input(text)
        player_df = get_player(name)
        if not player_df.empty:
            lock = False
        else:
            print('Player not found, try again')

    p_dict = dict(player_df.iloc[0])
    return p_dict

def get_player(name: str):
    try:
        player_cur = cnx.cursor()
        player_cur.callproc('get_full_player', (name,))
        all_players = player_cur.fetchall()
        player_df = pd.DataFrame(all_players)
    except pymysql.Error as e:
        print(e)
    player_cur.close()
    return player_df
            
if __name__ == "__main__":
    cnx = get_cnx()
    go = True
    while go:
        main()
        lock = True
        while lock:
            to_get = input(f'Check other player (0) or end (1)? ')

            if to_get in ['0', '1']:
                lock = False
            else:
                print('Incorrect input, try again')
        go = to_get == '0'

