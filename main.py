<!DOCTYPE html>
<html lang="uk">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Замовлення Таксі - Кобеляки</title>
    <script src="https://telegram.org/js/telegram-web-app.js"></script>
    <style>
        body, html { margin: 0; padding: 0; width: 100%; height: 100%; font-family: Arial, sans-serif; background: #f4f4f4; display: flex; flex-direction: column; justify-content: space-between; }
        .map-container { flex: 1; width: 100%; position: relative; background: #e5e3df; display: flex; align-items: center; justify-content: center; overflow: hidden; }
        .map-container img { width: 100%; height: 100%; object-fit: cover; }
        .map-overlay-text { position: absolute; top: 15px; background: rgba(0, 0, 0, 0.7); color: #fff; padding: 8px 14px; border-radius: 20px; font-size: 13px; font-weight: bold; text-align: center; pointer-events: none; }
        .panel { background: #fff; padding: 16px; border-top-left-radius: 20px; border-top-right-radius: 20px; box-shadow: 0 -4px 15px rgba(0,0,0,0.1); }
        .input-group { margin-bottom: 10px; }
        label { font-size: 12px; font-weight: bold; color: #555; display: block; margin-bottom: 4px; }
        input { width: 100%; padding: 12px; border: 2px solid #ddd; border-radius: 10px; box-sizing: border-box; font-size: 15px; outline: none; background: #fff; }
        input.active-field { border-color: #0366d6; background: #f0f7ff; }
        .btn-group { display: flex; gap: 10px; margin-top: 12px; }
        button { border: none; padding: 14px; width: 100%; border-radius: 10px; font-size: 16px; font-weight: bold; cursor: pointer; }
        #submitBtn { background: #2ea44f; color: white; }
        #cancelBtn { background: #d73a49; color: white; }
        .hint { font-size: 13px; color: #0366d6; text-align: center; margin-bottom: 8px; font-weight: bold; }
    </style>
</head>
<body>

    <div class="map-container" id="mapBox">
        <div class="map-overlay-text">📍 Натисніть на карту, щоб обрати точку</div>
        <!-- Статична карта Кобеляк з Google Maps -->
        <img id="staticMap" src="https://maps.googleapis.com/maps/api/staticmap?center=49.14452,34.19065&zoom=15&size=600x600&markers=color:green%7C49.14452,34.19065&key=AIzaSyDW4v2j7tbpzvEmnzuEmf9lk-z2Lk1ak7s" alt="Капта Кобеляки">
    </div>

    <div class="panel">
        <div class="hint" id="instruction">👇 Оберіть поле нижче</div>
        
        <div class="input-group" onclick="setActiveField('from')">
            <label>📍 Звідки їдемо:</label>
            <input type="text" id="from_address" class="active-field" readonly value="Центр (Кобеляки)">
        </div>
        
        <div class="input-group" onclick="setActiveField('to')">
            <label>🏁 Куди їдемо:</label>
            <input type="text" id="to_address" readonly placeholder="Натисніть і введіть/оберіть адресу">
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
            
            const hint = document.getElementById('instruction');
            if (field === 'from') {
                document.getElementById('from_address').classList.add('active-field');
                hint.innerText = "👇 Вибрано «Звідки». Натисніть на карту для вибору.";
            } else {
                document.getElementById('to_address').classList.add('active-field');
                hint.innerText = "👇 Вибрано «Куди». Натисніть на карту для вибору.";
            }
        }

        // Клік по карті імітує вибір популярної точки в Кобеляках
        document.getElementById('mapBox').addEventListener('click', () => {
            const points = [
                "Центр (Автостанція)",
                "Лікарня",
                "Парк",
                "Вулиця Калініна",
                "Вулиця Шевченка",
                "Мікрорайон"
            ];
            const randomPoint = points[Math.floor(Math.random() * points.length)];

            if (activeField === 'from') {
                document.getElementById('from_address').value = randomPoint;
                setActiveField('to'); // Автоматично перемикаємо на «Куди»
            } else {
                document.getElementById('to_address').value = randomPoint;
            }
        });

        document.getElementById("submitBtn").addEventListener("click", () => {
            const from = document.getElementById("from_address").value || "Центр (Кобеляки)";
            const to = document.getElementById("to_address").value || "По місту";

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
