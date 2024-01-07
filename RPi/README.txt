Place all python files in the directory: /home/pi/scripts

# Install MySQL Database  
sudo apt update
sudo apt upgrade
sudo apt install mariadb-server
sudo mysql -u root -p
CREATE DATABASE CameraDB;
CREATE USER 'OpenVisionUser'@'localhost' IDENTIFIED BY 'OpenVision';
GRANT ALL PRIVLEGES ON CameraDB.* TO 'OpenVisionUser'@'localhost';
FLUSH PRIVLIGES;

# Install PHPMyAdmin (optional)
sudo apt install phpmyadmin -> select apache2 web server
sudo nano /etc/apache2/apache2.conf
  Include @ bottom: /etc/phpmyadmin/apache.conf
sudo service apache2 restart
sudo ln -s /usr/share/phpmyadmin /var/www/html


