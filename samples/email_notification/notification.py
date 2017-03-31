from flask import Flask
from flask import request
from flask import abort
import pytz
import json
import logging
import binascii
import dateutil.parser
import hmac
from hashlib import sha1
from datetime import datetime
from subprocess import Popen, PIPE
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

logging.basicConfig(level=logging.INFO)
config_file = os.path.join(os.path.dirname(__file__), 'settings.json')
app = Flask(__name__)

# will be overridden if present in config_file
SCALR_SIGNING_KEY = ''


@app.route("/", methods=['POST'])
def webhook_listener():
    try:
        if not validateRequest(request):
            abort(403)

        data = json.loads(request.data)
        if not 'eventName' in data or not 'data' in data:
            abort(404)

        return processEvent(data['data'], data['eventName'])

    except Exception as e:
        logging.exception('Error processing this request')
        abort(500)

def processEvent(data, event):
    r = send_email(data, event)
    logging.info(r)
    return 'Ok'

def send_email(data, event):
    msg = MIMEMultipart('alternative')
    msg['Subject'] = "Scalr event"
    msg['From'] = "notifications@scalr.com"
    msg['To'] = data['SCALR_EVENT_FARM_OWNER_EMAIL']
    text = """Hello,

An event just occurred: {event} {hostname}

Regards,
The Scalr team
""".format(event=event, hostname=data['SCALR_EVENT_SERVER_HOSTNAME'])
    html = """<html>
<head></head>
<body>
    <p>
        Hello,<br>
        An event just occurred: {event} {hostname}<br>
        <br>
        Regards,<br>
        The Scalr team
    </p>
</body>
</html>""".format(event=event, hostname=data['SCALR_EVENT_SERVER_HOSTNAME'])
    part1 = MIMEText(text, 'plain') 
    part2 = MIMEText(html, 'html')
    msg.attach(part1)
    msg.attach(part2)
    return send_notification(msg)

def send_notification(msg):
    p = Popen(["/usr/sbin/sendmail", "-t", "-oi"], stdin=PIPE)
    p.communicate(msg.as_string())
    return p.wait()

def validateRequest(request):
    if not 'X-Signature' in request.headers or not 'Date' in request.headers:
        return False
    date = request.headers['Date']
    body = request.data
    expected_signature = binascii.hexlify(hmac.new(SCALR_SIGNING_KEY, body + date, sha1).digest())
    if expected_signature != request.headers['X-Signature']:
        return False
    date = dateutil.parser.parse(date)
    now = datetime.now(pytz.utc)
    delta = abs((now - date).total_seconds())
    return delta < 300

def loadConfig(filename):
    with open(config_file) as f:
        options = json.loads(f.read())
        for key in options:
            if key in []:
                logging.info('Loaded config: {}'.format(key))
                globals()[key] = options[key]
            elif key == 'SCALR_SIGNING_KEY':
                logging.info('Loaded config: {}'.format(key))
                globals()[key] = options[key].encode('ascii')

loadConfig(config_file)

if __name__=='__main__':
    app.run(debug=False, host='0.0.0.0')
