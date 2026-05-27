#!/usr/bin/env python3
"""
OFP Server Query API
Python port of the Ruby OFP server status query API
"""

import socket
import json
import ipaddress
import time
import re
from urllib.parse import parse_qs
from concurrent.futures import ThreadPoolExecutor

# Constants
TIMEOUT_LIMIT = (0.1, 5.0)
BUFFER_SIZE = 4096
DEFAULT_TIMEOUT = 2.0


def query_server(ip: str, port: int, timeout: float = DEFAULT_TIMEOUT) -> dict:
    """
    Query an OFP server for status information
    
    Args:
        ip: Server IP address
        port: Query port (game port + 1)
        timeout: Timeout in seconds
    
    Returns:
        Dictionary containing server status data
    """
    sock = None
    try:
        # Create UDP socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(timeout)
        
        # Connect and send status request
        sock.connect((ip, port))
        sock.send(b"\\status\\")
        
        # Receive response
        start_time = time.time()
        data, _ = sock.recvfrom(BUFFER_SIZE)
        elapsed = time.time() - start_time
        
        # Decode data, replacing invalid characters
        data = data.decode('utf-8', errors='replace')
        
        # Parse the response
        parts = data.split("\\")
        parts.pop(0)  # Remove empty first element
        
        # Find where "final" appears (end of server data)
        try:
            final_index = parts.index("final")
        except ValueError:
            final_index = len(parts)
        
        # Build dictionary from key-value pairs
        raw_data = {}
        for i in range(0, final_index - 1, 2):
            if i + 1 < final_index:
                raw_data[parts[i]] = parts[i + 1]
        
        raw_data['players'] = []
        raw_data['replied_in'] = elapsed
        
        # Parse player data
        i = 0
        while True:
            player_key = f"player_{i}"
            if player_key not in raw_data:
                break
            
            player = {}
            for info in ['player', 'team', 'score', 'deaths']:
                key = f"{info}_{i}"
                if key in raw_data:
                    player[info] = raw_data.pop(key)
            
            raw_data['players'].append(player)
            i += 1
        
        # Convert numeric fields where appropriate
        for field in ['numplayers', 'maxplayers', 'gstate']:
            if field in raw_data:
                try:
                    raw_data[field] = int(raw_data[field])
                except ValueError:
                    pass
        
        return raw_data
        
    except socket.timeout:
        raise TimeoutError(f"Query to {ip}:{port} timed out")
    except Exception as e:
        raise RuntimeError(f"Error querying server: {e}")
    finally:
        if sock:
            sock.close()


def parse_path(path: str):
    """
    Parse path to extract IP and port
    Expected format: /IP:PORT or /IP/PORT
    """
    # Remove leading/trailing slashes
    path = path.strip('/')
    
    # Try different separators
    if ':' in path:
        ip_part, port_part = path.split(':', 1)
    elif '/' in path:
        ip_part, port_part = path.split('/', 1)
    else:
        raise ValueError(f"Invalid path format: {path}")
    
    # Resolve hostname to IP if needed
    try:
        ip = socket.gethostbyname(ip_part)
    except socket.gaierror:
        raise ValueError(f"Cannot resolve hostname: {ip_part}")
    
    # Validate IP
    try:
        ipaddress.ip_address(ip)
    except ValueError:
        raise ValueError(f"Invalid IP address: {ip}")
    
    # Parse port
    try:
        port = int(port_part)
    except ValueError:
        raise ValueError(f"Invalid port: {port_part}")
    
    return ip, port


