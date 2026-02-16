# # import streamlit as st
# # import requests

# # st.title("🤖 Python Gemini Chatbot")

# # # 1. Create a text box for user input
# # user_topic = st.text_input("insert your topic:")

# # # 2. Create a button to send the request
# # if st.button("Send"):
# #     if user_topic:
# #         with st.spinner("Thinking..."):
# #             try:
# #                 # 3. Send the data to your FastAPI backend
# #                 api_url = "http://127.0.0.1:8000/chat_topic"
# #                 payload = {"topic": user_topic}
                
# #                 response = requests.post(api_url, json=payload)
                
# #                 # 4. Display the result
# #                 if response.status_code == 200:
# #                     data = response.json()

# #                     st.subheader("Easy")
# #                     st.info(data.get("easy", ""))
# #                     user_easy_answer = st.text_area("Your answer for EASY:")

# #                     st.subheader("Medium")
# #                     st.info(data.get("medium", ""))
# #                     user_medium_answer = st.text_area("Your answer for MEDIUM:")

# #                     st.subheader("Hard")
# #                     st.info(data.get("hard", ""))
# #                     user_hard_answer = st.text_area("Your answer for HARD:")

# #                 else:
# #                     st.error(f"Error: {response.status_code}")
                    
# #             except requests.exceptions.ConnectionError:
# #                 st.error("Could not connect to backend. Is uvicorn running?")
# #     else:
# #         st.warning("Please enter a prompt.")

# # import streamlit as st
# # import requests

# # st.set_page_config(layout="wide")  # מאפשר תצוגה רחבה לשאלות בשורה

# # st.title("🤖 Python Gemini Chatbot")

# # # נשתמש ב-session_state כדי להסתיר את ה-input אחרי שליחה
# # if "questions" not in st.session_state:
# #     st.session_state.questions = None

# # # אם עדיין אין שאלות – מציגים את שדה ה-topic
# # if st.session_state.questions is None:
# #     user_topic = st.text_input("Insert your topic:")

# #     if st.button("Send"):
# #         if user_topic:
# #             with st.spinner("Thinking..."):
# #                 try:
# #                     api_url = "http://127.0.0.1:8000/chat_topic"
# #                     payload = {"topic": user_topic}

# #                     response = requests.post(api_url, json=payload)

# #                     if response.status_code == 200:
# #                         st.session_state.questions = response.json()
# #                         st.rerun()
# #                     else:
# #                         st.error(f"Error: {response.status_code}")

# #                 except requests.exceptions.ConnectionError:
# #                     st.error("Could not connect to backend. Is uvicorn running?")
# #         else:
# #             st.warning("Please enter a topic.")

# # # אם יש שאלות – מציגים אותן בשורה אחת
# # else:
# #     q = st.session_state.questions

# #     col1, col2, col3 = st.columns(3)

# #     with col1:
# #         st.subheader("Easy")
# #         st.info(q["easy"])
# #         st.text_area("Your answer:", key="easy_answer")

# #     with col2:
# #         st.subheader("Medium")
# #         st.info(q["medium"])
# #         st.text_area("Your answer:", key="medium_answer")

# #     with col3:
# #         st.subheader("Hard")
# #         st.info(q["hard"])
# #         st.text_area("Your answer:", key="hard_answer")

# #     st.markdown("---")

# #     # כפתור סיום
# #     if st.button("Finish"):
# #         st.success("Thank you! Your answers were submitted.")
# #         st.session_state.questions = None
# #         st.rerun()


import streamlit as st
import requests

st.set_page_config(layout="wide")
st.title("🤖 Python Gemini Chatbot")

API_TOPIC = "http://127.0.0.1:8000/chat_topic"
API_ANSWER = "http://127.0.0.1:8000/chat_answers"

# שמירה של השאלות ב-session_state
if "questions" not in st.session_state:
    st.session_state.questions = None

# פונקציה ששולחת תשובה ל-backend
def send_answer(question, answer):
    payload = {
        "question": {
            "question": question,
            "answer": answer
        }
    }
    response = requests.post(API_ANSWER, json=payload)
    if response.status_code == 200:
        return response.json()
    return None


