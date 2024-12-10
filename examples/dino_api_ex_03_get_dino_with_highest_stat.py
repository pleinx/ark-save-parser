from pathlib import Path

from arkparse.ftp.ark_ftp_client import ArkFtpClient, FtpArkMap
from arkparse.api.dino_api import DinoApi
from arkparse.enums import ArkMap
from arkparse.objects.saves.asa_save import AsaSave

save_path = Path.cwd() / "Aberration_WP.ark"                                                                    # replace with path to your save file
save_path = ArkFtpClient.from_config('../ftp_config.json', FtpArkMap.ABERRATION).download_save_file(Path.cwd()) # or download the save file from an FTP server
save = AsaSave(save_path)                                                                                       # load the save file
dino_api = DinoApi(save)                                                                                        # create a DinoApi object

dino, value, stat = dino_api.get_best_dino_for_stat()                                                           # get the dino with the highest stat

print(f"The dino with the highest {stat} is {dino.get_short_name()} with {value} points")   # print the dino with the highest stat
print(f"Location: {dino.location.as_map_coords(ArkMap.ABERRATION)}")                        # print the location of the dino
print(f"Level: {dino.stats.current_level}")                                                 # print the level of the dino
