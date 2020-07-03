## Test script to read in the 2020-02-21 data collection.

## To get the meaRtools package:
## install.packages('devtools')
## devtools::install_github(repo='igm-team/meaRtools/meaRtools', ref='mcs')


## SJE version only:
##require(devtools); load_all("~/langs/R/meaRtools/meaRtools")

library(meaRtools)

data_directory = "data/2020-02-21"
files = list.files(path=data_directory, pattern='.txt', full.names=TRUE)


files = files[11:20]

pdf(file="test1.pdf", width=11, height=8)
par(mfrow=c(2,1))
for (f in files) {
  print(f)

  ## this is a bit more complicated than I like -- my code currently errors
  ## on an empty spike file. 
  s <- tryCatch({
    read_spikelist_mcs100um(f)
  }, error = function(err) {
    print("read_spikelist_mcs100um failed")
    NULL
  })
  if (is.null(s)) {
    plot(1:10, type='n', main = f, bty='n', xaxt='n', yaxt='n', xlab='', ylab='')
    plot(1:10, type='n', main = 'no spikes', bty='n', xaxt='n', yaxt='n', xlab='', ylab='')

  }  else {
    nspikes = sum(s$nspikes)
    meaRtools:::.plot_spike_list(s, main=s$file, label_cells = TRUE)
    title(sub=sprintf("#spikes = %s", nspikes))
    ##meaRtools:::.plot_mealayout(s$layout, use_names=TRUE, cex=1)
    meaRtools:::.plot_meanfiringrate(s, main = "Mean Firing Rate by Plate (Hz)")
  }
}
dev.off()



## posfile = system.file("extdata/textreader/mcs-8x8-100um.pos", package="meaRtools")
## s = read_spikelist_text("/tmp/empty.csv", posfile, array="mcs-8x8-100um")




##   f = "/tmp/empty.csv"
##   f = "/tmp/empty.csv"
##   f = "/tmp/data.csv"
  
##   data <- tryCatch({
##     read.table(f, header = F, sep=",")
##   }, error = function(err) {
##     ## error handler picks up where error was generated
##     print(paste("Read.table didn't work!:  ",err))
##   })



## show burst analysis 

## example dataset...
data(S)
S$allb <- lapply(S$spikes, mi_find_bursts, S$parameters$mi_par )
S$allb
meaRtools:::.plot_spike_list(S, main=S$file, label_cells = TRUE,
                             whichcells=1:5,
                             beg=0, end=10,
                             show_bursts=TRUE)


s = read_spikelist_mcs100um("data/2020-02-21/171013_D36_2540.txt")
s$allb <- lapply(s$spikes, mi_find_bursts, S$parameters$mi_par )

s$allb

meaRtools:::.plot_spike_list(s, main=s$file, label_cells = TRUE,
                             beg=20, end=40,
                             show_bursts=TRUE)
