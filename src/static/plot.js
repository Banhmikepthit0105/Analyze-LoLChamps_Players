// Thông tin về các bộ dữ liệu
const datasetInfo = {
    champion: {
        name: "Champion Data",
        description: "Dữ liệu về các tướng trong League of Legends, bao gồm thống kê chiến thắng, pickrate, KDA...",
        examples: [
            "Hiển thị top 10 tướng có tỉ lệ thắng cao nhất",
            "So sánh tỉ lệ chọn và tỉ lệ cấm của các tướng",
            "Phân tích KDA theo vị trí tướng"
        ]
    },
    player: {
        name: "Player Data",
        description: "Dữ liệu về các người chơi, bao gồm thống kê KDA, CS/M, tỉ lệ thắng...",
        examples: [
            "So sánh KDA của 10 người chơi hàng đầu",
            "Phân tích tỉ lệ thắng theo vai trò",
            "Hiển thị mối quan hệ giữa CS/M và G/M của các người chơi"
        ]
    }
};

// Hàm khởi tạo khi trang được load
document.addEventListener('DOMContentLoaded', function() {
    updateDatasetInfo();
});

// Hàm cập nhật thông tin dataset khi người dùng chọn
function updateDatasetInfo() {
    const selectedDataset = document.getElementById('dataset').value;
    const infoElement = document.getElementById('datasetInfo');
    
    if (selectedDataset && datasetInfo[selectedDataset]) {
        const dataset = datasetInfo[selectedDataset];
        
        infoElement.innerHTML = `
            <h3>${dataset.name}</h3>
            <p>${dataset.description}</p>
            <p><strong>Ví dụ câu hỏi:</strong></p>
            <ul>
                ${dataset.examples.map(ex => `<li>${ex}</li>`).join('')}
            </ul>
        `;
        infoElement.style.display = 'block';
    } else {
        infoElement.style.display = 'none';
    }
}

async function generatePlot() {
    const userInput = document.getElementById('userInput').value;
    const dataset = document.getElementById('dataset').value;
    
    if (!userInput) {
        alert('Vui lòng nhập yêu cầu trực quan hóa!');
        return;
    }
    
    try {
        // Hiển thị thông báo đang xử lý
        const plotDiv = document.getElementById('plot');
        plotDiv.innerHTML = '<div style="text-align: center; padding: 20px;"><h3>Đang xử lý yêu cầu...</h3></div>';
        
        const response = await fetch('/api/plot', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                user_input: userInput,
                dataset: dataset
            })
        });
        
        const data = await response.json();
        if (data.error) {
            plotDiv.innerHTML = `<div style="color: red; padding: 20px;"><h3>Lỗi:</h3><p>${data.error}</p></div>`;
            return;
        }

        // Debug để kiểm tra dữ liệu JSON
        console.log("Received plot data:", data.plot);
        
        try {
            // Parse JSON nếu server trả về string
            const plotData = typeof data.plot === 'string' ? JSON.parse(data.plot) : data.plot;
            
            // Kiểm tra dữ liệu plotly
            if (!plotData || !plotData.data || !Array.isArray(plotData.data)) {
                throw new Error('Dữ liệu biểu đồ không hợp lệ');
            }
            
            // Render biểu đồ
            Plotly.newPlot(plotDiv, plotData.data, plotData.layout);
        } catch (parseError) {
            console.error('Error parsing plot data:', parseError);
            plotDiv.innerHTML = `
                <div style="color: red; padding: 20px;">
                    <h3>Lỗi khi xử lý dữ liệu biểu đồ:</h3>
                    <p>${parseError.message}</p>
                </div>
            `;
        }
    } catch (error) {
        console.error('Error:', error);
        document.getElementById('plot').innerHTML = `
            <div style="color: red; padding: 20px;">
                <h3>Đã xảy ra lỗi:</h3>
                <p>${error.message || 'Không thể kết nối với máy chủ'}</p>
            </div>
        `;
    }
}