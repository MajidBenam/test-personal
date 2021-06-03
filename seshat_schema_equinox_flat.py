# This is a reduced version; see Kevin's idea about other enumerations
# What about Categories?
# takes 577s to create schema or nearly 10m
# takes ~4s to assert a fact, implying 52hrs to assert equinox!
schema_declarations = {'combine_section_subsection_variable':False,
                       'csv_file':'equinox.csv'}    # equinox.csv
enumerations = [
    # This is only used in ScopedValue
    ("Confidence", "Confidence Tags", "Tags that can be added to values to indicate confidence in the value of some piece data", [
    ["inferred", "Inferred", "The value has been logically inferred from other evidence"], # This means that if we parse 'inferred present' we need to assert present as value w/ confidence inferred
    #["disputed", "Disputed", "The evidence is disputed - some believe this data to be incorrect"], # for {} values
    ["suspected", "Suspected", "An RA asserts that it can be said with a high degree of confidence that it is not known whether the feature was present or absent in the context."],

    # Actually treat suspected like inferred...a type of confidence on, e.g., unknown below
    # uncertain is represented as alternative entries (triples) for the same date or as a numeric range (using a Range type)
    ]),

    # present/absent properties via ScopedEpistemicState
    ("EpistemicState", "Epistemic State", "The existence of a feature in the historical record", [
    ["absent", "Absent", "The feature was absent in this historical context"],
    ["present", "Present", "The feature was present in this historical context"],
    ["absent-to-present", "Absent To Present", "The feature was in transition from absent to present in this historical context"],
    ["present-to-absent", "Present To Absent", "The feature was in transition from present to absent in this historical context"],
    #["unknown", "Unknown", "It can be said with a high degree of confidence that it is not known whether the feature was present or absent in the context."],
    #["suspected_unknown", "Suspected unknown", "An RA asserts that it can be said with a high degree of confidence that it is not known whether the feature was present or absent in the context."],
    ]),
    ]

class_defns = [
    # Must have this since define_seshat_schema.py assumes this as a default domain for all properties
    ("PoliticalAuthority","Political Authority","A human social group with some autonomous political authority.", ["Organization"]),
    ("Polity","Polity","A polity is defined as an independent political unit. Kinds of polities range from villages (local communities) through simple and complex chiefdoms to states and empires. A polity can be either centralized or not (e.g., organized as a confederation). What distinguishes a polity from other human groupings and organizations is that it is politically independent of any overarching authority; it possesses sovereignty. Polities are defined spatially by the area enclosed within a boundary on the world map. There may be more than one such areas. Polities are dynamical entities, and thus their geographical extent may change with time. Thus, typically each polity will be defined by a set of multiple boundaries, each for a specified period of time. For prehistoric periods and for areas populated by a multitude of small-scale polities we use a variant called quasi-polity.",
     ["PoliticalAuthority"]),
    ("QuasiPolity","Quasi-Polity","The polity-based approach is not feasible for those periods when a region is divided up among a multitude of small-scale polities (e.g., independent villages or even many small chiefdoms). In this instance we use the concept of 'quasi-polity'. Similarly, for societies known only archaeologically we may not be able to establish the boundaries of polities, even approximately. Quasi-polity is defined as a cultural area with some degree of cultural homogeneity (including linguistic, if known) that is distinct from surrounding areas. For example, the Marshall Islands before German occupation had no overarching native or colonial authority (chiefs controlled various subsets of islands and atolls) and therefore it was not a polity. But it was a quasi-polity because of the significant cultural and linguistic uniformity.<P>We collect data for the quasi-polity as a whole. This way we can integrate over (often patchy) data from different sites and different polities to estimate what the 'generic' social and political system was like. Data is not entered for the whole region but for a 'typical' polity in it. For example, when coding a quasi-polity, its territory is not the area of the region as a whole, but the average or typical area of autonomous groups within the NGA.",
     ["PoliticalAuthority"]),
    ("Macrostate", "Macrostate","A very large centralized state", ["PoliticalAuthority"]), # Category: Macrostate
    ]

