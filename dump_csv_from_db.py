import terminusdb_client as woql
from terminusdb_client import WOQLQuery
import pprint
import time
import pickle
import os
from utils_3store import *
pp = pprint.PrettyPrinter(indent=4) # for debugger

# updated below
variable_info = {}
type_info = {}
schema_declarations = []
property_name_info = {} # remap variable info: property_name -> (variable_name,scoped,type)
client = None
csv_file = None # handle to the open csv file we are creating

def dump_variables(polid,polity_name):
    global variable_info,type_info,client,csv_file
    ignore_pv = ['@context', '@type', 'rdfs:label', 'scm:original_PolID']
    value_options = ["scm:String","scm:DecimalRange","scm:IntegerRange","scm:EpistemicState","scm:GYearRange"]
    
    start_time = time.time()
    def dump_line(var_name,actual_value='',Years_value='',Confidence_value='simple', Disputed_value='', Unknown_value=''):
        # Note that var_name could have embedded |
        csv_file.write(f"NGA|{polity_name}|{var_name}|{actual_value}|{Years_value}|{Confidence_value}|{Disputed_value}|{Unknown_value}\n")

    # do a read_object to get all the data at once
    results = WOQLQuery().read_object(polid,'v:o').execute(client)
    obj = results['bindings'][0]['o'] # bindings is a single list
    for pv,value in obj.items():
        if pv in ignore_pv or pv == '@id':
            continue
        pv_stripped = pv.split(':')[1] # lose scm: prefix
        try:
            var_name, scoped, property_type = property_name_info[pv_stripped]
        except KeyError:
            # complain about missing pv data
            continue

        if scoped:
            if type(value) is dict:
                value = [value] # make iterable
            for value_dict in value:
                actual_value =''
                Years_value = ''
                Confidence_value = ''
                Disputed_value = ''
                Unknown_value = ''

                for sp,sv in value_dict.items():
                    if sp in ignore_pv:
                        continue
                    if sp == '@id':
                        doc_name = sv.split(':')[1]
                        correct_doc_name ='terminusdb:///data/' + doc_name
                        results_2 = WOQLQuery().read_object(correct_doc_name, 'v:oo').execute(client)
                        obj_2 = results_2['bindings'][0]['oo'] # bindings is a single list
                        for pv_2, value_2 in obj_2.items():
                            if pv_2 in value_options:
                                actual_value = value_2['@value']
                            if pv_2 == 'scm:confidence_tags':
                                if type(value_2) == dict:
                                    Confidence_value = value_2['scm:Confidence']['@value']
                                else: # type is list
                                    # confidence_value = value_2['scm:Confidence']['@value']
                                    # Confidence_value = 'inferreddisputedsuspected'
                                    print('Possible conflict in confidence tags')
                            if pv_2 == 'scm:Years':
                                Years_value = value_2['@value']
                            if pv_2 == 'scm:Disputed':
                                Disputed_value = True # or value_2['@value']
                            if pv_2 == 'scm:Unknown':
                                Unknown_value = True # or value_2['@value']
                dump_line(var_name,actual_value,Years_value,Confidence_value,Disputed_value,Unknown_value)
        else:
            # already have the values
            actual_value = value['@value']
            dump_line(var_name,actual_value)

    print('Time for %s: %.1fs' % (polity_name,time.time() - start_time))


if __name__ == "__main__":
    # global client
    start_time = time.time()
    db_id = "test_seshat_jim_majid" #  this gets its own scm: and doc: world
    client = woql.WOQLClient(server_url = "https://127.0.0.1:6363", insecure=True)
    client.connect(key="root", account="admin", user="admin")
    existing = client.get_database(db_id, client.account())
    if existing:
        client.set_db(db_id,client.account())
        schema_tuple = load_schema_info()
        if schema_tuple is None:
            sys.exit(0)

        schema_declarations, variable_info, type_info = schema_tuple
        # create inverted mapping
        for variable,entry in variable_info.items():
            property_name, scoped, property_type = entry
            property_name_info[property_name]  = (variable,scoped,property_type)
            
        csv_filename = 'seshat_test.csv';
        try:
            csv_file = open(csv_filename,"w")
        except IOError:
            print("ERROR: Could not open %s for writing." %  csv_filename)
            sys.exit(0)
        # probe for all polities
        csv_file.write("NGA|PolityName|Section|Subsection|Variable|ActualValue|Years|Confidence|Disputed|Unknown\n")

        results = WOQLQuery().triple('v:Polity_ID','original_PolID','v:PolityName').execute(client)
        for b in results['bindings']:
            polid = b['Polity_ID']
            polity_name = b['PolityName']['@value']
            #if polid == 'http://terminusdb.com/schema/woql#code book':
            #    continue
            dump_variables(polid,polity_name);
        csv_file.close()
    else:
        print(f"Database {db_id} does not exist!")
    print('Execution time: %.1fs' % (time.time() - start_time))
