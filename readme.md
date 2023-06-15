# UPDATE  on Feb 23th 2023

Looks like [chiasenhac.vn](http://chiasenhac.vn) is down, it's good while it lasted!

# download album from chiasenhac.vn

Need login to download music quality > 128Kbps. Who listen to lower quality these days anyway?

Set env `CSN_USERNAME`, `CS_PASSWORD` or passing as args

Set optional `REQUESTS_EXTRA_KWARGS` if needed (e.g: proxies, skip ssl verify...)

```
usage: chiasenhac.py [-h] --url URL --username USERNAME --password PASSWORD [--quality QUALITY] [--threads NUM_THREADS] [--output OUTPUT_DIR]

download album from chiasenhac.vn

optional arguments:
  -h, --help            show this help message and exit
  --url URL, -u URL     url of the album
  --username USERNAME, -U USERNAME
                        username to login
  --password PASSWORD, -p PASSWORD
                        password to login
  --quality QUALITY, -q QUALITY
                        music quality, 128/320/m4a/flac
  --threads NUM_THREADS, -t NUM_THREADS
                        number of threads
  --output OUTPUT_DIR, -o OUTPUT_DIR
                        output folder
```

@vietvudanh, 2020
