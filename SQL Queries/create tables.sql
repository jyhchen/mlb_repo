drop database if exists mlb;
create database mlb;
use mlb;
set sql_safe_updates = 0;

create table league(
	league_id int primary key auto_increment,
	name varchar(50) not null,
    founded int not null
);

drop table team;
create table team(
	team_id int primary key auto_increment,
    league int not null,
    name varchar(50) not null,
    city varchar(50) not null,
    owner varchar(50) not null,
    wins int not null,
    losses int not null,
    
    constraint team_fk_league
    foreign key (league) references league(league_id)
    on update restrict on delete restrict
);

drop table player;
create table player(
	player_id int primary key,
    name varChar(100) not null,
    position int not null,
    team int not null,
    height int not null,
    weight int not null,
    school varChar(100),
    country varChar(50),
    
    constraint player_fk_team
    foreign key (team) references team(team_id)
    on update restrict on delete restrict
);

drop table transaction;
create table transaction (
	transaction_id int primary key auto_increment,
    player int not null,
    team int not null,
    description varchar(500) not null,
    date date,
    
    constraint transaction_fk_team
    foreign key (team) references team(team_id),
    
    constraint transaction_fk_player
    foreign key (player) references player(player_id)
);

drop table pitcherStats;
create table pitcherStats(
	player_id int primary key,
    games int default 0,
    wins int default 0,
    losses int default 0,
    era float default 0,
    whip float default 0,
    hits int default 0,
    runs int default 0,
    innings float default 0,
    so int default 0,
    bb int default 0,
    
    constraint stat_fk_pitcher
    foreign key (player_id) references player(player_id)
);
drop table hitterStats;
create table hitterStats(
	player_id int primary key,
    games int default 0,
    ba float default 0,
    pa int default 0,
    slg float default 0,
    obp float default 0,
    hits int default 0,
    singles int default 0,
    doubles int default 0,
    triples int default 0,
    hr int default 0,
    so int default 0,
    bb int default 0,
    hbp int default 0,
    
    constraint stat_fk_hitter
    foreign key (player_id) references player(player_id)
);

drop table trade;
create table trade (
	trade_id int primary key auto_increment,
    player int not null,
    team_from int not null,
    team_to int not null,
    description varchar(500) not null,
    date date,
    
    constraint trade_fk_team_from
    foreign key (team_from) references team(team_id),
    constraint trade_fk_team_to
    foreign key (team_to) references team(team_id),
    constraint trade_fk_player
    foreign key (player) references player(player_id)
);

drop table advancedStats;
create table advancedStats(
	pitch_id int primary key auto_increment,
    hitter_id int not null,
    pitcher_id int not null,
    velocity float not null,
    exit_speed float,
    launch_angle float,
    
    constraint advancedStats_fk_hitter
    foreign key (hitter_id) references player(player_id)
    on update restrict on delete restrict,
    constraint advancedStats_fk_pitcher
    foreign key (pitcher_id) references player(player_id)
    on update restrict on delete restrict
);



