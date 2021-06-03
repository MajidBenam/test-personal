# Support functions for 3store schema and DB definition
import copy
import pickle
import pprint
import os

variable_type_info_filename = 'seshat_types.pkl'
def display_variable_info(variable_info,type_info):
    print('Variable info:')
    pprint.pprint(variable_info,indent=4)
    print('Type info:')
    pprint.pprint(type_info,indent=4)
    
def save_schema_info(schema_info_tuple):
    # save it and test reload it
    try:
        fh = open(variable_type_info_filename,'wb')
        pickle.dump(schema_info_tuple,fh)
        fh.close()
    except:
        print(f"Unable to save data to {variable_type_info_filename}!")
        return False
    return True

def load_schema_info():
    try:
        fh = open(variable_type_info_filename,'rb')
        variable_type_info = pickle.load(fh,encoding="latin1")
        fh.close()
        return variable_type_info
    except:
        print(f"Unable to load {variable_type_info_filename}!")
        return None

# This must be used by both the schema defn and insertion code
# so they are in sync
raw_type_map = {
    # comment out these lines if we get a version of TDB that casts properly
    'xsd:gYear': 'xsd:integer', # xsd:integer
    'xdd:gYearRange': 'xdd:integerRange', # xdd:integerRange
    # comment out these lines if we get a version of generate_choice_list() that works and we fix the definition of enumerations 
    'scm:EpistemicState': 'xsd:string', # enumerations are not supported yet
    'scm:Confidence': 'xsd:string', # enumerations are not supported yet
    }
def ensure_raw_type(raw_type):
    # return getattr(raw_type_map,raw_type,raw_type) # why does this fail?
    try:
        raw_type = raw_type_map[raw_type]
    except KeyError:
        pass
    return raw_type

def pretty_year(year):
    if type(year) is str :
        if year == '':
            return year
        year = int(year)
    return '%d%s' % (abs(year), 'BCE' if year < 0 else 'CE')

# this function always returns a string but properly formatted for the cast()
def precast_values(value,value_type,source):
    if value_type == 'xsd:string':
        # per http://www.datypic.com/sc/xsd/t-xsd_string.html
        # must do this in proper order! since &amp; uses &!
        value = value.replace('&','&amp;') # do this first!
        value = value.replace('<','&lt;')

    if value_type == 'xsd:gYear':
        # Per Kevin 3/2021: Doesn't work.  But even if it did it does not handle CE/AD/BCE etc.
        # Convert CE/BCE/AD/BC to +/- and expand to CCYY
        # per http://www.datypic.com/sc/xsd/t-xsd_gYear.html
        date = value.strip() # eliminate leading and trailing whitespace
        date = date.upper() # canonically BCE or CEo
        date = date.replace(' ','') # no spaces
        bce = date.find('B')
        if bce >= 0:
            # assume XXXBCE
            # the form '-1234' is derived from '1234BCE'
            try:
                date = '-%04d' % int(date[0:bce])
            except ValueError:
                print(f"WARNING: Unable to pre-cast '{value}' from {source} to gYear; assuming 0CE")
                date = '0000'
        else:
            ce_ad = date.find('A')
            if ce_ad == -1:    # no 'A' found
                ce_ad = date.find('C')
                if ce_ad == -1:   # no 'C' found
                    ce_ad = len(date)+1   # to be used in the next try: block
            try:
                date = '%04d' % int(date[0:ce_ad])
            except ValueError:
                print(f"WARNING: Unable to pre-cast '{value}' from {source} to gYear; assuming 0CE")
                date = '0000'
        return date

    if value_type == 'xdd:gYearRange':
        parts = value.split('-') # Assume we never get -400 - 300BCE but rather 400BCE-300BCE
        if len(parts) == 2:
            ys = precast_values(parts[0],'xsd:gYear',source)
            ye = precast_values(parts[1],'xsd:gYear',source)
            if ye[0] == '-' and ys[0] != '-': # deal with 400-300BCE which really means 400BCE-300BCE
                ys = '-' + ys
            return '[' + ys + ',' + ye + ']'
        else:
            return precast_values(value,'xsd:gYear',source)

    if value_type in ['xdd:integerRange','xdd:decimalRange']:

        subtype = {'xdd:integerRange': 'xsd:integer',
                   'xdd:decimalRange': 'xsd:decimal'}[value_type]
        value = value.strip()
        # population or territory sometimes is '60000:80000' (clearly w/o a date!)   or '60000-80000' 
        parts = value.split(':') # local Seshat convention to separate a range of positive numbers (see insert_from_csv)
        if len(parts) == 2:
            print(f"WARNING: Pre-casting '{value}' from {source} to a range: likely ill-formed!")
            return '[' + precast_values(parts[0],subtype,source) + ',' + precast_values(parts[1],subtype,source) + ']'
        if value[0] == '-': # a negative number?  could be -100-300 but how to parse that?
            return precast_values(value,subtype,source) # treat as singleton negative number
        parts = value.split('-') # local Seshat convention to separate a range of positive numbers (see insert_from_csv)
        if len(parts) == 2:
            return '[' + precast_values(parts[0],subtype,source) + ',' + precast_values(parts[1],subtype,source) + ']'
        return precast_values(value,subtype,source) # single positive number

    if value_type == 'xsd:integer':
        # Quite often you'll get absent/present/suspected unknown rather than 0 for long walls
        try:
            int(value)
        except ValueError:
            print(f"WARNING: Unable to pre-cast '{value}' from {source} to integer; assuming 0")
            value = '0'

    if value_type == 'xsd:decimal':
        try:
            float(value)
        except ValueError:
            print(f"WARNING: Unable to pre-cast '{value}' from {source} to decimal; assuming 0.0")
            value = '0.0'

    # if no explicit conversion, just return value...
    return value

