import os
env = os.getenv('BOT_ENV', 'staging')
if env=='debug':
    bot = {'token' : '183365432:AAEs5OxDxYAZ22qJqjM4SzoNtv-GmyTKOsQ'}
    mongo = {'uri': 'localhost'}
else:
    bot = {'token': '157704339:AAH9HsU_e90F8xosACaZJC4NPviGR0Z2IYo'}
    mongo = {'uri': 'mongodb://root:monr9900@equal.cf'}




