import bgp_report_source
import time
s = time.time()
bgp_report_source.main()
#bgp_report_source.main("2017-11-05-00-16-03","2017-11-05-00-31-03")
print "Total time compute ",time.time()-s

