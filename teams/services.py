from datetime import timedelta, datetime
import re

from django.conf import settings
from django.db.models import Q, Prefetch

from nba_api.stats.endpoints.franchisehistory import FranchiseHistory
from nba_api.stats.endpoints.leaguestandingsv3 import LeagueStandingsV3
from nba_api.stats.endpoints.playercareerstats import PlayerCareerStats
from nba_api.stats.endpoints.playerindex import PlayerIndex
from nba_api.stats.endpoints.scoreboardv2 import ScoreboardV2
from nba_api.stats.endpoints.playergamelogs import PlayerGameLogs
import pytz

from games.models import Game, LineScore
from games.serializers import GameSerializer, LineScoreSerializer, PlayerCareerStatisticsSerializer
from players.models import Player, PlayerCareerStatistics, PlayerStatistics
from teams.models import Team, TeamName
from teams.utils import calculate_time, create_empty_player_season_stats


def get_all_teams_season_stats(year):
    ## Use Regex to get the year from the season
    year = re.search(r'^\d\d\d\d-\d\d', year)
    if not year:
        raise ValueError('Invalid year format. Use YYYY-YY format')
    
    ## Get the ranking from nba_api
    standings = LeagueStandingsV3(
        league_id='00',
        season=year.group(),
        season_type='Regular Season'
    ).get_dict()['resultSets'][0]

    headers = standings['headers']
    standings = standings['rowSet']

    ## Get the team ranking
    ranking = {
        'East': [],
        'West': []
    }

    # Separate the teams by conference
    all_teams = Team.objects.all().only('symbol')

    for team in standings:
        conference = team[6]
        if conference == 'East':
            ranking['East'].append(dict(zip(headers, team)))
        else:
            ranking['West'].append(dict(zip(headers, team)))

        ranking[conference][-1]['TeamAbbreviation'] = all_teams.get(id=ranking[conference][-1]['TeamID']).symbol

    return ranking

def get_all_games_for_team_this_season(team_id):
    team = None
    try:
        team = Team.objects.get(id=team_id)
    except Team.DoesNotExist:
        raise ValueError('Invalid team_id')

    all_team_names = TeamName.objects.select_related('language').all()
    
    games = Game.objects.select_related(
        'home_team', 'visitor_team'
    ).prefetch_related(
        Prefetch(
            'line_scores',
            queryset=LineScore.objects.select_related('team').prefetch_related(
                Prefetch(
                    'team__teamname_set',
                    queryset=all_team_names
                )
            )
        ),
        Prefetch(
            'home_team__teamname_set',
            queryset=all_team_names
        ),
        Prefetch(
            'visitor_team__teamname_set',
            queryset=all_team_names
        )
    ).filter(
        Q(home_team=team) | Q(visitor_team=team)
    ).order_by('game_date_est')

    serializer = GameSerializer(
        games,
        many=True,
        fields_exclude=[
            'home_team_statistics',
            'visitor_team_statistics',
            'home_team_player_statistics',
            'visitor_team_player_statistics'
        ],
        context={
            'linescore': {
                'fields_exclude': ['id', 'game']
            },
            'team': {
                'fields': ['id', 'symbol', 'teamname_set']
            },
            'teamname': {
                'fields': ['name', 'language']
            },
            'language': {
                'fields': ['name']
            }
        }
    )

    return serializer.data

def get_monthly_games_for_team_this_season(team_id, month):
    team = None
    try:
        team = Team.objects.get(id=team_id)
    except Team.DoesNotExist:
        raise ValueError('Invalid team_id')

    all_team_names = TeamName.objects.select_related('language').all()

    games = Game.objects.select_related(
        'home_team', 'visitor_team'
    ).prefetch_related(
        Prefetch(
            'line_scores',
            queryset=LineScore.objects.select_related('team').prefetch_related(
                Prefetch(
                    'team__teamname_set',
                    queryset=all_team_names
                )
            )
        ),
        Prefetch(
            'home_team__teamname_set',
            queryset=all_team_names
        ),
        Prefetch(
            'visitor_team__teamname_set',
            queryset=all_team_names
        ),
    ).filter(
        Q(home_team=team) | Q(visitor_team=team),
        Q(game_date_est__month=month)
    ).order_by('game_date_est')

    serializer = GameSerializer(
        games,
        many=True,
        fields_exclude=[
            'home_team_statistics',
            'visitor_team_statistics',
            'home_team_player_statistics',
            'visitor_team_player_statistics'
        ],
        context={
            'linescore': {
                'fields_exclude': ['id', 'game']
            },
            'team': {
                'fields': ['id', 'symbol', 'teamname_set']
            },
            'teamname': {
                'fields': ['name', 'language']
            },
            'language': {
                'fields': ['name']
            }
        }
    )

    return serializer.data

