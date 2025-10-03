from playwright.sync_api import sync_playwright
import time
import subprocess
import sys


class TcheckAutomation:
    def __init__(self):
        self.browser = None
        self.context = None
        self.page = None

    @staticmethod
    def install_playwright_browsers():
        """Installe les navigateurs Playwright si nécessaire"""
        print("Installation des navigateurs Playwright...")
        subprocess.run([sys.executable, "-m", "playwright", "install", "chromium"])
        print("Installation terminée.")

    def initialize_browser(self):
        """Initialise le navigateur et crée une nouvelle page"""
        try:
            self.playwright = sync_playwright().start()
            self.browser = self.playwright.chromium.launch(
                headless=False,  # Activation du mode headless
                args=[
                    '--no-sandbox',
                    '--disable-setuid-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-gpu'
                ]
            )
            self.context = self.browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                ignore_https_errors=True
            )
            self.page = self.context.new_page()
        except Exception as e:
            if "Executable doesn't exist" in str(e):
                print("Les navigateurs Playwright ne sont pas installés. Installation en cours...")
                self.install_playwright_browsers()
                print("Veuillez relancer le script.")
                sys.exit(1)
            raise e

    def clear_and_fill(self,locator, value):
        field = self.page.locator(locator)
        field.fill("")
        if value:  # Vérifier si la valeur n'est pas None ou vide
            field.type(value, delay=20)

    def fill_information(self, information_to_fill=None):
        vin = information_to_fill.get("vin")
        mileage = information_to_fill.get("mileage")
        brand = information_to_fill.get("brand")
        model = information_to_fill.get("model")
        color = information_to_fill.get("color")
        licence_plate = information_to_fill.get("license_plate")

        # Attendre que la page soit chargée
        self.page.wait_for_load_state("networkidle")

        self.clear_and_fill('input[formcontrolname="vin"]', vin)
        self.clear_and_fill('input[formcontrolname="immat"]', licence_plate)
        self.clear_and_fill('input[formcontrolname="mileage"]', mileage)
        self.clear_and_fill('input[formcontrolname="brand"]', brand)
        self.clear_and_fill('input[formcontrolname="model"]', model)
        self.clear_and_fill('input[formcontrolname="color"]', color)

        update_button = self.page.locator('button:has-text("Mettre à jour le véhicule")')
        update_button.click()

        # Attendre que le bouton disparaisse ou ne soit plus désactivé
        print("Attente de la fin du traitement...")
        self.page.wait_for_selector('button:has-text("Mettre à jour le véhicule")[disabled]',
                                    state="hidden",
                                    timeout=30000)  # 30 secondes maximum d'attente

        # Attendre un peu que la page se stabilise
        self.page.wait_for_load_state("networkidle")

        client_name = information_to_fill.get("client_name")
        client_firstname = information_to_fill.get("client_firstname")
        client_email = information_to_fill.get("client_email")
        client_phone = information_to_fill.get("client_phone")

        self.clear_and_fill('#mat-input-6', client_name)
        self.clear_and_fill('#mat-input-7', client_firstname)
        self.clear_and_fill('#mat-input-8', client_email)
        self.clear_and_fill('#mat-input-9', client_phone)

        update_button = self.page.locator('button:has-text("Mettre à jour les informations client")')
        update_button.click()

        # Attendre que le bouton disparaisse ou ne soit plus désactivé
        print("Attente de la fin du traitement...")
        self.page.wait_for_selector('button:has-text("Mettre à jour les informations client")[disabled]',
                                    state="hidden",
                                    timeout=30000)  # 30 secondes maximum d'attente

        # Attendre un peu que la page se stabilise
        self.page.wait_for_load_state("networkidle")

    def login(self, login, password):
        """
        Remplit les champs de connexion et clique sur le bouton de connexion
        """
        try:
            print("Début de la tentative de connexion...")

            # Attendre que la page soit chargée
            self.page.wait_for_load_state("networkidle")
            self.page.wait_for_load_state("domcontentloaded")

            # Email
            print("Attente du champ email...")
            self.page.wait_for_selector('input[formcontrolname="username"]', state="visible", timeout=30000)
            email_field = self.page.locator('input[formcontrolname="username"]')
            email_field.click()
            email_field.type(login, delay=20)

            # Mot de passe
            print("Attente du champ mot de passe...")
            self.page.wait_for_selector('input[formcontrolname="password"]', state="visible", timeout=30000)
            password_field = self.page.locator('input[formcontrolname="password"]')
            password_field.click()
            password_field.type(password, delay=20)

            # Bouton de connexion
            print("Recherche du bouton de connexion...")
            self.page.wait_for_selector('button.btn.btn-green:has-text("Se connecter")', state="visible", timeout=30000)
            login_button = self.page.locator('button.btn.btn-green:has-text("Se connecter")')
            login_button.click()

            # Attendre la fin du chargement après connexion
            print("Attente après connexion...")
            self.page.wait_for_load_state("networkidle")
            time.sleep(1)  # Attente supplémentaire pour s'assurer que tout est chargé

            # Recherche du bouton Identification avec plusieurs tentatives
            print("Recherche du bouton Identification...")
            max_attempts = 5
            for attempt in range(max_attempts):
                try:
                    # Attendre que le bouton soit présent dans le DOM
                    self.page.wait_for_selector('span.mdc-button__label:text("Identification")',
                                                state="visible",
                                                timeout=20000)

                    # Trouver et cliquer sur le bouton
                    identify_button = self.page.locator('span.mdc-button__label:text("Identification")')
                    if identify_button.is_visible():
                        print("Bouton Identification trouvé")
                        identify_button.click()
                        break
                except Exception as e:
                    print(f"Tentative {attempt + 1}/{max_attempts} échouée: {str(e)}")
                    if attempt < max_attempts - 1:
                        print("Attente avant nouvelle tentative...")
                        time.sleep(1)
                    else:
                        print("Échec de toutes les tentatives")
                        self.page.screenshot(path="identification_button_not_found.png")
                        raise Exception("Impossible de trouver le bouton Identification après plusieurs tentatives")

            # Attendre la fin du chargement
            self.page.wait_for_load_state("networkidle")
            time.sleep(1)

        except Exception as e:
            print(f"Erreur détaillée lors de la connexion : {str(e)}")
            self.page.screenshot(path="error_screenshot.png")
            raise

    def close(self):
        """Ferme le navigateur et termine la session"""
        if self.browser:
            self.browser.close()
        if hasattr(self, 'playwright'):
            self.playwright.stop()

    def __enter__(self):
        """Permet l'utilisation du context manager (with statement)"""
        self.initialize_browser()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Ferme automatiquement le navigateur à la fin du bloc with"""
        self.close()


def main():
    url = "https://webapp.tchek.fr/fr/tchek/wu3dZngvYC/estimation"

    information = {
        "vin": "VF1RJL009UC337954",
        "license_plate": "XX-123-XX",
        "mileage": "808451",
        "brand": "RENAULT1",
        "model": "ARKANA1",
        "color": "NOIR1",
        "client_name": "Nom",
        "client_firstname": "Prénom",
        "client_email": "email@exemple.com",
        "client_phone": "0123456789"
    }

    with TcheckAutomation() as automation:
        print(f"Navigation vers {url}")
        automation.page.goto(url)

        # Vérifier que la page est chargée
        print("Attente du chargement initial...")
        automation.page.wait_for_load_state("networkidle")
        time.sleep(1)

        print("Page chargée, tentative de connexion...")
        automation.login(
            "aurelien.bernard+MPC@monpetitcarrossier.com",
            "Monpetitcarrossier2024"
        )
        automation.fill_information(information)


if __name__ == "__main__":
    main()