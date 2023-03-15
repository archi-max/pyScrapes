# PyScrapes
A work in progress library to get started with production-grade scraping quickly by adding the following features

- Multi-threading: Easily scale your scraping script to use resources efficiently
- Pause and Play: Save your data without impacting performance. Resume it again, when you are ready
- Proxy: Setting up proxies api again and again? Not anymore.
- Logging: Options to page you on errors. Useful for deploying on servers
- Multi-threaded error handling: Easier handling of multi threaded tasks

### Working Features

Only two! Don't worry though you can contribute to our code. Get started today!
- Multi-threading: Easily scale your script by overriding just one function (two if using selenium)
- Saving data: Just put data in queue and it will be saved in a json file!

### Potential Features

Features that I wish to add, but not sure if its feasaible

- Checks: Verify your scraped data! after some intervals. It becomes necessary when you are scraping for larger data. 
- Web Portal: Easy way to monitor scripts, data, and trigger any tasks.
- Automatically download and use webdrivers. Checking browser version, then downloading drivers is a troublesome process. To get started quickly use this library to download any webdriver. 