topics = [
    ("GeneralVariables","General variables","",["Topic"]),
    ("InstitutionalVariables","Institutional Variables","",["Topic"]),

    ("ReligionNormativeIdeology","Religion and Normative Ideology","",["Topic"]),
    ("DeificationRulers","Deification of Rulers","",["ReligionNormativeIdeology"]),
    ("MoralizingSupernaturalPowers","Moralizing Supernatural Powers","",["ReligionNormativeIdeology"]),
    ("NormativeIdeologicalAspectsEquityProsociality","NormativeIdeologicalAspectsEquityProsociality","",["ReligionNormativeIdeology"]),
    ("LimitsOnPowerOfChiefExecutive", "Limits on the power of the Chief Executive","", ["InstitutionalVariables"]),
    
    ("SocialComplexityVariables","Social Complexity variables","",["Topic"]),
    ("BureaucracyCharacteristics","Bureaucracy characteristics","",["SocialComplexityVariables"]),
    ("HierarchicalComplexity","Hierarchical Complexity","",["SocialComplexityVariables"]),
    ("Information","Information","",["SocialComplexityVariables"]),
    ("Law","Law","",["SocialComplexityVariables"]),
    ("Professions","Professions","",["SocialComplexityVariables"]),
    ("SocialScale","Social Scale","",["SocialComplexityVariables"]),
    ("SpecializedBuildings","Specialized Buildings: polity owned","",["SocialComplexityVariables"]),

    ("MacrostateVariables","Macrostate Variables","Information about macrostates",["Topic"]),

    ("WarfareVariables","Warfare Variables","",["Topic"]),
    ("MilitaryTechnologies","Military Technologies","",["WarfareVariables"]),

    ("SocialMobility","Social Mobility","",["Topic"]),
    ("Status","Military Technologies","",["SocialMobility"]),

    ]

# issues: RA is different by 'Topic' which means that the Topics need to be instantiated and associated with a Polity
# this will be the same with Ritual
# GoldHorde: [Polity]
# sections: <sections> # several tuples: GeneralVariables_#55 SocialComplexityVariables_#23

# GeneralVariables_#55 [GeneralVariables]
# applies_to: <GoldenHorde>
# RA: 'DanH'

# SocialComplexityVariables_#23: [SocialComplexityVariables]
# applies_to: <GoldenHorde>
# RA: 'Edward'
# subsections: <subsections> # several tuples BureaucracyCharacteristics_#45

# BureaucracyCharacteristics_#45 [BureaucracyCharacteristics]
# applies_to: <SocialComplexityVariables_#23>!!
# examination_system: 'present'


unscoped_properties = [
    # Must have this for insert_to_csv to find existing Polities using original PolIDs
    ('original_PolID','xsd:string','Original Polity ID','The original name encoding on the wiki, preserving capitalization'),
    ]
