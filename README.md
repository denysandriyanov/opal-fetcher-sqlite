<p align="center">
 <img src="https://i.ibb.co/BGVBmMK/opal.png" height=170 alt="opal" border="0" />
</p>
<h2 align="center">
OPAL Fetcher for SQLite
</h2>

[Check out OPAL main repo here.](https://github.com/permitio/opal)

### What's in this repo?
An OPAL custom fetch provider to bring authorization state from SQLite.

This fetcher is both:
- A fully functional fetch-provider for SQLite: can be used by OPAL to fetch data from SQLite databases.
- Serving as an example how to write custom fetch providers for OPAL and how to publish them as pip packages.

### How to try this custom fetcher in one command? (Example docker-compose configuration)

You can test this fetcher with the example docker-compose file in this repository root. Clone this repo, cd into the cloned repo, and then run:
docker compose up

This docker-compose configuration already correctly configures OPAL to load the SQLite Fetch Provider, and correctly configures OPAL_DATA_CONFIG_SOURCES to include an entry that uses this fetcher.

### How to use this fetcher in your OPAL Setup

1) Build a custom opal-client Dockerfile

The official docker image only contains the built-in fetch providers. You need to create your own Dockerfile (that is based on the official docker image), that includes this fetcher's pip package.

Your Dockerfile should look like this:
FROM permitio/opal-client:latest
RUN pip install --no-cache-dir --user opal-fetcher-sqlite

2) Build your custom opal-client container
   Say your special Dockerfile from step one is called custom_client.Dockerfile.

You must build a customized OPAL container from this Dockerfile, like so:
docker build -t yourcompany/opal-client -f custom_client.Dockerfile .

3) When running OPAL, set OPAL_FETCH_PROVIDER_MODULES
   Pass the following environment variable to the OPAL client docker container (comma-separated provider modules):
   OPAL_FETCH_PROVIDER_MODULES=opal_common.fetcher.providers,opal_fetcher_sqlite.provider

Notice that OPAL receives a list from where to search for fetch providers.
The list in our case includes the built-in providers (opal_common.fetcher.providers) and our custom SQLite provider.

4) Using the custom provider in your DataSourceEntry objects

Your DataSourceEntry objects (either in OPAL_DATA_CONFIG_SOURCES or in dynamic updates sent via the OPAL publish API) can now include this fetcher's config.

The example value of OPAL_DATA_CONFIG_SOURCES (formatted nicely, but in the env var you should pack this to one line and remove spaces):
{
    "config": 
    {
        "entries": 
        [
            {
                "url": "sqlite:///path/to/your/sqlite/database.db",
                "config":
                    {
                     "fetcher": "SQLiteFetchProvider",
                     "query": "SELECT * FROM city;"
                    },
                "topics": ["policy_data"],
                "dst_path": "cities"
            }
        ]
    }
}



Notice how config is an instance of SQLiteFetcherConfig (code is in opal_fetcher_sqlite/provider.py).

Values for this fetcher config:
- The url is the SQLite database file path.
- Your config must include the fetcher key to indicate to OPAL that you use a custom fetcher.
- Your config must include the query key to indicate what query to run against SQLite.

Possible User Issues
While trying to send requests to an SQLite data source, you may encounter that the request fails. This can be caused by incorrect formatting of the config entry URL.

The correct format of the config entry URL for SQLite is:
sqlite:///path/to/your/sqlite/database.db

About OPAL (Open Policy Administration Layer)
OPAL is an administration layer for Open Policy Agent (OPA), detecting changes to both policy and policy data in real-time and pushing live updates to your agents.

OPAL brings open policy up to the speed needed by live applications. As your application state changes (whether it's via your APIs, databases, git, S3, or 3rd-party SaaS services), OPAL ensures your services are always in sync with the authorization data and policy they need (and only those they need).

Check out OPAL's main site at OPAL.ac.

