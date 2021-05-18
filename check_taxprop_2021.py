import sys
import csv


def get_filename_stub(this_name, this_ext):
    this_stub = this_name

    this_pos = this_name.rfind(this_ext)
    if this_pos > 0:
        this_stub = this_name[:this_pos]

    return this_stub


def check_taxprop(tax_filename, names_filename, prop_filename):

    # names file is a single field file - store all names used in MSL
    if names_filename == "1":
        names_filename = "/Users/richardorton/TPMS/MSLs/MSL-all-2020_unique.txt"

    # tax_filename - my version of the current MSL with higher taxons on own line
    if tax_filename == "1":
        tax_filename = "/Users/richardorton/TPMS/MSLs/TaxPropChecker.csv"

    # prop_filename = "/Users/richardorton/TPMS/MSLs/TesProp2.txt"
    output_filename = get_filename_stub(prop_filename, ".txt") + "_changes.txt"

    #print("Input taxonomy file = " + tax_filename)
    #print("Input names file = " + names_filename)
    print("Input proposal file = " + prop_filename)
    #print("Output report file = " + output_filename)

    this_stub = prop_filename
    this_pos = prop_filename.rfind("_tpms.txt")
    if this_pos > 0:
        this_stub = prop_filename[:this_pos]

    # rank names
    ranks = [
        "realm",
        "subrealm",
        "kingdom",
        "subkingdom",
        "phylum",
        "subphylum",
        "class",
        "subclass",
        "order",
        "suborder",
        "family",
        "subfamily",
        "genus",
        "subgenus",
        "species"]

    # rank name endings for viruses
    rank_ends = {
        "realm": "viria",
        "subrealm": "vira",
        "kingdom": "virae",
        "subkingdom": "virites",
        "phylum": "viricota",
        "subphylum": "viricotina",
        "class": "viricetes",
        "subclass": "viricetidae",
        "order": "virales",
        "suborder": "virineae",
        "family": "viridae",
        "subfamily": "virinae",
        "genus": "virus",
        "subgenus": "virus"}

    # rank name endings for satellites
    satellite_ends = {
        "realm": "satellitia",
        "subrealm": "satellita",
        "kingdom": "satellitiae",
        "subkingdom": "satellitites",
        "phylum": "satelliticota",
        "subphylum": "satelliticotina",
        "class": "satelliticetes",
        "subclass": "satelliticetidea",
        "order": "satellitales",
        "suborder": "satellitineae",
        "family": "satellitidae",
        "subfamily": "satellitinae",
        "genus": "satellite",
        "subgenus": "satellite"}

    viroid_ends = {
        "realm": "viroidia",
        "subrealm": "viroida",
        "kingdom": "viroidiae",
        "subkingdom": "viroidites",
        "phylum": "viroidicota",
        "subphylum": "viroidicotina",
        "class": "viroidicetes",
        "subclass": "viroidicetidea",
        "order": "viroidales",
        "suborder": "viroidineae",
        "family": "viroidae",
        "subfamily": "viroidinae",
        "genus": "viroid",
        "subgenus": "viroid"}

    # field number -> name in TP
    fields = {
        0: "realm",
        1: "subrealm",
        2: "kingdom",
        3: "subkingdom",
        4: "phylum",
        5: "subphylum",
        6: "class",
        7: "subclass",
        8: "order",
        9: "suborder",
        10: "family",
        11: "subfamily",
        12: "genus",
        13: "subgenus",
        14: "species",
        15: "type sp?",
        16: "Exemplar GenBank Accession Number",
        17: "realm",
        18: "subrealm",
        19: "kingdom",
        20: "subkingdom",
        21: "phylum",
        22: "subphylum",
        23: "class",
        24: "subclass",
        25: "order",
        26: "suborder",
        27: "family",
        28: "subfamily",
        29: "genus",
        30: "subgenus",
        31: "species",
        32: "Type species?",
        33: "Exemplar GenBank Accession Number",
        34: "Exemplar virus name",
        35: "Virus name abbrevn",
        36: "Exemplar isolate designation",
        37: "Genome coverage",
        38: "Genome composition",
        39: "Change",
        40: "Rank",
        41: "Comments"}

    # the proposed taxonomy field col numbers (0 index) in the TP for each rank
    rank_fields = {
        "realm": 17,
        "subrealm": 18,
        "kingdom": 19,
        "subkingdom": 20,
        "phylum": 21,
        "subphylum": 22,
        "class": 23,
        "subclass": 24,
        "order": 25,
        "suborder": 26,
        "family": 27,
        "subfamily": 28,
        "genus": 29,
        "subgenus": 30,
        "species": 31}

    # the current taxonomy field col numbers (0 index) in the TP for each rank
    current_rank_fields = {
        "realm": 0,
        "subrealm": 1,
        "kingdom": 2,
        "subkingdom": 3,
        "phylum": 4,
        "subphylum": 5,
        "class": 6,
        "subclass": 7,
        "order": 8,
        "suborder": 9,
        "family": 10,
        "subfamily": 11,
        "genus": 12,
        "subgenus": 13,
        "species": 14}

    # genome coverage options in the TP
    genome_cov = ["CG", "CCG", "PG"]

    # genome composition options in the TP
    genome_comp = [
        "dsDNA",
        "ssDNA (-)",
        "ssDNA (+)",
        "ssDNA (+/-)",
        "dsDNA-RT",
        "ssRNA-RT",
        "dsRNA",
        "ssRNA",
        "ssRNA (-)",
        "ssRNA (+)",
        "ssRNA (+/-)",
        "multiple"]

    # genome composition without the spaces
    old_genome_comp = [
        "dsDNA",
        "ssDNA(-)",
        "ssDNA(+)",
        "ssDNA(+/-)",
        "dsDNA-RT",
        "ssRNA-RT",
        "dsRNA",
        "ssRNA",
        "ssRNA(-)",
        "ssRNA(+)",
        "ssRNA(+/-)",
        "multiple"]

    # taxonomic change options in the TP
    changes = [
        "Create new",
        "Abolish",
        "Move",
        "Rename",
        "Move; rename",
        "Split",
        "Merge",
        "Promote",
        "Demote"]

    hosts = []

    # These are the tax changes that result in a new name
    # New name needs to be checked if conform to rules and not existed before
    check_name_changes = [
        "Create new",
        "Rename",
        "Move; rename"]

    strict = False

    # names_filename is a single field file - store all names in tax_names
    tax_names = []
    with open(names_filename) as file_handler:
        for line in file_handler:
            line = line.strip()

            if line in tax_names:
                print("Internal error during unique name import - duplicate tax name found: " + line)
            else:
                tax_names.append(line)

    #print("Total unique taxon names in all ICTV MSLs = " + str(len(tax_names)))

    # string comparisons are case sensitive so store a lower case version of the names
    tax_names_lower = []
    case_dups = 0
    for name in tax_names:
        if name.lower() in tax_names_lower:
            case_dups += 1
            # print("Internal error during unique name import - duplicate tax name when ignoring case: " + name + " " + name.lower())
        else:
            tax_names_lower.append(name.lower())

    #print("Total taxon names with duplicate names when ignoring case = " + str(case_dups))

    # tax_filename - my version of the current MSL with higher taxons on own line
    mytax_fields = {
        "ID": 0,
        "realm": 1,
        "subrealm": 2,
        "kingdom": 3,
        "subkingdom": 4,
        "phylum": 5,
        "subphylum": 6,
        "class": 7,
        "subclass": 8,
        "order": 9,
        "suborder": 10,
        "family": 11,
        "subfamily": 12,
        "genus": 13,
        "subgenus": 14,
        "species": 15,
        "rank": 16,
        "taxonName": 17,
        "taxPath": 18}

    # taxonomy is a dict using taxName - to pull out the complete tax of a taxon
    taxonomy = {}
    # taxonomy_rank is a dict of just taxName and taxRank - to quickly check the rank of an existing taxon
    taxonomy_rank = {}
    # taxonomy_parent is a dict of just taxName and taxParent
    taxonomy_parent = {}
    # taxonomy lower case - used for case checking names against current taxonomy
    taxonomy_lower = []

    with open(tax_filename) as file_handler:
        reader = csv.reader(file_handler, delimiter=',')

        # header line
        next(reader)

        for row in reader:
            if row[17] in taxonomy:
                print("Internal error - duplicate taxon name found in taxonomy: " + row[18])
            else:
                # In the TPs family, genus, species rank assignments etc do not use capital at start - so convert rank to lower
                row[16] = row[16].lower()
                taxonomy[row[17]] = row
                taxonomy_rank[row[17]] = row[16]

                if row[17].lower() in taxonomy_lower:
                    print("Internal error - duplicate taxon name found in taxonomy when ignoring case: " + row[18])
                else:
                    taxonomy_lower.append(row[17].lower())

                # find the parent for the taxon (the first one that is not blank
                parent_from = mytax_fields[row[16]] - 1
                found_parent = False
                for i in range(parent_from, 0, -1):
                    if row[i] != "":
                        taxonomy_parent[row[17]] = row[i]
                        found_parent = True
                        break

                if not found_parent:
                    taxonomy_parent[row[17]] = ""

    #print("Total number of taxons in current MSL = " + str(len(taxonomy)))

    non_species_count = 0
    for parent in taxonomy_rank:
        if taxonomy_rank[parent] != "species":
            tax_count = 0
            non_species_count += 1
            for child in taxonomy_parent:
                if taxonomy_parent[child] == parent:
                    tax_count += 1

            if tax_count == 0:
                print("Internal error - parent without any children: " + parent)

    #print("Total non-species taxons in the current MSL = " + str(non_species_count))

    # taxprop list stores each line of the TP - filtered to remove empty lines out
    taxprop = []
    with open(prop_filename) as file_handler:
        # using tab in case comma used in comments
        # the java conversion from excel to txt should of removed any tabs within fields
        reader = csv.reader(file_handler, delimiter='\t')

        # 3 header lines - MUST BE like this - suggest double checking in the java program - as well as format
        # 1 = code assigned
        # 2 = Current Tax, Proposed Tax, Specify Chnages
        # 3 = Realm -> Species etc column headings
        next(reader)
        next(reader)
        next(reader)

        for row in reader:
            # Remove trailing and leading spaces - essential as exact matches used to compare to existing names
            for i in range(0, len(row)):
                row[i] = row[i].strip()

                space_test = True

                while space_test:
                    space_test = False
                    row[i] = row[i].replace("\t", " ")
                    # replace double space with space
                    row[i] = row[i].replace("  ", " ")

                    if row[i].find("  ") >= 0:
                        space_test = True

            # Java removes the blank lines - so no need to check here

            new_row = row[0:15] + [""] + row[15:31] + [""] + row[31:37] + row[38:]
            taxprop.append(new_row)

    print("Number of taxonomic changes in the TP = " + str(len(taxprop)))

    # all_output stores all the error messages
    all_output = []
    all_changes = []
    total_errors = 0
    # check that each line has a rank and a change (empty lines have already been filtered)
    for prop in taxprop:
        if prop[40] not in ranks:
            if prop[40].lower() in ranks:
                prop[40] = prop[40].lower()
            else:
                all_output.append("Error-F1\t" + prop[39] + "\t" + prop[40] + "\t\trank field '" + prop[40] + "' not found in the expected ranks - this means most of the checks can not be done - please fix\tline number = " + str(taxprop.index(prop) + 1))
                total_errors += 1
        if prop[39] not in changes:
            this_tax = ""
            if prop[40] in ranks:
                this_tax = prop[rank_fields[prop[40]]]

            all_output.append("Error-F2\t" + prop[39] + "\t" + prop[40] + "\t" + this_tax + "\tchange field '" + prop[39] + "' not found in the expected changes\tline number = " + str(taxprop.index(prop) + 1))
            total_errors += 1

        if prop[39] == "Promote" or prop[39] == "Demote" or prop[39] == "Split" or prop[39] == "Merge":
            all_output.append("Warning-W1\t" + prop[39] + "\t" + prop[40] + "\t" + this_tax + " this script can not currently process split/merge/promote/demote")

    # for species - initially check the species data is entered e.g. genome cov/comp
    for prop in taxprop:
        if prop[40] == "species":
            if prop[39] == "Create new":
                # 33=Exemplar genbank -> 38=genome comp
                for i in range(33, 39):
                    # often virus abbrev and/or isolate design are empty - turn off with strict = False
                    if prop[i] == "" and (strict or (not strict and i != 35 and i != 36)):
                        all_output.append("Error-S1\t" + prop[39] + "\t" + prop[40] + "\t" + prop[31] + "\tempty '" + fields[i] + "' data field\tline number = " + str(taxprop.index(prop) + 1))
                        total_errors += 1

                if prop[37] not in genome_cov:
                    all_output.append("Error-S2\t" + prop[39] + "\t" + prop[40] + "\t" + prop[31] + "\tgenome coverage '" + prop[37] + "' not in the expected coverages\tline number = " + str(taxprop.index(prop) + 1))
                    total_errors += 1

                if prop[38] not in genome_comp and prop[38] not in old_genome_comp:
                    all_output.append("Error-S3\t" + prop[39] + "\t" + prop[40] + "\t" + prop[31] + "\tgenome composition '" + prop[38] + "' not in the expected compositions\tline number = " + str(taxprop.index(prop) + 1))
                    total_errors += 1

    # check higher taxons do not have the species data populated
    for prop in taxprop:
        if prop[40] != "species" and prop[40] != "Please select":
            for i in range(33, 37):
                if prop[i] != "":
                    this_tax = ""
                    if prop[40] in ranks:
                        this_tax = prop[rank_fields[prop[40]]]

                    all_output.append("Error-S4\t" + prop[39] + "\t" + prop[40] + "\t" + this_tax + "\tnot a species rank but has the species field '" + fields[i] + "' populated with '" + prop[i] + "'\tline number = " + str(taxprop.index(prop) + 1))
                    total_errors += 1

    # genbanks used to check for duplicates within proposal
    # output all create species statement to check all props against each other AND against VMR
    # expand to check for delimiters
    genbanks = {}
    for prop in taxprop:
        if prop[33] != "":
            if "_" in prop[33]:
                all_output.append("Error-S5\t" + prop[39] + "\t" + prop[40] + "\t" + prop[31] + "\tunderscore in GenBank field (do not use RefSeqs): " + prop[33] + "\tline number = " + str(taxprop.index(prop) + 1))
                total_errors += 1

            if prop[33] in genbanks:
                all_output.append("Error-S6\t" + prop[39] + "\t" + prop[40] + "\t" + prop[31] + "\tduplicate GenBank accession number used: '" + prop[33] + "', also used for '" + genbanks[prop[33]] + "'\tline number = " + str(taxprop.index(prop) + 1))
                total_errors += 1
            else:
                genbanks[prop[33]] = prop[31]

    # check create and rename taxons are correct, and not used before
    # new_names is used to store the name and rank of all new taxons to check parents later
    new_names = {}
    new_names_lower = {}

    for prop in taxprop:
        # if the tax change (create, rename etc) results in a name change
        if prop[39] in check_name_changes:
            # Can't do anything in rank not defined!
            if prop[40] not in ranks:
                continue

            this_name = prop[rank_fields[prop[40]]]

            if this_name in taxonomy:
                all_output.append("Error-N1\t" + prop[39] + "\t" + prop[40] + "\t" + this_name + "\tthe proposed " + prop[40] + " name '" + this_name + "' already exists in the ICTV Taxonomy\tline number = " + str(taxprop.index(prop) + 1))
                total_errors += 1
            elif this_name.lower() in taxonomy_lower:
                all_output.append("Error-N2\t" + prop[39] + "\t" + prop[40] + "\t" + this_name + "\tthe proposed " + prop[40] + " name '" + this_name + "' already exists in the ICTV Taxonomy [if you ignore the case]\tline number = " + str(taxprop.index(prop) + 1))
                total_errors += 1
            elif this_name in tax_names or this_name.lower() in tax_names_lower:
                all_output.append("Error-N3\t" + prop[39] + "\t" + prop[40] + "\t" + this_name + "\tthe proposed " + prop[40] + " name '" + this_name + "' previously existed in the ICTV Taxonomy\tline number = " + str(taxprop.index(prop) + 1))
                total_errors += 1
            elif this_name in new_names:
                all_output.append("Error-N4\t" + prop[39] + "\t" + prop[40] + "\t" + this_name + "\tthe proposed " + prop[40] + " name '" + this_name + "' has already been used to create a new taxon in this proposal\tline number = " + str(taxprop.index(prop) + 1))
                total_errors += 1
            elif this_name.lower() in new_names_lower:
                all_output.append("Error-N5\t" + prop[39] + "\t" + prop[40] + "\t" + this_name + "\tthe proposed " + prop[40] + " name '" + this_name + "' has already been used [if you ignore the case] to create a new taxon in this proposal\tline number = " + str(taxprop.index(prop) + 1))
                total_errors += 1
            elif this_name == "":
                all_output.append("Error-N6\t" + prop[39] + "\t" + prop[40] + "\t\tthe proposed " + prop[40] + " name is blank\tline number = " + str(taxprop.index(prop) + 1))
                total_errors += 1
            else:
                new_names[this_name] = prop[40]
                new_names_lower[this_name.lower()] = prop[40]

            if this_name != "":
                check_taxon_name(prop[39], this_name, prop[40], rank_ends, satellite_ends, viroid_ends, all_output, prop, taxprop)

    # check that sub taxa are contained within a parent - a subgenus must be in a genus etc
    for prop in taxprop:
        if prop[18] != "" and prop[17] == "":
            all_output.append("Error-CS1\tsubrealm\t" + prop[18] + "\t\tsubrealm not in a realm in the proposed taxonomy\tline number = " + str(taxprop.index(prop) + 1))
            total_errors += 1
        if prop[20] != "" and prop[19] == "":
            all_output.append("Error-CS1\tsubkingdom\t" + prop[20] + "\t\tsubkingdom not in a kingdom in the proposed taxonomy\tline number = " + str(taxprop.index(prop) + 1))
            total_errors += 1
        if prop[22] != "" and prop[21] == "":
            all_output.append("Error-CS1\tsubphylum\t" + prop[22] + "\t\tsubphylum not in a phylum in the proposed taxonomy\tline number = " + str(taxprop.index(prop) + 1))
            total_errors += 1
        if prop[24] != "" and prop[23] == "":
            all_output.append("Error-CS1\tsubclass\t" + prop[24] + "\t\tsubclass not in a class in the proposed taxonomy\tline number = " + str(taxprop.index(prop) + 1))
            total_errors += 1
        if prop[26] != "" and prop[25] == "":
            all_output.append("Error-CS1\tsuborder\t" + prop[26] + "\t\tsuborder not in a order in the proposed taxonomy\tline number = " + str(taxprop.index(prop) + 1))
            total_errors += 1
        if prop[28] != "" and prop[27] == "":
            all_output.append("Error-CS1\tsubfamily\t" + prop[28] + "\t\tsubfamily not in a family in the proposed taxonomytline number = " + str(taxprop.index(prop) + 1))
            total_errors += 1
        if prop[30] != "" and prop[29] == "":
            all_output.append("Error-CS1\tsubgenus\t" + prop[30] + "\t\tsubgenus not in a genus in the proposed taxonomy\tline number = " + str(taxprop.index(prop) + 1))
            total_errors += 1

    # check if species is floating
    for prop in taxprop:
        if prop[40] == "species":
            # did have it only checking new ones but now just report all in proposed section that are floating
            if prop[29] == "" and prop[30] == "" and prop[39] != "Abolish":
                all_output.append("Error-FL1\t" + prop[39] + "\t" + prop[40] + "\t" + prop[31] + "\tspecies '" + prop[31] + "' is floating and not in a genus or a subgenus\tline number = " + str(taxprop.index(prop) + 1))
                total_errors += 1

    # check for floating genera - subgenera not in genera already checked above
    for prop in taxprop:
        if prop[40] == "genus":
            if prop[27] == "" and prop[28] == "" and prop[39] != "Abolish":
                all_output.append("Error-FL2\t" + prop[39] + "\t" + prop[40] + "\t" + prop[29] + "\tgenus '" + prop[29] + "' is floating and not in a family or subfamily\tline number = " + str(taxprop.index(prop) + 1))
                total_errors += 1

    is_abolished = []
    is_moved = []
    is_renamed = []
    renamed_list = {}

    # separate initial loop for abolish - need to make sure in the next loop creation, moves, renames can not involve abolished taxons
    for prop in taxprop:
        if prop[40] in ranks:
            if prop[39] == "Abolish":
                current_name = prop[current_rank_fields[prop[40]]]

                this_parent = current_parent = find_current_parent(prop, current_rank_fields[prop[40]])
                all_changes.append(["Abolish", prop[40], current_name, current_name.lower(), this_parent, prop[10], "", "", "", "", ""])

                all_output.append(check_proposed_taxonomy_empty(prop, fields, current_name, taxprop))

                # check the taxon actually exists in MSL
                if current_name in taxonomy:
                    this_tax = taxonomy[current_name]

                    # check not already been abolished
                    if current_name in is_abolished:
                        all_output.append("Error-A1\t" + prop[39] + "\t" + prop[40] + "\t" + current_name + "\tthe " + prop[40] + " '" + current_name + "' has already been abolished in the proposal\tline number = " + str(taxprop.index(prop) + 1))
                        total_errors += 1
                    else:
                        is_abolished.append(current_name)

                    all_output.append(check_current_taxonomy_not_empty(prop, taxprop))
                    all_output.append(check_current_taxonomy_correct_loose(prop, fields, current_name, taxprop, this_tax, strict))

                else:
                    all_output.append("Error-A2\t" + prop[39] + "\t" + prop[40] + "\t" + current_name + "\tthe taxon to be abolished '" + current_name + "' is not in the current MSL taxonomy\tline number = " + str(taxprop.index(prop) + 1))
                    all_output.append(check_taxon_case(current_name, prop, tax_names, tax_names_lower))

    # loop through ranks realm to species - top down order important
    for rank in ranks:
        # loop through each proposed change and do create/rename/move
        for prop in taxprop:
            if prop[40] == rank:
                current_name = prop[current_rank_fields[rank]]
                new_name = prop[rank_fields[rank]]

                if prop[39] == "Create new":

                    all_output.append(check_current_taxonomy_empty(prop, fields, new_name, taxprop))

                    all_output.append(check_proposed_empty_after_rank(prop, fields, new_name, taxprop, rank_fields))

                    check_parents_exist(prop, fields, new_name, taxprop, rank_fields, rank, taxonomy, taxonomy_rank, new_names, is_abolished, all_output, tax_names, tax_names_lower)

                    check_proposed_parents_loose(prop, rank_fields[rank], taxonomy_parent, all_output, fields, taxprop, taxonomy_rank, strict)

                    if new_name not in taxonomy_parent:
                        parent = find_proposed_parent(prop, rank_fields[rank])
                        taxonomy_parent[new_name] = parent
                        taxonomy_rank[new_name] = rank

                    this_genbank = prop[33].replace(" ", "").replace("/", ";").replace(",", ";")
                    out_gb = this_genbank
                    if ";" in this_genbank:
                        this_genbank_list = this_genbank.split(';')
                        out_gb = ""
                        for gb in this_genbank_list:
                            if out_gb != "":
                                out_gb += ";"

                            if ":" in gb:
                                this_gb_list = gb.split(':')
                                out_gb += this_gb_list[1]
                            else:
                                out_gb += gb

                    all_changes.append(["Create", rank, "", "", "", prop[10], new_name, new_name.lower(), taxonomy_parent[new_name], prop[27], out_gb])

                elif prop[39] == "Move" or prop[39] == "Rename" or prop[39] == "Move; rename":
                    current_parent = find_current_parent(prop, current_rank_fields[rank])
                    proposed_parent = find_proposed_parent(prop, rank_fields[rank])
                    all_changes.append([prop[39], rank, current_name, current_name.lower(), current_parent, prop[10], new_name, new_name.lower(), proposed_parent, prop[27], ""])

                    if current_name == "":
                        all_output.append("Error-MR11\t" + prop[39] + "\t" + prop[40] + "\t" + current_name + "\tthe current taxonomy name for the selected rank '" + prop[40] + "' is empty\tline number = " + str(taxprop.index(prop) + 1))

                    if new_name == "":
                        all_output.append("Error-MR12\t" + prop[39] + "\t" + prop[40] + "\t" + current_name + "\tthe proposed taxonomy name for the selected rank '" + prop[40] + "' is empty\tline number = " + str(taxprop.index(prop) + 1))

                    if prop[39] == "Rename" or prop[39] == "Move; rename":
                        if new_name == current_name:
                            all_output.append("Error-R1\t" + prop[39] + "\t" + prop[40] + "\t" + current_name + "\tthe renamed " + prop[40] + " does not actually change the name '" + current_name + "' -> '" + new_name + "'\tline number = " + str(taxprop.index(prop) + 1))

                    if prop[39] == "Move":
                        if current_name != new_name:
                            all_output.append("Error-M1\t" + prop[39] + "\t" + prop[40] + "\t" + current_name + "\tthe moved " + prop[40] + " does not have the same name after the move [possibly should be a move + rename] '" + current_name + "' -> '" + new_name + "'\tline number = " + str(taxprop.index(prop) + 1))

                    all_output.append(check_current_taxonomy_not_empty(prop, taxprop))

                    if current_name in taxonomy:
                        this_tax = taxonomy[current_name]

                        if current_name in is_abolished:
                            all_output.append("Error-MR1\t" + prop[39] + "\t" + prop[40] + "\t" + current_name + "\tthe " + prop[40] + " '" + prop[39] + "' has already been abolished in the proposal\tline number = " + str(taxprop.index(prop) + 1))

                        if (current_name in is_renamed and prop[39] == "Move") or (current_name in is_moved and prop[39] == "Rename"):
                            all_output.append("Error-MR2\t" + prop[39] + "\t" + prop[40] + "\t" + current_name + "\tthe " + prop[40] + " '" + prop[39] + "' is being renamed and moved separately in the proposal - merge the rename and move into one change\tline number = " + str(taxprop.index(prop) + 1))

                        if current_name in is_renamed and (prop[39] == "Rename" or prop[39] == "Move; rename"):
                            all_output.append("Error-MR3\t'" + prop[39] + "\t" + prop[40] + "\t" + current_name + "\tthe " + prop[40] + " '" + prop[39] + "' has already been renamed in the proposal\tline number = " + str(taxprop.index(prop) + 1))

                        if current_name in is_moved and (prop[39] == "Move" or prop[39] == "Move; rename"):
                            all_output.append("Error-MR4\t" + prop[39] + "\t" + prop[40] + "\t" + current_name + "\tthe " + prop[40] + " '" + prop[39] + "' has already been moved in the proposal\tline number = " + str(taxprop.index(prop) + 1))

                        if prop[39] == "Move" and current_name not in is_moved:
                            is_moved.append(current_name)
                        elif prop[39] == "Rename" and current_name not in is_renamed:
                            is_renamed.append(current_name)
                        else:
                            # rename and move
                            if current_name not in is_renamed:
                                is_renamed.append(current_name)
                            if current_name not in is_moved:
                                is_moved.append(current_name)

                        all_output.append(check_current_taxonomy_correct(prop, fields, current_name, taxprop, this_tax, strict))
                    else:
                        all_output.append("Error-MR5\t" + prop[39] + "\t" + prop[40] + "\t" + current_name + "\tthe " + prop[40] + " '" + current_name + "' is not in the current MSL taxonomy\tline number = " + str(taxprop.index(prop) + 1))
                        all_output.append(check_taxon_case(current_name, prop, tax_names, tax_names_lower))

                    all_output.append(check_proposed_empty_after_rank(prop, fields, current_name, taxprop, rank_fields))

                    if prop[39] == "Move" or prop[39] == "Move; rename":
                        if current_name in taxonomy:
                            current_parent = find_current_parent(prop, current_rank_fields[rank])
                            proposed_parent = find_proposed_parent(prop, rank_fields[rank])

                            renamed_parent = ""

                            if current_parent in renamed_list:
                                renamed_parent = renamed_list[current_parent]

                            if current_parent == proposed_parent or renamed_parent == proposed_parent:
                                all_output.append("Error-M10\t" + prop[39] + "\t" + prop[40] + "\t" + current_name + "\tthe moved taxon does not seem to have moved: parent = '" + current_parent + "' -> '" + proposed_parent + "'\tline number = " + str(taxprop.index(prop) + 1))

                            # all_output.append(check_current_proposed_different(prop, current_name, taxprop, rank_fields))
                    elif prop[39] == "Rename":
                        if current_name in taxonomy:
                            current_parent = find_current_parent(prop, current_rank_fields[rank])
                            proposed_parent = find_proposed_parent(prop, rank_fields[rank])

                            renamed_parent = ""

                            if current_parent in renamed_list:
                                renamed_parent = renamed_list[current_parent]

                            if current_parent != proposed_parent and renamed_parent != proposed_parent:
                                all_output.append("Error-R10\t" + prop[39] + "\t" + prop[40] + "\t" + current_name + "\tthe renamed taxon seems to have moved as well (perhaps should be a 'Move; Rename '" + current_parent + "' -> '" + proposed_parent + "'\tline number = " + str(taxprop.index(prop) + 1))

                        # all_output.append(check_current_proposed_same(prop, current_name, taxprop, rank_fields))

                    check_parents_exist(prop, fields, new_name, taxprop, rank_fields, rank, taxonomy, taxonomy_rank, new_names, is_abolished, all_output, tax_names, tax_names_lower)

                    if prop[39] == "Rename":
                        if current_name in taxonomy:
                            taxonomy_parent[new_name] = taxonomy_parent.pop(current_name)
                            taxonomy_rank[new_name] = taxonomy_rank.pop(current_name)

                            for child in taxonomy_parent:
                                if taxonomy_parent[child] == current_name:
                                    taxonomy_parent[child] = new_name

                            renamed_list[current_name] = new_name
                    elif prop[39] == "Move; rename":
                        if current_name in taxonomy:
                            taxonomy_parent[new_name] = taxonomy_parent.pop(current_name)
                            taxonomy_rank[new_name] = taxonomy_rank.pop(current_name)

                            for child in taxonomy_parent:
                                if taxonomy_parent[child] == current_name:
                                    taxonomy_parent[child] = new_name

                            parent = find_proposed_parent(prop, rank_fields[rank])
                            taxonomy_parent[new_name] = parent

                            renamed_list[current_name] = new_name
                    elif prop[39] == "Move":
                        if current_name in taxonomy:
                            parent = find_proposed_parent(prop, rank_fields[rank])
                            taxonomy_parent[current_name] = parent

                    check_proposed_parents(prop, rank_fields[rank], taxonomy_parent, all_output, fields, taxprop, taxonomy_rank, strict)

                else:
                    if prop[39] in changes and prop[39] != "Abolish":
                        all_output.append("Error-Internal\t" + prop[39] + "\t" + prop[40] + "\t" + current_name + "\tscript error - script can't currently cope with the taxonomic change: '" + prop[39] + "'\tline number = " + str(taxprop.index(prop) + 1))

    # do we need to catch a family being moved from a Class into a Realm???

    for parent in taxonomy_rank:
        if taxonomy_rank[parent] != "species":
            tax_count = 0

            for child in taxonomy_parent:
                if taxonomy_parent[child] == parent and child not in is_abolished:
                    tax_count += 1

                    if parent in is_abolished:
                        all_output.append("Error-AC1\tAbolish\t{}\t{}\ttaxon '{}' has been abolished but is not empty - still contains '{}'".format(taxonomy_rank[parent], parent, parent, child))

            if tax_count == 0 and parent not in is_abolished:
                all_output.append("Error-AC2\t\t{}\t{}\tthe taxon '{}' is empty - it does not contain any lower taxons".format(taxonomy_rank[parent], parent, parent))

    for out in all_output:
        if out == "":
            continue

        print(this_stub + " \t" + out)

    with open(output_filename, "w") as file_output:
        for change in all_changes:
            file_output.write(this_stub)
            for i in change:
                file_output.write("\t" + i)

            file_output.write("\n")

    if total_errors > 0:
        print("\nAfter fixing any errors - the Excel file should be re-run through the checker, as other errors may be apparent.")


