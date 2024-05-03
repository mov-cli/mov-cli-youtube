<div align="center">

  # mov-cli-youtube
  <sub>A mov-cli v4 plugin for watching youtube.</sub>

  <img src="https://github.com/mov-cli/mov-cli-youtube/assets/66202304/7b586dd2-2084-4d6c-b008-92e0539f5123">

</div>

## Installation 🛠️
Here's how to install and add the plugin to mov-cli.

1. Install the pip package.
```sh
pip install mov-cli-youtube
```
2. Then add the plugin to your mov-cli config.
```sh
mov-cli -e
```
```toml
[mov-cli.plugins]
youtube = "mov-cli-youtube"
```

## Usage 🖱️
```sh
mov-cli -s youtube nyan cat
```

### Audio Only 🔉
```sh
mov-cli -s youtube nyan cat -- --audio
```
