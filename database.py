import sqlite3
from datetime import date
from sms_service import send_sms

DB_NAME = "adherence.db"


# ---------------- CONNECT ----------------
def connect():
    return sqlite3.connect(DB_NAME)


# ---------------- INIT DATABASE ----------------
def init_db():

    conn = connect()
    c = conn.cursor()

    # USERS
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT,
            role TEXT,
            phone_number TEXT
        )
    """)
    

    # MEDICATION LOG
    c.execute("""
        CREATE TABLE IF NOT EXISTS medication_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            med_name TEXT,
            med_time TEXT,
            date TEXT,
            dosage TEXT,
            instructions TEXT,
            status TEXT,

            UNIQUE(username, med_name, med_time, date)    
        )
    """)

    # ASSIGNED MEDICATIONS
    c.execute("""
    CREATE TABLE IF NOT EXISTS medications (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        patient_username TEXT,
        medicine_name TEXT,
        time TEXT,
        dosage TEXT,
        instructions TEXT,
              
        start_date TEXT,
        end_date TEXT,      
        start_time TEXT,
        frequency_hours INTEGER,    
                      
        purpose TEXT,
        how_to_take TEXT,
        side_effects TEXT,
        reminders TEXT,

        UNIQUE (
            patient_username,
            medicine_name,
            time
        )
    )
