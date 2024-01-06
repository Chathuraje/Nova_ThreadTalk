import json
import logging
import random
import hashlib
import requests
import datetime

class TikTokTokenData:
    def __init__(
        self, 
        token_path=None,
        apps_id=None, 
        client_key=None, 
        client_secret=None, 
        redirect_uri="http://127.0.0.1:8000/tiktok_auth_callback",
        csrf_state=None, 
        code_verifier=None, 
        access_token=None,
        expires_in=0,
        open_id=None, 
        refresh_expires_in=0,
        refresh_token=None, 
        scope=None,
        approved_scopes=None,
        token_type=None
    ):
        
        self.token_path = token_path
        self.apps_id = apps_id
        self.client_key = client_key
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.csrf_state = csrf_state
        self.code_verifier = code_verifier
        self.access_token = access_token
        self.expires_in = expires_in
        self.open_id = open_id
        self.refresh_expires_in = refresh_expires_in
        self.refresh_token = refresh_token
        self.scope = scope
        self.approved_scopes = approved_scopes
        self.token_type = token_type

        if expires_in:
            self.expiry = datetime.datetime.utcnow() + datetime.timedelta(seconds=expires_in)
        else:
            self.expiry = None
        
        if refresh_expires_in:
            self.refresh_expiry = datetime.datetime.utcnow() + datetime.timedelta(seconds=refresh_expires_in)
        else:
            self.refresh_expiry = None
            
    def setup_from_client_secrets_file(self, token_path, scopes_val):
        try:
            self.token_path = token_path
            with open(token_path, "r") as file:
                config = json.load(file)
            
            if 'auth' in config:
                auth_config = config['auth']
                apps_id = auth_config.get('apps_id', None)
                client_key = auth_config.get('client_key', None)
                client_secret = auth_config.get('client_secret', None)
                code_verifier = auth_config.get('code_verifier', None)
                csrf_state = auth_config.get('csrf_state', None)
                
                if apps_id is None or client_key is None or client_secret is None:
                    missing_keys = [key for key, value in [('apps_id', apps_id), ('client_key', client_key), ('client_secret', client_secret)] if value is None]
                    raise KeyError(f"Json configuration file is missing the following keys: {', '.join(missing_keys)}")
            
                self.apps_id = apps_id
                self.client_key = client_key
                self.client_secret = client_secret
                self.scope = scopes_val
                
                if code_verifier is not None:
                    self.code_verifier = code_verifier
                if csrf_state is not None:
                    self.csrf_state = csrf_state
                
            else:
                raise ValueError("JSON file does not contain 'auth' object")

        except FileNotFoundError:
            raise FileNotFoundError("Configuration file not found.")
        except json.JSONDecodeError:
            raise json.JSONDecodeError("Error decoding JSON from configuration file.")
        except Exception as e:
            raise Exception(f"An error occurred: {e}")
        

    @staticmethod
    def generate_random_string(length):
        try:
            return ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-._~', k=length))
        except Exception as e:
            raise ValueError("Error generating random string")

    def get_authorization_url(self):
        try:
        
            self.csrf_state = self.generate_random_string(6)
            self.code_verifier = self.generate_random_string(128)
            code_challenge = hashlib.sha256(self.code_verifier.encode()).hexdigest()
            authorization_url = 'https://www.tiktok.com/v2/auth/authorize/'
            authorization_url += f'?client_key={self.client_key}'
            authorization_url += f'&scope={",".join(self.scope)}'
            authorization_url += '&response_type=code'
            authorization_url += f'&redirect_uri={self.redirect_uri}'
            authorization_url += f'&state={self.csrf_state}'
            authorization_url += f'&code_challenge={code_challenge}'
            authorization_url += '&code_challenge_method=S256'
            
            try:
                with open(self.token_path, 'r') as file:
                    data = json.load(file)
                    
                data['auth']['csrf_state'] = self.csrf_state
                data['auth']['code_verifier'] = self.code_verifier
                    
                with open(self.token_path, 'w') as file:
                    json.dump(data, file, indent=4)
                
                    
            except FileNotFoundError as e:
                raise FileNotFoundError(f"Configuration file not found. {e}")
            except json.JSONDecodeError as e:
                raise json.JSONDecodeError(f"Error decoding JSON from configuration file. {e}")
            except IOError as e:
                raise IOError(f"Error reading configuration file. {e}")
            except Exception as e:
                raise Exception(f"An error occurred: {e}")
                

            return authorization_url
        except Exception as e:
            raise ValueError(f"Error generating authorization URL: {e}")
    
    
    def get_refresh_token(self, request, code, scopes, state):
        try:
            if state != self.csrf_state:
                raise ValueError('CSRF state mismatch.')
            
            token_url = 'https://open.tiktokapis.com/v2/oauth/token/'
            params = {
                'client_key': self.client_key,
                'client_secret': self.client_secret,
                'code': code,
                'redirect_uri': self.redirect_uri,
                'grant_type': 'authorization_code',
                'code_verifier': self.code_verifier,
            }

            response = requests.post(token_url, data=params)
            if response.status_code == 200:
                token_data = response.json()
                
                if 'error' in token_data:
                    error_message = token_data.get('error_description', 'Unknown error')
                    raise ValueError(f"{error_message}")
                    
                try:
                    with open(self.token_path, 'r') as file:
                        data = json.load(file)
                    
                    data['auth'].pop('csrf_state', None)
                    data['auth'].pop('code_verifier', None)
                    self.csrf_state = None
                    self.code_verifier = None
                        
                    with open(self.token_path, 'w') as file:
                        json.dump(data, file, indent=4)
                    
                    
                except FileNotFoundError as e:
                    raise FileNotFoundError(f"Configuration file not found. {e}")
                except json.JSONDecodeError as e:
                    raise json.JSONDecodeError(f"Error decoding JSON from configuration file. {e}")
                except IOError as e:
                    raise IOError(f"Error reading configuration file. {e}")
                except Exception as e:
                    raise Exception(f"An error occurred: {e}")
                    
                    
                self.update_token_data(token_data)
                return token_data
            else:
                raise ValueError(f"Failed to get access token: {response.text}")
        except requests.RequestException as e:
            raise ValueError("Error in accessing the token endpoint")
        
    
    # def is_expired(self):
    #     return datetime.datetime.utcnow() >= self.expiry

    # def can_refresh(self):
    #     return datetime.datetime.utcnow() < self.refresh_expiry

    # def is_token_valid(self):
    #     return not self.is_expired() or self.can_refresh()

    # def refresh(self):
    #     if not self.can_refresh():
    #         logging.error("Cannot refresh the token, refresh period has expired.")
    #         return None

    #     config = self.get_config()
    #     if not config:
    #         return None

    #     REFRESH_TOKEN_ENDPOINT = 'https://open.tiktokapis.com/v2/oauth/token/'

    #     params = {
    #         'client_key': config['client_key'],
    #         'client_secret': config['client_secret'],
    #         'grant_type': 'refresh_token',
    #         'refresh_token': self.refresh_token,
    #     }

    #     response = requests.post(REFRESH_TOKEN_ENDPOINT, data=params)
    #     if response.status_code == 200:
    #         token_data = response.json()
    #         self.update_token_data(token_data)
    #     else:
    #         logging.error(f"Failed to refresh token: {response.text}")
    #         return None

    def update_token_data(self, token_data):
        self.access_token = token_data.get('access_token')
        self.expires_in = token_data.get('expires_in')
        self.open_id = token_data.get('open_id')
        self.refresh_expires_in = token_data.get('refresh_expires_in')
        self.refresh_token = token_data.get('refresh_token')
        self.approved_scopes = token_data.get('scope')
        self.token_type = token_data.get('token_type')
        self.expiry = datetime.datetime.utcnow() + datetime.timedelta(seconds=self.expires_in)
        self.refresh_expiry = datetime.datetime.utcnow() + datetime.timedelta(seconds=self.refresh_expires_in)