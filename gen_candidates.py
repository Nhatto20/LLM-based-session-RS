import random
import json
import re
import os
import time

current_path = os.path.dirname(os.path.realpath(__file__))
random.seed(42)


def candidate_expanse(candidates:list,allCandidates:dict,numCandidate = 100):
    n_items = len(candidates)
    len_expanse = numCandidate - n_items
    clone = allCandidates.copy()
    keys = list(clone.keys())
    
    while len_expanse > 0:
        key = str(random.choice(keys))
       
        item = clone[key]
        candidates.append(item)
        clone.pop(key)
        len_expanse -= 1

        keys = list(clone.keys())

    return candidates

def shuffle_items(items):
    random.shuffle(items)
    return items

def get_candidate(data):
    return get_info(data,candidate=True)

def get_target(data):
    return {"target": data["target"],"target_index": data["target_index"]}

def get_session(data):
    return get_info(data,candidate=False)
    

def get_info(data,candidate=True):
    pattern1 = r'Current session interactions: \[(.*?)\]'
    if candidate:
        pattern1 = r'Candidate set: \[(.*)\]'

    pattern2 = r'"(.*?)"'
    
    candidate = re.findall(pattern1,data["input"],re.DOTALL)
    candidates = re.findall(pattern2,candidate[0])
    return candidates


def get_data(path):
    with open(path,'r') as json_file:
        data = json.load(json_file)
    return data

def list_to_dict(list):
    dic = dict()
    n_items = len(list)
    vec = [i for i in range(n_items)]
    for i in vec:
        dic[f"{i}"] = list[i]
    return dic

def get_all_candidates(data,save=False,fileName = "allCandidates"):

    candidates = []
    seen = set()
    for d in data:
        items = get_candidate(d)
        for item in items:
            if item not in seen:
                seen.add(item)
                candidates.append(item)
            
    candidates = list_to_dict(candidates)
    #candidates = list(candidates)
    
    if save:
        output_directory = f"{current_path}/allCandidate"
        os.makedirs(output_directory, exist_ok=True)

        with open(f"{output_directory}/{fileName}", "w") as json_file:
            json_object = json.dumps(candidates, indent=2)
            json_file.write(json_object)
    
    return candidates


def search(strings,this):
    len_strings = len(strings)
    for i in range(len_strings):
        if strings[i] == this:
            return i
        


def packaging(data):
    count = 1
    string = "["
    for d in data:
        line = f'{count}.\"{d}\", '
        string = string + line
        count+=1
    string = string[:-2] + "]\n"
    return string

def combine(session,candidates):
    session = packaging(session)
    candidates = packaging(candidates)
    string = "Current session interactions: " + session + "Candidate set: " + candidates[:-1]
    #print(string)
    return string

def expand_dataCandidate(path,save = True,fileName=None,expand_resource = None):
    #path = path.replace("\\","/")

    data = get_data(path)
    if not fileName:
        fileName = path.split("\\")[-1]
    
    allCandidates = None
    if expand_resource:
        with open(expand_resource,'r') as file:
            allCandidates = json.load(file)
    else:
        allCandidates = get_all_candidates(data,save=True,fileName=fileName)

    
    new_data = []   
    for d in data:
        candidates = get_candidate(d)
        session = get_session(d)
        target = get_target(d)

        expanded = candidate_expanse(candidates,allCandidates)
        
        shuffle_items(expanded)
        
        index = search(expanded,target["target"])
        target["target_index"] = index

        _input_ = combine(session,candidates)
        target["input"] = _input_
        new_data.append(target)
    if save:
        output_directory = f"{current_path}/expanded"
        os.makedirs(output_directory, exist_ok=True)

        with open(f"{output_directory}/{fileName}", 'w') as json_file:
            json_object = json.dumps(new_data, indent=2)
            json_file.write(json_object)