""")
    
    c.execute("""
        CREATE TABLE IF NOT EXISTS caregiver_assignment (
            caregiver_username TEXT UNIQUE,
            patient_username TEXT UNIQUE,
            assigned_by TEXT
        )
    """)

    # ALERT SYSTEM
    c.execute("""
        CREATE TABLE IF NOT EXISTS medication_alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            medicine_name TEXT,
            med_time TEXT,
            snooze_count INTEGER DEFAULT 0,
            missed INTEGER DEFAULT 0,
            next_alarm_time TEXT,

            UNIQUE(username, medicine_name,med_time)  
        )
    """)
    
    c.execute("""
        CREATE TABLE IF NOT EXISTS sms_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            medication TEXT,
            med_time TEXT,
            sms_type TEXT,
            sent_date TEXT,
            UNIQUE(
                username,
                medication,
                med_time,
                sms_type,
                sent_date
            )               
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS emergency_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_username TEXT,
            caregiver_username TEXT,
            provider_username TEXT,
            emergency_time TEXT,
            status TEXT
        )
    """)

    # EMERGENCY ALERTS
    c.execute("""
        CREATE TABLE IF NOT EXISTS emergency_alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_username TEXT,
            provider_username TEXT,
            emergency_time TEXT,
            status TEXT DEFAULT 'Pending'
        )
    """)
    
    conn.commit()
    conn.close()
# ---------------- USERS ----------------
def add_user(username, password, role, phone_number):

    conn = connect()
    c = conn.cursor()

    c.execute("""
        INSERT INTO users (
            username,
            password,
            role,
            phone_number
        )
        VALUES (?, ?, ?, ?)
    """, (username, password, role, phone_number))

    conn.commit()
    conn.close()


def get_user(username):

    conn = connect()
    c = conn.cursor()

    c.execute("""
        SELECT username, password, role
        FROM users
        WHERE username = ?
    """, (username,))

    user = c.fetchone()

    conn.close()

    return user


def get_patients():

    conn = connect()
    c = conn.cursor()

    c.execute("""
        SELECT username
        FROM users
        WHERE role = 'Patient'
    """)

    patients = c.fetchall()

    conn.close()

    return patients

def get_caregivers():

    conn = connect()
    c = conn.cursor()

    c.execute("""
        SELECT username
        FROM users
        WHERE role='Caregiver'
    """)

    result = c.fetchall()

    conn.close()

    return result

def assign_caregiver(caregiver, patient, physician):

    conn = connect()
    c = conn.cursor()

    # Remove caregiver assignment
    if caregiver is None:

        c.execute("""
            DELETE FROM caregiver_assignment
            WHERE patient_username = ?
        """, (patient,))

    else:

        c.execute("""
            INSERT OR REPLACE INTO caregiver_assignment
            (
                caregiver_username,
                patient_username,
                assigned_by
            )
            VALUES (?, ?, ?)
        """, (
            caregiver,
            patient,
            physician
        ))

    conn.commit()
    conn.close()

from datetime import datetime

def send_emergency(patient_username):

    conn = connect()
    c = conn.cursor()

    # Get caregiver
    c.execute("""
        SELECT caregiver_username
        FROM caregiver_assignment
        WHERE patient_username = ?
    """, (patient_username,))

    caregiver = c.fetchone()

    # Get physician
    c.execute("""
        SELECT assigned_by
        FROM caregiver_assignment
        WHERE patient_username = ?
    """, (patient_username,))

    provider = c.fetchone()

    provider_username = provider[0] if provider else None

    # Save emergency alert
    c.execute("""
        INSERT INTO emergency_alerts
        (
            patient_username,
            provider_username,
            emergency_time,
            status
        )
        VALUES (?, ?, ?, ?)
    """, (
        patient_username,
        provider_username,
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "Pending"
    ))

    conn.commit()
     
    # ================= SEND SMS =================

    patient_phone = get_user_phone(patient_username)

    caregiver_phone = get_caregiver_phone(patient_username)

    provider_phone = get_provider_phone(patient_username)

    if patient_phone:

        send_sms(
            patient_phone,
            "🚨 Emergency alert has been activated."
        )

    if caregiver_phone:

        send_sms(
            caregiver_phone,
            f"🚨 {patient_username} activated Emergency SOS."
        )

    if provider_phone:

        send_sms(
            provider_phone,
            f"🚨 Emergency alert from patient {patient_username}."
        )

    conn.close()

    return caregiver[0] if caregiver else None

def get_user_phone(username):

    conn = connect()
    c = conn.cursor()

    c.execute("""
        SELECT phone_number
        FROM users
        WHERE username=?
    """,(username,))

    result = c.fetchone()

    conn.close()

    return result[0] if result else None

def get_caregiver_phone(patient_username):

    conn = connect()
    c = conn.cursor()

    c.execute("""
        SELECT caregiver_username
        FROM caregiver_assignment
        WHERE patient_username=?
    """,(patient_username,))

    caregiver = c.fetchone()

    if not caregiver:

        conn.close()

        return None

    c.execute("""
        SELECT phone_number
        FROM users
        WHERE username=?
    """,(caregiver[0],))

    phone = c.fetchone()

    conn.close()

    return phone[0] if phone else None

def get_provider_phone(patient_username):

    conn = connect()
    c = conn.cursor()

    c.execute("""
        SELECT assigned_by
        FROM caregiver_assignment
        WHERE patient_username=?
    """,(patient_username,))

    provider = c.fetchone()

    if not provider:

        conn.close()

        return None

    c.execute("""
        SELECT phone_number
        FROM users
        WHERE username=?
    """,(provider[0],))

    phone = c.fetchone()

    conn.close()

    return phone[0] if phone else None
    
def get_healthcare_provider():

    conn = connect()
    c = conn.cursor()

    c.execute("""
        SELECT username
        FROM users
        WHERE role='Healthcare Provider'
        LIMIT 1
    """)

    result = c.fetchone()

    conn.close()

    if result:
        return result[0]

    return None


def get_assigned_caregiver(patient_username):

    conn = connect()
    c = conn.cursor()

    c.execute("""
        SELECT caregiver_username
        FROM caregiver_assignment
        WHERE patient_username = ?
    """, (patient_username,))

    result = c.fetchone()

    conn.close()

    if result:
        return result[0]

    return None

def get_phone_number(username):

    conn = connect()
    c = conn.cursor()

    c.execute("""
        SELECT phone_number
        FROM users
        WHERE username = ?
    """, (username,))

    result = c.fetchone()

    conn.close()

    if result:
        return result[0]

    return None

def get_provider_emergencies(provider_username):

    conn = connect()
    c = conn.cursor()

    c.execute("""
        SELECT
            e.patient_username,
            ca.caregiver_username,
            e.emergency_time,
            e.status
        FROM emergency_alerts e
        LEFT JOIN caregiver_assignment ca
            ON e.patient_username = ca.patient_username
        WHERE e.provider_username = ?
        ORDER BY e.emergency_time DESC
    """, (provider_username,))

    emergencies = c.fetchall()

    conn.close()

    return emergencies

def resolve_emergency(patient_username, emergency_time):

    conn = connect()
    c = conn.cursor()

    c.execute("""
        UPDATE emergency_alerts
        SET status = 'Resolved'
        WHERE patient_username = ?
        AND emergency_time = ?
    """, (
        patient_username,
        emergency_time
    ))

    conn.commit()
    conn.close()

def get_assigned_patient(caregiver):

    conn = connect()
    c = conn.cursor()

    c.execute("""
        SELECT patient_username
        FROM caregiver_assignment
        WHERE caregiver_username = ?
    """, (caregiver,))

    result = c.fetchone()

    conn.close()

    if result:
        return result[0]

    return None


# ---------------- MEDICATIONS ----------------
def add_medication(
        patient_username, 
        medicine_name, 
        time,
        start_date,
        end_date,
        start_time,
        frequency_hours, 
        dosage=None, 
        instructions=None, 
        purpose=None, 
        how_to_take=None, 
        side_effects=None, 
        reminders=None
):

    conn = connect()
    c = conn.cursor()

    c.execute("""
        INSERT OR IGNORE INTO medications (
            patient_username,
            medicine_name,
            time,
            dosage,
            instructions,  
            start_date,
            end_date,
            start_time,
            frequency_hours,     
            purpose,
            how_to_take,
            side_effects,
            reminders  
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (patient_username, medicine_name, time, dosage, instructions, start_date, end_date, start_time, frequency_hours, purpose, how_to_take, side_effects, reminders))

    conn.commit()
    conn.close()


