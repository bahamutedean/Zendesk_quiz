import os
from os import path
import json


def fetch_files():
    '''
    fetch the current directory and return all 3 json files full path for further operation
    :return:  a list of json files' full path
    '''
    # fetch the current working path -- compatible for all OS
    current_path = os.getcwd()

    lists=os.listdir(current_path)
    # find out all the json files based on its extension.
    # This is a way to be extensible when more json are required for operation
    json_file_lists=[]

    for each in lists:

        full_path = current_path+'/'+each

        if path.splitext(full_path)[1]=='.json':

            json_file_lists.append(full_path)

    return json_file_lists


def show_terms():
    '''
    This function is to give users a hint about the terms that appear in the files
    :return: No actual return here
    '''
    #load the global variable
    global file_list
    # convert all the keys in the dictionary into a list in a loop
    for json_file in file_list:
        #using with clause could reduce the risk of breaking the files
        with open(json_file,'r') as f:
            # call josn module to extract json and convert it into a dictionary
            content = json.load(f)
        # return the actual file name without extension
        file_category=json_file.split('/')[-1][:-5]
        # a temp list
        keys=[]
        # to build a list of all the keys that exist in the dataset
        for each in content:
            # use dictionary build-in method to enumerate all elements
            for key,value in each.items():
                # avoid duplication key appending
                # another option is to use set, but this uses hash sort which can break the order of terms
                if key not in keys:
                    keys.append(key)
        #print out all the keys in the specific dataset
        print('*'*40)
        print('Search',file_category.upper(),'with terms below:')
        for terms in keys:
            print(terms)
        # release memory since no idea about the actual size of file
        del keys,content



def convert_dict(inputs):
    '''
    This function is to transform the list into a one-to-many relational dictionary
    :param inputs: a list that includes requiered entry
    :return: a one-to-many relational dictionary for searching convenience
    '''
    #build an empty dictionary
    return_dict = {}
    for each in inputs:
        # if the id is not in the dictionary key_lists, create that key
        if each[0] not in return_dict.keys():
            return_dict[each[0]]=each[1]
        # otherwise, using extend function to put other entry with same id into its value field
        else:
            return_dict[each[0]].extend(each[1])

    return  return_dict



def build_relation(type,result_set):
    # to put relation to organization file search
    if type == 'organizations':
        # make sure the files exist in the relative path
        with open('users.json', 'r') as f:
            users = json.load(f)
        with open('tickets.json', 'r') as f:
            tickets = json.load(f)
        # duplicates
        # apparently org_id is the parent of user_id, so there will be one-to-many relationship
        user_in_org = [[each.get('organization_id'), [each.get('name')]] for each in users]
        # duplicates
        # apparently org_id is the upper level of tickets, so there will be one-to-many relationship
        tic_in_org = [[each.get('organization_id'), [each.get('subject')]] for each in tickets]
        # use a function to convert that relation into a dictionary for searching convenience
        user_in_org=convert_dict(user_in_org)
        tic_in_org = convert_dict(tic_in_org)
        # an empty list, which will hold element in dictionary data type
        return_set=[]
        for each in result_set:
            #using try is a way to avoid errors when executing each['_id'].
            #because (each is a dict), when '_id' doesn't exist, each['_id'] will raise error while each.get('_id') will return a NULL value
            try:
                # to show the users in this organization
                each['RELATION -- users in this org']=user_in_org.get(each['_id'])
            except:
                pass
            try:
                # to show the tickets belong to this organization
                each['RELATION -- tickets in this org']=tic_in_org.get(each['_id'])
            except:
                pass
            return_set.append(each)


    # to put relation to users file search
    # same logic as above
    elif type == 'users':
        with open('organizations.json', 'r') as f:
            orgnizations = json.load(f)
        with open('tickets.json', 'r') as f:
            tickets = json.load(f)
        # unique
        org_name = [[each.get('_id'), each.get('name')] for each in orgnizations]
        # duplicates
        ticket_submitted = [[each.get('submitter_id'), [each.get('subject')]] for each in tickets]
        ticket_assignee = [[each.get('assignee_id'), [each.get('subject')]] for each in tickets]
        ticket_submitted=convert_dict(ticket_submitted)
        ticket_assignee=convert_dict(ticket_assignee)
        org_name=dict(org_name)

        return_set = []
        for each in result_set:
            try:
                # converting the org_id into org_name, a way to build the relation
                each['RELATION -- org name'] = org_name.get(each['organization_id'])
            except:
                pass
            try:
                # to show the tickets created by this user in this organization
                each['RELATION -- tickets raised by this user'] = ticket_submitted.get(each['_id'])
            except:
                pass
            try:
                # to show the tickets assigned by this user in this organization
                each['RELATION -- tickets assigned by this user'] = ticket_assignee.get(each['_id'])
            except:
                pass
            return_set.append(each)


    # type=='tickets'
    # to put relation to tickets file search
    # same logic as above

    else:
        with open('users.json', 'r') as f:
            users = json.load(f)
        with open('organizations.json', 'r') as f:
            orgnizations = json.load(f)
        # unique
        user_name = [(each.get('_id'), each.get('name')) for each in users]
        # unique
        org_name = [(each.get('_id'), each.get('name')) for each in orgnizations]
        user_name=dict(user_name)
        org_name=dict(org_name)
        return_set = []
        for each in result_set:
            try:
                #converting submitter_id into his name
                each['RELATION -- submitter name'] = user_name.get(each['submitter_id'])
            except:
                pass
            try:
                #converting assignee_id into his name
                each['RELATION -- assignee name'] = user_name.get(each['assignee_id'])
            except:
                pass
            try:
                #converting org_id into org_name
                each['RELATION -- org name'] = org_name.get(each['organization_id'])
            except:
                pass
            return_set.append(each)
    #release memory
    del result_set
    return return_set