def get_team_franchise_history(team_id):
    try:
        Team.objects.get(id=team_id)
    except Team.DoesNotExist:
        raise ValueError('Invalid team_id')

    franchise_history = FranchiseHistory(
        league_id='00'
    ).get_dict()['resultSets'][0]
    
    headers = franchise_history['headers']
    franchise_history = franchise_history['rowSet']

    for team in franchise_history:
        if str(team[1]) == team_id:
            return dict(zip(headers, team))

def get_team_season_stats(year, team_id):
    ## Use Regex to get the year from the season
    year = re.search(r'^\d\d\d\d-\d\d', year)
    if not year:
        raise ValueError('Invalid year format. Use YYYY-YY format')
    
    try:
        Team.objects.get(id=team_id)
    except Team.DoesNotExist:
        raise ValueError('Invalid team_id')
    
    ## Get the ranking from nba_api
    standings = LeagueStandingsV3(
        league_id='00',
        season=year.group(),
        season_type='Regular Season'
    ).get_dict()['resultSets'][0]

    headers = standings['headers']
    standings = standings['rowSet']

    ## Get the team ranking
    ranking = {}

    for team in standings:
        if str(team[2]) == team_id:
            ranking = dict(zip(headers, team))
            break
    
    return ranking

def get_player_last_n_games_log(player_id, n=5):
    stats = PlayerStatistics.objects.filter(
        player__id=player_id
    ).select_related(
        'player',
        'game__visitor_team',
        'team'
    ).order_by(
        '-game__game_date_est'
    )[:n]

    return stats

def get_last_n_games_log(team_id, n=5):
    if n < 1 or n > 82:
        raise ValueError('Invalid n value. n should be between 1 and 82')

    try:
        Team.objects.get(id=team_id)
    except Team.DoesNotExist:
        raise ValueError('Invalid team_id')
    
    all_team_names = TeamName.objects.select_related('language').all()
    
    ## Get the last 5 games log from nba_api
    games = Game.objects.select_related(
        'home_team', 'visitor_team'
    ).prefetch_related(
        Prefetch(
            'home_team__teamname_set',
            queryset=all_team_names
        ),
        Prefetch(
            'visitor_team__teamname_set',
            queryset=all_team_names
        )
    ).filter(
        Q(home_team__id=team_id) | Q(visitor_team__id=team_id),
        Q(game_status_id=3) | Q(game_status_id=2)
    ).order_by('-game_date_est')[:n]

    if games.count() < n:
        games = Game.objects.select_related(
            'home_team', 'visitor_team'
        ).prefetch_related(
            Prefetch(
                'home_team__teamname_set',
                queryset=all_team_names
            ),
            Prefetch(
                'visitor_team__teamname_set',
                queryset=all_team_names
            )
        ).filter(
            Q(home_team=team_id) | Q(visitor_team=team_id),
        ).order_by('game_date_est')[:n]

    serializer = GameSerializer(
        games,
        many=True,
        fields_exclude=[
            'line_scores',
            'home_team_statistics',
            'visitor_team_statistics',
            'home_team_player_statistics',
            'visitor_team_player_statistics'
        ],
        context={
            'team': {
                'fields': ['id', 'symbol', 'teamname_set']
            },
            'teamname': {
                'fields': ['name', 'language']
            },
            'language': {
                'fields': ['name']
            }
        }
    )

    linescores = LineScore.objects.filter(
        game__in=games
    ).select_related(
        'game',
        'team'
    ).order_by(
        'game__game_date_est',
        'game__game_sequence'
    )

    linescore_serializer = LineScoreSerializer(
        linescores,
        many=True,
        context={
            'game': {
                'fields': ['game_id']
            },
            'team': {
                'fields': ['id']
            }
        }
    )

    return serializer.data, linescore_serializer.data