def check_proposed_parents_loose(prop, rank_pos, taxonomy_parent, all_output, fields, taxprop, taxonomy_rank, strict):

    # find the last parent that is populated - so we know when to stop checking in the next loop
    end_pos = 17
    for i in range(17, rank_pos):
        if prop[i] != "":
            end_pos = i
            break

    # loop through each of the parents backwards - we don't check the parent of the realm as there is not one
    for i in range(rank_pos - 1, 17, -1):
        if prop[i] != "":
            child = prop[i]
            child_rank = fields[i]

            parent = ""
            parent_rank = "?"
            parent_pos = 0

            for j in range(i-1, 16, -1):
                if prop[j] != "":
                    parent = prop[j]
                    parent_rank = fields[j].lower()
                    parent_pos = j
                    break

            if not strict and parent_pos < end_pos:
                hide_me = "Hidden error"
            elif child in taxonomy_parent:
                if taxonomy_parent[child] != parent:
                    if parent_rank == "?":
                        parent_rank = taxonomy_rank[taxonomy_parent[child]]

                    msl_rank = ""
                    if taxonomy_parent[child] in taxonomy_rank:
                        msl_rank = taxonomy_rank[taxonomy_parent[child]]

                    all_output.append("Error-CPT10\t" + prop[39] + "\t" + prop[40] + "\t" + prop[rank_pos] + "\tin the proposed taxonomy the " + child_rank + " '" + child + "' has an incorrect parent, in the proposal the parent is: " + parent_rank + " = '" + parent + "', but the parent should be (based on MSL + any changes in the proposal): " + msl_rank + " = '" + taxonomy_parent[child] + "'\tline number = " + str((taxprop.index(prop) + 1)))


