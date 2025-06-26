import os
import random
import string
from locust import HttpUser, task, between

class WebsiteUser(HttpUser):
    """
    Simulates a user that:
    - Logs in at start via JWT endpoint.
    - Fetches regions and existing products once at start.
    - Periodically lists products, creates new products,
      lists/creates planted-products, etc.
    """
    wait_time = between(1, 3)  # simulate user think/wait time between tasks

    def on_start(self):
        """
        Called when a simulated user starts. We:
        1. Log in to get JWT access token.
        2. Update Authorization header.
        3. Fetch initial data: regions, products, so we can reference them in tasks.
        """
        # Use environment variables or defaults for credentials
        email = os.getenv("LOCUST_EMAIL", "vbahodir00@gmail.com")
        password = os.getenv("LOCUST_PASSWORD", "12345")

        # 1. Login to get JWT
        login_payload = {
            "login_field": email,
            "password": password
        }
        # Adjust path if your login URL is different; according to your urls.py: /accounts/login/
        with self.client.post("/accounts/login/", json=login_payload, catch_response=True) as resp:
            if resp.status_code == 200:
                # Expecting a JSON with "access" (and "refresh")
                json_data = resp.json()
                access_token = json_data.get("access")
                if access_token:
                    # Set Authorization header for all subsequent requests
                    self.client.headers.update({"Authorization": f"Bearer {access_token}"})
                else:
                    resp.failure("Login did not return access token")
                    # If you want to stop this user entirely on failure:
                    # self.environment.runner.quit()  # or other appropriate measure
            else:
                resp.failure(f"Login failed with status {resp.status_code}: {resp.text}")

        # 2. Fetch regions for use in create_planted_product
        # According to your urls: GET /regions/  (from main: path 'regions/' include regions.urls)
        with self.client.get("/regions/", catch_response=True) as resp:
            if resp.status_code == 200:
                try:
                    self.regions = resp.json()
                    # Expect a list of region objects with "id" and "name", etc.
                    if not isinstance(self.regions, list):
                        # If paginated, adjust accordingly:
                        # e.g., {"results": [...], ...}
                        if isinstance(self.regions, dict) and "results" in self.regions:
                            self.regions = self.regions["results"]
                        else:
                            # Unexpected format
                            self.regions = []
                except Exception:
                    self.regions = []
            else:
                self.regions = []

        # 3. Fetch existing products
        # According to your router: GET /products/products/
        with self.client.get("/products/products/", catch_response=True) as resp:
            if resp.status_code == 200:
                try:
                    self.products = resp.json()
                    if not isinstance(self.products, list):
                        # Handle pagination if DRF pagination is on:
                        if isinstance(self.products, dict) and "results" in self.products:
                            self.products = self.products["results"]
                        else:
                            self.products = []
                except Exception:
                    self.products = []
            else:
                self.products = []

    @task(5)
    def list_products(self):
        """
        List products. Hitting GET /products/products/.
        """
        # If pagination is enabled, DRF may return {"results": [...], ...}; we won't parse here.
        self.client.get("/products/products/")

    @task(1)
    def create_product(self):
        """
        Create a new product with a random name.
        Then, if successful, append to self.products for later use.
        """
        # Generate a semi-random name to avoid collisions:
        random_suffix = ''.join(random.choices(string.ascii_letters + string.digits, k=6))
        name = f"LocustTestProd_{random_suffix}"
        payload = {
            "name": name
        }
        with self.client.post("/products/products/", json=payload, catch_response=True) as resp:
            if resp.status_code in (200, 201):
                try:
                    data = resp.json()
                    # Expect data includes "id". Append so future tasks can use it.
                    prod_id = data.get("id")
                    if prod_id:
                        self.products.append(data)
                except Exception:
                    pass
            else:
                # Optionally record failure
                resp.failure(f"Failed to create product: {resp.status_code}")

    @task(3)
    def list_planted_products(self):
        """
        GET /products/planted-products/ to list planted products.
        """
        self.client.get("/products/planted-products/")

    @task(2)
    def create_planted_product(self):
        """
        Create a planted product, referencing an existing product and region.
        POST /products/planted-products/
        """
        # Need at least one product and one region:
        if not self.products or not self.regions:
            # Skip if we don't have data
            return

        # Choose random product and region
        prod = random.choice(self.products)
        region = random.choice(self.regions)
        prod_id = prod.get("id")
        region_id = region.get("id")
        if prod_id is None or region_id is None:
            return

        # Generate random decimal values; DRF expects strings or numbers
        planting_area = round(random.uniform(1.0, 100.0), 3)
        expecting_weight = round(random.uniform(10.0, 1000.0), 3)
        payload = {
            "product": prod_id,
            "region": region_id,
            "planting_area": str(planting_area),
            "expecting_weight": str(expecting_weight)
            # Note: owner is likely inferred from the authenticated user,
            # so we don't send "owner" explicitly unless your serializer requires it.
        }
        with self.client.post("/products/planted-products/", json=payload, catch_response=True) as resp:
            if resp.status_code in (200, 201):
                # Optionally parse and store
                pass
            else:
                resp.failure(f"Failed to create planted product: {resp.status_code}")

    @task(1)
    def get_user_profile(self):
        """
        Example of hitting another authenticated endpoint: e.g., GET /accounts/profile/
        According to your urls: path 'profile/' => /accounts/profile/
        """
        self.client.get("/accounts/profile/")

    # Optionally: add more tasks, e.g., update/delete operations if your API supports them.


    def on_stop(self):
        """
        Optionally: cleanup when user stops. E.g., logout, revoke token, etc.
        """
        # Example: call logout endpoint if exists:
        # self.client.post("/accounts/logout/")
        pass

