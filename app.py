import streamlit as st
import datetime
import requests
import json
import pandas as pd

page = st.sidebar.selectbox("Choose your page", ["ユーザー登録", "会議室登録", "予約登録", "登録取り消し", "登録情報更新"])

if page == "ユーザー登録":
    st.title("ユーザー登録画面")
    with st.form(key="user"):
        # user_id: int = random.randint(0, 10)
        username: str = st.text_input("ユーザー名", max_chars=12)
        data = {
            "username": username
        }
        submit_button = st.form_submit_button(label="ユーザー登録")

    if submit_button:
        url = "http://127.0.0.1:8000/users"
        res = requests.post(
            url,
            data=json.dumps(data)
        )
        if res.status_code == 200:
            st.success("ユーザー登録完了")

elif page == "会議室登録":
    st.title("会議室登録画面")

    with st.form(key="room"):
        # room_id: int = random.randint(0, 10)
        room_name: str = st.text_input("会議室名", max_chars=12)
        capacity: int = st.number_input("定員", step=1)
        data = {
            # "room_id": room_id,
            "room_name": room_name,
            "capacity": capacity
        }
        submit_button = st.form_submit_button(label="会議室登録")

    if submit_button:
        url = "http://127.0.0.1:8000/rooms"
        res = requests.post(
            url,
            data=json.dumps(data)
        )
        if res.status_code == 200:
            st.success("会議室登録完了")

elif page == "予約登録":
    st.title("会議室予約画面")
    # ユーザー一覧取得
    url_users = "http://127.0.0.1:8000/users"
    res = requests.get(url_users)
    users = res.json()

    # ユーザー名をキー、ユーザーIDをバリュー
    users_name = {}
    for user in users:
        users_name[user["username"]] = user["user_id"]
    

    #会議室一覧の取得
    url_rooms = "http://127.0.0.1:8000/rooms"
    res = requests.get(url_rooms)
    rooms = res.json()
    rooms_name = {}
    for room in rooms:
        rooms_name[room["room_name"]] = {
            "room_id": room["room_id"],
            "capacity": room["capacity"]
        }

    st.write(" ### 会議室一覧")
    df_rooms = pd.DataFrame(rooms)
    df_rooms.columns = ["会議室名", "定員", "会議室ID"]
    st.table(df_rooms)

    #予約一覧の取得
    url_bookings = "http://127.0.0.1:8000/bookings"
    res = requests.get(url_bookings)
    bookings = res.json()
    df_bookings = pd.DataFrame(bookings)

    #ユーザー一覧の表示
    users_id = {}
    for user in users:
        users_id[user["user_id"]] = user["username"]

    #会議室一覧の表示
    rooms_id = {}
    for room in rooms:
        rooms_id[room["room_id"]] = {
            "room_name": room["room_name"],
            "capacity": room["capacity"]
        }

    #IDを各値に変更
    to_username = lambda x: users_id[x]
    to_room_name = lambda x: rooms_id[x]["room_name"]
    to_datetime = lambda x: datetime.datetime.fromisoformat(x).strftime("%Y/%M/%d %H:%M")


    #特定の列に適用
    df_bookings["user_id"] = df_bookings["user_id"].map(to_username)
    df_bookings["room_id"] = df_bookings["room_id"].map(to_room_name)
    df_bookings["start_datetime"] = df_bookings["start_datetime"].map(to_datetime)
    df_bookings["end_datetime"] = df_bookings["end_datetime"].map(to_datetime)
    df_bookings = df_bookings.rename(columns={
        "user_id": "予約者名",
        "room_id": "会議室名",
        "booked_num": "予約人数",
        "start_datetime": "開始時刻",
        "end_datetime": "終了時刻",
        "booking_id": "予約番号"
    })
    
    st.write("###  予約一覧")
    st.table(df_bookings)

    with st.form(key="booking"):
        # booking_id: int = random.randint(0, 10)
        username: str = st.selectbox("予約者名", users_name.keys())
        room_name: str = st.selectbox("会議室名", rooms_name.keys())
        booked_num: int = st.number_input("予約人数", step=1, min_value=1)
        date = st.date_input("日付を入力", min_value=datetime.date.today())
        start_time = st.time_input("日付時刻: ", value=datetime.time(hour=9, minute=0))
        end_time = st.time_input("終了時刻: ", value=datetime.time(hour=20, minute=0))
        submit_button = st.form_submit_button(label="予約登録")

    if submit_button:
        user_id: int = users_name[username]
        room_id: int = rooms_name[room_name]["room_id"]
        capacity: int = rooms_name[room_name]["capacity"]

        data = {
            "user_id": user_id,
            "room_id": room_id,
            "booked_num": booked_num,
            "start_datetime": datetime.datetime(
                year=date.year,
                month=date.month,
                day=date.day,
                hour=start_time.hour,
                minute=start_time.minute
            ).isoformat(),
            "end_datetime": datetime.datetime(
                year=date.year,
                month=date.month,
                day=date.day,
                hour=end_time.hour,
                minute=end_time.minute
            ).isoformat()
        }

        # 定員以上の予約人数の場合
        if booked_num > capacity:
            st.error(f"{room_name}の定員は、{capacity}名です。{capacity}名以下の予約人数のみ受け付けます。")
        # 開始時刻より終了時奥の方が多い場合   
        elif start_time >= end_time:
            st.error("開始時刻が終了時刻を超えています。") 
        #開始時刻(9時)~終了時刻(20時)の間に収まっていない場合
        elif start_time < datetime.time(hour=9, minute=0, second=0) or end_time > datetime.time(hour=20, minute=0, second=0):
            st.error("利用時間は9:00~20:00になります。")
        else:
            # 会議室の予約
            url = "http://127.0.0.1:8000/bookings"
            res = requests.post(
                url,
                data=json.dumps(data)
            )
            if res.status_code == 200:
                st.success("予約完了しました")
            elif res.status_code == 404 and res.json()["detail"] == "Already booked":
                st.error("指定の時間にはすでに予約が入っています")

