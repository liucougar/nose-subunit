Nose-Subunit
============

This [nose] plugin changes the default output to [subunit] format. This can be used along with [buildbot] to have better reports.

Installation
------------
nose-subunit apparently depends on both `nosetests` and `subunit`.

The following command would install `nose-subunit` and all its dependencies:

	easy_install nose-subunit

nose-subunit can also be downloaded manually from [pypi] or [github]

Usage
-----
Enable this plugin with `--with-subunit`. This plugin is known to work with following builtin nose plugins:

  - `skip` plugin
  - `multiprocess` plugin
  - `failuredetail` plugin
  - `stopOnFailure` builtin feature (enabled by `-x`/`--stop`)
  - `testid` plugin

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
  [pypi]: http://pypi.python.org/pypi/nose-subunit/
  [github]: http://github.com/liucougar/nose-subunit/downloads
  [report your experience]: http://github.com/liucougar/nose-subunit/issues
