import streamlit as st
import pandas as pd
from plot_generator import create_plot

# Cấu hình trang và nền trắng cho dashboard
st.set_page_config(page_title="Dashboard League of Legends", layout="wide")
st.markdown(
    """
    <style>
    /* Đặt nền trang chính thành trắng */
    .reportview-container {
        background-color: white;
    }
    /* Đặt nền sidebar thành trắng */
    .sidebar .sidebar-content {
        background-color: white;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.title("Dashboard Trực Quan Hóa Dữ Liệu League of Legends")
st.write("Nhập yêu cầu của bạn để tạo biểu đồ trực quan dựa trên dữ liệu của giải đấu.")

file_path = "../data/preprocessed_data/processed_champion_stats.csv"
try:
    df = pd.read_csv(file_path)
except FileNotFoundError:
    st.error(f"Không tìm thấy file dữ liệu tại {file_path}")
    st.stop()  

user_input = st.text_input("Yêu cầu của người dùng:", value="")

if st.button("Tạo Biểu Đồ"):
    with st.spinner("Đang tạo biểu đồ..."):
        try:
            # Truyền DataFrame cùng yêu cầu vào hàm tạo biểu đồ
            fig = create_plot(user_input, df)
            st.success("Biểu đồ đã được tạo thành công!")
            st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.error(f"Lỗi: {e}")
