# Network Config Scraper

This repository demonstrates the use of Github Actions and `git-scraping` to build an automated backup solution for network configuration files. The `scrape.yml` action runs on a schedule, and it uses the `retrieve_configs.py` script to fetch configurations from network devices and creates a commit if any changes are detected. This approach is heavily inspired by [Git scraping: track changes over time by scraping to a Git repository](https://simonwillison.net/2020/Oct/9/git-scraping/)  by Simon Willison.

![config scraper (1)](https://user-images.githubusercontent.com/7189920/127178866-1fee3988-fd0c-4fed-9097-91d2acedfe92.png)

## Why should I use this?

Because of the textual nature of network configurations, git-scraping offers a simple yet effective way to backup and version configuration data. It runs entirely on GitHub Actions, so there's no complex infrastructure or orchestrations to manage. The action fetches configurations for devices you specify in the `inventory.yml` file using a simple script in the root of this repo. If any changes are detected, the new data is committed to the repository with a commit message that can be customized to reflect the latest changes. The action can also be triggered manually as need.

## What about my other systems?

Using the webhooks capability of Github can extend this solution by allowing you to build or set up integrations to external automation systems which can subscribe to certain events on the repository. For example, if new commits are made, you can trigger an HTTP POST to a system like Ansible Tower to provide additional automation.

## How does it work?

### trigger

The configuration scraper is configured and scheduled in the [.github/workflows/scrape.yml](.github/workflows/scrape.yml) action workflow. The workflow can be triggered in 3 different ways: on a push event to the repo, manually using the `workflow_dispatch`, or, most importantly, on a cron schedule. For example, in the snippet below, you can see that we have the workflow triggered every 30 minutes.

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
