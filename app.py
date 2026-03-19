# -*- coding: utf-8 -*-
"""
Created on Thu Feb 19 09:21:05 2026

@author: LENOVO
"""
import os
import uuid
import time
from datetime import datetime

import pandas as pd
import streamlit as st
APP_TITLE = "AI Chatbot Shopping Study (Demo)"
DATA_DIR = "Data"
OUTFILE = os.path.join(DATA_DIR, "responses.csv")
SCRIPTS = {
    "LOW": [
        "Mình có thể giúp bạn. Bạn đang quan tâm tiêu chí nào (giá, chứng nhận, thành phần, nguồn gốc)?",
        "OK. Bạn có thể cho mình biết sản phẩm bạn đang cân nhắc và ngân sách khoảng bao nhiêu?",
        "Dựa trên thông tin bạn đưa, mình gợi ý ưu tiên: (1) kiểm tra chứng nhận; (2) xem thành phần; (3) so sánh giá/khối lượng.",
        "Bạn muốn mình tóm tắt 2–3 lựa chọn theo bảng so sánh không?",
    ],
    "HIGH": [
        "Mình đã hiểu mục tiêu của bạn. Mình sẽ chủ động hỏi 2 câu để tối ưu lựa chọn: bạn ưu tiên (A) giảm nhựa, (B) giảm carbon, hay (C) an toàn thành phần?",
        "Cảm ơn! Mình sẽ đề xuất 3 lựa chọn phù hợp và giải thích nhanh ‘vì sao’ cho từng lựa chọn. Bạn cho mình biết bạn mua cho cá nhân hay gia đình?",
        "Mình tóm tắt phương án tối ưu: chọn sản phẩm có chứng nhận rõ + bao bì ít nhựa + giá/khối lượng tốt. Nếu bạn muốn, mình có thể giúp bạn kiểm tra claim/nhãn hiệu theo checklist 5 điểm.",
        "Mình đề xuất bạn chốt theo ‘đủ tốt’ thay vì ‘hoàn hảo’: chọn phương án có tác động lớn nhất theo ưu tiên bạn đã chọn. Bạn muốn mình đưa ra quyết định cuối cùng theo ưu tiên A/B/C không?",
    ],
}
ITEMS = {
    "Digital agenticity (perceived)": [
        "Chatbot phản hồi đúng trọng tâm và liên quan đến nhu cầu của tôi.",
        "Chatbot chủ động gợi ý bước tiếp theo thay vì chỉ trả lời bị động.",
        "Chatbot thích nghi với thông tin tôi cung cấp trong cuộc trò chuyện.",
    ],
    "Perceived efficiency": [
        "Chatbot giúp tôi tiết kiệm thời gian tìm kiếm thông tin.",
        "Chatbot làm quá trình ra quyết định của tôi dễ dàng hơn.",
        "Chatbot giảm nỗ lực (effort) tôi phải bỏ ra khi chọn sản phẩm.",
    ],
    "Trust": [
        "Tôi tin các gợi ý của chatbot là đáng tin cậy.",
        "Tôi tin chatbot không cố tình đánh lừa tôi.",
        "Tôi tin chatbot hiểu đúng nhu cầu của tôi.",
    ],
    "Willingness to pay premium": [
        "Tôi sẵn sàng trả giá cao hơn cho lựa chọn được chatbot gợi ý (nếu phù hợp).",
        "Tôi chấp nhận mức giá cao hơn để đổi lấy lợi ích bền vững được giải thích.",
    ],
}

MC_ITEMS = [
    "Chatbot trong nghiên cứu này thể hiện tính chủ động (proactive) cao.",
    "Chatbot trong nghiên cứu này có khả năng thích nghi theo ngữ cảnh tốt.",
]

def ensure_data_dir():
    os.makedirs(DATA_DIR, exist_ok=True)

def init_state():
    if "pid" not in st.session_state:
        st.session_state.pid = str(uuid.uuid4())[:8]  # short anonymous id
    if "stage" not in st.session_state:
        st.session_state.stage = "consent"
    if "condition" not in st.session_state:
        st.session_state.condition = None
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "script_idx" not in st.session_state:
        st.session_state.script_idx = 0
    if "start_ts" not in st.session_state:
        st.session_state.start_ts = time.time()

def random_assign():
    # 50/50 assignment
    return "HIGH" if (uuid.uuid4().int % 2 == 0) else "LOW"

def likert(label, key):
    return st.radio(
        label,
        options=[1,2,3,4,5,6,7],
        index=3,
        horizontal=True,
        key=key,
        help="1 = Rất không đồng ý … 7 = Rất đồng ý"
    )

def save_row(row: dict):
    ensure_data_dir()
    df_row = pd.DataFrame([row])
    if os.path.exists(OUTFILE):
        df_row.to_csv(OUTFILE, mode="a", header=False, index=False, encoding="utf-8-sig")
    else:
        df_row.to_csv(OUTFILE, mode="w", header=True, index=False, encoding="utf-8-sig")

