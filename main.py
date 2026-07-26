import pandas as pd
import streamlit as st
import time
import base64
from sms_service import send_sms
from datetime import date, datetime, timedelta
from plyer import notification
from streamlit_autorefresh import st_autorefresh

from database import (
    init_db,
    add_user,
    get_user,
    mark_med_done,
    get_user_logs,
    add_medication,
    get_medications,
    delete_medication,
    create_alert,
    get_alert,
    snooze_alert,
    mark_missed,
    reset_alert,
    set_next_alarm,
    get_patients,
    get_caregivers,
    assign_caregiver,
    get_assigned_patient,
    get_phone_number,
    get_assigned_caregiver,
    sms_already_sent,
    get_assigned_physician,
    send_emergency,
    get_provider_emergencies,
    resolve_emergency,
    get_caregiver_emergencies,
    log_sms,
    calculate_today_adherence,
    calculate_treatment_adherence,
    get_patient_caregiver,
    get_user_phone,
    get_caregiver_phone,
    get_provider_phone,
    generate_dose_schedule,
    add_missed_log,
    get_user_snoozes,
    get_next_alarm,
    create_missed_alert,
    get_pending_missed_alerts,
    acknowledge_missed_alert,
    get_patient_emergency_alerts,
    acknowledge_emergency,
    calculate_adherence_summary

)
st.set_page_config(
    page_title="A.N.I.M.O.",
    page_icon="💊",
    layout="wide"
)

st.markdown("""
<style>

/* Main background */
.stApp {
    background-color: #F5FAF8;
}

/* Headers */
h1, h2, h3 {
    color: #0F766E;
}

/* Buttons */
.stButton > button {
    background-color: #14B8A6;
    color: white;
    border-radius: 10px;
    border: none;
    font-weight: bold;
    width: 100%;
}

.stButton > button:hover {
    background-color: #0F766E;
    color: white;
}

/* Text Inputs */
.stTextInput input {
    border-radius: 8px;
}

/* Select Boxes */
.stSelectbox {
    border-radius: 8px;
}

/* Metric cards */
[data-testid="stMetric"] {
    background-color: white;
    padding: 15px;
    border-radius: 12px;
    box-shadow: 0px 2px 5px rgba(0,0,0,0.1);
}

</style>
""", unsafe_allow_html=True)


init_db()

# ---------------- SESSION STATE ----------------
if "current_user" not in st.session_state:
    st.session_state.current_user = None

if "page" not in st.session_state:
    st.session_state.page = "role"

if "show_splash" not in st.session_state:
    st.session_state.show_splash = True

if "role" not in st.session_state:
    st.session_state.role = None

if "notified_meds" not in st.session_state:
    st.session_state.notified_meds = []
# ---------------- ROLE SCREEN ----------------
def get_base64_image(image_path):

    with open(image_path, "rb") as image_file:
        encoded = base64.b64encode(
            image_file.read()
        ).decode()

    return encoded

def splash_screen():

    st.markdown("""
    <style>

    .block-container {
        padding-top: 0rem !important;
        padding-bottom: 0rem !important;
    }

    header {
        visibility: hidden;
    }

    footer {
        visibility: hidden;
    }

    </style>
    """, unsafe_allow_html=True)

    # Center logo
    col1, col2, col3 = st.columns([1.2,1,1.2])

    with col2:
        st.image("assets/logo.png", width=280)

    st.markdown(
        "<h1 style='text-align:center; color:#14B8A6;'>A.N.I.M.O.</h1>",
        unsafe_allow_html=True
    )

    st.markdown(
        "<h4 style='text-align:center; color:gray;'>Adherence and Notification for Intelligent Medication Oversight</h4>",
        unsafe_allow_html=True
    )
    st.markdown(
        """
        <p style='text-align:center;
        color:#6B7280;
        font-size:16px;'>

        Developed by<br>

        Bose • Deza • Gatinao • Peren

        </p>
        """,
        unsafe_allow_html=True
    )

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown(
        "<p style='text-align:center;'>Loading...</p>",
        unsafe_allow_html=True
    )

    import time
    time.sleep(3)

    st.session_state.show_splash = False
    st.rerun()

def role_screen():

    left, center, right = st.columns([7, 5, 7])

    with center:
        st.title("A.N.I.M.O")
        st.caption("Medication Adherence App")
    # Center section
    col1, col2, col3 = st.columns([1,2,1])

    with col2:

        st.markdown(
            "<h3 style='text-align:center;'>Select Your Role</h3>",
            unsafe_allow_html=True
        )

        # PATIENT
        st.markdown("""
        <div style="
        background:white;
        padding:15px;
        border-radius:15px;
        border-left:6px solid #14B8A6;
        margin-bottom:10px;
        ">
        <h4>🧑 Patient</h4>
        <p>Receive reminders and track medication adherence.</p>
        </div>
        """, unsafe_allow_html=True)

        if st.button(
            "Continue as Patient",
            use_container_width=True
        ):
            st.session_state.role = "Patient"
            st.session_state.page = "login"
            st.rerun()

        st.write("")

        # CAREGIVER
        st.markdown("""
        <div style="
        background:white;
        padding:15px;
        border-radius:15px;
        border-left:6px solid #F59E0B;
        margin-bottom:10px;
        ">
        <h4>🧑‍⚕️ Caregiver</h4>
        <p>Monitor adherence and support patients.</p>
        </div>
        """, unsafe_allow_html=True)

        if st.button(
            "Continue as Caregiver",
            use_container_width=True
        ):
            st.session_state.role = "Caregiver"
            st.session_state.page = "login"
            st.rerun()

        st.write("")

        # HEALTHCARE PROVIDER
        st.markdown("""
        <div style="
        background:white;
        padding:15px;
        border-radius:15px;
        border-left:6px solid #3B82F6;
        margin-bottom:10px;
        ">
        <h4>👨‍⚕️ Healthcare Provider</h4>
        <p>Manage prescriptions and monitor adherence.</p>
        </div>
        """, unsafe_allow_html=True)

        if st.button(
            "Continue as Healthcare Provider",
            use_container_width=True
        ):
            st.session_state.role = "Healthcare Provider"
            st.session_state.page = "login"
            st.rerun()

