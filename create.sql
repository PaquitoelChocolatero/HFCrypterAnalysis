CREATE TABLE posts (
    tid INT PRIMARY KEY,
    name TEXT,
    creation TEXT,
    creatorName TEXT,
    creatorUid INT,
    url TEXT,
    views INT,
    lastPost TEXT,
    originalPost BLOB,
    imgUrl BLOB,
    imgData BLOB,
    nComments INT,
    commentPage INT DEFAULT 1,
    nPages INT,
    FOREIGN KEY(creatorUid) REFERENCES users(id)
);

CREATE TABLE users (
    id INT PRIMARY KEY,
    name TEXT,
    moto TEXT,
    posts INT,
    threads INT,
    popularity INT,
    goodReviews INT,
    neutralReviews INT,
    badReviews INT
);

CREATE TABLE comments (
    commentId INT PRIMARY KEY,
    userUid INT,
    postId INT,
    date TEXT,
    content BLOB,
    FOREIGN KEY(userUid) REFERENCES users(id),
    FOREIGN KEY(postId) REFERENCES posts(tid)
);
