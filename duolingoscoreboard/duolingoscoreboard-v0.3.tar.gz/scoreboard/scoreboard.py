import requests
import datetime


def get(username):
    user_data = _get_json(username)

    return {
        'username': username,
        'score_per_day': _get_improvement_grouped_by_day(user_data),
        'current_streak': _get_streak(user_data),
        'total_points': _get_total_points(username, user_data),
    }


def _get_json(username):
    response = requests.get(f'https://www.duolingo.com/users/{username}')
    return response.json()


def _get_improvement_grouped_by_day(user_data):
    last_activity = user_data['calendar']
    last_activity.sort(key=lambda x: x['datetime'])
    last_activity = [_parse_activity(a) for a in last_activity]
    last_activity = _group_by(last_activity, key_field='datetime', sum_field='improvement')
    return last_activity


def _get_streak(user_data):
    return user_data['site_streak']


def _get_total_points(user_name, user_data):
    ranking = user_data['language_data']['es']['points_ranking_data_dict']
    ranking = ranking.values()
    ranking = list(filter(lambda x: x['username'].lower() == user_name, ranking))
    ranking = ranking[0]
    ranking = ranking['points_data']['total']
    return ranking


def _group_by(some_list, key_field, sum_field):
    result = {}
    for item in some_list:
        if result.get(item[key_field]):
            result[item[key_field]] += item[sum_field]
        else:
            result[item[key_field]] = item[sum_field]

    return result


def _parse_activity(activity):
    occurrence_time = datetime.datetime.fromtimestamp(activity['datetime'] / 1000)
    return {'improvement': activity['improvement'], 'datetime': occurrence_time.strftime('%Y-%m-%d')}
