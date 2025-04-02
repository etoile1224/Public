import streamlit as st
import pandas as pd
import os
from fpdf import FPDF

DATA_FILE = "reading_bingo_data.csv"

# 초기화 함수
@st.cache_data
def load_data():
    if os.path.exists(DATA_FILE):
        return pd.read_csv(DATA_FILE)
    else:
        return pd.DataFrame(columns=["row", "col", "reading_goal", "book_title", "author", "review", "read"])

# 저장 함수
def save_data(data):
    data.to_csv(DATA_FILE, index=False)

# PDF 출력 함수
def export_to_pdf(data):
    pdf = FPDF()
    pdf.add_page()
    pdf.add_font("ArialUnicode", '', fname="./NanumGothic.ttf", uni=True)
    pdf.set_font("ArialUnicode", size=12)

    for index, row in data.iterrows():
        pdf.cell(0, 10, txt=f"\ud83d\udcda 독서 목표: {row['reading_goal']}", ln=True)
        pdf.cell(0, 10, txt=f"제목: {row['book_title']}", ln=True)
        pdf.cell(0, 10, txt=f"저자: {row['author']}", ln=True)
        pdf.cell(0, 10, txt=f"리뷰: {row['review']}", ln=True)
        pdf.cell(0, 10, txt=f"읽음 여부: {'예' if row['read'] else '아니오'}", ln=True)
        pdf.cell(0, 10, txt="", ln=True)

    pdf.output("bingo.pdf")
    return "bingo.pdf"

st.set_page_config(page_title="2025 Reading Bingo", layout="wide")
st.title("2025 Reading Bingo")

st.markdown(":books: 5x5 독서 빙고를 작성하고, 저장하거나 PDF로 출력하세요!")

data = load_data()

cols = st.columns(5)
updated_rows = []

for i in range(5):
    for j in range(5):
        cell_key = f"cell_{i}_{j}"
        with cols[j]:
            st.markdown(f"**({i+1}, {j+1})**")
            goal = st.text_input("독서 목표", value=data.query("row==@i & col==@j").reading_goal.values[0] if not data.query("row==@i & col==@j").empty else "", key=cell_key+"_goal")
            title = st.text_input("제목", value=data.query("row==@i & col==@j").book_title.values[0] if not data.query("row==@i & col==@j").empty else "", key=cell_key+"_title")
            author = st.text_input("저자", value=data.query("row==@i & col==@j").author.values[0] if not data.query("row==@i & col==@j").empty else "", key=cell_key+"_author")
            review = st.text_area("리뷰", value=data.query("row==@i & col==@j").review.values[0] if not data.query("row==@i & col==@j").empty else "", key=cell_key+"_review")
            read = st.checkbox("읽었어요", value=bool(data.query("row==@i & col==@j").read.values[0]) if not data.query("row==@i & col==@j").empty else False, key=cell_key+"_read")

            updated_rows.append({"row": i, "col": j, "reading_goal": goal, "book_title": title, "author": author, "review": review, "read": read})

# 저장 버튼
if st.button("💾 저장하기"):
    df = pd.DataFrame(updated_rows)
    save_data(df)
    st.success("저장 완료!")

# PDF 출력 버튼
if st.button("📄 PDF로 내보내기"):
    df = pd.DataFrame(updated_rows)
    path = export_to_pdf(df)
    with open(path, "rb") as f:
        st.download_button(label="PDF 다운로드", data=f, file_name="bingo.pdf")