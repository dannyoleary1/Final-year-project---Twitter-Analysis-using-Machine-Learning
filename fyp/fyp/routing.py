from channels.routing import route
from fyp_webapp.consumers import ws_connect, ws_receive, ws_disconnect

channel_routing = [
    route('websocket.connect', ws_connect),
    route('ws_receive', ws_receive),
    route('ws_disconnect', ws_disconnect),
]