import streamlit as st
from supabase import create_client


SUPABASE_URL = st.secrets["SUPABASE_URL"]

SUPABASE_KEY = st.secrets["SUPABASE_KEY"]


supabase = create_client(
    SUPABASE_URL,
    SUPABASE_KEY
)

from datetime import date
from sms_service import send_sms



# ---------------- INIT DATABASE ----------------
def init_db():
    # Tables are already managed by Supabase.
    pass
# ---------------- USERS ----------------
def add_user(username, password, role, phone_number):

    result = (
        supabase.table("users")
        .insert({
            "username": username,
            "password": password,
            "role": role,
            "phone_number": phone_number
        })
        .execute()
    )

    return result


def get_user(username):

    result = (
        supabase
        .table("users")
        .select("username,password,role")
        .eq("username", username)
        .execute()
    )

    if result.data:

        user = result.data[0]

        return (
            user["username"],
            user["password"],
            user["role"]
        )

    return None


def get_patients():

    result = (
        supabase
        .table("users")
        .select("username")
        .eq("role", "Patient")
        .execute()
    )

    return [(r["username"],) for r in result.data]

def get_caregivers():

    result = (
        supabase
        .table("users")
        .select("username")
        .eq("role", "Caregiver")
        .execute()
    )

    return [(r["username"],) for r in result.data]

def assign_caregiver(caregiver, patient, physician):

    if caregiver is None:

        supabase.table("caregiver_assignment").delete().eq(
            "patient_username",
            patient
        ).execute()

    else:

        # Delete old assignment first
        supabase.table("caregiver_assignment").delete().eq(
            "patient_username",
            patient
        ).execute()

        # Insert new assignment
        supabase.table("caregiver_assignment").insert({

            "caregiver_username": caregiver,
            "patient_username": patient,
            "assigned_by": physician

        }).execute()

from datetime import datetime

def send_emergency(patient_username):

    caregiver = get_patient_caregiver(patient_username)

    provider_username = get_assigned_physician(patient_username)

    supabase.table("emergency_alerts").insert({

        "patient_username": patient_username,
        "provider_username": provider_username,
        "emergency_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "status": "Pending"

    }).execute()

    # ---------- SMS ----------

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

    return caregiver

def get_user_phone(username):

    result = (
        supabase
        .table("users")
        .select("phone_number")
        .eq("username", username)
        .execute()
    )

    if result.data:

        return result.data[0]["phone_number"]

    return None

def get_caregiver_phone(patient_username):

    caregiver = get_patient_caregiver(patient_username)

    if caregiver is None:

        return None

    return get_user_phone(caregiver)

def get_provider_phone(patient_username):

    provider = get_assigned_physician(patient_username)

    if provider is None:

        return None

    return get_user_phone(provider)
    
def get_healthcare_provider():

    result = (
        supabase
        .table("users")
        .select("username")
        .eq("role", "Healthcare Provider")
        .limit(1)
        .execute()
    )

    if result.data:

        return result.data[0]["username"]

    return None


def get_assigned_caregiver(patient_username):

    return get_patient_caregiver(patient_username)

def get_phone_number(username):

    return get_user_phone(username)

def get_patient_emergency_alerts(patient_username):

    result = (
        supabase
        .table("emergency_alerts")
        .select(
            "patient_username, emergency_time, status"
        )
        .eq(
            "patient_username",
            patient_username
        )
        .order(
            "emergency_time",
            desc=True
        )
        .execute()
    )


    return result.data

def get_provider_emergencies(provider_username):

    emergency_result = (
        supabase
        .table("emergency_alerts")
        .select("*")
        .eq("provider_username", provider_username)
        .order("emergency_time", desc=True)
        .execute()
    )

    emergencies = []

    for alert in emergency_result.data:

        caregiver_result = (
            supabase
            .table("caregiver_assignment")
            .select("caregiver_username")
            .eq("patient_username", alert["patient_username"])
            .execute()
        )

        caregiver = None

        if caregiver_result.data:
            caregiver = caregiver_result.data[0]["caregiver_username"]

        emergencies.append((
            alert["patient_username"],
            caregiver,
            alert["emergency_time"],
            alert["status"]
        ))

    return emergencies