elif page == "登録取り消し":
    st.title("ユーザー取り消し")
    # ユーザー一覧取得
    url_users = "http://127.0.0.1:8000/users"
    res = requests.get(url_users)
    users = res.json()
    # ユーザー名をキー、ユーザーIDをバリュー
    users_name = {}
    for user in users:
        users_name[user["username"]] = user["user_id"]
        
    with st.form(key="usersfrom"):
        username: str = st.selectbox("予約者名", users_name.keys())
        user_delete_button = st.form_submit_button(label="ユーザー取り消し")

    if user_delete_button:
        user_id: int = users_name[username]
        print(user_id)
        url_user_delete = f"http://127.0.0.1:8000/users/{user_id}"
        res = requests.delete(
            url_user_delete
        )
        if res.status_code == 200:
            st.success("ユーザー取り消し完了")
        elif res.status_code == 404 or res.status_code == 422:
            st.error("取り消しに失敗しました。")

    # 会議室一覧取得
    url_rooms = "http://127.0.0.1:8000/rooms"
    res = requests.get(url_rooms)
    rooms = res.json()
        # ユーザー名をキー、ユーザーIDをバリュー
    rooms_name = {}
    for room in rooms:
        rooms_name[room["room_name"]] = room["room_id"]
        
    with st.form(key="roomsfrom"):
        room_name: str = st.selectbox("会議室名", rooms_name.keys())
        room_delete_button = st.form_submit_button(label="会議室取り消し")


    if room_delete_button:
        room_id: int = rooms_name[room_name]
        print(room_id)
        url_room_delete = f"http://127.0.0.1:8000/rooms/{room_id}"
        res = requests.delete(
            url_room_delete
        )
        if res.status_code == 200:
            st.success("会議室取り消し完了")
        elif res.status_code == 404 or res.status_code == 422:
            st.error("取り消しに失敗しました。")

elif page == "登録情報更新":
    st.title("ユーザー情報更新")
