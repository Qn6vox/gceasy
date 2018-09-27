#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from django.shortcuts import render_to_response
from django.http.response import HttpResponse
import commands, time, json
import logging

logger = logging.getLogger("default")

def analyze(request):
    path = request.GET.get("path").strip()
    cmd = 'curl -s -X POST --data-binary @%s http://api.gceasy.io/analyzeGC?apiKey=6d79606b-28d1-4bf5-a03e-64e28b0422ea --header "Content-Encoding:zip"' % path
    status,result = commands.getstatusoutput(cmd)
    logger.info(cmd)
    logger.info(result)
    test = '{"isProblem":false,"jvmHeapSize":{"youngGen":{"allocatedSize":"682.69 mb","peakSize":"456.9 mb"},"oldGen":{"allocatedSize":"1 gb","peakSize":"649.73 mb"},"total":{"allocatedSize":"1.67 gb","peakSize":"997.54 mb"}},"gcStatistics":{"totalCreatedBytes":"2.07 tb","measurementDuration":"48 hrs 26 min 36 sec","avgAllocationRate":"12.46 mb/sec","avgPromotionRate":"3 kb/sec","minorGCCount":"6367","minorGCTotalTime":"23 sec 946 ms","minorGCAvgTime":"4 ms","minorGCAvgTimeStdDeviation":"5 ms","minorGCMinTIme":"0","minorGCMaxTime":"70 ms","minorGCIntervalAvgTime":"27 sec 394 ms","fullGCCount":"0"},"gcKPI":{"throughputPercentage":99.986,"averagePauseTime":3.7608793,"maxPauseTime":70.0},"gcDurationSummary":{"groups":[{"start":"0","end":"0.1","numberOfGCs":2335}]},"heapTuningTips":["It looks like you have over allocated Overall Heap size. During entire run, Overall Heap is peak utilization was only <strong>58.45%</strong> of the allocated size. You can consider lowering the Overall Heap Size."],"throughputPercentage":99.986,"responseId":"b39d9c1f-07ab-483c-a735-7208dd5946f1","graphURL":"http://api.gceasy.io/my-gc-report.jsp?p=YXJjaGl2ZWQvMjAxOC8wOS8xMS8tLWFwaS02ZDc5NjA2Yi0yOGQxLTRiZjUtYTAzZS02NGUyOGIwNDIyZWFkODcxODhmNi00MDczLTQ2ODgtODg1OS0yYzA3YTI1YmJkZjQudHh0LS0=&channel=API"}'
    #gurl = json.loads(result)
    gurl = json.loads(test)
    url = gurl["graphURL"]
    return HttpResponse(json.dumps({"reporturl":url, "result":test}))