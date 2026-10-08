from olt.zte import get_uncfg_onu
from olt.parser import parse_uncfg

output = get_uncfg_onu()

data = parse_uncfg(output)

print(data)
