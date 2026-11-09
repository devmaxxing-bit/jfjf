from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from . import models, schemas, database


models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title = "Banking APi")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods = ["*"]
    allow_headers=["*"]
)

@app.post("/api/users")
def create_user(user: schemas.UserCreate, db: Session = Depends(database.get_db)):
    db_user = models.User(username=user.username)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.get("/api/users/{user_id}")
def get_user(user_id: int, db: Session = Depends(database.get_db)):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@app.post("/api/deposits")
def deposit(transaction: schemas.TransactionCreate, db: Session = Depends(database.get_db)):
    db_user = db.query(models.User).filter(models.User.id == transaction.user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    db_user.balance += transaction.amount
    db_transaction = models.Transaction(user_id=transaction.user_id, type="deposit", amount=transaction.amount)
    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)
    return {"message": "Deposit successful", "new_balance": db_user.balance}

@app.post("/api/withdrawals")
def withdraw(transaction: schemas.TransactionCreate, db: Session = Depends(database.get_db)):
    db_user = db.query(models.User).filter(models.User.id == transaction.user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    if db_user.balance < transaction.amount:
        raise HTTPException(status_code=400, detail="Insufficient funds")
    db_user.balance -= transaction.amount
    db_transaction = models.Transaction(user_id=transaction.user_id, type="withdrawal", amount=transaction.amount)
    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)
    return {"message": "Withdrawal successful", "new_balance": db_user.balance}

@app.get("/api/transactions/{user_id}")
def get_transactions(user_id: int, db: Session = Depends(database.get_db)):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    transactions = db.query(models.Transaction).filter(models.Transaction.user_id == user_id).all()
    return transactions