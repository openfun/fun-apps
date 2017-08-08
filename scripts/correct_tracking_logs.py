from json import loads, dumps
from sys import argv,stdout
from archery.bow import Daikyu as _dict
import re
usage = """
Correct any given log given on the command line (beware of space in file name
and IFS)

OUTPUT STOUT: progress E=Error(line number), C=Corrected, F=Failure
A dot every 1000 lines

At the end the number of failure by detectable input

OUTPUT 2
in current dir, extra informations in results.txt
OUTPUT 3

corrected logs written in filenamne.clean

"""
until_bloat = re.compile('''(^.*"event": \["[^"]*")''').match
whois_afflicted = re.compile('''.*"(?:referer)": "([^"]*)"''').match
_get_course = re.compile(""".*courses/([^/]*)/""").match
get_course = lambda referer: _get_course(referer).group(1)

ln = 0
success = 0
error = 0
corr = 0
if len(argv) <= 1:
    print usage
    exit(1)

file_name = argv[1:]

pp = stdout.write

out = open("result.txt", "w")

for fn in file_name:

    out.write( "*" * len(fn))
    out.write("\n")
    out.write( fn )
    out.write("\n")
    out.write( "*" * len(fn))
    out.write("\n")
    out.write("\n")
    victim=_dict()
    correction = _dict()
    last_time=""
    wtf=0
    clean = open("%s.clean" % fn, "w")
    for i,l in enumerate(open(fn)):
        ln+=1
        if not ln%1000:
            pp(".")
        try:
            data = loads(l)
            last_time = data.get("time", last_time)
            success += 1
            clean.write(l)
            to_print = l
        except Exception as e:
            error+=1
            pp("E(%d)" % (ln))
            corrected = False
            try:
                match =  until_bloat(l)
                if match:
                    match = match.group(1)
                    corec =  match + ', "IRRECOVERABLE CONTENT"]}'
                    data = loads(corec)
                    out.write(str(ln) + ":CORRECTED:")
                    out.write(l)
                    out.write("\n")
                    if last_time:
                        data["time"] = str(last_time)
                    to_print = dumps(data) + "\n"
                    out.write(to_print)
                    out.write("\n")
                    corr+=1;
                    corrected=True
                    pp("C")
                    sniff = whois_afflicted(l)
                    if sniff:
                       sniff =  sniff.group(1)
                       correction +=_dict({sniff:1})
                       out.write( sniff )
                else:
                    wtf+=1
                    pp("F")
            except Exception as f:
                print f
                if not corrected:
                    out.write("not corrected %s\n" % l)
                sniff = whois_afflicted(l)
                if sniff:
                    sniff=sniff.group(1)
                    out.write( sniff )
                    victim+=_dict({sniff:1})
                else:
                    print l
                out.write("\n")
                out.write("-" * 80)
                out.write("\n")
            finally:
                clean.write(to_print)
    clean.close()
    print "\n"
    print "***************"
    print "NON correctable"
    print "***************"
    print dumps(victim, indent=4)
    print "***********"
    print "corrections"
    print "***********"
    print dumps(correction, indent=4)
    print "\nErrors: %d Corrections:%d  Success:%d Lines:%d\n" % (error, corr, success, ln)

out.close()
