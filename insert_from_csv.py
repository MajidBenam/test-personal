import terminusdb_client as woql
from terminusdb_client import WOQLQuery
import pprint
import time
import pickle
import os
from utils_3store import *
pp = pprint.PrettyPrinter(indent=4) # for debugger

verbose_mode = False # CONTROL silence 'adds' but report commits
dump_results = False # CONTROL on successful commits; very noisy with batched queries
enumerations_enabled = False # CONTROL
# gYear_type = 'xsd:gYear'
gYear_type = 'xdd:gYearRange'
raw_gYear_type = ensure_raw_type(gYear_type)
Confidence_type = 'scm:Confidence'
raw_Confidence_type = ensure_raw_type(Confidence_type)

# updated below
variable_info = {}
type_info = {}
schema_declarations = []

client = None
flushed_values = {}
polity_query_name = None
polity_query = None
total_assertions = 0
total_inserts = 0
total_deletes = 0
total_commit_failures = 0

def execute_commit(qlist):
    global client, polity_query_name, polity_query
    global total_assertions,total_inserts,total_deletes,total_commit_failures
    msg = f"Committing data for {polity_query_name}"
    try:
        q = WOQLQuery().woql_and(*qlist)
        execute_start_time = time.time()
        result = q.execute(client,commit_msg=msg)
        # Makes no difference to timing: client.squash(msg) # per Kevin: flatten the 'journal'
        execute_elapsed_s = "%.2fs" % (time.time() - execute_start_time)
        total_assertions += 1
        if type(result) is dict :
            inserts = result['inserts']
            deletes = result['deletes']
            total_inserts += inserts
            total_deletes += deletes
            print(f"{msg} i:{inserts} d:{deletes} {execute_elapsed_s}")
        else:
            # Sometimes we get a <Response> object that is not subscriptable?
            # result.status_code is the HTTP status code, 200 is successful but we don't have bindings?
            print(f"{msg} {execute_elapsed_s}")
        if dump_results:
            pprint.pprint(result,indent=4)
    except Exception as exception: # API error or whatever
        execute_elapsed_s = "%.2fs" % (time.time() - execute_start_time)
        print(f"Execution ERROR while {msg} after {execute_elapsed_s} -- skipped")
        print(f"{exception.msg}")
        total_commit_failures += 1
    