def check_proposed_parents(prop, rank_pos, taxonomy_parent, all_output, fields, taxprop, taxonomy_rank, strict):

    # loop through each of the parents backwards - we don't check the parent of the realm as there is not one
    for i in range(rank_pos - 1, 17, -1):
        if prop[i] != "":
            child = prop[i]
            child_rank = fields[i]

            parent = ""
            parent_rank = "?"
            parent_pos = 0

            for j in range(i-1, 16, -1):
                if prop[j] != "":
                    parent = prop[j]
                    parent_rank = fields[j].lower()
                    parent_pos = j
                    break

            if child in taxonomy_parent:
                if taxonomy_parent[child] != parent:
                    if parent_rank == "?":
                        parent_rank = taxonomy_rank[taxonomy_parent[child]]

                    msl_rank = ""
                    if taxonomy_parent[child] in taxonomy_rank:
                        msl_rank = taxonomy_rank[taxonomy_parent[child]]

                    all_output.append("Error-CPT10\t" + prop[39] + "\t" + prop[40] + "\t" + prop[rank_pos] + "\tin the proposed taxonomy the " + child_rank + " '" + child + "' has an incorrect parent, in the proposal the parent is: " + parent_rank + " = '" + parent + "', but the parent should be (based on MSL + any changes in the proposal): " + msl_rank + " = '" + taxonomy_parent[child] + "'\tline number = " + str((taxprop.index(prop) + 1)))


