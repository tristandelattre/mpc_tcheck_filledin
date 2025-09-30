from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import os
import base64
import io
import requests


class RequestHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            # Lecture des données reçues
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))

            # Récupération et décodage des données PDF
            data_pdf = data.get("data_bytes_pdf")
            # Conversion base64 en bytes
            pdf_bytes = base64.b64decode(data_pdf)
            # Création d'un objet BytesIO
            pdf_stream = io.BytesIO(pdf_bytes)

            # Extraction du numéro de facture avec le stream
            invoice_number = extract_invoice_id(pdf_stream)

            # Envoi de la réponse avec le numéro de facture
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({
                "message": "Request received successfully",
                "status": 200,
                "invoice_number": invoice_number
            }).encode('utf-8'))

        except Exception as e:
            print(f"Erreur serveur: {str(e)}")
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode('utf-8'))


def run_server():
    # Récupérer le port depuis la variable d'environnement
    port = int(os.environ.get('PORT', '8080'))
    print(f"Démarrage du serveur sur le port {port}")

    # Important : utiliser '0.0.0.0' au lieu de '' pour écouter sur toutes les interfaces
    server_address = ('0.0.0.0', port)
    httpd = HTTPServer(server_address, RequestHandler)
    print(f"Serveur démarré sur le port {port}")
    httpd.serve_forever()


if __name__ == '__main__':
    run_server()