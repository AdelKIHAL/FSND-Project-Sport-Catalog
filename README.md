# Udacity Full Stack Nanodegree - Project: Sport Ctalog (Item Catalog)
### Solution by Adel KIHAL

This project is part of Udacity's [Full Stack Web Developer Nanodegree](https://www.udacity.com/course/full-stack-web-developer-nanodegree--nd004)
## Project Objectives

Develop an application that provides a list of items (sports) within a variety of categories (sports' categories) as well as provide a user registration and authentication system (via google signup). Registered users will have the ability to post, edit and delete their own items.

## Project Requirements

### System
- Linux
### Programs
- python3
- sqlite3

## How to Run the Project
- Clone this repository
```
git clone https://github.com/AdelKIHAL/FSND-Project-Sport-Catalog.git
cd FSND-Project-Sport-Catalog
```
- Create a python virtual envirenment and activate it  
```bash
sudo apt install python3-pip
sudo apt-get install python3-venv
python3 -m venv udacity-nanodegree-catalog
source udacity-nanodegree-catalog/bin/activate
```
- Install the project requirements
```bash
pip install -r requirements.txt
```
- You can use the pre-existing database ```sport.dp``` or you can delete it and create a new one by
```bash
python database_setup.py
python populate_db.py
```
- Run the project
```bash
python catalog.py
```
### To use google sign in
1. Go to your [google developer console](https://www.google.com/url?sa=t&rct=j&q=&esrc=s&source=web&cd=1&cad=rja&uact=8&ved=2ahUKEwiv66G1lbnhAhUFxYUKHdZuD_sQFjAAegQIABAB&url=https%3A%2F%2Fconsole.developers.google.com%2F&usg=AOvVaw39ieEDI7pzBj4NtuzqS57M)
2. Create a new project
3. Go to credentials > create credentials >  Create OAuth client ID > Web application
4. Name your project: Sport Catalog Application
5. Set  Authorized redirect URIs to : 
  - http://localhost:5000/login 	
  -	http://localhost:5000/gconnect 	
  -	http://127.0.0.1:5000/gconnect 
6. Set  Authorized JavaScript origins to: http://localhost:5000 
7. Select Create
8. Copy the Client ID and paste it into the google-signin-client_id in templates/base.html (meta)
9. On the Dev Console Select Download JSON
10. Rename JSON file to client_secret.json
11. Run the project
```bash
python catalog.py
```

### Project Features 

1. The index page shows a list of all categories with the count of sports in each one, and the latest added sports (5)
2. Non logged users cannot edit or delete items and if they try to access to an unauthorized ressource by url ()delete sport page for example) they will be redirected to the login page
3. After login they can add Categories and Sports, they can only edit or delete their created items. If they try to access an unauthorized ressource by url, a message will be shown unstead of the ressource
4. When creating a new sport the name must be unique and it will be striped and lower case before adding it to the database (to ensure unicity)
5. The added picture if provided is resized for the thumbnail display
6. If no picture is added the program will use a placeholder picture
7. When editing a Sport, if a new picture is uploaded it will erase the old picture on the server
8. When a Category is deleted all the sports withing are moved to the Uncategorized (Non modifiable)
9. Enjoy playing with sports :)


### API

The program has only one API entry, 

<http://localhost:5000/api/JSON>

Output sample:
```json
{
  "Catalog": [
    {
      "id": 1, 
      "name": "uncategorized", 
      "sports": []
    }, 
    {
      "id": 2, 
      "name": "adventure sports", 
      "sports": [
        {
          "description": "Kayaking is the use of a kayak for moving across water. It is distinguished from canoeing by the sitting position of the paddler and the number of blades on the paddle.", 
          "id": 1, 
          "image": "/media/root/vm/Project_Catalog/static/uploads/kayaking.jpg", 
          "name": "kayaking"
        }, 
        {
          "description": "Surfing is a surface water sport in which the wave rider, referred to as a surfer, rides on the forward or deep face of a moving wave, which usually carries the surfer towards the shore.", 
          "id": 2, 
          "image": "/media/root/vm/Project_Catalog/static/uploads/surfing.jpg", 
          "name": "surfing"
        }
      ]
    }, 
    {
      "id": 3, 
      "name": "aquatic sports", 
      "sports": [
        {
          "description": "Underwater diving, as a human activity, is the practice of descending below the water's surface to interact with the environment. Immersion in water and exposure to high ambient pressure have physiological effects that limit the depths and duration possible in ambient pressure diving.", 
          "id": 4, 
          "image": "/media/root/vm/Project_Catalog/static/uploads/diving.jpg", 
          "name": "diving"
        }, 
        {
          "description": "Swimming has been a sport at every modern Summer Olympics. It has been open to women since 1912. Along with track & field athletics and gymnastics, it is one of the most popular spectator sports at the Games. Swimming has the second largest number of events.", 
          "id": 3, 
          "image": "/media/root/vm/Project_Catalog/static/uploads/olympic_swimming.jpg", 
          "name": "olympic swimming"
        }
      ]
    }, 
    {
      "id": 4, 
      "name": "strength and agility sports", 
      "sports": [
        {
          "description": "Bodybuilding is the use of progressive resistance exercise to control and develop one's musculature for aesthetic purposes. An individual who engages in this activity is referred to as a bodybuilder.", 
          "id": 5, 
          "image": "/media/root/vm/Project_Catalog/static/uploads/bodybuilding.jpg", 
          "name": "bodybuilding"
        }, 
        {
          "description": "Cycling, also called biking or bicycling, is the use of bicycles for transport, recreation, exercise or sport. People engaged in cycling are referred to as \"cyclists\", \"bikers\", or less commonly, as \"bicyclists\".", 
          "id": 6, 
          "image": "/media/root/vm/Project_Catalog/static/uploads/cycling.jpg", 
          "name": "cycling"
        }
      ]
    }, 
    {
      "id": 5, 
      "name": "ball sports", 
      "sports": [
        {
          "description": "Basketball is a team sport in which two teams, most commonly of five players each, opposing one another on a rectangular court, compete with the primary objective of shooting a basketball through the defender's hoop while preventing the opposing team from shooting through their own hoop.", 
          "id": 7, 
          "image": "/media/root/vm/Project_Catalog/static/uploads/0e296810-62c0-47c2-8141-052dd42403e2_basketball.jpg", 
          "name": "basketball"
        }
      ]
    }, 
    {
      "id": 6, 
      "name": "extreme sports", 
      "sports": [
        {
          "description": "Skateboarding is an action sport which involves riding and performing tricks using a skateboard, as well as a recreational activity, an art form, an entertainment industry job, and a method of transportation. Skateboarding has been shaped and influenced by many skateboarders throughout the years. ", 
          "id": 8, 
          "image": "/media/root/vm/Project_Catalog/static/uploads/186992b0-cb30-4868-b5da-9f28e12d63ae_skateboarding.jpg", 
          "name": "skateboarding"
        }
      ]
    }
  ]
}
```