def search_record(*input):
    '''

    :param input: accept key,value to search. the third input is the index of file in the global variable
    :return: a list of matchable record. If no result, it will return an empty list
    '''
    # load the global variable
    global file_list
    key_input = input[0]
    value_input = input[1]
    file_index=input[2]

    with open(file_list[file_index], 'r') as f:
        # call josn module to extract json and convert it into a dictionary
        content = json.load(f)
    # to fetch the name of the file that is under searching
    file_category = file_list[file_index].split('/')[-1][:-5]
    # generate a list that holds the possible matched records
    result_set=[]
    # to generate a list of all keys
    key_list = []
    for each in content:

        key_list.extend(each.keys())
    # remove duplicate
    key_list = set(key_list)
    # convert keys into str format
    key_list = [str(each) for each in key_list]

    # enumerate the file, where index will be used to locate the entry
    '''
    # NOTE: loop inside loop looks a little complicated, but since there are only limited keys, embedding another loop will not cause exponential
    # increase in time and space complexity when searching larger files
    '''
    '''
    Another way to do this is to use zip function to convert the value with same keys into a list
    However, not all the records have same number of keys, so this method cannot be used under this circumstance
    '''



    for index,each in enumerate(content):
        # if the key_input is in the list but not exists in that record and also the value entry from input is empty, return that record
        if (key_input in key_list) and (key_input not in each.keys()) and value_input.strip().__len__()==0:
            result_set.append(content[index])
        else:
            for key,value in each.items():
                # convert the key into string to minimize unmatchable situation caused by different data types
                # This is a full match. by using 'key_input' in 'key' could make this a fussy match
                if str(key)==key_input:
                    # same option, this might be a little tricky when searching something based on timestamp
                    # This is a full match. by using 'value_input' in 'get(key)' could make this a fussy match

                    # using each.get(key) is to avoid possible errors when the key doesn't exist
                    if str(each.get(key))==value_input:
                        # append matchable record in this list, which will be a return value
                        result_set.append(content[index])
    # leave this here for debug
    #print(result_set.__len__(),' results returned')
    # release memory in case of huge size file running out of memory
    del content
    if result_set.__len__()!=0:
        result_set=build_relation(file_category,result_set)
    return result_set




def feedback(file_index):
    '''
    :param file_index: a manual input that labels the index of the file selected
    :return: No return value
    '''
    # load global varialbe
    global file_list
    # get the exact name of the file without extension.
    file_category = file_list[file_index].split('/')[-1][:-5]
    # convert input into string for further comparison
    print('please input the key you want to search:')
    # as an improvement, can use strip() to remove leading and tailing whitespaces caused by typo
    key = str(input())
    print('please input the value you are searching:')
    # as an improvement, can use strip() to remove leading and tailing whitespaces caused by typo
    value = str(input())
    # call the function above
    result = search_record(key, value,file_index)
    print('Searching', file_category,'for', key, 'with the value equal', value, '\n')
    # Error control:if the return value has nothing, then give a notification
    if result.__len__() == 0:

        print('No result found\n')
    else:
        # it is possible someone searches information using unusually key, so here is to return all the matchable records
        print(result.__len__(), 'result(s) returned:\n')
        print('-+-+-+-+' * 20)

        for each in result:
            for k, v in each.items():
                print(k, ':-------->', v)
            print('-+-+-+-+' * 20)

if __name__=='__main__':
    # call this function before the job in case new files are put, which may break the file index.
    # file_list is a list, which will be used as a global variable across the script.
    file_list = fetch_files()
    # in if clause, the script checks if all three files are all in the current directory, otherwise it will raise an error to abort the mission
    if file_list.__len__() < 3:
        print('Insufficient files for the quiz, please check the current working directory\n')
        raise FileExistsError

    # welcome interface
    print('Welcome to search interface')
    print(' '*20,'Select search option')
    print(' '*20,'* press 1 to Search zendesk')
    print(' '*20,'* press 2 to show all the fields available')
    print(' '*20,'* press \'quit\' to quit')
    # convert the input into a string
    initial_input = str(input())

    # Error control in case of unexpected input
    while initial_input not in ['1','2','quit']:
        print('Invalid option, please retry')

        initial_input=str(input())

    # call the functions based on different input
    if initial_input == '2':
        show_terms()
    elif initial_input == '1':

        print('Here are the search options:')
        for i, each in enumerate(file_list):
            # because python starts with 0, 'i+1' could be a more human readable method for Non-tech users
            print(i + 1,')', each.split('/')[-1][:-5], end=' ')
        print('Please choose a category to search')
        second_input = str(input())
        # Error control, to check if the input is within the range
        while second_input not in ['1','2','3','quit']:
            print('Invalid entry, please retry')
            second_input = str(input())
        if second_input=='quit':
            print('see you next time\n')
            exit()
        else:
            # convert the input back to a computer language
            second_input = int(second_input) - 1
            print('you have chosen:',file_list[second_input].split('/')[-1][:-5])
            # call the function to give feedback about the searching result
            feedback(second_input)

    else:
        print('see you next time\n')
        exit()





