def find_proposed_parent(prop, rank_pos):
    parent = ""

    for i in range(rank_pos-1, 16, -1):
        if prop[i] != "":
            parent = prop[i]
            break

    return parent


def find_current_parent(prop, rank_pos):
    parent = ""

    for i in range(rank_pos-1, -1, -1):
        if prop[i] != "":
            parent = prop[i]
            break

    return parent


def check_taxon_name(this_change, this_name, this_rank, rank_ends, satellite_ends, viroid_ends, all_output, prop, taxprop):

    if not this_name[0].isalpha():
        all_output.append("Error-CTN1\t" + this_change + "\t" + this_rank + "\t" + this_name + "\tthe proposed " + this_rank + " name '" + this_name + "' does not start with a letter\tline number = " + str((taxprop.index(prop) + 1)))
    elif not this_name[0].isupper():
        all_output.append("Error-CTN2\t" + this_change + "\t" + this_rank + "\t" + this_name + "\tthe proposed " + this_rank + " name '" + this_name + "' does not start with a capital letter\tline number = " + str((taxprop.index(prop) + 1)))

    if this_rank != "species":
        for i in this_name:
            if not i.isalpha():
                all_output.append("Error-CTN3\t" + this_change + "\t" + this_rank + "\t" + this_name + "\tthe proposed " + this_rank + " name '" + this_name + "' contains non-alphabetic characters\tline number = " + str((taxprop.index(prop) + 1)))

        if not this_name.endswith(rank_ends[this_rank]) and not this_name.endswith(satellite_ends[this_rank]) and not this_name.endswith(viroid_ends[this_rank]):
            all_output.append("Error-CTN4\t" + this_change + "\t" + this_rank + "\t" + this_name + "\tthe proposed " + this_rank + " name '" + this_name + "' does not end with '" + rank_ends[this_rank] + "' or '" + satellite_ends[this_rank] + "' or '" + viroid_ends[this_rank] + "'\tline number = " + str((taxprop.index(prop) + 1)))
    else:
        for i in this_name:
            if not i.isalnum() and i != " " and i != "-":
                all_output.append("Error-CTN5\t" + this_change + "\t" + this_rank + "\t" + this_name + "\tthe proposed " + this_rank + " name '" + this_name + "' contains a character that is not alphanumeric, a space or a hyphen\tline number = " + str((taxprop.index(prop) + 1)))

            if len(this_name) < 6:
                all_output.append("Error-CTN6\t" + this_change + "\t" + this_rank + "\t" + this_name + "\tthe proposed " + this_rank + " name '" + this_name + "' is too short (<6 characters) (" + str(len(this_name)) + "\tline number = " + str((taxprop.index(prop) + 1)))


