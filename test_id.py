from olt.zte import get_olt_config
from olt.find_onu_id import find_free_onu_id

cfg = get_olt_config("1/1/4")

print(cfg)

print(
    "ONU ID =",
    find_free_onu_id(cfg)
)
