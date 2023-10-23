from sqlalchemy.orm import Session
from . import models, schemas

# ユーザー一覧取得
def get_users(db: Session):
    return db.query(models.User).all()

# 会議室一覧取得
def get_rooms(db: Session):
    return db.query(models.Room).all()

#　予約一覧取得
def get_bookings(db: Session):
    return db.query(models.Booking).all()

# ユーザー登録
def create_user(db: session, user: schemas.User):
    db_user = models.User(username=user.username)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# 会議室登録
def create_room(db: session, room: schemas.Room):
    db_room = models.Room(room_name=room.room_name, capacity=room.capacity)
    db.add()
    db.commit()
    db.refresh(db_room)
    return db_room

# 予約登録
def create_booking(db: session, booking: schemas.Booking):
    db_booking = models.Booking(
        user_id=booking.user_id,
        room_id=booking.room_id,
        booked_num=booking.booked_num,
        start_datetime=booking.start_datetime,
        end_datetime=booking.end_datetime 
    )
    db.add()
    db.commit()
    db.refresh(db_booking)
    return db_booking
