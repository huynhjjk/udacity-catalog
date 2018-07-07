import datetime

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Category, Base, Item, User

engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

tester = User(name="tester", email="tester@gmail.com")

snowboard = Category(name="Snowboard")
session.add(snowboard)
session.commit()

goggles = Item(
        name="Goggles",
        description="Goggles to protect your eyes!",
        category=snowboard,
        created_date=datetime.datetime.now(),
        updated_date=datetime.datetime.now(),
        user=tester)

session.add(goggles)
session.commit()

basketball = Category(name="Basketball")
session.add(basketball)
session.commit()

shoes = Item(
        name="Shoes",
        description="Shoes to play on the court!",
        category=basketball,
        created_date=datetime.datetime.now(),
        updated_date=datetime.datetime.now(),
        user=tester)

session.add(shoes)
session.commit()

baseball = Category(name="Baseball")
session.add(baseball)
session.commit()

bat = Item(
        name="Bat",
        description="Bat to play on the field!",
        category=baseball,
        created_date=datetime.datetime.now(),
        updated_date=datetime.datetime.now(),
        user=tester)

session.add(bat)
session.commit()

football = Category(name="Football")
session.add(football)
session.commit()

jersey = Item(
        name="Jersey",
        description="Jersey to wear on the field!",
        category=football,
        created_date=datetime.datetime.now(),
        updated_date=datetime.datetime.now(),
        user=tester)

session.add(jersey)
session.commit()

helmet = Item(
        name="Helmet",
        description="Helmet to protect yourself from collisions!",
        category=football,
        created_date=datetime.datetime.now(),
        updated_date=datetime.datetime.now(),
        user=tester)

session.add(helmet)
session.commit()
