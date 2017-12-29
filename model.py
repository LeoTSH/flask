from flask_sqlalchemy import SQLAlchemy
from flask import Flask, request, render_template, send_from_directory

app = Flask('__test__')
#<user>:<password>@localhost/<db>
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://xiibraves:xiibraves@localhost/xiibraves'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['BASE_URL'] = 'https://fp-assets-dlc.s3.amazonaws.com:443/production/'
app.config['GLOBAL_FILE'] = None
app.config['DOWNLOAD_PATH'] = None
db = SQLAlchemy(app)

class DLCVersion(db.Model):
    __tablename__ = 'dlc_version'
    id = db.Column(db.Integer, primary_key=True)
    created = db.Column(db.DateTime(timezone=True),
    	default=db.func.now(),
    	server_default=db.text('now()'))
    version = db.Column(db.Integer, nullable=False)
    type = db.Column(db.String(128), nullable=False)
    link = db.Column(db.String(4096), nullable=False)
    is_active = db.Column(db.Boolean, default=True, server_default='t')
    is_cloudfront = db.Column(db.Boolean, default=False, server_default='f')