# אם אין שאלות – מציגים את שדה ה-topic
if st.session_state.questions is None:
    topic = st.text_input("Insert your topic:")

    if st.button("Send"):
        if topic:
            with st.spinner("Thinking..."):
                response = requests.post(API_TOPIC, json={"topic": topic})
                if response.status_code == 200:
                    st.session_state.questions = response.json()
                    st.rerun()
                else:
                    st.error("Error fetching questions.")
        else:
            st.warning("Please enter a topic.")

# אם יש שאלות – מציגים אותן
else:
    q = st.session_state.questions

    col1, col2, col3 = st.columns(3)

    # ---------------- EASY ----------------
    with col1:
        st.subheader("Easy")
        st.info(q["easy"])
        easy_answer = st.text_area("Your answer:", key="easy_ans")

        if st.button("Submit Easy"):
            with st.spinner("Thinking..."):
                result = send_answer(q["easy"], easy_answer)
                if result:
                    score = result["score"]
                    feedback = result["feedback"]

                    bg = "#d4edda" if score >= 7 else "#fff3cd" if score >= 4 else "#f8d7da"

                    st.markdown(
                        f"""
                        <div style="padding:10px; border-radius:8px; background:{bg}">
                            <b>Score:</b> {score}<br>
                            <b>Feedback:</b> {feedback}
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

    # ---------------- MEDIUM ----------------
    with col2:
        st.subheader("Medium")
        st.info(q["medium"])
        medium_answer = st.text_area("Your answer:", key="medium_ans")

        if st.button("Submit Medium"):
            with st.spinner("Thinking..."):
                result = send_answer(q["medium"], medium_answer)
                if result:
                    score = result["score"]
                    feedback = result["feedback"]

                    bg = "#d4edda" if score >= 7 else "#fff3cd" if score >= 4 else "#f8d7da"

                    st.markdown(
                        f"""
                        <div style="padding:10px; border-radius:8px; background:{bg}">
                            <b>Score:</b> {score}<br>
                            <b>Feedback:</b> {feedback}
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

    # ---------------- HARD ----------------
    with col3:
        st.subheader("Hard")
        st.info(q["hard"])
        hard_answer = st.text_area("Your answer:", key="hard_ans")

        if st.button("Submit Hard"):
            with st.spinner("Thinking..."):
                result = send_answer(q["hard"], hard_answer)
                if result:
                    score = result["score"]
                    feedback = result["feedback"]

                    bg = "#d4edda" if score >= 7 else "#fff3cd" if score >= 4 else "#f8d7da"

                    st.markdown(
                        f"""
                        <div style="padding:10px; border-radius:8px; background:{bg}">
                            <b>Score:</b> {score}<br>
                            <b>Feedback:</b> {feedback}
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

    st.markdown("---")

    # כפתור סיום
    if st.button("Finish"):
        st.session_state.questions = None
        st.rerun()

# import streamlit as st
# import requests

# # הגדרות עמוד
# st.set_page_config(layout="wide")

# # כותרת ממורכזת באמת
# st.markdown(
#     "<h1 style='text-align:center; direction:rtl;'>🤖 Python Gemini Chatbot</h1>",
#     unsafe_allow_html=True
# )

# API_TOPIC = "http://127.0.0.1:8000/chat_topic"
# API_ANSWER = "http://127.0.0.1:8000/chat_answers"

# # --- עיצוב RTL + כפתור קטן + input קטן ---
# st.markdown("""
# <style>

# /* יישור כללי */
# .block-container {
#     text-align: center !important;
# }

# /* RTL */
# html, body, [class*="css"] {
#     direction: rtl;
# }

# /* תיבות טקסט RTL */
# textarea, input {
#     direction: rtl !important;
#     text-align: right !important;
# }

# /* כפתור קטן */
# div.stButton > button {
#     width: 120px !important;
#     height: 35px !important;
#     font-size: 14px !important;
#     padding: 3px 8px !important;
#     margin: auto !important;
#     display: block !important;
# }

# /* שדה topic קטן */
# input[type="text"] {
#     width: 60% !important;
#     margin: auto !important;
# }

# </style>
# """, unsafe_allow_html=True)

# # עטיפת טקסט RTL
# def rtl(text):
#     return f"<div style='direction: rtl; text-align: right;'>{text}</div>"

# # שמירת שאלות
# if "questions" not in st.session_state:
#     st.session_state.questions = None


# # פונקציה לשליחת תשובה ל-backend
# def send_answer(question, answer):
#     payload = {
#         "question": {
#             "question": question,
#             "answer": answer
#         }
#     }
#     response = requests.post(API_ANSWER, json=payload)
#     if response.status_code == 200:
#         return response.json()
#     return None


# # --- מסך הכנסת נושא ---
# if st.session_state.questions is None:

#     # עוטפים את ה-input והכפתור בעמודה אמצעית
#     colA, colB, colC = st.columns([1,2,1])
#     with colB:

#         topic = st.text_input("הכנס נושא ללמידה:", key="topic_input")

#         # כפתור ממורכז באמת
#         if st.button("שלח"):
#             if topic:
#                 with st.spinner("חושב..."):
#                     response = requests.post(API_TOPIC, json={"topic": topic})
#                     if response.status_code == 200:
#                         st.session_state.questions = response.json()
#                         st.rerun()
#                     else:
#                         st.error("שגיאה בקבלת השאלות מהשרת.")
#             else:
#                 st.warning("אנא הכנס נושא.")

# # --- מסך השאלות ---
# else:
#     q = st.session_state.questions

#     col1, col2, col3 = st.columns(3)

#     # ---------------- EASY ----------------
#     with col1:
#         st.subheader("קל")
#         st.markdown(rtl(q["easy"]), unsafe_allow_html=True)
#         easy_answer = st.text_area("התשובה שלך:", key="easy_ans")

#         if st.button("בדוק שאלה קלה"):
#             with st.spinner("בודק תשובה..."):
#                 result = send_answer(q["easy"], easy_answer)
#                 if result:
#                     score = result["score"]
#                     feedback = result["feedback"]

#                     bg = "#d4edda" if score >= 7 else "#fff3cd" if score >= 4 else "#f8d7da"

#                     st.markdown(
#                         f"""
#                         <div style="padding:10px; border-radius:8px; background:{bg}; direction: rtl; text-align: right;">
#                             <b>ציון:</b> {score}<br>
#                             <b>פידבק:</b> {feedback}
#                         </div>
#                         """,
#                         unsafe_allow_html=True
#                     )

#     # ---------------- MEDIUM ----------------
#     with col2:
#         st.subheader("בינוני")
#         st.markdown(rtl(q["medium"]), unsafe_allow_html=True)
#         medium_answer = st.text_area("התשובה שלך:", key="medium_ans")

#         if st.button("בדוק שאלה בינונית"):
#             with st.spinner("בודק תשובה..."):
#                 result = send_answer(q["medium"], medium_answer)
#                 if result:
#                     score = result["score"]
#                     feedback = result["feedback"]

#                     bg = "#d4edda" if score >= 7 else "#fff3cd" if score >= 4 else "#f8d7da"

#                     st.markdown(
#                         f"""
#                         <div style="padding:10px; border-radius:8px; background:{bg}; direction: rtl; text-align: right;">
#                             <b>ציון:</b> {score}<br>
#                             <b>פידבק:</b> {feedback}
#                         </div>
#                         """,
#                         unsafe_allow_html=True
#                     )

#     # ---------------- HARD ----------------
#     with col3:
#         st.subheader("קשה")
#         st.markdown(rtl(q["hard"]), unsafe_allow_html=True)
#         hard_answer = st.text_area("התשובה שלך:", key="hard_ans")

#         if st.button("בדוק שאלה קשה"):
#             with st.spinner("בודק תשובה..."):
#                 result = send_answer(q["hard"], hard_answer)
#                 if result:
#                     score = result["score"]
#                     feedback = result["feedback"]

#                     bg = "#d4edda" if score >= 7 else "#fff3cd" if score >= 4 else "#f8d7da"

#                     st.markdown(
#                         f"""
#                         <div style="padding:10px; border-radius:8px; background:{bg}; direction: rtl; text-align: right;">
#                             <b>ציון:</b> {score}<br>
#                             <b>פידבק:</b> {feedback}
#                         </div>
#                         """,
#                         unsafe_allow_html=True
#                     )

#     st.markdown("---")

#     # כפתור סיום — ממורכז
#     colX, colY, colZ = st.columns([1,1,1])
#     with colY:
#         if st.button("סיום"):
#             st.session_state.questions = None
#             st.rerun()