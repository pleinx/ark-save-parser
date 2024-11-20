import ftplib
import logging
from datetime import datetime
from io import BytesIO
from pytz import timezone, UTC
from pathlib import Path
import json

SAVE_FILES_LOCATION = ["arksa", "ShooterGame", "Saved", "SavedArks"]
INI_FOLDER_LOCATION = ["arksa", "ShooterGame", "Saved", "Config", "WindowsServer"]

SAVE_FOLDER_EXTENSION = "_WP"
SAVE_FILE_EXTENSION = ".ark"

PROFILE_FILE_EXTENSION = ".arkprofile"
TRIBE_FILE_EXTENSION = ".arktribe"
LOCAL_TIMEZONE = timezone('Europe/Berlin')

class ArkFile:
    path: str
    name: str
    last_modified: datetime

    def __init__(self, name, path, last_modified): 
        """
        Initialize ArkFile with name, path, and last_modified time.
        The last_modified time is expected to be in the format returned by FTP MDTM command.
        """
        # Parse the MDTM response, assuming it's in UTC
        # Example MDTM response: '213 20240426153000'
        # We remove the first 4 characters ('213 ') and parse the datetime
        dt_str = last_modified[4:]
        try:
            dt = datetime.strptime(dt_str, "%Y%m%d%H%M%S")
            dt = UTC.localize(dt)  # Make it timezone-aware as UTC
            self.last_modified = dt.astimezone(LOCAL_TIMEZONE)  # Convert to local timezone
        except ValueError as e:
            logging.error(f"Error parsing date '{dt_str}': {e}")
            self.last_modified = None  # Handle invalid date format

        self.name = name
        self.path = path

    def __str__(self):
        return f"Name: {self.name}, Path: {self.path}, Last Modified: {self.last_modified}"

    def is_newer_than(self, other: "ArkFile"):
        if self.last_modified and other.last_modified:
            return self.last_modified > other.last_modified
        return False  # Handle cases where last_modified might be None


class ArkMaps:
    ISLAND = {"folder": "TheIsland"}
    ABERRATION = {"folder": "Aberration"}

class INI:
        ENGINE= "Engine.ini"
        GAME_USER_SETTINGS= "GameUserSettings.ini"
        GAME= "Game.ini"

