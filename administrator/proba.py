from datetime import datetime, timezone;
from time import strftime

import pytz;


file_object = open('D:\Desktop\sample.txt', 'a');
file_object.write('\nProvera     ');
timeNow = datetime.now().astimezone(pytz.timezone('Europe/Belgrade'));
file_object.write(datetime.strftime(timeNow,"%Y-%m-%dT%H:%M:%S%z"));
startTime="2021-09-29T17:02:36";
endTime="2021-09-29T17:03:06";
time="2021-09-29T17:02:51"
if endTime<=time:
    print("Manje");
else:
    print("Vece");