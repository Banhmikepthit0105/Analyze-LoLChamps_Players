# import os
# import google.generativeai as genai
# from utils import clean_the_response
# from dotenv import load_dotenv

# # Khởi tạo ngay khi ứng dụng chạy
# load_dotenv()  # Load biến môi trường từ file .env
# api_key = os.environ.get('GEMINI_API_KEY')
# if not api_key:
#     raise ValueError("Biến môi trường GEMINI_API_KEY chưa được thiết lập")

# # Cấu hình Gemini API và khởi tạo model ngay từ đầu
# genai.configure(api_key=api_key)
# gemini_model = genai.GenerativeModel('gemini-2.0-flash-thinking-exp-01-21')


# def create_plot(user_input, df):
#     """
#     Tạo biểu đồ dựa trên yêu cầu của người dùng với DataFrame đã được load từ file.
#     Hàm này sẽ gọi Gemini API và nhận về mã code tạo Plotly Figure, 
#     mã code phải gán đối tượng Plotly Figure vào biến 'fig' mà không thực hiện lệnh hiển thị biểu đồ.
#     """
#     # Định nghĩa mô tả các cột
#     column_descriptions = {
#         'Year': 'Năm của giải đấu (INT, ví dụ: 2018)',
#         'Date': 'Ngày trong khoảng thời gian của mùa giải (DATETIME, ví dụ: 2018-03-19)',
#         'Tournamment': 'Tên giải đấu (VARCHAR, ví dụ: Spring_Season)',
#         'Champion': 'Tên của tướng (VARCHAR, ví dụ: Ryze, Camille)',
#         'G': 'Tổng số trận mà tướng tham gia (được chơi hoặc bị cấm) (INT)',
#         'PB': 'Tỉ lệ chọn hoặc cấm (FLOAT, G / tổng số trận trong mùa giải)',
#         'B': 'Số trận mà tướng bị cấm (INT)',
#         'GP': 'Số trận mà tướng được chơi (INT)',
#         'By': 'Số người chơi duy nhất đã chọn tướng (INT)',
#         'W': 'Số trận thắng khi tướng được chơi (INT)',
#         'L': 'Số trận thua khi tướng được chơi (INT)',
#         'WR': 'Tỉ lệ thắng khi được chơi (FLOAT, W / GP dưới dạng phần trăm)',
#         'K': 'Số lần hạ gục trung bình mỗi trận (FLOAT)',
#         'D': 'Số lần bị hạ gục trung bình mỗi trận (FLOAT)',
#         'A': 'Số lần hỗ trợ trung bình mỗi trận (FLOAT)',
#         'KDA': 'Chỉ số hiệu suất (FLOAT, tính theo (K + A) / D)',
#         'CS': 'Số lính trung bình bị hạ mỗi trận (FLOAT)',
#         'CS/M': 'Số lính trung bình bị hạ mỗi phút (FLOAT)',
#         'G.1': 'Số vàng trung bình kiếm được mỗi trận (FLOAT)',
#         'G/M': 'Số vàng kiếm được mỗi phút (FLOAT)',
#         'KPAR': 'Tham gia hạ gục (FLOAT, tính theo (K + A) / tổng số hạ gục của đội dưới dạng phần trăm)',
#         'KS': 'Tỉ lệ hạ gục trong đội (FLOAT, phần trăm)',
#         'GS': 'Tỉ lệ vàng trong đội (FLOAT, phần trăm)',
#         'As': 'Vị trí của tướng (LIST[VARCHAR], chứa danh sách các vị trí, ví dụ: ["Mid Laner", "Top Laner", "Jungler", "Bot", "Support"])',
#         'total_games': 'Tổng số trận trong mùa giải (INT)',
#         '%B': 'Tỉ lệ bị cấm (FLOAT, phần trăm)',
#         '%P': 'Tỉ lệ được chọn (FLOAT, phần trăm)'
#     }

#     # Kiểm tra các cột cần có trong DataFrame
#     missing_cols = [col for col in column_descriptions.keys() if col not in df.columns]
#     if missing_cols:
#         raise ValueError(f"Các cột sau không có trong DataFrame: {missing_cols}")

#     # Tạo chuỗi mô tả các cột
#     col_desc_str = '\n'.join([f"{col}: {desc}" for col, desc in column_descriptions.items()])

