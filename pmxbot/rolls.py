
from __future__ import absolute_import

import datetime

import pmxbot
from . import storage
from . import logging
from pmxbot.core import on_join

class ParticipantLogger(storage.SelectableStorage):
	"Base class for logging participants"

	@classmethod
	def initialize(cls):
		cls.store = cls.from_URI(pmxbot.config.database)
		cls._finalizers.append(cls.finalize)

	@classmethod
	def finalize(cls):
		del cls.store

	def list_channels(self):
		return self._list_channels()

	def log_join(self, nick, channel):
		self.log(nick, channel, 'join')

	def log_leave(self, nick, channel):
		self.log(nick, channel, 'leave')


@on_join()
def log_join(nick, channel, **kwargs):
	if channel not in pmxbot.config.log_channels:
		return
	ParticipantLogger.store.log_join(nick, channel)

class SQLiteLogger(ParticipantLogger, storage.SQLiteStorage):

	def init_tables(self):
		LOG_CREATE_SQL = '''
		CREATE TABLE IF NOT EXISTS rolls (
			id INTEGER NOT NULL,
			datetime DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
			channel VARCHAR NOT NULL,
			nick VARCHAR NOT NULL,
			change TEXT,
			PRIMARY KEY (id) )
		'''
		INDEX_DTC_CREATE_SQL = 'CREATE INDEX IF NOT EXISTS ix_rolls_datetime_channel ON rolls (datetime, channel)'
		INDEX_DT_CREATE_SQL = 'CREATE INDEX IF NOT EXISTS ix_rolls_datetime ON rolls (datetime desc)'
		self.db.execute(LOG_CREATE_SQL)
		self.db.execute(INDEX_DTC_CREATE_SQL)
		self.db.execute(INDEX_DT_CREATE_SQL)
		self.db.commit()

	def log(self, nick, channel, change):
		INSERT_LOG_SQL = 'INSERT INTO rolls (datetime, channel, nick, change) VALUES (?, ?, ?, ?)'
		now = datetime.datetime.utcnow()
		self.db.execute(INSERT_LOG_SQL, [now, channel, nick, change])
		self.db.commit()

class MongoDBLogger(ParticipantLogger, storage.MongoDBStorage):
	collection_name = 'rolls'

	def log(self, nick, channel, change):
		self.db.ensure_index([
			('datetime.d', storage.pymongo.DESCENDING),
			('channel', storage.pymongo.ASCENDING),
			])
		now = datetime.datetime.utcnow()
		self.db.insert(dict(channel=channel, nick=nick, change=change,
			datetime=logging.MongoDBLogger._fmt_date(now)))
