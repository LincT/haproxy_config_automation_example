# Overview

To create HA proxy configuration, edit this file as needed, then run:
```
./readme_to_hap_optimized.py > conf/haproxy.cfg
```

To reload configs in haproxy:
```
./refresh_haproxy.sh
```

!!!IMPORTANT!!! check logs after refresh
```
docker compose logs
```

# Features:
> - [x] refresh script allows hot updates to config with haproxy able to fall back if config error
> - [x] Extracts config from HAProxy Configuration code block further down this document


# TODO:
> - [ ] follow up on open pr's and issues in this repo

# HAProxy Configuration

HAProxy is configured in the following manner:
```haproxy

  https://www.foobar.com                -> http://foobarcom-wp-server-1:80
  https://foobar.com                    -> http://foobarcom-wp-server-1:80
  https://stage.foobar.com              -> http://stage-foobarcom-wp-server-1:80
#  https://old.foobar.com                -> http://old-foobarcom-wp-server-1:80
#  https://non-existent.foobar.com       -> http://non-existent-foobarcom-wp-server-1:80
  https://new.foobar.com                -> http://new-foobarcom-wp-server-1:80
```

# References:
> - [Mozilla](https://ssl-config.mozilla.org)
> - [HAProxy](https://www.haproxy.org/)
> - [Docker compose](https://docs.docker.com/reference/cli/docker/compose/)
> - [Regular expressions](https://regex101.com/)
