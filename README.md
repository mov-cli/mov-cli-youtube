<div align="center">

  # mov-cli-test
  <sub>A mov-cli v4 plugin to test mov-cli's capabilities.</sub>

  <img width="900px" src="https://github.com/THEGOLDENPRO/mov-cli-test/assets/66202304/ce7a12e1-9455-428e-88d4-a6946cfa7a79">

</div>

## Installation
Here's how to install and add the plugin to mov-cli.

1. Install the pip package.
```sh
pip install git+https://github.com/THEGOLDENPRO/mov-cli-test
```
2. Then add the plugin to your mov-cli config.
```sh
mov-cli -e
```
```toml
[mov-cli.plugins]
test = "mov-cli-test"
```

## Usage
```sh
mov-cli abc --scraper test.test
```
