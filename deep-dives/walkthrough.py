#!/usr/bin/env python3
"""Run one real lab and print its executed commands and responses for inspection."""
import argparse
import json
import shlex
import subprocess
import sys
import time

import lab


def interesting(args, input_text):
    command = ' '.join(map(str, args))
    if input_text and 'psql' in args:
        return input_text.strip() != 'SELECT 1;' and 'pg_stat_activity' not in input_text
    if 'redis-cli' in args:
        return args[-1] != 'PING'
    return any(marker in command for marker in (
        '/work/Replay.java', '/work/recovery.py', '/bin/promtool',
        'docker build --progress=plain', 'docker history --no-trunc',
    ))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('name', choices=lab.LABS)
    parser.add_argument('--hold', type=int, default=0, help='Keep the completed terminal visible for 0–60 seconds.')
    options = parser.parse_args()
    if not 0 <= options.hold <= 60:
        parser.error('--hold must be between 0 and 60')
    if not __debug__:
        parser.error('Run without -O so the lab assertions remain enabled.')
    original_run = subprocess.run

    def visible_run(args, **kwargs):
        selected = interesting(args, kwargs.get('input'))
        if selected:
            print('\n$ ' + shlex.join(map(str, args)), flush=True)
            if kwargs.get('input'):
                print(kwargs['input'].rstrip(), flush=True)
        result = original_run(args, **kwargs)
        if selected:
            for output in (result.stdout, result.stderr):
                if output:
                    print(output.rstrip(), flush=True)
        return result

    print(f'EMMINEX TECHDOCS | {options.name} | live command walkthrough', flush=True)
    print('Disposable local fixtures. Commands below are executed, not replayed from a saved report.\n', flush=True)
    subprocess.run = visible_run
    try:
        sys.argv = [sys.argv[0], options.name]
        lab.main()
    finally:
        subprocess.run = original_run
    if options.name == 'otel':
        for label in ['before', 'after']:
            path = lab.ROOT / f'evidence/otel-export-{label}.json'
            data = json.loads(path.read_text())
            span = data['resourceSpans'][0]['scopeSpans'][0]['spans'][0]
            print(f'\n{label.upper()} EXPORT: span attributes and events')
            print(json.dumps({'attributes': span['attributes'], 'events': span['events']}, indent=2))
    print('\nWALKTHROUGH COMPLETE: all lab assertions passed and cleanup finished.', flush=True)
    if options.hold:
        time.sleep(options.hold)


if __name__ == '__main__':
    main()
