#!/usr/bin/python3
import os
#######################################################################################################################
###                                                                                                                   #
### By Gregg Russell <g.russ77@gmail.com> - https://greggoryrussell.com                                               #
###                                                                                                                   #
### This somewhat hacky script helped me convert an existing configuration repository on Gitlab that contained        #
### Icinga configuration files, but the monitoring server itself was quite deprecated with several broken features    #
### within the web interface. This was my first assignment to tackle after hiring in at a university. This program    #
### converts Icinga1 configuration scripts into the Icinga2 syntax. This program helped me automate the process of    #
### migrating existing monitoring configurations of over 900 services and 500 hosts for the college of engineering    #
### including assets that overlapped with multiple departments, groups and even special interest projects.            #
### I haven't tested this script since the last time I ran it. This is a scrubbed version of that conversion program. #
#######################################################################################################################
# 1. ) Load the V1 Script --
def read_v1_config(v1File):
    global FileName
    match = re.search(r'[^\/]*\.\w+$',str(v1File))
    FileName = match.group() + '.conf'
    split_line = []
    with open(str(v1File),"r") as f:
        print(8 * '~' + ' FILE READING ' + 8 * '~')
        print("Loaded File: " + str(v1File))      
# 2a.)   Count the lines --
        line_total=0 # Start at 0 for COUNTING. Don't forget to subtract 1!
        for line in f:
            line_total += 1
# 2b.)  Append each line into a stripped, and split list string so we can run it through the if-then gauntlet            
            split_line.append(line.strip().split())
        f.close() # Even if the script is closed, we have a list full of stuff to compute!
        print('==- File Closed --=')
        #print(*split_line, sep = "\n")
        return split_line
# 3. ) Return the split_line

