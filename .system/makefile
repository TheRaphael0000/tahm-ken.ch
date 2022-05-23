install:
	pip install -r ../requirements.txt

	ln -s /var/www/theraphael0000.ch/challsection.theraphael0000.ch/.system/challsection.theraphael0000.ch_nginx.conf /etc/nginx/sites-enabled
	ln -s /var/www/theraphael0000.ch/challsection.theraphael0000.ch/.system/challsection.theraphael0000.ch_gunicorn.service /etc/systemd/system

	systemctl daemon-reload
	systemctl restart nginx
	systemctl enable challsection.theraphael0000.ch_gunicorn
	systemctl restart challsection.theraphael0000.ch_gunicorn
