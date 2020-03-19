## Developing addon builders

In order to load this module properly into the Splunk Add-On builder for development, the following needs to happen:

- Checkout the branch you want to work on
- tar.gz the directory
- Go to the splunk addon builder
- Delete a previous version of the add-on if it exists
- Import this version

```
$ git checkout -b 'my working branch'
$ COPYFILE_DISABLE=1 tar -C .. --exclude=".git" --exclude="local/" --exclude="metadata/local.meta" --exclude="tmpdir" --owner=0 --group=0 -czvf tmpdir/TA-puppet-report-viewer_export.tar.gz TA-puppet-report-viewer
```

To add your finished work back to the repo:
- Export the build from the Splunk Add-On tool
- Move the downloaded tar.gz to tmpdir
- Expand the export the export in tmpdir
- sync the local repo with the tmpdir contents
- proceed with git commits as needed, etc

```
$ cd tmpdir
$ tar xzvf TA-puppet-report-viewer_2_0_1_export.tgz
$ cd ..
$ rsync -vr tmpdir/TA-puppet-report-viewer_2_0_1_export/* ./
```

## Debuging python alerts

The only modifiable by us python code in this application is the following files INSIDE the `bin/ta_puppet_report_viewer` directory:
```
pie/*
modalert_generate_detailed_report_helper.py
modalert_puppet_run_task_act_helper.py
modalert_puppet_run_task_helper.py
modalert_puppet_run_task_investigate_helper.py
puppet_bolt_action.py
puppet_report_generation.py
```

Alerts are now stand alone functions that can be run via commandline if they are passed the correct alert content. This works because we've changed the modalert provided by the app builder to be a simple "take the values automagically provided by the builder, create a dictionary, and pass that to our own library."

Those files (`bin/ta_puppet_report_viewer/puppet_report_generation.py` & `puppet_bolt_action.py`) have an `if __main__` block that will instead parse json from stdin and convert that to an alert dictionary and pass that to the same function invoked by the alert action. This lets us mock up a complete alert action outside of Splunk. These are stored in README/helperjson/ along with a simple python script that lets you end the dictionary and save it to a file.

Testing should look like:
```
cd bin/ta_puppet_report_vewier`
cat ../../README/helperjson/debugalert.json | python puppet_report_generation.py
```

This gives you interactive python prompt to debug and work with, add print statements, and make sure our interactions with splunk hec and puppet apis are working outside of the Splunk environment, before trying to debug this in the context of the Splunk ecosystem.