###########################################################################
### The Cruncher will understand v2 syntax rules and format accordingly ###
### for writing to new files (V2 Configs)                               ###
###########################################################################
def crunch_split_list(MySplitList):
    print('\t####- CRUNCHING -####') # Make Crunch Function's output be one tab unit

    split_count=len(MySplitList)
    n=0
    while n < split_count:
        split_line = MySplitList[n] # Just like how I had it before...
 #       print(split_line)
        n += 1 # Increment to the next line when finished
        ########### BEGIN V1-Syntax Interpretation ###########
        if len(split_line) == 0:
            continue
        ## If we read a config's comments, simply write them as-is into the new script
        if split_line[0] == '#':
            #'/#.*/g'
            # for match in re.finditer(r'/#.*/g', command_line): # Capture Comment Syntax
            # TODO: Preserve full comment lines AND account for '##'* not just '#'
            print('\tHashmark -- Comment Detected!')
            comment_str=' '.join(map(str,split_line))
 #           print(comment_str) # Testing
            write_v2_conf(comment_str) # Write string to output file 
            del split_line[0] # del, not pop (which makes it returnable) allows the list to continue reiterating.
            #['#', 'Example', 'Config', 'with', 'only', '1', 'entry']
            print('\tRemoved comment from queue..................')
            continue
        elif split_line[0] == 'define' and split_line[2] == '{':
            print('\tdefine statement encountered!')
            keyword = split_line[1]
            if keyword == 'command':
                print('\tKeyword \"command\" found!')            
                continue # If we know we have a define just go back to the loop, the conditions will be okay!
                          
            elif keyword == 'service':
                print('\tKeyword \"service\" found!')
                continue
            elif keyword == 'host':
                print('\t\tHOST Detected!')
                continue
            elif keyword == 'hostgroup':
                print('\t\tHOSTGROUP Detected!')
                continue
            elif keyword == 'contact':
                print('CONTACT DETECTED!')
                continue
    
            n += 1 # Increment to the next line when finished
            continue
        elif keyword == 'contact' and split_line[0] != '}':
            contact_dict.update( { str(split_line[0] ) :''.join(map(str,split_line[1:])) })
            print('py dict equiv ->\t' + str(split_line[0] ) +':' + str(split_line[1] ))
            print("contact dictionary updated.....")
            process_contact()
        elif keyword == 'host' and split_line[0] != '}':
                print('v1 [host] detected - adding\n' + str(split_line[0]) + ':' + str(split_line[1:]))
                #host_list.append(split_line[0])
                host_dict.update({str(split_line[0]):''.join(map(str,split_line[1:]))})
                print(host_dict)
        elif keyword == 'hostgroup' and split_line[0] != '}':
                print('v1 [hostgroup] detected - adding\n' + str(split_line[0]) + ':' + str(split_line[1:]))
                #hostgroup_list.append(split_line[0])
                hostgroup_dict.update({str(split_line[0]):' '.join(map(str,split_line[1:]))})
                print(hostgroup_dict)
        elif split_line[0] == 'use' and keyword == 'service':
                print('v1 [service] -- Detected keyword "use"')
                service_dict.update({'use': str(split_line[1])})
                process_service()
                continue
        elif split_line[0] == 'use' and keyword == 'host':
                print('v1 [host] -- Detected keyword "use" -- CONVERTING TO import statements...')
                import_list.append(str(split_line[1]))
                print('ADDING ~~~~ ' + str(split_line[1]))
                #process_import() # A bit premature
                continue
        elif split_line[0] == 'hostgroup_name':
                print('v1 [service] -- Detected keyword "hostgroup_name"')
                service_dict.update({'hostgroup_name': str(split_line[1])})
                process_service()
                continue
        elif split_line[0] == 'host_name' and keyword == 'service':
                print('v1 [service] -- Detected keyword "host_name"')
                service_dict.update({'host_name': str(split_line[1])})
                process_service()
                continue
        elif split_line[0] == 'service_description':
                print('v1 [service] -- Detected keyword "service_description"')
                service_dict.update({'service_description': ' '.join(map(str,split_line[1:]))  })
                process_service()
                continue
        elif split_line[0] == 'check_command':
                print('v1 [service] -- Detected keyword "check_command"')
                service_dict.update({'check_command': str(split_line[1])})
                process_service()
                continue
        elif split_line[0] in serv_extras.keys():
            print('Detected nagios '+ str(split_line[0]) +' service command...')
            service_dict.update({str(split_line[0]):str(split_line[1])})
            process_service()
            continue
    
        elif split_line[0] == 'command_name':
            print('\tFound a "command_name"')
            command_name = split_line[1] # Now that I have it I need a means of converting and writing it into the output file 
 #           print("Here is the command name:\t"+str(command_name)) #
            v2_commands.append({'command_name':str(command_name)})
            process_commands()
        elif split_line[0] == 'command_line':
            print('\tFound "command_line" (@)(@)(@)(@)(@)(@)(@)(@)(@)')
            command_line =' '.join(map(str,split_line[1:])) 
            if '/usr/bin/perl' in command_line:
                print('Found a pesky binary call, attempting reslicing of string...')
                command_line =' '.join(map(str,split_line[2:]))
                dex = split_line.index('/usr/bin/perl')
                split_line.pop(dex) # pop the perl binary call out of our command line, otherwise we get blanks in the output files!
            print(command_line)
            # To Preserve order, write them into the args_dict as we encounter them...
            # Floating Arguments (Such as "-a 450" "-P 8808" "-H db.example.com")
            
            for match in re.finditer(r'(-\w)(\s\S+)',command_line): # Captures '-h = $HOSTNAME$'
                print("\"" + match.group(1).strip() + "\" = " + "\"" + match.group(2).strip() + "\"")
                first = match.group(1)
                second = match.group(2)
                arguments_list.append(NewArgument(first,second))
            for match in re.finditer(r'(--\w+)=(\w*\S+)', command_line): # Captures via Regex '--user=nagios'
                first = match.group(1)
                second = match.group(2)
                arguments_list.append(NewArgument(first,second))
            v2_commands.append({'command_line':str(split_line[1])})
            process_commands()
        elif split_line[0] == '}':
            if keyword == 'host':
                print('HOST ENDING BRACE')
                process_host()
            elif keyword == 'hostgroup':
                print('HOSTGROUP ENDING BRACE')
                process_hostgroup()
            else:
                print('\tEnding brace detected!')

##############################################################
### Collections - Groups we can use to prep v2 conversions ###
##############################################################
v2_commands = []
arguments_list = []
args_dict = {}
service_dict = {}
host_dict = {}

