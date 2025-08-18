<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Loading...</title>
    <style>
        body {
            margin: 0;
            padding: 0;
            height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            background-color: white;
            font-family: Arial, sans-serif;
        }

        .loading-container {
            text-align: center;
        }

        .loading-text {
            font-size: 48px;
            font-weight: bold;
            color: #333;
            display: inline-block;
        }

        .dots {
            font-size: 48px;
            font-weight: bold;
            color: #333;
            display: inline-block;
            min-width: 120px;
            text-align: left;
        }
    </style>
</head>
<body>
    <div class="loading-container">
        <span class="loading-text">Loading</span>
        <span class="dots" id="loadingDots">.</span>
    </div>

    <script>
        let dotCount = 1;
        let increasing = true;
        
        function updateDots() {
            const dotsElement = document.getElementById('loadingDots');
            dotsElement.textContent = '.'.repeat(dotCount);
            
            if (increasing) {
                dotCount++;
                if (dotCount === 5) {
                    increasing = false;
                }
            } else {
                dotCount--;
                if (dotCount === 1) {
                    increasing = true;
                }
            }
        }
        
        // 500ms마다 점 업데이트
        setInterval(updateDots, 500);
    </script>
</body>
</html>
