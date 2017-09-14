from optparse import OptionParser
from datetime import *
from mrtparse import *
import commands
import ast
myASnumber = 0
indt = 0
target1 = open("outPut.txt","a")
target2 = open("FinalStability","a")
ipset = set()
ip_to_asn = {}

AsnFile_sent = open("asnFile_sent","r")
asnList_sent = ast.literal_eval(AsnFile_sent.read())
AsnFile_sent.close()
print "asnList sent - "
print asnList_sent

AsnFile_recv = open("asnFile_recv","r")
asnList_recv = ast.literal_eval(AsnFile_recv.read())
AsnFile_recv.close()
print "asnList recv - "
print asnList_recv

AsnFile_total = open("asnFile_total","r")
asnList_total = ast.literal_eval(AsnFile_total.read())
AsnFile_total.close()
print "asnList total - "
print asnList_total


asnStability = {}

def prline(line):
	global indt
	print('    ' * indt + line)

def print_bgp4mp(m):
	global indt
	indt = 0
	#prline('%s' % BGP4MP_ST[m.subtype])
	indt += 1
	if ( m.subtype == BGP4MP_ST['BGP4MP_MESSAGE'] or m.subtype == BGP4MP_ST['BGP4MP_MESSAGE_AS4'] or m.subtype == BGP4MP_ST['BGP4MP_MESSAGE_LOCAL'] or m.subtype == BGP4MP_ST['BGP4MP_MESSAGE_AS4_LOCAL']):
		print_bgp_msg(m.bgp.msg, m.subtype, m)

def print_bgp_msg(msg, subtype, m):
	global indt
	global ipset
	global asnStability
	global ip_to_asn
	indt = 0
	for withdrawn in msg.withdrawn:
		ip = str(withdrawn.prefix)+"/"+str(withdrawn.plen)
		if ip in ipset:
			asnToAdd= ip_to_asn[ip]
			#target1.write("withdrew route " + ip+" asn "+asnToAdd + " at "+str(datetime.fromtimestamp(m.ts))+"\n")
			asnStability[asnToAdd] = asnStability[asnToAdd]+1
            
	for attr in msg.attr:
		if attr.type == BGP_ATTR_T['AS_PATH']:
			asPathValue = []
			for path_seg in attr.as_path:
				asPathValue = path_seg['val']
				#print asPathValue
				addedAsn = str(asPathValue[-1])
				if addedAsn in asnList_sent:
					for nlri in msg.nlri:
						addedIp = str(nlri.prefix)+"/"+str(nlri.plen)
						#target1.write("added route " + addedIp + " asn "+ addedAsn+" at "+str(datetime.fromtimestamp(m.ts))+"\n")
						asnStability[addedAsn] = asnStability[addedAsn] + 1

				if addedAsn in asnList_recv:
                                        for nlri in msg.nlri:
                                                addedIp = str(nlri.prefix)+"/"+str(nlri.plen)
                                                #target1.write("added route " + addedIp + " asn "+ addedAsn+" at "+str(datetime.fromtimestamp(m.ts))+"\n")
                                                asnStability[addedAsn] = asnStability[addedAsn] + 1

				if addedAsn in asnList_total:
                                        for nlri in msg.nlri:
                                                addedIp = str(nlri.prefix)+"/"+str(nlri.plen)
                                                #target1.write("added route " + addedIp + " asn "+ addedAsn+" at "+str(datetime.fromtimestamp(m.ts))+"\n")
                                                asnStability[addedAsn] = asnStability[addedAsn] + 1
def main():
	global ipset
	global asnStability
	global as_to_ip_map
	global asnList_sent
	global asnList_recv
	global asnList_total
	d = Reader(sys.argv[1])
	for myASnumber in asnList_sent:
		asnStability[myASnumber] = 0
		cmd = "whois -h whois.radb.net -- '-i origin AS"+myASnumber+ "' | grep route:"
		ipInfo = commands.getoutput(cmd)
		for ip in ipInfo.split("\n"):
			ip_to_asn[ip[12:]] = myASnumber
			ipset.add(ip[12:])
	
	for myASnumber in asnList_recv:
                asnStability[myASnumber] = 0
                cmd = "whois -h whois.radb.net -- '-i origin AS"+myASnumber+ "' | grep route:"
                ipInfo = commands.getoutput(cmd)
                for ip in ipInfo.split("\n"):
                        ip_to_asn[ip[12:]] = myASnumber
                        ipset.add(ip[12:])

        for myASnumber in asnList_total:
                asnStability[myASnumber] = 0
                cmd = "whois -h whois.radb.net -- '-i origin AS"+myASnumber+ "' | grep route:"
                ipInfo = commands.getoutput(cmd)
                for ip in ipInfo.split("\n"):
                        ip_to_asn[ip[12:]] = myASnumber
                        ipset.add(ip[12:])

	#i =0
	#for i in range(0,1000):
	for m in d:
		m = m.mrt
		if ( m.type == MRT_T['BGP4MP'] or m.type == MRT_T['BGP4MP_ET']):
			print_bgp4mp(m)
	print "asnStability --- "
	print asnStability
	target2.write(str(asnStability)+",")
	target2.close()
	target1.close()

if __name__ == '__main__':
	print "main entered"
	main()