# ---------------- LOGIN ----------------
def login_screen():

    col1, col2, col3 = st.columns([1,2,1])

    with col2:

        # Center Logo
        logo_left, logo_center, logo_right = st.columns([1,2,1])

        with logo_center:
            st.image(
                "assets/logo.png",
                width=200
            )

        st.markdown(f"""
        <h2 style='text-align:center;color:#0F766E;'>
        Welcome to the A.N.I.M.O.
        </h2>

        <p style='text-align:center;color:gray;'>
        {st.session_state.role} Portal
        </p>
        """, unsafe_allow_html=True)

        mode = st.radio(
            "Mode",
            ["Login", "Sign Up"],
            horizontal=True
        )

        st.title(
            f"{st.session_state.role} Access"
        )

        username = st.text_input(
            "Username"
        )

        password = st.text_input(
            "Password",
            type="password"
        )

        if mode == "Sign Up":

            phone_number = st.text_input(
                "Phone Number",
                placeholder="09XXXXXXXXX"
            )

            st.caption(
                "Format: 09XXXXXXXXX"
            )

            if st.button(
                "📝 Create Account",
                use_container_width=True
            ):

                if not is_valid_phone(phone_number):

                    st.error(
                        "Please enter a valid Philippine mobile number."
                    )

                else:

                    try:

                        add_user(
                            username,
                            password,
                            st.session_state.role,
                            phone_number
                        )

                        st.success("Account created!")

                    except Exception as e:

                        st.error(str(e))

        else:

            if st.button(
                "🔑 Login",
                use_container_width=True
            ):

                user = get_user(username)

                if user and user[1] == password:

                    st.session_state.current_user = username
                    st.session_state.role = user[2]
                    st.session_state.page = "dashboard"

                    st.rerun()

                else:

                    st.error(
                        "Invalid username or password"
                    )

        st.write("")

        if st.button(
            "⬅ Back",
            use_container_width=True
        ):

            st.session_state.page = "role"
            st.session_state.role = None

            st.rerun()

# ---------------- HELPERS ----------------
def is_valid_phone(phone_number):
    return (
        len(phone_number) == 11
        and phone_number.isdigit()
        and phone_number.startswith("09")
    )

def get_risk_label(adherence):
    if adherence >= 80:
        return "🟢 Low Risk"
    elif adherence >= 50:
        return "🟡 Medium Risk"
    return "🔴 High Risk"

def send_notification(med_name):
    notification.notify(
        title="💊 Medication Reminder",
        message=f"Time to take {med_name} at {datetime.now().strftime('%H:%M:%S')}",
        app_name="Adherence App",
        timeout=10
    )

def generate_times(
    start_time,
    frequency_hours
):

    times = []

    current = datetime.strptime(
        start_time,
        "%I:%M %p"
    )

    doses = int(24 / frequency_hours)

    for _ in range(doses):

        times.append(
            current.strftime("%I:%M %p")
        )

        current += timedelta(
            hours=frequency_hours
        )

    return times  

