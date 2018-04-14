from channels import Group
import json
from channels import Channel
from channels.auth import channel_session_user
from fyp_webapp import tasks

@channel_session_user
def ws_connect(message):
    Group('notifications').add(message.reply_channel)
    message.channel_session['notify'] = 'notifications'
    message.reply_channel.send({
        'accept': True
    })

@channel_session_user
def ws_receive(message):
    print ("its in receive")
    data = json.loads(message.content.get('text'))
    print (data.get("text"))
    tasks.test_job.delay(message.reply_channel.name)

@channel_session_user
def ws_disconnect(message):
    print ("Disconnect.")
    user_group = message.channel_session["notify"]
    Group(user_group).discard(message.reply_channel)

