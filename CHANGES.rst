1104.3
======

* New @regexp decorator. Similar to @contains, except allows regular
  expressions instead of simple string matching. See the README for an example
  of usage. Thanks to `Craig Wright <https://bitbucket.org/crw>`_ for the
  contribution.

1104.2
======

* pmxbot will assume local host name is appropriate for logs URL if no logs
  URL is specified in the config.

1104.1
======

* One may now specify the database name in the URI.
* pmxbot will log the config when starting up.

1104
====

* Updated to work with irc 5.0

1103.6
======

* @contains decorator has a new keyword parameter: `allow_chain`. Set to True
  to allow subsequent @contains decorators to match.
* Issue #18: Strip periods from acronym, fixing errors from remote service.

1103.5
======

* Now use irc 3.3.
* Python 3 bug fixes.

1103.4
======

* Updated to irc 3.1.
* Replaced cleanhtml with BeautifulSoup.
* Preliminary Python 3 support (compiles and runs).

1103.3
======

* Initial support for logging joins/parts in logged channels.

1103.2
======

* Added !logs command to query for the location of the logs.

1103.1
======

* Moved config to 'pmxbot.config'.
* Config parameter no longer required.

1103
====

This release incorporates another substantial refactor. The `pmxbotweb`
package is being removed in favor of the namespaced-package `pmxbot.web`.

Additionally, config entries for the pmxbotweb command have been renamed::

 - `web_host` is now simply `host`
 - `web_port` is now simply `port`

A backward-compatibility shim has been added to support the old config values
until version 1104.

The backward compatibile module `pmxbot.botbase` has been removed.

1102
====

Build 1102 of `pmxbot` involves some major refactoring to normalize the
codebase and improve stability.

With version 1102, much of the backward compatibility around quotes and karma
has been removed::

 - The Karma store must now be referenced as `pmxbot.karma:Karma.store` (a
   class attribute). It is no longer available as `pmxbot.pmxbot:karma` nor
   `pmxbot.util:karma` nor `pmxbot.karma.karma`.
 - Similarly, the Quotes store must now be referenced as
   `pmxbot.quotes:Quotes.store` (a class attribute).
 - Similarly, the Logger store must now be referenced as
   `pmxbot.logging:Logger.store` instead of `pmxbot.botbase.logger`.

Other backward-incompatible changes::

 - The `config` object has been moved into the parent `pmxbot` package.
 - A sqlite db URI must always specify the full path to the database file;
   pmxbot will no longer accept just the directory name.

Other changes::

 - Renamed `pmxbot.botbase` to `pmxbot.core`. A backward-compatibility
   `botbase` module is temporarily available to provide access to the public
   `command`, `execdelay`, and similar decorators.