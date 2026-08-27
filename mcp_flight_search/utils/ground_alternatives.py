"""
Ground and High-Speed Rail Alternative Advisor
Recommends ground/rail alternatives for corridors where trains/buses are faster, cheaper, or more practical than multi-stop flights.
"""
from typing import Optional, Dict

GROUND_ALTERNATIVES: Dict[str, str] = {
    "HAN_KWL": "💡 陆路/高铁优选建议：河内 ➔ 桂林直飞较少，转机需14~17小时(约¥850~2000+)。更优方案为【陆路大巴过友谊关至南宁(约4~5h, ¥150~200)】+【南宁东高铁至桂林(2h, ¥108)】，全程约6~7小时，总花费仅约¥260~330($40左右)，省时又省钱。",
    "KWL_HAN": "💡 陆路/高铁优选建议：桂林 ➔ 南宁(高铁2h, ¥108) + 南宁 ➔ 河内(国际大巴/火车至友谊关过境4~5h, ¥150~200)，全程约6~7小时，远快于多段转机。",
    "HAN_NNG": "💡 陆路/火车直达建议：河内与南宁陆路紧邻，建议选择国际大巴(约4~5小时, ¥150~200)或中越国际联运列车(MR1/MR2 / T8702次)，无需转机。",
    "NNG_HAN": "💡 陆路/火车直达建议：南宁 ➔ 河内国际大巴或国际客运列车(T8701)，4~5小时直达友谊关/同登过境。",
    "HAN_KMG": "💡 陆路/高铁建议：河内 ➔ 老街/河口口岸(大巴/火车约4h) + 河口北 ➔ 昆明(动车约3.5h)，全程约8小时，花费约¥150~250。",
    "SZX_HKG": "💡 高铁/地铁直达：深圳至香港西九龙高铁仅14~18分钟(¥68~75)，或乘地铁经福田/罗湖口岸过关，无需航空出行。",
    "HKG_SZX": "💡 高铁/地铁直达：香港西九龙至深圳北/福田高铁仅14~18分钟。",
    "CAN_SZX": "💡 城际高铁直达：广州南/广州东至深圳北/福田高铁仅需30~45分钟(¥74.5~79.5)。",
    "SHA_HGH": "💡 高铁直达：上海虹桥至杭州东高铁车次极其密集，仅需45~60分钟(¥73)。",
    "TYO_OSA": "💡 新干线直达：东京至新大阪东海道新干线(Nozomi号)仅需2小时15分钟，省去两头去机场的时间。",
}

def get_ground_alternative(origin: str, destination: str) -> Optional[str]:
    key = f"{origin.upper()}_{destination.upper()}"
    return GROUND_ALTERNATIVES.get(key)
