use mlb;

drop procedure if exists get_full_player;
delimiter //
create procedure get_full_player(
	player_name varChar(100)
)
begin
	select player.*, team.name team from player 
    left join team on player.team = team.team_id
    left join transaction on player.player_id = transaction.player
    where player.name = player_name;
end //
delimiter ; 

call get_full_player('Justin Chen');

drop procedure get_player_transactions;
delimiter //
create procedure get_player_transactions(
	player_id int
)
begin
	select * from transaction where transaction.player = player_id;
end //
delimiter ;
call get_player_transactions(17);

drop procedure if exists initialize_vals;
delimiter //
create procedure initialize_vals(
	player_id int,
    position int
)
begin
	if (select count(*) from hitterstats where hitterstats.player_id = player_id) <> 1 and position = 0
	then insert into hitterstats values (player_id, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0);
    end if;
    if (select count(*) from pitcherstats where pitcherstats.player_id = player_id) <> 1 and position = 1
	then insert into pitcherstats values (player_id, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0);
    end if;
end //
delimiter ;

drop trigger if exists initialize_player_stats;
delimiter //
create trigger initialize_player_stats
after insert on mlb.player
for each row
begin
    call initialize_vals(new.player_id, new.position);
end //
delimiter ;

insert into player (name, position, team, height, weight, school, country)
values ('Justin Chen', 1, 5, 173, 64, 'Northeastern', 'USA');


drop procedure add_player;

delimiter //
create procedure add_player(
    name varChar(100),
    position int,
    team int,
    height int,
    weight int,
    school varChar(100),
    country varChar(50)
)
begin
	insert into mlb.player (name, position, team, height, weight, school, country)
	values (name, position, team, height, weight, school, country);
end //
delimiter ;

call add_player('Justin Chen', 1, 5, 173, 64, 'Northeastern', 'USA');
drop procedure delete_player;
delimiter //
create procedure delete_player(
	p_id int
)
begin
	declare position int;
    select player.position into position from player where player_id = p_id;
    if position = 0 -- hitter
    then begin 
    delete from advancedstats where hitter_id = p_id;
    delete from hitterstats where player_id = p_id;
    end;
    else
	delete from advancedstats where pitcher_id = p_id;
    delete from pitcherstats where player_id = p_id;
    end if;
    delete from player where player_id = p_id;
end //
delimiter ;
use mlb;
call delete_player(36);

drop procedure if exists find_basic_stats;
delimiter // 
create procedure find_pitcher_stats(
	p_id int
)
begin
	select * from mlb.pitcherstats where player_id = p_id;
    
end //
delimiter ; 

delimiter // 
create procedure find_hitter_stats(
	p_id int
)
begin
	select * from mlb.hitterstats where player_id = p_id;
end //
delimiter ; 

delimiter //
create procedure get_stats(
	p_id int,
    position int
)
begin
	if position = 0
    then call find_hitter_stats(p_id);
    else
    call find_pitcher_stats(p_id);
    end if;
end // 
delimiter ;

call get_stats(1, 1);

drop procedure get_matchup;
delimiter //
create procedure get_matchup(
	hitter int,
    pitcher int
)
begin
	select * from advancedstats 
    where hitter_id = hitter and pitcher_id = pitcher;
end //
delimiter ;

delimiter //
create procedure get_player_stats(
	player_id int,
    position int
)
begin
	if position = 0
    then select * from hitterstats where hitterstats.player_id = player_id;
    else
    select * from pitcherstats where pitcherstats.player_id = player_id;
    end if;
end //

delimiter ;

drop procedure get_advanced_stats;
delimiter //
create procedure get_advanced_stats(
	player_id int,
    position int
)
begin
	if position = 0
    then select * from advancedstats where advancedstats.hitter_id = player_id;
    else
    select * from advancedstats where advancedstats.pitcher_id = player_id;
    end if;
end //
delimiter ;

delimiter //
create procedure get_league(
	league_name varchar(50)
)
begin
	select * from league 
    left join team on team.league = league.league_id
    where league.name = league_name;
end //
delimiter ;
call get_league('AL');

delimiter //
create procedure get_team(
	team_name varchar(50)
)
begin
	select * from team 
    left join player on team.team_id = player.team
    where team.name = team_name;
end //
delimiter ;
call get_team('Baltimore Orioles');

delimiter //
create procedure get_team_stats(
	team_id int,
    position int
)
begin
	if position = 0
    then select * from player
    left join hitterstats on player.player_id = hitterstats.player_id
    where player.team = team_id and player.position = 0;
    else
    select * from player
    left join pitcherstats on player.player_id = pitcherstats.player_id
    where player.team = team_id and player.position = 1;
    end if;
    
end //
delimiter ;

delimiter //
create procedure get_team_advanced(
	team_id int,
    position int
)
begin
	if position = 0
    then select * from player
    left join advancedstats on player.player_id = advancedstats.hitter_id
    where player.team = team_id and player.position = 0;
    else
    select * from player
    left join advancedstats on player.player_id = advancedstats.pitcher_id
    where player.team = team_id and player.position = 1;
    end if;
    
end //
delimiter ;