# God what a hack...need a persisstent id with the db so new scoped instances are unique

# unique() is like idgen but for each unique set of prefix and keys to appends a unique tag
# however it does NOT generate a new one for the same prefix and keys

# Eventually we have a DB class with property 'version' (a decimal) and 'unique_id' (an integer) cardinality of 1
# TODO when inserting a row, fetch the unique id (from results into python), update locally, then reassert to db when adding the row
# triple('v:DB','unique_id','v:unique'); unique_id_old = results['bindings']['unique']; unique_id = unique_id_old
# update as needed, then unique_id += 1; idgen(prefix,[keys,unique_id],variable)
# if unique_id is not unique_id_old:
# eq('v:u_new',unique_id), delete_triple('v:DB','unique_id','v:unique'), add_triple('v:DB','unique_id','v:u_new') 
unique_id_counter = 0;
def increment_unique_id():
    global unique_id_counter
    unique_id_counter += 1
    return unique_id_counter

def unique_id(q,prefix,keys,variable):
    keys = copy.copy(keys)
    keys.append(increment_unique_id())
    if q is None:
        q = WOQLQuery()
    return q.idgen(prefix,keys,variable) # NOTE this extends given q by side effect

# Attempt to fix buggy version of code from woql_query.py
def fixed_generate_choice_list(
    cls=None,
    clslabel=None,
    clsdesc=None,
    choices=None,
    graph=None,
    parent=None,
    ):
    if not graph:
        graph = WOQLQuery()._graph
    clist = []
    if False:
        # ensure that _: is part of the current @context per Kevin/Gavin
        # some deep OWL or rdf thing
        # without it you get an API error, e.g.: api:message":"Error: key_has_unknown_prefix(\"_:Confidence\")
        # This code fails...it needs to be done such that each time the WOQLQuery() constructor is called
        # the _: prefix is available wherever it needs to be...
        # this might work if we cache qu = WOQLQuery() and then replace all the WOQLQuery() calls here with qu
        try:
            ctxt = WOQLQuery()._cursor['@context'] # access current context
        except KeyError:
            # missing
            ctxt = {}
            WOQLQuery()._context(ctxt) # update cursor context
        ctxt['_'] = '_' # ensure _: is available
        
    if ":" not in cls:
        listid = "_:" + cls
    else:
        listid = "_:" + cls.split(":")[1]
    lastid = listid
    wq = WOQLQuery().add_class(cls, graph).label(clslabel)
    if clsdesc:
        wq.description(clsdesc)
    if parent:
        wq.parent(parent)
    confs = [wq]
    for i in range(len(choices)): #  JSB range(len(choices)) rather than choices
        if not choices[i]:
            continue
        if type(choices[i]) is list:
            chid = choices[i][0]
            clab = choices[i][1]
            desc = choices[i][2] if len(choices[i]) >= 3 else False
        else:
            chid = choices[i]
            clab = utils.label_from_url(chid)
            desc = False
        cq = WOQLQuery().insert(chid, cls, graph).label(clab)
        if desc:
            cq.description(desc)
        confs.append(cq)
        if i < len(choices) - 1:
            nextid = listid + "_" + str(i) # JSB str()
        else:
            nextid = "rdf:nil"
        clist.append(WOQLQuery().add_quad(lastid, "rdf:first", chid, graph))
        clist.append(WOQLQuery().add_quad(lastid, "rdf:rest", nextid, graph))
        lastid = nextid
    oneof = WOQLQuery().woql_and(
        WOQLQuery().add_quad(cls, "owl:oneOf", listid, graph), *clist)
    return WOQLQuery().woql_and(*confs, oneof)
