import sys
import os

sys.path.append(
    os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )
)

from olt.change_pppoe import change_pppoe

change_pppoe(
    "1/1/6",
    "3",
    "popon@cyber.net",
    "popon123",
    "154"
)
