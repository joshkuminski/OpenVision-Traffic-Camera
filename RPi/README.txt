Place all python files in the directory: /home/pi/scripts

# Install MySQL Database  
sudo apt update
sudo apt upgrade
sudo apt install mariadb-server
sudo mysql_secure_installation
sudo mysql -u root -p
CREATE DATABASE RPiCamera_db;
CREATE USER 'OpenVisionUser'@'localhost' IDENTIFIED BY 'OpenVision';
GRANT ALL PRIVILEGES ON CameraDB.* TO 'OpenVisionUser'@'localhost';
FLUSH PRIVILEGES;

# Install PHPMyAdmin
sudo apt install phpmyadmin -> select apache2 web server -> select 'yes' on the next prompt. This will run you through setting up a password for PHPmyAdmin itself
sudo nano /etc/apache2/apache2.conf
  Include @ bottom: Include /etc/phpmyadmin/apache.conf
sudo service apache2 restart
sudo ln -s /usr/share/phpmyadmin /var/www/html

# Now go to ip/phpmyadmin in a browser

sudo apt install matchbox-keyboard
sudo apt install arduino
sudo apt-get install python3-pil python3-pil.imagetk

#edit file /etc/X11/xorg.conf
Section "InputClass"
   Identifier "calibration"
   Driver "evdev"
   MatchProduct "FT5406 memory based driver"

   Option "EmulateThirdButton" "1"
   Option "EmulateThirdButtonTimeout" "750"
   Option "EmulateThirdButtonMoveThreshold" "30"
EndSection
