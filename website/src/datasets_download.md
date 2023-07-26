# Downloading the datasets

## SMAesH-A7_d2

The `SMAesH-A7_d2-vk0` and `SMAesH-A7_d2-fk0` datasets are currently available
on multiple servers.

### Compressed archive, single-file

A compressed archive (~200GB, ~300GB decompressed) available
[here](https://seafile.iaik.tugraz.at/f/781ac3e7ad2949129502/). It can be
easily downloaded with `wget` (download can be resumed if interrupted by
re-launching the same command):
```bash
wget -c --trust-server-names https://seafile.iaik.tugraz.at/f/781ac3e7ad2949129502/\?dl\=1
```
(File size: `211067203762 bytes`, SHA256: `bde1b7a930c9cef0193baa1c56a013cbbd5cf4da38ec1767076c06e980778b49`.)
It is compressed with the [zstd](http://facebook.github.io/zstd/) tool
(typically available on linux distributions as the `zstd` package), and
archived in the `tar` format.
To decompress it, run
```bash
zstdcat -T0 smaesh-dataset-v1-A7_d2.tar.zstd | tar xv
```

### Compressed archive, multi-file

The above archive is also available on [micorosft's cloud](https://uclouvain-my.sharepoint.com/:f:/g/personal/charles_momin_uclouvain_be/Er18thWjf2pGm531pte_LjcBx50Xu38e_MPOMqTJ6dhh5Q?e=IIqXKw), split in 10 files of ~20GB.
```
sha256sums:
816e5b3c569f4373529ab92c6175a6a3c6e9385b1168274c06c5419a1d9ba374  smaesh-dataset-v1-A7_d2.tar.zstd.0
c9b5d1029ebb19950d9d3a90c49e6a5cf7e88438cd362192a8059b4bc6b67de6  smaesh-dataset-v1-A7_d2.tar.zstd.1
d5f129bb482443783be751f39fbdda46c309643762ffc58c66c74c2589cc8af8  smaesh-dataset-v1-A7_d2.tar.zstd.2
025bac7d0215d8704454113d7439dcb1adac11f88bdcaca81cbd9cb2d1f666c6  smaesh-dataset-v1-A7_d2.tar.zstd.3
a813880c99e8c660c61c9a91e7921e75b1b6a5891c742ed69c43bc252b9ff277  smaesh-dataset-v1-A7_d2.tar.zstd.4
98d32140b96464f1581a43d6ae1b9dff94f5e9a221221f1223f5eed3de2604b0  smaesh-dataset-v1-A7_d2.tar.zstd.5
cc06b4fb835e296ac91b0097ec3bbd3e57e78521f4cde7a031e679f60834f570  smaesh-dataset-v1-A7_d2.tar.zstd.6
01b46d8008dd2ec01457dafd4eb82e476befc2001aecc05397b717ffedcc44ec  smaesh-dataset-v1-A7_d2.tar.zstd.7
6183429122c1ad012ae23c91e565e621c598322b527b26cf8e50721281a0c179  smaesh-dataset-v1-A7_d2.tar.zstd.8
7dec242a76a1a19609e521ff067f05182be8a4bffd1b525320bcd2a1617db26a  smaesh-dataset-v1-A7_d2.tar.zstd.9
file sizes 21474836480 for all except smaesh-dataset-v1.tar.zstd.9: 17793675442 bytes
```
You can concatenate and decompress in a single command:
```bash
cat smaesh-dataset-v1-A7_d2.tar.zstd.* | zstdcat -T0 - | tar xv
```

### Individual files

Individual files are available [here](https://nextcloud.cism.ucl.ac.be/s/82XMewXRBP5PZNP) (slow, not recommened for full dataset download).

## SMAesH-S6_d2

The `SMAesH-S6_d2-vk0` and `SMAesH-S6_d2-fk0` datasets are currently available
as a single archive and as a split archive.

### Compressed archive, single-file

A compressed archive (~190GB, ~300GB decompressed) available
[here](https://seafile.iaik.tugraz.at/f/7e78e6b4b7fc4e67994a/?dl=1). It can be
easily downloaded with `wget` (download can be resumed if interrupted by
re-launching the same command):
```bash
wget -c --trust-server-names https://seafile.iaik.tugraz.at/f/30416640d8fc42a999d6/?dl=1
```
(File size: `190667931874 bytes`, SHA256: `c542ed543b46a6228ffe8c39a959dbd6425330b4d00bb5d40ae849cf87bb18eb`.)
It is compressed with the [zstd](http://facebook.github.io/zstd/) tool
(typically available on linux distributions as the `zstd` package), and
archived in the `tar` format.
To decompress it, run
```bash
zstdcat -T0 smaesh-dataset-v1-S6_d2.tar.zstd | tar xv
```

### Compressed archive, multi-file

The above archive is also available on [micorosft's cloud](https://uclouvain-my.sharepoint.com/:f:/g/personal/charles_momin_uclouvain_be/Er18thWjf2pGm531pte_LjcBx50Xu38e_MPOMqTJ6dhh5Q?e=IIqXKw), split in 9 files of ~20GB.
```
sha256sums:
17783f6e538aa5f261a5998b3d11cdcc5d39cdeaf7d4b61f198c79c4426c9077  smaesh-dataset-v1-S6_d2.tar.zstd.0
6f16c7c81737ea220ec0ec8bd6392f5e6ade8b214b530bc4e96626c418565ce1  smaesh-dataset-v1-S6_d2.tar.zstd.1
ca260224ec7ba68194a5c9f934fff211ad9e55d555fe7c98574f2e68270b68a8  smaesh-dataset-v1-S6_d2.tar.zstd.2
adf311f9679a407ec211b92d21186bba1926ae9256d52932cdc8daf1bb03dce0  smaesh-dataset-v1-S6_d2.tar.zstd.3
53619e338e9651d1935cdd10964c2e45291d803b0575fadb1e8d947f8ef11eee  smaesh-dataset-v1-S6_d2.tar.zstd.4
d7879b6af425cafd5c26fccff38b01c0550a4a5314c3004b70c873ea7be95bdf  smaesh-dataset-v1-S6_d2.tar.zstd.5
6e0240fa1e6d5cc9ede4e7f090b7df76ff4f3b56f9da51693353773c1b5a8721  smaesh-dataset-v1-S6_d2.tar.zstd.6
e958645a992650da5ac8bf845d1085b711270d8895a23897e55ce057701ab93e  smaesh-dataset-v1-S6_d2.tar.zstd.7
50989a2564f26a3efba41dc527ce63f9c1e05d6622c81b2e87ba0c552ffc786a  smaesh-dataset-v1-S6_d2.tar.zstd.8
```
You can concatenate and decompress in a single command:
```bash
cat smaesh-dataset-v1-S6_d2.tar.zstd.* | zstdcat -T0 - | tar xv