serv_extras = {
'name':'1',
'register':"0",
'active_checks_enabled':'0', # Note these 0 and 1 values are just placeholders. The process_service() command will fill the extras_dict value with the split_line[1] index instead.
'passive_checks_enabled':'1',
'parallelize_check':'1',
'obsess_over_service':'1',
'check_freshness':'0',
'notifications_enabled':'1',
'event_handler_enabled':'1',
'flap_detection_enabled':'1',
'process_perf_data':'1',
'retain_status_information':'1',
'retain_nonstatus_information':'1'
            }
contact_dict = {}
hostgroup_dict = {}
groups_list = []
import_list = []


# Writing CheckCommand objects to V2 Configs
# 
def process_commands(): # Make output at least 2 tab characters
    create_args = False
    arg_count = str(len(arguments_list))
    if len(arguments_list) == 0:
        print('\t\tNo Detected Arguments to process')
    else:
        print('\t\tDetected ' + arg_count + " arguments!")
        create_args = True
    if len(v2_commands) !=2: #Two because 'command_line' and 'command_name'
        print('\t\tNo Arguments to process')
        write_it = False
    else:
        print(12 * '=' + ' Commands ready to process! ' + 12 * '=')
        write_it = True
        for item in v2_commands:
            if 'command_line' in item:
                #print(item['command_line'])
                cmd_line = item['command_line']
            elif 'command_name' in item:
                #print(item['command_name'])
                cmd_name=item['command_name']
            else:
                print('Whoops')
##################### WITHOUT ARGUMENTS #####################
    if write_it == True and create_args == False:
        # Key = Original Term/Word in V1 Syntax
        # Value = Replacement for V2 Syntax
        print("Writing no Arguments in this script...")
        v2_str = "object CheckCommand " + "\"" + str(cmd_name) + "\" " + "{\n" \
            "\tcommand = [\t"+ str(cmd_line) + "\t]" \
                "\n}"
        # FIXME: $HOSTNAME$ should be $host.name$
        replace_words= {
            '$USER1$/':'PluginDir + ',
            '/usr/bin/perl ':'', # Hacky, but it IS one way of removing full path calls to the perl binary
            '$HOSTNAME$':'host.name',
            '$HOSTADDRESS$':'$host.address$',
            '$HOSTADDRESS6$':'$host.address6$',
            '$HOSTDISPLAYNAME$':'$host.display_name$',
            '$HOSTALIAS$':'(use$',
            '$HOSTCHECKCOMMAND$':'$host.check_command$',
            '$HOSTSTATE$':'$host.state$',
            '$HOSTSTATEID$':'$host.state_id$',
            '$HOSTSTATETYPE$':'$host.state_type$',
            '$HOSTATTEMPT$':'$host.check_attempt$',
            '$MAXHOSTATTEMPT$':'$host.max_check_attempts$',
            '$LASTHOSTSTATE$':'$host.last_state$',
            '$LASTHOSTSTATEID$':'$host.last_state_id$',
            '$LASTHOSTSTATETYPE$':'$host.last_state_type$',
            '$LASTHOSTSTATECHANGE$':'$host.last_state_change$',
            '$HOSTDOWNTIME$':'$host.downtime_depth$',
            '$HOSTDURATIONSEC$':'$host.duration_sec$',
            '$HOSTLATENCY$':'$host.latency$',
            '$HOSTEXECUTIONTIME$':'$host.execution_time$',
            '$HOSTOUTPUT$':'$host.output$',
            '$HOSTPERFDATA$':'$host.perfdata$',
            '$LASTHOSTCHECK$':'$host.last_check$',
            '$HOSTNOTES$':'$host.notes$',
            '$HOSTNOTESURL$':'$host.notes_url$',
            '$HOSTACTIONURL$':'$host.action_url$',
            '$TOTALSERVICES$':'$host.num_services$',
            '$TOTALSERVICESOK$':'$host.num_services_ok$',
            '$TOTALSERVICESWARNING$':'$host.num_services_warning$',
            '$TOTALSERVICESUNKNOWN$':'$host.num_services_unknown$',
            '$TOTALSERVICESCRITICAL$':'$host.num_services_critical$'
        }
        for key, value in replace_words.items():
            v2_str = v2_str.replace(str(key), str(value))
        print('\t\twriting to output file...')
        print(v2_str)
        write_v2_conf(v2_str)
        print(12 * '=' + ' Command Processing Finished ' + 12 * '=')
        v2_commands.clear()