def get_player_career_stats(player_id):
    ## Get the team players from nba_api
    career_stats = PlayerCareerStatistics.objects.select_related('player', 'team').filter(
        player__id=player_id
    )

    return career_stats

def get_player_current_season_stats(player_id, team_id):
    current_season = settings.SEASON_YEAR 

    career_stats = PlayerCareerStatistics.objects.select_related('player', 'team').filter(
        player__id=player_id,
        season_id=current_season
    )

    if not career_stats.exists():
        return create_empty_player_season_stats()

    serializer = PlayerCareerStatisticsSerializer(
        career_stats.first(),
        fields_exclude=['player', 'team', 'team_data'],
    )
    
    return serializer.data

def get_team_players(team_id):
    try:
        Team.objects.get(id=team_id)
    except Team.DoesNotExist:
        raise ValueError('Invalid team_id')

    return Player.objects.filter(
        team__id=team_id
    ).prefetch_related('team__teamname_set').all()

def register_games_for_the_current_season():
    # extract data from the certain date to certain date
    # save the data to the database

    starting_date = datetime(2024, 10, 22)
    ending_date = datetime(2025, 4, 13)

    current_date = starting_date
    
    while current_date <= ending_date:
        scoreboard_data = ScoreboardV2(
            game_date=current_date,
            league_id='00',
            day_offset=0
        ).get_dict()['resultSets']

        games = scoreboard_data[0]
        headers = games['headers']
        games = games['rowSet']

        for game in games:
            game_data = dict(zip(headers, game))
            print(game_data)
            home_team = None
            visitor_team = None 

            try:
                home_team = Team.objects.get(id=game_data['HOME_TEAM_ID'])
                print(f'Home team: {home_team.symbol}')
                visitor_team = Team.objects.get(id=game_data['VISITOR_TEAM_ID'])
                print(f'Visitor team: {visitor_team.symbol}')
            except Team.DoesNotExist:
                continue

            if home_team.symbol == visitor_team.symbol:
                raise ValueError('Home team and visitor team are the same')
            
            ## create a datetime object from the string date and time, with the timezone set to EST
            datetime_obj = datetime.fromisoformat(game_data['GAME_DATE_EST'])

            timezone = pytz.timezone('US/Eastern')
            try:
                hour, minute = calculate_time(game_data['GAME_STATUS_TEXT'])
                datetime_obj = datetime_obj.replace(hour=hour, minute=minute, tzinfo=timezone)
            except IndexError:
                pass 

            game_instance = Game(
                game_id=game_data['GAME_ID'],
                game_date_est=datetime_obj,
                game_sequence=game_data['GAME_SEQUENCE'],
                game_status_id=game_data['GAME_STATUS_ID'],
                game_status_text=game_data['GAME_STATUS_TEXT'],
                game_code=game_data['GAMECODE'],
                home_team=home_team,
                visitor_team=visitor_team,
                season=game_data['SEASON'],
                live_period=game_data['LIVE_PERIOD'],
                live_pc_time=game_data['LIVE_PC_TIME'],
                natl_tv_broadcaster_abbreviation=game_data['NATL_TV_BROADCASTER_ABBREVIATION'],
                home_tv_broadcaster_abbreviation=game_data['HOME_TV_BROADCASTER_ABBREVIATION'],
                away_tv_broadcaster_abbreviation=game_data['AWAY_TV_BROADCASTER_ABBREVIATION'],
                live_period_time_bcast=game_data['LIVE_PERIOD_TIME_BCAST'],
                arena_name=game_data['ARENA_NAME'],
                wh_status=game_data['WH_STATUS'],
                wnba_commissioner_flag=game_data['WNBA_COMMISSIONER_FLAG']
            )

            game_instance.save()
            LineScore.objects.create(
                game=game_instance,
                team=home_team,
            )
            LineScore.objects.create(
                game=game_instance,
                team=visitor_team,
            )

            LineScore.objects.filter(game=game_instance, team=home_team).get()
            LineScore.objects.filter(game=game_instance, team=visitor_team).get()

            print(f"Game {game_instance.game_id} created")

        current_date += timedelta(days=1)