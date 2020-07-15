# bookkeeper
### "Will I be able to get this class?"

This scrapes UMD's course catalog (every 15 minutes via `cron`) to keep an eye on what classes students are interested in.
This data is fed into influxDB, and will be used in the future to analyze patterns in course selection at UMD.

#### Note: this implementation is quick and dirty!
I didn't want to miss out on the beginning of course selection, so I didn't implement multitasking properly. Depending on the quality of the data I've gotten so far, I might redo this in Go to take advantage of goroutines.