def check_proposed_taxonomy_empty(prop, fields, current_name, taxprop):
    this_out = ""
    for i in range(17, 32):
        if prop[i] != "":
            if this_out != "":
                this_out += ", "

            this_out += fields[i] + ": '" + prop[i] + "'"

    out_return = ""

    if this_out != "":
        out_return = "Error-CPT1\t{}\t{}\t{}\thas populated proposed taxonomy fields [no need for proposed taxonomy for an abolish]: {}\tline number = {}".format(prop[39], prop[40], current_name, this_out, (taxprop.index(prop) + 1))

    return out_return


def check_proposed_empty_after_rank(prop, fields, new_name, taxprop, rank_fields):
    this_out = ""
    for i in range(rank_fields[prop[40]] + 1, 32):
        if prop[i] != "":
            if this_out != "":
                this_out += ", "

            this_out += fields[i] + ": " + prop[i]

    out_return = ""

    if this_out != "":
        out_return = "Error-CPT2\t{}\t{}\t{}\thas proposed taxonomy fields populated after the taxon itself: {}\tline number = {}".format(prop[39], prop[40], new_name, this_out, (taxprop.index(prop) + 1))

    return out_return


def check_current_taxonomy_empty(prop, fields, new_name, taxprop):
    this_out = ""
    for i in range(0, 17):
        if prop[i] != "":
            if this_out != "":
                this_out += ", "

            this_out += fields[i] + ": " + prop[i]

    out_return = ""

    if this_out != "":
        out_return = "Error-CCT1\t{}\t{}\t{}\thas populated current taxonomy fields [no need for current taxonomy for creations]: {}\tline number = {}".format(prop[39], prop[40], new_name, this_out, (taxprop.index(prop) + 1))

    return out_return


