install:
	pip install -r ../requirements.txt

	ln -s /var/www/tahm-ken.ch/www.tahm-ken.ch/.system/www.tahm-ken.ch_nginx.conf /etc/nginx/sites-enabled
	ln -s /var/www/tahm-ken.ch/www.tahm-ken.ch/.system/www.tahm-ken.ch_gunicorn.service /etc/systemd/system

	systemctl daemon-reload
	systemctl restart nginx
	systemctl enable www.tahm-ken.ch_gunicorn
	systemctl restart www.tahm-ken.ch_gunicorn