def get_caregiver_emergencies(caregiver_username):

    # Get assigned patient
    patient_result = (
        supabase
        .table("caregiver_assignment")
        .select("patient_username")
        .eq(
            "caregiver_username",
            caregiver_username
        )
        .execute()
    )


    if not patient_result.data:

        return []


    patient_username = patient_result.data[0]["patient_username"]


    # Get emergency alerts of that patient
    emergency_result = (
        supabase
        .table("emergency_alerts")
        .select("*")
        .eq(
            "patient_username",
            patient_username
        )
        .order(
            "emergency_time",
            desc=True
        )
        .execute()
    )


    emergencies = []


    for alert in emergency_result.data:

        emergencies.append(
        {
            "id": alert["id"],
            "patient_username": alert["patient_username"],
            "emergency_time": alert["emergency_time"],
            "status": alert["status"]
        }
        )


    return emergencies

def get_user_snoozes(username):

    result = (
        supabase
        .table("medication_alerts")
        .select(
            "medicine_name, med_time, next_alarm_time"
        )
        .eq(
            "username",
            username
        )
        .execute()
    )


    return result.data    

def resolve_emergency(
    patient_username,
    emergency_time
):

    supabase.table("emergency_alerts").update({

        "status": "Resolved"

    }).eq(

        "patient_username",
        patient_username

    ).eq(

        "emergency_time",
        emergency_time

    ).execute()
    
def get_assigned_patient(caregiver):

    result = (
        supabase
        .table("caregiver_assignment")
        .select("patient_username")
        .eq("caregiver_username", caregiver)
        .execute()
    )

    if result.data:
        return result.data[0]["patient_username"]

    return None

def calculate_treatment_adherence(username):

    medicines = get_medications(username)
    logs = get_user_logs(username)

    current_time = datetime.now()

    overall_total = 0
    completed = 0


    for (
        med,
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
    ) in medicines:


        if frequency_hours:

            dose_schedule = generate_dose_schedule(
                start_date,
                end_date,
                start_time,
                frequency_hours
            )

        else:

            dose_schedule = [
                (
                    time,
                    datetime.strptime(
                        f"{start_date} {time}",
                        "%Y-%m-%d %I:%M %p"
                    )
                )
            ]


        for dose_time, dose_datetime in dose_schedule:


            if dose_datetime > current_time:

                continue


            overall_total += 1


            log_found = next(
                (
                    l for l in logs
                    if l[0] == med
                    and l[1] == dose_time
                    and l[2] == str(dose_datetime.date())
                ),
                None
            )


            if log_found and log_found[3] in [
                "Taken",
                "Delayed"
            ]:

                completed += 1



    if overall_total == 0:

        return 0


    return round(
        (completed / overall_total) * 100
    )


def calculate_today_adherence(username):

    medicines = get_medications(username)
    logs = get_user_logs(username)

    today = date.today()

    today_total = 0
    today_taken = 0


    for (
        med,
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
    ) in medicines:


        if frequency_hours:

            dose_schedule = generate_dose_schedule(
                start_date,
                end_date,
                start_time,
                frequency_hours
            )

        else:

            dose_schedule = [
                (
                    time,
                    datetime.strptime(
                        f"{start_date} {time}",
                        "%Y-%m-%d %I:%M %p"
                    )
                )
            ]


        for dose_time, dose_datetime in dose_schedule:


            if dose_datetime.date() != today:

                continue


            today_total += 1


            log_found = next(
                (
                    l for l in logs
                    if l[0] == med
                    and l[1] == dose_time
                    and l[2] == str(today)
                ),
                None
            )


            if log_found and log_found[3] in [
                "Taken",
                "Delayed"
            ]:

                today_taken += 1



    if today_total == 0:

        return 0


    return round(
        (today_taken / today_total) * 100
    )
    


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

    result = supabase.table("medications").insert({

        "patient_username": patient_username,
        "medicine_name": medicine_name,
        "time": time,
        "dosage": dosage,
        "instructions": instructions,
        "start_date": start_date,
        "end_date": end_date,
        "start_time": start_time,
        "frequency_hours": frequency_hours,
        "purpose": purpose,
        "how_to_take": how_to_take,
        "side_effects": side_effects,
        "reminders": reminders

    }).execute()

    return result


