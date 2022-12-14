# Develop a secure Back end using Django ORM. 

This repository is the project 12 of my Open ClassRooms path. The story is that I am working for Epic Events, a consulting firm helping high profile clients throw the next "greatest party". Because their outdated Customer Relationship Manager have been hacked, their client data have been compromised. Thus, in order to regain their customer trust, they decided to built their own internal secure CRM. I am in charge of the project. 

## 🔧 SET UP 

requirements.txt lists all the needed dependencies. The unusual line 5 and setup.py are written in order to avoid the `ImportError: attempted relative import beyond top-level package`. I had to package the django project, install and import it. In other words, I import some resources internal to the project from the git repository, just as if the project would be a third party library, instead of writing relative imports.  

## 📄 Description 

The crm folder holds the admin app. The frontend is the django admin website. Only authenticated users can access it. The module models.py defines four models (CustomUser, Client, Event and Contract) that are used throughout this app and the other one, named api. The CustomUser models allows us to differentiate three types of users: managers, salesmen and support team members. They have different create, read, update and delete permissions. The differentiated access levels are set in admins.py. 

The app folder holds the api app. There's no frontend as the goal is to enable another application to securely access the database. Indeed, urls.py defines endpoints accessible only with credentials. The create, read, update and delete differentiated permissions are set in views.py. They follow the same guidelines as the crm app.  

# 👷‍♂️ Contributors

Gide Rutazihana, student, giderutazihana81@gmail.com 
Ashutosh Purushottam, mentor

# License

 There's no license 