st.set_page_config(page_title=APP_TITLE, layout="centered")
init_state()

st.title(APP_TITLE)
st.caption("Demo app: consent → random condition → chat → manipulation check → scales → submit (save CSV).")

with st.expander("Researcher notes (demo)", expanded=False):
    st.write(
        "- Đây là demo để bạn thay script, thang đo, và bối cảnh task.\n"
        "- Dữ liệu được lưu local vào `data/responses.csv`.\n"
        "- Có thể nâng cấp thành Wizard-of-Oz thật bằng 'operator panel'."
    )

if st.session_state.stage == "consent":
    st.subheader("Consent")
    st.write(
        "Bạn được mời tham gia một nghiên cứu về trải nghiệm tương tác với chatbot hỗ trợ mua sắm. "
        "Tham gia là tự nguyện và bạn có thể dừng bất cứ lúc nào."
    )
    agree = st.checkbox("Tôi đồng ý tham gia (I agree).")
    age_ok = st.checkbox("Tôi xác nhận tôi đáp ứng điều kiện tham gia theo hướng dẫn của nghiên cứu.")
    if st.button("Start"):
        if not (agree and age_ok):
            st.warning("Vui lòng tick đủ các ô xác nhận để bắt đầu.")
        else:
            st.session_state.condition = random_assign()
            st.session_state.stage = "task"
            st.rerun()

elif st.session_state.stage == "task":
    st.subheader("Scenario / Task")
    st.write(
        "Giả sử bạn đang chọn **một sản phẩm tiêu dùng** và muốn cân nhắc các yếu tố bền vững "
        "(ví dụ: bao bì, chứng nhận, thành phần, nguồn gốc). "
        "Hãy trò chuyện với chatbot để nhận gợi ý."
    )

    with st.expander("Debug (researcher)", expanded=False):
        st.write("Assigned condition:", st.session_state.condition)
        st.write("Participant ID:", st.session_state.pid)

    st.markdown("### Chat")

    for m in st.session_state.messages:
        with st.chat_message(m["role"]):
            st.markdown(m["content"])

    if len(st.session_state.messages) == 0:
        first = SCRIPTS[st.session_state.condition][0]
        st.session_state.messages.append({"role": "assistant", "content": first})
        st.session_state.script_idx = 1
        st.rerun()

    user_input = st.chat_input("Nhập tin nhắn của bạn…")
    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})

        idx = st.session_state.script_idx
        script = SCRIPTS[st.session_state.condition]
        if idx < len(script):
            reply = script[idx]
            st.session_state.script_idx += 1
        else:
            reply = "Cảm ơn bạn. Nếu bạn đã đủ thông tin, bạn có thể bấm **Next** để trả lời bảng câu hỏi."
        st.session_state.messages.append({"role": "assistant", "content": reply})
        st.rerun()

    st.divider()
    if st.button("Next → Questionnaire"):
        st.session_state.stage = "survey"
        st.rerun()

elif st.session_state.stage == "survey":
    st.subheader("Questionnaire")

    st.markdown("#### Manipulation check")
    mc1 = likert(MC_ITEMS[0], "mc1")
    mc2 = likert(MC_ITEMS[1], "mc2")

    st.markdown("#### Main scales (1–7)")
    answers = {}
    for scale, items in ITEMS.items():
        st.markdown(f"**{scale}**")
        for i, it in enumerate(items, start=1):
            k = f"{scale}_{i}".replace(" ", "_").replace("(", "").replace(")", "").replace("-", "_")
            answers[k] = likert(it, k)

    st.markdown("#### Optional demographics (demo)")
    gender = st.selectbox("Gender (optional)", ["", "Female", "Male", "Other", "Prefer not to say"])
    age = st.number_input("Age (optional)", min_value=0, max_value=120, value=0, step=1)

    st.divider()

    if st.button("Submit"):
        end_ts = time.time()
        duration_sec = int(end_ts - st.session_state.start_ts)

        row = {
            "timestamp": datetime.utcnow().isoformat(),
            "participant_id": st.session_state.pid,
            "condition": st.session_state.condition,
            "duration_sec": duration_sec,
            "mc1": mc1,
            "mc2": mc2,
            "gender": gender,
            "age": int(age) if age else "",
            "chat_transcript": " | ".join([f'{m["role"]}:{m["content"]}' for m in st.session_state.messages]),
        }
        row.update(answers)

        save_row(row)

        st.success("Đã ghi nhận phản hồi. Cảm ơn bạn!")
        st.session_state.stage = "done"
        st.rerun()

else:
    st.subheader("Done")
    st.write("Bạn có thể đóng trang này.")
    st.caption(f"Participant ID: {st.session_state.pid}")

    if os.path.exists(OUTFILE):
        with st.expander("Preview last rows (researcher)", expanded=False):
            df = pd.read_csv(OUTFILE)
            st.dataframe(df.tail(5))