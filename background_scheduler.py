from datetime import datetime, timedelta
import time

from database import (
    get_patients,
    get_medications,
    get_user_logs,
    generate_dose_schedule,
    get_user_phone,
    get_caregiver_phone,
    get_provider_phone,
    sms_already_sent,
    log_sms
)

from sms_service import send_sms

def check_medication_reminders():

    patients = get_patients()

    current_time = datetime.now()


    for patient in patients:

        username = patient[0]

        medicines = get_medications(username)

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


                # only today
                if dose_datetime.date() != current_time.date():
                    continue


                # reminder window
                if (
                    current_time >= dose_datetime
                    and current_time <= dose_datetime + timedelta(minutes=1)
                ):


                    if not sms_already_sent(
                        username,
                        med,
                        dose_time,
                        "REMINDER"
                    ):


                        patient_phone = get_user_phone(
                            username
                        )


                        caregiver_phone = get_caregiver_phone(
                            username
                        )


                        message = (
                            f"Reminder: Time to take {med} "
                            f"scheduled at {dose_time}."
                        )


                        if patient_phone:

                            send_sms(
                                patient_phone,
                                message
                            )


                        if caregiver_phone:

                            send_sms(
                                caregiver_phone,
                                f"{username} should now take {med}."
                            )


                        log_sms(
                            username,
                            med,
                            dose_time,
                            "REMINDER"
                        )

def check_missed_medications():

    patients = get_patients()

    current_time = datetime.now()


    for patient in patients:


        username = patient[0]


        medicines = get_medications(username)

        logs = get_user_logs(username)



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



                # only check today's medications

                if dose_datetime.date() != datetime.today().date():

                    continue



                # check if already taken

                log_found = next(
                    (
                        l for l in logs
                        if l[0] == med
                        and l[1] == dose_time
                        and l[2] == str(datetime.today().date())
                    ),
                    None
                )



                if log_found:

                    continue



                # missed after 30 minutes

                if current_time > dose_datetime + timedelta(minutes=30):



                    if not sms_already_sent(
                        username,
                        med,
                        dose_time,
                        "MISSED"
                    ):



                        caregiver_phone = get_caregiver_phone(
                            username
                        )


                        provider_phone = get_provider_phone(
                            username
                        )


                        patient_phone = get_user_phone(
                            username
                        )



                        message = (
                            f"Medication Alert:\n"
                            f"{username} missed {med} "
                            f"scheduled at {dose_time}."
                        )



                        if patient_phone:

                            send_sms(
                                patient_phone,
                                message
                            )


                        if caregiver_phone:

                            send_sms(
                                caregiver_phone,
                                message
                            )


                        if provider_phone:

                            send_sms(
                                provider_phone,
                                message
                            )



                        log_sms(
                            username,
                            med,
                            dose_time,
                            "MISSED"
                        )

while True:

    try:

        check_medication_reminders()

        check_missed_medications()


        print(
            "Medication checker running..."
        )


    except Exception as e:

        print(
            "Error:",
            e
        )


    time.sleep(60)