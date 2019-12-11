
# encoding = utf-8
import json
from puppet_report_generation import run_report_generation

def process_event(helper, *args, **kwargs):
    """
    # IMPORTANT
    # Do not remove the anchor macro:start and macro:end lines.
    # These lines are used to generate sample code. If they are
    # removed, the sample code will not be updated when configurations
    # are updated.

    [sample_code_macro:start]

    # The following example gets the setup parameters and prints them to the log
    puppet_enterprise_console = helper.get_global_setting("puppet_enterprise_console")
    helper.log_info("puppet_enterprise_console={}".format(puppet_enterprise_console))
    puppet_read_user = helper.get_global_setting("puppet_read_user")
    helper.log_info("puppet_read_user={}".format(puppet_read_user))
    puppet_read_user_pass = helper.get_global_setting("puppet_read_user_pass")
    helper.log_info("puppet_read_user_pass={}".format(puppet_read_user_pass))
    splunk_hec_url = helper.get_global_setting("splunk_hec_url")
    helper.log_info("splunk_hec_url={}".format(splunk_hec_url))
    splunk_hec_token = helper.get_global_setting("splunk_hec_token")
    helper.log_info("splunk_hec_token={}".format(splunk_hec_token))
    bolt_user = helper.get_global_setting("bolt_user")
    helper.log_info("bolt_user={}".format(bolt_user))
    bolt_user_pass = helper.get_global_setting("bolt_user_pass")
    helper.log_info("bolt_user_pass={}".format(bolt_user_pass))
    puppet_bolt_server = helper.get_global_setting("puppet_bolt_server")
    helper.log_info("puppet_bolt_server={}".format(puppet_bolt_server))
    puppet_action_hec_token = helper.get_global_setting("puppet_action_hec_token")
    helper.log_info("puppet_action_hec_token={}".format(puppet_action_hec_token))
    puppet_db_url = helper.get_global_setting("puppet_db_url")
    helper.log_info("puppet_db_url={}".format(puppet_db_url))

    # The following example adds two sample events ("hello", "world")
    # and writes them to Splunk
    # NOTE: Call helper.writeevents() only once after all events
    # have been added
    helper.addevent("hello", sourcetype="sample_sourcetype")
    helper.addevent("world", sourcetype="sample_sourcetype")
    helper.writeevents(index="summary", host="localhost", source="localhost")

    # The following example gets the events that trigger the alert
    events = helper.get_events()
    for event in events:
        helper.log_info("event={}".format(event))

    # helper.settings is a dict that includes environment configuration
    # Example usage: helper.settings["server_uri"]
    helper.log_info("server_uri={}".format(helper.settings["server_uri"]))
    [sample_code_macro:end]
    """

    helper.log_info("Alert action puppet_generate_detailed_report started.")

    # Lets generate that dict we need

    alert = {}
    alert['global'] = {}
    alert['param'] = {}
    alert['global']['puppet_enterprise_console'] = helper.get_global_setting("puppet_enterprise_console")
    alert['global']['puppet_read_user'] = helper.get_global_setting("puppet_read_user")
    alert['global']['puppet_read_user_pass'] = helper.get_global_setting("puppet_read_user_pass")
    alert['global']['splunk_hec_url'] = helper.get_global_setting("splunk_hec_url")
    alert['global']['splunk_hec_token'] = helper.get_global_setting("splunk_hec_token")
    alert['global']['puppet_action_hec_token'] = helper.get_global_setting("puppet_action_hec_token")
    alert['global']['puppet_db_url'] = helper.get_global_setting("puppet_db_url")

    alert['param']['global_override'] = helper.get_param("global_override")

    helper.log_info("Alert action puppet_generate_detailed_report check for json.")

    # Checks for a global overrides parameter and overrides any keys it finds
    try:
      global_override = json.loads(alert['param']['global_override'])
      for keyname, value in global_override.items():
        alert['global'][keyname] = value
    except:
      helper.log_info("global_override failed to be parsed,is it empty or not json.")
    finally:
      helper.log_info("global_override parsing finished continuing to run")

    events = helper.get_events()
    
    for event in events:
        alert['result'] = event
    
    helper.log_info("Alert action data extracted and passed to run_report_generation.")
    run_report_generation(alert)

    helper.log_info("run_report_generation completed successfully.")

    # TODO: Implement your alert action logic here
    return 0
