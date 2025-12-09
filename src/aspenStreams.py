from aspen import Aspen, read_data, get_all_children, Fetcher, DEFAULT_SEARCH, HAP_RECORDTYPE
from pprint import pprint

def GetStreams(aspen: Aspen, data = None):
    '''
    Docstring for GetStreams
    
    :param aspen: Description
    :type aspen: Aspen
    :param data: Description
    '''
    if data == None:
        data = read_data(aspen)
        # pprint(data)
    
    blocks = data.keys()
    # for i in blocks:
    #     for j in range()
    for i in blocks:
        print(rf"{i}\Connections")
        streams = aspen.Application.Tree.FindNode(rf"{i}\Connections")
        print(streams)
    
    # return streams
    






if __name__ == "__main__":
    from aspen import init_aspen, run_aspen
    import sys
    import os.path as op
    print("start")
    if len(sys.argv) < 2:
        print("Should be called with the name of the aspen file")
        exit(1)
    
    
    aspen = init_aspen(op.abspath(sys.argv[1]))
    print("aspin initialized")
    
    # run_aspen(aspen=aspen)
    print("done\ngetting streams")
    
    GetStreams(aspen=aspen)