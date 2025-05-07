import os
import requests
from utils import clean_the_response
from dotenv import load_dotenv
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
    return result["choices"][0]["message"]["content"]

def create_plot(user_input, df, dataset_type, deepseek_api_key=None):
    """
    Tạo biểu đồ dựa trên yêu cầu của người dùng với DataFrame đã được load.
    Hàm này sẽ gọi DeepSeek API để nhận về mã code Plotly,
    mã code trả về phải tạo đối tượng Plotly Figure được gán vào biến 'fig' mà không thực hiện lệnh hiển thị.
    
    Parameters:
      - user_input: Yêu cầu trực quan hóa của người dùng (string)
      - df: DataFrame chứa dữ liệu (pandas.DataFrame)
      - dataset_type: Loại dữ liệu ("champion" hoặc "player")
      - deepseek_api_key: (tuỳ chọn) API key của DeepSeek, nếu không, sẽ lấy từ biến môi trường DEEPSEEK_API_KEY.
    Returns:
      - fig: Đối tượng Plotly Figure được tạo ra từ mã code trả về.
    """
    # Định nghĩa mô tả các cột cho dataset champion
    champion_column_descriptions = {
        'Champion': 'Tên tướng (VARCHAR, ví dụ: Ryze, Camille)',
        'Date': 'Ngày xảy ra giải đấu (DATETIME, ví dụ: 2018-03-19)',
        'Season': 'Mùa giải (VARCHAR, ví dụ: Spring, Summer)',
        'Event_Type': 'Loại sự kiện (VARCHAR, có thể là Promotion, Season, Playoffs)',
        'G': 'Số trận mà tướng xuất hiện (bao gồm cả khi được chọn hoặc bị cấm) (INT)',
        'PB': 'Tỷ lệ chọn/cấm (%) = (Số trận tướng xuất hiện / Tổng số trận trong mùa) * 100 (FLOAT)',
        'B': 'Số trận tướng bị cấm (Ban) (INT)',
        'GP': 'Số trận tướng được chơi (Games Played) (INT)',
        'By': 'Số người chơi đã sử dụng tướng này (INT)',
        'W': 'Số trận thắng của tướng (INT)',
        'L': 'Số trận thua của tướng (INT)',
        'WR': 'Tỷ lệ thắng (%) = (W / GP) * 100 (FLOAT)',
        'K': 'Số mạng hạ gục trung bình (Kills) (FLOAT)',
        'D': 'Số lần bị hạ gục trung bình (Deaths) (FLOAT)',
        'A': 'Số lần hỗ trợ trung bình (Assists) (FLOAT)',
        'KDA': 'Tỷ lệ KDA = (K + A) / D (FLOAT)',
        'CS': 'Số lính tiêu diệt trung bình (Creep Score) (FLOAT)',
        'CS/M': 'Số lính tiêu diệt mỗi phút (Creep Score per Minute) (FLOAT)',
        'G.1': 'Số vàng kiếm được trung bình (Gold) (FLOAT)',
        'G/M': 'Số vàng kiếm được mỗi phút (Gold per Minute) (FLOAT)',
        'KPAR': 'Tỷ lệ tham gia hạ gục (%) = [(K + A) / Tổng số hạ gục của đội] * 100 (FLOAT)',
        'KS': 'Tỷ lệ đóng góp hạ gục (%) = (K / Tổng số hạ gục của đội) * 100 (FLOAT)',
        'GS': 'Tỷ lệ đóng góp vàng (%) = (G / Tổng số vàng của đội) * 100 (FLOAT)',
        'Mid Laner': 'Tướng được chơi ở vị trí đường giữa (BOOLEAN, 1 = Có, 0 = Không)',
        'Top Laner': 'Tướng được chơi ở vị trí đường trên (BOOLEAN, 1 = Có, 0 = Không)',
        'Bot Laner': 'Tướng được chơi ở vị trí xạ thủ (BOOLEAN, 1 = Có, 0 = Không)',
        'Jungler': 'Tướng được chơi ở vị trí đi rừng (BOOLEAN, 1 = Có, 0 = Không)',
        'Support': 'Tướng được chơi ở vị trí hỗ trợ (BOOLEAN, 1 = Có, 0 = Không)',
        'total_games': 'Tổng số trận trong mùa giải (INT)',
        '%B': 'Tỷ lệ cấm của tướng (%) = (B / total_games) * 100 (FLOAT)',
        '%P': 'Tỷ lệ chọn của tướng (%) = (GP / total_games) * 100 (FLOAT)'
    }
    
    # Định nghĩa mô tả các cột cho dataset player
    player_column_descriptions = {
        'Year': 'Năm diễn ra giải đấu (INT, ví dụ: 2018)',
        'Season': 'Tên mùa giải (VARCHAR, ví dụ: Spring, Season)',
        'Event_Type': 'Tên giai đoạn mùa giải (VARCHAR, ví dụ: Playoffs, Season, Promotion)',
        'Team': 'Tên đội của người chơi (VARCHAR, ví dụ: Cherry Esports)',
        'Player': 'Tên người chơi (VARCHAR)',
        'G': 'Số trận đã chơi (Games) (INT)',
        'W': 'Số trận thắng (Wins) (INT)',
        'L': 'Số trận thua (Losses) (INT)',
        'WR': 'Tỷ lệ thắng (%) = (W / G) * 100 (FLOAT)',
        'K': 'Số mạng hạ gục trung bình mỗi trận (Kills) (FLOAT)',
        'D': 'Số lần bị hạ gục trung bình mỗi trận (Deaths) (FLOAT)',
        'A': 'Số lần hỗ trợ trung bình mỗi trận (Assists) (FLOAT)',
        'KDA': 'Tỷ lệ KDA = (K + A) / D (FLOAT)',
        'CS': 'Số lính tiêu diệt trung bình mỗi trận (Creep Score) (FLOAT)',
        'CS/M': 'Số lính tiêu diệt mỗi phút (Creep Score per Minute) (FLOAT)',
        'G.1': 'Số vàng kiếm được trung bình mỗi trận (Gold) (FLOAT)',
        'G/M': 'Số vàng kiếm được mỗi phút (Gold per Minute) (FLOAT)',
        'KPAR': 'Tỷ lệ tham gia hạ gục (%) = [(K + A) / Tổng số hạ gục của đội] * 100 (FLOAT)',
        'KS': 'Tỷ lệ đóng góp hạ gục (%) = (K / Tổng số hạ gục của đội) * 100 (FLOAT)',
        'GS': 'Tỷ lệ đóng góp vàng (%) = (G.1 / Tổng số vàng của đội) * 100 (FLOAT)',
        'CP': 'Số tướng khác nhau đã chơi (Champions Played) (INT)',
        'Champion_1': 'Tướng được chơi thường xuyên nhiều nhất (VARCHAR)',
        'Champion_2': 'Tướng được chơi thường xuyên nhiều thứ hai (VARCHAR)',
        'Champion_3': 'Tướng được chơi thường xuyên nhiều thứ ba (VARCHAR)',
        'Role': 'Vai trò của người chơi (VARCHAR, ví dụ: Mid Laner, Bot Laner, Support, Jungler)',
        'total_games': 'Tổng số trận trong mùa giải (INT)',
        'max_G/M': 'Số vàng mỗi phút tối đa trong mùa giải (FLOAT)',
        'max_CS/M': 'Số lính tiêu diệt mỗi phút tối đa trong mùa giải (FLOAT)',
        'max_KDA': 'Tỷ lệ KDA tối đa trong mùa giải (FLOAT)',
        'max_KPAR': 'Tỷ lệ tham gia hạ gục tối đa trong mùa giải (FLOAT)'
    }
    
    # Chọn mô tả cột phù hợp dựa trên tham số dataset_type
    dataset_type = dataset_type.lower()
    if dataset_type == "champion":
        column_descriptions = champion_column_descriptions
    elif dataset_type == "player":
        column_descriptions = player_column_descriptions
    else:
        raise ValueError("Loại dữ liệu không hợp lệ. Sử dụng 'champion' hoặc 'player'.")
    
    # Kiểm tra các cột cần có trong DataFrame
    available_cols = [col for col in column_descriptions.keys() if col in df.columns]
    if not available_cols:
        raise ValueError(f"DataFrame không chứa bất kỳ cột nào được mô tả trong {dataset_type}_column_descriptions.")
    
    # Tạo chuỗi mô tả các cột
    col_desc_str = "\n".join([f"{col}: {desc}" for col, desc in column_descriptions.items() if col in df.columns])
    
    # Tạo prompt dựa trên loại dữ liệu
    if dataset_type == "champion":
        prompt = create_champion_prompt(user_input, col_desc_str)
    elif dataset_type == "player":
        prompt = create_player_prompt(user_input, col_desc_str)
    
    print(f"Prompt for API ({dataset_type} data):\n", prompt)
    
    # Gọi DeepSeek API
    if not deepseek_api_key:
        deepseek_api_key = os.environ.get("DEEPSEEK_API_KEY")
    if not deepseek_api_key:
        raise ValueError("Biến môi trường DEEPSEEK_API_KEY chưa được thiết lập")
    
    generated_response = call_deepseek_api(prompt, deepseek_api_key)
    extracted_code = clean_the_response(generated_response)
    print("Generated Code:\n", extracted_code)
    
    # Thực thi mã code được tạo ra, truyền DataFrame vào context của exec
    local_vars = {}
    exec(extracted_code, {'px': px, 'pd': pd, 'df': df}, local_vars)
    fig = local_vars.get("fig")
    if fig is None:
        raise Exception("Không tìm thấy biến 'fig' sau khi thực thi code.")
    return fig

