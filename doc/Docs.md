# Project BookRank: Documentation

## Overview
I want to create a book recommendation system based on graphs. Let a book be represented by a node. 
Each node stores the average weighted score and the number of reviews it has. 

There is a directed and weighted link between 2 books, A and B. The weight will represent the average weighted score of book B by users who have read A (they must have read both A and B). This will be the local score.

Users will request for a book, by giving input of the last book they have read and books they have already read (reading history). 
Based on the last book they have read and the genre that user wants to read, the program will find the relevant node and 
find the neighbour with highest combined score and is unread.

## Technicals
### Average weighted score
In most of the world (lest Japan and some others), ratings follow a dichotomy, 1 and 5, with a lack of in between. We try to centre our score on 3 (average).
Since average goodreads score of goodbooks-10k is 4.00, we will use 4.00 as our centre.
We introduce scaling at both sides, below and above average so that more of the scale can be used.
This gives equal chances to niche books and mainstream books.

**Weighted Score = $\begin{cases} 3 + (S - C)*\frac{2}{5 - C} & \text{if } S \geq C\\ 3 + (S - C)*\frac{2}{C - 1} & \text{if } S \lt C\end{cases} $**
- S = Average score for the book
- C = The mean score across the entire book database

### Libraries used
- numpy
- igraph (we use this instead of networkx because of its C backend)
- pandas

### Determining the recommendations
#### Combined Score 
From the global score (G) and local score (L), we calculate the combined score

### Combined Score = $\frac{n_{AB}}{n_{A}} * \frac{n_{AB} * L + m * G}{n_{AB} + m} $

- $n_{AB}$ - number of people who read A and B
- $n_{A}$ - number of people who read A
- m - mininimum value of ratings needed to trust an A->B average rating
- m can be adjusted by user (or fixed for speed)
- if m is fixed, combined score can be precalculated and added to edge attributes, for faster recommendations
- if the user something, more popular they can increase wg. If they want something more specific, they increase wl.
- To aid in exploration, damping factor can be implemented here as well.

#### Selecting the recommendations
1. Input last book read, and reading history
2. Find the node for the last book read, retrieve its neighbours
3. Filter its neighbours for the reading history and for the genre specified by user
4. For each neighbour, determine its combined score 
5. Select 10 books randomly from top 100 score (can be adjusted with n and k params)

#### Efficiency
1. Lookup for book metadata, linking them to bookid and internal graphid can be improved by using database
2. Results can be cached, especially if weights wg and wl are not controlled by user

## Schema

### Graph
#### Book/Node
- Global Score - G (float): Average weighted score centered on 3
- BookId (int): Correspond to book_id in databases

#### Link between Books
- Local Score: Average weighted score given by users for a Book A by those who also read B
- Between 2 books, the link will be bidirectional (but each direction is weighted differently)

### Database
#### books
- bookId (INTEGER; PRIMARY KEY)
- goodreadsBookId (INTEGER)
- isbn (INTEGER)
- authors (TEXT)
- title (TEXT)
- ratingsCount (INTEGER)
- averageRating (REAL)
- weightedScore (REAL)

#### ratings
- bookIdA (INTEGER; PRIMARY KEY)
- bookIdB (INTEGER; PRIMARY KEY)
- averageRating (given by users who read B who also read A; A -> B) (REAL)
- sumRating (INTEGER)
- ratingsCount (number of users who read A and B) (INTEGER)
- weightedScore (REAL)

#### book_genres (many - many relationship)
- bookId (INTEGER; FOREIGN KEY)
- genreId (INTEGER; FOREIGN KEY)

#### genres
- genreId (INTEGER; PRIMARY KEY)
- name (TEXT)

### Python
#### Books
- same as above

#### Ratings
- same as above
- to obtain ratings (A, B) pair, we need to iterate through each user, permute bookId pairs (using reviews) and determine averageRating

#### Users
- userId
- reviews (dict) : (bookId: rating)
We need this because ratings.csv is not sorted by userId. 
After processing ratings.csv, for each user, we determine the pair combinations between books the user has read (reviews.keys()) and add to the averageRating
in Ratings
