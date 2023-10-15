# Hospital-Management-System

A web application designed for a hospital management system. The system registers patients, schedules appointment with doctors, maintains patient information about diagnostics tests and treatments administered, maintains information about doctors’/healthcare professionals, stores admit/discharge information about the patients.

Intended users are:
Front Desk Operators: registers/admits/discharges patients
Data Entry Operators: enters patient data about tests and treatments Doctors: query patient information
Database Administrators: add/delete users

Functional Requirements:
The system  supports the following workflow:
1. Patient registration/discharge and doctor appointment/test scheduling – information about new patients need to be registered, appointments based on availability and priority should be scheduled, doctor should be notified about the appointments in a dashboard. For admitted patients a room should be assigned based on available room capacity. For discharged patients information should be preserved but room occupancy should be updated. The workflow should also support scheduling tests and treatments prescribed by doctors. 
2. Patient data entry – All the health information of a patient including test results and treatments administered should be recorded. ( supporting storage and display of images e.g., x-ray)
3. Doctor dashboard – all the records of the patients treated by a doctor should be displayed to his/her as a dashboard. Doctor may also query for any patient information. Doctor should be able to record drugs/treatments prescribed to a patien and also sends automated email reports to a doctor about the health information of patients treated by his/her on a weekly basis
4. Database administration – should be able to add/delete new users 