class ArkFtpClient:
    def __init__(self, host, port, user, password):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.ftp = ftplib.FTP()
        self.ftp.connect(host, port, timeout=10)
        self.ftp.login(user, password)
        self.map = None
        self.connected = True

    @staticmethod
    def from_config(config, map=None):
        with open(config, 'r') as config_file:
            config = json.load(config_file)

        print(f"Logging in with {config['user']}:{config['password']} on {config['host']}:{config['port']}")

        ftp_client = ArkFtpClient(config['host'], config['port'], config['user'], config['password'])
        
        if map is not None:
            ftp_client.set_map(map)

        return ftp_client

    def download_file(self, remote_file, local_file):
        with open(local_file, 'wb') as f:
            self.ftp.retrbinary('RETR ' + remote_file, f.write)

    def upload_file(self, local_file, remote_file):
        with open(local_file, 'rb') as f:
            self.ftp.storbinary('STOR ' + remote_file, f)

    def get_file_contents(self, remote_file) -> bytes:
        contents = bytearray()
        self.ftp.retrbinary('RETR ' + remote_file, contents.extend)
        return bytes(contents)
    
    def write_file_contents(self, remote_file, contents: bytes):
        with BytesIO(contents) as f:
            self.ftp.storbinary('STOR ' + remote_file, f)
    
    def connect(self):
        if not self.connected:
            self.ftp.connect(self.host, self.port)
            self.ftp.login(self.user, self.password)
            self.connected = True

    def __del__(self):
        self.close()

    def close(self):
        if self.connected:
            self.ftp.quit()
            self.connected = False

    def set_map(self, map: dict):
        self.map = map

    def _check_map(self, map: dict):
        if map is None and self.map is None:
            raise ValueError("Map is not set. Please set the map using set_map() method.")
        elif map is None:
            return self.map
        else:
            return map

    def nav_to_save_files(self, map: dict):
        self.ftp.cwd("/")

        for location in SAVE_FILES_LOCATION:
            self.ftp.cwd(location)

        self.ftp.cwd(map["folder"] + SAVE_FOLDER_EXTENSION) 

    def __nav_to_ini_files(self):
        self.ftp.cwd("/")

        for location in INI_FOLDER_LOCATION:
            self.ftp.cwd(location)

    def list_ftp_files_recursive(self, indent: int = 0):
        try:
            # Retrieve directory listing using LIST
            items = []
            self.ftp.retrlines('LIST', items.append)

            for item in items:
                # Parsing the LIST response
                parts = item.split(maxsplit=8)
                if len(parts) < 9:
                    logging.warning(f"Unrecognized LIST format: {item}")
                    continue  # Not a standard LIST format

                name = parts[8]

                # Determine if it's a directory based on the first character
                if item.startswith('d'):
                    print('    ' * indent + f"[DIR]  {name}/")

                    try:
                        # Attempt to change into the directory
                        self.ftp.cwd(name)
                        
                        # Recursively list the contents of the directory
                        self.list_ftp_files_recursive(indent + 1)
                        
                        # Change back to the parent directory after traversal
                        self.ftp.cwd('..')
                    except ftplib.error_perm as e:
                        error_message = f"Error accessing {name}: {e}"
                        print('    ' * indent + f"    {error_message}")
                else:
                    print('    ' * indent + f"       {name}")

        except ftplib.error_perm as e:
            error_message = f"Permission error: {e}"
            print('    ' * indent + f"    {error_message}")
        except Exception as e:
            error_message = f"Unexpected error: {e}"
            print('    ' * indent + f"    {error_message}")

    def list_all_profile_files(self, map: dict = None):
        map = self._check_map(map)
        self.nav_to_save_files(map)
        files = self.ftp.nlst()
        profile_files = [file for file in files if file.endswith(PROFILE_FILE_EXTENSION)]
        profile_files = [ArkFile(file, self.ftp.pwd(), self.ftp.sendcmd(f"MDTM {file}")) for file in profile_files]
        # print(f"Profile files for {map['folder']}: {profile_files}")

        return profile_files
    
    def list_all_tribe_files(self, map: dict = None):
        map = self._check_map(map)
        self.nav_to_save_files(map)
        files = self.ftp.nlst()
        tribe_files = [file for file in files if file.endswith(TRIBE_FILE_EXTENSION)]
        tribe_files = [ArkFile(file, self.ftp.pwd(), self.ftp.sendcmd(f"MDTM {file}")) for file in tribe_files]
        # print(f"Tribe files for {map['folder']}: {tribe_files}")

        return tribe_files
    
    def check_save_file(self, map: dict = None):
        map = self._check_map(map)
        self.nav_to_save_files(map)
        files = self.ftp.nlst()
        save_files = [file for file in files if file.endswith(SAVE_FILE_EXTENSION)]
        save_files = [ArkFile(file, self.ftp.pwd(), self.ftp.sendcmd(f"MDTM {file}")) for file in save_files]
        # print(f"Save files for {map['folder']}: {save_files}")
        return save_files
    
    def download_tribe_file(self, file_name, output_directory=None, map: dict = None) -> Path:
        self.nav_to_save_files(self._check_map(map))
        
        if output_directory is None:
            return self.get_file_contents(file_name)
        else:
            local_file = output_directory / file_name
            self.download_file(file_name, local_file)
            return local_file
    
    def download_profile_file(self, file_name, output_directory=None, map: dict = None) -> Path:
        self.nav_to_save_files(self._check_map(map))

        if output_directory is None:
            return self.get_file_contents(file_name)
        else:
            local_file = output_directory / file_name
            self.download_file(file_name, local_file)
            return local_file

    def download_save_file(self, file_name, output_directory=None, map: dict = None):
        self.nav_to_save_files(self._check_map(map))

        if output_directory is None:
            return self.get_file_contents(file_name)
        else:
            local_file = output_directory / file_name
            self.download_file(file_name, local_file)
            return local_file
    
    def change_ini_setting(self, setting: str, value: str, file_name: INI):
        self.__nav_to_ini_files()
        contents = self.get_file_contents(file_name).decode('utf-8')
        new_content = ""
        for line in contents.split('\n'):
            if not "ManagedKeys=" in line and setting in line:
                line = f"{setting}={value}"

            new_content += f"{line}\n"

        self.write_file_contents(file_name, new_content.encode('utf-8'))
    