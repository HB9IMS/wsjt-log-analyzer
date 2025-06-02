# wsjt-log-analyzer

This is a tool to analyze WSJT log files. 

## Needed individualisations

In order to use this tool, you must either insert your locator into the variable
´´´YOUR_LOCATOR´´´ or set it before running the main function.



## Running

Running is relatively simple:

´´´python3 wsjtx_log_analyzer.py <Path to your log file>´´´

## Known issues

This script unfortunately only works, if the QSO has a logged locator. 
Not every station does provide one; if they don't, they will be skipped. 

Also, all all the distances are in kilometers; if you wish miles, you can adjust it on line 22.

I higly encurage you to mess around with the number of bins, the axes of the plots etc.!
It may drasticly enhance the understanding of your propagation. 

In case you have the will and determination, you could also modify the script to take in the received messages and display in real time or something like that...

## Results

You should get seven plots:

### 1.: $log$'d polar:

A polar plot with you in the center, but the radius (distance) is scaled logarithmicly. 
A good usecase is in the example file: 
As you will be able to see; there are a lot of QSOs at the $1000km$ / 1 ionospherical skip mark,
and the Rest of the QSOs are (relatively) well spread out.
Additionally, the used power will appear as the size, wereas less power is marked with 

### 2.: Linear polar

This is very simple: Distance and bearing, with the color being the report you received

### 3.: $log$'d histogram of distances

Again, very simple. Counts are on the $y$-axis, the distance in a logarithmic scale on the $x$.

### 4.: SNR histogram of distances

Nothing special; Counts are on the $y$-axis, the $x$-axis holds the reported SNR from the other station.

### 5.: $xy$-plot with SNR, Power and Distance

This is one of the more interesting graphs. Once again, the $log$ scaled $x$-axis, 
the report on the $y$-axis but this time, the power used is displayed as color. 

### 6.: (useless) scatter plot between power and SNR

Please don't use this; the power values are too discrete for the data to make sense in such a format

### 7.: (Way more useful) box plot between power and SNR

Although it is quite limited by how many power settings you use, 
it may be useful to determine QRP performance but be aware of the bias introduced.
As an example: many times with a bad antenna, I am greatful for every QSO I make, 
whereas when I have adequate antenna performance, I am more DX-minded. 

# LICENSE

I'm not bothering to license it, just do not try to sue me or sell my work as yours.
