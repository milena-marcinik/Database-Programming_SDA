from sqlalchemy import create_engine, Column, Integer, String, Sequence, text, func, ForeignKey, exists
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, aliased, relationship, selectinload, joinedload, contains_eager

engine = create_engine("sqlite:///:memory:", echo=False)
Base = declarative_base()
Session = sessionmaker(bind=engine)
session = Session()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, Sequence("user_id_seq"), primary_key=True)
    name = Column(String(50))
    fullname = Column(String(50))
    nickname = Column(String(50))

    addresses = relationship("Address", order_by="Address.id", back_populates="user")

    def __repr__(self):
        return f"User(id: {self.id}, name: {self.name}, fullname: {self.fullname}, nickname: {self.nickname})"


class Address(Base):
    __tablename__ = "addresses"

    id = Column(Integer, primary_key=True)
    email_address = Column(String, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"))

    user = relationship("User", back_populates="addresses")

    def __repr__(self):
        return f"Addresses (email_address={self.email_address})"


Base.metadata.create_all(engine)

andrzej = User(name="Andrzej", fullname="Andrzej Gołota", nickname="Andżej")
janusz = User(name="Janusz", fullname="Janusz Tracz", nickname="prywaciarz")
mariusz = User(name="Mariusz", fullname="Mariusz Pudzianowski", nickname="Pudzian")

session.add_all([andrzej, janusz, mariusz])
session.commit()
q = engine.execute("SELECT * FROM users;").fetchall()

jack = User(name='Jack', fullname='Jack Doe', nickname='jc123')
print(jack.addresses)
jack.addresses = [Address(email_address='jack.doe@gmail.com')]
print(jack.addresses)
print(jack.addresses[0].user)

session.add(jack)
session.commit()

new = Address(email_address='j25@yahoo.com', user_id=4)
session.add(new)
session.commit()


print("ŁADOWANIE SELEKTYWNE")
# ladowanie selektywne
# wskazanie pola relacji addresses metodzie orm,selectinload()
# wygeneruje dwa zapytania jednorazowo: pobranie użytkowika, pobranie jego adresów
jack = session.query(User).options(selectinload(User.addresses)).filter_by(name="Jack").one()
print(jack)

print("JONED LOAD")
# joined load
jack2 = session.query(User).options(joinedload(User.addresses)).filter_by(name="Jack").one()
print(jack2)

print("POLACZENIE JOIN I EAGEAR LOADING")
# wyciaganie obiektu z relacji wielu do jeden, ktory musi byc wielokrotnie odfiltrowany
jack3 = session.query(Address).join(Address.user).filter(User.name == "Jack").options(contains_eager(Address.user)).all()
print(jack3)
