from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import os
import time
import requests
from tcheck import TcheckAutomation


class RequestHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            # Lecture des données reçues
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            print(f"Données brutes reçues: {post_data.decode('utf-8')}")

            # Récupération des données de Airtable
            url = data.get("url")
            vin = data.get("vin")
            license_plate = data.get("license_plate")
            mileage = data.get("mileage")
            brand = data.get("brand")
            model = data.get("model")
            color = data.get("color")
            client_name = data.get("client_name")
            client_firstname = data.get("client_firstname")
            client_email = data.get("client_email")
            client_phone = data.get("client_phone")

            information = {
                "vin": vin,
                "license_plate": license_plate,
                "mileage": mileage,
                "brand": brand,
                "model": model,
                "color": color,
                "client_name": client_name,
                "client_firstname": client_firstname,
                "client_email": client_email,
                "client_phone": client_phone
            }

            print("Lancement du processus Tchek...")
            launch_tchek_process(url, information)
            print("Processus Tchek terminé avec succès")

            # Envoi de la réponse avec le numéro de facture
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({
                "message": "Request received successfully",
                "status": 200
            }).encode('utf-8'))

        except Exception as e:
            print(f"Erreur serveur: {str(e)}")
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode('utf-8'))


def launch_tchek_process(url, information):
    """Lance le processus TcheckAutomation"""
    try:
        with TcheckAutomation() as automation:
            print(f"Navigation vers {url}")
            automation.page.goto(url)

            # Attendre le chargement initial
            print("Attente du chargement initial...")
            automation.page.wait_for_load_state("networkidle")
            time.sleep(1)

            # Connexion
            print("Tentative de connexion...")
            automation.login(
                "aurelien.bernard+MPC@monpetitcarrossier.com",
                "Monpetitcarrossier2024"
            )

            # Remplir les informations
            automation.fill_information(information)

    except Exception as e:
        print(f"Erreur lors du processus Tchek : {str(e)}")
        raise e


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