##################### WITH ARGUMENTS #####################
    if write_it == True and create_args == True:
        # Key = Original Term/Word in V1 Syntax
        # Value = Replacement for V2 Syntax
        print("@@@@ WE ARE Writing Arguments in this script!!!")
        #process_args()
        #print(cmd_line.split)
        # Note to self: The extra "\"" is necessary so we can get command = [ PluginDir + "/blah" ] (Complete Double Quote Wrap)
        v2_str = "object CheckCommand " + "\"" + str(cmd_name) + "\" " + "{\n" \
            "\tcommand = [\t" + str(cmd_line) +"\"" + "\t]" \
                "\n\n\targuments = {" \
                    "\t" + process_args() + "" \
                    "\n\t}\n" \
                "\n}"
        replace_words= {
            '$USER1$/':'PluginDir + ',
            '/usr/bin/perl ':'', # Hacky, but it IS one way of removing full path calls to the perl binary
            '$HOSTNAME$':'host.name',
            '$HOSTADDRESS$':'$host.address$',
            '$HOSTADDRESS6$':'$host.address6$',
            '$HOSTDISPLAYNAME$':'$host.display_name$',
            '$HOSTALIAS$':'(use$',
            '$HOSTCHECKCOMMAND$':'$host.check_command$',
            '$HOSTSTATE$':'$host.state$',
            '$HOSTSTATEID$':'$host.state_id$',
            '$HOSTSTATETYPE$':'$host.state_type$',
            '$HOSTATTEMPT$':'$host.check_attempt$',
            '$MAXHOSTATTEMPT$':'$host.max_check_attempts$',
            '$LASTHOSTSTATE$':'$host.last_state$',
            '$LASTHOSTSTATEID$':'$host.last_state_id$',
            '$LASTHOSTSTATETYPE$':'$host.last_state_type$',
            '$LASTHOSTSTATECHANGE$':'$host.last_state_change$',
            '$HOSTDOWNTIME$':'$host.downtime_depth$',
            '$HOSTDURATIONSEC$':'$host.duration_sec$',
            '$HOSTLATENCY$':'$host.latency$',
            '$HOSTEXECUTIONTIME$':'$host.execution_time$',
            '$HOSTOUTPUT$':'$host.output$',
            '$HOSTPERFDATA$':'$host.perfdata$',
            '$LASTHOSTCHECK$':'$host.last_check$',
            '$HOSTNOTES$':'$host.notes$',
            '$HOSTNOTESURL$':'$host.notes_url$',
            '$HOSTACTIONURL$':'$host.action_url$',
            '$TOTALSERVICES$':'$host.num_services$',
            '$TOTALSERVICESOK$':'$host.num_services_ok$',
            '$TOTALSERVICESWARNING$':'$host.num_services_warning$',
            '$TOTALSERVICESUNKNOWN$':'$host.num_services_unknown$',
            '$TOTALSERVICESCRITICAL$':'$host.num_services_critical$'
        }
        for key, value in replace_words.items():
            v2_str = v2_str.replace(str(key), str(value))
        print('\t\twriting to output file...')
        print(v2_str)
        write_v2_conf(v2_str)
        print(12 * '=' + ' Command Processing Finished ' + 12 * '=')
        v2_commands.clear()
        arguments_list.clear() # Purge arguments list so we avoid repeating another statement's arguments

def process_args():
    print(8 * '!!##$$')
    arg_str = ''
    for x in arguments_list:
        arg_str += '\n\t' + str(x)
    print(arg_str)
    return arg_str
# Argument Class should allow me to dump all arguments into the output file like how I want...
class NewArgument:
    def __init__(self, arg_flag, arg_target):
        self.arg_flag = arg_flag.strip()
        self.arg_target = arg_target.strip()
    
    def __str__(self):
        outstr = '"' + str(self.arg_flag) + '" = "' + str(self.arg_target) + '"'
        return outstr

def process_groups():
    print(8 * '!!##$$')
    grp_str = ''
    for x in groups_list:
        grp_str += '\n\t' + str(x)
    print(grp_str)
    return str(grp_str)

