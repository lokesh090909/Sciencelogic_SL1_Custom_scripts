#!/bin/bash
# path to hosts file and file name
FILE_PATH='/etc/ssh'
FILE_NAME='sshd_config'
FILE_NAME_TEMP='sshd_config.temp'

cd "$FILE_PATH"

# setup temp file

if test -f "$FILE_PATH/$FILE_NAME_TEMP";
then
        rm "$FILE_PATH/$FILE_NAME_TEMP"
        touch "$FILE_PATH/$FILE_NAME_TEMP"
fi


# make a backup of the sshd_config file before we do anything

MYBACKUP="$FILE_PATH/sshd_config_"`date +"%Y-%m-%d_T%T_%Z"`.backup
cp $FILE_NAME $MYBACKUP

echo "# Re-write of my.text file" > $FILE_NAME_TEMP
while IFS= read -r LINE
do

    if [ "$LINE" == "#Port 22" ] || [ "$LINE" == "Port 22" ];
    then
     echo "##########################################################################" >> "$FILE_PATH/$FILE_NAME_TEMP"
     echo "# added by script $0 on `date`"                                             >> "$FILE_PATH/$FILE_NAME_TEMP"
     echo "Port 22"                                                                    >> "$FILE_PATH/$FILE_NAME_TEMP"
     echo "Port 7705"                                                                  >> "$FILE_PATH/$FILE_NAME_TEMP"
     echo "##########################################################################" >> "$FILE_PATH/$FILE_NAME_TEMP"
     echo " "                                                                          >> "$FILE_PATH/$FILE_NAME_TEMP"
    elif [ "$LINE" == "#GatewayPorts no" ] || [ "$LINE" == "#GatewayPorts yes" ];
    then
     echo " "                                                                          >> "$FILE_PATH/$FILE_NAME_TEMP"
     echo "##########################################################################" >> "$FILE_PATH/$FILE_NAME_TEMP"
     echo "# modified by script $0 on `date`"                                          >> "$FILE_PATH/$FILE_NAME_TEMP"
     echo "GatewayPorts yes"                                                           >> "$FILE_PATH/$FILE_NAME_TEMP"
     echo "##########################################################################" >> "$FILE_PATH/$FILE_NAME_TEMP"
     echo " "                                                                          >> "$FILE_PATH/$FILE_NAME_TEMP"
    else
     echo "$LINE"                                                                      >>"$FILE_PATH/$FILE_NAME_TEMP"
    fi
done < "$FILE_PATH/$FILE_NAME"

mv "$FILE_PATH/$FILE_NAME_TEMP" "$FILE_PATH/$FILE_NAME"
systemctl restart sshd

# add user em7admin to group em7-ph-local

sudo usermod -aG em7-ph-local em7admin


# Run firewall configurations
sudo  firewall-cmd --permanent --zone=drop --add-port=7750/tcp
sudo  firewall-cmd --permanent --zone=drop --add-port=7705/tcp
sudo  firewall-cmd --permanent --zone=drop --add-port=7760/tcp
sudo  firewall-cmd --permanent --zone=drop --add-port=7770/tcp
sudo  firewall-cmd --reload
