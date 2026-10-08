from olt.zte import get_uncfg_onu
from olt.parser import parse_uncfg

output = get_uncfg_onu()

print(output)

print(parse_uncfg(output))
