
# Zabbix configurations backup


**zabbix_export** is a Python application  for backing up the configuration data of a Zabbix server.  

## Get started
* [Requirements](#requirements)
* [Installation](#installation)
  * [Quick setup](#quick-setup)
  * [Manual setup](#manual-setup) 
  * [Initial Configuration](#initial-configuration)
 * [Examples](#examples)


## Requirements

Supported versions:

* Zabbix 5.0+
* Python 3.8+

## Installation

### Quick setup

This works on a Linux machine. Just run:
```bash
$ make install
```
This will setup a Python virtual environment, download the library dependencies, and set up a *cron job* to back up the 'hosts' configurations on a daily basis, inside the *'BACKUPS'* directory.   
Furthermore, backups older than 15 days will get deleted.  
The details of this job can be adjusted with `crontab -e` command, as usual.  
You will then need to configure the application with the Zabbix Web server's connection details, as described in [Initial Configuration](#initial-configuration).

In order to uninstall the backup job, just:
```bash
$ make uninstall
```


### Manual setup

Install the required dependencies, by:
``` bash
$ pip install -r requirements.txt
```
Then follow the instructions, as provided by the `--help` option:
```bash
$ ./zabbix_export.py --help
```
You will then need to configure the application with the Zabbix Web server's connection details, as described in [Initial Configuration](#initial-configuration).

### Initial Configuration

The application needs to know the listening socket of the Zabbix Web server, as well as a token by which to authenticate its connection. 
The token can be generated either on the Zabbix Web server, or via the provided **getToken.py** script:

**via Zabbix Web server:**  
Navigate to *Users -> API tokens* and choose **Create API token** for a user of Admin roles. 

**via getToken.py:**  
Provide the Zabbix Web server's connection details and the credentials of a user of Admin roles to the script (refer to `getToken.--help`).  
E.g.:  
```bash
$ python getToken.py -s 10.10.10.10 -u Admin -p p@sw0rd
```

Finally, provide the server's connection string and the token in the **zbx_config.ini** file. 

## Examples

Collect the 'hosts' 'maps' configurations, in json format, inside /tmp/zbxBkps directory:
```bash
$ ./zabbix_export.py -d /tmp/zbxBkps -f json -t hosts maps
```
Collect all supported configurations, in xml format, inside Backup directory; compress the collected files, in a zipped archive:   
```bash
$ ./zabbix_export.py -d Backup -z -f xml -t all
```