# ---------------- DASHBOARD ----------------
def dashboard():
    role = st.session_state.role
    today = str(date.today())
    col1, col2, col3 = st.columns([1,1,1])

    with col2:
        st.image(
            "assets/logo.png",
            width=150
        )

     
    with st.sidebar:

        st.markdown("## 💊 Adherence App")

        st.write("---")

        st.write("### Logged In User")
        st.success(st.session_state.current_user)

        st.write("### Role")
        st.info(st.session_state.role)

        st.write("---")

        st.write("### Today's Date")
        st.write(today)
    
        if st.button("🚪 Logout"):
            st.session_state.page = "role"
            st.session_state.role = None
            st.session_state.current_user = None
            st.rerun()

    # ================= PATIENT =================
    if role == "Patient":

        st.markdown("""
        <div style="
        background: linear-gradient(90deg,#14B8A6,#0F766E);
        padding:20px;
        border-radius:15px;
        text-align:center;
        color:white;
        margin-bottom:20px;
        ">
        <h1>💊 A.N.I.M.O.</h1>
        <p>Adherence and Notification for Intelligent Medication Oversight</p>
        </div>
        """, unsafe_allow_html=True)
        st.markdown(f"""
        <div style="
        background: linear-gradient(90deg,#14B8A6,#0F766E);
        padding:20px;
        border-radius:18px;
        color:white;
        margin-bottom:20px;
        ">

        <h2>👋 Welcome,
        {st.session_state.current_user}!</h2>

        <p>Your medication companion for today.</p>

        </div>
        """, unsafe_allow_html=True)
        
        st_autorefresh(interval=60000, key="alarm_refresh")

        medicines = get_medications(st.session_state.current_user)
        logs = get_user_logs(st.session_state.current_user)
        overall_taken = 0
        overall_delayed = 0
        overall_total = 0

        current_time = datetime.now()

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

                # Ignore future doses
                if dose_datetime > current_time:
                    continue
                if dose_datetime.date() < datetime.strptime(start_date,"%Y-%m-%d").date():
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

                if log_found:

                    if log_found[3] == "Taken":
                        overall_taken += 1

                    elif log_found[3] == "Delayed":
                        overall_delayed += 1
        
        
        today_logs = []

        for log in logs:

            if (
                log[2] == str(date.today())
                and log[3] in ["Taken", "Delayed"]
            ):
                today_logs.append((log[0], log[1]))

        # ==========================
        # Dashboard Statistics
        # ==========================

        total_doses = 0

        completed = 0

        pending = 0

        missed = 0

        upcoming = 0

        current_time = datetime.now()

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


                # TODAY'S DOSES
                if dose_datetime.date() == date.today():

                    total_doses += 1


                    log_found = next(
                        (
                            l for l in logs
                            if l[0] == med
                            and l[1] == dose_time
                            and l[2] == str(date.today())
                        ),
                        None
                    )


                    if log_found:


                        if log_found[3] in [
                            "Taken",
                            "Delayed"
                        ]:

                            completed += 1


                        elif log_found[3] in [
                            "Missed",
                            "Missed Reviewed"
                        ]:

                            missed += 1



                    else:


                        if current_time > dose_datetime + timedelta(minutes=30):

                            missed += 1


                        elif current_time >= dose_datetime:

                            pending += 1



                # FUTURE DOSES UNTIL END DATE
                elif dose_datetime.date() > date.today():

                    upcoming += 1

        c1, c2, c3, c4, c5 = st.columns(5)

        with c1:
            st.metric("💊 Today's Doses", total_doses)

        with c2:
            st.metric("✅ Taken", completed)

        with c3:
            st.metric("⏳ Pending", pending)

        with c4:
            st.metric("❌ Missed", missed)

        with c5:

            st.metric(
                "📅 Remaining Doses",
                upcoming
            )    

        st.divider()        


        st.subheader("🚨 Emergency")

        if st.button("🚨 EMERGENCY SOS"):

            caregiver = send_emergency(
                st.session_state.current_user
            )

            if caregiver:

                st.success(
                    f"🚨 Emergency alert sent to caregiver: {caregiver}"
                )

            else:

                st.warning(
                    "⚠ No caregiver assigned. Emergency recorded."
                )


        st.subheader("💊 Medication Schedule")

        if not medicines:
            st.info("No medications assigned.")

            # WE WILL BUILD THE NEW SCHEDULER HERE
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
        
            try:
                end = datetime.strptime(
                    end_date,
                    "%Y-%m-%d"
                ).date()

                days_left = max(
                    (end - date.today()).days,
                    0
                )

            except:
                days_left = 0
            

            with st.container(border=True):

                # ===== Header =====
                header_left, header_right = st.columns([4, 1])

                with header_left:
                    st.subheader(f"💊 {med.upper()}")

                with header_right:
                    st.success("🟢 Active")

                # ===== First Row =====
                row1_col1, row1_col2 = st.columns(2)

                with row1_col1:
                    st.metric("💉 Dosage", dosage)

                with row1_col2:
                    st.metric("📅 Days Left", f"{days_left} day(s)")

                # ===== Instructions =====
                st.info(f"📝 {instructions}")

                # ===== Treatment Dates =====
                col1, col2 = st.columns(2)

                with col1:
                    st.caption("📅 Start")
                    st.write(start_date)

                with col2:
                    st.caption("🏁 End")
                    st.write(end_date)


                # ==========================
                # Additional Medication Details
                # ==========================

                st.divider()

                st.subheader("📋 Medication Information")


                st.write(
                    f"🎯 Purpose: {purpose if purpose else 'N/A'}"
                )


                st.write(
                    f"💊 How to Take: {how_to_take if how_to_take else 'N/A'}"
                )


                st.write(
                    f"⚠ Side Effects: {side_effects if side_effects else 'N/A'}"
                )


                st.write(
                    f"🔔 Reminder Notes: {reminders if reminders else 'N/A'}"
                )


                st.divider()

                st.subheader("🕒 Today's Medication")


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
                                    
                if "sms_sent" not in st.session_state:
                    st.session_state.sms_sent = set()

                for dose_time, dose_datetime in dose_schedule:
                # Show only today's doses

                    if dose_datetime.date() != date.today():
                        continue
             

                    log_found = next(
                        (
                            l for l in logs
                            if l[0] == med
                            and l[1] == dose_time
                            and l[2] == str(dose_datetime.date())
                        ),
                        None
                    )

                    current_time = datetime.now()

                    missed_time = dose_datetime + timedelta(minutes=30)

                    next_alarm = get_next_alarm(
                        st.session_state.current_user,
                        med,
                        dose_time
                    )


                    is_snoozed = next_alarm is not None


                    is_snoozed = next_alarm is not None

                    if log_found:

                        if log_found[3] in ["Taken", "Delayed"]:

                            status = "taken"

                        elif log_found[3] == "Missed":

                            status = "missed"

                        else:

                            status = "pending"

                    elif is_snoozed:

                        status = "snoozed"

                    elif current_time > missed_time:

                        status = "missed"

                        sms_key = f"{st.session_state.current_user}_{med}_{dose_time}_MISSED"

                        if not sms_already_sent(
                            st.session_state.current_user,
                            med,
                            dose_time,
                            "MISSED"
                        ):

                            patient_phone = get_user_phone(
                                st.session_state.current_user
                            )

                            caregiver_phone = get_caregiver_phone(
                                st.session_state.current_user
                            )

                            provider_phone = get_provider_phone(
                                st.session_state.current_user
                            )

                            if patient_phone:

                                if send_sms(
                                    patient_phone,
                                    f"You missed your {med} scheduled at {dose_time}."
                                ):

                                    log_sms(
                                        st.session_state.current_user,
                                        med,
                                        dose_time,
                                        "MISSED"
                                    )

                            if caregiver_phone:

                                send_sms(
                                    caregiver_phone,
                                    f"{st.session_state.current_user} missed {med}."
                                )

                            if provider_phone:

                                send_sms(
                                    provider_phone,
                                    f"{st.session_state.current_user} missed {med}."
                                )

                            st.session_state.sms_sent.add(sms_key)

                    elif current_time >= dose_datetime:

                        status = "pending"

                    else:

                        status = "upcoming"  
                    
                    # ================= SMS REMINDER =================

                    if (
                        status == "pending"
                        and current_time >= dose_datetime
                        and current_time <= dose_datetime + timedelta(minutes=1)
                    ):

                        if not sms_already_sent(
                            st.session_state.current_user,
                            med,
                            dose_time,
                            "REMINDER"
                        ):

                            patient_phone = get_user_phone(
                                st.session_state.current_user
                            )

                            caregiver_phone = get_caregiver_phone(
                                st.session_state.current_user
                            )

                            message = (
                                f"Reminder: Time to take {med} "
                                f"scheduled at {dose_time}."
                            )

                            send_sms(
                                patient_phone,
                                message
                            )

                            if caregiver_phone:

                                send_sms(
                                    caregiver_phone,
                                    f"{st.session_state.current_user} should now take {med}."
                                )

                            log_sms(
                                st.session_state.current_user,
                                med,
                                dose_time,
                                "REMINDER"
                            )

                    with st.container(border=True):
                        show_buttons = (
                            status == "pending"
                            and dose_datetime <= current_time <= missed_time
                        )

                        left, right = st.columns([5,2])

                        with left:

                            if status == "taken":

                                st.success(
                                    "✅ Medication taken"
                                )

                            elif status == "missed":

                                st.error(
                                    "⚠ Medication missed"
                                )

                            elif status == "snoozed":

                                st.info(
                                    f"😴 Reminder delayed until {next_alarm}"
                                )

                            elif status == "pending":

                                st.warning(
                                    "💊 Time to take medication"
                                )

                            elif status == "upcoming":

                                st.caption(
                                    f"⏰ Next dose at {dose_time}"
                                )

                        with right:

                            if status == "snoozed":

                                if st.button(
                                    "❌ Cancel Snooze",
                                    key=f"cancel_{med}_{dose_time}"
                                ):

                                    set_next_alarm(
                                        st.session_state.current_user,
                                        med,
                                        dose_time,
                                        None
                                    )
                                    
                                    patient_phone = get_user_phone(
                                        st.session_state.current_user
                                    )

                                    caregiver_phone = get_caregiver_phone(
                                        st.session_state.current_user
                                    )

                                    if not sms_already_sent(
                                        st.session_state.current_user,
                                        med,
                                        dose_time,
                                        "SNOOZE"
                                    ):

                                        if patient_phone:

                                            if send_sms(
                                                patient_phone,
                                                f"Snooze for {med} has been cancelled."
                                            ):

                                                log_sms(
                                                    st.session_state.current_user,
                                                    med,
                                                    dose_time,
                                                    "SNOOZE"
                                                )

                                        if caregiver_phone:

                                            send_sms(
                                                caregiver_phone,
                                                f"{st.session_state.current_user} snoozed {med}."
                                            )   

                                    st.success("Snooze cancelled.")

                                    st.rerun()

                        if show_buttons:

                            with right:

                                if st.button(
                                    "✅ Mark Done",
                                    key=f"done_{st.session_state.current_user}_{med}_{dose_time}",
                                    use_container_width=True
                                ):

                                    if current_time > missed_time:

                                        mark_med_done(
                                            st.session_state.current_user,
                                            med,
                                            dose_time,
                                            status="Delayed"
                                        )

                                    else:

                                        mark_med_done(
                                            st.session_state.current_user,
                                            med,
                                            dose_time,
                                            status="Taken"
                                        )
                                    
                                    # ---------------- SMS ----------------
                                    sms_key = f"{st.session_state.current_user}_{med}_{dose_time}_TAKEN"

                                    if not sms_already_sent(
                                        st.session_state.current_user,
                                        med,
                                        dose_time,
                                        "TAKEN"
                                    ):

                                        patient_phone = get_user_phone(
                                            st.session_state.current_user
                                        )

                                        caregiver_phone = get_caregiver_phone(
                                            st.session_state.current_user
                                        )

                                        # Patient SMS
                                        if patient_phone:

                                            if send_sms(
                                                patient_phone,
                                                f"Medication recorded.\n{med} ({dose_time}) has been marked as TAKEN."
                                            ):

                                                log_sms(
                                                    st.session_state.current_user,
                                                    med,
                                                    dose_time,
                                                    "TAKEN"
                                                )

                                        # Caregiver SMS
                                        if caregiver_phone:

                                            send_sms(
                                                caregiver_phone,
                                                f"{st.session_state.current_user} has taken {med} scheduled at {dose_time}."
                                            )
                                        st.session_state.sms_sent.add(sms_key)      

                                    st.rerun()

                                alert = get_alert(
                                    st.session_state.current_user,
                                    med,
                                    dose_time
                                )

                                if not alert:

                                    create_alert(
                                        st.session_state.current_user,
                                        med,
                                        dose_time
                                    )

                                    alert = get_alert(
                                        st.session_state.current_user,
                                        med,
                                        dose_time
                                    )

                                snooze_count = alert[0]

                                st.caption(f"Snoozes: {snooze_count}/3")

                                if snooze_count < 3:

                                    if st.button(
                                        "😴 Snooze",
                                        key=f"snooze_{st.session_state.current_user}_{med}_{dose_time}",
                                        use_container_width=True
                                    ):

                                        snooze_alert(
                                            st.session_state.current_user,
                                            med,
                                            dose_time
                                        )

                                        next_time = (
                                            datetime.now() +
                                            timedelta(minutes=5)
                                        ).strftime("%I:%M %p")

                                        set_next_alarm(
                                            st.session_state.current_user,
                                            med,
                                            dose_time,
                                            next_time
                                        )

                                        st.rerun()

                                else:

                                    st.error("⚠ Maximum snoozes reached.")
        

        # ---------------- ADHERENCE ----------------


        # ---------------- ADHERENCE ----------------


        today_taken = 0
        today_total = 0


        overall_taken = 0
        overall_total = 0


        current_time = datetime.now()


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


                # OVERALL COUNTER

                if dose_datetime <= current_time:

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


                    if log_found:

                        if log_found[3] in [
                            "Taken",
                            "Delayed"
                        ]:

                            overall_taken += 1



                # TODAY COUNTER

                if dose_datetime.date() == date.today():

                    today_total += 1


                    log_found = next(
                        (
                            l for l in logs
                            if l[0] == med
                            and l[1] == dose_time
                            and l[2] == str(date.today())
                        ),
                        None
                    )


                    if log_found:

                        if log_found[3] in [
                            "Taken",
                            "Delayed"
                        ]:

                            today_taken += 1



        # USE SHARED CALCULATIONS

        today_adherence = calculate_today_adherence(
            st.session_state.current_user
        )


        overall_adherence = calculate_treatment_adherence(
            st.session_state.current_user
        )

                  
        st.subheader("📈 Medication Adherence")


        col1, col2 = st.columns(2)


        with col1:

            st.metric(
                "📅 Today's Adherence",
                f"{today_adherence}%"
            )

            st.caption(
                f"{today_taken}/{today_total} doses completed"
            )


        with col2:

            st.metric(
                "📊 Treatment Adherence",
                f"{overall_adherence}%"
            )

            st.caption(
                f"{overall_taken}/{overall_total} doses completed"
            )

        st.subheader("⚠ Risk Level")


        if overall_adherence >= 90:

            st.success(
                "🟢 Low Risk\n\nExcellent medication adherence."
            )


        elif overall_adherence >= 70:

            st.warning(
                "🟡 Medium Risk\n\nPatient missed some medications."
            )


        else:

            st.error(
                "🔴 High Risk\n\nImmediate follow-up recommended."
            )

        st.divider()

        st.subheader("⚙️ Account")

        if st.button(
            "🚪 Logout",
            key="patient_logout",
            use_container_width=True
        ):

            st.session_state.current_user = None
            st.session_state.role = None
            st.session_state.page = "role"

            st.rerun()   

    # ================= CAREGIVER =================
    elif role == "Caregiver":

        st.markdown("""
        <div style="
        background: linear-gradient(90deg,#14B8A6,#0F766E);
        padding:20px;
        border-radius:15px;
        text-align:center;
        color:white;
        margin-bottom:20px;
        ">
        <h1>🧑‍⚕️ Caregiver Dashboard</h1>
        <p>Monitor Patient Medication Adherence</p>
        </div>
        """, unsafe_allow_html=True)
        st.title("🧑‍⚕️ Caregiver Dashboard")

        selected_patient = get_assigned_patient(
            st.session_state.current_user
        )

        if not selected_patient:
           st.warning("⚠ No patient assigned to you.")
           return

        medicines = get_medications(selected_patient)
        logs = get_user_logs(selected_patient)

        today = date.today()

        overall_taken = 0
        overall_delayed = 0
        overall_total = 0

        today_taken = 0
        today_total = 0
        today_pending = 0
        today_missed = 0

        remaining_doses = 0


        current_time = datetime.now()


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

                    remaining_doses += 1


                # ==========================
                # OVERALL TREATMENT ADHERENCE
                # ==========================

                if dose_datetime <= current_time:

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


                    if log_found:

                        if log_found[3] == "Taken":

                            overall_taken += 1


                        elif log_found[3] == "Delayed":

                            overall_delayed += 1



                # ==========================
                # TODAY'S ADHERENCE
                # ==========================

                if dose_datetime.date() == date.today():

                    today_total += 1


                    log_found = next(
                        (
                            l for l in logs
                            if l[0] == med
                            and l[1] == dose_time
                            and l[2] == str(date.today())
                        ),
                        None
                    )


                    if log_found:

                        if log_found[3] in [
                            "Taken",
                            "Delayed"
                        ]:

                            today_taken += 1

        # ===========================
        # STANDARDIZED ADHERENCE
        # ===========================


        adherence = calculate_today_adherence(
            selected_patient
        )


        treatment_adherence = calculate_treatment_adherence(
            selected_patient
        )             
        
        # ===========================
        # NEXT MEDICATION TRACKER
        # ===========================

        next_med_name = None
        next_med_dose = None
        next_med_datetime = None

        st.subheader("👤 Patient Summary")

        with st.container(border=True):

            st.subheader(f"👤 {selected_patient}")

            col1, col2, col3, col4 = st.columns(4)

            with col1:

                st.metric(
                    "💊 Today's Scheduled Doses",
                    today_total
                )

                st.caption(
                    f"{today_taken}/{today_total} doses completed"
                )


            with col2:

                st.metric(
                    "📈 Today's Adherence",
                    f"{adherence}%"
                )


            with col3:

                st.metric(
                    "📊 Treatment Adherence",
                    f"{treatment_adherence}%"
                )


            with col4:

                st.metric(
                    "📅 Remaining Doses",
                    remaining_doses
                )

                

            if treatment_adherence >= 90:

                st.success(
                    "🟢 Low Risk\n\nExcellent medication adherence."
                )


            elif treatment_adherence >= 70:

                st.warning(
                    "🟡 Medium Risk\n\nPatient shows inconsistent medication adherence."
                )


            else:

                st.error(
                    "🔴 High Risk\n\nImmediate follow-up recommended."
                )
        
        # ===========================
        # LOAD SNOOZE DATA ONCE
        # ===========================

        snooze_data = {}


        snooze_records = get_user_snoozes(
            selected_patient
        )


        for snooze in snooze_records:

            key = (
                snooze["medicine_name"],
                snooze["med_time"]
            )

            snooze_data[key] = snooze["next_alarm_time"]  

        # ===========================
        # CAREGIVER ALERT PANEL
        # ===========================

        st.subheader("🚨 Alerts")


        # ===========================
        # LOAD MISSED ALERTS
        # ===========================

        missed_alerts = get_pending_missed_alerts(
            selected_patient
        )


        missed_count = len(
            missed_alerts
        )


        snoozed_count = 0


        current_time = datetime.now()



        # ===========================
        # GET EMERGENCY ALERTS
        # ===========================

        emergencies = get_caregiver_emergencies(
            st.session_state.current_user
        )


        emergency_count = len(
            [
                e for e in emergencies
                if e["status"] == "Pending"
            ]
        )



        # ===========================
        # SCAN MEDICATIONS
        # ===========================

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


            # Generate schedule

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


                # ===========================
                # CHECK SNOOZE
                # ===========================

                next_alarm = snooze_data.get(
                    (
                        med,
                        dose_time
                    )
                )

                if next_alarm:

                    snoozed_count += 1



                # Only check finished doses

                if dose_datetime >= current_time:

                    continue



                # Find medication log

                log_found = next(
                    (
                        l for l in logs
                        if l[0] == med
                        and l[1] == dose_time
                        and l[2] == str(dose_datetime.date())
                    ),
                    None
                )

                # ===========================
                # CHECK MEDICATION STATUS
                # ===========================


                if log_found:


                    # Completed medication
                    if log_found[3] in [
                        "Taken",
                        "Delayed"
                    ]:

                        continue



                    # Already missed medication
                    elif log_found[3] in [
                        "Missed",
                        "Missed Reviewed"
                    ]:

                        missed_count += 1



                # No log yet, detect missed dynamically

                else:


                    if current_time > dose_datetime + timedelta(minutes=30):


                        missed_count += 1


                        add_missed_log(
                            selected_patient,
                            med,
                            dose_time,
                            dose_datetime.date()
                        )


                        create_missed_alert(
                            selected_patient,
                            med,
                            dose_time,
                            dose_datetime.date()
                        )





        # ===========================
        # DISPLAY ALERT SUMMARY
        # ===========================

        col1, col2, col3 = st.columns(3)


        with col1:

            st.metric(
                "❌ Missed",
                missed_count
            )


        with col2:

            st.metric(
                "🚑 Emergency",
                emergency_count
            )


        with col3:

            st.metric(
                "😴 Snoozed",
                snoozed_count
            )





        # ===========================
        # MISSED MEDICATION ALERTS
        # ===========================


        pending_alerts = get_pending_missed_alerts(
            selected_patient
        )


        if pending_alerts:


            for alert in pending_alerts:

                with st.container(border=True):

                    st.error(
                        f"""
                        ❌ Missed Medication


                        💊 {alert['med_name']}


                        🕒 Scheduled:
                        {alert['med_time']}


                        📅 Date:
                        {alert['date']}
                        """
                    )


                    if st.button(
                        "✅ Acknowledged",
                        key=f"review_{alert['id']}"
                    ):


                        acknowledge_missed_alert(
                            alert['id']
                        )


                        st.rerun()



        else:


            st.success(
                "✅ No missed medications"
            )
            
        # ===========================
        # DISPLAY EMERGENCY DETAILS
        # ===========================

        st.subheader("🚑 Emergency Alerts")



        if emergencies:


            for emergency in emergencies:

                with st.container(border=True):

                    if emergency["status"] == "Pending":

                        st.error(
                            f"""
                            🚨 Emergency Alert

                            Patient:
                            {emergency["patient_username"]}

                            Time:
                            {emergency["emergency_time"]}

                            Status:
                            {emergency["status"]}
                            """
                        )


                        if st.button(
                            "✅ Acknowledge",
                            key=f"emergency_{emergency['id']}"
                        ):

                            acknowledge_emergency(
                                emergency["id"]
                            )

                            st.success(
                                "Emergency acknowledged."
                            )

                            st.rerun()


                    else:

                        st.success(
                            f"""
                            ✅ Emergency Resolved

                            Patient:
                            {emergency["patient_username"]}

                            Time:
                            {emergency["emergency_time"]}

                            Status:
                            {emergency["status"]}
                            """
                        )


        else:


            st.success(
                "✅ No emergency alerts"
            )
  

        st.subheader("💊 Today's Medications")

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

                with st.container(border=True):

                    top_left, top_right = st.columns([4,1])

                    with top_left:
                        st.subheader(f"💊 {med}")

                    with top_right:

                        next_alarm = snooze_data.get(
                            (
                                med,
                                dose_time
                            )
                        )

                        is_snoozed = next_alarm is not None

                        log_found = next(
                            (
                                l for l in logs
                                if l[0] == med
                                and l[1] == dose_time
                                and l[2] == str(dose_datetime.date())
                            ),
                            None
                        )


                        if log_found:

                            if log_found[3] in [
                                "Taken",
                                "Delayed"
                            ]:

                                st.success(
                                    "✅ Medication Taken"
                                )

                            elif log_found[3] in [
                                "Missed",
                                "Missed Reviewed"
                            ]:

                                st.error(
                                    "❌ Medication Missed"
                                )


                        else:

                            if is_snoozed:

                                st.info(
                                    f"😴 Snoozed until {next_alarm}"
                                )


                            elif datetime.now() > dose_datetime + timedelta(minutes=30):

                                st.error(
                                    "❌ Medication Missed"
                                )


                            elif datetime.now() >= dose_datetime:

                                st.warning(
                                    "⏳ Pending Confirmation"
                                )


                            else:

                                st.info(
                                    "⏰ Upcoming"
                                )

                    info1, info2 = st.columns(2)

                    with info1:
                        st.metric(
                            "💉 Dosage",
                            dosage
                        )

                    with info2:
                        st.metric(
                            "🕒 Time",
                            dose_time
                        )

                    st.info(f"📝 {instructions}")

                    info3, info4 = st.columns(2)

                    with info3:
                        st.metric(
                            "📅 Start",
                            start_date
                        )

                    with info4:
                        st.metric(
                            "🏁 End",
                            end_date
                        )

                    st.caption(
                        f"⏰ Every {frequency_hours} hour(s)"
                    )

            
            st.divider()

        st.subheader("📈 Adherence")

        st.progress(
            treatment_adherence / 100
        )

        col1, col2, col3, col4 = st.columns(4)


        with col1:

            st.metric(
                "✅ Taken Today",
                today_taken
            )


        with col2:

            st.metric(
                "💊 Scheduled Today",
                today_total
            )


        with col3:

            st.metric(
                "📅 Remaining Doses",
                remaining_doses
            )


        with col4:

            st.metric(
                "📊 Treatment Adherence",
                f"{treatment_adherence}%"
    )

        st.divider()

        st.subheader("📜 Recent Medication History")

        history = get_user_logs(selected_patient)

        if history:

            history_df = pd.DataFrame(
                history,
                columns=[
                    "Medicine",
                    "Time",
                    "Date",
                    "Status"
                ]
            )

            st.dataframe(
                history_df.tail(10),
                use_container_width=True,
                hide_index=True
            )

        else:

            st.info("No history available.")

        st.subheader("⚙️ Account")

        if st.button(
            "🚪 Logout",
            key="caregiver_logout",
            use_container_width=True
        ):

            st.session_state.current_user = None
            st.session_state.role = None
            st.session_state.page = "role"

            st.rerun()

         


