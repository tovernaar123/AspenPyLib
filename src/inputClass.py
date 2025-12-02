from .aspen import read_data, Aspen

def getinputClass(data:dict=None,Aspen:Aspen = None) -> dict:
    '''
    uses the dict or Aspen to generate an Dict for input in the TEA package
    If both are input then the data:dict will be prefferd

    
    :param data: Description
    :type data: dict
    :param Aspen: Description
    :type Aspen: Aspen
    :return: Description
    :rtype: dict
    '''
    if data == None and Aspen == None:
        Exception("eather data or Aspen should be an input")
    elif data != None:
        print("this should do things")
    elif Aspen != None:
        data = read_data(Aspen)
    
    placeholder = {}
    return placeholder


def makeCustonClass(input)->dict:
    placeholder = {}
    return placeholder