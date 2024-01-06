Service files go in /etc/systemd/system
After saving the file run the following commands:
pi:~ $ sudo systemctl enable "name-of-service.service"
pi:~ $ sudo systemctl daemon-reload
