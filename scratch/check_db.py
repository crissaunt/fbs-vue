import psycopg2

db_url = "postgresql://flight_database_crfm_user:te6dBBjm8S0RecQkQIk2TMLWPuK9YCgW@dpg-d8123ajeo5us7380tncg-a.oregon-postgres.render.com/flight_database_crfm"

try:
    conn = psycopg2.connect(db_url)
    cursor = conn.cursor()
    
    # Check if instructor1 exists
    cursor.execute("SELECT id, username FROM auth_user WHERE username = 'instructor1';")
    user = cursor.fetchone()
    
    if user:
        print(f"User found: {user}")
        
        # Check UserProfile
        cursor.execute("SELECT id, role FROM app_userprofile WHERE user_id = %s;", (user[0],))
        profile = cursor.fetchone()
        if profile:
            print(f"UserProfile found: {profile}")
        else:
            print("ERROR: No UserProfile found for this user!")
            
    else:
        print("User 'instructor1' not found in database!")
        
    conn.close()
except Exception as e:
    print(f"Connection failed: {e}")