def lambda_handler(event: dict, context: dict = None) -> dict:
    """
    AWS Lambda handler compatible interface
    
    Expected event:
        - pathParameters: {"proxy": "IP:PORT"}
        - queryStringParameters: {"timeout": "2.0"} (optional)
    """
    try:
        # Get path parameter
        if event.get('pathParameters') and event['pathParameters'].get('proxy'):
            path = event['pathParameters']['proxy']
        elif event.get('path'):
            path = event['path']
        else:
            return {
                'statusCode': 400,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Content-Type': 'application/json'
                },
                'body': json.dumps({'error': 'missing path parameter'})
            }
        
        # Get timeout from query string
        timeout = DEFAULT_TIMEOUT
        if event.get('queryStringParameters'):
            timeout_param = event['queryStringParameters'].get('timeout')
            if timeout_param:
                try:
                    t = float(timeout_param)
                    if TIMEOUT_LIMIT[0] <= t <= TIMEOUT_LIMIT[1]:
                        timeout = t
                except ValueError:
                    pass
        
        # Parse and query
        ip, port = parse_path(path)
        # Query port is game port + 1
        result = query_server(ip, port + 1, timeout)
        
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Content-Type': 'application/json'
            },
            'body': json.dumps(result)
        }
        
    except ValueError as e:
        return {
            'statusCode': 400,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Content-Type': 'application/json'
            },
            'body': json.dumps({'error': str(e)})
        }
    except TimeoutError as e:
        return {
            'statusCode': 408,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Content-Type': 'application/json'
            },
            'body': json.dumps({'error': str(e)})
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Content-Type': 'application/json'
            },
            'body': json.dumps({'error': 'Internal server error'})
        }


# Flask version for local development
def create_flask_app():
    """Create a Flask application for local development"""
    try:
        from flask import Flask, request, jsonify
    except ImportError:
        print("Flask not installed. Run: pip install flask")
        return None
    
    app = Flask(__name__)
    
    @app.route('/<path:server_path>', methods=['GET'])
    def query(server_path):
        """GET /IP:PORT endpoint"""
        try:
            # Get timeout parameter
            timeout = float(request.args.get('timeout', DEFAULT_TIMEOUT))
            if not (TIMEOUT_LIMIT[0] <= timeout <= TIMEOUT_LIMIT[1]):
                timeout = DEFAULT_TIMEOUT
        except (ValueError, TypeError):
            timeout = DEFAULT_TIMEOUT
        
        try:
            ip, port = parse_path(server_path)
            result = query_server(ip, port + 1, timeout)
            return jsonify(result)
        except ValueError as e:
            return jsonify({'error': str(e)}), 400
        except TimeoutError as e:
            return jsonify({'error': str(e)}), 408
        except Exception as e:
            return jsonify({'error': 'Internal server error'}), 500
    
    @app.errorhandler(404)
    def not_found(e):
        return jsonify({'error': 'Not found'}), 404
    
    return app


# FastAPI version for modern async support
def create_fastapi_app():
    """Create a FastAPI application for async support"""
    try:
        from fastapi import FastAPI, Path, Query, HTTPException
        from fastapi.middleware.cors import CORSMiddleware
        from fastapi.responses import JSONResponse
    except ImportError:
        print("FastAPI not installed. Run: pip install fastapi uvicorn")
        return None
    
    app = FastAPI(title="OFP Server Query API")
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    @app.get("/{server_path:path}")
    async def query(
        server_path: str = Path(..., description="IP:PORT format"),
        timeout: float = Query(default=DEFAULT_TIMEOUT, ge=TIMEOUT_LIMIT[0], le=TIMEOUT_LIMIT[1])
    ):
        try:
            ip, port = parse_path(server_path)
            result = await asyncio.to_thread(query_server, ip, port + 1, timeout)
            return result
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except TimeoutError as e:
            raise HTTPException(status_code=408, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail="Internal server error")
    
    return app


