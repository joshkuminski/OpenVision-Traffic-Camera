**Running 64bit Debian Bullseye**

Place all python files in the directory: /home/pi/scripts

*** Install MySQL Database *** 
sudo apt update
sudo apt upgrade
sudo apt install mariadb-server
sudo mysql_secure_installation
sudo mysql -u root -p
CREATE DATABASE RPiCamera_db;
CREATE USER 'OpenVisionUser'@'localhost' IDENTIFIED BY 'OpenVision';
GRANT ALL PRIVILEGES ON CameraDB.* TO 'OpenVisionUser'@'localhost';
FLUSH PRIVILEGES;

*** Install PHPMyAdmin *** 
sudo apt install phpmyadmin -> select apache2 web server -> select 'yes' on the next prompt. This will run you through setting up a password for PHPmyAdmin itself
sudo nano /etc/apache2/apache2.conf
  Include @ bottom: Include /etc/phpmyadmin/apache.conf
sudo service apache2 restart
sudo ln -s /usr/share/phpmyadmin /var/www/html

*** Now go to 'your pi ip'/phpmyadmin in a browser *** 
*** Create a Table Named 'CameraSchedule' with 4 Columns: *** 
ID - int - AutoIncrement
Date - Date
Time - text
Duration - int

*** Additional Packages Needed *** 
sudo apt install matchbox-keyboard
sudo apt install arduino
sudo apt-get install python3-pil python3-pil.imagetk
sudo apt install xinput-calibrator  # Then run, sudo xinput_calibrator, to calibrate the touchscreen

*** Setup RTC module *** 
sudo nano /boot/config.txt
add to the end of the file: dtoverlay=i2c-rtc,ds3231
sudo apt -y remove fake-hwclock
sudo update-rc.d -f fake-hwclock remove
sudo nano /lib/udev/hwclock-set -> comment out the following lines:
  #if [ -e /run/systemd/system ] ; then
  #    exit 0
  #fi

#edit file /etc/X11/xorg.conf
Section "InputClass"
   Identifier "calibration"
   Driver "evdev"
   MatchProduct "FT5406 memory based driver"

   Option "EmulateThirdButton" "1"
   Option "EmulateThirdButtonTimeout" "750"
   Option "EmulateThirdButtonMoveThreshold" "30"
EndSection