def get_medications(username):

    result = (
        supabase
        .table("medications")
        .select("*")
        .eq("patient_username", username)
        .execute()
    )

    meds = []

    for row in result.data:

        meds.append(

            (
                row["medicine_name"],
                row["time"],
                row["dosage"],
                row["instructions"],
                row["start_date"],
                row["end_date"],
                row["start_time"],
                row["frequency_hours"],
                row["purpose"],
                row["how_to_take"],
                row["side_effects"],
                row["reminders"]
            )

        )

    return meds

def resolve_missed_medication(
    username,
    med_name,
    med_time,
    med_date
):

    # Do NOT modify medication_log status
    # Missed must remain Missed

    return True


def create_missed_alert(
    username,
    med_name,
    med_time,
    med_date
):

    existing = (
        supabase
        .table("missed_alerts")
        .select("*")
        .eq("username", username)
        .eq("med_name", med_name)
        .eq("med_time", med_time)
        .eq("date", str(med_date))
        .execute()
    )


    if existing.data:
        return


    supabase.table(
        "missed_alerts"
    ).insert({

        "username": username,
        "med_name": med_name,
        "med_time": med_time,
        "date": str(med_date),
        "alert_status": "Pending"

    }).execute()

def get_pending_missed_alerts(username):

    result = (
        supabase
        .table("missed_alerts")
        .select("*")
        .eq(
            "username",
            username
        )
        .eq(
            "alert_status",
            "Pending"
        )
        .execute()
    )

    return result.data

def acknowledge_missed_alert(alert_id):

    supabase.table(
        "missed_alerts"
    ).update({

        "alert_status": "Acknowledged"

    }).eq(
        "id",
        alert_id
    ).execute()        

def delete_medication(
    patient_username,
    medicine_name,
    med_time
):
    # Delete medication assignment
    supabase.table("medications") \
        .delete() \
        .eq("patient_username", patient_username) \
        .eq("medicine_name", medicine_name) \
        .eq("time", med_time) \
        .execute()

    # Delete medication history
    supabase.table("medication_log") \
        .delete() \
        .eq("username", patient_username) \
        .eq("med_name", medicine_name) \
        .eq("med_time", med_time) \
        .execute()

    # Delete medication alerts
    supabase.table("medication_alerts") \
        .delete() \
        .eq("username", patient_username) \
        .eq("medicine_name", medicine_name) \
        .eq("med_time", med_time) \
        .execute()

    # Delete SMS logs
    supabase.table("sms_logs") \
        .delete() \
        .eq("username", patient_username) \
        .eq("medication", medicine_name) \
        .eq("med_time", med_time) \
        .execute()


# ---------------- MEDICATION LOGS ----------------
def mark_med_done(
    username,
    med_name,
    med_time,
    status="Taken"
):

    # Check if today's log already exists
    result = (
        supabase
        .table("medication_log")
        .select("id")
        .eq("username", username)
        .eq("med_name", med_name)
        .eq("med_time", med_time)
        .eq("date", str(date.today()))
        .execute()
    )

    if result.data:

        # Update existing record
        supabase.table("medication_log").update({

            "status": status

        }).eq(
            "id",
            result.data[0]["id"]
        ).execute()

    else:

        # Insert new record
        supabase.table("medication_log").insert({

            "username": username,
            "med_name": med_name,
            "med_time": med_time,
            "date": str(date.today()),
            "dosage": None,
            "instructions": None,
            "status": status

        }).execute()

def get_user_logs(username):

    result = (
        supabase
        .table("medication_log")
        .select("*")
        .eq("username", username)
        .order("date", desc=True)
        .execute()
    )

    logs = []

    for row in result.data:

        logs.append(

            (
                row["med_name"],
                row["med_time"],
                row["date"],
                row["status"]
            )

        )

    return logs

# ---------------- ALERT SYSTEM ----------------
def create_alert(
    username,
    medicine_name,
    med_time
):

    result = (
        supabase
        .table("medication_alerts")
        .select("id")
        .eq("username", username)
        .eq("medicine_name", medicine_name)
        .eq("med_time", med_time)
        .execute()
    )

    if not result.data:

        supabase.table("medication_alerts").insert({

            "username": username,
            "medicine_name": medicine_name,
            "med_time": med_time,
            "snooze_count": 0,
            "missed": 0

        }).execute()