def get_medications(patient_username):

    conn = connect()
    c = conn.cursor()

    c.execute("""
        SELECT
            medicine_name,
            time,
            dosage,
            instructions,
            start_date,
            end_date,
            start_time,
            frequency_hours,
            purpose,
            how_to_take,
            side_effects,
            reminders
        FROM medications
        WHERE patient_username = ?
    """, (patient_username,))

    meds = c.fetchall()

    conn.close()

    return meds


def delete_medication(
    patient_username,
    medicine_name,
    med_time
):

    conn = connect()
    c = conn.cursor()

    # Delete medication assignment
    c.execute("""
        DELETE FROM medications
        WHERE patient_username = ?
        AND medicine_name = ?
        AND time = ?
    """, (
        patient_username,
        medicine_name,
        med_time
    ))

    # Delete medication history
    c.execute("""
        DELETE FROM medication_log
        WHERE username = ?
        AND med_name = ?
        AND med_time = ?
    """, (
        patient_username,
        medicine_name,
        med_time
    ))

    # Delete medication alerts
    c.execute("""
        DELETE FROM medication_alerts
        WHERE username = ?
        AND medicine_name = ?
        AND med_time = ?
    """, (
        patient_username,
        medicine_name,
        med_time
    ))

    # Delete SMS logs
    c.execute("""
        DELETE FROM sms_logs
        WHERE username = ?
        AND medication = ?
        AND med_time = ?
    """, (
        patient_username,
        medicine_name,
        med_time
    ))

    conn.commit()
    conn.close()


