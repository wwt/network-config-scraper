# Network Config Scraper

This repository demonstrates the use of Github Actions and `git-scraping` to build an automated backup solution for network configuration files. **Git** already provides an efficient way to track and manage changes to textual data, and Github Actions provide automation that we can use to fetch and process configuration backups without reliance on any additional infrastructure. The solution in this repository uses both to retrieve configurations from network devices on a defined schedule and commits the detected changes back to the repository.

This approach is heavily inspired by [Git scraping: track changes over time by scraping to a Git repository](https://simonwillison.net/2020/Oct/9/git-scraping/)  by Simon Willison. His post provides an excellent overview of git-scraping data from various sources on the Internet.

![config scraper](https://user-images.githubusercontent.com/7189920/127345302-e08d8144-2c97-40b3-973c-637fe0933220.png)

## Could I use this?

Because of the textual nature of network configurations, git-scraping offers a simple yet effective way to backup and version configuration data. It runs entirely on GitHub Actions, so there's no complex infrastructure or orchestrations to manage.

Because the data we retrieve data from devices in a private lab, the repository uses a self-hosted runner that makes a connection to Github and has access to the lab. You'd have to decide if this is an acceptable model for your environment.

However, the solution works wonderfully and can be extended to fit into your existing automation. For example, using the webhooks in Github can extend this solution by allowing you to build or set up integrations to external automation systems which can subscribe to certain events on the repository. The configured events can trigger an HTTP POST to a system like Ansible Tower to provide additional automation.

## How does it work?

The configuration scraper is configured and scheduled in the [.github/workflows/scrape.yml](.github/workflows/scrape.yml) action workflow. It's a short and simple workflow that defines all the triggers and steps to run our automation.

### trigger

The workflow can be triggered in 3 different ways: on a push event to the repo, manually using the `workflow_dispatch`, or, most importantly, on a cron schedule. For example, in the snippet below, you can see that we have the workflow triggered every 30 minutes.

```yaml
on:
  push:
    branches:
      - main
  workflow_dispatch:
  schedule:
    - cron:  '*/30 * * * *'
```

### self-hosted runner(s)

Because our use case is slightly different from fetching data from flat files, we need to account for how GitHub would access the devices that we are fetching data from. For example, the devices in the `inventory.yml` are in a lab that sits behind a firewall, so a public Github action runner would not have the required access. For that reason, the repo is configured to use a self-hosted Github action runner that has access to the lab environment. It took about 15 minutes to [provision and to configure a runner](https://docs.github.com/en/actions/hosting-your-own-runners/about-self-hosted-runners) in this environment, so it is a relatively easy and painless process.  Once configured, the self-hosted runner creates a connection to Github and  listens for job requests to execute your actions.

Within the action workflow, the only things to specify are the fact that we're using a self-hosted runner and we also provide the tags to identify which runner to use for the action. We use the `runs-on` directive in the action to do just that, as shown below.

```yaml
jobs:
  scheduled:
    runs-on: [self-hosted, ubuntu1804atc-runner01]
```

## data

For data gathering, the `retrieve_configs.py` script is used to retrieve and save configuration data from each of the devices listed in the `inventory.yml` file. The script uses an async SSH connection transport from the `scrapli` library to handle parallel sessions to devices. Once the files are saved, the action workflow uses `git` to stage any files in which changes have been detected. A commit is created with a timestamp before the changes are pushed into the repository.

```yaml
  - name: Fetch latest configs
    run: |-
      python retrieve_configs.py
    env:
      SSH_AUTH_USERNAME: ${{ secrets.SSH_AUTH_USERNAME }}
      SSH_AUTH_PASSWORD: ${{ secrets.SSH_AUTH_PASSWORD }}

  - name: Commit and push if it changed
    run: |-
      git config user.name "Automated"
      git config user.email "actions@users.noreply.github.com"
      git add -A
      timestamp=$(date -u)
      git commit -m "Latest data: ${timestamp}" || exit 0
      git push
```

## How do I track changes?

The neat thing about using **Git** to manage your configuration backups is that you get this [commit log](https://github.com/ttafsir/network-config-scraper/commits/main/configs) showing the history of commits that have been made to your configs.
