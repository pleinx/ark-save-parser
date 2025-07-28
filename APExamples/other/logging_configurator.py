from enum import Enum
from arkparse.logging import ArkSaveLogger

print("Welcome to the ArkSaveLogger configurator!")
print("This tool will help you configure the ArkSaveLogger settings for your project.")

print("When arkparse parses objects, you can stop parsing when an invalid object is encountered.")
print("Alternatively, you can allow invalid objects to be parsed, but they will be logged as errors.")
enable = input("\nWould you like to allow invalid objects? (y/n): ").strip().lower()
if enable == "y":
    ArkSaveLogger.allow_invalid_objects(True, True)
    print("Invalid objects will be allowed and logged as errors.")
else:
    ArkSaveLogger.allow_invalid_objects(False, True)
    print("Invalid objects will not be allowed and parsing will stop on the first invalid object.")

input("\nPress Enter to continue...")

print("\nYou can set enable logging at different levels for different resolution of detail.")
log_types: Enum = ArkSaveLogger.LogTypes
print("Available log types:")
for log_type in log_types.__members__.values():
    print(f" - {log_type.value}")

for log_type in log_types.__members__.values():
    enable = input(f"\nWould you like to enable {log_type.value} logging? (y/n): ").strip().lower()
    if enable == "y":
        ArkSaveLogger.set_log_level(ArkSaveLogger.LogTypes(log_type.value), True, True)
        print(f"{log_type.value} logging enabled.")
    else:
        ArkSaveLogger.set_log_level(ArkSaveLogger.LogTypes(log_type.value), False, True)
        print(f"{log_type.value} logging disabled.")

print("All done! Your ArkSaveLogger is now configured.")

