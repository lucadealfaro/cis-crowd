# coding: utf8
from datetime import datetime
import datetime as dates # Ah, what a mess these python names
from gluon.validators import IS_FLOAT_IN_RANGE

DATE_FORMAT = '%Y-%m-%d %H:%M %Z'
datetime_validator = IS_LOCALIZED_DATETIME(timezone=pytz.timezone(user_timezone), format=DATE_FORMAT)

db.define_table('binding',
    Field('chromosome', required=True),
    Field('start', 'integer', required=True),
    Field('end', 'integer', required=True),
    Field('gene_id', required=True),
    Field('cell_type', required=True),
    Field('score', 'double'),
    Field('status', 'integer'),
    Field('method'),
    Field('user', default=current.user_email),
    Field('user_id', default=current.user_id),
    Field('created_on', 'datetime', default=datetime.utcnow()),
    Field('updated_on', 'datetime', update=datetime.utcnow()),
    )

db.binding.id.readable = False
db.binding.user.writable = False
db.binding.user_id.readable = db.binding.user_id.writable = False
db.binding.created_on.writable = False
db.binding.updated_on.writable = False
#db.binding.created_on.requires = datetime_validator
#db.binding.updated_on.requires = datetime_validator

db.define_table('comment',
    Field('binding', db.binding, required=True),
    Field('vote', 'double'),
    Field('comment', 'text'),
    Field('user', default=current.user_email),
    Field('user_id', default=current.user_id),
    Field('created_on', 'datetime', default=datetime.utcnow()),
    Field('updated_on', 'datetime', update=datetime.utcnow()),                
    )

db.comment.id.readable = False
db.comment.binding.writable = False
db.comment.vote.requires=IS_FLOAT_IN_RANGE(-2, 2)
db.comment.user.writable = False
db.comment.user_id.readable = db.comment.user_id.writable = False
db.comment.created_on.writable = False
db.comment.updated_on.writable = False
db.comment.created_on.requires = datetime_validator
db.comment.updated_on.requires = datetime_validator
