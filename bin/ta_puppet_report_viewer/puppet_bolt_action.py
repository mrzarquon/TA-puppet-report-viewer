# encoding = utf-8

import pie
import json

# alert['global']['puppet_enterprise_console'] = helper.get_global_setting("puppet_enterprise_console")
# alert['global']['puppet_read_user'] = helper.get_global_setting("puppet_read_user")
# alert['global']['puppet_read_user_pass'] = helper.get_global_setting("puppet_read_user_pass")
# alert['global']['splunk_hec_url'] = helper.get_global_setting("splunk_hec_url")
# alert['global']['splunk_hec_token'] = helper.get_global_setting("splunk_hec_token")
# alert['global']['bolt_user'] = helper.get_global_setting("bolt_user")
# alert['global']['bolt_user_pass'] = helper.get_global_setting("bolt_user_pass")
# alert['global']['puppet_bolt_server'] = helper.get_global_setting("puppet_bolt_server")
# alert['global']['puppet_action_hec_token'] = helper.get_global_setting("puppet_action_hec_token")
# alert['global']['puppet_db_url'] = helper.get_global_setting("puppet_db_url")

# alert['param']['transaction_uuid'] = helper.get_param("transaction_uuid")

# events = helper.get_events()
# for event in events:
#     alert['event'] = json.loads(event['_raw'])


def run_bolt_task_custom(alert):
  # this just writes the alert with a proper task name and param
  # then passes it to the generic run_bolt_task function

  if not alert['param']['task_type']:
    raise Exception("No task type specified in the alert event")

  task_type = alert['param']['task_type'] 
  bolt_target = alert['param']["bolt_{0}_target".format(task_type)]
  bolt_name = alert['param']["bolt_{0}_name".format(task_type)]
  task_name = '{0}::{1}'.format(task_type, bolt_name)

  # these are the values created by our generic modalert for tasks
  alert['param']['task_name'] = task_name
  alert['param']['task_parameters'] = '{}'
  alert['param']['bolt_target'] = bolt_target

  # hardcoding to production for Investigate module
  alert['param']['puppet_environment'] = 'production'

  run_bolt_task(alert)

def run_bolt_task(alert):
  # load our URLs, we generate possible ones assuming the console hostname is valid
  # however if a user provides their own pdb or bolt url it goes here
  # this also allows for us to add an int_proxy feature in the future
  endpoints = pie.util.getendpoints(alert['global']['puppet_enterprise_console'])
  rbac_url = endpoints['rbac']
  bolt_url = alert['global']['puppet_bolt_server'] or endpoints['bolt']
  puppet_environment = alert['param']['puppet_environment']
  splunk_hec_url = alert['global']['splunk_hec_url']
  puppet_action_hec_token = alert['global']['puppet_action_hec_token'] or alert['global']['splunk_hec_token']
  bolt_target = alert['param']['bolt_target']
  task_name = alert['param']['task_name']
  task_parameters = '{}'

  if 'task_parameters' in alert['param'].keys():
    try:
      json_task_parameters = json.loads(alert['param']['task_parameters'])
      task_parameters = json.dumps(json_task_parameters)
    except:
      error_string = 'Task {} on host {} uninstigated - Task Parameters must be in a correct JSON format, please check this and try again'.format(task_name,bolt_target)
      pie.hec.post_action(error_string, bolt_target, splunk_hec_url, puppet_action_hec_token)
      raise SystemExit(error_string)

  pe_console = endpoints['console_hostname']

  message = {
    'message': 'Running task {} on {} '.format(task_name,bolt_target),
    'action_type': 'task',
    'action_name': task_name,
    'action_parameters': task_parameters,
    'action_state': 'starting',
    'alert_event': alert['result'],
  }

  # if this happens to be a puppet run causing this task to be fired
  if alert['result']['transaction_uuid']:
    message['transaction_uuid'] = alert['result']['transaction_uuid']
  
  pie.hec.post_action(message, bolt_target, splunk_hec_url, puppet_action_hec_token)

  bolt_user = alert['global']['bolt_user'] or alert['global']['puppet_read_user']
  bolt_user_pass = alert['global']['bolt_user_pass'] or alert['global']['puppet_read_user_pass']
  task_timeout = alert['param']['task_timeout'] or 360

  auth_token = pie.rbac.genauthtoken(bolt_user,bolt_user_pass,'splunk report viewer',rbac_url, timeout=task_timeout)

  # note: parameters is expected as a text string, not json, so in sample alert json must be represented as:
  # "task_parameters": "{ \"name\": \"ntpd\", \"action\": \"status\"}"

  job = pie.bolt.reqtask(bolt_target,
                         task_name,
                         auth_token,
                         puppet_environment,
                         bolt_url,
                         parameters=task_parameters)

  jobid = job['name']
  jobresults = pie.bolt.getjobresult(jobid, auth_token, bolt_url, timeout=task_timeout)

  # right now we're only running tasks against a single target, but may have things in the future returing multiple nodes
  for result in jobresults['items']:
    rmessage = message
    rmessage['action_state'] = result['state']
    rmessage['joburl'] = 'https://{}/#/run/jobs/{}'.format(pe_console,jobid)
    rmessage['pe_console'] = pe_console
    rmessage['result'] = result['result']
    rmessage['transaction_uuid'] = result['transaction_uuid'] or message['transaction_uuid']
    rmessage['start_timestamp'] = result['start_timestamp']
    rmessage['duration'] = result['duration']
    rmessage['finish_timestamp'] = result['finish_timestamp']

    if rmessage['action_state'] == 'finished':
      rmessage['message'] = 'Successfully ran task {} on {} '.format(task_name,result['name'])
    elif result['state'] == 'failed':
      rmessage['message'] = 'Failed to run task {} on {} '.format(task_name,result['name'])
    else:
      rmessage['message'] = 'Something happened to task {} on {} that we have no idea about'.format(task_name,result['name'])

    pie.hec.post_action(rmessage, result['name'], splunk_hec_url, puppet_action_hec_token)

# this is our interactive load option
# assumes you're running this library directly from the command line
# cat example_alert.json | python $thisfile.py

if __name__ == "__main__":
  import sys
  import json

  alert = json.load(sys.stdin)
  try:
    run_bolt_task_custom(alert)
  except KeyError:
    run_bolt_task(alert)
