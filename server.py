import json
import os
import hashlib
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from hash_utils import calculate_hash, save_hash, verify_integrity


class HashHandler(BaseHTTPRequestHandler):
    
    def do_GET(self):
        parsed_path = urlparse(self.path)
        
        if parsed_path.path == '/' or parsed_path.path == '/index.html':
            self.serve_html('web_interface.html')
        elif parsed_path.path == '/style.css':
            self.serve_css()
        else:
            self.send_response(404)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b'404 Not Found')
    
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        data = json.loads(post_data.decode('utf-8'))
        
        parsed_path = urlparse(self.path)
        
        if parsed_path.path == '/api/hash':
            response = self.handle_hash(data)
        elif parsed_path.path == '/api/save':
            response = self.handle_save(data)
        elif parsed_path.path == '/api/verify':
            response = self.handle_verify(data)
        elif parsed_path.path == '/api/upload':
            response = self.handle_upload(data)
        else:
            response = {'success': False, 'error': 'Unknown endpoint'}
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(response).encode('utf-8'))
    
    def handle_hash(self, data):
        try:
            file_path = data.get('file_path', '')
            algorithm = data.get('algorithm', 'sha256')
            
            if not os.path.exists(file_path):
                return {'success': False, 'error': f'Файл не найден: {file_path}'}
            
            hash_value = calculate_hash(file_path, algorithm, progress=False)
            
            return {
                'success': True,
                'hash': hash_value,
                'algorithm': algorithm,
                'file': file_path
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def handle_save(self, data):
        try:
            file_path = data.get('file_path', '')
            algorithm = data.get('algorithm', 'sha256')
            
            if not os.path.exists(file_path):
                return {'success': False, 'error': f'Файл не найден: {file_path}'}
            
            hash_value = calculate_hash(file_path, algorithm, progress=False)
            hash_path = save_hash(file_path, hash_value)
            
            return {
                'success': True,
                'hash': hash_value,
                'hash_file': hash_path,
                'algorithm': algorithm
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def handle_verify(self, data):
        try:
            file_path = data.get('file_path', '')
            hash_file = data.get('hash_file', None)
            
            if not os.path.exists(file_path):
                return {'success': False, 'error': f'Файл не найден: {file_path}'}
            
            is_valid, current_hash, saved_hash = verify_integrity(file_path, hash_file, progress=False)
            
            return {
                'success': True,
                'is_valid': is_valid,
                'current_hash': current_hash,
                'saved_hash': saved_hash
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def handle_upload(self, data):
        try:
            content = data.get('content', '')
            filename = data.get('filename', 'uploaded.txt')
            algorithm = data.get('algorithm', 'sha256')
            
            file_path = os.path.join('uploads', filename)
            os.makedirs('uploads', exist_ok=True)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            hash_value = calculate_hash(file_path, algorithm, progress=False)
            
            return {
                'success': True,
                'file_path': file_path,
                'hash': hash_value,
                'algorithm': algorithm
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def serve_html(self, filename):
        try:
            with open(filename, 'rb') as f:
                content = f.read()
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(content)
        except FileNotFoundError:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'File not found')
    
    def serve_css(self):
        css = """
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', 'Roboto', sans-serif;
            background: linear-gradient(135deg, #e8eef4 0%, #dce5f0 100%);
            min-height: 100vh;
            padding: 30px 20px;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        
        h1 {
            text-align: center;
            font-size: 2.2rem;
            font-weight: 300;
            background: linear-gradient(120deg, #5b7c9e, #8ba3bc);
            -webkit-background-clip: text;
            background-clip: text;
            color: transparent;
            margin-bottom: 10px;
        }
        
        .subtitle {
            text-align: center;
            color: #7b8a9b;
            margin-bottom: 30px;
        }
        
        .tabs {
            display: flex;
            gap: 10px;
            margin-bottom: 25px;
            justify-content: center;
        }
        
        .tab-btn {
            padding: 12px 28px;
            background: rgba(255,255,255,0.6);
            border: none;
            border-radius: 30px;
            font-size: 16px;
            font-weight: 500;
            cursor: pointer;
            color: #6b7f96;
            transition: all 0.3s;
        }
        
        .tab-btn:hover {
            background: rgba(255,255,255,0.9);
            transform: translateY(-2px);
        }
        
        .tab-btn.active {
            background: white;
            color: #5b7c9e;
            box-shadow: 0 5px 15px rgba(91,124,158,0.15);
        }
        
        .tab-content {
            background: rgba(255,255,255,0.95);
            border-radius: 25px;
            padding: 30px;
            min-height: 500px;
        }
        
        .tab-pane {
            display: none;
        }
        
        .tab-pane.active {
            display: block;
            animation: fadeIn 0.4s ease;
        }
        
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        .form-group {
            margin-bottom: 20px;
        }
        
        label {
            display: block;
            margin-bottom: 8px;
            font-weight: 500;
            color: #8ba3bc;
        }
        
        input, select, textarea {
            width: 100%;
            padding: 12px 15px;
            border: 1px solid #dce4ec;
            border-radius: 12px;
            font-size: 14px;
            background: white;
            transition: all 0.3s;
        }
        
        input:focus, select:focus, textarea:focus {
            outline: none;
            border-color: #b8cadf;
            box-shadow: 0 0 0 3px rgba(184,202,223,0.2);
        }
        
        textarea {
            resize: vertical;
            font-family: monospace;
        }
        
        .file-row {
            display: flex;
            gap: 10px;
            align-items: center;
        }
        
        .file-row input {
            flex: 1;
        }
        
        button {
            background: #e8edf2;
            color: #7b8a9b;
            padding: 12px 25px;
            border: none;
            border-radius: 12px;
            font-size: 14px;
            font-weight: 500;
            cursor: pointer;
            transition: all 0.3s;
        }
        
        button:hover {
            background: #dde4ea;
            transform: translateY(-1px);
        }
        
        .btn-primary {
            background: linear-gradient(120deg, #8ba3bc, #7b8a9b);
            color: white;
        }
        
        .btn-primary:hover {
            background: linear-gradient(120deg, #7b8a9b, #6b7f96);
        }
        
        .result-box {
            margin-top: 20px;
            padding: 20px;
            background: #f8fafd;
            border-radius: 15px;
            border: 1px solid #e8edf2;
        }
        
        .result-box h4 {
            color: #5b7c9e;
            margin-bottom: 15px;
        }
        
        .hash-value {
            font-family: monospace;
            word-break: break-all;
            background: #eef2f7;
            padding: 12px;
            border-radius: 10px;
            font-size: 12px;
        }
        
        .success {
            color: #7cb5a0;
        }
        
        .error {
            color: #d4a5a5;
        }
        
        .info {
            color: #8ba3bc;
        }
        
        .radio-group {
            display: flex;
            gap: 20px;
            align-items: center;
            margin-top: 8px;
        }
        
        .radio-group label {
            display: flex;
            align-items: center;
            gap: 8px;
            font-weight: normal;
            margin-bottom: 0;
        }
        
        .radio-group input {
            width: 18px;
            height: 18px;
            accent-color: #8ba3bc;
        }
        
        .progress-bar {
            width: 100%;
            height: 6px;
            background: #e8edf2;
            border-radius: 3px;
            overflow: hidden;
            margin: 10px 0;
            display: none;
        }
        
        .progress-fill {
            width: 0%;
            height: 100%;
            background: linear-gradient(90deg, #8ba3bc, #5b7c9e);
            border-radius: 3px;
            transition: width 0.3s;
        }
        """
        
        self.send_response(200)
        self.send_header('Content-type', 'text/css')
        self.end_headers()
        self.wfile.write(css.encode('utf-8'))
    
    def log_message(self, format, *args):
        pass


def main():
    port = 8000
    server = HTTPServer(('localhost', port), HashHandler)
    print(f'Сервер запущен на http://localhost:{port}')
    print('Нажмите Ctrl+C для остановки')
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print('\nСервер остановлен')
        server.server_close()


if __name__ == '__main__':
    main()