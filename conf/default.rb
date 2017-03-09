# This goes in scalr-server/attributes/default.rb

#########
# Proxy #
#########

# Whether to enable the web proxy. The proxy is a reverse proxy for the various web components that make up Scalr.
default[:scalr_server][:proxy][:enable] = false

# The host and port the proxy should bind to (for http). See below for HTTPS.
default[:scalr_server][:proxy][:bind_host] = '0.0.0.0'
default[:scalr_server][:proxy][:bind_port] = 80  # Setting this to anything but 80 isn't really supported at this time.

# The host and port the wsgi should bind to (for http).
default[:scalr_server][:wsgi][:enable] = false
default[:scalr_server][:wsgi][:bind_host] = '0.0.0.0'
default[:scalr_server][:wsgi][:bind_port] = 6300  # Setting this to anything but 80 isn't really supported at this time.

# HTTPS settings
default[:scalr_server][:proxy][:ssl_enable] = false   # Whether to enable HTTPS
default[:scalr_server][:proxy][:ssl_redirect] = true  # Whether to redirect from HTTP to HTTPS. You shouldn't enable this unless your cert is valid.
default[:scalr_server][:proxy][:ssl_bind_port] = 443  # Setting this to anything but 443 isn't really supported at this time.
default[:scalr_server][:proxy][:ssl_cert_path] = nil  # Path to the SSL cert that the proxy should use (required if SSL is enabled)
default[:scalr_server][:proxy][:ssl_key_path] = nil   # Path to the SSL key that the proxy should use (required if SSL is enabled)

# Upstream configuration for the proxy. These should all be lists of `host:port` entries.
default[:scalr_server][:proxy][:app_upstreams] = ['127.0.0.1:6270']
default[:scalr_server][:proxy][:graphics_upstreams] = ['127.0.0.1:6271']
default[:scalr_server][:proxy][:plotter_upstreams] = ['127.0.0.1:6272']
default[:scalr_server][:proxy][:wsgi_upstreams] = ['127.0.0.1:6300']
