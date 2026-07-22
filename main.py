import streamlit as st
import pandas as pd
from datetime import datetime, date, time, timedelta

# إعداد الصفحة
st.set_page_config(
    page_title="نظام إدارة الموارد البشرية", 
    page_icon="🏢", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- تنسيق CSS مخصص لتنسيق الواجهة والعناصر ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;500;600;700;800&display=swap');
    
    html, body, [class*="css"], div, span, p, label, input, textarea {
        font-family: 'Cairo', sans-serif !important;
        direction: rtl !important;
        text-align: right !important;
    }
    
    .stApp {
        background: radial-gradient(circle at center, #1b3a60 0%, #081325 100%) !important;
    }

    section[data-testid="stSidebar"] {
        background-color: #0d1b2a !important;
        border-left: 1px solid #1e293b;
    }

    section[data-testid="stSidebar"] * {
        color: #f8fafc !important;
    }

    .login-box-wrapper {
        background-color: #ffffff;
        padding: 35px 30px;
        border-radius: 16px;
        box-shadow: 0 15px 35px rgba(0, 0, 0, 0.3);
        max-width: 450px;
        margin: 40px auto;
        color: #1e293b;
    }

    .login-box-wrapper h3 {
        text-align: center;
        color: #0f172a;
        font-weight: 800;
        margin-bottom: 5px;
    }

    .login-box-wrapper p {
        text-align: center;
        color: #64748b;
        font-size: 0.9rem;
        margin-bottom: 20px;
    }

    /* تنسيق كارد المعلومات */
    .info-card-container {
        background: rgba(13, 27, 42, 0.75);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 14px;
        padding: 20px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        margin-bottom: 20px;
    }

    .info-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 12px 15px;
        border-bottom: 1px solid rgba(255, 255, 255, 0.08);
    }

    .info-row:last-child {
        border-bottom: none;
    }

    .info-label {
        color: #94a3b8;
        font-weight: 600;
        font-size: 0.95rem;
    }

    .info-value {
        color: #f8fafc;
        font-weight: 700;
        font-size: 1.05rem;
    }

    div.stButton > button {
        border-radius: 10px !important;
        font-weight: 700 !important;
        transition: all 0.3s ease !important;
    }
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

DEPARTMENTS = ["قسم الحسابات", "قسم الموارد البشرية", "قسم تقنية المعلومات", "القسم القانوني"]
QUALIFICATIONS = ["دكتوراه", "ماجستير", "بكالوريوس", "دبلوم عالي", "دبلوم", "إعدادية فما دون"]
ANNUAL_LEAVE_ENTITLEMENT = 36

# --- قاعدة البيانات المركزية ---
if "admin_credentials" not in st.session_state:
    st.session_state.admin_credentials = {
        "assistant": {"pass": "1234", "role": "assistant", "dept": "الكل", "name": "المعاون العام"},
        "head_hr": {"pass": "1234", "role": "manager", "dept": "قسم الموارد البشرية", "name": "مسؤول الموارد البشرية"},
        "head_it": {"pass": "1234", "role": "manager", "dept": "قسم تقنية المعلومات", "name": "مسؤول تقنية المعلومات"}
    }

if "hr_records" not in st.session_state:
    st.session_state.hr_records = {
        "1001": {
            "name": "أحمد علي حسين",
            "department": "قسم تقنية المعلومات",
            "password": "",
            "job_title": "مبرمج رئيسي",
            "qualification": "دكتوراه",
            "academic_title": "أستاذ مساعد",
            "grade": "الرابعة",
            "step": "المرحلة 3",
            "current_allowance_date": "2027-01-15",
            "new_grade_step": "الرابعة / المرحلة 4",
            "new_allowance_date": "2028-01-15",
            "last_promotion_date": "2024-06-01",
            "new_promotion_date": "2029-06-01",
            "leave_used_days": 9,
            "hourly_leave_accumulated": 3.0,
            "leave_cumulative": 65
        },
        "1002": {
            "name": "سارة محمود خليل",
            "department": "قسم الموارد البشرية",
            "password": "",
            "job_title": "معاون مدير شعبة",
            "qualification": "ماجستير",
            "academic_title": "مدرس",
            "grade": "الخامسة",
            "step": "المرحلة 1",
            "current_allowance_date": "2026-11-10",
            "new_grade_step": "الخامسة / المرحلة 2",
            "new_allowance_date": "2027-11-10",
            "last_promotion_date": "2023-03-20",
            "new_promotion_date": "2028-03-20",
            "leave_used_days": 4,
            "hourly_leave_accumulated": 1.5,
            "leave_cumulative": 30
        }
    }

if "requests" not in st.session_state:
    st.session_state.requests = []

if "logged_emp" not in st.session_state:
    st.session_state.logged_emp = None

if "logged_admin" not in st.session_state:
    st.session_state.logged_admin = None

if "emp_step" not in st.session_state:
    st.session_state.emp_step = 1

if "current_portal" not in st.session_state:
    st.session_state.current_portal = "🚪 بوابة الموظف"


# --- الشريط العلوي للتحويل بين البوابات ---
col_top_space, col_top_btn = st.columns([3, 1])
with col_top_btn:
    if st.session_state.current_portal == "🚪 بوابة الموظف":
        if st.button("🔑 بوابة دخول المدير", use_container_width=True):
            st.session_state.current_portal = "🔑 بوابة دخول المدير"
            st.rerun()
    else:
        if st.button("🚪 بوابة الموظفين", use_container_width=True):
            st.session_state.current_portal = "🚪 بوابة الموظف"
            st.rerun()

portal = st.session_state.current_portal

# ==============================================================================
# 👤 1. بوابة الموظف
# ==============================================================================
if portal == "🚪 بوابة الموظف":
    if st.session_state.logged_emp is None:
        _, center_col, _ = st.columns([1, 1.2, 1])
        with center_col:
            st.markdown("""
                <div class="login-box-wrapper">
                    <h3>👤 بوابة الموظفين</h3>
                    <p>يرجى إدخال الرقم الوظيفي للمتابعة</p>
                </div>
            """, unsafe_allow_html=True)
            
            emp_id = st.text_input("الرقم الوظيفي", placeholder="أدخل الرقم الوظيفي هنا", label_visibility="collapsed")
            
            if emp_id:
                records = st.session_state.hr_records
                if emp_id in records:
                    user_info = records[emp_id]
                    if user_info["password"] == "":
                        if st.session_state.emp_step == 1:
                            st.success(f"أهلاً بك **{user_info['name']}**")
                            if st.button("إنشاء كلمة السر الأولى", type="primary", use_container_width=True):
                                st.session_state.emp_step = 2
                                st.rerun()
                        elif st.session_state.emp_step == 2:
                            new_pass = st.text_input("كلمة السر الجديدة", type="password")
                            confirm_pass = st.text_input("تأكيد كلمة السر", type="password")
                            if st.button("حفظ ودخول", type="primary", use_container_width=True):
                                if new_pass and new_pass == confirm_pass:
                                    user_info["password"] = new_pass
                                    st.session_state.logged_emp = emp_id
                                    st.session_state.emp_step = 1
                                    st.rerun()
                                else:
                                    st.error("كلمتا السر غير متطابقتين أو فارغتين.")
                    else:
                        input_pass = st.text_input("كلمة السر", type="password", placeholder="أدخل كلمة السر")
                        if st.button("دخول النظام", type="primary", use_container_width=True):
                            if input_pass == user_info["password"]:
                                st.session_state.logged_emp = emp_id
                                st.rerun()
                            else:
                                st.error("كلمة السر خطأ.")
                else:
                    st.warning("الرقم الوظيفي غير مسجل.")
    else:
        current_user = st.session_state.logged_emp
        user_data = st.session_state.hr_records[current_user]
        
        st.sidebar.markdown(f"### 👤 {user_data['name']}")
        st.sidebar.caption(f"🏢 {user_data['department']}")
        st.sidebar.markdown("---")
        
        menu = st.sidebar.radio("القائمة:", ["📊 استحقاقاتي ورصيدي", "📝 تقديم طلب إجازة", "📄 تقديم طلب تأييد", "📂 سجل طلباتي"])
        st.sidebar.markdown("---")
        if st.sidebar.button("🚪 خروج", use_container_width=True):
            st.session_state.logged_emp = None
            st.rerun()
            
        st.markdown(f"## {menu}")
        st.markdown("---")
        
        used_days = user_data.get("leave_used_days", 0)
        remaining_days = max(0, ANNUAL_LEAVE_ENTITLEMENT - used_days)
        cumulative_balance = user_data.get("leave_cumulative", 0)

        if menu == "📊 استحقاقاتي ورصيدي":
            qual_val = user_data.get("qualification", "-")
            acad_val = user_data.get("academic_title", "")
            
            # عرض الحقول بالترتيب المطلوب مع تعديل تسمية اللقب العلمي بناءً على طلبك
            st.markdown('<div class="info-card-container">', unsafe_allow_html=True)
            
            st.markdown(f'''
                <div class="info-row">
                    <span class="info-label">الاسم:</span>
                    <span class="info-value">{user_data['name']}</span>
                </div>
            ''', unsafe_allow_html=True)
            
            st.markdown(f'''
                <div class="info-row">
                    <span class="info-label">مكان العمل:</span>
                    <span class="info-value">{user_data['department']}</span>
                </div>
            ''', unsafe_allow_html=True)
            
            st.markdown(f'''
                <div class="info-row">
                    <span class="info-label">الرقم الوظيفي:</span>
                    <span class="info-value">{current_user}</span>
                </div>
            ''', unsafe_allow_html=True)
            
            st.markdown(f'''
                <div class="info-row">
                    <span class="info-label">الشهادة:</span>
                    <span class="info-value">{qual_val}</span>
                </div>
            ''', unsafe_allow_html=True)
            
            st.markdown(f'''
                <div class="info-row">
                    <span class="info-label">العنوان الوظيفي:</span>
                    <span class="info-value">{user_data.get('job_title', '-')}</span>
                </div>
            ''', unsafe_allow_html=True)
            
            if qual_val in ["دكتوراه", "ماجستير"]:
                st.markdown(f'''
                    <div class="info-row">
                        <span class="info-label">اللقب العلمي:</span>
                        <span class="info-value">{acad_val if acad_val else "-"}</span>
                    </div>
                ''', unsafe_allow_html=True)
                
            st.markdown(f'''
                <div class="info-row">
                    <span class="info-label">الدرجة والمرحلة الحالية:</span>
                    <span class="info-value">{user_data['grade']} / {user_data['step']}</span>
                </div>
            ''', unsafe_allow_html=True)
            
            st.markdown(f'''
                <div class="info-row">
                    <span class="info-label">تاريخ الاستحقاق الحالي:</span>
                    <span class="info-value">{user_data.get('current_allowance_date', '-')}</span>
                </div>
            ''', unsafe_allow_html=True)
            
            st.markdown(f'''
                <div class="info-row">
                    <span class="info-label">الدرجة والمرحلة الجديدة:</span>
                    <span class="info-value">{user_data.get('new_grade_step', '-')}</span>
                </div>
            ''', unsafe_allow_html=True)
            
            st.markdown(f'''
                <div class="info-row">
                    <span class="info-label">تاريخ الاستحقاق الجديد:</span>
                    <span class="info-value">{user_data.get('new_allowance_date', '-')}</span>
                </div>
            ''', unsafe_allow_html=True)
            
            st.markdown(f'''
                <div class="info-row">
                    <span class="info-label">تاريخ اخر ترفيع:</span>
                    <span class="info-value">{user_data.get('last_promotion_date', '-')}</span>
                </div>
            ''', unsafe_allow_html=True)
            
            st.markdown(f'''
                <div class="info-row">
                    <span class="info-label">تاريخ الترفيع الجديد:</span>
                    <span class="info-value">{user_data.get('new_promotion_date', '-')}</span>
                </div>
            ''', unsafe_allow_html=True)
            
            st.markdown(f'''
                <div class="info-row">
                    <span class="info-label">الاجازات الاعتيادية المستخدمة:</span>
                    <span class="info-value">{used_days} يوم</span>
                </div>
            ''', unsafe_allow_html=True)
            
            st.markdown(f'''
                <div class="info-row">
                    <span class="info-label">الاجازات الاعتيادية المتبقية:</span>
                    <span class="info-value">{remaining_days} يوم</span>
                </div>
            ''', unsafe_allow_html=True)
            
            st.markdown(f'''
                <div class="info-row">
                    <span class="info-label">الرصيد المتراكم:</span>
                    <span class="info-value">{cumulative_balance} يوم</span>
                </div>
            ''', unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)

        elif menu == "📝 تقديم طلب إجازة":
            leave_category = st.radio("النوع:", ["⏱️ زمنية (ساعات)", "📅 اعتيادية (أيام)"], horizontal=True)
            
            if leave_category == "⏱️ زمنية (ساعات)":
                st.info("ℹ️ الدوام الرسمي يبدأ من الساعة 8:00 صباحاً ولغاية 3:00 عصراً. وللموظف الحق بحد أقصى ساعتين باليوم.")
                leave_date = st.date_input("تاريخ الإجازة الزمنية", value=date.today())
                col_t1, col_t2 = st.columns(2)
                with col_t1:
                    time_from = st.time_input("من ساعة", value=time(8, 0))
                with col_t2:
                    time_to = st.time_input("إلى ساعة", value=time(10, 0))
                
                start_datetime = datetime.combine(date.today(), time_from)
                end_datetime = datetime.combine(date.today(), time_to)
                duration_hours = (end_datetime - start_datetime).total_seconds() / 3600.0
                reason = st.text_area("السبب")
                
                if st.button("إرسال الطلب", type="primary"):
                    if duration_hours < 0.5:
                        st.error("خطأ: الحد الأدنى للإجازة الزمنية هو نصف ساعة.")
                    elif duration_hours > 2.0:
                        st.error("خطأ: الحد الأقصى للإجازة الزمنية هو ساعتان.")
                    else:
                        st.session_state.requests.append({
                            "username": current_user, "employee_name": user_data['name'],
                            "department": user_data['department'], "type": "إجازة (زمنية)",
                            "date_submitted": datetime.now().strftime("%Y-%m-%d %H:%M"),
                            "details": {"تاريخ الإجازة": str(leave_date), "من ساعة": str(time_from), "إلى ساعة": str(time_to), "السبب": reason}, 
                            "status": "بانتظار موافقة المسؤول المباشر"
                        })
                        st.success("تم إرسال الطلب بنجاح!")

            else:
                col_d1, col_d2 = st.columns(2)
                with col_d1:
                    date_from = st.date_input("من يوم", value=date.today())
                with col_d2:
                    date_to = st.date_input("إلى يوم", value=date.today())
                num_days = max(1, (date_to - date_from).days + 1)
                reason = st.text_area("السبب")
                
                if st.button("إرسال الطلب", type="primary"):
                    st.session_state.requests.append({
                        "username": current_user, "employee_name": user_data['name'],
                        "department": user_data['department'], "type": "إجازة (اعتيادية)",
                        "date_submitted": datetime.now().strftime("%Y-%m-%d %H:%M"),
                        "details": {"من يوم": str(date_from), "إلى يوم": str(date_to), "عدد الأيام": num_days, "السبب": reason}, 
                        "status": "بانتظار موافقة المسؤول المباشر"
                    })
                    st.success("تم إرسال الطلب بنجاح!")

        elif menu == "📄 تقديم طلب تأييد":
            purpose = st.text_input("الغرض من التأييد")
            salary_option = st.selectbox("الراتب", ["مع الراتب", "بدون راتب"])
            if st.button("إرسال التأييد", type="primary"):
                st.session_state.requests.append({
                    "username": current_user, "employee_name": user_data['name'],
                    "department": user_data['department'], "type": "طلب تأييد",
                    "date_submitted": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "details": {"الغرض": purpose, "الراتب": salary_option}, 
                    "status": "بانتظار موافقة المسؤول المباشر"
                })
                st.success("تم إرسال طلب التأييد بنجاح!")

        elif menu == "📂 سجل طلباتي":
            for req in [r for r in st.session_state.requests if r["username"] == current_user]:
                with st.expander(f"{req['type']} - الحالة: `{req['status']}`"):
                    st.json(req['details'])

# ==============================================================================
# 🔑 2. بوابة دخول المدير
# ==============================================================================
elif portal == "🔑 بوابة دخول المدير":
    if st.session_state.logged_admin is None:
        _, center_col, _ = st.columns([1, 1.2, 1])
        with center_col:
            st.markdown("""
                <div class="login-box-wrapper">
                    <h3>🔑 بوابة دخول المدير</h3>
                    <p>صلاحيات الإدارة والمسؤولين</p>
                </div>
            """, unsafe_allow_html=True)
            
            admin_user = st.text_input("اسم المستخدم")
            admin_pass = st.text_input("كلمة المرور", type="password")
            
            if st.button("تسجيل الدخول", type="primary", use_container_width=True):
                admins = st.session_state.admin_credentials
                if admin_user in admins and admins[admin_user]["pass"] == admin_pass:
                    st.session_state.logged_admin = admin_user
                    st.rerun()
                else:
                    st.error("بيانات الدخول غير صحيحة.")
    else:
        admin_info = st.session_state.admin_credentials[st.session_state.logged_admin]
        pending_requests = [r for r in st.session_state.requests if r['status'] == ("بانتظار موافقة المسؤول المباشر" if admin_info["role"] == "manager" else "بانتظار مصادقة المعاون العام")]
        pending_count = len(pending_requests)

        st.sidebar.markdown(f"### 🛠️ {admin_info['name']}")
        st.sidebar.markdown(f"📌 الصلاحية: `{admin_info['role']}`")
        st.sidebar.markdown("---")
        
        admin_menu_options = [f"🔔 الطلبات المعلقة ({pending_count})"]
        if admin_info["role"] == "assistant":
            admin_menu_options += ["➕ إضافة موظف جديد", "👥 عرض وسجل الموظفين", "⚙️ إدارة وتعديل وحذف الموظفين", "🔑 إدارة الحسابات والصلاحيات", "📥 استيراد الموظفين من Excel"]
            
        admin_menu = st.sidebar.radio("القائمة:", admin_menu_options)
        st.sidebar.markdown("---")
        if st.sidebar.button("🚪 خروج", use_container_width=True):
            st.session_state.logged_admin = None
            st.rerun()

        st.markdown(f"## {admin_menu}")
        st.markdown("---")

        if "الطلبات المعلقة" in admin_menu:
            pending_found = False
            for idx, req in enumerate(st.session_state.requests):
                is_mgr = (admin_info["role"] == "manager" and req['status'] == "بانتظار موافقة المسؤول المباشر")
                is_ast = (admin_info["role"] == "assistant" and req['status'] == "بانتظار مصادقة المعاون العام")
                if is_mgr or is_ast:
                    pending_found = True
                    with st.container():
                        st.markdown(f"📌 **الموظف:** {req['employee_name']} | **القسم:** {req['department']} | **نوع الطلب:** `{req['type']}`")
                        st.json(req['details'])
                        c1, c2 = st.columns(2)
                        with c1:
                            if st.button("✅ موافقة", key=f"app_{idx}", type="primary"):
                                req['status'] = "مقبول ومصادق عليه نهائياً" if admin_info["role"] == "assistant" else "بانتظار مصادقة المعاون العام"
                                st.success("تم تحديث حالة الطلب بنجاح!")
                                st.rerun()
                        with c2:
                            if st.button("❌ رفض", key=f"rej_{idx}"):
                                req['status'] = "مرفوض"
                                st.rerun()
            if not pending_found:
                st.success("لا توجد طلبات معلقة.")

        elif admin_menu == "➕ إضافة موظف جديد":
            c1, c2 = st.columns(2)
            with c1:
                new_emp_id = st.text_input("الرقم الوظيفي")
                new_name = st.text_input("اسم الموظف الثلاثي")
                new_dept = st.selectbox("القسم", DEPARTMENTS)
                new_qual = st.selectbox("الشهادة", QUALIFICATIONS)
            with c2:
                new_title = st.text_input("العنوان الوظيفي")
                new_grade = st.text_input("الدرجة الوظيفية")
                new_acad_title = st.text_input("اللقب العلمي") if new_qual in ["دكتوراه", "ماجستير"] else ""

            if st.button("حفظ الموظف", type="primary", use_container_width=True):
                if new_emp_id and new_name:
                    st.session_state.hr_records[new_emp_id] = {
                        "name": new_name, "department": new_dept, "password": "",
                        "job_title": new_title, "qualification": new_qual, "academic_title": new_acad_title,
                        "grade": new_grade, "step": "المرحلة 1", "current_allowance_date": str(date.today()),
                        "new_grade_step": "", "new_allowance_date": "", "last_promotion_date": "",
                        "new_promotion_date": "", "leave_used_days": 0, "hourly_leave_accumulated": 0.0, "leave_cumulative": 0
                    }
                    st.success("تمت الإضافة بنجاح!")

        elif admin_menu == "👥 عرض وسجل الموظفين":
            data_list = [{"الرقم الوظيفي": k, "الاسم": v["name"], "مكان العمل": v["department"], "الشهادة": v["qualification"]} for k, v in st.session_state.hr_records.items()]
            st.dataframe(pd.DataFrame(data_list), use_container_width=True)

        elif admin_menu == "⚙️ إدارة وتعديل وحذف الموظفين":
            records = st.session_state.hr_records
            if records:
                sel_id = st.selectbox("اختر الموظف:", options=list(records.keys()), format_func=lambda x: f"{x} - {records[x]['name']}")
                emp = records[sel_id]
                with st.form("edit_form"):
                    ed_name = st.text_input("الاسم", value=emp['name'])
                    ed_curr_allow = st.text_input("تاريخ الاستحقاق الحالي", value=emp.get('current_allowance_date', ''))
                    ed_new_allow = st.text_input("تاريخ الاستحقاق الجديد", value=emp.get('new_allowance_date', ''))
                    if st.form_submit_button("حفظ التعديلات"):
                        emp['name'] = ed_name
                        emp['current_allowance_date'] = ed_curr_allow
                        emp['new_allowance_date'] = ed_new_allow
                        st.success("تم التعديل بنجاح!")
                        st.rerun()

        elif admin_menu == "🔑 إدارة الحسابات والصلاحيات":
            st.info("إدارة حسابات المسؤولين الإداريين بالصلاحيات الكاملة.")

        elif admin_menu == "📥 استيراد الموظفين من Excel":
            uploaded_file = st.file_uploader("اختر ملف إكسل", type=["xlsx", "xls"])
            if uploaded_file:
                st.success("تم تحميل الملف بنجاح.")