import paramiko
import re
import traceback
from pprint import pprint
import time
from datetime import datetime, timedelta
timeNow = datetime.now()

__author__ = "Lokesh Choudhary"
__copyright__ = "Copyright 2022, Dell Emc Inc."
__version__ = "1.0"
__maintainer__ = "Lokesh Choudhary"
__email__ = "lokesh.choudhary@dell.com"
__status__ = "Development"

MY_SNIPPET_NAME = 'phonehome'
APP_ID = self.app_id
EM7_DID = self.did
DEVICEIP = self.ip
DEBUGGING = 0  # ENABLE WITH 1 = writing to file. 2: it prints to debug logs; if u want to disable set DEBUGGING to 0
DEBUG_LOG_PATH = "/data/logs/phonehome.log"
DEBUG_STR = '{} : {}: {} : {}'.format(MY_SNIPPET_NAME, EM7_DID, DEVICEIP, timeNow)
LOG = self.logger.ui_debug


# DEBUG METHOD TO LOG MESSAGES OF FAILURE SCANARIO
def debug(*data):
    text = ''
    for i in data: text += str(i)
    if (DEBUGGING == 1):
        with open(DEBUG_LOG_PATH, 'a+') as fh:
            fh.write('{}: {}\n'.format(datetime.now(), text))
    if (DEBUGGING == 2):
        if len(text) < 251:
            print(text)
        else:
            text_formatted = []
            while len(text) > 0:
                if len(text) > 250:
                    text_formatted.append(text[:250] + '\n')
                    text = text[250:]
                else:
                    text_formatted.append(text)
                    break
            print(''.join(text_formatted))
            
try:
    LOG("Main block started")
    debug("Main block started")

    API_USER = self.cred_details['cred_user']
    API_PASSWD = self.cred_details['cred_pwd']
    API_HOST = self.cred_details['cred_host']
    API_PORT = self.cred_details['cred_port']

    # Initialize instance of SSH client
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect('ud-em7-dba-09.gis.sms.local', username='em7admin', password='EM7adm1n!')
    client.get_transport()
    cmd1 = "sudo su -c 'phonehome status'"
    cmd2 = "sudo phonehome view"
    final_dict = {}
    stdin, stdout, stderr = client.exec_command(command=cmd1,get_pty=True)
    stdin.write("EM7adm1n!\n")
    stdin.flush()
    time.sleep(10)
    phonehome_ID_list = []
    count = 0
    count1 = 0
    for line in stdout:
        phonehome_ID_status_check = ''
        if re.search(r'(^         )(.[0-9][0-9])', line):
            phonehome_ID_status_check = re.search(r'(^         )(.[0-9][0-9])', line)
        if phonehome_ID_status_check:
            phonehome_ID_list.append(phonehome_ID_status_check.group(2))
    #print (phonehome_ID)
    for ID in phonehome_ID_list:
        stdin, stdout, stderr = client.exec_command(command=cmd2 + ID,get_pty=True)
        stdin.write("EM7adm1n!\n")
        stdin.flush()
        time.sleep(3)
        for view in stdout.readlines():
            output = view.split(":")
            if len(output) > 1:
                if output[0].strip() == 'Loopback' or output[0].strip() == 'ip':
                    ip_address = output[1].strip()
                    final_dict.setdefault("ip_address", {}).update({count: (ip_address.encode())})
                    count = count+1
                if output[0].strip() == 'Summary':
                    summ = output[1].strip()
                    final_dict.setdefault("summ", {}).update({count1: (summ.encode())})
                    count1 = count1 + 1
    print(final_dict)
   
    # debug("calling upload_data function",vcdav_services_status )
    debug("upload fuction call ", final_dict)
    if (final_dict):
        for group, oid_group in self.oids.iteritems():
            for obj_id, oid_detail in oid_group.iteritems():
                if oid_detail['oid_type'] != snippet_id:
                    continue
                oid = oid_detail["oid"]
                for key in final_dict:
                    if (oid == key): oid_detail['result'] = final_dict[key].items()

except Exception as e:
    errstr = traceback.format_exc()
    debug("Error string", errstr)
    LOG(errstr)