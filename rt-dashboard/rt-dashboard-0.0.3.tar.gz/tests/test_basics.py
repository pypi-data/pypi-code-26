import json


def test_dashboard_ok(app):
    response = app.get_response('localhost', '/')
    assert response.status_code == 200
    assert b"RQ dashboard" in response.data


def test_queues_list_json(app):
    response = app.get_response('localhost', '/queues.json')
    assert response.status_code == 200
    data = json.loads(response.data.decode('utf8'))
    print(data)
    assert len(data['queues']) == 3


def test_workers_list_json(app):
    response = app.get_response('localhost', '/workers.json')
    assert response.status_code == 200
    data = json.loads(response.data.decode('utf8'))
    assert data['workers'] == []


def test_queue_empty(app):
    response = app.get_response('localhost', '/queue/dashboardtestqueue/empty', method='POST')
    assert response.status_code == 200
