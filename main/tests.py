from django.test import TestCase

# Create your tests here.

import json,webbrowser

json_data = '{"isProblem":false,"jvmHeapSize":{"youngGen":{"allocatedSize":"682.69 mb","peakSize":"456.9 mb"},"oldGen":{"allocatedSize":"1 gb","peakSize":"649.73 mb"},"total":{"allocatedSize":"1.67 gb","peakSize":"997.54 mb"}},"gcStatistics":{"totalCreatedBytes":"2.07 tb","measurementDuration":"48 hrs 26 min 36 sec","avgAllocationRate":"12.46 mb/sec","avgPromotionRate":"3 kb/sec","minorGCCount":"6367","minorGCTotalTime":"23 sec 946 ms","minorGCAvgTime":"4 ms","minorGCAvgTimeStdDeviation":"5 ms","minorGCMinTIme":"0","minorGCMaxTime":"70 ms","minorGCIntervalAvgTime":"27 sec 394 ms","fullGCCount":"0"},"gcKPI":{"throughputPercentage":99.986,"averagePauseTime":3.7608793,"maxPauseTime":70.0},"gcDurationSummary":{"groups":[{"start":"0","end":"0.1","numberOfGCs":2335}]},"heapTuningTips":["It looks like you have over allocated Overall Heap size. During entire run, Overall Heap\'s peak utilization was only <strong>58.45%</strong> of the allocated size. You can consider lowering the Overall Heap Size."],"throughputPercentage":99.986,"responseId":"8ce8ff9e-6ffa-4f3b-a24b-5c600d4022e4","graphURL":"http://api.gceasy.io/my-gc-report.jsp?p=YXJjaGl2ZWQvMjAxOC8wOC8zLy0tYXBpLTZkNzk2MDZiLTI4ZDEtNGJmNS1hMDNlLTY0ZTI4YjA0MjJlYTgyMjVjMjc4LWEwYjUtNDE2ZS05ZDkzLWE5NjEyNDgwMDQ3Ny50eHQtLQ==&channel=API"}'

dict = json.loads(json_data)

url = dict["graphURL"]

webbrowser.open(url, new=2, autoraise=True)