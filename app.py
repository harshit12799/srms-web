import csv
import io
import json
from pathlib import Path

import streamlit as st

DATA_FILE = Path(__file__).parent / "srms_data.json"

st.set_page_config(
    page_title="SRMS • Academic Portal",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown(
    """
    <style>
    .block-container { padding-top: 2rem; max-width: 1200px; }
    .portal-banner {
        background: #ffffff;
        border: 1px solid #d0d7e2;
        border-left: 5px solid #1d4ed8;
        border-radius: 10px;
        padding: 18px 24px;
        margin-bottom: 16px;
    }
    .portal-banner h1 { margin: 0; font-size: 1.6rem; font-weight: 700; color: #0f172a; }
    .portal-banner p { margin: 4px 0 0 0; font-size: 0.92rem; color: #475569; }
    .notice-strip {
        background: #eff6ff;
        border: 1px solid #bfdbfe;
        border-radius: 8px;
        padding: 10px 16px;
        margin-bottom: 12px;
        color: #1e3a8a;
        font-size: 0.92rem;
    }
    .course-card {
        background: #ffffff;
        border: 1px solid #d0d7e2;
        border-radius: 10px;
        padding: 16px;
        margin-bottom: 14px;
        box-shadow: 0 1px 2px rgba(15, 23, 42, 0.05);
    }
    .course-head { display: flex; justify-content: space-between; align-items: center; gap: 8px; }
    .course-title { font-weight: 700; font-size: 1rem; color: #0f172a; }
    .course-sub { font-size: 0.84rem; color: #475569; margin: 4px 0 10px 0; }
    .badge { font-size: 0.72rem; font-weight: 700; padding: 2px 8px; border-radius: 4px; white-space: nowrap; }
    .badge-theory { background: #dbeafe; color: #1e40af; }
    .badge-lab { background: #dcfce7; color: #166534; }
    .meta-row { display: flex; justify-content: space-between; font-size: 0.88rem; color: #0f172a; }
    .bar-bg { width: 100%; height: 7px; background: #e2e8f0; border-radius: 999px; overflow: hidden; margin: 8px 0 12px 0; }
    .bar-fill { height: 100%; }
    .course-foot {
        display: flex; justify-content: space-between; align-items: center;
        border-top: 1px solid #e2e8f0; padding-top: 8px; font-size: 0.82rem; color: #334155;
    }
    .portal-footer {
        text-align: center; color: #64748b; font-size: 0.8rem;
        padding: 20px 0 8px 0; border-top: 1px solid #d0d7e2; margin-top: 28px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def seed_data() -> dict:
    return json.loads(
        """{"students": [{"roll_number": "BTAD26O1011", "name": "Brajmohan Dudve",
        "email": "brajmohan@mitsgwl.ac.in", "dob": "23/12/2007"}],
        "courses": [], "enrolments": []}"""
    )


def save_data(data: dict) -> None:
    DATA_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")


def load_data() -> dict:
    if DATA_FILE.exists():
        try:
            loaded = json.loads(DATA_FILE.read_text(encoding="utf-8"))
            if isinstance(loaded, dict):
                return {
                    "students": loaded.get("students", []),
                    "courses": loaded.get("courses", []),
                    "enrolments": loaded.get("enrolments", []),
                }
        except Exception:
            pass
    initial = seed_data()
    save_data(initial)
    return initial


def compute_grade_and_points(marks: float) -> tuple[str, float]:
    if marks >= 90.0:
        return "A", 10.0
    if marks >= 80.0:
        return "B", 9.0
    if marks >= 70.0:
        return "C", 8.0
    if marks >= 60.0:
        return "D", 7.0
    return "F", 0.0


def calculate_gpa(roll: str, data: dict) -> tuple[float | None, int]:
    credit_map = {c["course_code"]: int(c.get("credits", 3)) for c in data["courses"]}
    weighted_points = 0.0
    total_credits = 0
    for e in data["enrolments"]:
        if e["roll_number"] == roll:
            creds = credit_map.get(e["course_code"], 0)
            _, pts = compute_grade_and_points(float(e["marks"]))
            weighted_points += pts * creds
            total_credits += creds
    if total_credits == 0:
        return None, 0
    return round(weighted_points / total_credits, 2), total_credits


def to_csv(rows: list[dict]) -> str:
    if not rows:
        return ""
    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=list(rows[0].keys()))
    writer.writeheader()
    writer.writerows(rows)
    return buf.getvalue()


if "srms_data" not in st.session_state:
    st.session_state.srms_data = load_data()
if "show_notice" not in st.session_state:
    st.session_state.show_notice = True

data = st.session_state.srms_data
student_names = {s["roll_number"]: s["name"] for s in data["students"]}
course_map = {c["course_code"]: c for c in data["courses"]}
active_student = data["students"][0]["name"] if data["students"] else "Student"

st.markdown(
    f"""
    <div class="portal-banner">
        <h1>Welcome back, {active_student}!</h1>
        <p>Student Record Management System • Session: July–Dec 2026 • Data: srms_data.json</p>
    </div>
    """,
    unsafe_allow_html=True,
)

nav_choice = st.radio(
    "Navigation",
    ["Dashboard", "Students", "Courses", "Enrolment & Marks", "Result Sheet & GPA"],
    horizontal=True,
    label_visibility="collapsed",
)

if st.session_state.show_notice:
    n1, n2 = st.columns([11, 1])
    with n1:
        st.markdown(
            '<div class="notice-strip"><strong>Notice:</strong> Manage student profiles, '
            "courses, enrolments, marks, grades, and semester results.</div>",
            unsafe_allow_html=True,
        )
    with n2:
        if st.button("Hide", key="hide_notice"):
            st.session_state.show_notice = False
            st.rerun()

total_courses = len(data["courses"])
total_enrolments = len(data["enrolments"])
total_attended = sum(int(c.get("attended", 0)) for c in data["courses"])
total_classes = sum(int(c.get("total_classes", 0)) for c in data["courses"])
overall_pct = (total_attended / total_classes * 100.0) if total_classes > 0 else 0.0

all_gpas = [g for g, _ in (calculate_gpa(s["roll_number"], data) for s in data["students"]) if g is not None]
avg_gpa = f"{sum(all_gpas) / len(all_gpas):.2f}" if all_gpas else "—"

k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("Courses", total_courses)
k2.metric("Enrolments", total_enrolments)
k3.metric("Classes Attended", f"{total_attended} / {total_classes}" if total_classes else "0")
k4.metric("Overall Attendance", f"{overall_pct:.1f}%")
k5.metric("Average GPA", avg_gpa)

st.write("")

# ---------------- DASHBOARD ----------------
if nav_choice == "Dashboard":
    left, right = st.columns(2, gap="large")
    with left:
        st.subheader("Course-wise Attendance %")
        if data["courses"]:
            att_data = {
                c["course_title"][:24]: round(int(c.get("attended", 0)) / int(c["total_classes"]) * 100.0, 1)
                for c in data["courses"]
                if int(c.get("total_classes", 0)) > 0
            }
            st.bar_chart(att_data, height=260)
        else:
            st.info("No courses available yet.")
    with right:
        st.subheader("Course-wise Average Marks")
        if data["enrolments"] and data["courses"]:
            marks_data = {}
            for c in data["courses"]:
                vals = [float(e["marks"]) for e in data["enrolments"] if e["course_code"] == c["course_code"]]
                marks_data[c["course_title"][:24]] = round(sum(vals) / len(vals), 1) if vals else 0.0
            st.bar_chart(marks_data, height=260)
        else:
            st.info("No marks recorded yet.")

    st.subheader("My Courses")
    if data["courses"]:
        cols = st.columns(3, gap="medium")
        for idx, c in enumerate(data["courses"]):
            att = int(c.get("attended", 0))
            tot = int(c.get("total_classes", 0))
            pct = (att / tot * 100.0) if tot > 0 else 0.0
            c_type = c.get("course_type", "THEORY")
            badge_cls = "badge-lab" if c_type == "LAB" else "badge-theory"
            bar_color = "#16a34a" if pct >= 75 else ("#d97706" if pct >= 60 else "#dc2626")
            with cols[idx % 3]:
                st.markdown(
                    f"""
                    <div class="course-card">
                        <div class="course-head">
                            <span class="course-title">{c["course_title"]}</span>
                            <span class="badge {badge_cls}">{c_type}</span>
                        </div>
                        <div class="course-sub">Code: {c["course_code"]} • {c.get("credits", 3)} Credits</div>
                        <div class="meta-row">
                            <span>Attendance: <strong>{att}/{tot}</strong></span>
                            <span style="font-weight:700; color:{bar_color};">{pct:.1f}%</span>
                        </div>
                        <div class="bar-bg">
                            <div class="bar-fill" style="width:{min(pct, 100.0):.1f}%; background:{bar_color};"></div>
                        </div>
                        <div class="course-foot">
                            <span>{c.get("faculty", "Assigned Faculty")}</span>
                            <strong>{c.get("semester", "Sem 1")}</strong>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
    else:
        st.info("Add courses in the Courses tab to see cards here.")

# ---------------- STUDENTS ----------------
elif nav_choice == "Students":
    left, right = st.columns([1, 1.5], gap="large")
    with left:
        st.subheader("Add Student")
        with st.form("add_student_form", clear_on_submit=True):
            roll = st.text_input("Roll Number").strip()
            name = st.text_input("Full Name").strip()
            email = st.text_input("Email").strip()
            dob = st.text_input("Date of Birth (dd/mm/yyyy)").strip()
            sub = st.form_submit_button("Save Student")
        if sub:
            existing = {s["roll_number"] for s in data["students"]}
            if not roll or not name or not email or not dob:
                st.error("All student fields are required.")
            elif roll in existing:
                st.error(f"Roll number '{roll}' already exists.")
            else:
                data["students"].append({"roll_number": roll, "name": name, "email": email, "dob": dob})
                save_data(data)
                st.success(f"Added {name} ({roll}).")
                st.rerun()

    with right:
        st.subheader("Registered Students")
        q = st.text_input("Search roll number, name, or email").strip().lower()
        rows = [
            s for s in data["students"]
            if not q or q in s["roll_number"].lower() or q in s["name"].lower() or q in s["email"].lower()
        ]
        if rows:
            st.dataframe(rows, use_container_width=True, hide_index=True)
            st.download_button("Export Students CSV", to_csv(rows), "students.csv", "text/csv")
        else:
            st.info("No student records found.")

        if data["students"]:
            with st.expander("Remove Student"):
                d_roll = st.selectbox("Select Roll Number", [s["roll_number"] for s in data["students"]], key="del_roll_box")
                if st.button("Delete Student", key="del_roll_btn"):
                    data["students"] = [s for s in data["students"] if s["roll_number"] != d_roll]
                    data["enrolments"] = [e for e in data["enrolments"] if e["roll_number"] != d_roll]
                    save_data(data)
                    st.success(f"Removed {d_roll}.")
                    st.rerun()

# ---------------- COURSES ----------------
elif nav_choice == "Courses":
    c_left, c_right = st.columns([1, 1.5], gap="large")
    with c_left:
        st.subheader("Add Course")
        with st.form("add_course_form", clear_on_submit=True):
            code = st.text_input("Course Code").strip()
            title = st.text_input("Course Title").strip()
            c_type = st.selectbox("Type", ["THEORY", "LAB"])
            faculty = st.text_input("Faculty Name", value="Faculty Member").strip()
            semester = st.text_input("Semester", value="Sem 1").strip()
            credits = st.number_input("Credits", min_value=1, max_value=10, value=3, step=1)
            attended = st.number_input("Classes Attended", min_value=0, max_value=500, value=0, step=1)
            total_cls = st.number_input("Total Classes", min_value=1, max_value=500, value=16, step=1)
            c_sub = st.form_submit_button("Save Course")
        if c_sub:
            existing_codes = {c["course_code"] for c in data["courses"]}
            if not code or not title:
                st.error("Course code and title are required.")
            elif code in existing_codes:
                st.error(f"Course code '{code}' already exists.")
            elif attended > total_cls:
                st.error("Attended classes cannot exceed total classes.")
            else:
                data["courses"].append({
                    "course_code": code,
                    "course_title": title,
                    "course_type": c_type,
                    "faculty": faculty or "Assigned Faculty",
                    "semester": semester or "Sem 1",
                    "credits": int(credits),
                    "attended": int(attended),
                    "total_classes": int(total_cls),
                })
                save_data(data)
                st.success(f"Saved course {code} — {title}.")
                st.rerun()

    with c_right:
        st.subheader("Course Catalog")
        if data["courses"]:
            catalog_rows = [
                {
                    "Code": c["course_code"],
                    "Title": c["course_title"],
                    "Type": c.get("course_type", "THEORY"),
                    "Credits": c.get("credits", 3),
                    "Faculty": c.get("faculty", ""),
                    "Semester": c.get("semester", "Sem 1"),
                    "Attendance": f"{c.get('attended', 0)}/{c.get('total_classes', 0)}",
                }
                for c in data["courses"]
            ]
            st.dataframe(catalog_rows, use_container_width=True, hide_index=True)
            with st.expander("Delete Course"):
                d_code = st.selectbox("Select Course Code", [c["course_code"] for c in data["courses"]], key="del_course_box")
                if st.button("Delete Course", key="del_course_btn"):
                    data["courses"] = [c for c in data["courses"] if c["course_code"] != d_code]
                    data["enrolments"] = [e for e in data["enrolments"] if e["course_code"] != d_code]
                    save_data(data)
                    st.success(f"Deleted course {d_code}.")
                    st.rerun()
        else:
            st.info("No courses added yet.")

# ---------------- ENROLMENT & MARKS ----------------
elif nav_choice == "Enrolment & Marks":
    roll_opts = [s["roll_number"] for s in data["students"]]
    course_opts = [c["course_code"] for c in data["courses"]]
    e_col, m_col = st.columns(2, gap="large")

    with e_col:
        st.subheader("Enrol Student in Course")
        if not roll_opts or not course_opts:
            st.warning("Add at least one student and one course first.")
        else:
            with st.form("enrol_form"):
                r_sel = st.selectbox("Student", roll_opts,
                                     format_func=lambda r: f"{r} — {student_names.get(r, '')}")
                c_sel = st.selectbox("Course", course_opts,
                                     format_func=lambda c: f"{c} — {course_map.get(c, {}).get('course_title', '')}")
                e_sub = st.form_submit_button("Enrol Student")
            if e_sub:
                exists = any(e["roll_number"] == r_sel and e["course_code"] == c_sel for e in data["enrolments"])
                if exists:
                    st.error("Student is already enrolled in this course.")
                else:
                    data["enrolments"].append({"roll_number": r_sel, "course_code": c_sel, "marks": 0.0})
                    save_data(data)
                    st.success(f"Enrolled {r_sel} in {c_sel}.")
                    st.rerun()

    with m_col:
        st.subheader("Enter Marks & Compute Grade")
        if not data["enrolments"]:
            st.info("No enrolments available.")
        else:
            labels = [
                f"{e['roll_number']} • {e['course_code']} • current {e['marks']}"
                for e in data["enrolments"]
            ]
            with st.form("marks_form"):
                sel_idx = st.selectbox("Enrolment", range(len(labels)), format_func=lambda i: labels[i])
                cur_marks = float(data["enrolments"][sel_idx]["marks"])
                new_marks = st.number_input("Marks (0–100)", min_value=0.0, max_value=100.0,
                                            value=cur_marks, step=0.5)
                m_sub = st.form_submit_button("Update Marks")
            if m_sub:
                data["enrolments"][sel_idx]["marks"] = float(new_marks)
                g, p = compute_grade_and_points(float(new_marks))
                save_data(data)
                st.success(f"Updated marks to {new_marks:.1f} → Grade {g} ({p:.1f} pts)")
                st.rerun()

# ---------------- RESULT SHEET & GPA ----------------
elif nav_choice == "Result Sheet & GPA":
    st.subheader("Semester Result Sheet")
    roll_filter = st.selectbox("Filter by Student", ["All Students"] + [s["roll_number"] for s in data["students"]])

    result_rows = []
    for e in data["enrolments"]:
        r = e["roll_number"]
        if roll_filter != "All Students" and r != roll_filter:
            continue
        c_obj = course_map.get(e["course_code"], {})
        credits = int(c_obj.get("credits", 3))
        m = float(e["marks"])
        grade, pts = compute_grade_and_points(m)
        result_rows.append({
            "Roll No.": r,
            "Student": student_names.get(r, "Unknown"),
            "Course Code": e["course_code"],
            "Course Title": c_obj.get("course_title", "Unknown"),
            "Credits": credits,
            "Marks": round(m, 1),
            "Grade": grade,
            "Grade Points": round(pts, 1),
            "Weighted Points": round(pts * credits, 1),
        })

    if result_rows:
        st.dataframe(result_rows, use_container_width=True, hide_index=True)
        st.download_button("Download Result Sheet CSV", to_csv(result_rows),
                           "semester_result_sheet.csv", "text/csv")
    else:
        st.info("No enrolment records to display.")

    st.divider()
    st.subheader("GPA Calculator")
    if data["students"]:
        gpa_target = st.selectbox("Select Student", [s["roll_number"] for s in data["students"]],
                                  format_func=lambda r: f"{r} — {student_names.get(r, '')}",
                                  key="gpa_target_box")
        gpa_val, creds_sum = calculate_gpa(gpa_target, data)
        if gpa_val is not None:
            st.success(f"{student_names.get(gpa_target, gpa_target)} ({gpa_target}) — "
                       f"GPA: {gpa_val:.2f} / 10.0 across {creds_sum} credits")
        else:
            st.info("No enrolled courses found for this student.")
    else:
        st.info("Add a student to calculate GPA.")

st.markdown(
    '<div class="portal-footer">Student Record Management System • Academic Microproject Portal</div>',
    unsafe_allow_html=True,
)