# Simple HTTP server for standalone deployment
class OFPQueryHandler:
    """Simple HTTP handler for the OFP query API"""
    
    def __init__(self, host='0.0.0.0', port=8080):
        self.host = host
        self.port = port
        self.executor = ThreadPoolExecutor(max_workers=10)
    
    def handle_request(self, client_socket, address):
        """Handle a single HTTP request"""
        try:
            request = client_socket.recv(BUFFER_SIZE).decode('utf-8', errors='replace')
            if not request:
                return
            
            # Parse request line
            lines = request.split('\r\n')
            if not lines:
                return
            
            method, path, version = lines[0].split(' ')
            
            # Only handle GET requests
            if method != 'GET':
                self.send_response(client_socket, 405, {'error': 'Method not allowed'})
                return
            
            # Parse query string for timeout
            timeout = DEFAULT_TIMEOUT
            if '?' in path:
                path, query_string = path.split('?', 1)
                params = parse_qs(query_string)
                if 'timeout' in params:
                    try:
                        t = float(params['timeout'][0])
                        if TIMEOUT_LIMIT[0] <= t <= TIMEOUT_LIMIT[1]:
                            timeout = t
                    except ValueError:
                        pass
            
            # Parse and query
            ip, port = parse_path(path)
            result = query_server(ip, port + 1, timeout)
            self.send_response(client_socket, 200, result)
            
        except ValueError as e:
            self.send_response(client_socket, 400, {'error': str(e)})
        except TimeoutError as e:
            self.send_response(client_socket, 408, {'error': str(e)})
        except Exception as e:
            self.send_response(client_socket, 500, {'error': 'Internal server error'})
        finally:
            client_socket.close()
    
    def send_response(self, client_socket, status_code, data):
        """Send HTTP response"""
        body = json.dumps(data)
        response = f"""HTTP/1.1 {status_code} OK\r
Content-Type: application/json\r
Access-Control-Allow-Origin: *\r
Content-Length: {len(body)}\r
Connection: close\r
\r
{body}"""
        client_socket.send(response.encode('utf-8'))
    
    def start(self):
        """Start the HTTP server"""
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((self.host, self.port))
        server_socket.listen(5)
        
        print(f"OFP Query API listening on {self.host}:{self.port}")
        print(f"Example: curl http://localhost:{self.port}/1.2.3.4:2302")
        
        try:
            while True:
                client_socket, addr = server_socket.accept()
                self.executor.submit(self.handle_request, client_socket, addr)
        except KeyboardInterrupt:
            print("\nShutting down...")
        finally:
            server_socket.close()
            self.executor.shutdown()


# CLI entry point
if __name__ == '__main__':
    import sys
    import asyncio
    
    if len(sys.argv) > 1 and sys.argv[1] == '--flask':
        app = create_flask_app()
        if app:
            app.run(host='0.0.0.0', port=8080, debug=False)
    elif len(sys.argv) > 1 and sys.argv[1] == '--fastapi':
        app = create_fastapi_app()
        if app:
            import uvicorn
            uvicorn.run(app, host='0.0.0.0', port=8080)
    else:
        # Default: simple HTTP server
        handler = OFPQueryHandler()
        handler.start()

# Usage Examples
# 1. Simple HTTP Server (No dependencies)
# python ofp_api.py
# curl "http://localhost:8080/1.2.3.4:2302"

# 2. Flask Server
# pip install flask
# python ofp_api.py --flask

# 3. FastAPI Server (Async)
# pip install fastapi uvicorn
# python ofp_api.py --fastapi

# 4. AWS Lambda
# from ofp_api import lambda_handler

# event = {
#     'pathParameters': {'proxy': '1.2.3.4:2302'},
#     'queryStringParameters': {'timeout': '2.0'}
# }
# response = lambda_handler(event)

# API Response Example
# {
#     "hostname": "My OFP Server",
#     "numplayers": 4,
#     "maxplayers": 32,
#     "mission": "1-8_D_Paintball.ABEL",
#     "gamever": "1.96",
#     "gstate": 14,
#     "players": [
#         {"player": "Player1", "team": "WEST", "score": "10", "deaths": "2"},
#         {"player": "Player2", "team": "EAST", "score": "5", "deaths": "4"}
#     ],
#     "replied_in": 0.023
# }