# ================= PHYSICIAN =================
    elif role == "Healthcare Provider":

        st.markdown("""
        <div style="
            background: linear-gradient(90deg,#14B8A6,#0F766E);
            padding:20px;
            border-radius:15px;
            text-align:center;
            color:white;
            margin-bottom:20px;
        ">
            <h1>👨‍⚕️ Healthcare Provider Dashboard</h1>
            <p>Manage Patients, Medications, and Caregivers</p>
        </div>
        """, unsafe_allow_html=True)

        st.title("🏥 Healthcare Provider Dashboard")

        patients = get_patients()

        if not patients:
            st.info("No patients found.")
            return

        st.subheader("👥 Select Patient")

        selected_patient = st.selectbox(
            "Choose Patient",
            [p[0] for p in patients],
            key="selected_patient_dashboard"
        )

        page = st.radio(
            "Patient Workspace",
            [
                "🏠 Dashboard",
                "🏥 Patient Record",
                "💊 Assign Medication",
                "📜 Medication History",
                "📊 Analytics",
                "👤 Assign Caregiver",
                "🚨 Emergency Alerts",
                "⚙️ Settings"
            ],
            horizontal=True
        )

        # ------------------------------------
        # Load selected patient's medications
        # ------------------------------------

        medicines = get_medications(selected_patient)
        #====================================
        # DASHBOARD
        # ====================================
        if page == "🏠 Dashboard":

            st.subheader("🏠 Healthcare Provider Overview")

            total_patients = len(patients)

            total_meds = sum(
                len(get_medications(p[0]))
                for p in patients
            )

            emergencies = get_provider_emergencies(
                st.session_state.current_user
            )

            pending_emergencies = len([
                e for e in emergencies
                if e[3] == "Pending"
            ])

            scheduled_doses = 0

            today = date.today()

            today = date.today()

            scheduled_doses = 0


            for patient in patients:


                summary = calculate_adherence_summary(
                    patient[0]
                )


                scheduled_doses += summary["today_total"]

            total_adherence = 0

            count = 0


            for patient in patients:

                summary = calculate_adherence_summary(
                    patient[0]
                )


                total_adherence += summary["overall_adherence"]

                count += 1



            if count > 0:

                average_adherence = round(
                    total_adherence / count
                )

            else:

                average_adherence = 0

            col1, col2, col3, col4 = st.columns(4)

            with col1:

                st.metric(
                    "👥 Patients",
                    total_patients
                )


            with col2:

                st.metric(
                    "💊 Today's Scheduled Doses",
                    scheduled_doses
                )


            with col3:

                st.metric(
                    "📊 Average Adherence",
                    f"{average_adherence}%"
                )


            with col4:

                st.metric(
                    "🚨 Emergencies",
                    pending_emergencies
                )

            st.divider()

            st.subheader("⚡ Quick Actions")

            c1, c2, c3 = st.columns(3)

            c1.info("🏥 View Patient Records")
            c2.info("💊 Assign Medication")
            c3.info("📊 View Analytics")

        # ====================================
        # PATIENT RECORD
        # ====================================     
        elif page == "🏥 Patient Record":
            st.subheader("👤 Patient Record")

            caregiver = get_patient_caregiver(selected_patient)
            meds = get_medications(selected_patient)
            logs = get_user_logs(selected_patient)

            today = date.today()
            current_time = datetime.now()  
            schedule_rows = []

            summary = calculate_adherence_summary(
                selected_patient
            )


            taken = summary["today_taken"]

            delayed = summary["today_delayed"]

            missed = summary["today_missed"]

            pending = summary["today_pending"]


            for (
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
            ) in meds:
                   
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


                    status = "🔵 Upcoming"

                    # Check if this dose exists in the medication log
                    log_found = None

                    for log in logs:

                        if (
                            log[0] == med_name
                            and log[1] == dose_time
                            and log[2] == str(dose_datetime.date())
                        ):

                            log_found = log
                            break


                    if log_found:

                        if log_found[3] == "Taken":

                            status = "✅ Taken"


                        elif log_found[3] == "Delayed":

                            status = "🟡 Delayed"


                        elif log_found[3] in [
                            "Missed",
                            "Missed Reviewed"
                        ]:

                            status = "❌ Missed"

                    else:

                        # Today's dose
                        if dose_datetime.date() == today:

                            if current_time > dose_datetime + timedelta(minutes=30):

                                status = "❌ Missed"


                            else:

                                status = "⏳ Pending"


                        # Future dose
                        elif dose_datetime.date() > today:

                            status = "🔵 Upcoming"

                        # Future dose
                        elif dose_datetime.date() > today:

                            status = "🔵 Upcoming"

                    schedule_rows.append({

                        "Medicine": med_name,
                        "Date": dose_datetime.strftime("%Y-%m-%d"),
                        "Time": dose_time,
                        "Dosage": dosage,
                        "Status": status

                    })

            treatment_adherence = summary["overall_adherence"]
            
            st.subheader("👤 Patient Summary")

            with st.container(border=True):

                st.write(f"👥 Caregiver: {caregiver if caregiver else 'None'}")

                col1, col2 = st.columns(2)

                with col1:

                    st.metric(
                        "Today's Medication Schedule",
                        summary["today_total"]
                    )

                with col2:

                    st.metric(
                        "Overall Adherence",
                        f"{treatment_adherence}%"
                    )

                col1, col2, col3, col4 = st.columns(4)

                col1.metric("✅ Taken", taken)
                col2.metric("🟡 Delayed", delayed)
                col3.metric("⏳ Pending", pending)
                col4.metric("❌ Missed", missed) 

                st.divider()

                st.subheader("💊 Current Medications")

                for (
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
                ) in meds:

                    with st.container(border=True):
                        
                        header_left, header_right = st.columns([1,4])

                        with header_left:
                            st.subheader(f"💊 {med_name}")

                        with header_right:

                            days_left = (
                                datetime.strptime(end_date,"%Y-%m-%d").date()
                                - date.today()
                            ).days

                            if days_left >= 0:
                                st.success("🟢 Active")
                            else:
                            
                               st.error("🔴 Finished")

                            col1, col2 = st.columns(2)

                            with col1:
                                st.metric("💉 Dosage", dosage)

                            with col2:
                                st.metric(
                                    "⏰ Frequency",
                                    f"Every {frequency_hours} hr(s)"
                                    if frequency_hours
                                    else "Daily"
                                )  
                            st.info(f"📝 {instructions}")

                            st.write(f"🎯 Purpose: {purpose or 'N/A'}")
                            st.write(f"💊 Administration: {how_to_take or 'N/A'}")
                            st.write(f"⚠ Side Effects: {side_effects or 'N/A'}")                                             
                        
                        st.divider()
                
                        if st.button(
                            "🗑️Delete Medication",
                            key=f"delete_{selected_patient}_{med_name}_{start_date}_{med_time}"
                        ):

                            delete_medication(
                                selected_patient,
                                med_name,
                                med_time
                            )

                            st.success("Medication deleted.")

                            st.rerun()

        # ====================================
        # ASSIGN MEDICATION
        # ====================================
        elif page == "💊 Assign Medication":
            # ---------------- BASIC INFO ----------------

            col1, col2 = st.columns(2)

            with col1:
                med_name = st.text_input(
                    "💊 Medicine Name",
                    key="physician_med_name"
                )

            with col2:
                dosage = st.text_input(
                    "💉 Dosage",
                    key="physician_dosage"
                )

            col1, col2 = st.columns(2)

            with col1:
                instructions = st.text_input(
                    "📝 Instructions",
                    key="physician_instructions"
                )

            with col2:
                frequency_hours = st.selectbox(
                    "⏰ Every",
                    [1,2,3,4,6,8,12,24],
                    key="physician_frequency"
                )

                st.caption(
                    f"Reminder every {frequency_hours} hour(s)"
                )

            # ---------------- START / END ----------------

            col1, col2 = st.columns(2)

            with col1:
                start_date = st.date_input(
                    "📅 Treatment Start"
                )

            with col2:
                duration = st.number_input(
                    "Duration",
                    min_value=1,
                    value=30
                )

            duration_unit = st.selectbox(
                "Duration Unit",
                ["Days","Months"]
            )

            if duration_unit == "Days":

                end_date = start_date + timedelta(days=duration-1)

            else:

                end_date = start_date + timedelta(days=(duration*30)-1)

            # ---------------- START TIME ----------------

            col1, col2, col3 = st.columns(3)

            with col1:
                hour = st.selectbox(
                    "Hour",
                    list(range(1,13)),
                    key="physician_hour"
                )

            with col2:
                minute = st.selectbox(
                    "Minute",
                    [f"{i:02d}" for i in range(60)],
                    key="physician_minute"
                )

            with col3:
                ampm = st.selectbox(
                    "AM/PM",
                    ["AM","PM"],
                    key="physician_ampm"
                )

            start_time = f"{hour:02d}:{minute} {ampm}"

            # ---------------- EXTRA DETAILS ----------------

            col1, col2 = st.columns(2)

            with col1:
                purpose = st.text_area("🎯 Purpose")

            with col2:
                how_to_take = st.text_area("💊 How to Take")

            col1, col2 = st.columns(2)

            with col1:
                side_effects = st.text_area("⚠ Side Effects")

            with col2:
                reminders = st.text_area("🔔 Reminders")

            # ---------------- SUBMIT ----------------

            if "adding_med" not in st.session_state:
                st.session_state.adding_med = False

            if st.button(
                
                "Assign Medication",
                disabled=st.session_state.adding_med
            ):

                if med_name.strip() == "":
                    st.error("Medicine name is required.")

                elif dosage.strip() == "":
                    st.error("Dosage is required.")

                else:

                    st.session_state.adding_med = True

                    add_medication(
                        patient_username=selected_patient,
                        medicine_name=med_name,
                        time=start_time,
                        dosage=dosage,
                        instructions=instructions,
                        start_date=str(start_date),
                        end_date=str(end_date),
                        start_time=start_time,
                        frequency_hours=frequency_hours,
                        purpose=purpose,
                        how_to_take=how_to_take,
                        side_effects=side_effects,
                        reminders=reminders
                    )

                    st.session_state.med_added = True
                    st.session_state.adding_med = False

                    st.rerun()    
            
            if st.session_state.get("med_added", False):
                st.success("✅ Medication assigned successfully!")
                st.session_state.med_added = False
        # ====================================
        # MEDICATION HISTORY
        # ====================================
        elif page == "📜 Medication History":

            st.subheader("📋 Medication Schedule")

            meds = get_medications(selected_patient)
            logs = get_user_logs(selected_patient)

            if not meds:
                st.info("No medication history.")
                st.stop()

            schedule_rows = []

            current_time = datetime.now()

            for (
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
            ) in meds:

                dose_schedule = generate_dose_schedule(
                    start_date,
                    end_date,
                    start_time,
                    frequency_hours
                )

                for dose_time, dose_datetime in dose_schedule:

                    if dose_datetime < current_time:

                        log = next(
                            (
                                l for l in logs
                                if l[0] == med_name
                                and l[1] == dose_time
                                and l[2] == str(dose_datetime.date())
                            ),
                            None
                        )

                        if log:

                            if log[3] == "Taken":
                                status = "✅ Taken"

                            elif log[3] == "Delayed":
                                status = "🟡 Delayed"

                            else:
                                status = "❌ Missed"

                        else:
                            status = "❌ Missed"

                    else:

                        status = "🔵 Upcoming"

                    schedule_rows.append([
                        dose_datetime.strftime("%Y-%m-%d"),
                        dose_time,
                        med_name,
                        status
                    ])

            schedule_rows.sort()

            schedule_df = pd.DataFrame(
                schedule_rows,
                columns=[
                    "Date",
                    "Time",
                    "Medicine",
                    "Status"
                ]
            )

            st.dataframe(
                schedule_df,
                use_container_width=True,
                hide_index=True
            )                 

        # ====================================
        # ANALYTICS
        # ====================================
        elif page == "📊 Analytics":
            st.subheader("📊 Patient Analytics")

            meds = get_medications(selected_patient)
            logs = get_user_logs(selected_patient)

            today = date.today()
            today_str = str(today)

            today_logs = [
                log
                for log in logs
                if log[2] == today_str
            ]
            # ==========================
            # LOAD ADHERENCE SUMMARY
            # ==========================

            summary = calculate_adherence_summary(
                selected_patient
            )


            total_doses = summary["today_total"]

            completed = summary["today_taken"]

            delayed = summary["today_delayed"]

            pending = summary["today_pending"]

            missed = summary["today_missed"]

            treatment_adherence = summary["overall_adherence"]  

            

            treatment_adherence = calculate_treatment_adherence(
                selected_patient
            )

            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric(
                    "📈 Adherence",
                    f"{treatment_adherence}%"
                )

            with col2:
                st.metric(
                    "✅ Taken",
                    completed
                )

            with col3:
                st.metric(
                    "🟡 Delayed",
                    delayed
                )

            with col4:
                st.metric(
                    "❌ Missed",
                    missed
                )
            
            st.divider()

            st.subheader("📈 Daily Medication Activity")

            if logs:

                df = pd.DataFrame(

                    logs,

                    columns=[

                        "Medicine",

                        "Time",

                        "Date",

                        "Status"

                    ]

                )

                daily = (

                    df.groupby("Date")

                    .size()

                    .reset_index(name="Total")

                )

                st.line_chart(

                    daily.set_index("Date")

                )

            else:

                st.info("No medication history available.")

            st.divider()

            st.subheader("📜 Medication Schedule")

            schedule_rows = []

            current_time = datetime.now()

            for (
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
            ) in meds:

                dose_schedule = generate_dose_schedule(
                    start_date,
                    end_date,
                    start_time,
                    frequency_hours
                )

                for dose_time, dose_datetime in dose_schedule:

                    status = "⏳ Upcoming"

                    for log in logs:

                        if (
                            log[0] == med_name
                            and log[1] == dose_time
                            and log[2] == str(dose_datetime.date())
                        ):

                            if log[3] == "Taken":
                                status = "✅ Taken"

                            elif log[3] == "Delayed":
                                status = "🟡 Delayed"

                            elif log[3] in [
                                "Missed",
                                "Missed Reviewed"
                            ]:
                                status = "❌ Missed"

                            break

                    if status == "⏳ Upcoming":


                        # Past medication date

                        if dose_datetime.date() < today:

                            status = "❌ Missed"



                        # Today's medication

                        elif dose_datetime.date() == today:


                            if current_time > dose_datetime + timedelta(minutes=30):

                                status = "❌ Missed"


                            else:

                                status = "⏳ Pending"



                        # Future medication

                        elif dose_datetime.date() > today:

                            status = "🔵 Upcoming"

                    schedule_rows.append([

                        med_name,

                        dose_datetime.strftime("%Y-%m-%d"),

                        dose_time,

                        status

                    ])

            if schedule_rows:

                schedule_df = pd.DataFrame(

                    schedule_rows,

                    columns=[

                        "Medicine",

                        "Date",

                        "Time",

                        "Status"

                    ]

                )

                st.dataframe(

                    schedule_df,

                    hide_index=True,

                    use_container_width=True

                )

            else:

                st.info("No medication schedule.")  

            st.divider()

            st.subheader("⚠ Risk Level")

            if treatment_adherence >= 90:

                st.success(
                    "🟢 Low Risk\n\nExcellent medication adherence."
                )

            elif treatment_adherence >= 70:

                st.warning(
                    "🟡 Medium Risk\n\nPatient missed some medications."
                )

            else:

                st.error(
                    "🔴 High Risk\n\nImmediate follow-up recommended."
                )            
        # ====================================
        # ASSIGN CAREGIVER
        # ====================================
        elif page == "👤 Assign Caregiver":

            st.subheader("👥 Assign Caregiver")

            caregivers = [
                c[0]
                for c in get_caregivers()
            ]

            if not caregivers:

                st.warning("No caregivers available.")

            else:

                caregiver = st.selectbox(

                    "Assign Caregiver",

                    ["None"] + caregivers

                )

                if st.button("Assign Caregiver"):

                    if caregiver == "None":

                        assign_caregiver(

                            None,

                            selected_patient,

                            st.session_state.current_user

                        )

                        st.success(
                            "Caregiver removed."
                        )

                    else:

                        assign_caregiver(

                            caregiver,

                            selected_patient,

                            st.session_state.current_user

                        )

                        st.success(
                            f"{caregiver} assigned successfully."
                        )

                    st.rerun()
        
        # ====================================
        # EMERGENCY ALERTS
        # ====================================
        elif page == "🚨 Emergency Alerts":

            st.subheader("🚨 Emergency Alerts")

            emergencies = get_provider_emergencies(
                st.session_state.current_user
            )

            if not emergencies:

                st.success("✅ No emergency alerts.")

            else:

                for patient, caregiver, emergency_time, status in emergencies:

                    with st.container(border=True):

                        st.error(f"🚨 Emergency from: {patient}")

                        st.write(
                            f"👤 Caregiver: {caregiver if caregiver else 'None'}"
                        )

                        st.write(f"🕒 {emergency_time}")

                        st.write(f"📌 Status: {status}")

                        if status == "Pending":

                            if st.button(
                                "✔ Resolve",
                                key=f"resolve_{patient}_{emergency_time}"
                            ):

                                resolve_emergency(
                                    patient,
                                    emergency_time
                                )

                                st.success("Emergency resolved.")

                                st.rerun()

                        else:

                            st.success("✅ Already Resolved")

        # ====================================
        # EMERGENCY ALERTS
        # ====================================                                  
        elif page == "⚙️ Settings":

            st.subheader("⚙️ Account")

            st.info(f"👤 Username: {st.session_state.current_user}")

            st.info(f"🩺 Role: {role}")

            st.divider()

            if st.button(
                "🚪 Logout",
                key="provider_logout",
                use_container_width=True
            ):

                st.session_state.current_user = None
                st.session_state.role = None
                st.session_state.page = "role"

                st.rerun()


    # ---------------- LOGOUT ----------------
    st.write("---")

    if st.button("Logout", key="logout_btn"):
        st.session_state.page = "role"
        st.session_state.role = None
        st.session_state.current_user = None
        st.rerun()

# ---------------- ROUTER ----------------
if st.session_state.show_splash:
    splash_screen()

if st.session_state.page == "role":
    role_screen()

elif st.session_state.page == "login":
    login_screen()

elif st.session_state.page == "dashboard":
    dashboard()