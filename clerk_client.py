import requests

class Clerk:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://api.clerk.com/v1"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    def get_user(self, user_id):
        """
        Fetches user details from Clerk using their User ID.
        """
        try:
            response = requests.get(f"{self.base_url}/users/{user_id}", headers=self.headers)
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Error fetching user: {response.status_code} - {response.text}")
                return None
        except Exception as e:
            print(f"Connection error: {e}")
            return None

    def get_email_address(self, user_id):
        """
        Helper to get the primary email of a user.
        """
        user_data = self.get_user(user_id)
        if user_data:
            try:
                return user_data['email_addresses'][0]['email_address']
            except (KeyError, IndexError):
                return "No Email Found"
        return None