def process_import():
    global import_list
    print('\t\t\tNow outputting from "import_list"..............................................')
    for i in import_list:
        print(i + ' (FROM import_list)' )
        imp_str += '\n\timport\t "' + str(i) + '"'
    print(imp_str)
    return str(imp_str)    

def process_host():
    print(host_dict)
    has_contacts = False
    try:
        i_str = str(host_dict['use'])
        c_hst = str(host_dict['contacts'])
        if len(str(host_dict['contacts'])) > 0:
            print('Host processing --> scraping contacts')
            has_contacts = True
            groups_list.append(str(hostgroup_dict['contacts']))
        if has_contacts == False:
            # join function allows for seperation of multiple items via "x1","x2","y1", etc.
            i_str = '","'.join(map(str,i_str))
            out_str = 'object Host ' + '"' + str(host_dict['host_name']) + '" {\n' \
                '\timport ' + '"' + i_str + '"\n' \
                    '\tdisplay_name =' + ' "' +str(host_dict['alias']) + '"\n' \
                        '\taddress =' + ' "' + str(host_dict['address']) + '"\n' \
                            '\t}'
        elif has_contacts == True:
            c_hst = str(hostgroup_dict['contacts'])
            print('c_hst first: ' + c_hst)
            c_hst = '","'.join(map(str,c_hst))
            print('c_hst second (post join): ' + c_hst)
            i_str = str(process_import())
            out_str = 'object Host ' + '"' + str(host_dict['host_name']) + '" {\n' \
                '\timport ' + '"' + i_str + '"\n' \
                    '\tdisplay_name =' + ' "' + str(host_dict['alias']) + '"\n' \
                        '\tgroups =' + ' "' + c_hst + '"\n' \
                            '\taddress =' + ' "' + str(host_dict['address']) + '"\n' \
                                '\t}'
    except KeyError: # To catch 'register 0' for making host templates
        i_lst = str(host_dict['use']).split(',')
        # Wrap this in a function so we can return i_str into out_str for fileoutput writing.
        def prep_imports():
            i_str = ''
            for i in i_lst:
                i_str += 'import\t' + '"' + i + '"' + '\n\t' # Why must I write statements like this? 
            return i_str

        g_str = str(host_dict['contacts']).split(',')
        g_str = '","'.join(map(str,g_str))
        out_str = 'template Host ' + '"' + str(host_dict['name']) + '" {\n' \
            '\t' + str(prep_imports()) + '\n' \
                '\tgroups = [' + ' "' + g_str + '" ]\n' \
                    '\t}\n'
    print(out_str)
    write_v2_conf(out_str)

def process_hostgroup():
    print(hostgroup_dict)
    s_hst = str(hostgroup_dict['members']).split(',')
    s_hst = '","'.join(map(str,s_hst))
    try:
        out_str = 'object HostGroup ' + '"' + str(hostgroup_dict['hostgroup_name']) + '" {\n' \
            '\tassign where host.name in [ ' + '"' + s_hst + '" ]\n' \
                '\tdisplay_name =' + ' "' +str(hostgroup_dict['alias']) + '"\n' \
                        '\t}'
        write_v2_conf(str(out_str))
        return str(out_str)

    except:
        print('DOH! Something went wrong!')

def process_contact():
    print(contact_dict)

    try:
        out_str = 'object User \"' + str(contact_dict['contact_name']) + '\" {' \
            "\n\timport " + '"' + str(contact_dict['use'])  + '"' \
            "\n\tdisplay_name =" + '"' + str(contact_dict['alias']) + '"' \
            "\n\tgroups = [ " + '"' + str(contact_dict['contactgroup_name']) + '" ]' \
                "\n\temail =" + '"' + str(contact_dict['email']) + '"' \
                    "\n}"
    except KeyError:
        out_str = 'object User \"' + str(contact_dict['contact_name']) + '\" {' \
            "\n\timport " + '"' + str(contact_dict['use'])  + '"' \
            "\n\tgroups = [ " + '"' + str(contact_dict['contactgroup_name']) + '" ]' \
                "\n\temail =" + '"' + str(contact_dict['email']) + '"' \
                    "\n}"
    write_v2_conf(str(out_str))

