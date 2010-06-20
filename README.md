Nose-Subunit
============

This [nose] plugin changes the default output to [subunit] format. This can be used along with [buildbot] to have better reports.

Installation
-------
Issue the following command:

	easy_install nose-subunit

Usage
-----
Enable this plugin with `--with-subunit`. This plugin is known to work with following builtin nose plugins:

  - `skip` plugin
  - `multiprocess` plugin
  - `failuredetail` plugin

The following plugins are known to conflict with subunit plugin:

  - `collectonly` plugin: If you are only collecting tests, you probably don't care about the output

Nose plugins not mentioned here are not tested by the author. Please feel free to [report your experience] about using nose-subunit with other nose plugins.

UnitTest
--------
under the root of nose-subunit, run

	nosetests --exe

  [nose]: http://somethingaboutorange.com/mrl/projects/nose/
  [subunit]: https://launchpad.net/subunit/
  [buildbot]: http://buildbot.net/
  [report your experience]: mailto:liucougar@gmail.com

