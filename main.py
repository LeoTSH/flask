import os, zipfile, sys
from model import db
from model import DLCVersion
from model import app
from werkzeug.utils import secure_filename
from flask import Flask, request, render_template, send_from_directory

allowed_extensions = set(['zip'])
ufolder = './production/'

def allowed_filename(filename):
	return '.'in filename and \
	filename.rsplit('.', 1)[1].lower() in allowed_extensions

def file_check(file):
	if (file.content_type == 'application/x-zip-compressed') and allowed_filename(file.filename):
		return True
	else:
		error = ('File is not zip. Please kindly verify')
		return render_template('uploads.html', error=error)

def insert_db(version, type, link):
	result = True
	db.create_all()
	try:
		insert = DLCVersion(
			version=version,
			type= type,
			link=link
			)
		db.session.add(insert)
		db.session.commit()
	except:
		db.session.rollback()
		result = False
	finally:
		db.session.close()
	return result

def check_version(version):
	result = True
	try:
		int(version)
	except ValueError:
		result = False
		return result
	finally:
		return result

@app.route('/uploads', methods = ['GET', 'POST'])
def upload_file():
	if request.method == 'POST':
		file = request.files['file']	
		if file.filename == None or file.filename == '':
			error = ('Please select a file')
			return render_template('uploads.html', error=error)
		dlc_type = request.form['type']
		version = request.form['version']
		path = (ufolder + dlc_type + '/' + version + '/')
		link = (app.config['BASE_URL'] + dlc_type + '/' + version + '/')
		if version == None or version == '' or check_version(version) == False:
			error = ('Please enter a correct version number')
			return render_template('uploads.html', error=error)
		if file_check(file):			
			if not os.path.exists(path):
				os.makedirs(path)
			filename = secure_filename(file.filename)
			file.save(os.path.join(path, filename))	
			if insert_db(version, dlc_type, link) == False:
				error = ('Insert error, please kindly verify')
				return render_template('uploads.html', error=error)
			success = ('File uploaded successfully')	
			for file in os.listdir(path):
				unzipped = file	
			app.config['DOWNLOAD_PATH'] = path
			app.config['GLOBAL_FILE'] = unzipped
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