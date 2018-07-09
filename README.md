# Project 4: Catalog
A python program that runs a Flask application catalog website where users are able to sign-in with Google authentication and view a list of producted grouped by categories. Registered users have the ability to create, edit, and delete their own items. This is the fourth project assignment from [Udacity's Full Stack Web Developer Nanodegree](https://www.udacity.com/nanodegree).

## Prerequisites

### Python
Python 2.x is required to run the project. Python can be downloaded [here](https://www.python.org/downloads/).

### VirtualBox
VirtualBox is required to run on the virtual machine. The download link can be found here [here](https://www.virtualbox.org/wiki/Download_Old_Builds_5_1).

### Vagrant
Vagrant is required and used with VirtualBox to create a local development environment. You can download it [here](https://www.vagrantup.com/downloads.html).

### Udacity's Full Stack Nanodegree VM
The Virtual Machine configuration will be provided by Udacity. It will contain the directory **fullstack-nanodegree-vm** Download the VM Connfiguration [here](https://github.com/udacity/fullstack-nanodegree-vm).

## How to Use
1. Clone this repository and make sure that the downloaded files are inside the **fullstack-nanodegree-vm/vagrant/catalog** directory.
2. Open the terminal and **cd** into the **fullstack-nanodegree-vm/vagrant** directory.<br>
3. Enter the command **vagrant up** to run vagrant<br>
4. Enter the command **vagrant ssh** to login into the VM<br>
5. **cd** into the **fullstack-nanodegree-vm/vagrant/catalog** directory.
6. Enter the command **python database_setup.py** to setup your database<br>
7. Enter the command **python load_database.py** to load pre-populated data onto your database.<br>
8. Enter the command **python application.py** to run your server.<br>
9. Open your web browser and visit the url: [http://localhost:5000/](http://localhost:5000/).<br>

## Authors
- Code contributed by Johnson Huynh
