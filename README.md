Blogging template for GitHub pages
==================================

	buzzwords:
	- jekyll
	- responsive web design (initializr-template)
	assets:
	- jquery 1.7.1
	- twitter bootstrap 2.0.2
	- modernizr 2.5.3
	seo:
	- microformats
	- rich snippets
	- page-specific title and description
	sosials:
	- +1
	- tweet

Usage
-----

- Fork.
- Rename the repo to username.github.com.
- Push something to your renamed repo to trig GitHub to generate the page, for example, edit _configs.yml and set the correct url. You should do this anyway to setup seo.
- Browse to http://username.github.com to see the result.

If you like to polish the default design or know some awesome Jekyll magic, I'm happy to merge pull requests.

__Try locally__

	git clone https://kblomqvist@github.com/kblomqvist/ghblog-template.git
	cd ghblog-template
	jekyll --server --auto --url=""

Now open your browser and go to _localhost:4000_. The url param tells the jekyll to override the url specified in _config.yml. Overwriting url with empty string gives us baseurl, which is "/". This way the links, for example in archive list, link to their local copies -- not to our production version, which would otherwise be the case because of the seo.

Did not have Jekyll? To install Jekyll you have to have Ruby and Ruby gems installed. If you do not have these yet, it is recommended to install Ruby locally:

	# MANDATORY! Install a bunch of support software
	sudo aptitude install build-essential curl autoconf \
	zlib1g zlib1g-dev bison openssl libssl-dev \
	libsqlite3-0 libsqlite3-dev sqlite3 libxml2-dev

	# Install RVM locally (no sudo!)
	bash < <(curl -s https://raw.github.com/wayneeseguin/rvm/master/binscripts/rvm-installer)

	# Install Ruby 1.9.3 locally (no sudo!)
	rvm install 1.9.3

	# If you got ssl cert errors
	#echo insecure >> ~/.curlrc

	# Use Ruby in this login session
	rvm use 1.9.3

Now you are ready to install Jekyll (do not use sudo)

	gem install jekyll 

## License

The code that this project consists of is licensed under MIT and is based of MIT-licensed work by [Tom Preston-Werner](http://github.com/mojombo/jekyll).

### Assets

- Twitter Bootstrap: Apache License, Version 2.0.
- jQuery: MIT/GPL license.
- Modernizr: MIT/BSD license.
- Normalize.css: Public Domain.
- Icons from Glyphicons Free, licensed under CC BY 3.0.
- The template design is based on [initializr-template](https://github.com/verekia/initializr-template).