def create_champion_prompt(user_input, col_desc_str):
    """Tạo prompt cho dữ liệu champion"""
    prompt = (
        "Viết mã Python sử dụng Plotly để tạo trực quan hóa dựa trên yêu cầu của người dùng: \"{}\"\n"
        "Sử dụng DataFrame có tên `df` với các cột và mô tả sau:\n"
        "{}\n"
        "Đảm bảo trực quan hóa tuân theo các yêu cầu sau:\n"
        "- Tiêu đề của biểu đồ ngắn gọn: \"{}\"\n"
        "- Bao gồm nhãn trục x và trục y rõ ràng, phù hợp với dữ liệu được vẽ\n"
        "- Ưu tiên sử dụng theo giá trị trung bình của các biến được chọn"
        "- Nếu biểu đồ cần sử dụng yếu tố liên quan đến thời gian, chỉ sử dụng cột Date và sắp xếp theo thứ tự thời gian\n"
        "- Làm tròn tất cả các giá trị số (ví dụ: nhãn, thông tin khi rê chuột) đến 2 chữ số thập phân\n"
        "- Sử dụng tông màu chính là #C89B3C (gold) hoặc các gradient màu sáng như #005A82\n"
        "- Không sử dụng đối số `animation_group` trong các hàm của Plotly\n\n"
        "Dưới đây là ví dụ ngắn sử dụng Few-shot prompting và Chain-of-Thought:\n\n"
        "Ví dụ:\n"
        "Problem: 'Phân tích tỉ lệ chiến thắng (WR) của 10 champion được chơi nhiều nhất.'\n"
        "Chain-of-Thought:\n"
        "- Xác định rằng cần xem xét cột 'Champion', 'GP' (số trận đấu) và 'WR' (tỉ lệ thắng).\n"
        "- Cần sắp xếp theo số trận đấu (GP) để tìm 10 champion được chơi nhiều nhất.\n"
        "- Biểu đồ cột (bar chart) là lựa chọn phù hợp để thể hiện tỉ lệ thắng của các champion.\n"
        "Kết luận: Sử dụng **bar chart** có sắp xếp theo GP.\n\n"
        "Bây giờ, dựa trên yêu cầu và mô tả dữ liệu dưới đây, hãy xác định loại biểu đồ phù hợp.\n\n"
        "Yêu cầu của người dùng: \"{}\"\n\n"
        "Mô tả các cột của DataFrame (Champion dataset):\n"
        "{}\n\n"
        "Yêu cầu thêm:\n"
        "- Tiêu đề của biểu đồ phải khớp chính xác với yêu cầu của người dùng\n"
        "- Bao gồm nhãn trục rõ ràng\n"
        "- Làm tròn các giá trị số đến 2 chữ số thập phân\n"
        "- Sử dụng màu chủ đạo #C89B3C (gold) hoặc các gradient màu sáng như #005A82\n"
        "- Tránh hiển thị các giá trị Null trên biểu đồ\n"
        "QUAN TRỌNG NHẤT: Nếu số lượng đối tượng vượt quá 20, chỉ chọn ra top 20 đối tượng có giá trị cao nhất hoặc thấp nhất "
        "dựa trên tiêu chí liên quan đến câu hỏi của người dùng (không được chọn ngẫu nhiên)\n\n"
        "Giả sử dữ liệu đã được tải vào biến `df`. "
        "Trả về chỉ mã Plotly cần thiết để tạo trực quan hóa, phải gán vào biến 'fig', không kèm theo lời giải thích, "
        "Phải có các dòng import thư viện và KHÔNG ĐƯỢC gọi hàm fig.show() hoặc bất kỳ hàm hiển thị nào khác."
    ).format(user_input, col_desc_str, user_input, user_input, col_desc_str)
    
    return prompt

