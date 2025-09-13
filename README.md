# PROJECT-KT

---
A Streamlit-based student portal with separate admin and student interfaces. Features include authentication, student ATKT prediction, student record search, attendance and marks visualization, messaging, broadcast announcements, and auto-generated student ID cards with QR codes.
---

## Student Portal – Streamlit App

This project is a **web-based student portal** built using **Streamlit**. It provides separate interfaces for **students** and **administrators (admin)** with authentication, dashboards, and communication features.

### 🔑 Features

#### **Authentication**

* Admin login.
* Student login.
* Help request option for forgotten credentials.

#### **Admin Interface**

* Search student records by roll number or name.
* View complete student marks table.
* Broadcast announcements to all students.
* Review login help requests from students.

#### **Student Interface**

* **Bottom navigation bar** with:

  * 🏠 Home → Attendance, Subject-Performance dashboard.
  * 💬 Message → Send messages to admin and get hier queries solve directly from admin.
  * 🪪 Student ID → Auto-generated ID card with QR code of PSID.
  * 🔔 Broadcast → Read-only admin announcements.
  * 👤 Personal Info → Student details and logout option.

#### **Utilities**

* Student dataset with auto-generated personal info, marks, and attendance.
* Messaging system between students and admin.
* Broadcast management for announcements.
* QR code generator for student ID.

### 🛠 Tech Stack

* **Frontend/Backend:** [Streamlit](https://streamlit.io/)
* **Data Handling:** Pandas, NumPy
* **Database:** Firebase, firebase_admin, firestore
* **Machine-Learning Algorithm:** RandomForest, Hypertuning, Caliberation, Thresold
* **Visualization:** Altair, Streamlit Charts
* **Extras:** QRCode (for student IDs), Pillow

### 📂 Project Structure

```
.
├── app.py             # Main entry point (runs admin/student interface)
├── auth.py            # Authentication + record fetching
├── admin_view.py      # Admin dashboard interface
├── student_view.py    # Student dashboard interface
├── init_data.py       # Data initialization (students, marks, attendance, etc.)
├── Final_RF_SMOTE_Model.pkl   # ML model (future performance prediction)
├── pydb-*.json        # Firebase service account key (for DB integration)
```

### 🚀 Future Enhancements

* Firebase integration for persistent storage.
* Machine learning model for predicting student performance.
* Real-time chat between students and admin.
* Improved UI/UX with advanced theming.

---
### License
This project is licensed under the MIT License.


