import os
import time
from flask import render_template, jsonify, request
from flask_login import login_required, current_user

from . import agora
from ..models import User
from .agora_key.RtcTokenBuilder import RtcTokenBuilder, Role_Attendee
from pusher import Pusher


# Instantiate a Pusher Client
pusher_client = Pusher(app_id="1340915",
                       key="361d34bd8ddf12fbb43a",
                       secret="d9593d6cebccfec91331,"
                       ssl=True,
                       cluster="ap2"
                       )

@agora.route('/')
@agora.route('/agora')
@login_required
def index():
    users = User.query.all()
    all_users = [user.to_json() for user in users]
    return render_template('agora/index.html', title='Video Chat', allUsers=all_users)


@agora.route('/agora/pusher/auth', methods=['POST'])
def pusher_auth():
    auth_user = current_user.to_json()
    payload = pusher_client.authenticate(
        channel=request.form['channel_name'],
        socket_id=request.form['socket_id'],
        custom_data={
            'user_id': auth_user['id'],
            'user_info': {
                'id': auth_user['id'],
                'name': auth_user['username']
            }
        })
    return jsonify(payload)


@agora.route('/agora/token',  methods=['POST'])
def generate_agora_token():
    auth_user = current_user.to_json()
    appID = "144576c2e25c4a629ce399e7eab920b7"
    appCertificate = "63deaf61e2ff4a13b7c8474ea82a8eac"
    channelName = request.json['channelName']
    userAccount = auth_user['username']
    expireTimeInSeconds = 3600
    currentTimestamp = int(time.time())
    privilegeExpiredTs = currentTimestamp + expireTimeInSeconds

    token = RtcTokenBuilder.buildTokenWithAccount(
        appID, appCertificate, channelName, userAccount, Role_Attendee, privilegeExpiredTs)

    return jsonify({'token': token, 'appID': appID})


@agora.route('/agora/call-user',  methods=['POST'])
def call_user():
    auth_user = current_user.to_json()
    pusher_client.trigger(
        'presence-online-channel',
        'make-agora-call',
        {
            'userToCall': request.json['user_to_call'],
            'channelName': request.json['channel_name'],
            'from': auth_user['id']
        }
    )
    return jsonify({'message': 'call has been placed'})
