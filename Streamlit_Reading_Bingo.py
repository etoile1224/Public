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

# PDF를 빙고판 형태로 출력하는 함수
def export_bingo_pdf_grid(data):
    BASE_DIR = os.path.dirname(__file__)
    FONT_PATH = os.path.join(BASE_DIR, "NanumGothic.ttf")
    pdf = FPDF(orientation='L', unit='mm', format='A4')
    pdf.add_page()

    try:
        pdf.add_font("NanumGothic", "", FONT_PATH, uni=True)
        pdf.set_font("NanumGothic", size=10)
    except Exception as e:
        st.warning(f"폰트 오류로 기본 폰트 사용함: {e}")
        pdf.set_font("Arial", size=10)

    cell_width = 50
    cell_height = 30

    for i in range(5):  # row
        for j in range(5):  # col
            cell_data = data.query("row==@i & col==@j")
            if not cell_data.empty:
                entry = cell_data.iloc[0]
                content = f"{entry['reading_goal']}\n《{entry['book_title']}》\n- {entry['author']}\n{'✅' if entry['read'] else ''}"
            else:
                content = ""

            x = pdf.get_x()
            y = pdf.get_y()
            pdf.multi_cell(cell_width, 6, txt=content, border=1, align='C')
            pdf.set_xy(x + cell_width, y)

        pdf.ln(cell_height)

    output_path = "bingo_grid.pdf"
    pdf.output(output_path)
    return output_path

# Streamlit 앱 UI 시작
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
            cell_data = data.query("row==@i & col==@j")
            goal = st.text_input("독서 목표", value=cell_data.reading_goal.values[0] if not cell_data.empty else "", key=cell_key+"_goal")
            title = st.text_input("제목", value=cell_data.book_title.values[0] if not cell_data.empty else "", key=cell_key+"_title")
            author = st.text_input("저자", value=cell_data.author.values[0] if not cell_data.empty else "", key=cell_key+"_author")
            review = st.text_area("리뷰", value=cell_data.review.values[0] if not cell_data.empty else "", key=cell_key+"_review")
            read = st.checkbox("읽었어요", value=bool(cell_data.read.values[0]) if not cell_data.empty else False, key=cell_key+"_read")

            updated_rows.append({"row": i, "col": j, "reading_goal": goal, "book_title": title, "author": author, "review": review, "read": read})

# 저장 버튼
if st.button("💾 저장하기"):
    df = pd.DataFrame(updated_rows)
    save_data(df)
    st.success("저장 완료!")

# PDF 출력 버튼 (빙고판 스타일)
if st.button("📄 PDF로 내보내기"):
    df = pd.DataFrame(updated_rows)
    path = export_bingo_pdf_grid(df)
    with open(path, "rb") as f:
        st.download_button(label="PDF 다운로드", data=f, file_name="bingo_grid.pdf")