def create_player_prompt(user_input, col_desc_str):
    """Tạo prompt cho dữ liệu player"""
    prompt = (
        "Viết mã Python sử dụng Plotly để tạo trực quan hóa dựa trên yêu cầu của người dùng: \"{}\"\n"
        "Sử dụng DataFrame có tên `df` với các cột và mô tả sau:\n"
        "{}\n"
        "Đảm bảo trực quan hóa tuân theo các yêu cầu sau:\n"
        "- Tiêu đề của biểu đồ ngắn gọn: \"{}\"\n"
        "- Bao gồm nhãn trục x và trục y rõ ràng, phù hợp với dữ liệu được vẽ\n"
        "- Nếu cần phân tích theo thời gian, sử dụng cột Year và sắp xếp theo thứ tự tăng dần\n"
        "- Làm tròn tất cả các giá trị số (ví dụ: nhãn, thông tin khi rê chuột) đến 2 chữ số thập phân\n"
        "- Sử dụng tông màu chính là #C89B3C (gold) hoặc các gradient màu sáng như #005A82\n"
        "- Không sử dụng đối số `animation_group` trong các hàm của Plotly\n\n"
        "Dưới đây là ví dụ ngắn sử dụng Few-shot prompting và Chain-of-Thought:\n\n"
        "Ví dụ:\n"
        "Problem: 'So sánh KDA của top 10 người chơi có KDA cao nhất.'\n"
        "Chain-of-Thought:\n"
        "- Xác định rằng cần xem xét cột 'Player' và 'KDA'.\n"
        "- Cần sắp xếp theo KDA giảm dần để tìm 10 người chơi có KDA cao nhất.\n"
        "- Biểu đồ cột (bar chart) là lựa chọn phù hợp để so sánh KDA giữa các người chơi.\n"
        "Kết luận: Sử dụng **bar chart** có sắp xếp theo KDA.\n\n"
        "Bây giờ, dựa trên yêu cầu và mô tả dữ liệu dưới đây, hãy xác định loại biểu đồ phù hợp.\n\n"
        "Yêu cầu của người dùng: \"{}\"\n\n"
        "Mô tả các cột của DataFrame (Player dataset):\n"
        "{}\n\n"
        "Yêu cầu thêm:\n"
        "- Tiêu đề của biểu đồ phải khớp chính xác với yêu cầu của người dùng\n"
        "- Bao gồm nhãn trục rõ ràng\n"
        "- Làm tròn các giá trị số đến 2 chữ số thập phân\n"
        "- Sử dụng màu chủ đạo #C89B3C (gold) hoặc các gradient màu sáng như #005A82\n"
        "- Tránh hiển thị các giá trị Null trên biểu đồ\n"
        "QUAN TRỌNG NHẤT: Nếu số lượng đối tượng vượt quá 20, chỉ chọn ra top 20 đối tượng có giá trị cao nhất hoặc thấp nhất "
        "dựa trên tiêu chí liên quan đến câu hỏi của người dùng (không được chọn ngẫu nhiên)\n\n"
        "Giả sử dữ liệu đã được tải vào biến `df`. "
        "Trả về chỉ mã Plotly cần thiết để tạo trực quan hóa, phải gán vào biến 'fig', không kèm theo lời giải thích, "
        "Phải có các dòng import thư viện và KHÔNG ĐƯỢC gọi hàm fig.show() hoặc bất kỳ hàm hiển thị nào khác."
    ).format(user_input, col_desc_str, user_input, user_input, col_desc_str)
    
    return prompt