def check_current_taxonomy_not_empty(prop, taxprop):
    blank_test = True
    for i in range(0, 15):
        if prop[i] != "":
            blank_test = False

    out_return = ""

    if blank_test:
        out_return = "Error-CCT2\t{}\t{}\t\thas a completely blank current taxonomy\tline number = {}".format(prop[39], prop[40], (taxprop.index(prop) + 1))

    return out_return


def check_current_taxonomy_correct_loose(prop, fields, current_name, taxprop, this_tax, strict):
    # for a create only the parent needs to be correct

    # this checks against MSL - so automatically checks there are no ranks after the taxon
    # when would the exemplar for the current every really be populated

    # find the first parent populated in current tax
    start_pos = 0
    for i in range(0, 15):
        if prop[i] != "":
            start_pos = i
            break

    this_out = ""
    for i in range(0, 15):
        if not strict and i < start_pos:
            continue
        if prop[i] != this_tax[i + 1]:
            if this_out != "":
                this_out += ", "
            this_out += fields[i] + " in this proposal = '" + prop[i] + "' but MSL = '" + this_tax[i + 1] + "'"

    out_return = ""

    if this_out != "":
        out_return = "Error-CCT3\t{}\t{}\t{}\tcurrent taxonomy does not match the existing MSL: {}\tline number = {}".format(prop[39], prop[40], current_name, this_out, (taxprop.index(prop) + 1))

    return out_return


