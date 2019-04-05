from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Category, Base, Sport, User

engine = create_engine('sqlite:///sports.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

"""
Infromation
source of sports and  categories :
https://www.lingokids.com/english-for-kids/list-of-sports
Sports description: wikipedia
dummy user :https://randomuser.me/
"""

# Dummy user
User1 = User(name="joel alvarez", email="joel.alvarez20@example.com",
             picture='https://randomuser.me/api/portraits/men/81.jpg')
session.add(User1)
session.commit()

# Uncategorized Sports Category
category0 = Category(user_id=1, name="Uncategorized")
session.add(category0)
session.commit()

# Adventure Sports Category
category1 = Category(user_id=1, name="Adventure Sports")
session.add(category1)
session.commit()

sport1 = Sport(user_id=1,
               name='kayaking',
               description='Kayaking is the use of a kayak for moving across water. It is distinguished from canoeing by the sitting position of the paddler and the number of blades on the paddle.',
               image='kayaking.jpg',
               category=category1)
session.add(sport1)
session.commit()

sport2 = Sport(user_id=1,
               name='surfing',
               description='Surfing is a surface water sport in which the wave rider, referred to as a surfer, rides on the forward or deep face of a moving wave, which usually carries the surfer towards the shore.',
               image='surfing.jpg',
               category=category1)
session.add(sport2)
session.commit()

# Aquatic Sports Category
category2 = Category(user_id=1, name="Aquatic Sports")
session.add(category2)
session.commit()

sport1 = Sport(user_id=1,
               name='olympic swimming',
               description='Swimming has been a sport at every modern Summer Olympics. It has been open to women since 1912. Along with track & field athletics and gymnastics, it is one of the most popular spectator sports at the Games. Swimming has the second largest number of events.',
               image='olympic_swimming.jpg', category=category2)
session.add(sport1)
session.commit()

sport2 = Sport(user_id=1,
               name='diving',
               description="Underwater diving, as a human activity, is the practice of descending below the water's surface to interact with the environment. Immersion in water and exposure to high ambient pressure have physiological effects that limit the depths and duration possible in ambient pressure diving.",
               image='diving.jpg',
               category=category2)
session.add(sport2)
session.commit()

# Strength and Agility Sports Category
category3 = Category(user_id=1, name="Strength and Agility Sports")
session.add(category3)
session.commit()

sport1 = Sport(user_id=1,
               name='bodybuilding',
               description="Bodybuilding is the use of progressive resistance exercise to control and develop one's musculature for aesthetic purposes. An individual who engages in this activity is referred to as a bodybuilder.",
               image='bodybuilding.jpg',
               category=category3)
session.add(sport1)
session.commit()

sport2 = Sport(user_id=1,
               name='cycling',
               description='Cycling, also called biking or bicycling, is the use of bicycles for transport, recreation, exercise or sport. People engaged in cycling are referred to as "cyclists", "bikers", or less commonly, as "bicyclists".',
               image='cycling.jpg',
               category=category3)
session.add(sport2)
session.commit()

print("database succesfully populated")