# This is no more a flat version of Equinox: every variable is scoped, but they also involve Topics for better querying
# variable property names no more involve section and subsection, but labels still involve actual section and subsections
# the 'label' is the text from the csv Section|Subsection|Variable for matching
scoped_properties = [
    ("Alternative_names", "String", ["GeneralVariables"], "General variables||Alternative names",""),
    ("Capital","String",["GeneralVariables"],"General variables||Capital",""),
    ("Degree_of_centralization","String",["GeneralVariables"],"General variables||Degree of centralization",""),
    ("Duration","GYearRange",["GeneralVariables"],"General variables||Duration",""),
    ("Language","String",["GeneralVariables"],"General variables||Language",""),
    ("Original_name","String",["GeneralVariables"],"General variables||Original name",""),
    ("Peak_Date","GYearRange",["GeneralVariables"],"General variables||Peak Date",""),
    ("GV_RA","String",["GeneralVariables"],"General variables||RA",""),
    ("Supra-polity_relations","String",["GeneralVariables"],"General variables||Supra-polity relations",""),
    ("Supracultural_entity","String",["GeneralVariables"],"General variables||Supracultural entity",""),
    ("scale_of_supra-cultural_interaction","String",["GeneralVariables"],"General variables||scale of supra-cultural interaction",""),
    ("Constraint_on_executive_by_government","EpistemicState",["LimitsOnPowerOfChiefExecutive"],"Institutional Variables|Limits on Power of the Chief Executive|Constraint on executive by government",""),
    ("Constraint_on_executive_by_non-government","EpistemicState",["LimitsOnPowerOfChiefExecutive"],"Institutional Variables|Limits on Power of the Chief Executive|Constraint on executive by non-government",""),
    ("Impeachment","EpistemicState",["LimitsOnPowerOfChiefExecutive"],"Institutional Variables|Limits on Power of the Chief Executive|Impeachment",""),
    ("IV_RA","String",["InstitutionalVariables"],"Institutional Variables||RA",""),
    ("Ideological_reinforcement_of_equality","EpistemicState",["DeificationRulers"],"Religion and Normative Ideology|Deification of Rulers|Ideological reinforcement of equality",""),
    ("Ideological_thought_equates_elites_and_commoners","EpistemicState",["DeificationRulers"],"Religion and Normative Ideology|Deification of Rulers|Ideological thought equates elites and commoners",""),
    ("Ideological_thought_equates_rulers_and_commoners","EpistemicState",["DeificationRulers"],"Religion and Normative Ideology|Deification of Rulers|Ideological thought equates rulers and commoners",""),
    ("Rulers_are_gods","EpistemicState",["DeificationRulers"],"Religion and Normative Ideology|Deification of Rulers|Rulers are gods",""),
    ("Rulers_are_legitimated_by_gods","EpistemicState",["DeificationRulers"],"Religion and Normative Ideology|Deification of Rulers|Rulers are legitimated by gods",""),
    ("Moral_concern_is_primary","EpistemicState",["MoralizingSupernaturalPowers"],"Religion and Normative Ideology|Moralizing Supernatural Powers|Moral concern is primary",""),
    ("Moralizing_enforcement_in_afterlife","EpistemicState",["MoralizingSupernaturalPowers"],"Religion and Normative Ideology|Moralizing Supernatural Powers|Moralizing enforcement in afterlife",""),
    ("Moralizing_enforcement_in_this_life","EpistemicState",["MoralizingSupernaturalPowers"],"Religion and Normative Ideology|Moralizing Supernatural Powers|Moralizing enforcement in this life",""),
    ("Moralizing_enforcement_is_agentic","EpistemicState",["MoralizingSupernaturalPowers"],"Religion and Normative Ideology|Moralizing Supernatural Powers|Moralizing enforcement is agentic",""),
    ("Moralizing_enforcement_is_certain","EpistemicState",["MoralizingSupernaturalPowers"],"Religion and Normative Ideology|Moralizing Supernatural Powers|Moralizing enforcement is certain",""),
    ("Moralizing_enforcement_is_targeted","EpistemicState",["MoralizingSupernaturalPowers"],"Religion and Normative Ideology|Moralizing Supernatural Powers|Moralizing enforcement is targeted",""),
    ("Moralizing_enforcement_of_rulers","EpistemicState",["MoralizingSupernaturalPowers"],"Religion and Normative Ideology|Moralizing Supernatural Powers|Moralizing enforcement of rulers",""),
    ("Moralizing_norms_are_broad","EpistemicState",["MoralizingSupernaturalPowers"],"Religion and Normative Ideology|Moralizing Supernatural Powers|Moralizing norms are broad",""),
    ("Moralizing_religion_adopted_by_commoners","EpistemicState",["MoralizingSupernaturalPowers"],"Religion and Normative Ideology|Moralizing Supernatural Powers|Moralizing religion adopted by commoners",""),
    ("Moralizing_religion_adopted_by_elites","EpistemicState",["MoralizingSupernaturalPowers"],"Religion and Normative Ideology|Moralizing Supernatural Powers|Moralizing religion adopted by elites",""),
    ("Ideological_reinforcement_of_equality","EpistemicState",["NormativeIdeologicalAspectsEquityProsociality"],"Religion and Normative Ideology|Normative Ideological Aspects of Equity and Prosociality|Ideological reinforcement of equality",""),
    ("Ideological_thought_equates_elites_and_commoners","EpistemicState",["NormativeIdeologicalAspectsEquityProsociality"],"Religion and Normative Ideology|Normative Ideological Aspects of Equity and Prosociality|Ideological thought equates elites and commoners",""),
    ("Ideological_thought_equates_rulers_and_commoners","EpistemicState",["NormativeIdeologicalAspectsEquityProsociality"],"Religion and Normative Ideology|Normative Ideological Aspects of Equity and Prosociality|Ideological thought equates rulers and commoners",""),
    ("Ideology_reinforces_prosociality","EpistemicState",["NormativeIdeologicalAspectsEquityProsociality"],"Religion and Normative Ideology|Normative Ideological Aspects of Equity and Prosociality|Ideology reinforces prosociality",""),
    ("production_of_public_goods","EpistemicState",["NormativeIdeologicalAspectsEquityProsociality"],"Religion and Normative Ideology|Normative Ideological Aspects of Equity and Prosociality|production of public goods",""),
    ("Ideological_reinforcement_of_equality","EpistemicState",["NormativeIdeologicalAspectsEquityProsociality"],"Religion and Normative Ideology|Normative ideological Aspects of Equity and Prosociality|Ideological reinforcement of equality",""),
    ("Ideological_thought_equates_elites_and_commoners","EpistemicState",["NormativeIdeologicalAspectsEquityProsociality"],"Religion and Normative Ideology|Normative ideological Aspects of Equity and Prosociality|Ideological thought equates elites and commoners",""),
    ("Ideological_thought_equates_rulers_and_commoners","EpistemicState",["NormativeIdeologicalAspectsEquityProsociality"],"Religion and Normative Ideology|Normative ideological Aspects of Equity and Prosociality|Ideological thought equates rulers and commoners",""),
    ("Ideology_reinforces_prosociality","EpistemicState",["NormativeIdeologicalAspectsEquityProsociality"],"Religion and Normative Ideology|Normative ideological Aspects of Equity and Prosociality|Ideology reinforces prosociality",""),
    ("production_of_public_goods","EpistemicState",["NormativeIdeologicalAspectsEquityProsociality"],"Religion and Normative Ideology|Normative ideological Aspects of Equity and Prosociality|production of public goods",""),
    ("RNI_RA","String",["ReligionNormativeIdeology"],"Religion and Normative Ideology||RA",""),
    ("Examination_system","EpistemicState",["BureaucracyCharacteristics"],"Social Complexity variables|Bureaucracy characteristics|Examination system",""),
    ("Full-time_bureaucrats","EpistemicState",["BureaucracyCharacteristics"],"Social Complexity variables|Bureaucracy characteristics|Full-time bureaucrats",""),
    ("Merit_promotion","EpistemicState",["BureaucracyCharacteristics"],"Social Complexity variables|Bureaucracy characteristics|Merit promotion",""),
    ("Specialized_government_buildings","EpistemicState",["BureaucracyCharacteristics"],"Social Complexity variables|Bureaucracy characteristics|Specialized government buildings",""),
    ("Administrative_levels","IntegerRange",["HierarchicalComplexity"],"Social Complexity variables|Hierarchical Complexity|Administrative levels",""),
    ("Military_levels","IntegerRange",["HierarchicalComplexity"],"Social Complexity variables|Hierarchical Complexity|Military levels",""),
    ("Religious_levels","IntegerRange",["HierarchicalComplexity"],"Social Complexity variables|Hierarchical Complexity|Religious levels",""),
    ("Settlement_hierarchy","IntegerRange",["HierarchicalComplexity"],"Social Complexity variables|Hierarchical Complexity|Settlement hierarchy",""),
    ("Articles","EpistemicState",["Information"],"Social Complexity variables|Information|Articles",""),
    ("Calendar","EpistemicState",["Information"],"Social Complexity variables|Information|Calendar",""),
    ("Couriers","EpistemicState",["Information"],"Social Complexity variables|Information|Couriers",""),
    ("Fiction","EpistemicState",["Information"],"Social Complexity variables|Information|Fiction",""),
    ("Foreign_coins","EpistemicState",["Information"],"Social Complexity variables|Information|Foreign coins",""),
    ("General_postal_service","EpistemicState",["Information"],"Social Complexity variables|Information|General postal service",""),
    ("History","EpistemicState",["Information"],"Social Complexity variables|Information|History",""),
    ("Indigenous_coins","EpistemicState",["Information"],"Social Complexity variables|Information|Indigenous coins",""),
    ("Lists_tables_and_classifications","EpistemicState",["Information"],"Social Complexity variables|Information|Lists tables and classifications",""),
    ("Mnemonic_devices","EpistemicState",["Information"],"Social Complexity variables|Information|Mnemonic devices",""),
    ("Non-phonetic_writing","EpistemicState",["Information"],"Social Complexity variables|Information|Non-phonetic writing",""),
    ("Nonwritten_records","EpistemicState",["Information"],"Social Complexity variables|Information|Nonwritten records",""),
    ("Paper_currency","EpistemicState",["Information"],"Social Complexity variables|Information|Paper currency",""),
    ("Philosophy","EpistemicState",["Information"],"Social Complexity variables|Information|Philosophy",""),
    ("Phonetic_alphabetic_writing","EpistemicState",["Information"],"Social Complexity variables|Information|Phonetic alphabetic writing",""),
    ("Postal_stations","EpistemicState",["Information"],"Social Complexity variables|Information|Postal stations",""),
    ("Practical_literature","EpistemicState",["Information"],"Social Complexity variables|Information|Practical literature",""),
    ("Precious_metals","EpistemicState",["Information"],"Social Complexity variables|Information|Precious metals",""),
    ("Religious_literature","EpistemicState",["Information"],"Social Complexity variables|Information|Religious literature",""),
    ("Sacred_Texts","EpistemicState",["Information"],"Social Complexity variables|Information|Sacred Texts",""),
    ("Scientific_literature","EpistemicState",["Information"],"Social Complexity variables|Information|Scientific literature",""),
    ("Script","EpistemicState",["Information"],"Social Complexity variables|Information|Script",""),
    ("Tokens","EpistemicState",["Information"],"Social Complexity variables|Information|Tokens",""),
    ("Written_records","EpistemicState",["Information"],"Social Complexity variables|Information|Written records",""),
    ("Courts","EpistemicState",["Law"],"Social Complexity variables|Law|Courts",""),
    ("Formal_legal_code","EpistemicState",["Law"],"Social Complexity variables|Law|Formal legal code",""),
    ("Judges","EpistemicState",["Law"],"Social Complexity variables|Law|Judges",""),
    ("Professional_Lawyers","EpistemicState",["Law"],"Social Complexity variables|Law|Professional Lawyers",""),
    ("Professional_military_officers","EpistemicState",["Professions"],"Social Complexity variables|Professions|Professional military officers",""),
    ("Professional_priesthood","EpistemicState",["Professions"],"Social Complexity variables|Professions|Professional priesthood",""),
    ("Professional_soldiers","EpistemicState",["Professions"],"Social Complexity variables|Professions|Professional soldiers",""),
    ("Polity_population","DecimalRange",["SocialScale"],"Social Complexity variables|Social Scale|Polity Population",""),
    ("Polity_territory","DecimalRange",["SocialScale"],"Social Complexity variables|Social Scale|Polity territory",""),
    ("Population_of_the_largest_settlement","DecimalRange",["SocialScale"],"Social Complexity variables|Social Scale|Population of the largest settlement",""),
    ("Bridges","EpistemicState",["SpecializedBuildings"],"Social Complexity variables|Specialized Buildings: polity owned|Bridges",""),
    ("Canals","EpistemicState",["SpecializedBuildings"],"Social Complexity variables|Specialized Buildings: polity owned|Canals",""),
    ("Mines_or_quarries","EpistemicState",["SpecializedBuildings"],"Social Complexity variables|Specialized Buildings: polity owned|Mines or quarries",""),
    ("Ports","EpistemicState",["SpecializedBuildings"],"Social Complexity variables|Specialized Buildings: polity owned|Ports",""),
    ("Roads","EpistemicState",["SpecializedBuildings"],"Social Complexity variables|Specialized Buildings: polity owned|Roads",""),
    ("Drinking_water_supply_systems","EpistemicState",["SpecializedBuildings"],"Social Complexity variables|Specialized Buildings: polity owned|drinking water supply systems",""),
    ("Food_storage_sites","EpistemicState",["SpecializedBuildings"],"Social Complexity variables|Specialized Buildings: polity owned|food storage sites",""),
    ("Irrigation_systems","EpistemicState",["SpecializedBuildings"],"Social Complexity variables|Specialized Buildings: polity owned|irrigation systems",""),
    ("Markets","EpistemicState",["SpecializedBuildings"],"Social Complexity variables|Specialized Buildings: polity owned|markets",""),
    ("SC_RA","String",["SocialComplexityVariables"],"Social Complexity variables||RA",""),
    ("Elite_status_is_hereditary","EpistemicState",["Status"],"Social Mobility|Status|Elite status is hereditary",""),
    ("SM_RA","String",["SocialMobility"],"Social Mobility||RA",""),  
    ("WV_RA","String",["WarfareVariables"],"Warfare variables||RA",""),      
    ("Atlatl","EpistemicState",["MilitaryTechnologies"],"Warfare variables|Military Technologies|Atlatl",""),
    ("Battle_axes","EpistemicState",["MilitaryTechnologies"],"Warfare variables|Military Technologies|Battle axes",""),
    ("Breastplates","EpistemicState",["MilitaryTechnologies"],"Warfare variables|Military Technologies|Breastplates",""),
    ("Bronze","EpistemicState",["MilitaryTechnologies"],"Warfare variables|Military Technologies|Bronze",""),
    ("Camels","EpistemicState",["MilitaryTechnologies"],"Warfare variables|Military Technologies|Camels",""),
    ("Chainmail","EpistemicState",["MilitaryTechnologies"],"Warfare variables|Military Technologies|Chainmail",""),
    ("Complex_fortifications","EpistemicState",["MilitaryTechnologies"],"Warfare variables|Military Technologies|Complex fortifications",""),
    ("Composite_bow","EpistemicState",["MilitaryTechnologies"],"Warfare variables|Military Technologies|Composite bow",""),
    ("Copper","EpistemicState",["MilitaryTechnologies"],"Warfare variables|Military Technologies|Copper",""),
    ("Crossbow","EpistemicState",["MilitaryTechnologies"],"Warfare variables|Military Technologies|Crossbow",""),
    ("Daggers","EpistemicState",["MilitaryTechnologies"],"Warfare variables|Military Technologies|Daggers",""),
    ("Ditch","EpistemicState",["MilitaryTechnologies"],"Warfare variables|Military Technologies|Ditch",""),
    ("Dogs","EpistemicState",["MilitaryTechnologies"],"Warfare variables|Military Technologies|Dogs",""),
    ("Donkeys","EpistemicState",["MilitaryTechnologies"],"Warfare variables|Military Technologies|Donkeys",""),
    ("Earth_ramparts","EpistemicState",["MilitaryTechnologies"],"Warfare variables|Military Technologies|Earth ramparts",""),
    ("Elephants","EpistemicState",["MilitaryTechnologies"],"Warfare variables|Military Technologies|Elephants",""),
    ("Fortified_camps","EpistemicState",["MilitaryTechnologies"],"Warfare variables|Military Technologies|Fortified camps",""),
    ("Gunpowder_siege_artillery","EpistemicState",["MilitaryTechnologies"],"Warfare variables|Military Technologies|Gunpowder siege artillery",""),
    ("Handheld_firearms","EpistemicState",["MilitaryTechnologies"],"Warfare variables|Military Technologies|Handheld firearms",""),
    ("Helmets","EpistemicState",["MilitaryTechnologies"],"Warfare variables|Military Technologies|Helmets",""),
    ("Horses","EpistemicState",["MilitaryTechnologies"],"Warfare variables|Military Technologies|Horses",""),
    ("Iron","EpistemicState",["MilitaryTechnologies"],"Warfare variables|Military Technologies|Iron",""),
    ("Javelins","EpistemicState",["MilitaryTechnologies"],"Warfare variables|Military Technologies|Javelins",""),
    ("Laminar_armor","EpistemicState",["MilitaryTechnologies"],"Warfare variables|Military Technologies|Laminar armor",""),
    ("Leather_cloth","EpistemicState",["MilitaryTechnologies"],"Warfare variables|Military Technologies|Leather cloth",""),
    ("Limb_protection","EpistemicState",["MilitaryTechnologies"],"Warfare variables|Military Technologies|Limb protection",""),
    ("Long_walls","IntegerRange",["MilitaryTechnologies"],"Warfare variables|Military Technologies|Long walls",""),
    ("Merchant_ships_pressed_into_service","EpistemicState",["MilitaryTechnologies"],"Warfare variables|Military Technologies|Merchant ships pressed into service",""),
    ("Moat","EpistemicState",["MilitaryTechnologies"],"Warfare variables|Military Technologies|Moat",""),
    ("Modern_fortifications","EpistemicState",["MilitaryTechnologies"],"Warfare variables|Military Technologies|Modern fortifications",""),
    ("Plate_armor","EpistemicState",["MilitaryTechnologies"],"Warfare variables|Military Technologies|Plate armor",""),
    ("Polearms","EpistemicState",["MilitaryTechnologies"],"Warfare variables|Military Technologies|Polearms",""),
    ("Scaled_armor","EpistemicState",["MilitaryTechnologies"],"Warfare variables|Military Technologies|Scaled armor",""),
    ("Self_bow","EpistemicState",["MilitaryTechnologies"],"Warfare variables|Military Technologies|Self bow",""),
    ("Settlements_in_a_defensive_position","EpistemicState",["MilitaryTechnologies"],"Warfare variables|Military Technologies|Settlements in a defensive position",""),
    ("Shields","EpistemicState",["MilitaryTechnologies"],"Warfare variables|Military Technologies|Shields",""),
    ("Sling_siege_engines","EpistemicState",["MilitaryTechnologies"],"Warfare variables|Military Technologies|Sling siege engines",""),
    ("Slings","EpistemicState",["MilitaryTechnologies"],"Warfare variables|Military Technologies|Slings",""),
    ("Small_vessels_canoes_etc","EpistemicState",["MilitaryTechnologies"],"Warfare variables|Military Technologies|Small vessels (canoes etc)",""),
    ("Spears","EpistemicState",["MilitaryTechnologies"],"Warfare variables|Military Technologies|Spears",""),
    ("Specialized_military_vessels","EpistemicState",["MilitaryTechnologies"],"Warfare variables|Military Technologies|Specialized military vessels",""),
    ("Steel","EpistemicState",["MilitaryTechnologies"],"Warfare variables|Military Technologies|Steel",""),
    ("Stone_walls_(mortared)","EpistemicState",["MilitaryTechnologies"],"Warfare variables|Military Technologies|Stone walls (mortared)",""),
    ("Stone_walls_(non-mortared)","EpistemicState",["MilitaryTechnologies"],"Warfare variables|Military Technologies|Stone walls (non-mortared)",""),
    ("Swords","EpistemicState",["MilitaryTechnologies"],"Warfare variables|Military Technologies|Swords",""),
    ("Tension_siege_engines","EpistemicState",["MilitaryTechnologies"],"Warfare variables|Military Technologies|Tension siege engines",""),
    ("War_clubs","EpistemicState",["MilitaryTechnologies"],"Warfare variables|Military Technologies|War clubs",""),
    ("Wood_bark_etc","EpistemicState",["MilitaryTechnologies"],"Warfare variables|Military Technologies|Wood bark etc",""),
    ("Wooden_palisades","EpistemicState",["MilitaryTechnologies"],"Warfare variables|Military Technologies|Wooden palisades",""),
 #   ("LSCR_of_OC_Duration","Integer",[],"Warfare variables|Most dysphoric collective ritual of the official cult|Duration",""),
 #   ("LSCR_of_OC_Duration","Integer",[],"Warfare variables|Most euphoric collective ritual of the official cult|Duration",""),
 #   ("LSCR_of_OC_Duration","Integer",[],"Warfare variables|Most frequent collective ritual of the official cult|Duration",""),
 #   ("Most_widespread_collective_ritual_of_the_official_cult_Duration","Integer",[],"Warfare variables|Most widespread collective ritual of the official cult|Duration",""),
    ]
