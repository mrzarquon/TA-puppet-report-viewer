# encoding = utf-8
import pie
import collections

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
#     alert['result'] = json.loads(event)


def build_report_query(uuid):
  report_elements = [
    'hash', 
    'status', 
    'puppet_version', 
    'report_format', 
    'catalog_uuid', 
    'job_id', 
    'cached_catalog_status', 
    'configuration_version', 
    'environment', 
    'corrective_change', 
    'noop', 
    'noop_pending', 
    'certname', 
    'transaction_uuid', 
    'code_id', 
    'resource_events', 
    'producer_timestamp', 
    'producer', 
    'start_time', 
    'end_time', 
    'receive_time', 
    'logs', 
    'metrics'
  ]

  joined_elements = ', '.join(report_elements)

  query_string = {}
  query_string['query'] = 'reports[{}] {{ transaction_uuid = "{}" }}'.format(joined_elements, uuid)

  return query_string

def parse_metrics(report_metrics):
  mdict = collections.defaultdict(dict)

  for m in report_metrics['data']:
    mdict[m['category']][m['name']] = m['value']
    
  return dict(mdict)

def run_report_generation(alert):

  transaction_uuid = alert['result']['transaction_uuid']
  host = alert['result']['host']

  # load our URLs, we generate possible ones assuming the console hostname is valid
  # however if a user provides their own pdb or bolt url it goes here
  # this also allows for us to add an int_proxy feature in the future
  endpoints = pie.util.getendpoints(alert['global']['puppet_enterprise_console'])
  rbac_url = endpoints['rbac']
  pdb_url = alert['global']['puppet_db_url'] or endpoints['pdb']
  pe_console = endpoints['console_hostname']

  splunk_hec_url = alert['global']['splunk_hec_url']
  puppet_action_hec_token = alert['global']['puppet_action_hec_token'] or alert['global']['splunk_hec_token']

  message = {
    'message': 'Looking up detailed report for run: {}'.format(transaction_uuid),
    'pe_console': pe_console,
    'transaction_uuid': transaction_uuid,
  }

  pie.hec.post_action(message, host, splunk_hec_url, puppet_action_hec_token)

  pql = build_report_query(transaction_uuid)

  pdbuser = alert['global']['puppet_read_user']
  pdbpass = alert['global']['puppet_read_user_pass']

  if alert['global']['use_token'] == 'true':
    auth_token = alert['global']['puppet_read_user_pass']
  else:
    auth_token = pie.rbac.genauthtoken(pdbuser,pdbpass,'splunk report viewer',rbac_url)

  detailed_report = {}
  try:
    detailed_report = pie.pdb.query(pql, pdb_url, auth_token)[0]
  except Exception as e:
    raise Exception("Puppet DB query {} returned no results: error = {}".format(pql, e))
  
  # add URL to the detailed report
  # https://puppet.angrydome.org/#/inspect/report/1261440031c1b59f8238cfbdaaefc7dabb4e3ddb/events

  repo_hash = detailed_report['hash']
  detailed_report['url'] = 'https://{}/#/inspect/report/{}/events'.format(pe_console,repo_hash)
  detailed_report['pe_console'] = pe_console

  parsed_metrics = parse_metrics(detailed_report['metrics'])

  detailed_report['metrics'] = parsed_metrics

  splunk_hec_token = alert['global']['splunk_hec_token']
  
  pie.hec.post_report(detailed_report,splunk_hec_url,splunk_hec_token)

# this is our interactive load option
# assumes you're running this library directly from the command line
# cat example_alert.json | python $thisfile.py

if __name__ == "__main__":
  import sys
  import json
  
  alert = json.load(sys.stdin)
  
  run_report_generation(alert)
