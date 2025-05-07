from flask import Flask, render_template, request, jsonify
import os
import pandas as pd
import plotly
import json
from dotenv import load_dotenv
from plot_generator import create_plot

app = Flask(__name__)

load_dotenv()

# Đường dẫn đến các file CSV
CHAMPION_DATA_PATH = "../data/preprocessed_data/processed_champion_stats.csv"
PLAYER_DATA_PATH = "../data/preprocessed_data/processed_player_stats.csv"

# Đọc DataFrame
try:
    champion_df = pd.read_csv(CHAMPION_DATA_PATH)
    print(f"Loaded champion data with {len(champion_df)} rows and {len(champion_df.columns)} columns")
except FileNotFoundError:
    champion_df = None
    print(f"Error: File {CHAMPION_DATA_PATH} not found.")
except Exception as e:
    champion_df = None
    print(f"Error loading champion data: {str(e)}")

try:
    player_df = pd.read_csv(PLAYER_DATA_PATH)
    print(f"Loaded player data with {len(player_df)} rows and {len(player_df.columns)} columns")
except FileNotFoundError:
    player_df = None
    print(f"Error: File {PLAYER_DATA_PATH} not found.")
except Exception as e:
    player_df = None
    print(f"Error loading player data: {str(e)}")

# Route để render trang Power BI
@app.route('/')
def powerbi():
    return render_template('dashboard-ai.html')

# Route để render trang Plotly
@app.route('/plot')
def plot():
    return render_template('render-tableau.html')

# Route để tạo biểu đồ từ yêu cầu người dùng
@app.route('/api/plot', methods=['POST'])
def generate_plot():
    # Kiểm tra xem DataFrame có được tải thành công không
    if champion_df is None and player_df is None:
        return jsonify({'error': 'No DataFrames loaded. Please provide valid data files.'}), 500

    try:
        data = request.get_json()
        user_input = data.get('user_input')
        deepseek_api_key = data.get('DEEPSEEK_API_KEY', None)
        dataset = data.get('dataset', 'champion')  

        if not user_input:
            return jsonify({'error': 'Missing user_input parameter'}), 400

        # Chọn DataFrame dựa trên tham số dataset
        if dataset.lower() == 'champion':
            if champion_df is None:
                return jsonify({'error': 'Champion DataFrame not loaded.'}), 500
            df = champion_df
        elif dataset.lower() == 'player':
            if player_df is None:
                return jsonify({'error': 'Player DataFrame not loaded.'}), 500
            df = player_df
        else:
            return jsonify({'error': 'Invalid dataset parameter. Use "champion" or "player".'}), 400

        # Debug: Kiểm tra dataframe
        print(f"Using {dataset} dataframe with shape: {df.shape}")
        
        # Gọi hàm create_plot để tạo biểu đồ, chuyển tham số dataset
        fig = create_plot(user_input, df, dataset, deepseek_api_key)
        
        # Debug: Kiểm tra figure
        print(f"Generated figure type: {type(fig)}")
        
        # Chuyển đổi biểu đồ thành JSON để hiển thị trên frontend
        try:
            fig_json = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
            print(f"JSON conversion successful, length: {len(fig_json)}")
            
            # Kiểm tra định dạng JSON
            parsed = json.loads(fig_json)
            if 'data' not in parsed or 'layout' not in parsed:
                print("WARNING: Missing 'data' or 'layout' in figure JSON")
                
            return jsonify({'plot': parsed})
            
        except Exception as json_error:
            print(f"JSON conversion error: {str(json_error)}")
            return jsonify({'error': f'Failed to convert plot to JSON: {str(json_error)}'}), 500

    except Exception as e:
        import traceback
        traceback_str = traceback.format_exc()
        print(f"Error in generate_plot: {str(e)}\n{traceback_str}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)