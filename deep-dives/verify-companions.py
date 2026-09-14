"""Assert observable UI-companion states through the products' HTTP APIs."""
import argparse
import base64
import json
import time
import urllib.parse
import urllib.request


def get(url, authenticated=False):
    request = urllib.request.Request(url)
    if authenticated:
        token = base64.b64encode(b'lab:local-lab-only').decode()
        request.add_header('Authorization', 'Basic ' + token)
    with urllib.request.urlopen(request, timeout=5) as response:
        return json.load(response)


def verify(mode):
    if mode == 'observability':
        query = urllib.parse.urlencode({'query': 'service:slow_requests:ratio5m'})
        result = get('http://127.0.0.1:19090/api/v1/query?' + query)
        value = float(result['data']['result'][0]['value'][1])
        assert .019 < value < .021, value
        alerts = get('http://127.0.0.1:19090/api/v1/alerts')['data']['alerts']
        assert any(a['labels']['alertname'] == 'CheckoutLatencyBudgetBurn' and a['state'] == 'firing' for a in alerts), alerts
        dashboard = get('http://127.0.0.1:13000/api/dashboards/uid/reliability-lab')
        assert dashboard['meta']['provisioned'] is True
        panels = dashboard['dashboard']['panels']
        assert len(panels) == 4
        assert all(p['datasource']['uid'] == 'prom-lab' for p in panels)
        return {'slow_fraction': value, 'alert': 'firing', 'provisioned_panels': len(panels)}
    queue = get('http://127.0.0.1:15674/api/queues/%2F/orders-ui', True)
    actual = {key: queue[key] for key in ('messages_ready', 'messages_unacknowledged', 'messages')}
    expected = {'messages_ready': int(mode == 'rabbit-ready'), 'messages_unacknowledged': int(mode == 'rabbit-unacked'), 'messages': 1}
    assert actual == expected, actual
    return actual


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=('observability', 'rabbit-unacked', 'rabbit-ready'))
    args = parser.parse_args()
    if not __debug__:
        parser.error('Run without -O so assertions remain enabled.')
    deadline = time.monotonic() + 210
    while True:
        try:
            result = verify(args.mode)
            print(json.dumps({'check': args.mode, 'passed': True, 'actual': result}))
            break
        except Exception:
            if time.monotonic() >= deadline:
                raise
            time.sleep(2)
