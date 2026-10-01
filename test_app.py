from fastapi.testclient import TestClient
from app.main import app


def test_health_and_data():
    with TestClient(app) as client:
        assert client.get('/health').status_code == 200
        schools = client.get('/api/schools')
        assert schools.status_code == 200
        total = sum(len(c['schools']) for c in schools.json()['categories'])
        assert total == 75
        assert client.get('/api/leaderboard').json()['items']

if __name__ == '__main__':
    test_health_and_data()
    print('OK')
