Release Notes
==============

3.0.1:
**Breaking Changes**:
- Alert Actions are now moved to https://github.com/puppetlabs/TA-puppet-alert-actions for better compatibility of this App for users who don't use or need the addons

2.0.0:
**Breaking Changes**:
- The alert action named `Generate detailed report` has been renamed `Generate a detailed Puppet report` to make it more specific. The internal name of the action has been renamed to `puppet_generate_detailed_report` from `generate_detailed_report` to prevent confusion with out alert actions and to ensure consistency with other. You will need to update existing searches using this action to use the new name, but no other changes to the searches is required.
- *alert actions will fail until Puppet Username is provided instead of PE auth token*
- *full URIs are now required instead of just hostnames* adds more flexibility the authorization methods (http support and custom ports) but you will need to redo your app configuration before alert actions resume functioning
- Searches defaulting to main and not using the index macros will stop updating if you move the corressponding puppet data to an index but don't change the search

New Features:
- Built in support for running Bolt Tasks in Puppet Enterprise from Splunk
- Metrics tab to show PE metric data if metrics are configured
- Actions Tab in dashboard added to show logs and status of any of this applications alert actions for debugging or auditing
- Support for Puppet Username/Password instead of auth token
- All searches support per sourcetype indexes

Fixes:
- Alert actions work with custom parameters
- Before there was no way to see if your alerts were working easily, now they publish information to the puppet:action sourcetype

1.5.1:
New Features:
- Full dashboard updates
- Support for Facts sourcetype (puppet:facts), and dashboards to use it
- Introduces "Report Builder" page to help a user build reports and then craft custom search from the iterface to use for alerts or their own uses
- Introduces Advanced Search macros to allow for customized indexs without requiring to modify the app. See Advanced Configuration section of the readme
- Add's sourcetypes of puppet:action, puppet:metrics, for future use
- Example Alert added, the search to generate a detailed report for any summary report that isn't "unchanged" has been added to the app, but set as disabled

Fixes:
- Duplicate item entry fixed, sourcetype's are now configured to extract KV from json only once
- [Updated documentation](https://github.com/puppetlabs/ta-puppet-report-viewer)