#     # Tạo prompt cho Gemini API với yêu cầu chỉ trả về biến 'fig' mà không gọi hiển thị biểu đồ
#     prompt = (
#         "Viết mã Python sử dụng Plotly để tạo trực quan hóa dựa trên yêu cầu của người dùng: \"{}\"\n"
#         "Sử dụng DataFrame có tên `df` với các cột và mô tả sau:\n"
#         "{}\n"
#         "Đảm bảo trực quan hóa tuân theo các yêu cầu sau:\n"
#         "- Tiêu đề của biểu đồ phải khớp chính xác với yêu cầu của người dùng: \"{}\"\n"
#         "- Bao gồm nhãn trục x và trục y rõ ràng, phù hợp với dữ liệu được vẽ\n"
#         "- Nếu biểu đồ cần sử dụng yếu tố liên quan đến thời gian, cần sử dụng cột Date hoặc cột Year, ưu tiên sử dụng cột Date\n"
#         "- Làm tròn tất cả các giá trị số (ví dụ: nhãn, thông tin khi rê chuột) đến 2 chữ số thập phân\n"
#         "- Sử dụng giao diện màu sắc chuyên nghiệp và bố cục sạch sẽ, thẩm mỹ\n"
#         "- Không sử dụng đối số `animation_group` trong các hàm của Plotly\n\n"
#         "Dưới đây là ví dụ ngắn sử dụng Few-shot prompting và Chain-of-Thought:\n\n"
#         "Ví dụ:\n"
#         "Problem: 'Phân tích xu hướng tỉ lệ chiến thắng (WR) của các champion qua các năm.'\n"
#         "Chain-of-Thought:\n"
#         "- Xác định rằng dữ liệu có yếu tố thời gian (cột 'Year') và chỉ số hiệu suất (cột 'WR').\n"
#         "- Biểu đồ đường (line chart) là lựa chọn phù hợp để thể hiện xu hướng theo thời gian.\n"
#         "Kết luận: Sử dụng **line chart**.\n\n"
#         "Bây giờ, dựa trên yêu cầu và mô tả dữ liệu dưới đây, hãy xác định loại biểu đồ phù hợp.\n\n"
#         "Yêu cầu của người dùng: \"{}\"\n\n"
#         "Mô tả các cột của DataFrame:\n"
#         "{}\n\n"
#         "Yêu cầu thêm:\n"
#         "- Tiêu đề của biểu đồ phải khớp chính xác với yêu cầu của người dùng\n"
#         "- Bao gồm nhãn trục rõ ràng\n"
#         "- Làm tròn các giá trị số đến 2 chữ số thập phân\n"
#         "- Sử dụng giao diện chuyên nghiệp\n"
#         "- Tránh hiển thị các giá trị Null trên biểu đồ\n"
#         "QUAN TRỌNG NHẤT: Nếu số lượng đối tượng vượt quá 20, chỉ chọn ra top 20 đối tượng có giá trị cao nhất hoặc thấp nhất dựa trên tiêu chí liên quan đến câu hỏi của người dùng (không được chọn ngẫu nhiên)\n\n"
#         "Giả sử dữ liệu đã được tải vào biến `df`. "
#         "Trả về chỉ mã Plotly cần thiết để tạo trực quan hóa, phải gán vào biến 'fig', không kèm theo lời giải thích, không có các dòng import và không gọi hàm hiển thị (không gọi fig.show())."
#     ).format(user_input, col_desc_str, user_input, user_input, col_desc_str)

#     print("Prompt for Gemini API:\n", prompt)

#     # Sử dụng mô hình đã được khởi tạo từ ban đầu (gemini_model)
#     try:
#         response = gemini_model.generate_content(prompt)
#     except Exception as e:
#         raise Exception(f"Yêu cầu đến Gemini API thất bại: {e}")

#     generated_code = response.text
#     extracted_code = clean_the_response(generated_code)
#     print("Generated Code:\n", extracted_code)

#     # Thực thi mã code được tạo ra, truyền DataFrame vào context của exec
#     local_vars = {}
#     exec(extracted_code, {'df': df}, local_vars)
#     fig = local_vars.get("fig")
#     if fig is None:
#         raise Exception("Không tìm thấy biến 'fig' sau khi thực thi code.")
#     return fig






import os
import requests
import google.generativeai as genai
from utils import clean_the_response
from dotenv import load_dotenv
import datetime
import pandas as pd
import plotly.express as px


def call_deepseek_api(prompt, api_key, model="deepseek-chat", temperature=0.1):
    """Gọi DeepSeek API với xử lý lỗi phù hợp và trả về nội dung kết quả."""
    url = "https://api.deepseek.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": "You are an expert data visualization assistant that generates precise Visualization Query Language (VQL) and Plotly code."},
            {"role": "user", "content": prompt}
        ],
        "temperature": temperature,
        "max_tokens": 2000
    }
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code != 200:
        raise Exception(f"DeepSeek API error: {response.status_code} - {response.text}")
    result = response.json()
    # Giả sử DeepSeek trả về nội dung trong trường ["choices"][0]["message"]["content"]
    return result["choices"][0]["message"]["content"]

