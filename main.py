<!DOCTYPE html>
<html lang="uk">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Замовлення Таксі - Кобеляки</title>
    <script src="https://telegram.org/js/telegram-web-app.js"></script>
    <style>
        body, html { margin: 0; padding: 0; width: 100%; height: 100%; font-family: Arial, sans-serif; background: #f4f4f4; overflow: hidden; }
        #map { width: 100%; height: 45vh; border: none; }
        .panel { position: absolute; bottom: 0; left: 0; width: 100%; height: 55vh; background: #fff; box-sizing: border-box; padding: 16px; display: flex; flex-direction: column; justify-content: space-between; border-top-left-radius: 20px; border-top-right-radius: 20px; box-shadow: 0 -4px 15px rgba(0,0,0,0.1); }
        .input-group { margin-bottom: 8px; }
        label { font-size: 12px; font-weight: bold; color: #444; display: block; margin-bottom: 4px; }
        input { width: 100%; padding: 12px; border: 2px solid #ddd; border-radius: 10px; box-sizing: border-box; font-size: 15px; outline: none; background: #fff; }
        input.active-field { border-color: #0366d6; background: #f0f7ff; }
        .btn-group { display: flex; gap: 10px; margin-top: 8px; }
        button { border: none; padding: 14px; width: 100%; border-radius: 10px; font-size: 15px; font-weight: bold; cursor: pointer; }
        #submitBtn { background: #2ea44f; color: white; }
        #cancelBtn { background: #d73a49; color: white; }
        .hint { font-size: 13px; color: #0366d6; text-align: center; margin-bottom: 6px; font-weight: bold; }
    </style>
</head>
<body>

    <!-- Відкрита карта Кобеляк (працює завжди і без ключів) -->
    <iframe id="map" src="https://www.openstreetmap.org/export/embed.html?bbox=34.175%2C49.135%2C34.215%2C49.155&layer=mapnik&marker=49.14452%2C34.19065"></iframe>

    <div class="panel">
        <div>
            <div class="hint" id="instruction">👇 Введіть маршрут поїздки</div>
            
            <div class="input-group" onclick="setActiveField('from')">
                <label>📍 Звідки їдемо:</label>
                <input type="text" id="from_address" class="active-field" value="Центр (Кобеляки)" placeholder="Введіть адресу подачі">
            </div>
            
            <div class="input-group" onclick="setActiveField('to')">
                <label>🏁 Куди їдемо:</label>
                <input type="text" id="to_address" placeholder="Введіть пункт призначення">
            </div>
        </div>

        <div class="btn-group">
            <button id="cancelBtn" onclick="cancelOrder()">Скасувати</button>
            <button id="submitBtn">Замовити таксі</button>
        </div>
    </div>

    <script>
        let activeField = 'from';
        const tg = window.Telegram.WebApp;
        tg.expand();

        function setActiveField(field) {
            activeField = field;
            document.getElementById('from_address').classList.remove('active-field');
            document.getElementById('to_address').classList.remove('active-field');
            
            if (field === 'from') {
                document.getElementById('from_address').classList.add('active-field');
            } else {
                document.getElementById('to_address').classList.add('active-field');
            }
        }

        document.getElementById("submitBtn").addEventListener("click", () => {
            const from = document.getElementById("from_address").value.trim() || "Центр (Кобеляки)";
            const to = document.getElementById("to_address").value.trim();

            if (!to) {
                alert("Будь ласка, введіть адресу призначення!");
                return;
            }

            const data = { 
                action: "new_order",
                address_from: from, 
                address_to: to 
            };
            
            tg.sendData(JSON.stringify(data));
            tg.close();
        });

        function cancelOrder() {
            tg.close();
        }
    </script>
</body>
</html>