def check_current_taxonomy_correct(prop, fields, current_name, taxprop, this_tax, strict):
    # this checks against MSL - so automatically checks there are no ranks after the taxon
    # when would the exemplar for the current every really be populated

    this_out = ""
    for i in range(0, 15):
        if prop[i] != this_tax[i + 1]:
            if this_out != "":
                this_out += ", "
            this_out += fields[i] + " in this proposal = '" + prop[i] + "' but MSL = '" + this_tax[i + 1] + "'"

    out_return = ""

    if this_out != "":
        out_return = "Error-CCT3\t{}\t{}\t{}\tcurrent taxonomy does not match the existing MSL: {}\tline number = {}".format(prop[39], prop[40], current_name, this_out, (taxprop.index(prop) + 1))

    return out_return


def check_current_proposed_different(prop, current_name, taxprop, rank_fields):
    # old and flawed - if checking a species, the parent genus could be renamed - this check would say it has moved when it has not
    # check that the current taxonomy is different to the proposed - ignoring the taxon itself - i.e. has it been moved
    out_return = ""
    move_test = False
    for i in range(17, rank_fields[prop[40]]):
        if prop[i] != prop[i - 17]:
            move_test = True

    if not move_test:
        out_return = "Error-CPT3\t{}\t{}\t{}\tthe moved taxon does not seem to have moved - it has the same proposed taxonomy as the current taxonomy\tline number = {}".format(prop[39], prop[40], current_name, (taxprop.index(prop) + 1))

    # technically this won't pick up if a species is in a genus, and the genus is renamed, moved - this would flag the species as yes species moved when it has not

    return out_return


