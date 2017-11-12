import os, zipfile
import sys
import pandas as pd
from werkzeug.utils import secure_filename
from flask import Flask, request, redirect, url_for
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, Integer, Boolean, DateTime, String

Base = declarative_base()
allowed_extensions = set(['zip', 'rar'])
app = Flask('test')
app.config['UPLOAD_FOLDER'] = ufolder
ufolder = "./uploads/"

class TEST_DB(Base):
	__tablename__ = 'test_db'
	number = Column(Integer, primary_key=True, nullable=False)
	enum = Column(String(4096))
	en = Column(String(4096))
	th = Column(String(4096))
	ko = Column(String(4096))
	de = Column(String(4096))
	
def allowed_filename(filename):
	print (filename)
	return '.'in filename and \
	filename.rsplit('.', 1)[1].lower() in allowed_extensions

def insert_db(csv):
	engine = create_engine('postgresql+psycopg2://postgres:LeoLio123@localhost/postgres')
	Base.metadata.create_all(engine)
	session = sessionmaker()
	session.configure(bind=engine)
	s = session()
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
	s.close()

@app.route('/uploads', methods = ['GET', 'POST'])
def upload_file():
	if request.method == 'POST':
		file = request.files['file']
		dlc_type = request.form['type']
		version = request.form['version']
		if file and allowed_filename(file.filename):
			filename = secure_filename(file.filename)
			if filename.endswith('.zip') or filename.endswith('.rar'):
				file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
				zip_file = zipfile.ZipFile(ufolder + filename, 'r')
				zip_file.extractall(ufolder)
				zipfile.ZipFile.close(zip_file)
				for file in os.listdir(ufolder):
					if file.endswith('.csv'):
						csv_file = file
				data = pd.read_csv(ufolder + csv_file, encoding='cp1252')															
				insert_db(data)
				for files in os.listdir(ufolder):
					os.remove(ufolder + files)
				data.to_csv(ufolder + dlc_type + str(version) + '.csv', index=False)
			else:
				file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))			
	return '''
	<!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form method=post enctype=multipart/form-data>
    	<b>DLC Type:</b>
      	<select name="type">
      		<option value="mtf">mtf</option>
      		<option value="client_db">client_db</option>
      		<option value="dlc_ios">dlc_ios</option>
      		<option value="dlc_android">dlc_android</option>
      	</select>
      	
      	<p><b>Version Number:</b>
      		<input type="text" name="version">    

      	<p><input type=file name='file'>
        	<input type=submit value=Upload> 
    </form>
    '''

if __name__ == '__main__':
	app.run()