# ---------------- MEDICATION LOGS ----------------
def mark_med_done(
    username,
    med_name,
    med_time,
    status="Taken"
):

    conn = connect()
    c = conn.cursor()

    c.execute("""
        SELECT id
        FROM medication_log
        WHERE username=?
        AND med_name=?
        AND med_time=?
        AND date=?
    """, (
        username,
        med_name,
        med_time,
        str(date.today())
    ))

    existing = c.fetchone()

    if existing:

        c.execute("""
            UPDATE medication_log
            SET status=?
            WHERE id=?
        """, (
            status,
            existing[0]
        ))

    else:

        c.execute("""
            INSERT INTO medication_log(
                username,
                med_name,
                med_time,
                date,
                dosage,
                instructions,
                status
            )
            VALUES(?,?,?,?,?,?,?)
        """, (
            username,
            med_name,
            med_time,
            str(date.today()),
            None,
            None,
            status
        ))

    conn.commit()
    conn.close()


def get_user_logs(username):

    conn = connect()
    c = conn.cursor()

    c.execute("""
        SELECT med_name, med_time, date, status
        FROM medication_log
        WHERE username = ?
        ORDER BY date DESC
    """, (username,))

    logs = c.fetchall()

    conn.close()

    return logs

# ---------------- ALERT SYSTEM ----------------
def create_alert(username, medicine_name, med_time):

    conn = connect()
    c = conn.cursor()

    c.execute("""
        SELECT id
        FROM medication_alerts
        WHERE username = ?
        AND medicine_name = ?
        AND med_time = ?
    """, (username, medicine_name, med_time))

    if c.fetchone() is None:
        c.execute("""
            INSERT INTO medication_alerts (
                username,
                medicine_name,
                med_time,
                snooze_count,
                missed
            )
            VALUES (?, ?, ?, 0, 0)
        """, (
            username,
            medicine_name,
            med_time
        ))

    conn.commit()
    conn.close()

def get_alert(
    username,
    medicine_name,
    med_time
):

    conn = connect()
    c = conn.cursor()

    c.execute("""
        SELECT snooze_count, missed
        FROM medication_alerts
        WHERE username = ?
        AND medicine_name = ?
        AND med_time = ?
    """, (
        username,
        medicine_name,
        med_time
    ))

    data = c.fetchone()

    conn.close()

    return data


def snooze_alert(
    username,
    medicine_name,
    med_time
):

    conn = connect()
    c = conn.cursor()

    c.execute("""
        UPDATE medication_alerts
        SET snooze_count = snooze_count + 1
        WHERE username = ?
        AND medicine_name = ?
        AND med_time = ?
    """, (
        username,
        medicine_name,
        med_time
    ))

    conn.commit()
    conn.close()


def mark_missed(username, medicine_name, med_time):

    conn = connect()
    c = conn.cursor()

    c.execute("""
        UPDATE medication_alerts
        SET missed = 1
        WHERE username = ?
        AND medicine_name = ?
        AND med_time = ?
    """, (
        username,
        medicine_name,
        med_time
    ))

    conn.commit()
    conn.close()

# ---------------- ALERT LOOKUP ----------------

def get_missed_alerts(username):
    conn = connect()
    c = conn.cursor()

    c.execute("""
        SELECT medicine_name, med_time
        FROM medication_alerts
        WHERE username = ?
        AND missed = 1
    """, (username,))

    alerts = c.fetchall()

    conn.close()

    return alerts


def reset_alert(
    username,
    medicine_name,
    med_time
):
    conn = connect()
    c = conn.cursor()

    c.execute("""
        DELETE FROM medication_alerts
        WHERE username = ?
        AND medicine_name = ?
        AND med_time = ?
    """, (
        username,
        medicine_name,
        med_time
    ))
    conn.commit()
    conn.close()


def get_snooze_count(username, medicine_name, med_time):
    conn = connect()
    c = conn.cursor()

    c.execute("""
        SELECT snooze_count
        FROM medication_alerts
        WHERE username = ?
        AND medicine_name = ?
        AND med_time = ?      
    """, (username, medicine_name, med_time))

    result = c.fetchone()

    conn.close()

    if result:
        return result[0]

    return 0

# ---------------- NEXT ALARM TIME ----------------

