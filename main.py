from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, Session
from sqlalchemy import Column, Integer, String
from pydantic import BaseModel

Base = declarative_base()

class AddressDB(Base):
    __tablename__ = "address"

    id = Column(Integer, primary_key=True)
    name = Column(String(255))
    email = Column(String(255))
    phone_number = Column(String(20))
    address = Column(String(255))

class AddressCreate(BaseModel):
    name: str
    email: str
    phone_number: str
    address: str

class AddressResponse(BaseModel):
    id: int
    name: str
    email: str
    phone_number: str
    address: str

engine = create_engine("sqlite:///address_database.db")

Base.metadata.create_all(engine)

app = FastAPI()

@app.get("/addresses", response_model=list[AddressResponse])
def get_addresses():
    with Session(engine) as session:
        addresses = session.query(AddressDB).all()
        return addresses

@app.post("/addresses", response_model=AddressResponse)
def create_address(address: AddressCreate):
    with Session(engine) as session:
        address_db = AddressDB(**address.dict())
        session.add(address_db)
        session.commit()
        session.refresh(address_db)
        return address_db

@app.get("/addresses/{id}", response_model=AddressResponse)
def get_address(id: int):
    with Session(engine) as session:
        address = session.query(AddressDB).get(id)
        if not address:
            raise HTTPException(status_code=404, detail="Address not found")
        return address

@app.put("/addresses/{id}", response_model=AddressResponse)
def update_address(id: int, address: AddressCreate):
    with Session(engine) as session:
        address_to_update = session.query(AddressDB).get(id)
        if not address_to_update:
            raise HTTPException(status_code=404, detail="Address not found")
        address_to_update.name = address.name
        address_to_update.email = address.email
        address_to_update.phone_number = address.phone_number
        address_to_update.address = address.address
        session.commit()
        session.refresh(address_to_update)
        return address_to_update

@app.delete("/addresses/{id}", response_model=None)
def delete_address(id: int):
    with Session(engine) as session:
        address = session.query(AddressDB).get(id)
        if not address:
            raise HTTPException(status_code=404, detail="Address not found")
        session.delete(address)
        session.commit()
    return JSONResponse(status_code=204, content={"message": "Address deleted"})
