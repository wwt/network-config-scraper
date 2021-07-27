# Network Config Scraper

This repository demonstrates the use of Github Actions and `git-scraping` to build an automated backup solution for network configuration files. The `scrape.yml` action runs on a schedule, and it uses the `retrieve_configs.py` script to fetch configurations from network devices and creates a commit if any changes are detected. This approach is heavily inspired by [Git scraping: track changes over time by scraping to a Git repository](https://simonwillison.net/2020/Oct/9/git-scraping/)  by Simon Willison.

![config scraper](https://user-images.githubusercontent.com/7189920/127108335-0b92ffb5-f80d-407c-b9cb-2d82167b4b2e.png)

## Why should I use this?

Because of the textual nature of network configurations, git-scraping offers a simple yet effective way to backup and version configuration data. It runs entirely on GitHub Actions, so there's no complex infrastructure or orchestrations to manage. The action fetches configurations for devices you specify in the `inventory.yml` file using a simple script in the root of this repo. If any changes are detected, the new data is committed to the repository with a commit message that can be customized to reflect the latest changes. The action can also be triggered manually as need.

## What about my other systems?

Using the webhooks capability of Github can extend this solution by allowing you to build or set up integrations to external automation systems which can subscribe to certain events on the repository. For example, if new commits are made, you can trigger an HTTP POST to a system like Ansible Tower to provide additional automation.