def process_service():
    has_nagios_vars = False
    print('-=- SERVICE DICT -=-')
    print(service_dict)
    for var in serv_extras.keys():
        if var in service_dict.keys():
            print('### Processing Nagios Service ###' + var)
            has_nagios_vars = True
    if 'use' and 'service_description' and 'check_command' in service_dict.keys():
        service_ready = True # This template I based off most of the services, as configured like nagios/afs-services.cfg. This may be cause me more stress in trying to integrate serv_extras, a dictionary of Nagios 
    else:
        service_ready = False
    if has_nagios_vars == True and service_ready == False:
        serv_str = 'Nagios Vars' 
    if service_ready == False:
        print('Not ready to process service')
    while service_ready == True:
        if 'host_name' in service_dict.keys() and service_ready == True:
            print('!!! host_name detected !!!')
            s_use = str(service_dict['use'])
            s_hst = str(service_dict['host_name'])
            s_dsec = str(service_dict['service_description'])
            s_cmd = str(service_dict['check_command'])
            if has_nagios_vars == False:
                print('No Nagios Vars detected.')
                serv_str = 'apply Service "' + s_dsec + '" {\n' \
                        '\timport "' + s_use + '"\n' \
                            '\tcheck_command = "' + s_cmd + '"\n\n' \
                                '\tassign where host.name in [ "' + s_hst + '" ]\n' \
                                    "}"
            if has_nagios_vars == True:
                print('Nagios Vars detected!')
                serv_str = 'apply Service "' + s_dsec + '" {\n' \
                    '\timport "' + s_use + '"\n' \
                        '\t' + 'Nagios vars' + '\n' \
                            '\tcheck_command = "' + s_cmd + '"\n\n' \
                                '\tassign where host.name in [ "' + s_hst + '" ]\n' \
                                    "}"
            print(serv_str)
            write_v2_conf(serv_str)
            service_dict.clear()
            print('Purging service dictionary now')
            service_ready = False
        elif 'hostgroup_name' in service_dict.keys() and service_ready == True:
            print('!!! hostgroup_name detected !!!')
            s_use = str(service_dict['use'])
            s_hst = str(service_dict['hostgroup_name'])
            s_dsec = str(service_dict['service_description'])
            s_cmd = str(service_dict['check_command'])
            if has_nagios_vars == False:
                serv_str = 'apply Service "' + s_dsec + '" {\n' \
                        '\timport "' + s_use + '"\n' \
                            '\tcheck_command = "' + s_cmd + '"\n\n' \
                                '\tassign where "' + s_hst + '"' + ' in host.groups' + '\n' \
                                    "}"
            elif has_nagios_vars == True:
                serv_str = 'apply Service "' + s_dsec + '" {\n' \
                        '\timport "' + s_use + '"\n' \
                            '\t' + ' - * - * - * NAGIOS VARS * - * - * - ' + '\n' \
                                '\tcheck_command = "' + s_cmd + '"\n\n' \
                                    '\tassign where "' + s_hst + '"' + ' in host.groups' + '\n' \
                                        "}"
            print(serv_str)
            write_v2_conf(serv_str)
            service_dict.clear()
            print('Purging service dictionary now')
            service_ready = False
    else:
        print('Continuing to check service dictionary...')

def write_v2_conf(MyStr):
    global FileName
    v2_out='./output/' + str(FileName)
    with open(v2_out,'a') as out:
        out.write(str(MyStr)+"\n") # Newline added so we don't write to the same lines.
        print('Text has been appended, please open ' + str(v2_out))
        out.close()
###########################
###-    RUN PROGRAM    -###
###########################

if len(os.listdir('./output')) > 0:
    print("'./output' dir already contains files!")
    prompt = input("Delete contents of './output/' ? [Y/N]: ")
    if str(prompt).upper() == 'Y':
        print('Purging!')
        shutil.rmtree('./output')
        os.mkdir('./output')
        print('Ready to run again!')
    elif str(prompt).upper() == 'N':
        print('Abandoning...')
        exit()
    else:
        print('Input Error, Please answer "Y" or "N". ')
        exit()

crunch_split_list(read_v1_config('./nagios/*.cfg'))