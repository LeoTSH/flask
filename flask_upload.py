import os, zipfile, sys
import pandas as pd
import sqlalchemy as sa
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, Integer, Boolean, DateTime, String, create_engine, func
from datetime import datetime
from werkzeug.utils import secure_filename
from flask import Flask, request, render_template, send_from_directory

Base = declarative_base()
allowed_extensions = set(['zip'])
app = Flask('flask_test')
ufolder = './production/'
#https://fp-assets-dlc.s3.amazonaws.com:443/production/mtf/151/localization.csv  
app.config['BASE_URL'] = 'https://fp-assets-dlc.s3.amazonaws.com:443/production/'
#<user>:<password>@<db server>/<db>
app.config['DB_CONNECTION'] = 'postgresql+psycopg2://xiibraves:xiibraves@localhost/xiibraves'
app.config['UPLOAD_FOLDER'] = ufolder
app.config['DOWNLOAD_PATH'] = None
app.config['GLOBAL_FILE'] = None

class TEST_DB(Base):
	__tablename__ = 'test_db'
	number = Column(Integer, primary_key=True, nullable=False)
	enum = Column(String(4096))
	en = Column(String(4096))
	th = Column(String(4096))
	ko = Column(String(4096))
	de = Column(String(4096))
	link = Column(String(4096), nullable=False)

class DLCVersion(Base):
    __tablename__ = 'dlc_version'
    id = Column(Integer, primary_key=True)
    created = Column(DateTime(timezone=True),
    	default=func.now(),
    	server_default=sa.text('now()'))
    version = Column(Integer, nullable=False)
    type = Column(String(128), nullable=False)
    link = Column(String(4096), nullable=False)
    is_active = Column(Boolean, default=False, server_default='f')
    is_cloudfront = Column(Boolean, default=False, server_default='f')
	
def allowed_filename(filename):
	return '.'in filename and \
	filename.rsplit('.', 1)[1].lower() in allowed_extensions

def file_check(file):
	if (file.content_type == 'application/x-zip-compressed') and allowed_filename(file.filename):
		return True
	else:
		error = ('File is not csv. Please kindly verify')
		return render_template('uploads.html', error=error)

def insert_db(csv):
	result = True
	#<user>:<password>@<db server>/<db>
	engine = create_engine(app.config['DB_CONNECTION'])
	Base.metadata.create_all(engine)
	session = sessionmaker()
	session.configure(bind=engine)
	s = session()
	try:
		for row in range(0, len(csv)):
			record = TEST_DB(**{
				'enum': csv['ENUM'][row],
				'en': csv['EN'][row],
				'th': csv['TH'][row],
				'ko': csv['KO'][row],
				'de': csv['DE'][row]
			})
			s.add(record)
		s.commit()
	except:
		s.rollback()
		result = False
	finally:
		s.close()
	return result

'''def insert_db(csv):
	result = True
	#<user>:<password>@localhost/<db>
	engine = create_engine(app.config['DB_CONNECTION'])
	Base.metadata.create_all(engine)
	session = sessionmaker()
	session.configure(bind=engine)
	s = session()
	try:
		for row in range(0, len(csv)):
			record = TEST_DB(**{
				'created': csv['created'][row],
				'version': csv['version'][row],
				'type': csv['type'][row],
				'link': csv['link'][row],
				'is_active': csv['is_active'][row],
				'is_cloudfront': csv['is_cloudfront'][row]
			})
			s.add(record)
		s.commit()
	except:
		s.rollback()
		result = False
	finally:
		s.close()
	return result'''

@app.route('/uploads', methods = ['GET', 'POST'])
def upload_file():
	if request.method == 'POST':
		file = request.files['file']		
		dlc_type = request.form['type']
		version = request.form['version']
		path = (ufolder + dlc_type + '/' + version + '/')
		if version == None or version == '':
			error = ('Please enter a version number')
			return render_template('uploads.html', error=error)
		if file_check(file):			
			if not os.path.exists(path):
				os.makedirs(path)
			'''else:
					error = ('Duplicate Version Number. Please kindly verify')
					return render_template('uploads.html', error=error)'''
			filename = secure_filename(file.filename)
			file.save(os.path.join(path, filename))
			zip_file = zipfile.ZipFile(path + filename, 'r')
			'''if files in path:
					error = ('Duplicate file. Please kindly verify')
					return render_template('uploads.html', error=error)'''
			zip_file.extractall(path)
			zipfile.ZipFile.close(zip_file)
			for files in os.listdir(path):
				if files.endswith('.zip'):
					os.remove(path + files)
				elif files.endswith('csv'):
					unzipped = files
			try:
				data = pd.read_csv(path + unzipped, encoding='cp1252')
			except:
				error = ('csv file error, please kindly verify')	
				return render_template('uploads.html', error=error)													
				#if insert_db(data) == False:
				#	error = ('Data/DB error, please kindly verify')
				#	return render_template('uploads.html', error=error)
				#else:
				#data.to_csv(ufolder + dlc_type + '/' + version + '/' + filename.split('.')[0] + '.csv', index=False)
			app.config['DOWNLOAD_PATH'] = path
			app.config['GLOBAL_FILE'] = unzipped
			success = ('File uploaded successfully')		
		return render_template('uploads.html', success=success, download=(app.config['BASE_URL'] + dlc_type + '/' + version + '/' + unzipped))
	return render_template('uploads.html')

@app.route('/download/', methods = ['GET', 'POST'])
def get_file():
	try:
		return send_from_directory(app.config['DOWNLOAD_PATH'], app.config['GLOBAL_FILE'], as_attachment= True)
	except Exception as e:
		return str(e)

if __name__ == '__main__':
	app.run(debug=True)