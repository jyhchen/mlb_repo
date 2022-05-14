import pandas as pd

def make_choice(choice_one, choice_two):
    lock = True
    while lock:
        to_get = input(f'Get {choice_one} (0) or get {choice_two} (1): ')

        if to_get in ['0', '1']:
            lock = False
        else:
            print('Incorrect input, try again')
    return to_get


def get_advanced_avg(pitches: pd.DataFrame):
    la = 0
    ev = 0
    count = 0

    for pitch in pitches.iterrows():
        pitch = dict(pitch[1])
        la += pitch.get('launch_angle')
        ev += pitch.get('exit_speed')
        count = count + (1 if int(pitch.get('exit_speed')) != 0 else 0)

    velo_avg = pitches['velocity'].mean()
    la_avg = float(la/count)
    ev_avg = float(ev/count)

    return velo_avg, la_avg, ev_avg

def get_team_pitching(stats: pd.DataFrame):
    innings = 0
    era = 0
    whip = 0
    so = stats['so'].sum()
    bb = stats['bb'].sum()
    for row in stats.iterrows():
        row = dict(row[1])
        innings += row.get('innings')
        era += row.get('era') * innings
        whip += row.get('whip') * innings
    era = round(era/innings, 2)
    whip = round(whip/innings, 2)
    return innings, era, whip, so, bb

def get_team_hitting(stats: pd.DataFrame):
    pa = stats['pa'].sum()
    ba = ((stats['ba'] * stats['pa']).sum())/pa
    obp = ((stats['obp'] * stats['pa']).sum())/pa
    slg = ((stats['slg'] * stats['pa']).sum())/pa
    hr = stats['hr'].sum()
    return round(pa, 2), round(ba, 2), round(obp, 2), round(slg, 2), round(hr)
    
        
def ip_to_dec(ip):
    full = int(ip)
    dec = round(ip-full, 1)
    full += float(f'{dec}/3')
    return full