def init_gemini_model(model_name="gemini-2.0-flash-thinking-exp-01-21"):
    """
    Khởi tạo và trả về instance của Gemini Model dựa trên model_name đã cho.
    Load biến môi trường và cấu hình API.
    """
    load_dotenv()  # Load biến môi trường từ file .env
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("Biến môi trường GEMINI_API_KEY chưa được thiết lập")
    genai.configure(api_key=api_key)
    return genai.GenerativeModel(model_name)

# Khởi tạo model Gemini mặc định ngay khi ứng dụng chạy.
gemini_model = init_gemini_model()

def create_plot(user_input, df, provider="gemini", deepseek_api_key=None):
    """
    Tạo biểu đồ dựa trên yêu cầu của người dùng với DataFrame đã được load.
    Hàm này sẽ gọi API (Gemini hoặc DeepSeek) để nhận về mã code Plotly,
    mã code trả về phải tạo đối tượng Plotly Figure được gán vào biến 'fig' mà không thực hiện lệnh hiển thị.
    
    Parameters:
      - user_input: Yêu cầu trực quan hóa của người dùng (string)
      - df: DataFrame chứa dữ liệu (pandas.DataFrame)
      - provider: Chuỗi chỉ định lựa chọn API ("gemini" hay "deepseek")
      - deepseek_api_key: (tuỳ chọn) API key của DeepSeek, nếu không, sẽ lấy từ biến môi trường DEEPSEEK_API_KEY.
    Returns:
      - fig: Đối tượng Plotly Figure được tạo ra từ mã code trả về.
    """
    # Định nghĩa mô tả các cột
    column_descriptions = {
        'Date': 'Ngày trong khoảng thời gian của mùa giải (DATETIME, ví dụ: 2018-03-19)',
        'Champion': 'Tên của tướng (VARCHAR, ví dụ: Ryze, Camille)',
        'G': 'Tổng số trận mà tướng tham gia (được chơi hoặc bị cấm) (INT)',
        'PB': 'Tỉ lệ chọn hoặc cấm (FLOAT, G / tổng số trận trong mùa giải)',
        'B': 'Số trận mà tướng bị cấm (INT)',
        'GP': 'Số trận mà tướng được chơi (INT)',
        'By': 'Số người chơi duy nhất đã chọn tướng (INT)',
        'W': 'Số trận thắng khi tướng được chơi (INT)',
        'L': 'Số trận thua khi tướng được chơi (INT)',
        'WR': 'Tỉ lệ thắng khi được chơi (FLOAT, W / GP dưới dạng phần trăm)',
        'K': 'Số lần hạ gục trung bình mỗi trận (FLOAT)',
        'D': 'Số lần bị hạ gục trung bình mỗi trận (FLOAT)',
        'A': 'Số lần hỗ trợ trung bình mỗi trận (FLOAT)',
        'KDA': 'Chỉ số hiệu suất (FLOAT, tính theo (K + A) / D)',
        'CS': 'Số lính trung bình bị hạ mỗi trận (FLOAT)',
        'CS/M': 'Số lính trung bình bị hạ mỗi phút (FLOAT)',
        'G.1': 'Số vàng trung bình kiếm được mỗi trận (FLOAT)',
        'G/M': 'Số vàng kiếm được mỗi phút (FLOAT)',
        'KPAR': 'Tham gia hạ gục (FLOAT, tính theo (K + A) / tổng số hạ gục của đội dưới dạng phần trăm)',
        'KS': 'Tỉ lệ hạ gục trong đội (FLOAT, phần trăm)',
        'GS': 'Tỉ lệ vàng trong đội (FLOAT, phần trăm)',
        'As': 'Vị trí của tướng (LIST[VARCHAR], chứa danh sách các vị trí, ví dụ: ["Mid Laner", "Top Laner", "Jungler", "Bot", "Support"])',
        'total_games': 'Tổng số trận trong mùa giải (INT)',
        '%B': 'Tỉ lệ bị cấm (FLOAT, phần trăm)',
        '%P': 'Tỉ lệ được chọn (FLOAT, phần trăm)'
    }

    # Kiểm tra các cột cần có trong DataFrame
    missing_cols = [col for col in column_descriptions.keys() if col not in df.columns]
    if missing_cols:
        raise ValueError(f"Các cột sau không có trong DataFrame: {missing_cols}")

    # Tạo chuỗi mô tả các cột
    col_desc_str = "\n".join([f"{col}: {desc}" for col, desc in column_descriptions.items()])

    # Tạo prompt cho API với yêu cầu chỉ trả về mã code tạo biểu đồ (gán vào biến 'fig')
    prompt = (
        "Viết mã Python sử dụng Plotly để tạo trực quan hóa dựa trên yêu cầu của người dùng: \"{}\"\n"
        "Sử dụng DataFrame có tên `df` với các cột và mô tả sau:\n"
        "{}\n"
        "Đảm bảo trực quan hóa tuân theo các yêu cầu sau:\n"
        "- Tiêu đề của biểu đồ phải khớp chính xác với yêu cầu của người dùng: \"{}\"\n"
        "- Bao gồm nhãn trục x và trục y rõ ràng, phù hợp với dữ liệu được vẽ\n"
        "- Nếu biểu đồ cần sử dụng yếu tố liên quan đến thời gian, cần sắp xếp thứ tự hiển thị theo thứ tự thời gian\n"
        "- Làm tròn tất cả các giá trị số (ví dụ: nhãn, thông tin khi rê chuột) đến 2 chữ số thập phân\n"
        "- Sử dụng giao diện màu sắc chuyên nghiệp và bố cục sạch sẽ, thẩm mỹ\n"
        "- Không sử dụng đối số `animation_group` trong các hàm của Plotly\n\n"
        "Dưới đây là ví dụ ngắn sử dụng Few-shot prompting và Chain-of-Thought:\n\n"
        "Ví dụ:\n"
        "Problem: 'Phân tích xu hướng tỉ lệ chiến thắng (WR) của các champion qua các năm.'\n"
        "Chain-of-Thought:\n"
        "- Xác định rằng dữ liệu có yếu tố thời gian (cột 'Year') và chỉ số hiệu suất (cột 'WR').\n"
        "- Biểu đồ đường (line chart) là lựa chọn phù hợp để thể hiện xu hướng theo thời gian.\n"
        "Kết luận: Sử dụng **line chart**.\n\n"
        "Bây giờ, dựa trên yêu cầu và mô tả dữ liệu dưới đây, hãy xác định loại biểu đồ phù hợp.\n\n"
        "Yêu cầu của người dùng: \"{}\"\n\n"
        "Mô tả các cột của DataFrame:\n"
        "{}\n\n"
        "Yêu cầu thêm:\n"
        "- Tiêu đề của biểu đồ phải khớp chính xác với yêu cầu của người dùng\n"
        "- Bao gồm nhãn trục rõ ràng\n"
        "- Làm tròn các giá trị số đến 2 chữ số thập phân\n"
        "- Sử dụng giao diện màu sắc chuyên nghiệp\n"
        "- Tránh hiển thị các giá trị Null trên biểu đồ\n"
        "QUAN TRỌNG NHẤT: Nếu số lượng đối tượng vượt quá 20, chỉ chọn ra top 20 đối tượng có giá trị cao nhất hoặc thấp nhất "
        "dựa trên tiêu chí liên quan đến câu hỏi của người dùng (không được chọn ngẫu nhiên)\n\n"
        "Giả sử dữ liệu đã được tải vào biến `df`. "
        "Trả về chỉ mã Plotly cần thiết để tạo trực quan hóa, phải gán vào biến 'fig', không kèm theo lời giải thích, "
        "Phải có các dòng import thư viện và không gọi hàm hiển thị (không gọi fig.show())."
    ).format(user_input, col_desc_str, user_input, user_input, col_desc_str)
    
    print("Prompt for API:\n", prompt)
    
    # Gọi API dựa trên provider được chọn
    if provider.lower() == "deepseek":
        if not deepseek_api_key:
            deepseek_api_key = os.environ.get("DEEPSEEK_API_KEY")
        if not deepseek_api_key:
            raise ValueError("Biến môi trường DEEPSEEK_API_KEY chưa được thiết lập")
        generated_response = call_deepseek_api(prompt, deepseek_api_key)
    else:
        try:
            response = gemini_model.generate_content(prompt)
            generated_response = response.text
        except Exception as e:
            raise Exception(f"Yêu cầu đến Gemini API thất bại: {e}")
    
    extracted_code = clean_the_response(generated_response)
    print("Generated Code:\n", extracted_code)
    
    # Thực thi mã code được tạo ra, truyền DataFrame vào context của exec
    local_vars = {}
    exec(extracted_code, {'px': px, 'pd': pd, 'df': df}, local_vars)
    fig = local_vars.get("fig")
    if fig is None:
        raise Exception("Không tìm thấy biến 'fig' sau khi thực thi code.")
    return fig