def set_next_alarm(
    username,
    medicine_name,
    med_time,
    next_time
):

    conn = connect()
    c = conn.cursor()

    c.execute("""
        UPDATE medication_alerts
        SET next_alarm_time = ?
        WHERE username = ?
        AND medicine_name = ?
        AND med_time = ?
    """, (
        next_time,
        username,
        medicine_name,
        med_time
    ))
    
    print("Rows Updated:", c.rowcount)

    conn.commit()
    conn.close()

def sms_already_sent(
    username,
    medication,
    med_time,
    sms_type
):
    conn = connect()
    c = conn.cursor()

    c.execute("""
        SELECT id
        FROM sms_logs
        WHERE username=?
        AND medication=?
        AND med_time=?
        AND sms_type=?
        AND sent_date=?
    """, (
        username,
        medication,
        med_time,
        sms_type,
        str(date.today())
    ))

    result = c.fetchone()

    conn.close()

    return result is not None

def log_sms(
    username,
    medication,
    med_time,
    sms_type
):
    conn = connect()
    c = conn.cursor()

    c.execute("""
        INSERT OR IGNORE INTO sms_logs(
            username,
            medication,
            med_time,
            sms_type,
            sent_date
        )
        VALUES (?, ?, ?, ?, ?)
    """, (
        username,
        medication,
        med_time,
        sms_type,
        str(date.today())
    ))

    conn.commit()
    conn.close()

def get_assigned_physician(patient):
    conn = connect()
    c = conn.cursor()

    c.execute("""
        SELECT assigned_by
        FROM caregiver_assignment
        WHERE patient_username = ?
    """, (patient,))

    result = c.fetchone()

    conn.close()

    return result[0] if result else None

def get_patient_caregiver(patient_username):

    conn = connect()
    c = conn.cursor()

    c.execute("""
        SELECT caregiver_username
        FROM caregiver_assignment
        WHERE patient_username = ?
    """, (patient_username,))

    result = c.fetchone()

    conn.close()

    return result[0] if result else None    

def create_emergency_alert(patient_username, provider_username):

    conn = connect()
    c = conn.cursor()

    c.execute("""
        INSERT INTO emergency_alerts
        (
            patient_username,
            provider_username,
            emergency_time,
            status
        )
        VALUES (?, ?, ?, 'Pending')
    """, (
        patient_username,
        provider_username,
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ))

    conn.commit()
    conn.close()

from datetime import datetime, timedelta

def generate_dose_schedule(start_date, end_date, start_time, frequency_hours):
    """
    Generates every medication dose between the start and end dates.
    Returns:
        [
            ("08:00 AM", datetime_object),
            ("02:00 PM", datetime_object),
            ...
        ]
    """

    schedule = []

    current = datetime.strptime(
        f"{start_date} {start_time}",
        "%Y-%m-%d %I:%M %p"
    )

    end = datetime.strptime(
        f"{end_date} 11:59 PM",
        "%Y-%m-%d %I:%M %p"
    )

    while current <= end:

        schedule.append(
            (
                current.strftime("%I:%M %p"),
                current
            )
        )

        current += timedelta(hours=frequency_hours)

    return schedule

# ==========================================
# PATIENT STATISTICS
# ==========================================

def calculate_patient_statistics(username):

    meds = get_medications(username)
    logs = get_user_logs(username)

    today = date.today()
    current_time = datetime.now()

    stats = {

        "overall_scheduled": 0,
        "today_scheduled": 0,

        "taken": 0,
        "delayed": 0,
        "missed": 0,
        "pending": 0,
        "upcoming": 0,

        "schedule": []

    }

    return stats    

def get_next_alarm(
    username,
    medicine_name,
    med_time
):

    conn = connect()
    c = conn.cursor()

    c.execute("""
        SELECT next_alarm_time
        FROM medication_alerts
        WHERE username = ?
        AND medicine_name = ?
        AND med_time = ?
    """, (
        username,
        medicine_name,
        med_time
    ))

    result = c.fetchone()

    conn.close()

    if result:
        return result[0]

    return None
    