def get_alert(
    username,
    medicine_name,
    med_time
):

    result = (
        supabase
        .table("medication_alerts")
        .select("snooze_count,missed")
        .eq("username", username)
        .eq("medicine_name", medicine_name)
        .eq("med_time", med_time)
        .execute()
    )

    if result.data:

        row = result.data[0]

        return (
            row["snooze_count"],
            row["missed"]
        )

    return None

def snooze_alert(
    username,
    medicine_name,
    med_time
):

    result = (
        supabase
        .table("medication_alerts")
        .select("snooze_count")
        .eq("username", username)
        .eq("medicine_name", medicine_name)
        .eq("med_time", med_time)
        .execute()
    )

    if result.data:

        current = result.data[0]["snooze_count"]

        supabase.table("medication_alerts").update({

            "snooze_count": current + 1

        }).eq(
            "username", username
        ).eq(
            "medicine_name", medicine_name
        ).eq(
            "med_time", med_time
        ).execute()


def mark_missed(
    username,
    medicine_name,
    med_time
):

    supabase.table("medication_alerts").update({

        "missed": 1

    }).eq(
        "username", username
    ).eq(
        "medicine_name", medicine_name
    ).eq(
        "med_time", med_time
    ).execute()

def add_missed_log(
    username,
    med_name,
    med_time,
    missed_date
):

    try:

        supabase.table("medication_log").insert({

            "username": username,
            "med_name": med_name,
            "med_time": med_time,
            "date": str(missed_date),
            "status": "Missed"

        }).execute()

    except:

        pass
# ---------------- ALERT LOOKUP ----------------

def get_missed_alerts(username):

    result = (
        supabase
        .table("medication_alerts")
        .select("medicine_name,med_time")
        .eq("username", username)
        .eq("missed", 1)
        .execute()
    )

    alerts = []

    for row in result.data:

        alerts.append(

            (
                row["medicine_name"],
                row["med_time"]
            )

        )

    return alerts


def reset_alert(
    username,
    medicine_name,
    med_time
):

    supabase.table("medication_alerts").delete().eq(

        "username", username

    ).eq(

        "medicine_name", medicine_name

    ).eq(

        "med_time", med_time

    ).execute()


def get_snooze_count(
    username,
    medicine_name,
    med_time
):

    result = (
        supabase
        .table("medication_alerts")
        .select("snooze_count")
        .eq("username", username)
        .eq("medicine_name", medicine_name)
        .eq("med_time", med_time)
        .execute()
    )

    if result.data:

        return result.data[0]["snooze_count"]

    return 0

# ---------------- NEXT ALARM TIME ----------------

def set_next_alarm(
    username,
    medicine_name,
    med_time,
    next_time
):

    supabase.table("medication_alerts").update({

        "next_alarm_time": next_time

    }).eq(

        "username", username

    ).eq(

        "medicine_name", medicine_name

    ).eq(

        "med_time", med_time

    ).execute()

def sms_already_sent(
    username,
    medication,
    med_time,
    sms_type
):

    result = (
        supabase
        .table("sms_logs")
        .select("id")
        .eq("username", username)
        .eq("medication", medication)
        .eq("med_time", med_time)
        .eq("sms_type", sms_type)
        .eq("sent_date", str(date.today()))
        .execute()
    )

    return len(result.data) > 0

def log_sms(
    username,
    medication,
    med_time,
    sms_type
):

    if not sms_already_sent(
        username,
        medication,
        med_time,
        sms_type
    ):

        supabase.table("sms_logs").insert({

            "username": username,
            "medication": medication,
            "med_time": med_time,
            "sms_type": sms_type,
            "sent_date": str(date.today())

        }).execute()

def get_assigned_physician(patient):

    result = (
        supabase
        .table("caregiver_assignment")
        .select("assigned_by")
        .eq("patient_username", patient)
        .execute()
    )

    if result.data:

        return result.data[0]["assigned_by"]

    return None

def get_patient_caregiver(patient_username):

    result = (
        supabase
        .table("caregiver_assignment")
        .select("caregiver_username")
        .eq("patient_username", patient_username)
        .execute()
    )

    if result.data:

        return result.data[0]["caregiver_username"]

    return None   

