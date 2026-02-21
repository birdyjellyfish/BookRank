# BookRank

## Overview
Inspired by Google's PageRank search ranking algorithm, BookRank is a book recommendation system that makes use of graphs to recommend books.

## How it works
Based on the last book read that the user liked (we call this book A), we find the neighbouring books of book A (books read by other users who also read A). For each neighbour, we calculate its combined score, and select the top kth books. We can filter for the genre that user wants to read next as well. 

For more info, read the [docs](./doc/Docs.md).

## Installation
Install the dependencies for BookRank.
```
pip install -r requirements.txt
```

Depending on size of dataset, enough memory and storage must be available to run BookRank. Based on our testing on ```goodbooks-10k-extended```, the db file requires **~2.7GB** and the graph pickle file requires **~1.6GB** of storage. While in use, BookRank takes up **~6GB** of memory.

## Usage
Before usage of ```bookrank.py```, we need to setup the database and graph structure. You can do this in [```data.ipnyb```](./data.ipynb).

Example code is provided in [```demo.ipynb```](./demo.ipynb).

## Acknowledgements
[```zygmuntz/goodbooks-10k```](https://github.com/malcolmosh/goodbooks-10k-extended)

[```malcolmosh/goodbooks-10k-extended```](https://github.com/malcolmosh/goodbooks-10k-extended)
