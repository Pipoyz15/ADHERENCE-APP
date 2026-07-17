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
    get_next_alarm,
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
    log_sms
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

    logo_base64 = get_base64_image("assets/logo.png")

    st.markdown(
        f"""
        <div style="
            background:linear-gradient(90deg,#14B8A6,#0F766E);
            padding:20px;
            border-radius:20px;
            margin-bottom:25px;
        ">
            <div style="display:flex;align-items:center;gap:20px;">

                <img src="data:image/png;base64,{logo_base64}" width="90">

                <div>
                    <h1 style="margin:0;color:white;">
                        Medication Adherence App
                    </h1>

                    <p style="margin:0;color:#E5E7EB;">
                        Medication Monitoring and SMS Reminder System
                    </p>
                </div>

            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

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

                        st.success(
                            "Account created!"
                        )

                    except:

                        st.error(
                            "Username already exists"
                        )

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

    doses_per_day = 24 // frequency_hours

    for _ in range(doses_per_day):

        times.append(
            current.strftime(
                "%I:%M %p"
            )
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


        today_logs = []

        for log in logs:

            if log[2] == str(date.today()):
                today_logs.append((log[0], log[1]))

        st.subheader("💊 Medication Schedule")

        if not medicines:
            st.info("No medications assigned.")

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

            col1, col2 = st.columns([3,1])

            if frequency_hours:
                times = generate_times(
                    start_time,
                    frequency_hours
                )
            else:
                times = [time]

            schedule_datetime = datetime.strptime(
                f"{start_date} {start_time}",
                "%Y-%m-%d %I:%M %p"
            )

            dose_schedule = []

            for i, dose in enumerate(times):

                if frequency_hours:
                    dose_datetime = schedule_datetime + timedelta(
                        hours=i * frequency_hours
                    )
                else:
                    dose_datetime = schedule_datetime

                dose_schedule.append(
                    (dose, dose_datetime)
                )

            today_date = date.today()

            start = datetime.strptime(
                start_date,
                "%Y-%m-%d"
            ).date()

            end = datetime.strptime(
                end_date,
                "%Y-%m-%d"
            ).date()

            if today_date < start:
                continue

            if today_date > end:
                continue

            days_left = max(
                0,
                (end - today_date).days
            )

            current_time = datetime.now()

            with col1:

                with st.container(border=True):

                    st.subheader(f"💊 {med.upper()}")

                    colA, colB = st.columns(2)

                    with colA:
                        st.metric(
                            "💉 Dosage",
                            dosage
                        )

                    with colB:
                        st.metric(
                            "📅 Days Left",
                            days_left
                        )

                    st.info(f"📝 {instructions}")

                    st.caption(f"Treatment Ends: {end_date}")

                    st.divider()

                    total_doses = len(dose_schedule)

                    completed_doses = sum(
                        1 for dose, _ in dose_schedule
                        if (med, dose) in today_logs
                    )

                    progress = (
                        completed_doses / total_doses
                        if total_doses
                        else 0
                    )

                    st.markdown("### 📈 Today's Progress")

                    st.progress(progress)

                    st.caption(
                        f"{completed_doses} of {total_doses} doses completed"
                    )

                    st.divider()

                    st.markdown("### 🕒 Today's Schedule")

                    for dose_time, dose_datetime in sorted(
                        dose_schedule,
                        key=lambda x: x[1]
                    ):

                        current_time = datetime.now()

                        dose_taken = (
                            med,
                            dose_time
                        ) in today_logs

                        base_alarm = dose_datetime

                        next_alarm = get_next_alarm(
                            st.session_state.current_user,
                            med,
                            dose_time
                        )

                        if next_alarm:

                            alarm_time = datetime.combine(
                                base_alarm.date(),
                                datetime.strptime(
                                    next_alarm,
                                    "%I:%M %p"
                                ).time()
                            )

                            alarm_time_str = next_alarm

                        else:

                            alarm_time = base_alarm

                            alarm_time_str = dose_time
# ----------------------------

                        remaining = alarm_time - current_time

                        minutes = max(
                            0,
                            int(remaining.total_seconds() // 60)
                        )

                        seconds = max(
                            0,
                            int(remaining.total_seconds() % 60)
                        )

                        missed_time = base_alarm + timedelta(minutes=30)

                        if dose_taken:

                            status = "taken"

                        elif current_time < base_alarm:

                            status = "pending"

                        elif current_time > missed_time:

                            status = "missed"

                        else:

                            status = "pending"
                        

                        with st.container(border=True):


                            col_time, col_status = st.columns([2, 1])

                            with col_time:

                                st.markdown(f"### 🕒 {dose_time}")

                            with col_status:

                                if status == "taken":
                                    st.success("✅ Taken")

                                elif status == "missed":
                                    st.error("❌ Missed")

                                else:
                                    st.warning("⏳ Pending")

                            if status == "pending":

                                st.progress(
                                    max(
                                        0,
                                        min(
                                            1,
                                            1 - (
                                                remaining.total_seconds() / 1800
                                            )
                                        )
                                    )
                                )

                                st.caption(
                                    f"⏰ Reminder in {minutes}m {seconds}s"
                                )
                            # -------------------------
                            # ACTION BUTTONS
                            # -------------------------
                            st.write("")
                            st.info("🔧 Buttons will be moved here.")

                if (
                    purpose
                    or how_to_take
                    or side_effects
                    or reminders
                ):

                    with st.expander("📖 Learn More"):

                        if purpose:

                            st.write("### 🎯 Purpose")
                            st.write(purpose)

                        if how_to_take:

                            st.write("### 💊 How to Take")
                            st.write(how_to_take)

                        if side_effects:

                            st.write("### ⚠️ Common Side Effects")
                            st.write(side_effects)

                        if reminders:

                            st.write("### 🔔 Important Reminder")
                            st.write(reminders)


        # ==============================
            # ---------------- RIGHT SIDE ----------------
               
            with col2:

                for dose_time, dose_datetime in sorted(
                    dose_schedule,
                    key=lambda x: x[1]
                ):

                    current_time = datetime.now()

                    dose_taken = (
                        med,
                        dose_time
                    ) in today_logs

                    base_alarm = dose_datetime

                    next_alarm = get_next_alarm(
                        st.session_state.current_user,
                        med,
                        dose_time
                    )

                    if next_alarm:

                        alarm_time = datetime.combine(
                            base_alarm.date(),
                            datetime.strptime(
                                next_alarm,
                                "%I:%M %p"
                            ).time()
                        )

                        alarm_time_str = next_alarm

                    else:

                        alarm_time = base_alarm
                        alarm_time_str = dose_time

                    is_snoozed = (
                        next_alarm is not None
                        and next_alarm != dose_time
                    )    

                    remaining = alarm_time - current_time

                    minutes = max(
                        0,
                        int(remaining.total_seconds() // 60)
                    )

                    seconds = max(
                        0,
                        int(remaining.total_seconds() % 60)
                    )

                    missed_time = base_alarm + timedelta(minutes=30)

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

                    is_missed = alert and alert[1] == 1

                    if dose_taken:

                        status = "taken"

                    elif current_time < base_alarm:

                        status = "pending"

                    elif current_time > missed_time:

                        status = "missed"

                    else:

                        status = "pending"

                    show_buttons = (
                        alarm_time <= current_time <= alarm_time + timedelta(minutes=30)
                        and not dose_taken
                        and not is_missed
                        and not is_snoozed
                    )

                    if show_buttons:

                        done_state = f"done_{med}_{dose_time}"

                        if done_state not in st.session_state:

                            st.session_state[done_state] = False

                        if st.button(
                            "✅ Mark Done",
                            key=f"done_{st.session_state.current_user}_{med}_{dose_time}",
                            disabled=st.session_state[done_state]
                        ):

                            st.session_state[done_state] = True

                            if current_time > missed_time:

                                mark_med_done(
                                    st.session_state.current_user,
                                    med,
                                    dose_time,
                                    status="Delayed"
                                )

                                st.warning(
                                    "⚠ Medication recorded as Delayed"
                                )

                            else:

                                mark_med_done(
                                    st.session_state.current_user,
                                    med,
                                    dose_time,
                                    status="Taken"
                                )

                                st.success(
                                    "✅ Medication recorded as Taken"
                                )

                            reset_alert(
                                st.session_state.current_user,
                                med,
                                dose_time
                            )

                            set_next_alarm(
                                st.session_state.current_user,
                                med,
                                dose_time,
                                None
                            )

                            notification_key = f"{med}_{dose_time}"

                            if notification_key in st.session_state.notified_meds:

                                st.session_state.notified_meds.remove(
                                    notification_key
                                )

                            st.session_state[done_state] = False

                            st.rerun()

                        snooze_count = alert[0] if alert else 0

                        st.caption(
                            f"😴 Snoozes used: {snooze_count}/3"
                        )

                        snooze_state = f"snooze_{med}_{dose_time}"

                        if snooze_state not in st.session_state:

                            st.session_state[snooze_state] = False

                        if snooze_count < 3:

                            if st.button(
                                "😴 Snooze",
                                key=f"snooze_{st.session_state.current_user}_{med}_{dose_time}",
                                disabled=st.session_state[snooze_state]
                            ):

                                st.session_state[snooze_state] = True

                                snooze_alert(
                                    st.session_state.current_user,
                                    med,
                                    dose_time
                                )

                                next_time = (
                                    datetime.now()
                                    + timedelta(minutes=5)
                                ).strftime("%I:%M %p")

                                set_next_alarm(
                                    st.session_state.current_user,
                                    med,
                                    dose_time,
                                    next_time,

                                )

                                saved = get_next_alarm(
                                    st.session_state.current_user,
                                    med,
                                    dose_time
                                )

                                st.write("DEBUG Saved Alarm:", saved)

                                active_dose = None

                                st.success(
                                    f"⏱ Snoozed until {next_time}"
                                )

                                st.session_state[snooze_state] = False

                                st.rerun()

                        else:

                            st.error(
                                "⚠ Maximum snoozes reached"
                            )

                    else:

                        if dose_taken:

                            st.success("✅ Completed")

                        elif status == "missed":

                            st.error("❌ Missed")

                        elif is_snoozed:

                            st.warning(
                                f"😴 Snoozed until {alarm_time_str}"
                            )

                            if st.button(
                                "❌ Cancel Snooze",
                                key=f"cancel_{st.session_state.current_user}_{med}_{dose_time}"
                            ):

                                set_next_alarm(
                                    st.session_state.current_user,
                                    med,
                                    dose_time,
                                    None
                                )

                                st.success("✅ Snooze cancelled.")

                                st.rerun()

                            st.warning(
                                f"😴 Snoozed until {alarm_time_str}"
                            )

                            st.progress(
                                max(
                                    0,
                                    min(
                                        1,
                                        1 - (
                                            remaining.total_seconds()
                                            / 300
                                        )
                                    )
                                )
                            )

                            st.caption(
                                f"⏳ Reminder in {minutes}m {seconds}s"
                            )

                        elif current_time < alarm_time:

                            st.info(
                                f"⏰ Scheduled at {alarm_time_str}"
                            )

                    st.divider()

        # ---------------- ADHERENCE ----------------
        total_doses = 0

        for med_data in medicines:
            frequency_hours = med_data[7]

            if frequency_hours:
                total_doses += 24 // frequency_hours
            else:
                total_doses += 1
        
        done = len(today_logs)

        adherence = (
            int((done / total_doses) * 100)
            if total_doses else 0
        )

        adherence = min(adherence, 100)

        st.subheader("📊 Adherence Overview")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("💊 Assigned", total_doses)
        with col2:
            st.metric("✅ Taken", done)
        with col3:
            st.metric("📈 Adherence", f"{adherence}%")                    
        st.progress(adherence / 100)     # Streamlit expects 0–1
        
        st.subheader("⚠ Risk Level")
        if adherence >= 80:
            st.success("🟢 Low Risk")

        elif adherence >= 50:
            st.warning("🟡 Medium Risk")

        else:
            st.error("🔴 High Risk") 


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

        today_logs = [
           (log[0], log[1])
           for log in logs
        if log[2] == today
        ]
        
        # ===========================
        # NEXT MEDICATION TRACKER
        # ===========================

        next_med_name = None
        next_med_dose = None
        next_med_datetime = None

        st.subheader(f"Patient: {selected_patient}")

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
            if (med, time) in today_logs:
                st.success(f"✅ {med} — {time} | {dosage} | {instructions}")
            else:
                st.error(f"❌ {med}")

        total = len(medicines)
        done = len(today_logs)

        adherence = int((done / total) * 100) if total else 0
        adherence = min(adherence, 100)

        st.subheader("📊 Adherence")
        st.progress(adherence / 100)
        st.write(f"{adherence}%")

        st.subheader("⚠ Risk Level")
        st.write(get_risk_label(adherence))



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


        st.subheader("🚨 Emergency Alerts")

        emergencies = get_provider_emergencies(
            st.session_state.current_user
        )

        if emergencies:

            for patient, caregiver, emergency_time, status in emergencies:

                st.error(f"🚨 Emergency from: {patient}")

                if caregiver:
                    st.write(f"👤 Caregiver: {caregiver}")
                else:
                    st.write("👤 No caregiver assigned")

                st.write(f"🕒 Time: {emergency_time}")

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

                        st.success("Emergency marked as resolved.")

                        st.rerun()

                else:

                    st.success("✅ Emergency Resolved")

                st.divider()

                st.divider()

        else:

            st.success("✅ No emergency alerts.")
            

    # ---------------- CAREGIVER ASSIGNMENT ----------------

        st.subheader("👥 Assign Caregiver")

        caregivers = [c[0] for c in get_caregivers()]
        patients_list = [p[0] for p in patients]

        if caregivers:

            caregiver_options = ["None"]

            for c in caregivers:
                caregiver_options.append(c)

            caregiver = st.selectbox(
                "Assign Caregiver (Optional)",
                caregiver_options
            )

            selected_patient_for_caregiver = st.selectbox(
                "Select Patient",
                patients_list,
                key="assign_patient"
            )

            if st.button("Assign Caregiver"):

                if caregiver == "None":

                    assign_caregiver(
                        None,
                        selected_patient_for_caregiver,
                        st.session_state.current_user
                    )

                    st.success(
                        f"Caregiver removed from {selected_patient_for_caregiver}."
                    )

                else:

                    assign_caregiver(
                        caregiver,
                        selected_patient_for_caregiver,
                        st.session_state.current_user
                    )

                    st.success(
                        f"{caregiver} assigned to {selected_patient_for_caregiver}"
                    )

        else:
            st.warning("No caregivers available.")

    # ---------------- PATIENT SELECTION ----------------

        selected_patient = st.selectbox(
            "Patient Record",
            [p[0] for p in patients],
            key="physician_patient"
        )

    # ---------------- ASSIGN MEDICATION ----------------

        st.subheader("💊 Assign Medication")

        dosage = st.text_input(
            "Dosage (e.g. 500mg)",
            key="physician_dosage"
        )

        instructions = st.text_input(
            "Instructions (e.g. after meal)",
            key="physician_instructions"
        )

        med_name = st.text_input(
            "Medicine Name",
            key="physician_med_name"
        )

        hour = st.selectbox(
            "Hour",
            list(range(1, 13)),
            key="physician_hour"
        )

        minute = st.selectbox(
            "Minute",
            [f"{i:02d}" for i in range(60)],
            key="physician_minute"
        )
        
        # Treatment Start Date

        start_date = st.date_input(
            "Treatment Start Date"
        )

        # Duration

        duration = st.number_input(
            "Duration",
            min_value=1,
            value=30
        )

        duration_unit = st.selectbox(
            "Duration Unit",
            [
                "Days",
                "Months"
            ]
        )
        
        if duration_unit == "Days":
            end_date = (
                start_date +
                timedelta(days=duration)
            )

        else:
            end_date = (
                start_date +
                timedelta(days=duration * 30)
            )


        ampm = st.selectbox(
            "AM/PM",
            ["AM", "PM"],
            key="physician_ampm"
        )

        med_time = f"{hour:02d}:{minute} {ampm}"

        frequency_hours = st.selectbox(
           "Take Every",
           [1,2,3,4,6,8,12,24]
        )

        st.caption(
            f"Reminder every {frequency_hours} hours"
        )



        purpose = st.text_area("Purpose")
        how_to_take = st.text_area("How to Take")
        side_effects = st.text_area("Common Side Effects")
        reminders = st.text_area("Important Reminders")



        if "adding_med" not in st.session_state:
            st.session_state.adding_med = False

        if st.button(
            "Assign Medication",
            key="assign_medication_btn",
            disabled=st.session_state.adding_med
        ):

            if med_name:

                st.session_state.adding_med = True
                
                add_medication(
                    patient_username=selected_patient,
                    medicine_name=med_name,
                    time=med_time,
                    dosage=dosage,
                    instructions=instructions,
                    start_date=str(start_date),
                    end_date=str(end_date),
                    start_time=med_time,
                    frequency_hours=frequency_hours,
                    purpose=purpose,
                    how_to_take=how_to_take,
                    side_effects=side_effects,
                    reminders=reminders
                )
               

                st.success("Medication assigned!")
                st.session_state.adding_med = False
                st.rerun()

    # ---------------- MEDICATION LIST ----------------

        st.subheader("📋 Assigned Medications")

        meds = get_medications(selected_patient)

        if not meds:
            st.info("No medications assigned.")
        else:

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
            ) in meds:
                
                today = date.today()

                start = datetime.strptime(
                    start_date,
                    "%Y-%m-%d"
                ).date()

                end = datetime.strptime(
                    end_date,
                    "%Y-%m-%d"
                ).date()

             # Skip expired medications
                if not (start <= today <= end):
                    continue   

                col1, col2 = st.columns([4, 1])

                with col1:
                    st.write(
                        f"{med} — {time} | {dosage} | {instructions}"
                    )

                with col2:

                    if st.button(
                        "❌",
                        key=f"delete_{selected_patient}_{med}_{time}"
                    ):

                        delete_medication(
                            selected_patient,
                            med,
                            time
                        )

                        st.rerun()

    # ---------------- ANALYTICS ----------------

        st.subheader("📊 Patient Analytics")

        logs = get_user_logs(selected_patient)

        if logs:

            df = pd.DataFrame(
                logs,
                columns=["Medicine","Time", "Date", "Status"]
            )

            daily = (
                df.groupby("Date")
                .size()
                .reset_index(name="Taken")
            )

            daily.columns = ["Date", "Taken"]

            st.line_chart(
                daily.set_index("Date")
            )

        else:
            st.info("No adherence history available.")

    # ---------------- ADHERENCE ----------------

        today_logs = [
            (log[0], log[1])
            for log in logs
            if log[2] == str(date.today())
        ]

        total = len(meds)
        done = len(today_logs)

        adherence = (
            int((done / total) * 100)
            if total else 0
    )

        adherence = min(adherence, 100)

        st.write(f"Adherence: {adherence}%")
        st.progress(adherence / 100)

    # ---------------- RISK LEVEL ----------------

        st.subheader("⚠ Risk Level")

        if adherence >= 80:
            st.success("🟢 Low Risk")
        elif adherence >= 50:
            st.warning("🟡 Medium Risk")
        else:
            st.error("🔴 High Risk")

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


        elif page == "🏥 Patient Record":

            st.subheader("👤 Patient Summary")

            caregiver = get_patient_caregiver(selected_patient)

            meds = get_medications(selected_patient)

            logs = get_user_logs(selected_patient)

            today = date.today()
            today_str = str(today)

            current_time = datetime.now()
            
            today_logs = [
                log
                for log in logs
                if log[2] == today_str
            ]

            # ==========================================
            # OVERALL MEDICATION COUNTS
            # ==========================================

            total_scheduled = 0
            taken = 0
            delayed = 0

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

                total_scheduled += len(dose_schedule)

                for dose_time, dose_datetime in dose_schedule:

                    for log in logs:

                        if (
                            log[0] == med_name
                            and log[1] == dose_time
                            and log[2] == str(dose_datetime.date())
                        ):

                            if log[3] == "Taken":
                                taken += 1

                            elif log[3] == "Delayed":
                                delayed += 1

                            break

            adherence = (
                int(
                    ((taken + delayed) / total_scheduled) * 100
                )
                if total_scheduled
                else 0
            )
            
            with st.container(border=True):

                st.subheader(selected_patient)

                st.write(
                    f"👥 Caregiver: {caregiver if caregiver else 'None'}"
                )

                col1, col2 = st.columns(2)

                with col1:

                    st.metric(
                        "Today's Scheduled Doses",
                        today_scheduled
                    )

                with col2:

                    st.metric(
                        "Today's Adherence",
                        f"{adherence}%"
                    )

                col1, col2, col3, col4 = st.columns(4)

                with col1:

                    st.metric(
                        "✅ Taken",
                        taken_today
                    )

                with col2:

                    st.metric(
                        "🟡 Delayed",
                        delayed_today
                    )

                with col3:

                    st.metric(
                        "⏳ Pending",
                        pending_today
                    )

                with col4:

                    st.metric(
                        "❌ Missed",
                        missed_today
                    )

                if adherence >= 90:

                    st.success("🟢 Low Risk")

                elif adherence >= 70:

                    st.warning("🟡 Medium Risk")

                else:

                    st.error("🔴 High Risk")
            
            st.divider()

            st.subheader("💊 Medication Schedule")
            schedule_rows = []
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

                        elif log_found[3] == "Missed":
                            status = "❌ Missed"

                        else:
                            status = "⏳ Pending"

                    else:

                        if dose_datetime.date() > today:

                            status = "🔵 Upcoming"

                        elif current_time > dose_datetime + timedelta(minutes=30):

                            status = "❌ Missed"

                        else:

                            status = "⏳ Pending"

                    schedule_rows.append([

                        med_name,

                        dose_datetime.strftime("%Y-%m-%d"),

                        dose_time,

                        dosage,

                        status

                    ])
            if schedule_rows:

                schedule_df = pd.DataFrame(

                    schedule_rows,

                    columns=[

                        "Medicine",

                        "Date",

                        "Time",

                        "Dosage",

                        "Status"

                    ]

                )

                schedule_df = schedule_df.sort_values(

                    by=["Date", "Time"]

                )

                st.dataframe(

                    schedule_df,

                    use_container_width=True,

                    hide_index=True

                )

            else:

                st.info("No medication schedule available.")        

            st.divider()

            st.subheader("📋 Assigned Medications")
            
            if not meds:

                st.info("No medications assigned.")

            else:

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

                    start = datetime.strptime(
                        start_date,
                        "%Y-%m-%d"
                    ).date()

                    end = datetime.strptime(
                        end_date,
                        "%Y-%m-%d"
                    ).date()

                    if today < start or today > end:
                        continue

                    with st.container(border=True):

                        left,right = st.columns([5,1])

                        with left:
                            st.subheader(f"💊 {med_name}")

                        with right:

                            if st.button(
                                "🗑️",
                                key=f"{selected_patient}_{med_name}_{med_time}"
                            ):

                                delete_medication(
                                    selected_patient,
                                    med_name,
                                    med_time
                                )

                                st.success("Medication deleted.")

                                st.rerun()

                        c1,c2 = st.columns(2)

                        c1.metric(
                            "💉 Dosage",
                            dosage
                        )

                        c2.metric(
                            "⏰ Every",
                            f"{frequency_hours} hr(s)"
                        )

                        st.info(instructions)

                        c3,c4 = st.columns(2)

                        c3.metric(
                            "📅 Start",
                            start_date
                        )

                        c4.metric(
                            "🏁 End",
                            end_date
                        )

                        st.write(f"🎯 Purpose: {purpose}")
                        st.write(f"💊 How to Take: {how_to_take}")
                        st.write(f"⚠ Side Effects: {side_effects}")
                        st.write(f"🔔 Reminders: {reminders}")    