def create_emergency_alert(
    patient_username,
    provider_username
):

    supabase.table("emergency_alerts").insert({

        "patient_username": patient_username,
        "provider_username": provider_username,
        "emergency_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "status": "Pending"

    }).execute()

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

def calculate_adherence_summary(username):

    meds = get_medications(username)

    logs = get_user_logs(username)


    today = date.today()

    current_time = datetime.now()


    # ==========================
    # TODAY COUNTERS
    # ==========================

    today_total = 0

    today_taken = 0

    today_delayed = 0

    today_missed = 0

    today_pending = 0



    # ==========================
    # OVERALL COUNTERS
    # ==========================

    overall_total = 0

    overall_taken = 0

    overall_delayed = 0

    overall_missed = 0



    for med in meds:


        (
            med_name,
            med_time,
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

        ) = med



        # Generate medication schedule

        if frequency_hours:


            dose_schedule = generate_dose_schedule(
                start_date,
                end_date,
                start_time,
                frequency_hours
            )


        else:


            dose_schedule = [

                (
                    med_time,

                    datetime.strptime(
                        f"{start_date} {med_time}",
                        "%Y-%m-%d %I:%M %p"
                    )

                )

            ]



        for dose_time, dose_datetime in dose_schedule:



            # Ignore doses outside treatment period

            if dose_datetime.date() > today:

                continue



            # ==========================
            # FIND MEDICATION LOG
            # ==========================


            log_found = next(

                (

                    log for log in logs

                    if log[0] == med_name

                    and log[1] == dose_time

                    and log[2] == str(dose_datetime.date())

                ),

                None

            )



            # ==========================
            # OVERALL ADHERENCE
            # ==========================


            overall_total += 1



            if log_found:


                if log_found[3] == "Taken":

                    overall_taken += 1



                elif log_found[3] == "Delayed":

                    overall_delayed += 1



                elif log_found[3] in [
                    "Missed",
                    "Missed Reviewed"
                ]:

                    overall_missed += 1



            else:


                if current_time > dose_datetime + timedelta(minutes=30):

                    overall_missed += 1



            # ==========================
            # TODAY ONLY
            # ==========================


            if dose_datetime.date() != today:

                continue



            today_total += 1



            if log_found:


                if log_found[3] == "Taken":

                    today_taken += 1



                elif log_found[3] == "Delayed":

                    today_delayed += 1



                elif log_found[3] in [
                    "Missed",
                    "Missed Reviewed"
                ]:

                    today_missed += 1



            else:


                if current_time > dose_datetime + timedelta(minutes=30):

                    today_missed += 1



                else:

                    today_pending += 1



    # ==========================
    # ADHERENCE CALCULATION
    # ==========================


    if overall_total > 0:

        overall_adherence = round(
            (
                (overall_taken + overall_delayed)
                /
                overall_total
            )
            * 100
        )

    else:

        overall_adherence = 0



    if today_total > 0:

        today_adherence = round(
            (
                (today_taken + today_delayed)
                /
                today_total
            )
            * 100
        )

    else:

        today_adherence = 0



    return {


        # TODAY

        "today_total": today_total,

        "today_taken": today_taken,

        "today_delayed": today_delayed,

        "today_missed": today_missed,

        "today_pending": today_pending,

        "today_adherence": today_adherence,



        # OVERALL

        "overall_total": overall_total,

        "overall_taken": overall_taken,

        "overall_delayed": overall_delayed,

        "overall_missed": overall_missed,

        "overall_adherence": overall_adherence

    }

def acknowledge_emergency(alert_id):

    result = (
        supabase
        .table("emergency_alerts")
        .update({
            "status": "Acknowledged"
        })
        .eq(
            "id",
            alert_id
        )
        .execute()
    )

    return result

def get_next_alarm(
    username,
    medicine_name,
    med_time
):

    result = (
        supabase
        .table("medication_alerts")
        .select("next_alarm_time")
        .eq("username", username)
        .eq("medicine_name", medicine_name)
        .eq("med_time", med_time)
        .execute()
    )

    if result.data:

        return result.data[0]["next_alarm_time"]

    return None
    