def check_current_proposed_same(prop, current_name, taxprop, rank_fields):
    # again - flawed - a renamed species could reside in a renamed genus - this would flag it as being moved
    # check that the current taxonomy is different to the proposed - ignoring the taxon itself - i.e. has it been renamed
    out_return = ""
    same_test = True
    for i in range(17, rank_fields[prop[40]]):
        if prop[i] != prop[i - 17]:
            same_test = False

    if not same_test:
        out_return = "Error-CPT3\t{}\t{}\t{}\tthe renamed taxon seems to have moved - it has a different proposed taxonomy to the current taxonomy (excluding the renamed taxon itself)\tline number = {}".format(prop[39], prop[40], current_name, (taxprop.index(prop) + 1))

    # technically this won't pick up if a species is in a genus, and the genus is renamed, moved - this would flag the species as yes species moved when it has not

    return out_return


def check_parents_exist(prop, fields, new_name, taxprop, rank_fields, rank, taxonomy, taxonomy_rank, new_names, is_abolished, all_output, tax_names, tax_names_lower):

    for i in range(17, rank_fields[rank]):
        if prop[i] != "":
            if prop[i] in taxonomy and prop[i] in is_abolished:
                all_output.append("Error-CPT4\t" + prop[39] + "\t" + prop[40] + "\t" + new_name + "\thas a parent taxon who is being abolished in this proposal: " + prop[i] + "\tline number = " + str(taxprop.index(prop) + 1))

            if prop[i] not in taxonomy and prop[i] not in new_names:
                all_output.append("Error-CPT5\t" + prop[39] + "\t" + prop[40] + "\t" + new_name + "\thas a parent taxon that does not exist in the current MSL or created in this proposal: " + fields[i] + " = '" + prop[i] + "'\tline number = " + str(taxprop.index(prop) + 1))

                this_name_lower = prop[i].lower()
                for name in new_names:
                    if name.lower() == this_name_lower:
                        all_output.append("Error-CPT9\t" + prop[39] + "\t" + prop[40] + "\t" + new_name + "\tthe parent taxon does however match when ignoring case to the proposed name: '" + prop[i] + "' - check and correct the case of the taxon name\tline number = " + str(taxprop.index(prop) + 1))

                this_out = check_taxon_case(prop[i], prop, tax_names, tax_names_lower)

                if this_out != "":
                    all_output.append("Error-CPT8\t" + prop[39] + "\t" + prop[40] + "\t" + new_name + "\tthe parent taxon does however match to the current MSL when ignoring the case: '" + prop[i] + "' - check and correct the case of the taxon name\tline number = " + str(taxprop.index(prop) + 1))
            else:
                if prop[i] in taxonomy_rank and rank_fields[taxonomy_rank[prop[i]]] != i:
                    all_output.append("Error-CPT6\t" + prop[39] + "\t" + prop[40] + "\t" + new_name + "\thas a parent whose rank is incorrect: '" + prop[i] + "' rank in this statement = '" + fields[i] + "' but MSL rank = " + taxonomy_rank[prop[i]] + "\tline number = " + str(taxprop.index(prop) + 1))
                if prop[i] in new_names and rank_fields[new_names[prop[i]]] != i:
                    all_output.append("Error-CPT7\t" + prop[39] + "\t" + prop[40] + "\t" + new_name + "\thas a parent whose rank is incorrect: '" + prop[i] + "' rank in this statement = '" + fields[i] + "' but rank created in this proposal = " + new_names[prop[i]] + "\tline number = " + str(taxprop.index(prop) + 1))


def check_taxon_case(this_name, prop, tax_names, tax_names_lower):
    this_out = ""
    this_name_lower = this_name.lower()

    if this_name not in tax_names:
        if this_name_lower in tax_names_lower:
            correct_name = "?"
            for name in tax_names:
                if this_name_lower == name.lower():
                    correct_name = name

            this_out = "Error-CTC1\t" + prop[39] + "\t" + prop[40] + "\t" + this_name + "\tthe " + prop[40] + " name is not found in the existing taxonomy but it does match when ignoring the case - the correct taxon name with correct case = " + correct_name;

    return this_out


arguments = len(sys.argv)

check_taxprop(sys.argv[1], sys.argv[2], sys.argv[3])


#print("\n...finished check_taxprop.py")
