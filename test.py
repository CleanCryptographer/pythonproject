# from utils import one_way, get_round_trip
import json
import utils


if __name__ == '__main__':
    print(json.dumps(utils.one_way('KHI', 'ISB', '28-07-2022'), indent=2))
    # r = utils.get_round_trip('LHE', 'DXB', '02-08-2022', '03-08-2022')
    # params_round_trip = {'SS': '', 'RT': '', 'FL': 'on', 'TT': 'RT', 'DC': 'LHE', 'AC': 'DXB', 'AM': '2022-08', 'AD': '02', 'RM': '2022-08', 'RD': '03', 'PA': '1', 'PC': '', 'PI': '', 'CC': '', 'CR': '', 'NS': 'true', 'PX': '', 'CD': ''}
    # res = utils.get_api_response(utils.url, params_round_trip)

    # d1 = json.loads(open("./samples/LHEtoDXBAirBlue.json").read())
    # d2 = json.loads(open("./samples/LHEtoDXBCRT.json").read())
    # with open('./samples/1.json', 'w') as fp:
    #     fp.write(json.dumps(utils.airblue_to_crt(d1), indent=2))