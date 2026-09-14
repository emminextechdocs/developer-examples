#!/usr/bin/env bash
# Run the complete sequence with assertions and automatic cleanup.
source deep-dives/redis/session.sh
echo '1. Create a group and deliver one event to worker A'
redis_lab_cli XGROUP CREATE orders workers 0 MKSTREAM
event_id=$(redis_lab_cli XADD orders '*' order_id ord-42)
redis_lab_cli XREADGROUP GROUP workers worker-a COUNT 1 STREAMS orders '>'
new_read=$(redis_lab_cli XREADGROUP GROUP workers worker-b COUNT 1 STREAMS orders '>')
[ -z "$new_read" ]
echo 'Worker B new-message read: empty'
echo '2. Restart Redis using the same container storage'
docker restart "$redis_lab" >/dev/null
wait_redis
pending=$(redis_lab_cli XPENDING orders workers)
printf '%s\n' "$pending"
[ "$(printf '%s\n' "$pending" | head -n 1)" = 1 ]
echo '3. Reclaim the original entry after its idle threshold'
sleep 1
claimed=$(redis_lab_cli XAUTOCLAIM orders workers worker-b 100 0-0 COUNT 10)
printf '%s\n' "$claimed"
[ "$(printf '%s\n' "$claimed" | sed -n '2p')" = "$event_id" ]
echo '4. Acknowledge, then inspect pending state and retention'
ack=$(redis_lab_cli XACK orders workers "$event_id")
again=$(redis_lab_cli XACK orders workers "$event_id")
pending=$(redis_lab_cli XPENDING orders workers)
length=$(redis_lab_cli XLEN orders)
echo "First XACK: $ack; repeated XACK: $again"
echo "Pending count: $(printf '%s\n' "$pending" | head -n 1); stream length: $length"
[ "$ack" = 1 ] && [ "$again" = 0 ] && [ "$length" = 1 ]
[ "$(printf '%s\n' "$pending" | head -n 1)" = 0 ]
echo 'PASS: same pending ID recovered and acknowledged; payload retained'