def assert_seshat_row(Polity, Variable, Value_From, Value_To, Date_From, Date_To, Fact_Type, Value_Note):
    global client, flushed_values, polity_query_name, polity_query
    empty_value = '' # Could be None

    def unique_var(prefix):
        uid = increment_unique_id()
        return f"{prefix}_{uid}"
    # this if only takes care of:
    # 1) the name of the polity for which we are creating a collective query (polity_query_name) 
    # 2) the list of all the queries we need for this Polity (polity_query)
    # this -if- will be only true, the first time we are seeing a new Polity in our csv file:
    # the first time we set the polity_query_name to *Polity* and the list of polity_query to *[]*
    # for the rest of the lines for *Polity*, the name is already set and the list of queries is getting appended
    # so no need to enter this -if- unless we encounter a new polity in the csv. 
    if polity_query_name != Polity:      
        if polity_query is not None:     # this condition is False unless we are about to start a new Polity
            execute_commit(polity_query)
        # fallthrough
        polity_query_name = Polity       
        polity_query = []                # we add individual queries to this for a final collective query for Polity


    # sample *key: value* pairs in variable_info[Variable]:
    # **********NEEDS RECHECKING***********
    # VERSION 1:
    # key: Variable ---> 'General variables||Alternative names'
    # value: ('General_variables__Alternative_names', True, 'String')
    # key: Variable ---> 'General variables||Capital'
    # value: ('General_variables__Capital', True, 'String')
    #
    # VERSION 2:
    # key: Variable ---> 'General variables||Alternative names'
    # value: ('Alternative_names', True, 'String')
    # key: Variable ---> 'General variables||Capital'
    # value: ('Capital', True, 'String')
    #
    # We must have ALL the possible properties in variable_info to get ZERO exception errors here: 
    try:
        property_name, scoped, property_type = variable_info[Variable]
    except KeyError:
        print(f"WARNING: Unknown property: {Variable} - skipping")
        return None
    
    if scoped:
        property_Value = property_name + '_Value'
        # workaround
        doc_property_Value = 'terminusdb:///data/' + property_Value
        # doc_property_Value = 'doc:' + property_Value
        scm_property_Value = 'scm:' + property_Value
        
        # typical values for type_info[property_type]:
        # key: property_type ---> 'String'
        # value: ('scm:String', 'xsd:string')
        #
        # We need to have as much knowledge as we can about the types to get no exceptions:
        try:
            property_value_name, raw_type = type_info[property_type]
        except KeyError:
            print(f"WARNING: Unknown type {property_type} for {Variable} - skipping")
            return None
            
    else:                                # if unscoped; the only case: 'original_PolID'
        raw_type = property_type         # xsd:string for 'original_PolID'
    
    # no matter scoped or unscoped, ensure the raw type in case casting is not done properly
    # Ex: make sure that 'xsd:gYear' (which does NOT work properly yet) casts to 'xsd:integer'
    real_raw_type = ensure_raw_type(raw_type)
    
    # up to here, we have only decided on the *Polity* and the property that the csv line is referring to
    # we have given them names and types, etc

    # we use lower_Polity from now on...
    lower_Polity = Polity.lower()       # Make canonical;this was the previous encoding idea for ids
    where = f"{Polity}|{Variable}"
    # normally (like on the wiki or on another web interface) we would present all the Scoped values
    # for a variable and then reassert them enmass, deleting the prior versions
    # However, with a csv we don't know the order of the lines for all the multiple values
    # so we maintain a dict of what variables we've started to assert and
    # if this is a new variable we delete all the extant triples
    # this assumes, of course, that the csv contains, eventually, all the values for the property
    # and not just additions
    # MB: flushed_values is a dict that contains all the different properties that have been done for a Polity
    # in the *key:value* form as: {'AfDurrn': [var1, var2, ...]}
    try:
        flushed_values[Polity]   # if this doesnt fail, the Polity is NOT new, therefore the next line.
        new_polity = False
    except KeyError:                      # if the -try- fails, this is a new Polity, so empty the flushed values
        flushed_values[Polity] = [] # what variables have been flushed this session      
        new_polity = True

    if new_polity:
        # TODO how do you bind all the instances of an scm:Polity to a variable?
        # it's like we are not trusting the new_polity variable and we are checking it again!!
        # NOTE: Polity is the original name (AfGhurd) and lower_Polity is the canonical name (afghurd) of the Polity
        # NOTE: if left alone, a triple normally puts 'scm:' before a triple word.
        qp = WOQLQuery().woql_or(WOQLQuery().triple('v:Polity_ID','original_PolID',Polity),
                            # look up original if it exists under the lower_Polity name
                            # Doesn't exist, so create a Polity instance
                            # the id of the instance of scm:Polity will be the lower_polity
                            # we make sure the new 'scm:Polity' has a property called 'scm:original_PolID' 
                            # with its value: Polity 
                             WOQLQuery().woql_and(WOQLQuery().idgen(lower_Polity,[],'v:Polity_ID'), # create an atom (why can't we use a raw string?)
                                                  (WOQLQuery().insert('v:Polity_ID','scm:Polity',label=Polity). # create an instance of scm:Polity
                                                   property('original_PolID',Polity)))) # record the original 'spelling', e.g. AfHepht vs. afhepht
        # whatever the qp is, append it to the list of queries for this polity 
        polity_query.append(qp)

    # collect up all property queries for each Polity and when it changes, execute the collection once
    # if the property (Variable) has not yet been seen for this polity:
    # Do two things:
    # 1) Flush the property (Variable) for this Polity
    # 2) Make sure there are no old garbage values for the smae property in the database 
    if Variable not in flushed_values[Polity]:
        flushed_values[Polity].append(Variable) # flushed done
        old_value_var = unique_var('v:Old_Values')
        # old_value_var will only provide us with a temporary variable to use in the delete query
        # in case of scoped variables, we need to delete it sepaately because it is a class itself
        # for unscoped properties it is only a value and there is no object involved
        # It is ok that this fails since it might be a new property
        # or a new class instance without any property at all
        qf = WOQLQuery()
        if scoped:
            qf.opt(WOQLQuery().woql_and(WOQLQuery().triple('v:Polity_ID',property_name,old_value_var),
                            # TODO the Old_Values scoped value instances could have notes
                            # and those instance need to be deleted as well
                            # BUT NOT the CitedWork which might be shared
                            # Do it before deleting the value object
                            WOQLQuery().delete_triple('v:Polity_ID',property_name,old_value_var),
                            WOQLQuery().delete_object(old_value_var)))
        else:
            # if unscoped just drop triples directly
            # but if the values happen to be instance themselves, .e.g, Politys, don't delete them
            qf.opt(WOQLQuery().woql_and(WOQLQuery().triple('v:Polity_ID',property_name,old_value_var),
                                         WOQLQuery().delete_triple('v:Polity_ID',property_name,old_value_var)))
        polity_query.append(qf)
        # NOTE: 'v:Polity_ID' remains the same variable in all above queries for each Polity
        # Remember that we are merging all queries for one polity together

    qv = WOQLQuery() # updated/continued by side effect

    # time to take care of properties (the third argument onward) in assert_seshat_row
    # First: make sure that the values are well casted.

    # the main value is almost always in Value_From
    # we check to see if there is a Value_To, in this case, we form a new value (string): 'Value_From:Value_To'
    value = Value_From
    if 'Range' in raw_type:
        if Value_To != empty_value:
            value = Value_From + ':' + Value_To # don't use - as separator
    # now that the value is quite ready, we precast it to make some minor changes for coherency.
    # value is THE important piece of information in this row
    value = precast_values(value,raw_type,where)
    
    # dates and confidence are empty strings so far.
    dates = ''
    confidence = ''
    if scoped:
        # generate an instance of a scoped data value type
        # and connect it to its Polity class using the property_name
        pv_var = unique_var('v:propertyValue_ID')
        unique_id(qv,doc_property_Value,[lower_Polity],pv_var) # will this generate a new id each time and ensure unique id
        qv.insert(pv_var,scm_property_Value) # create an instance of the _Value boxed class
        qv.add_triple('v:Polity_ID',property_name,pv_var) # assert the scoped property value

        # get type, if enumerated check that the given value is (lower) the allowed value
        # else cast to type
        # do dates handle CE and BCE and AD and BC?
        inferred = False
        suspected = False
        disputed = False
        unknown = False
        # check if the string 'inferred' is in the value, if so, remove it, but change *inferred* to True
        if 'inferred' in value:
            # test scoped here; if not scoped we have a problem
            inferred = True
            value = value.split(' ')[1]
        if 'suspected' in value:
            suspected = True
            value = value.split(' ')[1]
        if 'unknown' in value:
            unknown = True
            # maybe we need to break here and skip the row
            value = 'UNKNOWN'#value.split(' ')[1]
        val_var = unique_var('v:Value')
        qv.cast(value,real_raw_type,val_var) 
        qv.add_triple(pv_var,property_value_name,val_var) # store the cast value on the proper property name on the _Value instance
        # we just added a triple related to one scoped value in qv
        # when the enumerations are working, we should make sure that the value is stored in an enumeration
        # if it is present, absent, p_to_a or a_to_p, etc...

        # NOTE: hard coded information about types under ScopedValue
        # if those types change in the schema, this code must change as well
        if Date_From != empty_value:
            dates = dates + f":{Date_From}"
            Date_FromTo = Date_From
            if Date_To != empty_value:
                dates =  f"[{Date_From},{Date_To}]"
                Date_FromTo = Date_From + '-' + Date_To


            # merge the result with Date_FromTo
            # might be sensitive to raw_gYear_type or gYear_type
            Date_FromTo = precast_values(Date_FromTo,gYear_type,f"{where}_DateFromTo")
            date_f_t_var = unique_var('v:Date_From_To')
            qv.cast(Date_FromTo,raw_gYear_type,date_f_t_var) # cast'ing to xsd:gYear fails to return anything and does not complain
            qv.add_triple(pv_var,'Years',date_f_t_var)

        if scoped and (Value_Note == 'disputed' or Value_Note == 'uncertain'):
            disputed = True
            qv.add_triple(pv_var,'Disputed',disputed)

        if scoped and unknown:
            qv.add_triple(pv_var,'Unknown',unknown)

        # TODO require scoped to deal with disputed else badly formed csv
            
        # Note we can have multiple 'confidence' assertions such as 'disputed' and 'inferred'? for the same 'value'?  Happens in the db, e.g.,
        # NGA|CnLrJin|Warfare variables|Military Technologies|Incendiaries|inferred present||||simple|disputed||
        # NGA|CnLrJin|Warfare variables|Military Technologies|Incendiaries|present||||simple|disputed||
        # TODO require scoped to deal with inferred else badly formed csv
        if scoped and (inferred or suspected):
            ci_var = unique_var('v:SVci')
            confid_doc = 'terminusdb:///data/Confidence'
            unique_id(qv,confid_doc,[Polity,property_name],ci_var)
            qv.insert(ci_var,Confidence_type) # make a Confidence instance
            civ_var = unique_var('v:SVciv')
            # Does cast deal w/ enums?
            if inferred:
                qv.cast('inferred',raw_Confidence_type,civ_var) # eventually not 'inferred' but a variable bound to the right enum instance with disputed as 'label'
                qv.add_triple(ci_var,Confidence_type,civ_var)   # The property has the name as the class!
                # add the Confidence instance to the ScopedValue instance NOTE the cardinality of confidence must be > 1
                qv.add_triple(pv_var,'confidence_tags',ci_var)
                confidence = confidence + "inferred"
            if suspected:
                qv.cast('suspected',raw_Confidence_type,civ_var) # eventually not 'inferred' but a variable bound to the right enum instance with disputed as 'label'
                qv.add_triple(ci_var,Confidence_type,civ_var)   # The property has the name as the class!
                # add the Confidence instance to the ScopedValue instance NOTE the cardinality of confidence must be > 1
                qv.add_triple(pv_var,'confidence_tags',ci_var)
                confidence = confidence + "suspected"

        # TODO any Date_Note save as a Note instance (v:Note) and assert qv.property('notes','v:Note')
    else: # unscoped (is it ever hit? check later)
        val_var = unique_var('v:UnscopedValue')
        qv.cast(value,real_raw_type,val_var)
        qv.add_triple('v:Polity_ID',property_name,val_var)
    polity_query.append(qv)
    if verbose_mode:
        print(f"Added {value}{dates}{confidence} for {Variable} on {Polity}")
    return


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
        scrape_file = 'test.csv'
        if 'csv_file' in schema_declarations:
            scrape_file = schema_declarations['csv_file']
        print(f"Parsing data from {scrape_file}")
        # eventually we read from csvs that look like:
        # NGA|Polity|Section|Subsection|Variable|Value From|Value To|Date From|Date To|Fact Type|Value Note|Date Note|Error Note
        # NGA|AfHepht|Social Complexity variables|Social Scale|Polity territory|1000000||450CE||complex|simple||
        # we only care about strings so parse the csv ourselves
        try:
            csv_file = open(scrape_file,"r")
        except IOError:
            print("ERROR: Could not open %s for reading." %  scrape_file)
            sys.exit(0)
        report_line = False # CONTROL
        skip_header_lines = 1
        delimiter = '|'
        comment = '#'
        line_number = 0
        for raw_line in csv_file:
            line_number += 1
            raw_line.strip()
            if report_line:
                print(f"{line_number}: {raw_line}")
            if line_number <= skip_header_lines:
                continue
            if raw_line[0] == comment: # skip comment lines
                continue
            NGA, Polity, Section, Subsection, Variable, Value_From, Value_To, Date_From, Date_To, Fact_Type, Value_Note, Date_Note, Error_Note = raw_line.split(delimiter)

            if 'combine_section_subsection_variable' in schema_declarations:
                Variable = f"{Section}|{Subsection}|{Variable}"
                
            assert_seshat_row(Polity, Variable, Value_From, Value_To, Date_From, Date_To, Fact_Type, Value_Note)

        csv_file.close()
        if polity_query: # finish the last polity_query, if any
            execute_commit(polity_query)
        print(f"Total assertions: {total_assertions} requiring inserts: {total_inserts} deletes: {total_deletes}")
        print(f"Total failed commits: {total_commit_failures}")
    else:
        print(f"Database {db_id} does not exist!")
    print('Execution time: %.1fs' % (time.time() - start_time))
# debugging phrases
# retrieve all properties and values from an originally named polity
# pp WOQLQuery().woql_and(WOQLQuery().triple('v:Polity_ID','original_PolID','AfDurrn'),WOQLQuery().triple('v:Polity_ID','v:P','v:PV'),WOQLQuery().triple('v:PV','v:p','v:V')).execute(client)
